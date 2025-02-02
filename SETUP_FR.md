# Guide de Création d'un Bot Discord Musique avec YouTube

## Étape 1 : Générer une clé API YouTube

1. Rendez-vous sur la [documentation de l'API YouTube](https://developers.google.com/youtube/v3/getting-started?hl=fr).
2. Créez un projet dans Google Cloud Console.
3. Activez l'API YouTube Data API v3 pour votre projet.
4. Allez dans la section **Identifiants** et générez une **clé API**.
5. Conservez cette clé, car vous en aurez besoin pour interagir avec l'API YouTube dans votre bot.

## Étape 2 : Créer un Bot Discord

1. Allez sur le [portail des développeurs Discord](https://discord.com/developers/docs/intro).
2. Créez une **nouvelle application**.
3. Dans l'onglet **Bot**, cliquez sur **Add Bot** (Ajouter un bot).
4. Copiez le **Token** de votre bot. Ce token sera utilisé pour authentifier votre bot.
5. Activez les **Intentions Privées** (Presence + Server Members) dans les paramètres du bot.
6. Allez dans l'onglet **OAuth2** > **URL Generator**, sélectionnez **bot** et les permissions **"Connect"** et **"Speak"**.
7. Générez l'URL et invitez votre bot sur votre serveur Discord.

## Étape 3 : Préparer le fichier `bot.py`

Téléchargez ou créez votre fichier `bot.py` qui contiendra le code de votre bot. Le fichier doit inclure la logique pour se connecter à Discord, récupérer les vidéos YouTube et les jouer dans un salon vocal.

## Étape 4 : Créer un fichier `.env`

1. Créez un fichier **`.env`** dans le répertoire où se trouve votre fichier `bot.py`.
2. Ajoutez les lignes suivantes à votre fichier `.env` pour stocker en toute sécurité votre **token Discord** et votre **clé API YouTube** :

```env
TOKEN_BOT_DISCORD=VOTRE_TOKEN_DISCORD
API_GOOGLE_KEY=VOTRE_CLE_API_GOOGLE
```

## Étape 5 : Installation des modules nécessaires

### 1. Modules à installer
- **Discord.py** : Bibliothèque pour interagir avec l'API Discord.
- **yt-dlp** : Bibliothèque pour télécharger les vidéos YouTube.
- **google-api-python-client** : Bibliothèque pour interagir avec l'API YouTube.
- **python-dotenv** : Bibliothèque pour gérer les variables d'environnement.
- **re** : Module natif de Python pour les expressions régulières.

### 2. Installation sous Windows
1. Installer Python : [Télécharger Python pour Windows](https://www.python.org/downloads/windows/).
2. Ouvrez PowerShell ou Command Prompt et exécutez les commandes suivantes pour installer les modules nécessaires :
    ```bash
    pip install discord.py
    pip install yt-dlp
    pip install google-api-python-client
    pip install python-dotenv
    pip install re
    ```

### 3. Installation sous Linux
1. Installez Python et pip via les commandes suivantes dans votre terminal :
    ```bash
    sudo apt install python3
    sudo apt install python3-pip
    ```
2. Ensuite, installez les bibliothèques nécessaires en exécutant ces commandes :
    ```bash
    pip3 install discord.py
    pip3 install yt-dlp
    pip3 install google-api-python-client
    pip3 install python-dotenv
    pip3 install re
    ```

## Étape 6 : Exécuter votre Bot
Exécutez votre bot en utilisant la commande suivante dans le répertoire contenant votre fichier `botFR.py` :
```bash
python bot.py
```
Si tout fonctionne correctement, votre bot devrait maintenant être en ligne sur Discord et prêt à jouer de la musique à partir de YouTube.

### Commandes du bot :
- `!play <TITRE/URL youtube>` ou `!p <TITRE/URL youtube>` : Permet de jouer une vidéo YouTube (musique).
- `!queue` ou `!q` : Permet de voir le contenu de la file d'attente des musiques.
- `!join` ou `!j` : Permet de faire rejoindre le bot dans le salon vocal auquel vous êtes actuellement connecté.
- `!leave` : Permet de faire quitter le bot de Discord.
- `!stop` : Arrêter la musique et vider le contenu de la queue.
- `!pause` : Mettre la musique actuelle sur pause.
- `!resume` : Relancer la musique qui était en pause.
- `!playQueue <numéro dans la queue>` : Jouer un son de la queue avec son indice dans la file d'attente.

Ces commandes permettent de gérer facilement la lecture musicale sur votre serveur Discord. Assurez-vous que le bot a les bonnes permissions pour rejoindre les salons vocaux et gérer l'audio.
