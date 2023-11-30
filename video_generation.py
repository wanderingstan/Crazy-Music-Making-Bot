import os
import aiohttp
import asyncio
import logging
import random
import shutil
import tempfile
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
# Configure logging
logging.basicConfig(level=logging.INFO)


# Default image URL
DEFAULT_IMAGE_URL = "https://glif.app/_next/image?url=https%3A%2F%2Fres.cloudinary.com%2Fdzkwltgyd%2Fimage%2Fupload%2Fv1699551574%2Fglif-run-outputs%2Fs6s7h7fypr9pr35bpxul.png&w=2048&q=75&dpl=dpl_J7MPoF6chivDp2KiVJA6mJ9faKu1"


# Download a file from a URL to a local file
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


# Generate a video from an image and audio source
async def generate_video(
    image_source: str = None,
    audio_source: str = None,
    file_prefix: str = "./",
    duration: float = None,
    subtitle: str = "",
) -> str:
    """Generates video from image and audio sources using ffmpeg, returns path to local video file."""
    logging.info("generate_video zoom")

    # Define the paths for temporary files
    image_path = f"{file_prefix}img.jpg"
    audio_path = f"{file_prefix}wav.mp3"
    video_path = f"{file_prefix}video.mp4"

    # Download or assign image file
    if image_source and (
        image_source.startswith("http://") or image_source.startswith("https://")
    ):
        image_path = await download_file(image_source, image_path)
    elif image_source:
        image_path = image_source
    else:
        logging.warn(f"Could not find image source of {image_source}, using default.")
        image_path = await download_file(DEFAULT_IMAGE_URL, image_path)

    if not audio_source and duration is None:
        raise ValueError(f"No audio source found for video at {audio_source}.")

    # Download or assign audio file
    if audio_source and (
        audio_source.startswith("http://") or audio_source.startswith("https://")
    ):
        audio_path = await download_file(audio_source, audio_path)
    else:
        audio_path = audio_source

    if not audio_source and duration is None:
        raise ValueError(f"No audio source or duration provided.")

    if not os.path.exists(image_path):
        raise ValueError(
            f"No audio source found for video to go with image {image_path}."
        )

    # Create the ffmpeg command
    if audio_source is not None:
        # Duration implied from audio
        logging.info(f"Duration implied from audio: {audio_path}")
        cmd = (
            f"ffmpeg -loop 1 -framerate 10 -i {image_path} -i {audio_path} "
            f"-filter_complex \"[0:v]zoompan=z='zoom+0.001':d=200:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1024x1024, "
            f"drawtext=text='{subtitle}':fontsize=64:fontcolor=white:shadowcolor=black:shadowx=2:shadowy=2:x=(w-text_w)/2:y=h-th-100[fv];[fv][1:a]concat=n=1:v=1:a=1[v][a]\" "
            f"-map '[v]' -map '[a]' -c:v libx264 -tune stillimage -c:a aac -strict experimental "
            f"-b:a 192k -pix_fmt yuv420p -t 8 {video_path}"
        )
    else:
        # Duration specified
        logging.info(f"Duration specified: {duration}")
        cmd = (
            f"ffmpeg -loop 1 -framerate 10 -i {image_path} "
            f"-filter_complex \"[0:v]zoompan=z='zoom+0.001':d=200:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1024x1024, "
            f"drawtext=text='{subtitle}':fontsize=64:fontcolor=white:shadowcolor=black:shadowx=2:shadowy=2:x=(w-text_w)/2:y=h-th-100[fv]\" "
            f"-map '[fv]' -c:v libx264 -tune stillimage -pix_fmt yuv420p -t {duration} {video_path}"
        )

    logging.info(cmd)

    # Run the ffmpeg command
    process = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    # Wait for the command to complete
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        error_message = f"ffmpeg command failed for video:\n{stderr}"
        logging.error(error_message)
        raise Exception(error_message)

    logging.info(f"Video generated successfully: {video_path}")

    return video_path


async def concatenate_videos_async(video_files, output_file="./temp_files/output.mp4"):
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
    cmd = f"ffmpeg -y -safe 0 -f concat -i {list_path} -c copy {output_file}"
    logging.info(cmd)

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

async def concatenate_videos_with_audio_async(video1, video2, video3, video4, audio_file, output_file="./temp_files/output.mp4"):

  # Ensure FFmpeg is installed
  if not shutil.which("ffmpeg"):
      raise RuntimeError("FFmpeg is not installed or not in the PATH.")

  cmd = (
      f"ffmpeg -i {video1} -i {video2} -i {video3} -i {video4} -i {audio_file} "
      f"-filter_complex \"[0:v][1:v][2:v][3:v]concat=n=4:v=1:a=0[outv]\" "
      f"-map \"[outv]\" -map 4:a -c:a aac -strict -2 -y {output_file}"
  )

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

  return os.path.abspath(output_file)

