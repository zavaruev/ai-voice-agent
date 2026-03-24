# 🎙️ AI Voice Agent

> ESP32-based voice assistant with local wake-word detection, LLM integration, real-time STT/TTS and OTA firmware updates.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Home Network                            │
│                                                              │
│  ┌──────────────────┐        ┌───────────────────────────┐  │
│  │  ESP32 Device    │        │  Server (192.168.22.102)  │  │
│  │  (xiaozhi-esp32) │        │                           │  │
│  │                  │        │  ┌─────────────────────┐  │  │
│  │ 🎤 Microphone    │─OPUS──▶│  │  Nanobot Gateway    │  │  │
│  │ 🔊 Speaker       │◀─OPUS──│  │  (voice_server.py)  │  │  │
│  │                  │        │  └────────┬────────────┘  │  │
│  │ Wake Word:       │   WS   │           │               │  │
│  │ "Компьютер"      │◀──────▶│  ┌────────▼────────────┐  │  │
│  │                  │        │  │  OTA Server         │  │  │
│  │ Display: OLED    │        │  │  (ota_server.py)    │  │  │
│  └──────────────────┘        │  └─────────────────────┘  │  │
│                              └───────────┬───────────────┘  │
│                                          │                   │
│                          ┌───────────────▼────────────────┐ │
│                          │  GPU Server (192.168.22.111)   │ │
│                          │  Speaches STT (Whisper large)   │ │
│                          └────────────────────────────────┘ │
│                                                              │
│                          ☁️  OpenRouter / Ollama Cloud (LLM)  │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Wake Word** → ESP32 detects "Компьютер" via AFE neural net (offline)  
2. **Voice capture** → PCM audio compressed to OPUS, sent via WebSocket  
3. **STT** → Speaches (Whisper `large-v3`) transcribes speech to text  
4. **LLM** → Nanobot sends text to OpenRouter / Ollama Cloud  
5. **TTS** → Response synthesized and streamed back as OPUS  
6. **Playback** → ESP32 decodes and plays OPUS audio  

---

## 🧩 Components

| Component | Role | Location |
|---|---|---|
| [`xiaozhi-esp32`](https://github.com/78/xiaozhi-esp32) | ESP32 firmware (audio, wake-word, OTA) | submodule |
| [`nanobot`](https://github.com/HKUDS/nanobot) | LLM agent gateway + voice channel | submodule |
| [`speaches`](https://github.com/speaches-ai/speaches) | Local Whisper STT service | submodule |
| `ota_server.py` | Serves firmware `.bin` files by MAC address | root |
| `build_all.sh` | Builds firmware for all targets and deploys via SCP | root |

---

## 📦 Supported Hardware

| Board | Target Name | Display |
|---|---|---|
| **Xingzhi Cube 0.96 OLED WiFi** | `xingzhi-cube-0.96oled-wifi` | SSD1306 OLED |
| **Freenove ESP32-S3 2.8"** | `freenove_2.8` | ILI9341 LCD |

---

## ⚡ Quick Start

### 1. Clone with submodules

```bash
git clone --recurse-submodules https://github.com/zavaruev/ai-voice-agent.git
cd ai-voice-agent
```

### 2. Configure credentials

```bash
# Copy templates and fill in your values
cp xiaozhi-esp32/main/secrets.h.example xiaozhi-esp32/main/secrets.h
nano xiaozhi-esp32/main/secrets.h

cp device_map.json.example device_map.json
nano device_map.json   # map your ESP32 MAC → firmware filename

cp config.example.json nanobot/data/config.json
nano nanobot/data/config.json   # Telegram, OpenRouter, Home Assistant keys
```

> `secrets.h`, `device_map.json` and `config.json` are gitignored — they contain your private credentials.

### 3. Build firmware

```bash
cd xiaozhi-esp32
# Install ESP-IDF 5.x first: https://docs.espressif.com/projects/esp-idf/en/latest/
source /path/to/esp-idf/export.sh

# Build for your board (set in secrets.h: BOARD_XINGZHI or BOARD_FREENOVE)
idf.py build flash monitor
```

Or use the multi-target build script (builds all boards + deploys to OTA server):

```bash
# Set environment vars first
export OTA_SERVER=user@192.168.x.x
export OTA_SERVER_URL=http://192.168.x.x:18791

./build_all.sh
```

### 4. Start services

```bash
# OTA server (serves firmware updates to ESP32 devices)
python3 ota_server.py

# Voice gateway (Nanobot with voice channel)
cd nanobot
docker compose up -d
```

---

## 🔧 Configuration Files

| File | Purpose | Public? |
|---|---|---|
| `xiaozhi-esp32/main/secrets.h` | Wi-Fi SSID/pass, WebSocket URL/token | 🔒 gitignored |
| `xiaozhi-esp32/main/secrets.h.example` | Template for secrets.h | ✅ |
| `device_map.json` | MAC address → firmware mapping | 🔒 gitignored |
| `device_map.json.example` | Template for device_map.json | ✅ |
| `nanobot/data/config.json` | Nanobot agent config (all API keys) | 🔒 gitignored |
| `config.example.json` | Full template for Nanobot config | ✅ |

---

## 🏠 Home Assistant Integration

The Nanobot agent supports Home Assistant via MCP (Model Context Protocol):

```json
{
  "mcpServers": {
    "homeassistant": {
      "type": "streamableHttp",
      "url": "http://your-ha-ip:8123/api/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_LONG_LIVED_TOKEN"
      }
    }
  }
}
```

> Use `streamableHttp` transport type — `sse` returns 405.

---

## 🚀 OTA Updates

The OTA server routes firmware by MAC address:

```json
// device_map.json
{
  "aa:bb:cc:dd:ee:ff": "xiaozhi_freenove.bin",
  "11:22:33:44:55:66": "xiaozhi_xingzhi.bin"
}
```

```bash
# Set OTA server URL via environment variable
export OTA_SERVER_URL=http://192.168.x.x:18791
python3 ota_server.py
```

Unknown MAC addresses are rejected with `403 Forbidden`.

---

## 🧠 Known Issues & Tips

| Issue | Fix |
|---|---|
| Wake word stops working after 1st use | Fixed in `application.cc` — `SetDeviceState` moved before channel check |
| ESP32 speaker cuts out at high volume | Cap volume at 80–85% to avoid current spike |
| OLED colors inverted (white background) | `esp_lcd_panel_invert_color(panel_, true)` in board init |
| Build hangs at link step (low RAM) | `export CMAKE_BUILD_PARALLEL_LEVEL=2` in build script |
| Slow LLM responses (55+ sec) | Switch model or use local Ollama instead of cloud |

---

## 📄 License

This project orchestrates several open-source projects. Each submodule retains its own license.
Custom code in this repository is released under the **MIT License**.
