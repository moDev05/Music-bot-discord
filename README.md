# Discord Music Bot

## Overview
This is an open-source Discord Music Bot developed by me. The bot allows you to play music from YouTube in Discord voice channels. It features commands for managing the music queue, pausing, resuming, and more.

The bot uses the YouTube Data API to search for music videos and the yt-dlp library to download and stream them to your Discord server.

## Features
- Play music from YouTube using the `!play <TITLE/URL>` command.
- View the music queue with `!queue` or `!q`.
- Join or leave voice channels with `!join` and `!leave`.
- Control playback with `!pause`, `!resume`, and `!stop`.
- Play a specific song from the queue using `!playQueue <queue number>`.

## Setup and Deployment

The source files contain two README files: one in **French** and one in **English**, detailing how to deploy the bot from A to Z.

1. The **French README** explains everything in French, covering bot installation, setup, and configuration steps.
2. The **English README** provides the same detailed instructions in English.

Make sure to follow the instructions in either README to properly set up the bot on your server.

## Installation
You will need to install the following dependencies:

- `discord.py`: For interacting with the Discord API.
- `yt-dlp`: For downloading YouTube videos.
- `google-api-python-client`: For working with the YouTube API.
- `python-dotenv`: To manage environment variables like the Discord token and YouTube API key.
- `re`: A native Python module for regular expressions.

Follow the steps outlined in the README files to install and configure the necessary modules.

## Contributing
Feel free to contribute to the project by opening issues, submitting pull requests, or improving the documentation. This is an open-source project, and contributions are always welcome!
