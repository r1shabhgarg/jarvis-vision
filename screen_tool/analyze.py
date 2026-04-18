import os
import json
import base64
from openai import OpenAI
from dotenv import load_dotenv
from .prompts import SYSTEM_PROMPT

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY", "")

# Initialize Groq client (using OpenAI-compatible SDK)
client = None
if API_KEY:
    client = OpenAI(
        api_key=API_KEY,
        base_url="https://api.groq.com/openai/v1",
        timeout=60.0  # Increased timeout for vision processing
    )

# Current state-of-the-art vision model on Groq
MODEL_NAME = "meta-llama/llama-4-scout-17b-16e-instruct"
CONTEXT_FILE = "context_memory.json"


def get_base64_image(image_path: str) -> str:
    """Read image to base64 encoding."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def get_media_type(image_path: str) -> str:
    """Detect media type from file extension."""
    ext = os.path.splitext(image_path)[1].lower()
    return {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }.get(ext, "image/jpeg")


def load_context() -> list:
    """Loads previous conversation context from local file."""
    if os.path.exists(CONTEXT_FILE):
        try:
            with open(CONTEXT_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_context(history: list):
    """Saves conversation context to local file."""
    with open(CONTEXT_FILE, 'w') as f:
        json.dump(history, f)


def analyze_image(image_path: str, command: str, use_context: bool = False) -> dict:
    """Sends image and command to Groq Llama 4 Scout for analysis."""

    if not API_KEY or not client:
        raise ValueError("GROQ_API_KEY is not set in the .env file.")

    base64_image = get_base64_image(image_path)
    media_type = get_media_type(image_path)

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{media_type};base64,{base64_image}"
                    }
                },
                {
                    "type": "text",
                    "text": f"{command}. Return ONLY valid JSON matching the schema."
                }
            ]
        }
    ]

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            response_format={"type": "json_object"}
        )

        text_resp = response.choices[0].message.content

        # Save raw response for debugging
        with open("last_raw_response.txt", "w", encoding="utf-8") as f:
            f.write(text_resp)

        import re
        clean_text = text_resp.replace('```json', '').replace('```', '').strip()

        def is_low_quality_response(parsed: dict) -> bool:
            bad_phrases = ["no folders", "not mentioned", "no action items", "consider adding folders"]
            res_str = json.dumps(parsed).lower()
            return sum(1 for p in bad_phrases if p in res_str) >= 2

        def save_if_quality(parsed: dict, cmd: str, resp_text: str):
            if is_low_quality_response(parsed):
                return
            history = load_context()
            history.append({"role": "user", "content": cmd})
            history.append({"role": "assistant", "content": resp_text})
            save_context(history)

        try:
            parsed_json = json.loads(clean_text)
            save_if_quality(parsed_json, command, text_resp)
            return parsed_json
        except Exception:
            # Fallback regex extraction
            match = re.search(r'\{.*\}', clean_text, re.DOTALL)
            if match:
                try:
                    parsed_json = json.loads(match.group(0))
                    save_if_quality(parsed_json, command, text_resp)
                    return parsed_json
                except Exception:
                    pass
            
            raise ValueError(f"Failed to parse JSON: {text_resp}")

    except Exception as e:
        print(f"GROQ API ERROR: {e}")
        return {
            "screen_type": "error",
            "summary": ["System Error during Groq analysis.", str(e)],
            "key_information": ["Provider: Groq", f"Model: {MODEL_NAME}"],
            "action_items": [],
            "suggestions": ["Check API status", "Increase timeout"],
            "quick_actions": ["Retry"],
            "actions": []
        }


def chat_image(image_path: str, command: str) -> str:
    """Conversational follow-up using Groq image context."""
    if not API_KEY or not client:
        raise ValueError("GROQ_API_KEY is not set.")

    base64_image = get_base64_image(image_path)
    media_type = get_media_type(image_path)
    history = load_context()

    if len(history) > 6:
        history = history[-6:]

    SYSTEM_INSTRUCTION = (
        "You are Jarvis, a highly intelligent, sharp, and proactive AI assistant analyzing the user's screen. "
        "Your tone must be professional, authoritative, and concise—exactly like Jarvis from Iron Man."
    )

    messages = [{"role": "system", "content": SYSTEM_INSTRUCTION}]
    for turn in history:
        messages.append({"role": turn["role"], "content": turn["content"]})

    messages.append({
        "role": "user",
        "content": [
            {
                "type": "image_url",
                "image_url": {"url": f"data:{media_type};base64,{base64_image}"}
            },
            {"type": "text", "text": command}
        ]
    })

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages
        )
        text_resp = response.choices[0].message.content
        history.append({"role": "user", "content": command})
        history.append({"role": "assistant", "content": text_resp})
        save_context(history)
        return text_resp
    except Exception as e:
        return f"Groq Error: {str(e)}"
