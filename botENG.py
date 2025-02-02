import discord
from discord.ext import commands
import yt_dlp
import asyncio
from googleapiclient.discovery import build
import os
from dotenv import load_dotenv
import re
from urllib.parse import urlparse, parse_qs

# text constant
NOT_IN_CHANNEL_ERROR_MESSAGE = "❌ You must be in a voice channel to perform this action."
NO_MUSIC_PLAYING_MESSAGE = "❌ No music is currently playing."

# Load environment variables from the .env file (current directory)
load_dotenv()

# Retrieve the necessary API keys, both YouTube API key and Discord bot token
TOKEN_BOT_DISCORD = os.getenv("TOKEN_BOT_DISCORD")
API_GOOGLE_KEY = os.getenv("API_GOOGLE_KEY")

# To store music in a queue
musicQueue = []

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True  # Enable message reading (to capture message content)
bot = commands.Bot(command_prefix="!", intents=intents)

# Functions outside of Discord commands:

def isInTheVocalChannel(ctx):
    # Check if the author is in a voice channel and if the bot is in the same voice channel
    if ctx.author.voice and ctx.voice_client:
        return ctx.author.voice.channel == ctx.voice_client.channel
    return False

def isValidUrl(url):
    youtube_regex = re.compile(
        r"^(https?://)?(www\.)?"
        r"(youtube\.com|youtu\.be)/"
        r"(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})"
    )
    
    match = youtube_regex.match(url)
    if not match:
        return False  # URL doesn't match a YouTube video
    return True
    
def isPlaylist(url):
    # Check if the URL contains a "list=" parameter (playlist)
    parsedUrl = urlparse(url)
    queryParams = parse_qs(parsedUrl.query)
    
    print(queryParams)
    return "list" in queryParams  # Returns True if a playlist is detected

def searchOnYoutube(query):
    youtube = build('youtube', 'v3', developerKey=API_GOOGLE_KEY)
    
    # Perform the search
    request = youtube.search().list(
        q=query,
        part='snippet',
        type='video',
        maxResults=1 
    )
    response = request.execute()
    
    # Get the ID of the first found video
    if response['items']:
        video_id = response['items'][0]['id']['videoId']
        video_url = f'https://www.youtube.com/watch?v={video_id}'
        return video_url
    else:
        return None
    
# Function to play music from the queue
async def playNextMusic(ctx):
    voice_client = ctx.voice_client

    # Check if the bot is still connected and not already playing music
    if not voice_client or voice_client.is_playing() or voice_client.is_paused():
        return  

    if not musicQueue:
        return

    nextMusic = musicQueue.pop(0)
    audioUrl = nextMusic['url']
    audioName = nextMusic['name']

    ffmpegOptions = {"options": "-vn"}
    source = discord.FFmpegPCMAudio(audioUrl, **ffmpegOptions)

    await ctx.send(f"🎶 Now playing: **{audioName}**")

    def after_playing(error):
        if error:
            print(f"Error during playback: {error}")  

        # Check if there are more songs and play the next one
        if musicQueue:
            coro = playNextMusic(ctx)
            fut = asyncio.run_coroutine_threadsafe(coro, ctx.bot.loop)
            try:
                fut.result()  # Wait for completion to capture any potential errors
            except Exception as e:
                print(f"Error during the next song playback: {e}")

    try:
        voice_client.play(source, after=after_playing)  # Automatically detects when the song ends
    except Exception as e:
        await ctx.send(f"❌ Error during playback: {str(e)}")

# Bot commands:

# Join a voice channel
@bot.command(name='j', aliases=['join'])
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send(f"🔊 Connected to {channel.name}")
    else:
        await ctx.send("❌ You must be in a voice channel!")

# Leave a voice channel
@bot.command()
async def leave(ctx):
    if isInTheVocalChannel(ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("👋 Disconnected from the voice channel! See you later.")
    else:
        await ctx.send(NOT_IN_CHANNEL_ERROR_MESSAGE)

# Play a song or add it to the queue
@bot.command(name='p', aliases=['play'])
async def play(ctx, *, param: str = None):
    if param:
        # Make the bot join the voice channel if not already connected
        if ctx.voice_client is None:
            await ctx.invoke(bot.get_command("join"))
        
        if isInTheVocalChannel(ctx):
            processingMessage = await ctx.send("⌛ Processing... ")
            url = None
            if (isValidUrl(param)): 
                url = param
                if (isPlaylist(url)):
                    await ctx.send("❌ Playlists are not allowed.")
                    return
            else:
                url = searchOnYoutube(param)
                
            if url:
                # yt-dlp options
                ydl_opts = {"format": "bestaudio/best", "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}]}

                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=False)
                        if not info:  # Check if 'info' is None
                            await ctx.send("❌ Unable to retrieve information from this URL.")
                            return

                        audioUrl = info.get("url")  # Use .get() to avoid KeyError
                        audioName = info.get("title", "No title")  # Default to "No title" if missing

                        if not audioUrl:  # Check if the audio URL is retrievable
                            await ctx.send("❌ Unable to extract audio from this URL.")
                            return

                        musicQueue.append({'url': audioUrl, 'name': audioName})  # Added to the queue

                    # If it's the only song, play it immediately
                    await processingMessage.delete()
                    if len(musicQueue) == 1 and not ctx.voice_client.is_playing():
                        await playNextMusic(ctx)
                    else:
                        await ctx.send(f"🎶 {audioName} added to the queue.")

                except yt_dlp.utils.DownloadError:
                    await ctx.send("❌ An error occurred.")
                    return
                except Exception as e:
                    print(f"Error in the play command: {e}")
                    return
        else:
            await ctx.send(NOT_IN_CHANNEL_ERROR_MESSAGE)

# Command to skip to the next song
@bot.command(name='n', aliases=['next'])
async def next(ctx):
    if isInTheVocalChannel(ctx):
        ctx.voice_client.stop()
        if len(musicQueue) > 0:
            return
        else:
            await ctx.send("❌ No more songs in the queue.")
    else:
        await ctx.send(NOT_IN_CHANNEL_ERROR_MESSAGE)

@bot.command(name='q', aliases=['queue'])
async def queue(ctx):
    if isInTheVocalChannel(ctx):
        if len(musicQueue) > 0:
            queueList = '\n'.join([f"{idx + 1}. {music['name']}" for idx, music in enumerate(musicQueue)])
            await ctx.send(f"📋 Current queue:\n{queueList}")
        else:
            await ctx.send("❌ No songs in the queue.")
    else:
        await ctx.send(NOT_IN_CHANNEL_ERROR_MESSAGE)
    
@bot.command()
async def stop(ctx):
    if isInTheVocalChannel(ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()  # Stop current playback
            musicQueue.clear()
            await ctx.send("⏹️ Music stopped.")
        else:
            await ctx.send(NO_MUSIC_PLAYING_MESSAGE)
    else:
        await ctx.send(NOT_IN_CHANNEL_ERROR_MESSAGE)
    
@bot.command()
async def pause(ctx):
    if isInTheVocalChannel(ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()  # Pause current playback
            await ctx.send("⏸️ Music paused.")
        else:
            await ctx.send(NO_MUSIC_PLAYING_MESSAGE)
    else:
        await ctx.send(NOT_IN_CHANNEL_ERROR_MESSAGE)
        
@bot.command()
async def resume(ctx):
    if isInTheVocalChannel(ctx):
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()  # Resume playback
            await ctx.send("▶️ Music resumed.")
        else:
            await ctx.send("❌ No music is paused.")
    else:
        await ctx.send(NOT_IN_CHANNEL_ERROR_MESSAGE)
        
@bot.command()
async def playQueue(ctx, idx: str):
    if isInTheVocalChannel(ctx):
        try:
            index = int(idx)
            index -= 1
        except ValueError:
            await ctx.send(f"❌ The index {index} is invalid. The value must be between 1 and {len(musicQueue)}.")
            return
        
        if index < 0 or index >= len(musicQueue):
            await ctx.send(f"❌ The index {index} is invalid. The value must be between 1 and {len(musicQueue)}.")
            return
        
        # Get the music in question
        element = musicQueue[index]

        # Remove the song and add it to the front of the queue
        musicQueue.pop(index)
        musicQueue.insert(0, element)
        
        await ctx.invoke(bot.get_command("next"))
        
    else:
        await ctx.send(NOT_IN_CHANNEL_ERROR_MESSAGE)

# Start the bot
bot.run(TOKEN_BOT_DISCORD)
