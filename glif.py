import aiohttp
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)


# Function to call Glif API, return URL to image
async def call_glif_api(input_text: str) -> str:
    logging.info("Calling the Glif API.")
    async with aiohttp.ClientSession() as session:
        payload = {"id": "clooa2ge8002sl60ixieiocdp", "input": [input_text]}
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
