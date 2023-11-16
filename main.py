from interactions import Client, Intents, listen, File
from interactions import slash_command, SlashContext
from interactions import OptionType, slash_option
import replicate
import aiohttp
import os
import logging
import asyncio
from music_generation import music_generation
from video_generation import generate_video
from glif import call_glif_api, call_glif_story_api
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

logging.basicConfig(level=logging.INFO)

# Environment Variables
TOKEN = os.getenv("DISCORD_TOKEN")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
ACTIVE_CHANNEL_ID = os.getenv("ACTIVE_CHANNEL_ID")
TEMP_PATH = "temp_files/"

# Test if we have valid keys
# Check if TOKEN is valid
if not TOKEN:
    raise ValueError("DISCORD_TOKEN environment variable is not set or empty.")

# Check if REPLICATE_API_TOKEN is valid
if not REPLICATE_API_TOKEN:
    raise ValueError("REPLICATE_API_TOKEN environment variable is not set or empty.")

# Check if ACTIVE_CHANNEL_ID is valid
if not ACTIVE_CHANNEL_ID:
    raise ValueError("ACTIVE_CHANNEL_ID environment variable is not set or empty.")

if not os.path.exists(TEMP_PATH):
    raise ValueError("TEMP_PATH variable points to non existant directory.")

# Discord Bot
bot = Client(intents=Intents.DEFAULT)

# Replicate Client
replicate_client = replicate.Client(api_token=REPLICATE_API_TOKEN)


@slash_command(
    name="music",
    description="Generate some music from text",
    scopes=[ACTIVE_CHANNEL_ID],
)
async def music(ctx, *, text: str = ""):
    try:
        logging.info("music_generation")
        mp3_path = await music_generation(text)
        if mp3_path:
            async with ctx.typing():
                await ctx.send(files=File(mp3_path))
                os.remove(mp3_path)
        else:
            await ctx.send("An error occurred while generating the music.")

    except Exception as e:
        logging.exception("An error occurred while handling the music request.")
        await ctx.send(f"An error occurred while handling your music request: {e}")


@slash_command(
    name="image",
    description="Generate an image from text",
    scopes=[ACTIVE_CHANNEL_ID],
)
async def image(ctx, *, text: str):
    try:
        image_url = await call_glif_api(text)
        if image_url:
            await ctx.send(image_url)  # This will send the image URL directly
        else:
            await ctx.send("An error occurred or no image URL was returned.")
    except Exception as e:
        logging.exception("An error occurred while handling the image request.")
        await ctx.send(f"An error occurred while handling your image request: {e}")


@slash_command(
    name="comic",
    description="Generate a comic from text",
    scopes=[ACTIVE_CHANNEL_ID],
)
@slash_option(
    name="prompt",
    description="Describe the type of retro game you want a video for.",
    required=True,
    opt_type=OptionType.STRING,
)
async def image(ctx, *, prompt: str):
    await ctx.defer()

    try:
        image_url_1, image_url_2, image_url_3, image_url_4 = await call_glif_story_api(prompt)
        await ctx.send(image_url_1)  # This will send the image URL directly
        await ctx.send(image_url_2)  # This will send the image URL directly
        await ctx.send(image_url_3)  # This will send the image URL directly
        await ctx.send(image_url_4)  # This will send the image URL directly
    except Exception as e:
        logging.exception("An error occurred while handling the image request.")
        await ctx.send(f"An error occurred while handling your image request: {e}")


@slash_command(
    name="video",
    description="Generate a video from text",
    scopes=[ACTIVE_CHANNEL_ID],
)
@slash_option(
    name="prompt",
    description="Describe the type of retro game you want a video for.",
    required=True,
    opt_type=OptionType.STRING,
)
async def video(ctx, *, prompt: str):
    await ctx.defer()

    try:
        # Start both glif API and replicate API calls concurrently
        image_path, mp3_path = await asyncio.gather(
            call_glif_api(prompt),  # Ensure this returns a local file path
            music_generation(
                prompt, filename_prefix=TEMP_PATH
            ),  # Ensure this returns a local file path
        )

        # Check if both the image and the music were successfully generated
        if image_path and mp3_path:
            # Generate the video
            video_path = await generate_video(image_path, mp3_path, TEMP_PATH)

            # Send the video to the Discord channel
            await ctx.send(file=File(video_path))

            # Clean up the generated files
            # os.path.exists(video_path) and os.remove(video_path)
            # os.path.exists(mp3_path) and os.remove(mp3_path)
            # os.path.exists(image_path) and os.remove(image_path)
        else:
            await ctx.send("An error occurred while generating the video components.")

    except Exception as e:
        logging.exception(f"An error occurred while handling the video request: {e}")
        await ctx.send(f"An error occurred while handling your video request: {e}")




@listen()  # this decorator tells snek that it needs to listen for the corresponding event, and run this coroutine
async def on_ready():
    # This event is called when the bot is ready to respond to commands
    logging.info("Ready")
    logging.info(f"This bot is owned by {bot.owner}")


bot.start(TOKEN)
