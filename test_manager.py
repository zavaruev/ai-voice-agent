import sys
import traceback
sys.path.insert(0, "/app")

with open("/tmp/res.txt", "w") as f:
    try:
        from nanobot.config import load_config
        from nanobot.channels.registry import discover_all
        
        CHAN_REGISTRY = discover_all()
        c = load_config()
        
        for name, cls in CHAN_REGISTRY.items():
            if name != "voice_server":
                continue
            section = getattr(c.channels, name, None)
            f.write(f"{name} config: {section}\n")
            if section is not None:
                enabled = getattr(section, "enabled", False) if not isinstance(section, dict) else section.get("enabled", False)
                f.write(f"Enabled: {enabled}\n")
                try:
                    ch = cls(section, None)
                    f.write(f"Instantiated successfully!\n")
                except Exception as inst_err:
                    f.write(f"Instantiation failed: {inst_err}\n")
                    f.write(traceback.format_exc() + "\n")
            
    except Exception as e:
        f.write(f"Main Error: {e}\n")
        f.write(traceback.format_exc())
