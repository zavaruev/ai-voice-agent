import sys
import traceback
sys.path.append("/app")

with open("/app/nanobot/test_manager_res.txt", "w") as f:
    try:
        from nanobot.config import load_config
        from nanobot.channels.registry import CHAN_REGISTRY, discover_all
        
        discover_all()
        c = load_config()
        
        for name, cls in CHAN_REGISTRY.items():
            if name != "voice_server":
                continue
            f.write(f"Channel {name} found in registry\n")
            section = getattr(c.channels, name, None)
            f.write(f"Config section: {section}\n")
            if section is not None:
                enabled = section.get("enabled", False) if isinstance(section, dict) else getattr(section, "enabled", False)
                f.write(f"Enabled: {enabled}\n")
                
                try:
                    # Let's try to instantiate it as manager does!
                    channel = cls(section, None)
                    f.write(f"Instantiated successfully!\n")
                except Exception as inst_err:
                    f.write(f"Instantiation failed: {inst_err}\n")
                    f.write(traceback.format_exc() + "\n")
            
    except Exception as e:
        f.write(f"Error: {e}\n")
        f.write(traceback.format_exc())
