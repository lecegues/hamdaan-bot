import discord
import random
from discord.ext import commands
from yt_dlp import YoutubeDL


QUEUE_SONG_LIMIT = 5  # Max number of songs to display in /queue

class YoutubeCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.vc = None  # Voice Client instance

        self.is_playing = False
        self.is_paused = False

        # [ ( {"source": url, "title": title}, voice_channel_obj )]
        # where [0] is the NEXT song
        self.music_queue = []
        self.curr_song = None 

        # YoutubeDL options
        self.YDL_OPTIONS = {
            "format":
            "m4a/bestaudio/best",
            "noplaylist":
            "True",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "m4a",
                "preferredquality": "0",  # 0 is best quality
            }],
            "postprocessor_args": [
                "-ar",
                "48000",
                "-ac",
                "2"  # ensure stereo output
            ]
        }

        # FFMPEG options to handle reconnection
        self.FFMPEG_OPTIONS = {
            "before_options":
            "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            "options": "-vn -loglevel debug"
        }

    def search_yt(self, query: str) -> dict | bool:
        """
        Search YouTube with given query
        
        Returns: dict: {"source": url, "title" title}
        """
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                # perform yt search and extract info from first result without downloading the video
                info = ydl.extract_info("ytsearch:%s" % query, download=False)
                if not info:
                    raise ValueError(f"No results found for {query}")
                info = info['entries'][0]
                return {"source": info["url"], "title": info["title"]}

            except Exception as e:
                print(e)
                return False

    async def play_next(self) -> None:
        """Plays the next song in the music queue if available; otherwise stops music"""
        if len(self.music_queue) > 0:
            self.is_playing = True

            # get url of next song in queue and remove it from queue
            m_url = self.music_queue[0][0]["source"]
            self.curr_song = self.music_queue.pop(0)

            # Play audio with options, and after, call this function again to play next song
            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS),
                         after=lambda e: self.play_next())

        else:
            self.is_playing = False

    async def play_music(self, ctx):
        """Plays the current song in the music queue in a voice channel/connects to a voice channel"""
        if len(self.music_queue) > 0:
            self.is_playing = True
            m_url = self.music_queue[0][0]["source"]

            if (self.vc is None) or (not self.vc.is_connected()):
                # connect to the voice channel where song was requested
                self.vc = await self.music_queue[0][1].connect()

                # check if connection failed
                if self.vc is None:
                    await ctx.send("Could not connect to the voice channel")
                    return
                else:
                    await self.vc.move_to(self.music_queue[0][1])

            self.curr_song = self.music_queue.pop(0)
            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS),
                         after=lambda e: self.play_next())
        else:
            self.is_playing = False

    @discord.slash_command(name="play",
                           description="Play the selected song from YouTube. Can be a URL or a search query")
    async def play(self, ctx, query: str):
        """
        Allow users to search for songs and play it in their voice chat

        Post-Conditions:
        - If not connected: Prompt them to connect
        - If already playing a song: Add song to queue
        """

        voice_channel = ctx.author.voice
        if voice_channel is None:
            await ctx.respond("Connect to a voice channel!")
        else:
            voice_channel = voice_channel.channel
            # Search for the song on YT using the provided query
            await ctx.defer()
            song = self.search_yt(query)
            if not song:  # Check if the search failed
                await ctx.respond(
                    "Could not download the song. Incorrect format, try a different keyword"
                )
            else:
                # add song + voice channel to queue
                self.music_queue.append([song, voice_channel])
                await ctx.respond(f"{self.music_queue[-1][0]["title"]} added to the queue")

                if not self.is_playing:
                    await self.play_music(ctx)

    @discord.slash_command(name="pause", description="Pause the current song")
    async def pause(self, ctx):
        """Pause the currently playing song"""
        if self.is_playing:
            self.is_playing = False
            self.is_paused = True
            self.vc.pause()
            await ctx.respond("Music paused.")
        elif self.is_paused:
            await ctx.respond("Music is already paused.")

    @discord.slash_command(name="resume",
                           description="Resume the current song")
    async def resume(self, ctx):
        """Resume the currently paused song"""
        if self.is_paused:
            self.is_playing = True
            self.is_paused = False
            self.vc.resume()
            await ctx.respond("Music resumed.")
        elif self.is_playing:
            await ctx.respond("Music is already playing.")

    @discord.slash_command(name="skip", description="Skip the current song")
    async def skip(self, ctx):
        if self.vc and self.vc.is_playing(): 
            self.vc.stop() 
            await self.play_next()
            if self.curr_song: 
                await ctx.respond(f"Now playing {self.curr_song[0]['title']}")
            else: 
                await ctx.respond("No more songs in queue")
        else: 
            await ctx.respond("No music playing to skip.")
    
    # @TODO display in a code block
    @discord.slash_command(name="queue", description="Show the current queue")
    async def queue(self, ctx):
        """Displays the current music queue, showing up to a specified amount of songs"""
        retval = ""

        for i in range(0, len(self.music_queue)):
            if i > (QUEUE_SONG_LIMIT - 1):
                break
            retval += f"{i+1}. {self.music_queue[i][0]['title']}\n"

        if retval != "":
            await ctx.respond(retval)
        else:
            await ctx.respond("No music in the queue")

    @discord.slash_command(name="clear", description="Clear the current queue")
    async def clear(self, ctx):
        """Clear the queue and stop the currently playing song"""
        if self.vc and self.is_playing:
            self.vc.stop()
        self.music_queue = []
        await ctx.respond(f"Music queue cleared")

    @discord.slash_command(
        name="leave", description="Disconnect the bot from the voice channel")
    async def leave(self, ctx):
        """Kick the bot from the voice chat"""
        self.is_playing = False
        self.is_paused = False
        await self.vc.disconnect()
        await ctx.respond("Disconnected from the voice channel")

    @discord.slash_command(name="nowplaying", description="Show the current song name")
    async def now_playing(self, ctx): 
        """Show the title of the current song playing"""
        if self.vc and self.is_playing and self.curr_song: 
            await ctx.respond(f"Now playing {self.curr_song[0]['title']}")
        else: 
            await ctx.respond("No music playing")

    @discord.slash_command(name="shuffle", description="Shuffle the current queue")
    async def shuffle(self, ctx): 
        """Shuffle the current queue"""""
        if self.music_queue: 
            random.shuffle(self.music_queue) 
            await ctx.respond("Music queue shuffled")
        else: 
            await ctx.respond("No music in the queue")
            
    # /lyrics: use an API to find the lyrics for the song if it exists
    # /remove: remove a song from the queue
    # /repeat? Clone the current song to the next spot in the queue
    # /playlist: adds a playlist to the queue
    # /seek or /jump??-- can either go forward/backwards a certain time OR jump to a certain time 
    # /songinfo-- provide detailed information about the currently playing song? 

def setup(bot):
    bot.add_cog(YoutubeCog(bot))
