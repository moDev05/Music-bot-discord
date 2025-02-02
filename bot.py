import discord
from discord.ext import commands
import yt_dlp
import asyncio
from googleapiclient.discovery import build
import os
from dotenv import load_dotenv
import re
from urllib.parse import urlparse, parse_qs

#  text constant
NOT_IN_CHANNEL_EROR_MESSAGE = "❌ vous devez être dans le channel vocal pour effectuer cette action"
NO_MUSIC_PLAYING_MESSAGE = "❌ Aucune musique en cours de lecture."

# Charger les variable depuis le fichier .env (du répertoir courant)
load_dotenv()

# Récupération des deux clé API nécessaire, celle de l'api youtube et celle du bot discord
TOKEN_BOT_DISCORD = os.getenv("TOKEN_BOT_DISCORD")
API_GOOGLE_KEY = os.getenv("API_GOOGLE_KEY")

# Permet de conserver les musiques dans une queue
musicQueue = []

# Paramétrages du bot discord 
intents = discord.Intents.default()
intents.message_content = True  # Activer la lecture des messages (pour pouvoir récupérer le contenu des messages)
bot = commands.Bot(command_prefix="!", intents=intents)

# Fonctions hors commandes discord : 

def isInTheVocalChannel(ctx):
    # Vérifie si l'auteur est dans un canal vocal et si le bot est dans le même canal vocal
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
        return False  # L'URL ne correspond pas à une vidéo YouTube
    
def isPlaylist(url):
    # Vérifier si l'URL contient un paramètre "list=" (playlist)
    parsedUrl = urlparse(url)
    queryParams = parse_qs(parsedUrl.query)
    
    return "list" in queryParams  # Retourne False si une playlist est détectée

def searchOnYoutube(query):
    youtube = build('youtube', 'v3', developerKey=API_GOOGLE_KEY)
    
    # Effectuer la recherche
    request = youtube.search().list(
        q=query,
        part='snippet',
        type='video',
        maxResults=1 
    )
    response = request.execute()
    
    # Récupérer l'ID de la première vidéo trouvée
    if response['items']:
        video_id = response['items'][0]['id']['videoId']
        video_url = f'https://www.youtube.com/watch?v={video_id}'
        return video_url
    else:
        return None
    
# Permet de jouer les musiques de la queu
async def playNextMusic(ctx):
    voice_client = ctx.voice_client

    # Vérifie si le bot est toujours connecté et ne joue pas déjà une musique
    if not voice_client or voice_client.is_playing() or voice_client.is_paused():
        return  

    if not musicQueue:
        return

    nextMusic = musicQueue.pop(0)
    audioUrl = nextMusic['url']
    audioName = nextMusic['name']

    ffmpegOptions = {"options": "-vn"}
    source = discord.FFmpegPCMAudio(audioUrl, **ffmpegOptions)

    await ctx.send(f"🎶 Lecture en cours : **{audioName}**")

    def after_playing(error):
        if error:
            print(f"Erreur lors de la lecture : {error}")  

        # Vérifie s'il reste des musiques et joue la suivante
        if musicQueue:
            coro = playNextMusic(ctx)
            fut = asyncio.run_coroutine_threadsafe(coro, ctx.bot.loop)
            try:
                fut.result()  # Attend la fin de l'exécution pour capturer les erreurs éventuelles
            except Exception as e:
                print(f"Erreur lors du lancement de la musique suivante : {e}")

    try:
        voice_client.play(source, after=after_playing)  # Détection automatique de la fin de la lecture
    except Exception as e:
        await ctx.send(f"❌ Erreur lors de la lecture : {str(e)}")

# Les commandes du bot : 

# Rejoindre un canal vocal
@bot.command(name='j')
@bot.command(name='join')
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send(f"🔊 Connecté à {channel.name}")
    else:
        await ctx.send("❌ Tu dois être dans un canal vocal !")
        
# Quitter un canal vocal
@bot.command()
async def leave(ctx):
    if isInTheVocalChannel(ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("👋 Déconnecté du vocal ! À plus tard.")
    else :
        await ctx.send(NOT_IN_CHANNEL_EROR_MESSAGE)

# Permet de jouer une musique ou le mettre 
@bot.command(name='p')
@bot.command(name='play')
async def play(ctx, *, param: str = None):
    if param :
        # Faire rejoindre le bot au canal vocal si il n'est pas connecté à un channel
        if ctx.voice_client is None:
            await ctx.invoke(bot.get_command("join"))
                    
        if isInTheVocalChannel(ctx):
            url = None
            if (isValidUrl(param)): 
                url = param
                if (isPlaylist()):
                    await ctx.send("❌ Les playlist ne sont pas autorisés.")
                    return
            else:
                url = searchOnYoutube(param)
                
            if url :
                # Options yt-dlp
                ydl_opts = {"format": "bestaudio/best", "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}]}

                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=False)
                        if not info:  # Vérifie si 'info' est None
                            await ctx.send("❌ Impossible de récupérer l'information de cette URL.")
                            return

                        audioUrl = info.get("url")  # Utilise .get() pour éviter les KeyError
                        audioName = info.get("title", "Aucun titre")  # Si le titre est absent

                        if not audioUrl:  # Vérifie si l'URL audio est récupérable
                            await ctx.send("❌ Impossible d'extraire l'audio de cette URL.")
                            return

                        musicQueue.append({'url': audioUrl, 'name': audioName})  # Ajouté à la queue

                    # Si c'est la seule chanson, la jouer immédiatement
                    if len(musicQueue) == 1 and not ctx.voice_client.is_playing():
                        await playNextMusic(ctx)
                    else:
                        await ctx.send(f"🎶 {audioName} ajouté à la queue.")

                except yt_dlp.utils.DownloadError:
                    await ctx.send("❌ Une erreur est survenu.")
                    return
                except Exception as e:
                    print(f"Erreur dans la commande play: {e}")
                    return
        else :
            await ctx.send(NOT_IN_CHANNEL_EROR_MESSAGE)

# Commande next pour passer à la chanson suivante
@bot.command(name='n')
@bot.command(name='next')
async def next(ctx):
    if isInTheVocalChannel(ctx):
        ctx.voice_client.stop()
        if len(musicQueue) > 0:
            return
        else:
            await ctx.send("❌ Plus de chanson dans la queue.")
    else:
        await ctx.send(NOT_IN_CHANNEL_EROR_MESSAGE)

@bot.command(name='q')
@bot.command(name='queue')
async def queue(ctx):
    if isInTheVocalChannel(ctx):
        if len(musicQueue) > 0:
            queueList = '\n'.join([f"{idx + 1}. {music['name']}" for idx, music in enumerate(musicQueue)])
            await ctx.send(f"📋 Queue actuelle :\n{queueList}")
        else:
            await ctx.send("❌ Aucune chanson dans la queue.")
    else:
        await ctx.send(NOT_IN_CHANNEL_EROR_MESSAGE)
    
@bot.command()
async def stop(ctx):
    if isInTheVocalChannel(ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()  # Arrête la lecture en cours
            musicQueue.clear()
            await ctx.send("⏹️ Musique arrêtée.")
        else:
            await ctx.send(NO_MUSIC_PLAYING_MESSAGE)
    else:
        await ctx.send(NOT_IN_CHANNEL_EROR_MESSAGE)
    
@bot.command()
async def pause(ctx):
    if isInTheVocalChannel(ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()  # Met la lecture en pause
            await ctx.send("⏸️ Musique mise en pause.")
        else:
            await ctx.send(NO_MUSIC_PLAYING_MESSAGE)
    else:
        await ctx.send(NOT_IN_CHANNEL_EROR_MESSAGE)
        
@bot.command()
async def resume(ctx):
    if isInTheVocalChannel(ctx):
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()  # Reprend la lecture
            await ctx.send("▶️ Reprise de la musique.")
        else:
            await ctx.send("❌ Aucune musique en pause.")
    else:
        await ctx.send(NOT_IN_CHANNEL_EROR_MESSAGE)

# Démarrer le bot
bot.run(TOKEN_BOT_DISCORD)