
This simple program will allow you to paste your screenshot directly onto your desktop wallpaper.

# Stickerwind – Sticker Editor for Your Desktop Wallpaper

*Stickerwind* is a lightweight cross-platform GUI application that lets you add, drag, resize, and layer multiple stickers (PNG images with transparency) directly onto your desktop wallpaper. 
Supports **Linux (GNOME)** and **Windows** – the result becomes your new wallpaper, and all stickers are saved between sessions.


# Features

- ✅ Add unlimited PNG stickers (keeps original quality)
- 🖱️ Drag & drop stickers anywhere on the wallpaper preview
- 📏 Real‑time resize by dragging corner handles
- 📚 Layer ordering (move up/down)
- 💾 All stickers and their positions are saved automatically (restore after reboot)
- 🌍 Multi‑language interface (Russian / English) – switch in Settings
- 🧩 Works with your current wallpaper or any custom background
- 🚀 Applies the result as system wallpaper (GNOME on Linux, any Windows version)

# Download

- **Windows** – `Stickerwind.exe` (no Python required)
- **Linux** – `Stickerwind` executable (build from source, see below)

# Build from Source

### Requirements
- Python 3.8+
- `pip` and `venv`

### Linux & Windows (run directly)
```bash
git clone https://github.com/graygoopunk/Stickerwind.git
cd stickerwind
pip install pillow
python stickerwind.py
