# Py-dex: A Python CLI Learning Adventure 🎮

[![Py-dex Demo Video](https://img.shields.io/badge/Watch%20Demo-YouTube-red?logo=youtube&logoColor=white)](https://www.youtube.com/watch?v=1PB_8IISfD4)

A terminal-based educational game that teaches Python programming through an interactive RPG-style experience. Players navigate through levels, solve coding challenges, and learn Python concepts in an engaging way.

![Python](https://img.shields.io/badge/Python-3.7+-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

## 📝 Table of Contents
- [Features](#-features)
- [Educational Content](#-educational-content)
- [Requirements](#-requirements)
- [Installation](#-installation)
- [How to Play](#-how-to-play)
- [Advanced Features](#-advanced-features)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)
- [Credits](#-credits)
- [Updates & Maintenance](#-updates--maintenance)

## 🌟 Features
- Interactive terminal-based gameplay with colorful UI
- Multiple levels with increasing difficulty
- Built-in code editor with syntax highlighting
- Real-time code execution and validation
- Progress tracking and level selection
- Background music system with battle themes
- AI-powered level generation using Groq API
- Save/load game progress
- Cheat codes for testing (Ctrl+P)

## 🎯 Educational Content
The game covers Python programming concepts including:
- Variables and data types
- Basic operations
- Strings and string manipulation
- Lists, tuples, and dictionaries
- Functions and control flow
- And more advanced topics in higher levels

## 🔧 Requirements
```
python 3.7+
pygame==2.6.1
pydub==0.25.1
groq
curses (built-in with Python on Unix systems)
```

## 📦 Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Gardo32/py-dex.git
   cd py-dex
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create required music directories:
   ```bash
   mkdir -p music/battle_mp3
   ```

4. (Optional) Add background music:
   - Place main theme MP3 in music folder as "Chill & Relaxing Pokémon Music Mix.mp3"
   - Place battle music MP3s in battle_mp3 folder

## 🎮 How to Play
1. Start the game:
   ```bash
   python main.py
   ```

2. Game Controls:
   | Action | Key |
   |--------|-----|
   | Movement | Arrow keys or WASD |
   | Interact/Break bush | F |
   | Quit | Q |
   | Restart | R |
   | Toggle Music | M |
   | Level Select | Ctrl+Q |
   | Cheat Menu | Ctrl+P |

3. Gameplay:
   - Navigate through the maze-like levels
   - Encounter numbered bushes (1-5) containing coding challenges
   - Press F near a bush to open the code editor
   - Complete the Python challenge to break the bush
   - Reach the level exit (marked with special characters) to progress

## 🛠️ Advanced Features

### AI Level Generation
1. Select "AI Level Generator" from the main menu
2. Enter your Groq API key when prompted
3. Specify number of levels to generate
4. New levels will be added to the game automatically

### Music System
- Toggle music: M key in main menu
- Different music for exploration and coding challenges
- Supports custom music by adding MP3s to respective folders

### Level Selection
- Access level select menu with Ctrl+Q
- Jump to any previously unlocked level
- Restart from beginning with R

## 🔧 Troubleshooting

### Common Issues:
1. **Curses module not found (Windows):**
   - Install windows-curses: `pip install windows-curses`

2. **Music not playing:**
   - Ensure pygame is installed correctly
   - Check music files exist in correct directories
   - Verify file permissions

3. **Display issues:**
   - Ensure terminal supports colors and Unicode
   - Try resizing terminal window
   - Check terminal encoding settings

## 🤝 Contributing
1. Fork the repository
2. Create your feature branch: `git checkout -b feature/AmazingFeature`
3. Commit your changes: `git commit -m 'Add some AmazingFeature'`
4. Push to the branch: `git push origin feature/AmazingFeature`
5. Open a Pull Request

## 📝 License
This project is open source and available under the MIT License.

## 👏 Credits
- Developer: [Gardo32](https://github.com/Gardo32)
- Music: Add music credits here
- Special thanks to the Python community

## 🔄 Updates & Maintenance
- Check the repository for latest updates
- Bug reports and feature requests welcome in Issues
- Follow the project for notifications about new releases

## 🎥 Demo Video
Check out the gameplay demo:

[![Py-dex Demo](https://img.youtube.com/vi/1PB_8IISfD4/0.jpg)](https://www.youtube.com/watch?v=1PB_8IISfD4)
