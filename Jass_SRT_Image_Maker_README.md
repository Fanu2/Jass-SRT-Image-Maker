# Jass SRT Image Maker

**Version 1.0.1**

A standalone PySide6 desktop application for turning `.srt` subtitle files into beautiful, colourful PNG image cards.

## Features

### SRT
- 📂 Select and load SRT files
- UTF-8 / Unicode text support
- Hindi, Punjabi and English text
- Subtitle list and text editing
- Save edited SRT

### Design Presets
- ❤️ Romantic Rose
- 🌹 Rose Garden
- 🌅 Golden Sunset
- 🌌 Midnight Love
- 💜 Purple Dream
- ✨ Stardust
- 💎 Elegant Gold
- 🔥 Passion
- 🌸 Soft Blossom
- 🎬 Cinematic

### Visual Styling
- Three-colour gradient backgrounds
- Soft light pools and atmospheric effects
- Gradient typography
- Font selection
- Font size
- Bold / italic
- Text outline
- Shadow
- Glow
- Top / Center / Bottom positioning
- Translucent rounded text card
- Adjustable card opacity and padding

### Decorations
- Hearts
- Flowers
- Stars
- Sparkles
- Sunset effects
- Gold accents
- Minimal mode
- Adjustable decoration strength

### Canvas
- 1080 × 1920 Portrait — Shorts / Reels
- 1920 × 1080 Landscape — YouTube
- 1080 × 1080 Square
- 1200 × 1500 Portrait
- Custom dimensions

### Rendering
- Render current subtitle to PNG
- Render complete SRT to numbered PNG files
- High-resolution output
- Suitable for video editors and FFmpeg

Example:

```text
001.png
002.png
003.png
004.png
...
```

## Interface

```text
┌──────────────────────────────────────────────────────────────┐
│                 JASS SRT IMAGE MAKER                        │
│ 📂 SELECT SRT FILE   💾 Save SRT   Render Current   Render All│
├───────────────┬──────────────────────────┬───────────────────┤
│   SUBTITLES   │      LIVE PREVIEW        │      DESIGN       │
│               │                          │                   │
│ 01  Text...   │       IMAGE CARD        │ Presets           │
│ 02  Text...   │                          │ Canvas            │
│ 03  Text...   │                          │ Text Style        │
│               │                          │ Colour            │
│ Edit Text     │                          │ Decoration        │
└───────────────┴──────────────────────────┴───────────────────┘
```

## Requirements

- Python 3.10+ recommended
- PySide6

### Windows

```powershell
py -m pip install PySide6
```

### Linux

```bash
python3 -m pip install PySide6
```

## Run

From the application folder:

```powershell
py jass_srt_image_maker.py
```

or:

```powershell
python jass_srt_image_maker.py
```

## Basic Workflow

1. Start the application.
2. Click **📂 SELECT SRT FILE**.
3. Choose an `.srt` file.
4. Select a subtitle entry.
5. Choose a design preset.
6. Adjust text, colours and decorations.
7. Check the live preview.
8. Use **Render Current** or **Render All**.

## Recommended Romantic Workflow

For romantic videos, start with:

- Romantic Rose
- Midnight Love
- Soft Blossom
- Elegant Gold
- Cinematic

Use **1080 × 1920 Portrait** for YouTube Shorts and Reels.

## Example SRT

```srt
1
00:00:00,000 --> 00:00:05,000
मोनी... 🖤✨

2
00:00:05,000 --> 00:00:10,000
बस तेरा नाम लेता हूँ,
और मेरा दिल धड़कना भूल जाता है। 💓
```

Each subtitle entry can become an individual visual card.

## Multilingual Text

Unicode text is supported, for example:

```text
Hindi:
मोनी... तुम्हारा नाम मेरे दिल में बसता है।

Punjabi:
ਜੱਸੀ... ਤੇਰਾ ਨਾਮ ਮੇਰੇ ਦਿਲ ਵਿੱਚ ਵੱਸਦਾ ਹੈ।

English:
Jassi, you are always in my heart.
```

Choose an installed font that supports the required script.

## Project Structure

```text
Jass_SRT_Image_Maker/
│
├── jass_srt_image_maker.py
├── sample_romantic.srt
└── README.md
```

The built-in designs require no external image assets.

## Relationship to Jass Subtitle Studio

This is a **separate companion application** and should not modify the stable **Jass Subtitle Studio v1.2 Simple Pro**.

```text
Jass Subtitle Studio
    → subtitle editing / video subtitle workflow

Jass SRT Image Maker
    → SRT → beautiful visual image cards
```

Keeping them separate allows the image maker to evolve without disturbing the stable subtitle studio.

## Roadmap

### v1.1
- Drag-and-drop text positioning
- Multiple text layers
- Photo backgrounds
- Background blur
- Image cropping
- Frames and borders
- More typography controls
- More templates

### v1.2
- Animated effects
- Slow zoom / Ken Burns
- Fade transitions
- Particle animation
- Per-card design overrides
- Random design generator

### v2.x
- Direct SRT → video
- FFmpeg integration
- Music/audio support
- Automatic timing from SRT
- Shorts/Reels video generation
- Project save/load
- Custom template designer

## Design Philosophy

> **Turn words into beautiful visual moments.**

The application is intended to be fast and visual rather than becoming another complicated video editor.

## Version

**Jass SRT Image Maker v1.0.1**

Current focus:

**SRT → Beautiful PNG Cards**
