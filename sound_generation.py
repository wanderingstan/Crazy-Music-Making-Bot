import replicate
import aiohttp
import logging
import os
import asyncio

# Initialize logging
logging.basicConfig(level=logging.INFO)

REPLICATE_API_TOKEN = "r8_5Zjjr1aoF70x2tWHIhtdiwFin6eFEMs4S7X2L"
if not REPLICATE_API_TOKEN:
    raise ValueError("No Replicate API token found in environment variables.")


# Initialize Replicate Client with your API token
replicate_client = replicate.Client(api_token=REPLICATE_API_TOKEN)  # Replace with your actual API token

async def generate_and_download_music(prompt, duration="5.0", guidance_scale=2.5, n_candidates=3, music_filename='temp_music'):
    fullprompt = f"{prompt}"

    # Generate music using Replicate API asynchronously
    output = await asyncio.to_thread(replicate_client.run, 
        "haoheliu/audio-ldm:b61392adecdd660326fc9cfc5398182437dbe5e97b5decfb36e1a36de68b5b95",
        input={
            "text": fullprompt,
            "duration": duration,
            "guidance_scale": guidance_scale,
            "n_candidates": n_candidates
        }
    )

    if output is None:
        raise Exception("No output was returned from the model.")

    # Assuming the model returns a URL
    music_url = output

    # Download the music file
    logging.info("Starting download of music.")
    async with aiohttp.ClientSession() as session:
        async with session.get(music_url) as response:
            if response.status == 200:
                music_filename += '.mp3'
                with open(music_filename, 'wb') as f:
                    f.write(await response.read())
                logging.info("Music downloaded successfully.")
                return music_filename
            else:
                logging.error(f"Error downloading music: {response.status}")
                return ''
