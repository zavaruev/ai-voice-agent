import json
import traceback

with open("/tmp/res.txt", "w") as f:
    try:
        with open('/root/.nanobot/config.json', encoding='utf-8') as cf:
            d = json.load(cf)
        f.write(f"JSON KEYS: {list(d.get('channels', {}).keys())}\n")
    except Exception as e:
        f.write(f"Error: {e}\n{traceback.format_exc()}\n")
