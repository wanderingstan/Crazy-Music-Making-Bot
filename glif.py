import aiohttp
import logging
import json 

# Configure logging
logging.basicConfig(level=logging.INFO)


# Function to call Glif API, return URL to image
async def call_glif_api(input_text: str) -> str:
    logging.info("🕒 Calling the Glif API.")
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
                logging.info(f"🟢 Glif API responded with URL: {image_url}")
                return image_url
            else:
                error_message = f"🔴 Error calling Glif API: {response.status}"
                logging.error(error_message)
                return ""


# Function to call Glif API
async def call_glif_story_api(input_text: str) -> str:
    logging.info(f"🕒 Calling the Glif API call_glif_story_api with prompt '{input_text}'.")
    glif_id = "clp0liuxc0012la0f09f955rk" # Stan's Glif
    async with aiohttp.ClientSession() as session:
        payload = {
            "id": glif_id,
            "input": {
                "prompt": input_text, 
                "imagestyle": "comic book style using 8-bit pixel graphics"
            },
        }
        headers = {"Content-Type": "application/json"}

        # # TEST DATA
        # # response_data = {'id': 'clp0liuxc0012la0f09f955rk', 'inputs': {'prompt': 'John and mary go mountain biking in the alps', 'imagestyle': 'comic book style using 8-bit pixel graphics'}, 'output': '{\n  "part1" : "John and Mary were adventurous souls who longed for the adrenaline rush of mountain biking in the majestic Alps, where snowy peaks and lush valleys intertwined to create a breathtaking backdrop for their daring escapades. Little did they know that an unexpected obstacle awaited them on their exhilarating journey.",\n  "part2" : "As they pedaled through the treacherous terrain, their bikes gracefully gliding over rocky paths and dusty trails, a sudden storm unleashed its fury upon them, turning their once peaceful ride into a battle against nature\'s wrath. With each passing minute, the wind howled louder, rain poured harder, and visibility dwindled, testing their resilience and challenging their determination to conquer the mountains.",\n  "part3" : "In the midst of the tempest, their path became obscured, leading them towards the edge of a perilous cliff. Panic and fear gripped their hearts as they realized the gravity of the situation, their bikes teetering on the brink of disaster. With no time to spare, their survival instincts kicked in, prompting them to make a split-second decision that would define their fate.",\n  "part4" : "Summoning their courage, John and Mary clung onto each other, embracing the fierce winds, and maneuvered their bikes away from the precipice, narrowly avoiding a catastrophic end. Exhausted but triumphant, they emerged from the storm, strengthened by their shared experience and a deepened bond. With the storm now behind them, they continued their exhilarating journey, etching memories of resilience and adventure into the breathtaking landscape of the Alps.",\n  "image1" : "https://res.cloudinary.com/dzkwltgyd/image/upload/v1700153640/glif-run-outputs/xjsjz6mcgkdfq6dqsrg7.jpg",\n  "image2" : "https://res.cloudinary.com/dzkwltgyd/image/upload/v1700153652/glif-run-outputs/dslwqfsqxfz6mtsbodw0.jpg",\n  "image3" : "https://res.cloudinary.com/dzkwltgyd/image/upload/v1700153665/glif-run-outputs/wl6vbfoyjy6axtvjcttx.jpg",\n  "image4" : "https://res.cloudinary.com/dzkwltgyd/image/upload/v1700153679/glif-run-outputs/ay131vvwnomkum4txidc.jpg"\n}', 'outputFull': {'type': 'TEXT', 'value': '{\n  "part1" : "John and Mary were adventurous souls who longed for the adrenaline rush of mountain biking in the majestic Alps, where snowy peaks and lush valleys intertwined to create a breathtaking backdrop for their daring escapades. Little did they know that an unexpected obstacle awaited them on their exhilarating journey.",\n  "part2" : "As they pedaled through the treacherous terrain, their bikes gracefully gliding over rocky paths and dusty trails, a sudden storm unleashed its fury upon them, turning their once peaceful ride into a battle against nature\'s wrath. With each passing minute, the wind howled louder, rain poured harder, and visibility dwindled, testing their resilience and challenging their determination to conquer the mountains.",\n  "part3" : "In the midst of the tempest, their path became obscured, leading them towards the edge of a perilous cliff. Panic and fear gripped their hearts as they realized the gravity of the situation, their bikes teetering on the brink of disaster. With no time to spare, their survival instincts kicked in, prompting them to make a split-second decision that would define their fate.",\n  "part4" : "Summoning their courage, John and Mary clung onto each other, embracing the fierce winds, and maneuvered their bikes away from the precipice, narrowly avoiding a catastrophic end. Exhausted but triumphant, they emerged from the storm, strengthened by their shared experience and a deepened bond. With the storm now behind them, they continued their exhilarating journey, etching memories of resilience and adventure into the breathtaking landscape of the Alps.",\n  "image1" : "https://res.cloudinary.com/dzkwltgyd/image/upload/v1700153640/glif-run-outputs/xjsjz6mcgkdfq6dqsrg7.jpg",\n  "image2" : "https://res.cloudinary.com/dzkwltgyd/image/upload/v1700153652/glif-run-outputs/dslwqfsqxfz6mtsbodw0.jpg",\n  "image3" : "https://res.cloudinary.com/dzkwltgyd/image/upload/v1700153665/glif-run-outputs/wl6vbfoyjy6axtvjcttx.jpg",\n  "image4" : "https://res.cloudinary.com/dzkwltgyd/image/upload/v1700153679/glif-run-outputs/ay131vvwnomkum4txidc.jpg"\n}'}}
        # response_data = {'id': 'clp0liuxc0012la0f09f955rk', 'inputs': {'prompt': 'Intelligent mouse conquers the world.', 'imagestyle': 'comic book style using 8-bit pixel graphics'}, 'output': '{\n  "part1" : "In a small, cozy attic lived a highly intelligent mouse named Max, who dreamed of one day conquering the world with his intelligence and wit.",\n  "part2" : "Max embarked on a journey through dark alleys and hidden corners, gathering a group of loyal rodent friends who shared his ambition, as they planned their strategic takeover.",\n  "part3" : "Amidst a grand gathering of world leaders, Max revealed his ingenious invention—a device that could translate mouse squeaks into human language, leaving everyone astounded and eager to understand the secret world of mice.",\n  "part4" : "With the world now aware of the hidden brilliance of mice, Max and his rodent alliance negotiated a compromise that ensured their protection and respect, forever changing the paradigms of power and intelligence.",\n  "image1" : "https://res.cloudinary.com/dzkwltgyd/image/upload/v1700259865/glif-run-outputs/v5pr3f40mfrimunn8xcm.jpg",\n  "image2" : "https://res.cloudinary.com/dzkwltgyd/image/upload/v1700259895/glif-run-outputs/tggirt9wrqerwok7q1mf.jpg",\n  "image3" : "https://res.cloudinary.com/dzkwltgyd/image/upload/v1700259907/glif-run-outputs/w3qiepqh88rshibwdkhj.jpg",\n  "image4" : "https://res.cloudinary.com/dzkwltgyd/image/upload/v1700259922/glif-run-outputs/eb0uqh2beve2xlkujae2.jpg"\n}', 'outputFull': {'type': 'TEXT', 'value': '{\n  "part1" : "In a small, cozy attic lived a highly intelligent mouse named Max, who dreamed of one day conquering the world with his intelligence and wit.",\n  "part2" : "Max embarked on a journey through dark alleys and hidden corners, gathering a group of loyal rodent friends who shared his ambition, as they planned their strategic takeover.",\n  "part3" : "Amidst a grand gathering of world leaders, Max revealed his ingenious invention—a device that could translate mouse squeaks into human language, leaving everyone astounded and eager to understand the secret world of mice.",\n  "part4" : "With the world now aware of the hidden brilliance of mice, Max and his rodent alliance negotiated a compromise that ensured their protection and respect, forever changing the paradigms of power and intelligence.",\n  "image1" : "https://res.cloudinary.com/dzkwltgyd/image/upload/v1700259865/glif-run-outputs/v5pr3f40mfrimunn8xcm.jpg",\n  "image2" : "https://res.cloudinary.com/dzkwltgyd/image/upload/v1700259895/glif-run-outputs/tggirt9wrqerwok7q1mf.jpg",\n  "image3" : "https://res.cloudinary.com/dzkwltgyd/image/upload/v1700259907/glif-run-outputs/w3qiepqh88rshibwdkhj.jpg",\n  "image4" : "https://res.cloudinary.com/dzkwltgyd/image/upload/v1700259922/glif-run-outputs/eb0uqh2beve2xlkujae2.jpg"\n}'}}        
        # output = json.loads(response_data.get("output"))
        # image_url_1 = output.get("image1", "")                
        # image_url_2 = output.get("image2", "")                
        # image_url_3 = output.get("image3", "")                
        # image_url_4 = output.get("image4", "")                

        # logging.info(f"😎 Using faked test response from Glif API responded with URLs: \n{image_url_1}\n{image_url_2}\n{image_url_3}\n{image_url_4}")
        # return image_url_1, image_url_2, image_url_3, image_url_4

        async with session.post(
            "https://simple-api.glif.app", json=payload, headers=headers
        ) as response:
            if response.status == 200:
                response_data = await response.json()
                logging.info("response_data:")
                logging.info(response_data)

                output = json.loads(response_data.get("output"))

                if output is None:
                    raise Exception("No output was returned from the model.")
                    
                image_url_1 = output.get("image1", "")                
                image_url_2 = output.get("image2", "")                
                image_url_3 = output.get("image3", "")                
                image_url_4 = output.get("image4", "")                

                logging.info(f"🟢 Glif API responded with URLs: \n{image_url_1}\n{image_url_2}\n{image_url_3}\n{image_url_4}")
                return image_url_1, image_url_2, image_url_3, image_url_4
            else:
                error_message = f"🔴 Error calling Glif API: {response.status}"
                logging.error(error_message)
                return ""
