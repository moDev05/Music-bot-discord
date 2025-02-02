# Guide to Creating a Discord Music Bot with YouTube

## Step 1: Generate a YouTube API Key

1. Visit the [YouTube API documentation](https://developers.google.com/youtube/v3/getting-started?hl=en).
2. Create a project in the Google Cloud Console.
3. Enable the YouTube Data API v3 for your project.
4. Go to the **Credentials** section and generate an **API Key**.
5. Keep this key safe as you'll need it to interact with the YouTube API in your bot.

## Step 2: Create a Discord Bot

1. Go to the [Discord Developer Portal](https://discord.com/developers/docs/intro).
2. Create a **new application**.
3. In the **Bot** tab, click **Add Bot**.
4. Copy your **Bot Token**. This token will be used to authenticate your bot.
5. Enable **Privileged Intents** (Presence + Server Members) in the bot's settings.
6. Go to the **OAuth2** tab > **URL Generator**, select **bot** and the **"Connect"** and **"Speak"** permissions.
7. Generate the URL and invite your bot to your Discord server.

## Step 3: Prepare the `bot.py` File

Download or create your `bot.py` file, which will contain the code for your bot. The file should include the logic to connect to Discord, retrieve YouTube videos, and play them in a voice channel.

## Step 4: Create a `.env` File

1. Create a **`.env`** file in the same directory as your `bot.py` file.
2. Add the following lines to your `.env` file to securely store your **Discord token** and **YouTube API key**:

```env
TOKEN_BOT_DISCORD=YOUR_DISCORD_TOKEN
API_GOOGLE_KEY=YOUR_GOOGLE_API_KEY
```

## Step 5: Install Required Modules

### 1. Modules to Install
- **Discord.py**: Library to interact with the Discord API.
- **yt-dlp**: Library to download YouTube videos.
- **google-api-python-client**: Library to interact with the YouTube API.
- **python-dotenv**: Library to manage environment variables.
- **re**: Native Python module for regular expressions.

### 2. Installation on Windows
1. Install Python: [Download Python for Windows](https://www.python.org/downloads/windows/).
2. Open PowerShell or Command Prompt and run the following commands to install the required modules:
    ```bash
    pip install discord.py
    pip install yt-dlp
    pip install google-api-python-client
    pip install python-dotenv
    pip install re
    ```

### 3. Installation on Linux
1. Install Python and pip using the following commands in your terminal:
    ```bash
    sudo apt install python3
    sudo apt install python3-pip
    ```
2. Then, install the required libraries by running these commands:
    ```bash
    pip3 install discord.py
    pip3 install yt-dlp
    pip3 install google-api-python-client
    pip3 install python-dotenv
    pip3 install re
    ```

## Step 6: Run Your Bot
Run your bot using the following command in the directory containing your `botENG.py` file:
```bash
python bot.py
```
If everything works correctly, your bot should now be online on Discord and ready to play music from YouTube.

### Bot Commands :
- `!play <TITLE/Youtube URL>` or `!p <TITLE/Youtube URL>` : Play a YouTube video (music).
- `!queue` or `!q`: View the content of the music queue.
- `!join` or `!j`: Make the bot join the voice channel you are currently connected to.
- `!leave`: Make the bot leave Discord.
- `!stop`: Stop the music and clear the queue.
- `!pause`: Pause the current music.
- `!resume`: Resume the music that was paused.
- `!playQueue <queue number>`: Play a song from the queue by its index.

These commands allow easy management of music playback on your Discord server. Make sure the bot has the correct permissions to join voice channels and manage audio.