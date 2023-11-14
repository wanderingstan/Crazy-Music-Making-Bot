import discord
import aiohttp
import os
import subprocess
import logging
from discord.ext import commands
import replicate
import asyncio

# Set your API token as an environment variable


# Configure logging
logging.basicConfig(level=logging.INFO)

TOKEN = os.environ['mydiscordtoken']
ACTIVE_CHANNEL_ID = "988352005569384518"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Function to generate music using Replicate API
import os
import replicate

import os
import replicate

import asyncio
import os
import replicate

async def generate_music(prompt, duration=8):
    replicate_api_token = os.getenv('REPLICATE_API_TOKEN')
    fullprompt = f"8 bit nintendo style gaming music with {prompt}"
    replicate_client = replicate.Client(api_token=replicate_api_token)

    # Create the prediction
    prediction = await replicate_client.predictions.create(
        version="meta/musicgen:7a76a8258b23fae65c5a22debb8841d1d7e816b75c2f24218cd2bd8573787906",
        input={
            "prompt": fullprompt,
            "duration": duration,
            "output_format": "mp3"
        }
    )

    # Wait for the prediction to complete
    while prediction["status"] not in ["succeeded", "failed"]:
        prediction = await replicate_client.predictions.get(prediction["id"])
        if prediction["status"] == "starting":
            await asyncio.sleep(1)  # Sleep for a second before the next poll

    # Check the status and return the result or handle the error
    if prediction["status"] == "succeeded":
        return prediction["urls"]["get"]  # Returns the URL of the generated MP3 file
    else:
        raise Exception(f"Prediction failed with status {prediction['status']}")



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
                error_message = f"Error downloading music: {response.status}"
                logging.error(error_message)
                return ''

async def call_glif_api(input_text: str) -> str:
  logging.info("Calling the Glif API.")
  async with aiohttp.ClientSession() as session:
      payload = {"id": "clooa2ge8002sl60ixieiocdp", "input": [input_text]}
      headers = {"Content-Type": "application/json"}

      async with session.post('https://simple-api.glif.app', json=payload, headers=headers) as resp:
          if resp.status == 200:
              response_data = await resp.json()
              image_url = response_data.get('output', '')
              logging.info(f"Glif API responded with URL: {image_url}")
              return image_url
          else:
              error_message = f"Error calling Glif API: {resp.status}"
              logging.error(error_message)
              return ''

async def download_image(url: str) -> str:
  logging.info("Starting download of image.")
  async with aiohttp.ClientSession() as session:
      async with session.get(url) as response:
          if response.status == 200:
              with open('temp_image.png', 'wb') as f:
                  f.write(await response.read())
              logging.info("Image downloaded successfully.")
              return 'temp_image.png'
          else:
              error_message = f"Error downloading image: {response.status}"
              logging.error(error_message)
              return ''

def create_mp4(image_path: str, mp3_path: str) -> str:
    output_path = 'output.mp4'
    logging.info("Starting ffmpeg process to create MP4.")
    command = [
      'ffmpeg',
      '-loop', '1',
      '-i', image_path,
      '-i', mp3_path,
      '-c:v', 'libx264',
      '-t', '30',
      '-pix_fmt', 'yuv420p',
      '-vf', 'scale=320:240',
      '-y',
      output_path
    ]
    process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if process.returncode == 0:
      logging.info("MP4 file created successfully.")
    else:
      logging.error("ffmpeg process failed to create MP4 file.")

    return output_path


@bot.command()
async def inspo(ctx, *, text: str):
    if str(ctx.channel.id) != ACTIVE_CHANNEL_ID:
        return

    try:
        # Generate music
        music_url = await generate_music(text)
        if music_url:  # if music_url exists, it means it successfully got the url from the api
            # Download music
            mp3_path = await download_music(music_url)

        image_url = await call_glif_api(text)
        if image_url:
            image_path = await download_image(image_url)
            if image_path and mp3_path:  # also check if mp3_path exists before creating the video
                # Create Video
                video_path = create_mp4(image_path, mp3_path)
                await ctx.send(file=discord.File(video_path))
                os.remove(image_path)
                os.remove(video_path)
                os.remove(mp3_path)  # also remove the mp3 file after it's done
            else:
                await ctx.send("An error occurred while downloading the image or music.")
        else:
            await ctx.send("An error occurred or no image URL and music URL were returned.")
    except Exception as e:
        logging.exception("An unexpected error occurred while handling the request.")
        await ctx.send("An error occurred while handling your request.")



@bot.event
async def on_ready():
    logging.info(f"{bot.user.name} is now running!")

bot.run(TOKEN)