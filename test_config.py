import sys
import traceback
sys.path.append("/app")

with open("/root/.nanobot/test_output.txt", "w") as f:
    try:
        from nanobot.config import load_config
        c = load_config()
        if not c.tools.mcp_servers:
            f.write("MCP SERVERS ALIVE BUT EMPTY\n")
        else:
            for k, v in c.tools.mcp_servers.items():
                f.write(f"SERVER {k}: {v}\n")
    except Exception as e:
        f.write(f"Error loading config: {e}\n")
        f.write(traceback.format_exc())
