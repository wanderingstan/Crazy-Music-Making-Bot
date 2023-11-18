import replicate
import aiohttp
import logging
import asyncio
import re

# Configure logging
# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Initialize logging to only log errors
# Note: Replicate client generates a ton of info logs
logging.getLogger("httpx").setLevel(logging.ERROR)

def sanitize_for_unix_filename(s):
    # Replace spaces with underscores
    s = s.replace(" ", "_")

    # Remove characters that are not allowed in Unix file names
    s = re.sub(r"[^\w.-]", "", s)

    # Ensure the resulting string is not empty
    if not s:
        s = "unnamed_file"
    return s


async def music_generation(
    REPLICATE_API_TOKEN,
    prompt,
    model_version="melody",
    duration=8,
    continuation=False,
    normalization_strategy="loudness",
    top_k=250,
    top_p=0,
    temperature=1,
    classifier_free_guidance=3,
    output_format="wav",
    seed=None,
    filename_prefix="./"
):
    
    # # For testing
    # logging.info("😎 Using fake replicate response for testing.")
    # return ("test_files/wanderingstan_1175179192011333713_music.wav")

    # fullprompt = f"8 bit retro gaming soundtrack for {prompt} game"
    fullprompt = prompt

    if not REPLICATE_API_TOKEN:
        raise ValueError("No Replicate API token passed.")

    # Initialize Replicate Client with your API token
    replicate_client = replicate.Client(api_token=REPLICATE_API_TOKEN)

    logging.info("🕒 Calling the Replicate API for music_generation.")

    # Run the new music generation model using Replicate API
    output = await asyncio.to_thread(
        replicate_client.run,
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
            "classifier_free_guidance": 3,
        },
    )


    if output is None:
        raise Exception("No output was returned from the model.")

    # Assuming the model returns a URL to the generated music file
    music_url = output

    # Download the generated music file
    music_filename = (
        f"{filename_prefix}{sanitize_for_unix_filename(prompt)}.{output_format}"
    )
    music_filename = f"{filename_prefix}music.{output_format}"

    logging.info(f"🟢 Saving music to {music_filename}")

    async with aiohttp.ClientSession() as session:
        async with session.get(music_url) as response:
            if response.status == 200:
                with open(music_filename, "wb") as f:
                    f.write(await response.read())
                return music_filename
            else:
                raise Exception(f"Error downloading music: {response.status}")
