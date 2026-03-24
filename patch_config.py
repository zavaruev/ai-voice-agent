import json

path = "/home/alexander/nanobot/data/config.json"
try:
    with open(path, "r") as f:
        config = json.load(f)

    if "tools" not in config:
        config["tools"] = {}
    if "mcpServers" not in config["tools"]:
        config["tools"]["mcpServers"] = {}

    config["tools"]["mcpServers"]["xiaozhi"] = {
        "command": "python3",
        "args": ["-u", "/app/xiaozhi_proxy.py"]
    }

    # remove old typo if exists
    if "mcp_servers" in config["tools"]:
        del config["tools"]["mcp_servers"]

    with open(path, "w") as f:
        json.dump(config, f, indent=2)

    print("Config patched successfully on .102!")
except Exception as e:
    print(f"Error: {e}")
