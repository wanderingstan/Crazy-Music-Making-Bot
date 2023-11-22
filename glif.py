import aiohttp
import logging
import json
import config
import time
import sqlite3

# Configure logging
logging.basicConfig(level=logging.INFO)




# Initialize and create table if it doesn't exist
def init_db():
    with sqlite3.connect(config.db_path) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS player_state (
                player_id TEXT PRIMARY KEY,
                glif_id TEXT,
                timestamp REAL,
                game_state TEXT
            )
        ''')


# Function to get player state
def get_player_state(player_id):
    with sqlite3.connect(config.db_path) as conn:
        cursor = conn.execute('SELECT glif_id, timestamp, game_state FROM player_state WHERE player_id = ?', (player_id,))
        row = cursor.fetchone()
        if row:
            return {"glif_id": row[0], "timestamp": row[1], "game_state": row[2]}
        return None

# Function to update player state
def update_player_state(player_id, glif_id, timestamp, game_state):
    with sqlite3.connect(config.db_path) as conn:
        conn.execute('''
            INSERT INTO player_state (player_id, glif_id, timestamp, game_state)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(player_id) 
            DO UPDATE SET
                glif_id = excluded.glif_id,
                timestamp = excluded.timestamp,
                game_state = excluded.game_state
        ''', (player_id, glif_id, timestamp, game_state))


# ------------------------------------------------------------

# Function to call Glif API, return URL to image
async def image_glif(input_text: str) -> str:
    logging.info("🕒 Calling the Glif API.")
    glif_id = "clooa2ge8002sl60ixieiocdp"  # Fabian's game glif
    # glif_id = "clp0liuxc0012la0f09f955rk"

    if config.DO_FAKE_RESULTS:
        # return "https://res.cloudinary.com/dzkwltgyd/image/upload/v1699551574/glif-run-outputs/s6s7h7fypr9pr35bpxul.png"
        return f"./test_files/wanderingstan_1175179192011333713_img.jpg"

    async with aiohttp.ClientSession() as session:
        payload = {"id": glif_id, "input": [input_text]}
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


# Function to call Glif API. Returns URLs to 4 images
async def story_glif(input_text: str) -> str:
    logging.info(f"🕒 Calling story_glif with prompt '{input_text}'.")
    glif_id = "clp0liuxc0012la0f09f955rk"  # Stan's Glif
    async with aiohttp.ClientSession() as session:
        payload = {
            "id": glif_id,
            "input": {
                "prompt": input_text,
                "imagestyle": "comic book style using 8-bit pixel graphics",
            },
        }
        headers = {"Content-Type": "application/json"}

        if config.DO_FAKE_RESULTS:
            # response_data = {'id': 'clp0liuxc0012la0f09f955rk', 'inputs': {'prompt': 'John and mary go mountain biking in the alps', 'imagestyle': 'comic book style using 8-bit pixel graphics'}, 'output': '{\n  "part1" : "John and Mary were adventurous souls who longed for the adrenaline rush of mountain biking in the majestic Alps, where snowy peaks and lush valleys intertwined to create a breathtaking backdrop for their daring escapades. Little did they know that an unexpected obstacle awaited them on their exhilarating journey.",\n  "part2" : "As they pedaled through the treacherous terrain, their bikes gracefully gliding over rocky paths and dusty trails, a sudden storm unleashed its fury upon them, turning their once peaceful ride into a battle against nature\'s wrath. With each passing minute, the wind howled louder, rain poured harder, and visibility dwindled, testing their resilience and challenging their determination to conquer the mountains.",\n  "part3" : "In the midst of the tempest, their path became obscured, leading them towards the edge of a perilous cliff. Panic and fear gripped their hearts as they realized the gravity of the situation, their bikes teetering on the brink of disaster. With no time to spare, their survival instincts kicked in, prompting them to make a split-second decision that would define their fate.",\n  "part4" : "Summoning their courage, John and Mary clung onto each other, embracing the fierce winds, and maneuvered their bikes away from the precipice, narrowly avoiding a catastrophic end. Exhausted but triumphant, they emerged from the storm, strengthened by their shared experience and a deepened bond. With the storm now behind them, they continued their exhilarating journey, etching memories of resilience and adventure into the breathtaking landscape of the Alps.",\n  "image1" : "https://res.cloudinary.com/dzkwltgyd/image/upload/v1700153640/glif-run-outputs/xjsjz6mcgkdfq6dqsrg7.jpg",\n  "image2" : "https://res.cloudinary.com/dzkwltgyd/image/upload/v1700153652/glif-run-outputs/dslwqfsqxfz6mtsbodw0.jpg",\n  "image3" : "https://res.cloudinary.com/dzkwltgyd/image/upload/v1700153665/glif-run-outputs/wl6vbfoyjy6axtvjcttx.jpg",\n  "image4" : "https://res.cloudinary.com/dzkwltgyd/image/upload/v1700153679/glif-run-outputs/ay131vvwnomkum4txidc.jpg"\n}', 'outputFull': {'type': 'TEXT', 'value': '{\n  "part1" : "John and Mary were adventurous souls who longed for the adrenaline rush of mountain biking in the majestic Alps, where snowy peaks and lush valleys intertwined to create a breathtaking backdrop for their daring escapades. Little did they know that an unexpected obstacle awaited them on their exhilarating journey.",\n  "part2" : "As they pedaled through the treacherous terrain, their bikes gracefully gliding over rocky paths and dusty trails, a sudden storm unleashed its fury upon them, turning their once peaceful ride into a battle against nature\'s wrath. With each passing minute, the wind howled louder, rain poured harder, and visibility dwindled, testing their resilience and challenging their determination to conquer the mountains.",\n  "part3" : "In the midst of the tempest, their path became obscured, leading them towards the edge of a perilous cliff. Panic and fear gripped their hearts as they realized the gravity of the situation, their bikes teetering on the brink of disaster. With no time to spare, their survival instincts kicked in, prompting them to make a split-second decision that would define their fate.",\n  "part4" : "Summoning their courage, John and Mary clung onto each other, embracing the fierce winds, and maneuvered their bikes away from the precipice, narrowly avoiding a catastrophic end. Exhausted but triumphant, they emerged from the storm, strengthened by their shared experience and a deepened bond. With the storm now behind them, they continued their exhilarating journey, etching memories of resilience and adventure into the breathtaking landscape of the Alps.",\n  "image1" : "https://res.cloudinary.com/dzkwltgyd/image/upload/v1700153640/glif-run-outputs/xjsjz6mcgkdfq6dqsrg7.jpg",\n  "image2" : "https://res.cloudinary.com/dzkwltgyd/image/upload/v1700153652/glif-run-outputs/dslwqfsqxfz6mtsbodw0.jpg",\n  "image3" : "https://res.cloudinary.com/dzkwltgyd/image/upload/v1700153665/glif-run-outputs/wl6vbfoyjy6axtvjcttx.jpg",\n  "image4" : "https://res.cloudinary.com/dzkwltgyd/image/upload/v1700153679/glif-run-outputs/ay131vvwnomkum4txidc.jpg"\n}'}}
            response_data = {
                "id": "clp0liuxc0012la0f09f955rk",
                "inputs": {
                    "prompt": "Intelligent mouse conquers the world.",
                    "imagestyle": "comic book style using 8-bit pixel graphics",
                },
                "output": '{\n  "part1" : "In a small, cozy attic lived a highly intelligent mouse named Max, who dreamed of one day conquering the world with his intelligence and wit.",\n  "part2" : "Max embarked on a journey through dark alleys and hidden corners, gathering a group of loyal rodent friends who shared his ambition, as they planned their strategic takeover.",\n  "part3" : "Amidst a grand gathering of world leaders, Max revealed his ingenious invention—a device that could translate mouse squeaks into human language, leaving everyone astounded and eager to understand the secret world of mice.",\n  "part4" : "With the world now aware of the hidden brilliance of mice, Max and his rodent alliance negotiated a compromise that ensured their protection and respect, forever changing the paradigms of power and intelligence.",\n  "image1" : "https://res.cloudinary.com/dzkwltgyd/image/upload/v1700259865/glif-run-outputs/v5pr3f40mfrimunn8xcm.jpg",\n  "image2" : "https://res.cloudinary.com/dzkwltgyd/image/upload/v1700259895/glif-run-outputs/tggirt9wrqerwok7q1mf.jpg",\n  "image3" : "https://res.cloudinary.com/dzkwltgyd/image/upload/v1700259907/glif-run-outputs/w3qiepqh88rshibwdkhj.jpg",\n  "image4" : "https://res.cloudinary.com/dzkwltgyd/image/upload/v1700259922/glif-run-outputs/eb0uqh2beve2xlkujae2.jpg"\n}',
                "outputFull": {
                    "type": "TEXT",
                    "value": '{\n  "part1" : "In a small, cozy attic lived a highly intelligent mouse named Max, who dreamed of one day conquering the world with his intelligence and wit.",\n  "part2" : "Max embarked on a journey through dark alleys and hidden corners, gathering a group of loyal rodent friends who shared his ambition, as they planned their strategic takeover.",\n  "part3" : "Amidst a grand gathering of world leaders, Max revealed his ingenious invention—a device that could translate mouse squeaks into human language, leaving everyone astounded and eager to understand the secret world of mice.",\n  "part4" : "With the world now aware of the hidden brilliance of mice, Max and his rodent alliance negotiated a compromise that ensured their protection and respect, forever changing the paradigms of power and intelligence.",\n  "image1" : "https://res.cloudinary.com/dzkwltgyd/image/upload/v1700259865/glif-run-outputs/v5pr3f40mfrimunn8xcm.jpg",\n  "image2" : "https://res.cloudinary.com/dzkwltgyd/image/upload/v1700259895/glif-run-outputs/tggirt9wrqerwok7q1mf.jpg",\n  "image3" : "https://res.cloudinary.com/dzkwltgyd/image/upload/v1700259907/glif-run-outputs/w3qiepqh88rshibwdkhj.jpg",\n  "image4" : "https://res.cloudinary.com/dzkwltgyd/image/upload/v1700259922/glif-run-outputs/eb0uqh2beve2xlkujae2.jpg"\n}',
                },
            }
            output = json.loads(response_data.get("output"))
            image_url_1 = output.get("image1", "")
            image_url_2 = output.get("image2", "")
            image_url_3 = output.get("image3", "")
            image_url_4 = output.get("image4", "")

            logging.info(
                f"😎 Using faked test response from Glif API responded with URLs: \n{image_url_1}\n{image_url_2}\n{image_url_3}\n{image_url_4}"
            )
            return image_url_1, image_url_2, image_url_3, image_url_4

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

                logging.info(
                    f"🟢 Glif API responded with URLs: \n{image_url_1}\n{image_url_2}\n{image_url_3}\n{image_url_4}"
                )
                return image_url_1, image_url_2, image_url_3, image_url_4
            else:
                error_message = f"Error calling Glif API: {response.status}"
                raise Exception(error_message)


# Function to call Glif API. Returns URLs to 4 images
async def chattorio_glif(
    action_input_text: str, player_id: str, glif_id: str = None, inventory: str = None
) -> str:
    logging.info(f"🕒 Calling chattorio_glif with prompt '{action_input_text}'.")

    # TODO: move this to config.py
    # default_glif_id = "clp8aafnv0016jr0f5wrrgalv" # Fabian's Glif
    # default_glif_id = "clp8kxydk004ll10glo3rskx4"  # Stan's copy of Fabian's Glif (stanbot)
    default_glif_id = "clp94bjzu0030vf801f8t602x"  # Stan's copy of Fabian's Glif (private bot) 
    
    default_starting_inventory = """
1 COAL
2 FACTORIES
0 IRON
"""

    now = time.time()

    # Get existing state
    start_state = get_player_state(player_id)

    if start_state is None:
        # First time player
        logging.info("⚠️  First time player, creating new state.")
        start_state = {
            "glif_id": default_glif_id,
            "timestamp": now, 
            "game_state": default_starting_inventory,
        }

    if glif_id is not None:
        logging.info(f"⚠️ As requested, changing glif_id to {glif_id}.")
        api_glif_id = glif_id
    elif "glif_id" not in start_state or start_state["glif_id"] is None:
        logging.info("⚠️ No glif_id in start_state, using default.")
        api_glif_id = default_glif_id
    else:
        # Normal flow
        api_glif_id = start_state["glif_id"]

    if inventory is not None:
        logging.info(f"⚠️ As requested, changing inventory to {inventory}.")
        start_state["game_state"] = inventory

    if len(api_glif_id) != 25:
        logging.info(f"⚠️ glif_id invalid ({api_glif_id}), using default")
        api_glif_id = default_glif_id

    async with aiohttp.ClientSession() as session:
        payload = {
            "id": api_glif_id,
            "input": {
                "stateinput": start_state["game_state"],
                "action": action_input_text,
                "seconds_elapsed": str(now - start_state["timestamp"]),
            },
        }
        headers = {"Content-Type": "application/json"}

        if config.DO_FAKE_RESULTS:
            # response_data = {'id': 'clp0liuxc0012la0f09f955rk', 'inputs': {'prompt': 'Intelligent mouse conquers the world.', 'imagestyle': 'comic book style using 8-bit pixel graphics'}, 'output': '{\n  "part1" : "In a small, cozy attic lived a highly intelligent mouse named Max, who dreamed of one day conquering the world with his intelligence and wit.",\n  "part2" : "Max embarked on a journey through dark alleys and hidden corners, gathering a group of loyal rodent friends who shared his ambition, as they planned their strategic takeover.",\n  "part3" : "Amidst a grand gathering of world leaders, Max revealed his ingenious invention—a device that could translate mouse squeaks into human language, leaving everyone astounded and eager to understand the secret world of mice.",\n  "part4" : "With the world now aware of the hidden brilliance of mice, Max and his rodent alliance negotiated a compromise that ensured their protection and respect, forever changing the paradigms of power and intelligence.",\n  "image1" : "https://res.cloudinary.com/dzkwltgyd/image/upload/v1700259865/glif-run-outputs/v5pr3f40mfrimunn8xcm.jpg",\n  "image2" : "https://res.cloudinary.com/dzkwltgyd/image/upload/v1700259895/glif-run-outputs/tggirt9wrqerwok7q1mf.jpg",\n  "image3" : "https://res.cloudinary.com/dzkwltgyd/image/upload/v1700259907/glif-run-outputs/w3qiepqh88rshibwdkhj.jpg",\n  "image4" : "https://res.cloudinary.com/dzkwltgyd/image/upload/v1700259922/glif-run-outputs/eb0uqh2beve2xlkujae2.jpg"\n}', 'outputFull': {'type': 'TEXT', 'value': '{\n  "part1" : "In a small, cozy attic lived a highly intelligent mouse named Max, who dreamed of one day conquering the world with his intelligence and wit.",\n  "part2" : "Max embarked on a journey through dark alleys and hidden corners, gathering a group of loyal rodent friends who shared his ambition, as they planned their strategic takeover.",\n  "part3" : "Amidst a grand gathering of world leaders, Max revealed his ingenious invention—a device that could translate mouse squeaks into human language, leaving everyone astounded and eager to understand the secret world of mice.",\n  "part4" : "With the world now aware of the hidden brilliance of mice, Max and his rodent alliance negotiated a compromise that ensured their protection and respect, forever changing the paradigms of power and intelligence.",\n  "image1" : "https://res.cloudinary.com/dzkwltgyd/image/upload/v1700259865/glif-run-outputs/v5pr3f40mfrimunn8xcm.jpg",\n  "image2" : "https://res.cloudinary.com/dzkwltgyd/image/upload/v1700259895/glif-run-outputs/tggirt9wrqerwok7q1mf.jpg",\n  "image3" : "https://res.cloudinary.com/dzkwltgyd/image/upload/v1700259907/glif-run-outputs/w3qiepqh88rshibwdkhj.jpg",\n  "image4" : "https://res.cloudinary.com/dzkwltgyd/image/upload/v1700259922/glif-run-outputs/eb0uqh2beve2xlkujae2.jpg"\n}'}}
            # logging.info(f"😎 Using faked test response from Glif API responded with URLs: \n{image_url_1}\n{image_url_2}\n{image_url_3}\n{image_url_4}")
            # return image_url_1, image_url_2, image_url_3, image_url_4
            return "NYI"

        logging.info("Payload:")
        logging.info(payload)

        async with session.post(
            "https://simple-api.glif.app", json=payload, headers=headers
        ) as response:
            if response.status == 200:
                response_data = await response.json()
                logging.info("response_data:")
                logging.info(response_data)

                output = response_data.get("output")

                logging.info(f"🟢 Glif API responded with")
                logging.info(output)

                # Why is LLM adding these prefixes?
                cleaned_output_str = output.replace("```json\n", "").replace(
                    "\n```", ""
                )
                data = json.loads(cleaned_output_str)

                if data is None:
                    raise Exception("No output was returned from the model.")

                narrator = data["narrator"]
                reasoning = data["state"]["reasoning"]
                updated_state = data["state"]["updated_state"]
                image = data["image"] if "image" in data else None

                logging.info(
                    "🟢" + f"Glif API responded with:", json.dumps(data, indent=4)
                )

                # Save the state
                update_player_state(player_id, api_glif_id, time.time(), updated_state)

                return start_state, narrator, reasoning, image, get_player_state(player_id)

            else:
                error_message = f"Error calling Glif API: {response.status}"
                raise Exception(error_message)


# Ensure database and table are created
init_db()
