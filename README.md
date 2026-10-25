# 📱 Eagle Phone OS

**In-game smartphone OS for GTA San Andreas with 12 apps — finance, news, map, AI companion.**

A Python sidecar application (6,000+ lines) that reads GTA SA game state via `ReadProcessMemory` and serves a responsive anime-themed smartphone UI through a local web server, displayed in-game via F7 HUD overlay.

## Features

### Phone Core
- **Anime wallpapers** with mascot widget (Furina / Hu Tao / Keqing / Raiden)
- **3×3 app grid** with D-pad navigation (I/K/J/L keys)
- **Dynamic island** showing game time
- **Glassmorphism design** with neon themes
- **Bilingual** EN ↔ VI localization

### 12 Apps

| # | App | Description |
|---|-----|-------------|
| 1 | ❤️ Life & Bank | Life sim bars (Hunger/Energy/Health/Armor), banking with savings interest |
| 2 | 🏛️ Stocks & Commodities | 10 stocks + 6 commodities, real-time charts, trading |
| 3 | 🪙 Crypto Exchange | 8 cryptocurrencies, Bitcoin from \$0.01 (2010), historically accurate |
| 4 | ⚽ Sportsbook | 5 leagues (Champions League/World Cup/EPL/NBA), betting |
| 5 | 🎰 4-in-1 Lottery | Scratch Card, XSKT, Vietlott 6/45, 6-digit lottery |
| 6 | 📰 EagleTimes | 6 news categories, 5,844 days coverage (2010-2025), 1.78MB archive |
| 7 | 💼 Unified Portfolio | Combined view of all financial apps |
| 8 | 🐛 Map Bug Reporter | Auto-Inspector, debug controls, Ctrl+F11 report |
| 9 | ⚙️ Settings | Wallpaper, mascot, themes (Hydro/Purple/Crimson/Gold) |
| 10 | 🗺️ GG Map | 631+ POIs, GPS routing (F9/F10), fast travel |
| 11 | ✨ Paimon Companion | AI companion — free talk, portfolio review, daily news |
| 12 | 📱 TXD Builder | Build UI textures for in-game display |

## Architecture

```
EagleCompanion.py        # Main sidecar (6,011 lines, 302 KB)
├── eagle_phone_ui.py    # Web UI server (121 KB, glassmorphism)
├── eagle_gg_map_pois.py # GG Map POI database (303 KB, 631+ POIs)
└── Web Server           # localhost:8765
    ├── Phone UI          # Responsive smartphone layout
    ├── API endpoints     # /api/action, /api/state, etc.
    └── In-game HUD       # F7 overlay via hud.lua
```

### How It Works
1. **Python sidecar** reads GTA SA memory via Win32 `ReadProcessMemory`
2. **Web server** at `localhost:8765` serves the phone UI
3. **Lua HUD script** (`hud.lua`) renders the F7 overlay and syncs state
4. **Game state** (position, health, money, time) drives all app data

## Requirements

- **Python 3.8+** (stdlib only for core — no pip dependencies)
- **Windows** (uses Win32 API via ctypes)
- **GTA San Andreas 1.0 US** running
- **MoonLoader** (for hud.lua integration)

### Optional
- **Groq API** key for Paimon AI companion (`localhost:18082`)

## Usage

```bash
python EagleCompanion.py
```

Then press **F7** in-game to toggle the phone overlay, or open **http://localhost:8765** in a browser.

## License

MIT License — see [LICENSE](LICENSE).

## Credits

- Built as part of **Project Eagle** by [@nguyenlee97](https://github.com/nguyenlee97)
- Paimon AI companion uses [Groq API](https://groq.com/) for language model inference
- GTA SA memory addresses from documented HOODLUM 1.0 US symbols
- Chronological data (stocks, crypto, sports, news) sourced from historical records
