import aiohttp
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# clp0liuxc0012la0f09f955rk


# Function to call Glif API, return URL to image
async def call_glif_api(input_text: str) -> str:
    logging.info("Calling the Glif API.")
    glif_id = "clooa2ge8002sl60ixieiocdp"  # Fabian's game glif
    # glif_id = "clp0liuxc0012la0f09f955rk"
    async with aiohttp.ClientSession() as session:
        payload = {"id": glif_id, "input": [input_text]}
        headers = {"Content-Type": "application/json"}

        async with session.post(
            "https://simple-api.glif.app", json=payload, headers=headers
        ) as response:
            if response.status == 200:
                response_data = await response.json()
                image_url = response_data.get("output", "")
                logging.info(f"Glif API responded with URL: {image_url}")
                return image_url
            else:
                error_message = f"Error calling Glif API: {response.status}"
                logging.error(error_message)
                return ""


# Function to call Glif API
async def call_glif_story_api(input_text: str) -> str:
    logging.info(f"Calling the Glif API call_glif_story_api with prompt '{input_text}'.")
    # glif_id = "clooa2ge8002sl60ixieiocdp" # Fabian's game glif
    glif_id = "clp0liuxc0012la0f09f955rk"
    async with aiohttp.ClientSession() as session:
        payload = {
            "id": glif_id,
            "input": {
                "prompt": input_text, 
                "imagestyle": "comic book style using 8-bit pixel graphics"
            },
        }
        headers = {"Content-Type": "application/json"}

        async with session.post(
            "https://simple-api.glif.app", json=payload, headers=headers
        ) as response:
            if response.status == 200:
                response_data = await response.json()
                logging.info("response_data:")
                logging.info(response_data)
                image_url_1 = response_data.get("image1", "")
                image_url_2 = response_data.get("image2", "")
                image_url_3 = response_data.get("image3", "")
                image_url_4 = response_data.get("image4", "")
                logging.info(f"Glif API responded with URL: {image_url_1}")
                return image_url_1, image_url_2, image_url_3, image_url_4
            else:
                error_message = f"Error calling Glif API: {response.status}"
                logging.error(error_message)
                return ""
