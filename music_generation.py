import replicate
import aiohttp
import logging
import os

# Initialize logging to only log errors
logging.getLogger('httpx').setLevel(logging.ERROR)

REPLICATE_API_TOKEN = "r8_5Zjjr1aoF70x2tWHIhtdiwFin6eFEMs4S7X2L"
if not REPLICATE_API_TOKEN:
  raise ValueError("No Replicate API token found in environment variables.")

# Initialize Replicate Client with your API token
replicate_client = replicate.Client(
  api_token=REPLICATE_API_TOKEN)  # Replace with your actual API token

import re


def sanitize_for_unix_filename(s):
  # Replace spaces with underscores
  s = s.replace(' ', '_')

  # Remove characters that are not allowed in Unix file names
  s = re.sub(r'[^\w.-]', '', s)

  # Ensure the resulting string is not empty
  if not s:
    s = 'unnamed_file'
  return s


async def music_generation(prompt,
                           model_version="melody",
                           duration=8,
                           continuation=False,
                           normalization_strategy="loudness",
                           top_k=250,
                           top_p=0,
                           temperature=1,
                           classifier_free_guidance=3,
                           output_format="wav",
                           seed=None):

  fullprompt = f"8 bit retro gaming soundtrack for {prompt} game"

  # Run the new music generation model using Replicate API
  output = replicate_client.run(
    "meta/musicgen:7a76a8258b23fae65c5a22debb8841d1d7e816b75c2f24218cd2bd8573787906",
    input={
      "seed": -1,
      "top_k": 250,
      "top_p": 0,
      "prompt": fullprompt,
      "duration": 8,
      "temperature": 1,
      "continuation": False,
      "model_version": "large",
      "output_format": "wav",
      "continuation_end": 9,
      "continuation_start": 7,
      "normalization_strategy": "peak",
      "classifier_free_guidance": 3
    })

  if output is None:
    raise Exception("No output was returned from the model.")

  # Assuming the model returns a URL to the generated music file
  music_url = output

  # Download the generated music file
  music_filename = f'{sanitize_for_unix_filename(prompt)}.{output_format}'
  async with aiohttp.ClientSession() as session:
    async with session.get(music_url) as response:
      if response.status == 200:
        with open(music_filename, 'wb') as f:
          f.write(await response.read())
        return music_filename
      else:
        raise Exception(f"Error downloading music: {response.status}")
