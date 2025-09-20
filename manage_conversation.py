import json

CONV_FILE = "conversation_history.json"

def load_conversation(thread_id):
    try:
        with open(CONV_FILE, "r") as f:
            all_convs = json.load(f)
        return all_convs.get(thread_id, [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_conversation(thread_id, messages):
    try:
        with open(CONV_FILE, "r") as f:
            all_convs = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        all_convs = {}
    all_convs[thread_id] = messages
    with open(CONV_FILE, "w") as f:
        json.dump(all_convs, f)