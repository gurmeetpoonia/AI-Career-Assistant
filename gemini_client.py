from google import genai
import os
from dotenv import load_dotenv
import time 
load_dotenv()

API_KEYS = [
    os.getenv("API_KEY_1"),
    os.getenv("API_KEY_2"),
    os.getenv("API_KEY_3"),
]

API_KEYS = [k for k in API_KEYS if k]

# Last successful key
CURRENT_KEY_INDEX = 0

# Store exhausted keys with retry time
BLOCKED_KEYS = {}

def generate_with_rotation(model, contents, config=None):

    global CURRENT_KEY_INDEX, BLOCKED_KEYS

    total_keys = len(API_KEYS)

    last_error = None

    for i in range(total_keys):

        index = (CURRENT_KEY_INDEX + i) % total_keys
        api_key = API_KEYS[index]

        # Skip blocked key
        if api_key in BLOCKED_KEYS:

            if time.time() < BLOCKED_KEYS[api_key]:
                continue

            else:
                del BLOCKED_KEYS[api_key]

        client = genai.Client(api_key=api_key)

        try:

            response = client.models.generate_content(
                model=model,
                contents=contents,
                config=config
            )

            # Remember last successful key
            CURRENT_KEY_INDEX = index

            return response

        except Exception as e:

            error = str(e)
            last_error = e

            # ----------------------------
            # Quota Exceeded (429)
            # ----------------------------
            if "429" in error or "RESOURCE_EXHAUSTED" in error:

                print(f"❌ API KEY {index+1} quota exceeded.")

                # Block this key for 60 seconds
                BLOCKED_KEYS[api_key] = time.time() + 60

                continue

            # ----------------------------
            # Server Busy (503)
            # ----------------------------
            elif "503" in error or "UNAVAILABLE" in error:

                print(f"⚠️ API KEY {index+1} server busy. Retrying...")

                time.sleep(3)

                try:

                    response = client.models.generate_content(
                        model=model,
                        contents=contents,
                        config=config
                    )

                    CURRENT_KEY_INDEX = index

                    return response

                except Exception:

                    continue

            # ----------------------------
            # Any other error
            # ----------------------------
            else:
                raise e
            
    raise Exception(
        "All Gemini API Keys are unavailable or quota exceeded."
    ) from last_error        