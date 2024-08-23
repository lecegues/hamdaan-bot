import discord
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
        self.music_queue = []

        # YoutubeDL options
        # self.YDL_OPTIONS = {"format": "bestaudio", "noplaylist": "True"}
        self.YDL_OPTIONS = {
            "format":
            "m4a/bestaudio/best",
            "noplaylist":
            "True",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "m4a",
            }]
        }

        # FFMPEG options to handle reconnection
        self.FFMPEG_OPTIONS = {
            "before_options":
            "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            "options": "-vn -loglevel debug"
        }
        '''def search_yt(self, query: str) -> dict | bool:
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
                print(f"INFO: {info}")
                # make sure format is an audio stream
                formats = info.get('formats', [])
                for f in formats:
                    if f.get(
                            'acodec'
                    ) != 'none':  # acodec should not be 'none' for audio streams
                        return {"source": f["url"], "title": info["title"]}
                print("No audio stream found")
                return False  # No suitable audio format found
            except Exception as e:
                print(e)
                return False'''

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

    def play_next(self):
        """Plays the next song in the music queue if available; otherwise stops music"""
        if len(self.music_queue) > 0:
            self.is_playing = True

            # get url of next song in queue and remove it from queue
            m_url = self.music_queue[0][0]["source"]
            self.music_queue.pop(0)

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

            self.music_queue.pop(0)
            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS),
                         after=lambda e: self.play_next())
        else:
            self.is_playing = False

    @discord.slash_command(name="play",
                           description="Play the selected song from YouTube")
    async def play(self, ctx, query: str):
        """Allow users to search for songs and play it in their voice chat"""

        voice_channel = ctx.author.voice.channel
        if voice_channel is None:
            await ctx.respond("Connect to a voice channel!")
        elif self.is_paused:
            self.vc.resume()
        else:
            # Search for the song on YT using the provided query
            await ctx.defer()
            song = self.search_yt(query)
            if song == False:  # Check if the search failed
                await ctx.respond(
                    "Could not download the song. Incorrect format, try a different keyword"
                )
            else:
                await ctx.respond("Song added to the queue")

                # add song + voice channel to queue
                self.music_queue.append([song, voice_channel])

                if self.is_playing == False:
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
            self.vc.resume()

    @discord.slash_command(name="resume",
                           description="Resume the current song")
    async def resume(self, ctx):
        """Resume the currently paused song"""
        if self.is_paused:
            self.is_playing = True
            self.is_paused = False
            self.vc.resume()
            await ctx.respond("Music resumed.")

    @discord.slash_command(name="skip", description="Skip the current song")
    async def skip(self, ctx):
        if self.vc != None and self.vc:
            self.vc.stop()
            await self.play_music(ctx)

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
        if self.vc != None and self.is_playing:
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

    @discord.slash_command(name="youtube",
                           description="Ask me if I have YouTube features!")
    async def youtube(self, ctx):
        print("Slash Command: YouTube activated.")
        await ctx.respond("Not yet! Haha 😂")


def setup(bot):
    bot.add_cog(YoutubeCog(bot))
