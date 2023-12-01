from typing import List
import logging
import config
import asyncio
import replicate
import aiohttp
import shutil
import json
import os
import subprocess
import video_generation

class Film4:
    def __init__(self, filename_prefix: str = "./temp_files/film4"):
        logging.basicConfig(level=logging.INFO)

        # Json object describing the video to be generated
        self.data = None

        # Parse the JSON input
        self.filename_prefix: str = filename_prefix

    # Function that calls glif API wiht id clpkl1gt8005ymrou8dvkblqv , returns json
    async def ad_json_from_text(self, prompt: str):
        logging.info("🕒 Calling the Glif API.")
        # TODO: Change to come from env var
        # glif_id = "clpkl1gt8005ymrou8dvkblqv" # Stan's
        glif_id = "clpl0fv0x000ne48qaxajldu6"  # Fabian's

        # if config.DO_FAKE_RESULTS:
        #     # return "https://res.cloudinary.com/dzkwltgyd/image/upload/v1699551574/glif-run-outputs/s6s7h7fypr9pr35bpxul.png"
        #     return f"./test_files/wanderingstan_1175179192011333713_img.jpg"

        async with aiohttp.ClientSession() as session:
            payload = {"id": glif_id, "input": [prompt]}
            headers = {"Content-Type": "application/json"}

            async with session.post(
                "https://simple-api.glif.app", json=payload, headers=headers
            ) as response:
                if response.status == 200:
                    response_data = await response.json()

                    logging.info("response_data:")
                    logging.info(response_data)

                    ad_json = response_data.get("output", "")
                    logging.info(f"🟢 Glif API responded with json: {ad_json}")

                    if ad_json is None:
                        raise Exception("No output was returned from the glif.")

                    # Hack for Fabian's bug
                    # ad_json = ad_json.replace('""', '"')

                    self.data = json.loads(ad_json)

                    return ad_json
                else:
                    error_message = f"Error calling Glif API: {response.status}"
                    logging.error(error_message)
                    raise Exception(error_message)

    async def generate(self):
        if not self.data:
            raise ValueError("No data provided.")

        narration = self.data["narration"]
        speech_filename = f"{self.filename_prefix}narration.mp3"
        voice_model_id = (
            self.data["narration"]
            if "voice_model_id" in self.data
            else "T8Yl7BPwFrIshyDyPKau"
        )

        # Default duration is 12 seconds
        duration = self.data["duration"] if "duration" in self.data else 12

        # Collect tasks for each scene
        tasks = [
            self.create_scene(
                scene["duration"] if "duration" in scene else 4,
                scene["video_prompt"],
                scene["sound_prompt"] if "sound_prompt" in scene else None,
                scene["text"] if "text" in scene else "",
                scene["generator"] if "generator" in scene else "glif1",
            )
            for scene in self.data["scenes"]
        ]

        # Add speech_from_text and music_generation tasks to the list
        tasks.append(
            self.speech_from_text(
                narration, speech_filename, voice_model_id=voice_model_id
            )
        )
        tasks.append(
            self.music_generation(self.data["music_prompt"], duration=duration)
        )

        # Run all tasks concurrently and collect results
        results = await asyncio.gather(*tasks)

        # The last two results are the results of speech_from_text and music_generation
        video_filenames = results[:-2]
        music_url = results[-1]

        combined_video_filename = await self.concatenate_videos_with_audio(
            video_files=video_filenames,
            audio_files=[speech_filename],
            output_file=f"{self.filename_prefix}combined_video.mp4",
        )


        logging.info(f"🟢 Generated video: {combined_video_filename}")

        added_music_filename = await self.add_looping_music(combined_video_filename, music_url)

        logging.info(f"🟢 Added music to video: {added_music_filename}")

        return added_music_filename

    async def add_looping_music(self, video_filename, music_url):
        # Download the music file
        # music_filename = f"{self.filename_prefix}music.mp3"
        # os.system(f"wget -O {music_filename} {music_url}")

        music_file = os.path.abspath(f"{self.filename_prefix}music.mp3")
        await video_generation.download_file(music_url, music_file)
        logging.info(f"🟢 Saved music to {music_file}")

        # Output filename
        output_filename = f"{self.filename_prefix}video_with_music.mp4"

        # ffmpeg command to add music to the video
        # cmd = f"ffmpeg -y -i {video_filename} -i {music_url} -filter_complex \"[1:a]volume=0.5,aloop=loop=-1:size=2e+09[out]\" -map 0:v -map \"[out]\" -y {output_filename}"
        # cmd = f'ffmpeg -y -i {video_filename} -stream_loop -1 -i {music_url} -filter_complex "[1:a]volume=0.5[outa]" -map 0:v -map "[outa]" -shortest -y {output_filename}'

        # works
        # ffmpeg -y \
        #    -i /Users/wanderingstan/Developer/glif/Crazy-Music-Making-Bot/temp_files/wanderingstan_1179945063644680232_combined_video.mp4 \
        #    -stream_loop -1 -i https://replicate.delivery/pbxt/sYXHNGavfb1pGCRcoDxSFapvXHlldVolC3BywtTk4TJX72eRA/out.mp3 \
        #    -filter_complex "[0:a][1:a]amix=inputs=2:duration=first,volume=2.0[outa]" \
        #    -map 0:v -map "[outa]" -shortest \
        #    -y temp_files/wanderingstan_1179945063644680232_video_with_music.mp4

        # cmd = (
        #     f"ffmpeg -y "
        #     f"-i \"{video_filename}\" "
        #     f"-stream_loop -1 -i \"{music_url}\" "
        #     f"-filter_complex \"[0:a][1:a]amix=inputs=2:duration=first,volume=2.0[outa]\" "
        #     f"-map 0:v -map \"[outa]\" -shortest "
        #     f"-y \"{output_filename}\""
        # )

        cmd = (
            f"ffmpeg -y "
            f"-i \"{video_filename}\" "
            f"-stream_loop -1 -i \"{music_file}\" "
            f"-filter_complex \""
            f"[1:a]volume=0.3[volume_adjusted]; "
            f"[0:a][volume_adjusted]amix=inputs=2:duration=first[volume_normal]\" "
            f"-map 0:v -map \"[volume_normal]\" -shortest "
            f"-y \"{output_filename}\""
        )
        logging.info(cmd)

        # Run the command
        process = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await process.communicate()

        if stdout:
            logging.info(f'[stdout]\n{stdout.decode()}')
            return output_filename
        if stderr:
            logging.error(f'Error adding music to video. [stderr]\n{stderr.decode()}')
            # raise Exception(f"Error adding music to video: {stderr.decode()}")
            return output_filename


    async def create_scene(self, duration, video_prompt, sound_prompt, text, generator):
        # Implement your scene creation logic here
        print(
            f"Creating scene with duration {duration} and video prompt {video_prompt}"
        )

        if generator == "glif1":
            video_task = self.video_from_prompt_glif1(
                video_prompt, duration=duration, subtitle=text
            )
        elif generator == "replicate1":
            video_task = self.video_from_prompt_replicate1(
                video_prompt, duration=duration
            )
        else:
            raise ValueError(f"Unknown generator {generator}")

        # Start both glif API and replicate API calls concurrently
        video_path, sound_url = await asyncio.gather(
            video_task,
            # self.video_from_prompt(video_prompt, duration),
            self.sound_from_prompt(sound_prompt, duration),
        )

        # TODO: use the sound

        return video_path

    async def sound_from_prompt(self, prompt: str, duration: int = 4) -> str:
        # Implement sound_from_prompt logic
        return None

    async def music_generation(
        self,
        prompt: str,
        duration: int = 12,
        model_version: str = "melody",
        continuation_end: int = 0,  # 9,
        continuation_start: int = 0,  # 7,
        continuation: bool = False,
        normalization_strategy: str = "loudness",
        top_k: int = 250,
        top_p: int = 0,
        temperature: int = 1,
        classifier_free_guidance: int = 3,
        output_format: str = "mp3",  # "wav"
        seed=None,
    ):
        logging.info(
            f"%s Calling the Replicate API for music_generation. {duration} seconds."
            % "🕒"
        )

        # Testing
        if config.DO_FAKE_RESULTS:
            logging.info(
                "😎 Using fake replicate response for testing. Ignoring duration and other settings."
            )
            return "test_files/wanderingstan_1175179192011333713_music.wav"

        # Note: Don't fully understand the continuation settings yet.
        if continuation_end == 0:
            continuation_end = duration

        if not config.REPLICATE_API_TOKEN:
            raise ValueError("No Replicate API token passed.")

        # Initialize Replicate Client with your API token
        replicate_client = replicate.Client(api_token=config.REPLICATE_API_TOKEN)

        # Run the new music generation model using Replicate API
        output = await asyncio.to_thread(
            replicate_client.run,
            "meta/musicgen:7a76a8258b23fae65c5a22debb8841d1d7e816b75c2f24218cd2bd8573787906",
            input={
                "seed": -1,
                "top_k": top_k,
                "top_p": top_p,
                "prompt": prompt,
                "duration": duration,
                "temperature": temperature,
                "continuation": continuation,
                "model_version": "large",
                "output_format": output_format,
                "continuation_end": continuation_end,
                "continuation_start": continuation_start,
                "normalization_strategy": normalization_strategy,  # "peak",
                "classifier_free_guidance": classifier_free_guidance,
            },
        )

        if output is None:
            raise Exception("No output was returned from the model.")

        # Assuming the model returns a URL to the generated music file
        music_url = output

        logging.info(f"🟢 music_generation: {music_url}")

        return music_url

        # # Download the generated music file
        # music_filename = (
        #     f"{filename_prefix}{sanitize_for_unix_filename(prompt)}.{output_format}"
        # )
        # music_filename = f"{filename_prefix}music.{output_format}"

        # logging.info(f"🟢 Saving music to {music_filename}")

        # async with aiohttp.ClientSession() as session:
        #     async with session.get(music_url) as response:
        #         if response.status == 200:
        #             with open(music_filename, "wb") as f:
        #                 f.write(await response.read())
        #             return music_filename
        #         else:
        #             raise Exception(f"Error downloading music: {response.status}")

    # Function to call Glif API, return URL to image
    async def image_from_prompt(
        self,
        prompt: str,
        glif_id: str = "clpklzi650002ks9vo4lm7jqx",  # "clooa2ge8002sl60ixieiocdp"
    ) -> str:
        logging.info("🕒 Calling the Glif API.")

        if config.DO_FAKE_RESULTS:
            # return "https://res.cloudinary.com/dzkwltgyd/image/upload/v1699551574/glif-run-outputs/s6s7h7fypr9pr35bpxul.png"
            return f"./test_files/wanderingstan_1175179192011333713_img.jpg"

        async with aiohttp.ClientSession() as session:
            payload = {"id": glif_id, "input": [prompt]}
            headers = {"Content-Type": "application/json"}

            async with session.post(
                "https://simple-api.glif.app", json=payload, headers=headers
            ) as response:
                if response.status == 200:
                    response_data = await response.json()

                    logging.info("response_data:")
                    logging.info(response_data)

                    image_url = response_data.get("output", "")
                    logging.info(f"🟢 Glif API responded with URL: {image_url}")
                    return image_url
                else:
                    error_message = f"Error calling Glif API: {response.status}"
                    logging.error(error_message)
                    raise Exception(error_message)

    async def video_from_prompt_glif1(
        self,
        prompt: str,
        audio_path: str = None,
        duration: int = 4,
        subtitle: str = "",
    ) -> str:
        """Generate video by first generating an imate then using ffmpeg to repeat it for duration."""

        logging.info(f"🎬 Generating video for prompt: {prompt}")

        # Testing
        if config.DO_FAKE_RESULTS:
            logging.info("😎 Using fake static video response for testing.")
            return "test_files/video_gen_sample.mp4"

        # Try to generate image from prompt using glif API up to 5 times
        for _ in range(5):
            image_url = await self.image_from_prompt(
                prompt, glif_id="clpljuz4w00046j7svzyue8ur"
            )

            if image_url:
                break

            # Wait for 1 second before trying again
            await asyncio.sleep(1)
        else:
            # If no image is returned after 5 attempts, use the default image URL
            image_url = "https://res.cloudinary.com/dzkwltgyd/image/upload/v1699551574/glif-run-outputs/s6s7h7fypr9pr35bpxul.png"
        # Add line breaks to subtitle
        subtitle = (
            self.insert_linebreaks(subtitle, 32)
            # .replace("\n", "\\\\n")
            .replace('"', '\\"').replace("'", "\\'")
        )

        # # Download the image file
        # image_filename = await video_generation.download_file(
        #     image_url, f"{self.filename_prefix}img.jpg"
        # )

        # Create the ffmpeg command
        # cmd = (
        #     f"ffmpeg -loop 1 -i {image_filename} "
        #     f"-c:v libx264 -t {duration} -pix_fmt yuv420p "
        #     f"{self.filename_prefix}video_{self.sanitize_for_unix_filename(prompt)}.mp4"
        # )

        output_video_path = (
            f"{self.filename_prefix}video_{self.sanitize_for_unix_filename(prompt)}.mp4"
        )
        if config.RECYCLE_RESULTS and os.path.exists(output_video_path):
            logging.info(f"🟢 Using recycled cached video file: {output_video_path}")
            return output_video_path

        video_size = "1024x1024"
        # video_size = "512x512"

        # Create the ffmpeg command
        if audio_path is not None:
            # Duration implied from audio
            logging.info(f"Duration implied from audio: {audio_path}")
            cmd = (
                f"ffmpeg -y -loop 1 -framerate 20 -i {image_url} -i {audio_path} "
                f'-filter_complex "[0:v]scale=2048:2048:force_original_aspect_ratio=increase,crop=2048:2048, '
                f"zoompan=z='zoom+0.001':d=200:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={video_size}, "
                f"drawtext=text='{subtitle}':fontsize=64:fontcolor=white:shadowcolor=black:shadowx=2:shadowy=2:x=(w-text_w)/2:y=h-th-100[fv];[fv][1:a]concat=n=1:v=1:a=1[v][a]\" "
                f"-map '[v]' -map '[a]' -c:v libx264 -tune stillimage -c:a aac -strict experimental "
                f"-b:a 192k -pix_fmt yuv420p -t 8 {output_video_path}"
            )
        else:
            # Duration specified
            logging.info(f"Duration specified: {duration}")
            cmd = (
                f"ffmpeg -y -loop 1 -framerate 20 -i {image_url} "
                f'-filter_complex "[0:v]scale=2048:2048:force_original_aspect_ratio=increase,crop=2048:2048, '
                f"zoompan=z='zoom+0.001':d=200:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={video_size}, "
                f"drawtext=text='{subtitle}':fontsize=64:fontcolor=white:shadowcolor=black:shadowx=2:shadowy=2:x=(w-text_w)/2:y=h-th-100[fv]\" "
                f"-map '[fv]' -c:v libx264 -tune stillimage -pix_fmt yuv420p -t {duration} {output_video_path}"
            )

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

        logging.info("🟢 Video generated successfully.")

        # Return the path to the generated video file
        return os.path.abspath(
            f"{self.filename_prefix}video_{self.sanitize_for_unix_filename(prompt)}.mp4"
        )

    async def video_from_prompt_replicate1(self, prompt: str, duration: int = 4) -> str:
        """Generate video from prompt using Replicate API, return URL to video file."""

        logging.info(f"🎬 Generating video for prompt: {prompt}")

        # Testing
        if config.DO_FAKE_RESULTS:
            logging.info("😎 Using fake replicate video response for testing.")
            return "test_files/video_gen_sample.mp4"

        if not config.REPLICATE_API_TOKEN:
            raise ValueError("No Replicate API token REPLICATE_API_TOKEN.")

        # Initialize Replicate Client with your API token
        replicate_client = replicate.Client(api_token=config.REPLICATE_API_TOKEN)

        logging.info(
            "🕒 video_from_prompt_replicate1: Calling the Replicate API for video generation."
        )

        # # Run the video generation model using Replicate API
        # TODO: Might be better way to do this using the _run methods:
        #       https://github.com/replicate/replicate-python#run-a-model

        # # https://replicate.com/cjwbw/kandinskyvideo?input=python
        # output_url = await asyncio.to_thread(
        #     replicate_client.run,
        #     "cjwbw/kandinskyvideo:849b70f3e300a650aa8b78d0f8f24d104824b832ea7f61c79bd2c7e78a4ad545",
        #     input={
        #         "fps": 10,
        #         "width": 640,
        #         "height": 384,
        #         "prompt": prompt,
        #         "guidance_scale": 5,
        #         "interpolation_level": "low",
        #         "num_inference_steps": 50,
        #         "interpolation_guidance_scale": 0.25,
        #     },
        # )

        # https://replicate.com/cjwbw/text2video-zero?input=python
        output_url = await asyncio.to_thread(
            replicate_client.run,
            "cjwbw/text2video-zero:e671ffe4e976c0ec813f15a9836ebcfd08857ac2669af6917e3c2549307f9fae",
            input={
                "fps": 4,
                "prompt": prompt,
                "model_name": "dreamlike-art/dreamlike-photoreal-2.0",
                "timestep_t0": 44,
                "timestep_t1": 47,
                "video_length": duration,
                "negative_prompt": "",
                "motion_field_strength_x": 12,
                "motion_field_strength_y": 12,
            },
        )

        if output_url is None:
            raise Exception("No output_URL was returned from the model.")

        logging.info(f"🟢 video_from_prompt_replicate1: {output_url}")

        return output_url

        # # Download the generated video file
        # output_format = "mp4"
        # filename = f"{self.filename_prefix}video_{self.sanitize_for_unix_filename(prompt)}.{output_format}"

        # logging.info(f"🟢 Saving video to {filename}")

        # async with aiohttp.ClientSession() as session:
        #     async with session.get(output_url) as response:
        #         if response.status == 200:
        #             with open(filename, "wb") as f:
        #                 f.write(await response.read())
        #             return filename
        #         else:
        #             raise Exception(f"Error downloading video: {response.status}")

    async def speech_from_text(
        self,
        text: str,
        output_filename: str,
        voice_model_id: str = "21m00Tcm4TlvDq8ikWAM",
    ):
        """ " Generate speech from text using Eleven Labs API, return path to mp3 audio file."""
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_model_id}"
        headers = {
            "Content-Type": "application/json",
            "xi-api-key": config.ELEVENLABS_API_TOKEN,
        }
        data = {"text": text, "model_id": "eleven_turbo_v2"}

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 200:
                    with open(output_filename, "wb") as f:
                        f.write(await response.read())
                    logging.info(f"🟢 Speech audio saved as {output_filename}")
                else:
                    logging.error(f"Request failed: {response.status}")
                    text = await response.text()
                    logging.error(text)
                    raise RuntimeError(f"Elevenlabs Request failed: {response.status}")

    async def concatenate_videos_with_audio(
        self,
        video_files: List[str],
        audio_files: List[str],
        output_file: str = "./temp_files/output.mp4",
    ):
        logging.info(
            f"🎬 Concatenating {len(video_files)} videos with {len(audio_files)} audio files into {output_file}"
        )

        # Ensure FFmpeg is installed
        if not shutil.which("ffmpeg"):
            raise RuntimeError("FFmpeg is not installed or not in the PATH.")

        # Build the FFmpeg command for video and audio inputs
        video_input_cmd = " ".join(f'-i "{video}"' for video in video_files)
        audio_input_cmd = " ".join(f'-i "{audio}"' for audio in audio_files)
        video_filter_complex = " ".join(f"[{i}:v]" for i in range(len(video_files)))
        audio_filter_complex = " ".join(
            f"[{len(video_files) + i}:a]" for i in range(len(audio_files))
        )
        n_videos = len(video_files)
        n_audios = len(audio_files)

        # Concatenate videos and mix audio files
        filter_complex = (
            f"{video_filter_complex}concat=n={n_videos}:v=1:a=0[outv]; "
            f"{audio_filter_complex}amix=inputs={n_audios}[outa]"
        )

        cmd = (
            f"ffmpeg -y {video_input_cmd} {audio_input_cmd} "
            f'-filter_complex "{filter_complex}" '
            f'-map "[outv]" -map "[outa]" -c:v libx264 -c:a aac -strict -2 -y "{output_file}"'
        )
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

        logging.info(
            f"Finished concatenating {len(video_files)} videos with {len(audio_files)} audio files into {output_file}"
        )

        return os.path.abspath(output_file)

    # [vost#0:0/copy @ 0x124b1ee50] Streamcopy requested for output stream fed from a complex filtergraph. Filtering and streamcopy cannot be used together.

    # async def concatenate_videos_with_audio(
    #     self,
    #     video_files: List[str],
    #     audio_files: List[str],
    #     output_file: str = "./temp_files/output.mp4",
    # ):
    #     # Ensure FFmpeg is installed
    #     if not shutil.which("ffmpeg"):
    #         raise RuntimeError("FFmpeg is not installed or not in the PATH.")

    #     # Build the FFmpeg command for video inputs
    #     video_input_cmd = " ".join(f"-i {video}" for video in video_files)
    #     video_filter_complex = " ".join(f"[{i}:v]" for i in range(len(video_files)))
    #     n_videos = len(video_files)

    #     # Build the FFmpeg command for audio inputs
    #     audio_input_cmd = " ".join(f"-i {audio}" for audio in audio_files)
    #     audio_filter_complex = " ".join(
    #         f"[{n_videos + i}:a]" for i in range(len(audio_files))
    #     )
    #     n_audios = len(audio_files)

    #     # Create complex filter to mix audio files and concatenate video files
    #     filter_complex = (
    #         f"{video_filter_complex}concat=n={n_videos}:v=1:a=0[outv]; "
    #         f"{audio_filter_complex}amix=inputs={n_audios}[outa]"
    #     )

    #     cmd = (
    #         f"ffmpeg {video_input_cmd} {audio_input_cmd} "
    #         f'-filter_complex "{filter_complex}" '
    #         f'-map "[outv]" -map "[outa]" -c:v copy -c:a aac -strict -2 -y {output_file}'
    #     )

    #     # Run the command asynchronously
    #     process = await asyncio.create_subprocess_shell(
    #         cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    #     )

    #     # Wait for the command to complete and capture stdout and stderr
    #     stdout, stderr = await process.communicate()

    #     # Check for errors
    #     if process.returncode != 0:
    #         error_message = f"FFmpeg command failed: {stderr.decode('utf-8')}"
    #         raise Exception(error_message)

    #     return os.path.abspath(output_file)

    def sanitize_for_unix_filename(self, filename: str) -> str:
        """Helper function to sanitize string to valid filename, max len 100"""
        return "".join(
            char
            for char in filename.replace(" ", "_")
            if char.isalnum() or char in "_-"
        )[:100]

    def insert_linebreaks(self, input_string, max_line_length):
        words = input_string.split()
        current_line_length = 0
        lines = []
        current_line = []

        for word in words:
            if current_line_length + len(word) <= max_line_length:
                current_line.append(word)
                current_line_length += len(word) + 1  # Add 1 for the space
            else:
                lines.append(" ".join(current_line))
                current_line = [word]
                current_line_length = len(word) + 1

        # Add the last line if it contains any words
        if current_line:
            lines.append(" ".join(current_line))

        return "\n".join(lines)


# Test code to run when script is executed directly
if __name__ == "__main__":
    example_json_input = """{
        "duration": 30,
        "music_prompt": "orchestral EDM with a hint of bluegrass, rising to a crescendo",
        "narration" : "Bunnies should be very very careful these days. They are being hunted by the evil foxes.",
        "scenes": [
            {
                "duration": 2,
                "video_prompt": "a colorful rabbit juming across a green field",
                "sound_prompt": "crickets chirping",
                "text": "Funny bunny is happy",
                "generator": "glif1"
            },
            {
                "duration": 4,
                "video_prompt": "a colorful rabbit lying dead in the street",
                "sound_prompt": "machine gun firing",
                "text": "Funny bunny is not happy",
                "generator": "glif1"
            }
        ]
    }"""

    film4 = Film4()
    # film4.data = json.loads(example_json_input)

    # Run the generate method in an asyncio event loop
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(film4.ad_json_from_text("7 minute abs"))

        combined_video_filename = loop.run_until_complete(film4.generate())
        print(f"Generated combined video: {combined_video_filename}")
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        loop.close()

    # asyncio.run(film4.speech_from_text("Test of voice", "./temp_files/test_voice.mp3"))
