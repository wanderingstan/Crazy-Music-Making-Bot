import os
import aiohttp
import asyncio
import logging
import random
import shutil
import tempfile

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
    """ Generates video from image and audio sources using ffmpeg, returns path to local video file."""
    logging.info("generate_video zoom")

    # Generate random identifier for file naming
    random_id = random.randint(10000000, 99999999)
                                  
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


    # Zoompan Filter:

    # zoompan=z='zoom+0.001': This gradually increases the zoom over the duration. The value 0.001 controls the zoom speed. Adjust this value to change how quickly it zooms.
    # d=125: Duration of each frame in the zoompan filter (since the input framerate is 2, this means the zoom effect will last for the entire duration of the 8-second video).
    # x='iw/2-(iw/zoom/2)' and y='ih/2-(ih/zoom/2)': These are the x and y positions for the center of the zoom. This will keep the zoom centered.
    # s=hd1080: Sets the output size. You can adjust this according to your needs (e.g., hd720 for 720p).
    # Filter Complex:

    # The -filter_complex is used because the zoompan filter is a complex filter. It processes the video stream [0:v] and then concatenates it with the audio [1:a].
    # Maps:

    # -map '[v]' -map '[a]' ensures that the output uses the video and audio streams from the filter complex.


    # Construct the ffmpeg command with fixed 8 seconds duration
    # cmd = (
    #     f"ffmpeg -loop 1 -framerate 2 -i {image_path} -i {audio_path} "
    #     f"-c:v libx264 -tune stillimage -c:a aac -strict experimental "
    #     f"-b:a 192k -pix_fmt yuv420p -t 8 {video_path}"
    # )
    cmd = (
        f"ffmpeg -loop 1 -framerate 10 -i {image_path} -i {audio_path} "
        f"-filter_complex \"[0:v]zoompan=z='zoom+0.001':d=200:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1024x1024[fv];[fv][1:a]concat=n=1:v=1:a=1[v][a]\" "
        f"-map '[v]' -map '[a]' -c:v libx264 -tune stillimage -c:a aac -strict experimental "
        f"-b:a 192k -pix_fmt yuv420p -t 8 {video_path}"
    )

    logging.info(cmd)

    # Run the ffmpeg command
    process = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    # Wait for the command to complete
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        error_message = f"ffmpeg command failed for video{random_id}:\n{stderr}"
        logging.error(error_message)
        raise Exception(error_message)

    logging.info(f"Video generated successfully: {video_path}")

    # Delete temp files
    # os.path.exists(image_path) and os.remove(image_path)
    # os.path.exists(audio_path) and os.remove(audio_path)

    return video_path


# Example usage:
# asyncio.run(generate_video(image_source='[image_url]', audio_source='[audio_url]'))




async def generate_video(
    image_source: str = None, audio_source: str = None, file_prefix: str = "./"
) -> str:
    """ Generates video from image and audio sources using ffmpeg, returns path to local video file."""
    logging.info("generate_video zoom")

    # Generate random identifier for file naming
    random_id = random.randint(10000000, 99999999)
                                  
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


    # Zoompan Filter:

    # zoompan=z='zoom+0.001': This gradually increases the zoom over the duration. The value 0.001 controls the zoom speed. Adjust this value to change how quickly it zooms.
    # d=125: Duration of each frame in the zoompan filter (since the input framerate is 2, this means the zoom effect will last for the entire duration of the 8-second video).
    # x='iw/2-(iw/zoom/2)' and y='ih/2-(ih/zoom/2)': These are the x and y positions for the center of the zoom. This will keep the zoom centered.
    # s=hd1080: Sets the output size. You can adjust this according to your needs (e.g., hd720 for 720p).
    # Filter Complex:

    # The -filter_complex is used because the zoompan filter is a complex filter. It processes the video stream [0:v] and then concatenates it with the audio [1:a].
    # Maps:

    # -map '[v]' -map '[a]' ensures that the output uses the video and audio streams from the filter complex.


    # Construct the ffmpeg command with fixed 8 seconds duration
    # cmd = (
    #     f"ffmpeg -loop 1 -framerate 2 -i {image_path} -i {audio_path} "
    #     f"-c:v libx264 -tune stillimage -c:a aac -strict experimental "
    #     f"-b:a 192k -pix_fmt yuv420p -t 8 {video_path}"
    # )
    cmd = (
        f"ffmpeg -loop 1 -framerate 10 -i {image_path} -i {audio_path} "
        f"-filter_complex \"[0:v]zoompan=z='zoom+0.001':d=200:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1024x1024[fv];[fv][1:a]concat=n=1:v=1:a=1[v][a]\" "
        f"-map '[v]' -map '[a]' -c:v libx264 -tune stillimage -c:a aac -strict experimental "
        f"-b:a 192k -pix_fmt yuv420p -t 8 {video_path}"
    )

    logging.info(cmd)

    # Run the ffmpeg command
    process = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    # Wait for the command to complete
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        error_message = f"ffmpeg command failed for video{random_id}:\n{stderr}"
        logging.error(error_message)
        raise Exception(error_message)

    logging.info(f"Video generated successfully: {video_path}")

    # Delete temp files
    # os.path.exists(image_path) and os.remove(image_path)
    # os.path.exists(audio_path) and os.remove(audio_path)

    return video_path



async def concatenate_videos_async(video_files, output_file="output.mp4"):
    """
    Concatenates a list of videos into a single video file using FFmpeg, asynchronously,
    using the demuxer syntax for concatenation.

    :param video_files: List of paths to video files.
    :param output_file: Path to the output video file.
    :return: Path to the concatenated output video file.
    """
    # Ensure FFmpeg is installed
    if not shutil.which("ffmpeg"):
        raise RuntimeError("FFmpeg is not installed or not in the PATH.")

    # Create a temporary file to list all video files
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as list_file:
        for file in video_files:
            abs_path = os.path.abspath(file)  # Convert to absolute path
            list_file.write(f"file '{abs_path}'\n")
        list_path = list_file.name

    # Create the FFmpeg command
    cmd = f'ffmpeg -safe 0 -f concat -i {list_path} -c copy {output_file}'

    # Run the command asynchronously
    process = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    # Wait for the command to complete and capture stdout and stderr
    stdout, stderr = await process.communicate()

    # Check for errors
    if process.returncode != 0:
        error_message = f"FFmpeg command failed: {stderr.decode('utf-8')}"
        raise Exception(error_message)

    # Clean up the temporary file
    os.remove(list_path)

    return os.path.abspath(output_file)