import sys
import traceback
sys.path.append("/app")

with open("/root/.nanobot/test_channels.txt", "w") as f:
    try:
        from nanobot.config import load_config
        from nanobot.channels.registry import CHAN_REGISTRY, discover_all
        
        discover_all()
        f.write(f"CHAN_REGISTRY keys: {list(CHAN_REGISTRY.keys())}\n")
        
        c = load_config()
        has_vs = hasattr(c.channels, "voice_server")
        f.write(f"config.channels.voice_server exists: {has_vs}\n")
        
        if has_vs:
            vs = getattr(c.channels, "voice_server")
            enabled = vs.get("enabled", False) if isinstance(vs, dict) else getattr(vs, "enabled", False)
            f.write(f"voice_server enabled: {enabled}\n")
            
    except Exception as e:
        f.write(f"Error: {e}\n")
        f.write(traceback.format_exc())
