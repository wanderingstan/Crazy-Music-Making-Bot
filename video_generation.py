import os
import aiohttp
import asyncio
import logging
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Default image URL
DEFAULT_IMAGE_URL = "https://glif.app/_next/image?url=https%3A%2F%2Fres.cloudinary.com%2Fdzkwltgyd%2Fimage%2Fupload%2Fv1699551574%2Fglif-run-outputs%2Fs6s7h7fypr9pr35bpxul.png&w=2048&q=75&dpl=dpl_J7MPoF6chivDp2KiVJA6mJ9faKu1"


async def download_file(url, file_name):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                with open(file_name, "wb") as f:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        f.write(chunk)
                logging.info(f"File downloaded successfully: {file_name}")
                return file_name
            else:
                error_msg = f"Failed to download file from {url}"
                logging.error(error_msg)
                raise Exception(error_msg)


async def generate_video(
    image_source: str = None, audio_source: str = None, file_prefix: str = "./"
) -> str:
    logging.info("generate_video")

    # Generate random identifier for file naming
    random_id = random.randint(1, 99999999)

    # Define the paths for temporary files
    image_path = f"{file_prefix}img{random_id}.jpg"
    audio_path = f"{file_prefix}wav{random_id}.mp3"
    video_path = f"{file_prefix}video{random_id}.mp4"

    # Download or assign image file
    if image_source and (
        image_source.startswith("http://") or image_source.startswith("https://")
    ):
        image_path = await download_file(image_source, image_path)
    elif image_source:
        image_path = image_source
    else:
        image_path = await download_file(DEFAULT_IMAGE_URL, image_path)

    # Download or assign audio file
    if audio_source and (
        audio_source.startswith("http://") or audio_source.startswith("https://")
    ):
        audio_path = await download_file(audio_source, audio_path)
    else:
        audio_path = audio_source

    # Construct the ffmpeg command with fixed 8 seconds duration
    cmd = (
        f"ffmpeg -loop 1 -framerate 2 -i {image_path} -i {audio_path} "
        f"-c:v libx264 -tune stillimage -c:a aac -strict experimental "
        f"-b:a 192k -pix_fmt yuv420p -t 8 {video_path}"
    )

    # Run the ffmpeg command
    process = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    # Wait for the command to complete
    await process.communicate()

    if process.returncode != 0:
        error_message = f"ffmpeg command failed for video{random_id}"
        logging.error(error_message)
        raise Exception(error_message)

    logging.info(f"Video generated successfully: {video_path}")

    # Delete temp files
    os.path.exists(image_path) and os.remove(image_path)
    os.path.exists(audio_path) and os.remove(audio_path)

    return video_path


# Example usage:
# asyncio.run(generate_video(image_source='[image_url]', audio_source='[audio_url]'))
