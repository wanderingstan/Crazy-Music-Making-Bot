import discord
from discord.ext import commands

import replicate
import aiohttp
import os
import logging
import asyncio
from sound_generation import generate_and_download_music
from music_generation import music_generation
from video_generation import generate_video
from glif import call_glif_api

logging.basicConfig(level=logging.INFO)

# Environment Variables
TOKEN = os.getenv('mydiscordtoken')
REPLICATE_API_TOKEN = os.getenv('REPLICATE_API_TOKEN')
ACTIVE_CHANNEL_ID = os.getenv('ACTIVE_CHANNEL_ID')
TEMP_PATH = "temp_files/"
# ACTIVE_CHANNEL_ID = "988352005569384518"  # Replace with your channel ID

# Discord Bot Intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

# Replicate Client
replicate_client = replicate.Client(api_token=REPLICATE_API_TOKEN)


# async def generate_music(prompt,
#                          duration="5.0",
#                          guidance_scale=2.5,
#                          n_candidates=3):
#   fullprompt = f"8 bit nintendo style gaming music with {prompt}"

#   output = replicate_client.run(
#     "haoheliu/audio-ldm:b61392adecdd660326fc9cfc5398182437dbe5e97b5decfb36e1a36de68b5b95",
#     input={
#       "text": fullprompt,
#       "duration": duration,
#       "guidance_scale": guidance_scale,
#       "n_candidates": n_candidates
#     })

#   if output is None:
#     raise Exception("No output was returned from the model.")

#   # Assuming the model returns a URL
#   return output
async def download_music(url: str) -> str:
  logging.info("Starting download of music.")
  async with aiohttp.ClientSession() as session:
    async with session.get(url) as response:
      if response.status == 200:
        music_filename = 'temp_music.mp3'
        with open(music_filename, 'wb') as f:
          f.write(await response.read())
        logging.info("Music downloaded successfully.")
        return music_filename
      else:
        logging.error(f"Error downloading music: {response.status}")
        return ''


# @bot.command()
# async def inspo(ctx, *, text: str):
#   if str(ctx.channel.id) != ACTIVE_CHANNEL_ID:
#     logging.info(f"Ignoring channel {ctx.channel.id}")
#     return

#   prefix = TEMP_PATH + str(ctx.message.id) + "_music"

#   try:
#     mp3_path = await generate_and_download_music(text, prefix)
#     if mp3_path:
#       await ctx.send(file=discord.File(mp3_path))

#       os.remove(mp3_path)
#     else:
#       await ctx.send("An error occurred while downloading the music.")
#   except Exception as e:
#     logging.exception("An error occurred while handling the request.")
#     await ctx.send(f"An error occurred while handling your request: {e}")


@bot.command(name='music', description='Generate some music from text')
async def music(ctx, *, text: str = ""):
  if str(ctx.channel.id) != ACTIVE_CHANNEL_ID:
    logging.info(f"Ignoring channel {ctx.channel.id}")
    return

  if len(text.strip()) == 0:
    await ctx.send("You didn't give a style of music.")
    return

  # await ctx.send(f"Composing some music in the theme of {text}...")

  # Add a checkbox reaction to the message that triggered the command
  await ctx.message.add_reaction('🕑')

  # async with ctx.typing():

  try:
    logging.info("music_generation")
    mp3_path = await music_generation(text)
    if mp3_path:
      async with ctx.typing():
        await ctx.send(file=discord.File(mp3_path))
        os.remove(mp3_path)
    else:
      await ctx.send("An error occurred while generating the music.")

  except Exception as e:
    logging.exception("An error occurred while handling the music request.")
    await ctx.send(f"An error occurred while handling your music request: {e}")

  # Get the bot's user object
  bot_user = ctx.guild.get_member(bot.user.id)
  # Remove the checkbox reaction from the message
  await ctx.message.remove_reaction('🕑', bot_user)


@bot.command(name='image', description='Generate an image from text')
async def image(ctx, *, text: str):
  if str(ctx.channel.id) != ACTIVE_CHANNEL_ID:
    logging.info(f"Ignoring channel {ctx.channel.id}")
    return

  try:
    image_url = await call_glif_api(text)
    if image_url:
      await ctx.send(image_url)  # This will send the image URL directly
    else:
      await ctx.send("An error occurred or no image URL was returned.")
  except Exception as e:
    logging.exception("An error occurred while handling the image request.")
    await ctx.send(f"An error occurred while handling your image request: {e}")


@bot.command(name='video')
async def video(ctx, *, text: str):
  if str(ctx.channel.id) != ACTIVE_CHANNEL_ID:
    logging.info(f"Ignoring channel {ctx.channel.id}")
    return

  # Add a checkbox reaction to the message that triggered the command
  await ctx.message.add_reaction('🕑')

  try:
    async with ctx.typing():
      # Start both glif API and replicate API calls concurrently
      image_path, mp3_path = await asyncio.gather(
        call_glif_api(text),  # Ensure this returns a local file path
        music_generation(
          text,
          filename_prefix=TEMP_PATH)  # Ensure this returns a local file path
      )

    # Check if both the image and the music were successfully generated
    if image_path and mp3_path:
      # Generate the video
      video_path = await generate_video(image_path, mp3_path, TEMP_PATH)

      # Send the video to the Discord channel
      await ctx.send(file=discord.File(video_path))

      # Clean up the generated files
      os.path.exists(video_path) and os.remove(video_path)
      os.path.exists(mp3_path) and os.remove(mp3_path)
      os.path.exists(image_path) and os.remove(image_path)
    else:
      await ctx.send("An error occurred while generating the video components."
                     )

  except Exception as e:
    logging.exception("An error occurred while handling the video request.")
    await ctx.send(f"An error occurred while handling your video request: {e}")

  # Get the bot's user object
  bot_user = ctx.guild.get_member(bot.user.id)
  # Remove the checkbox reaction from the message
  await ctx.message.remove_reaction('🕑', bot_user)


@bot.event
async def on_ready():
  logging.info(f"🔵 {bot.user.name} is now running!")


bot.run(TOKEN)
