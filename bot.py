import discord
from discord.ext import commands
import yt_dlp
import asyncio
import validators
from googleapiclient.discovery import build
import os
from dotenv import load_dotenv

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

def isValidUrl(query):
    return validators.url(query)

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
    if not musicQueue:
        return

    next_music = musicQueue.pop(0)  # Sécuriser l'accès à la queue
    audio_url = next_music['url']
    audio_name = next_music['name']
    
    ffmpeg_options = {"options": "-vn"}
    source = discord.FFmpegPCMAudio(audio_url, **ffmpeg_options)

    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()

    await ctx.send(f"🎶 Lecture en cours : **{audio_name}**")

    def after_playing(error):
        if error:
            print(f"Erreur lors de la lecture : {error}")  # Log l'erreur
        if musicQueue:
            # Utilisation de ctx.bot.loop pour s'assurer que l'event loop principal est utilisé
            asyncio.run_coroutine_threadsafe(playNextMusic(ctx), ctx.bot.loop)

    try:
        ctx.voice_client.play(source, after=after_playing)
    except Exception as e:
        await ctx.send(f"❌ Erreur lors de la lecture : {str(e)}")

# Les commandes du bot : 

# Rejoindre un canal vocal
@bot.command()
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
        await ctx.send("❌ vous devez être dans le channel vocal pour effectuer cette action")

# Permet de jouer une musique ou le mettre 
@bot.command()
async def play(ctx, *, param: str = None):
    if param :
        # Faire rejoindre le bot au canal vocal si il n'est pas connecté à un channel
        if ctx.voice_client is None:
            await ctx.invoke(bot.get_command("join"))
                    
        if isInTheVocalChannel(ctx):
            url = None
            if (isValidUrl(param)): 
                url = param
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

                        musicQueue.append({'url': audioUrl, 'name': audioName})  # Ajouter à la queue

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
            await ctx.send("❌ vous devez être dans le channel vocal pour effectuer cette action")

# Commande next pour passer à la chanson suivante
@bot.command()
async def next(ctx):
    if isInTheVocalChannel(ctx):
        if len(musicQueue) > 0:
            await playNextMusic(ctx)
        else:
            # Si la queue est vide, arrêter la musique en cours
            if ctx.voice_client and ctx.voice_client.is_playing():
                ctx.voice_client.stop()
                await ctx.send("❌ Plus de chanson dans la queue.")
    else:
        await ctx.send("❌ vous devez être dans le channel vocal pour effectuer cette action")

# Commande pour afficher la queue des musiques
@bot.command()
async def queue(ctx):
    if isInTheVocalChannel(ctx):
        if len(musicQueue) > 0:
            queue_list = '\n'.join([f" {music['name']}" for music in musicQueue])
            await ctx.send(f"📋 Queue actuelle :\n{queue_list}")
        else:
            await ctx.send("❌ Aucune chanson dans la queue.")
    else:
        await ctx.send("❌ vous devez être dans le channel vocal pour effectuer cette action")
    
# Couper la musique
@bot.command()
async def stop(ctx):
    if isInTheVocalChannel(ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()  # Arrête la lecture en cours
            musicQueue.clear()
            await ctx.send("⏹️ Musique arrêtée.")
        else:
            await ctx.send("❌ Aucune musique en cours de lecture.")
    else:
        await ctx.send("❌ vous devez être dans le channel vocal pour effectuer cette action")
    
# Mettre l'audio sur pause
@bot.command()
async def pause(ctx):
    if isInTheVocalChannel(ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()  # Met la lecture en pause
            await ctx.send("⏸️ Musique mise en pause.")
        else:
            await ctx.send("❌ Aucune musique en cours de lecture.")
    else:
        await ctx.send("❌ vous devez être dans le channel vocal pour effectuer cette action")
        
# Relancer l'audio qui est sur pause
@bot.command()
async def resume(ctx):
    if isInTheVocalChannel(ctx):
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()  # Reprend la lecture
            await ctx.send("▶️ Reprise de la musique.")
        else:
            await ctx.send("❌ Aucune musique en pause.")
    else:
        await ctx.send("❌ vous devez être dans le channel vocal pour effectuer cette action")

# Démarrer le bot
bot.run(TOKEN_BOT_DISCORD)