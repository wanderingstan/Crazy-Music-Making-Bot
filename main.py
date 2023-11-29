from interactions import Client, Intents, listen, File
from interactions import slash_command, SlashContext
from interactions import OptionType, slash_option
import replicate
import aiohttp
import os
import logging
import asyncio
import json
from music_generation import music_generation
from video_generation import (
    generate_video,
    concatenate_videos_async,
    concatenate_videos_with_audio_async,
)
from glif import image_glif, story_glif, chattorio_glif
from dotenv import load_dotenv
import config


# Load environment variables from the .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)



# Discord Bot
bot = Client(intents=Intents.DEFAULT)

# Replicate Client
replicate_client = replicate.Client(api_token=config.REPLICATE_API_TOKEN)


# Return a unique filename prefix for the current user and command
def temp_file_prefix(ctx: SlashContext):
    return config.TEMP_PATH + ctx.user.global_name + "_" + str(ctx.id) + "_"


@slash_command(
    name="music",
    description="Generate some music from text",
    scopes=[config.ACTIVE_CHANNEL_ID],
)
@slash_option(
    name="prompt",
    description="Describe the type of music you would like.",
    required=True,
    opt_type=OptionType.STRING,
)
async def music(ctx, *, prompt: str = ""):
    await ctx.defer()  # Tell discord that we're gonna be a while
    logging.info(f"🔵 Creating music for: {prompt}")

    try:
        logging.info("music_generation")
        mp3_path = await music_generation(config.REPLICATE_API_TOKEN, prompt)
        if mp3_path:
            # await ctx.send(files=File(mp3_path))
            # await ctx.send(prompt)
            await ctx.send_message(content=prompt, file=File(mp3_path))

            if config.DELETE_TEMP_FILES:
                os.path.exists(mp3_path) and os.remove(mp3_path)
        else:
            await ctx.send("An error occurred while generating the music.")

    except Exception as e:
        logging.exception("An error occurred while handling the music request.")
        await ctx.send(f"An error occurred while handling your music request: {e}")


@slash_command(
    name="image",
    description="Generate an image from text",
    scopes=[config.ACTIVE_CHANNEL_ID],
)
@slash_option(
    name="prompt",
    description="Describe the type of image you would like.",
    required=True,
    opt_type=OptionType.STRING,
)
async def image(ctx, *, prompt: str):
    await ctx.defer()  # Tell discord that we're gonna be a while
    logging.info(f"🔵 Creating image for: {prompt}")

    try:
        image_url = await image_glif(prompt)
        if image_url:
            await ctx.send(image_url)  # This will send the image URL directly
            await ctx.send(prompt)

        else:
            await ctx.send("An error occurred or no image URL was returned.")
    except Exception as e:
        logging.exception("An error occurred while handling the image request.")
        await ctx.send(f"An error occurred while handling your image request: {e}")


@slash_command(
    name="video",
    description="Generate a video about a videogame from text",
    scopes=[config.ACTIVE_CHANNEL_ID],
)
@slash_option(
    name="prompt",
    description="Describe the type of retro game you want a video for.",
    required=True,
    opt_type=OptionType.STRING,
)
async def video(ctx, *, prompt: str):
    await ctx.defer()  # Tell discord that we're gonna be a while
    logging.info(f"🔵 Creating video for: {prompt}")

    music_prompt = f"8 bit retro gaming soundtrack for {prompt} game"

    try:
        # Start both glif API and replicate API calls concurrently
        image_path, mp3_path = await asyncio.gather(
            image_glif(prompt),  # Ensure this returns a URL
            music_generation(
                config.REPLICATE_API_TOKEN,
                music_prompt,
                filename_prefix=temp_file_prefix(ctx),
            ),
        )

        # Check if both the image and the music were successfully generated
        if image_path and mp3_path:
            # Generate the video
            video_path = await generate_video(
                image_path, mp3_path, temp_file_prefix(ctx), duration=8
            )

            # Send the video to the Discord channel
            await ctx.send(file=File(video_path))
            await ctx.send(prompt)

            # Clean up the generated files
            if config.DELETE_TEMP_FILES:
                os.path.exists(video_path) and os.remove(video_path)
                os.path.exists(mp3_path) and os.remove(mp3_path)
                os.path.exists(image_path) and os.remove(image_path)
        else:
            await ctx.send("An error occurred while generating the video components.")

    except Exception as e:
        logging.exception(f"An error occurred while handling the video request: {e}")
        await ctx.send(f"An error occurred while handling your video request: {e}")






@slash_command(
    name="film4",
    description="Generate a film from text",
    scopes=[config.ACTIVE_CHANNEL_ID],
)
@slash_option(
    name="prompt",
    description="Describe theme for the game.",
    required=True,
    opt_type=OptionType.STRING,
)
async def film4(ctx, *, prompt: str):
    await ctx.defer()  # Tell discord that we're gonna be a while
    logging.info(f"🔵 Creating film4 for: {prompt}")

    try:
        image_url = await image_glif(prompt)
        if image_url:
            await ctx.send(image_url)  # This will send the image URL directly
            await ctx.send(prompt)

        else:
            await ctx.send("An error occurred or no image URL was returned.")
    except Exception as e:
        logging.exception("An error occurred while handling the image request.")
        await ctx.send(f"An error occurred while handling your image request: {e}")



    # HERE







@slash_command(
    name="film",
    description="Generate a short film from text",
    scopes=[config.ACTIVE_CHANNEL_ID],
)
@slash_option(
    name="prompt",
    description="Describe the scene for your film.",
    required=True,
    opt_type=OptionType.STRING,
)
async def film(ctx, *, prompt: str):
    await ctx.defer()
    logging.info(f"🔵 Creating film for: {prompt}")

    run_path = temp_file_prefix(ctx)

    try:
        (
            image_url_1,
            image_url_2,
            image_url_3,
            image_url_4,
        ), mp3_path = await asyncio.gather(
            story_glif(prompt),  # Ensure this returns a URL
            music_generation(
                config.REPLICATE_API_TOKEN, prompt, filename_prefix=run_path
            ),
        )

        video_path1 = await generate_video(
            image_url_1, mp3_path, temp_file_prefix(ctx) + "1_"
        )
        video_path2 = await generate_video(
            image_url_2, mp3_path, temp_file_prefix(ctx) + "2_"
        )
        video_path3 = await generate_video(
            image_url_3, mp3_path, temp_file_prefix(ctx) + "3_"
        )
        video_path4 = await generate_video(
            image_url_4, mp3_path, temp_file_prefix(ctx) + "4_"
        )
        # await ctx.send(file=File(video_path1))
        # await ctx.send(file=File(video_path2))
        # await ctx.send(file=File(video_path3))
        # await ctx.send(file=File(video_path4))

        concat_video_path = await concatenate_videos_async(
            [video_path1, video_path2, video_path3, video_path4],
            run_path + "concat.mp4",
        )
        await ctx.send(file=File(concat_video_path))
        await ctx.send(prompt)

    except Exception as e:
        logging.exception("An error occurred while handling the image request.")
        await ctx.send(f"An error occurred while handling your image request: {e}")


@slash_command(
    name="film2",
    description="Generate a short film from text",
    scopes=[config.ACTIVE_CHANNEL_ID],
)
@slash_option(
    name="prompt",
    description="Describe the scene for your film.",
    required=True,
    opt_type=OptionType.STRING,
)
@slash_option(
    name="duration",
    description="How many seconds film should last.",
    required=False,
    opt_type=OptionType.INTEGER,
)
async def film2(ctx, *, prompt: str, duration: int = 12):
    await ctx.defer()
    logging.info(f"🔵 Creating film for: {prompt}")

    film_duration_s = float(duration)

    run_path = temp_file_prefix(ctx)

    try:
        (
            image_url_1,
            image_url_2,
            image_url_3,
            image_url_4,
        ), mp3_path = await asyncio.gather(
            story_glif(prompt),  # Ensure this returns a URL
            music_generation(
                config.REPLICATE_API_TOKEN,
                prompt,
                filename_prefix=run_path,
                duration=film_duration_s,
            ),
        )

        video_path1 = await generate_video(
            image_url_1,
            None,
            temp_file_prefix(ctx) + "1_",
            duration=film_duration_s / 4,
        )
        video_path2 = await generate_video(
            image_url_2,
            None,
            temp_file_prefix(ctx) + "2_",
            duration=film_duration_s / 4,
        )
        video_path3 = await generate_video(
            image_url_3,
            None,
            temp_file_prefix(ctx) + "3_",
            duration=film_duration_s / 4,
        )
        video_path4 = await generate_video(
            image_url_4,
            None,
            temp_file_prefix(ctx) + "4_",
            duration=film_duration_s / 4,
        )
        # await ctx.send(file=File(video_path1))
        # await ctx.send(file=File(video_path2))
        # await ctx.send(file=File(video_path3))
        # await ctx.send(file=File(video_path4))

        logging.info("concatenate_videos_with_audio_async")
        concat_video_path = await concatenate_videos_with_audio_async(
            video_path1,
            video_path2,
            video_path3,
            video_path4,
            mp3_path,
            run_path + "concat.mp4",
        )
        await ctx.send(prompt)
        await ctx.send(file=File(concat_video_path))
        logging.info(f"🟢 Finished creating film for: {prompt}")

    except Exception as e:
        logging.exception("An error occurred while handling the image request.")
        await ctx.send(f"An error occurred while handling your image request: {e}")


@slash_command(
    name="chattorio",
    description="Make a chattorio move",
    scopes=[config.ACTIVE_CHANNEL_ID],
)
@slash_option(
    name="action",
    description="Describe your action.",
    required=True,
    opt_type=OptionType.STRING,
)
@slash_option(
    name="glif_id",
    description="ID of Glif to use going forward. (Advanced)",
    required=False,
    opt_type=OptionType.STRING,
)
@slash_option(
    name="inventory",
    description="Manually set your inventory, i.e. cheat. (Advanced)",
    required=False,
    opt_type=OptionType.STRING,
)

async def chattorio(ctx, *, action: str, glif_id: str = None, inventory: str = None):
    await ctx.defer()
    logging.info(f"🔵 Doing chattorio for: {action}")

    run_path = temp_file_prefix(ctx)

    player_id = ctx.user.global_name

    try:
        start_state, narrator, reasoning, image, updated_state = await chattorio_glif(
            action_input_text=action, player_id=player_id, glif_id=glif_id, inventory=inventory
        )
        if not narrator:
            await ctx.send("An error occurred in chattorio.")
            return

        if image:
            await ctx.send(image) # Should be a URL
            
        await ctx.send(
            ""
            + "## Game update:\n"
            + narrator
            + "\n## Inventory:\n"
            + updated_state["game_state"]
            + "||"
            + "\n*Reasoning:*\n"
            + reasoning
            + "\n*Start state:*\n"
            + "```\n"
            + json.dumps(start_state, indent=4)
            + "```\n"
            + "*New state:*"
            + "```\n"
            + json.dumps(updated_state, indent=4)
            + "```\n"
            + "||"
        )
        logging.info("🟢" + f" Finished chattorio move for {player_id} performing {action})")

    except Exception as e:
        logging.exception("An error occurred while handling the chattorio request.")
        await ctx.send(f"An error occurred while handling your chattorio request: {e}")


@listen()  # this decorator tells snek that it needs to listen for the corresponding event, and run this coroutine
async def on_ready():
    # This event is called when the bot is ready to respond to commands
    logging.info("🔵 🔵 🔵 🔵 🔵 discord-gamebot-experiment")
    logging.info(f"This bot is owned by {bot.owner}")


bot.start(config.TOKEN)
