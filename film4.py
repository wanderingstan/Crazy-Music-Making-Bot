import logging
import config
import asyncio
import replicate
import aiohttp
import json
import os
import video_generation


class Film4:
    def __init__(self, json_input: str, filename_prefix: str = "./temp_files/"):
        logging.basicConfig(level=logging.INFO)

        # Parse the JSON input
        self.data = json.loads(json_input)
        self.filename_prefix = filename_prefix

    def generate(self):
        # Parse the JSON input

        # Iterate through each scene in the 'scenes' array
        for scene in self.data["scenes"]:
            # Extract information from the scene and call create_scene
            asyncio.run(
                self.create_scene(
                    scene["duration"],
                    scene["video_prompt"],
                    scene["sound_prompt"],
                    scene["text"],
                )
            )

    async def create_scene(self, duration, video_prompt, sound_prompt, text):
        # Implement your scene creation logic here
        print(
            f"Creating scene with duration {duration} and video prompt {video_prompt}"
        )

        # Start both glif API and replicate API calls concurrently
        video_url, sound_url = await asyncio.gather(
            self.video_from_prompt(video_prompt),
            self.sound_from_prompt(sound_prompt),
        )

        # GENERATE VIDEO

    async def sound_from_prompt(self, prompt: str) -> str:
        # Implement sound_from_prompt logic
        return None

    async def video_from_prompt(self, prompt: str) -> str:
        """ Generate video from prompt using Replicate API, return path to video file."""

        logging.info(f"🎬 Generating video for prompt: {prompt}")

        # Testing
        if config.DO_FAKE_RESULTS:
            logging.info("😎 Using fake replicate video response for testing.")
            return "test_files/video_gen_sample.mp4"

        if not config.REPLICATE_API_TOKEN:
            raise ValueError("No Replicate API token REPLICATE_API_TOKEN.")

        # Initialize Replicate Client with your API token
        replicate_client = replicate.Client(api_token=config.REPLICATE_API_TOKEN)

        logging.info("🕒 Calling the Replicate API for video generation.")

        # Run the new music generation model using Replicate API
        # https://replicate.com/cjwbw/kandinskyvideo?input=python
        output_url = await asyncio.to_thread(
            replicate_client.run,
            "cjwbw/kandinskyvideo:849b70f3e300a650aa8b78d0f8f24d104824b832ea7f61c79bd2c7e78a4ad545",
            input={
                "fps": 10,
                "width": 640,
                "height": 384,
                "prompt": prompt,
                "guidance_scale": 5,
                "interpolation_level": "low",
                "num_inference_steps": 50,
                "interpolation_guidance_scale": 0.25,
            },
        )

        if output_url is None:
            raise Exception("No output_URL was returned from the model.")

        # Download the generated video file
        output_format = "mp4"
        filename = f"{filename_prefix}{sanitize_for_unix_filename(prompt)}.{output_format}"
        filename = f"{filename_prefix}video.{output_format}"

        logging.info(f"🟢 Saving video to {filename}")

        async with aiohttp.ClientSession() as session:
            async with session.get(output_url) as response:
                if response.status == 200:
                    with open(filename, "wb") as f:
                        f.write(await response.read())
                    return filename
                else:
                    raise Exception(f"Error downloading music: {response.status}")


        

    def sanitize_for_unix_filename(self, filename: str) -> str:
        return "".join(char for char in filename if char.isalnum() or char in "._-")


# Test code to run when script is executed directly
if __name__ == "__main__":
    example_json_input = """{
        "duration": "30",
        "music_prompt": "orchestral EDM with a hint of bluegrass, rising to a crescendo",
        "scenes": [
            {
                "duration": 10,
                "video_prompt": "a colorful rabbit juming across a green field",
                "sound_prompt": "crickets chirping",
                "text": "Funny bunny is happy"
            },
            {
                "duration": 15,
                "video_prompt": "a colorful rabbit lying dead in the street",
                "sound_prompt": "machine gun firing",
                "text": "Funny bunny is not happy"
            }
        ]
    }"""

    film4 = Film4(example_json_input)
    film4.generate()

    # test_prompt = "a cyclist riding fast through a corner on a california road, close view, sunny day"
    # loop = asyncio.get_event_loop()
    # try:
    #     video_file = loop.run_until_complete(
    #         film4.video_from_prompt(test_prompt, "./temp_files/test_")
    #     )
    #     print(f"Generated video saved to: {video_file}")
    # except Exception as e:
    #     print(f"Error occurred: {e}")
    # finally:
    #     loop.close()


# def process_json_input(json_input):
#     # example_json_input = """{
#     #     "duration": "30",
#     #     "music_prompt": "orchestral EDM with a hint of bluegrass, rising to a crescendo",
#     #     "scenes": [
#     #         {
#     #             "duration": 10,
#     #             "video_prompt": "a colorful rabbit juming across a green field",
#     #             "sound_prompt": "crickets chirping",
#     #             "text": "Funny bunny is happy"
#     #         },
#     #         {
#     #             "duration": 15,
#     #             "video_prompt": "a colorful rabbit lying dead in the street",
#     #             "sound_prompt": "machine gun firing",
#     #             "text": "Funny bunny is not happy"
#     #         }
#     #     ]
#     # }"""

#     # Parse the JSON input
#     data = json.loads(json_input)

#     # Iterate through each scene in the 'scenes' array
#     for scene in data["scenes"]:
#         # Extract information from the scene
#         duration = scene["duration"]
#         video_prompt = scene["video_prompt"]
#         sound_prompt = scene["sound_prompt"]
#         text = scene["text"]

#         # Call the create_scene function
#         create_scene(duration, video_prompt, sound_prompt, text)


# async def create_scene(duration, video_prompt, sound_prompt, text):
#     # Implement your scene creation logic here
#     print(f"Creating scene with duration {duration} and video prompt {video_prompt}")

#     try:
#         # Start both glif API and replicate API calls concurrently
#         video_url, sound_url = await asyncio.gather(
#             video_from_prompt(video_prompt),
#             sound_from_prompt(sound_prompt),
#         )

#         # Check if both the image and the music were successfully generated
#         if video_from_prompt and sound_from_prompt:
#             # Generate the video
#             video_path = await video_generation.generate_video(
#                 image_path, mp3_path, temp_file_prefix(ctx), duration=8
#             )

#             # Send the video to the Discord channel
#             await ctx.send(file=File(video_path))
#             await ctx.send(prompt)

#             # Clean up the generated files
#             if config.DELETE_TEMP_FILES:
#                 os.path.exists(video_path) and os.remove(video_path)
#                 os.path.exists(mp3_path) and os.remove(mp3_path)
#                 os.path.exists(image_path) and os.remove(image_path)
#         else:
#             await ctx.send("An error occurred while generating the video components.")

#     except Exception as e:
#         logging.exception(f"An error occurred while handling the video request: {e}")
#         await ctx.send(f"An error occurred while handling your video request: {e}")


# # Function to call XXXX API, return URL to sound
# async def sound_from_prompt(prompt: str, filename_prefix: str) -> str:
#     return None


# # Function to call Replicate API, return URL to video
# async def video_from_prompt(prompt: str, filename_prefix: str) -> str:
#     logging.info(f"🎬 Generating video for prompt: {prompt}")

#     # Testing
#     if config.DO_FAKE_RESULTS:
#         logging.info("😎 Using fake replicate video response for testing.")
#         return "test_files/video_gen_sample.mp4"

#     if not config.REPLICATE_API_TOKEN:
#         raise ValueError("No Replicate API token REPLICATE_API_TOKEN.")

#     # Initialize Replicate Client with your API token
#     replicate_client = replicate.Client(api_token=config.REPLICATE_API_TOKEN)

#     logging.info("🕒 Calling the Replicate API for video generation.")

#     # Run the new music generation model using Replicate API
#     # https://replicate.com/cjwbw/kandinskyvideo?input=python
#     output_url = await asyncio.to_thread(
#         replicate_client.run,
#         "cjwbw/kandinskyvideo:849b70f3e300a650aa8b78d0f8f24d104824b832ea7f61c79bd2c7e78a4ad545",
#         input={
#             "fps": 10,
#             "width": 640,
#             "height": 384,
#             "prompt": prompt,
#             "guidance_scale": 5,
#             "interpolation_level": "low",
#             "num_inference_steps": 50,
#             "interpolation_guidance_scale": 0.25,
#         },
#     )

#     if output_url is None:
#         raise Exception("No output_URL was returned from the model.")

#     # Download the generated music file
#     output_format = "mp4"
#     filename = f"{filename_prefix}{sanitize_for_unix_filename(prompt)}.{output_format}"
#     filename = f"{filename_prefix}video.{output_format}"

#     logging.info(f"🟢 Saving video to {filename}")

#     async with aiohttp.ClientSession() as session:
#         async with session.get(output_url) as response:
#             if response.status == 200:
#                 with open(filename, "wb") as f:
#                     f.write(await response.read())
#                 return filename
#             else:
#                 raise Exception(f"Error downloading music: {response.status}")


# # Function to sanitize filename (assuming you need it)
# def sanitize_for_unix_filename(filename: str) -> str:
#     return "".join(char for char in filename if char.isalnum() or char in "._-")


# # Entry point for direct CLI execution
# if __name__ == "__main__":
#     # Test prompt for video generation
#     test_prompt = "a cyclist riding fast through a corner on a california road, close view, sunny day"

#     # Run the video generation in an asyncio event loop
#     loop = asyncio.get_event_loop()
#     try:
#         video_file = loop.run_until_complete(
#             video_from_prompt(test_prompt, "./temp_files/test_")
#         )
#         print(f"Generated video saved to: {video_file}")
#     except Exception as e:
#         print(f"Error occurred: {e}")
#     finally:
#         loop.close()
