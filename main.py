import curses
import random
from curses import wrapper
import importlib.util
import sys
import os
import json

def draw_borders(stdscr):
    h, w = stdscr.getmaxyx()
    # Draw horizontal borders (avoid last column)
    for x in range(w-1):
        stdscr.addch(0, x, '_')
        if x < w-2:  # Avoid bottom-right corner
            stdscr.addch(h-1, x, '_')
    # Draw vertical borders (avoid last row)
    for y in range(h-1):
        stdscr.addch(y, 0, '|')
        if y < h-2:  # Avoid bottom-right corner
            stdscr.addch(y, w-2, '|')

def get_available_levels():
    # Check both Python files and question store
    levels = set()
    
    # Check existing level files
    for i in range(1, 10):
        if os.path.exists(f"lvl-{i}.py"):
            levels.add(i)
    
    # Check question store
    try:
        with open('question_store.json', 'r') as f:
            questions = json.load(f)
            for level_key in questions:
                if level_key.startswith('level'):
                    level_num = int(level_key[5:])  # Extract number from 'levelX'
                    levels.add(level_num)
    except Exception:
        pass
        
    return sorted(list(levels))

def show_level_select(stdscr):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    
    # Get available levels using new function
    levels = get_available_levels()
            
    if not levels:
        return None
        
    selected_idx = 0  # Track currently selected level
    title = "Level Select"
    footer = "↑↓: Select | Enter: Choose | ESC: Cancel"
    
    while True:
        stdscr.clear()
        menu_text = [
            title,
            "-" * len(title),
            "",  # Space for levels
            "",
            footer
        ]
        
        # Draw menu
        for idx, text in enumerate(menu_text):
            x = w//2 - len(text)//2
            y = h//2 - len(menu_text)//2 + idx
            if idx < 2:  # Title and separator in different color
                stdscr.addstr(y, x, text, curses.color_pair(3) | curses.A_BOLD)
            elif idx == len(menu_text) - 1:  # Footer
                stdscr.addstr(y, x, text, curses.color_pair(2))
        
        # Draw level options
        base_y = h//2 - len(menu_text)//2 + 2
        for idx, level in enumerate(levels):
            x = w//2 - len(f"Level {level}")//2
            text = f"Level {level}"
            if idx == selected_idx:
                stdscr.addstr(base_y + idx, x, text, curses.A_REVERSE | curses.A_BOLD)
            else:
                stdscr.addstr(base_y + idx, x, text)
        
        stdscr.refresh()
        
        # Handle input
        key = stdscr.getch()
        if key == 27:  # ESC
            return None
        elif key == curses.KEY_UP and selected_idx > 0:
            selected_idx -= 1
        elif key == curses.KEY_DOWN and selected_idx < len(levels) - 1:
            selected_idx += 1
        elif key == 10:  # Enter
            return levels[selected_idx]

def show_menu(stdscr):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    menu_text = [
        "Welcome to the Game!",
        "Use WASD or Arrow Keys to move",
        "Use `F` to Break Bushes",
        "Press 'S' to Start",
        "Press 'Q' to Quit"
    ]
    
    for idx, text in enumerate(menu_text):
        x = w//2 - len(text)//2
        y = h//2 - 2 + idx
        stdscr.addstr(y, x, text, curses.color_pair(8))  # Use black text
    
    stdscr.refresh()
    while True:
        key = stdscr.getch()
        if key in [ord('q'), ord('Q')]:
            return 'QUIT'
        elif key in [ord('s'), ord('S')]:
            return 'START'
        elif key == 16:  # Ctrl+P
            return 'REMOVE_BUSHES'  # Changed from 'SECRET_CREDITS'
        elif key == 17:  # Ctrl+Q
            return 'LEVEL_SELECT'

def game_loop(stdscr):
    # Initialize colors
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    
    # Hide the cursor
    curses.curs_set(0)
    
    # Initialize player position
    h, w = stdscr.getmaxyx()
    player_y, player_x = h//2, w//2
    
    # Adjust bush placement to account for borders
    bushes = []
    for _ in range(20):
        bush_y = random.randint(1, h - 3)
        bush_x = random.randint(1, w - 3)
        bushes.append((bush_y, bush_x))
    
    while True:
        stdscr.clear()
        
        # Draw borders
        draw_borders(stdscr)
        
        # Draw bushes
        for bush_y, bush_x in bushes:
            stdscr.addch(bush_y, bush_x, '*', curses.color_pair(1) | curses.A_BOLD)
        
        # Draw player
        stdscr.addch(player_y, player_x, '@', curses.color_pair(2) | curses.A_BOLD )
        
        # Refresh the screen
        stdscr.refresh()
        
        # Get user input
        key = stdscr.getch()
        
        old_y, old_x = player_y, player_x
        
        # Update player position (with border constraints)
        if key == ord('w') and player_y > 1:
            player_y -= 1
        elif key == ord('s') and player_y < h - 3:  # Adjusted constraint
            player_y += 1
        elif key == ord('a') and player_x > 1:
            player_x -= 1
        elif key == ord('d') and player_x < w - 3:  # Adjusted constraint
            player_x += 1
        elif key == ord('q'):
            return 'QUIT'
        elif key == ord('r'):
            return 'RESTART'
        elif key == 16:  # Ctrl+P - Remove special bushes cheat
            bushes = []  # Clear all special bushes
            
        if (player_y, player_x) in bushes:
            player_y, player_x = old_y, old_x

def load_level(level_number):
    try:
        # Try loading Python file first
        level_path = f"lvl-{level_number}.py"
        if os.path.exists(level_path):
            spec = importlib.util.spec_from_file_location(f"level{level_number}", level_path)
            level = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(level)
            return level.Level
        
        # If no Python file exists but questions exist, use lvl-3 as template
        if level_number > 3:
            with open('question_store.json', 'r') as f:
                questions = json.load(f)
                if f"level{level_number}" in questions:
                    spec = importlib.util.spec_from_file_location("level3", "lvl-3.py")
                    level = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(level)
                    
                    # Create a subclass with the new level number
                    class DynamicLevel(level.Level):
                        def __init__(self, stdscr, player_name="Player"):
                            super().__init__(stdscr, player_name)
                            self.level_number = level_number
                    
                    return DynamicLevel
                    
        return None
    except Exception as e:
        print(f"Error loading level: {e}")
        return None

def show_end_credits(stdscr, player_name):  # Add player_name parameter
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)
    
    # Calculate box width based on player name length
    name_length = len(player_name)
    min_width = 35
    width = max(min_width, name_length + 30)  # Ensure minimum width plus padding
    
    border_top = "╔" + "═" * (width - 2) + "╗"
    border_bottom = "╚" + "═" * (width - 2) + "╝"
    empty_line = "║" + " " * (width - 2) + "║"
    
    # Create centered congratulations message
    congrats_text = f"🌟 CONGRATULATIONS {player_name}! 🌟"
    padding = (width - 2 - len(congrats_text)) // 2
    congrats_line = "║" + " " * padding + congrats_text + " " * (width - 2 - padding - len(congrats_text)) + "║"
    
    # Create centered completion message
    complete_text = "You completed all levels!"
    padding = (width - 2 - len(complete_text)) // 2
    complete_line = "║" + " " * padding + complete_text + " " * (width - 2 - padding - len(complete_text)) + "║"
    
    congratulations = [
        border_top,
        congrats_line,
        complete_line,
        border_bottom
    ]
    
    credits = [
        "Made by:",
        "Github: Gardo32",
        "",
        "Press any key to exit"
    ]
    
    colors = [4, 5, 6, 2, 3]  # Rotating colors
    frame = 0
    
    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        
        # Draw stars in background with boundary checking
        try:
            for i in range(20):
                y = random.randint(1, h-2)  # Avoid borders
                x = random.randint(1, w-2)  # Avoid borders
                try:
                    stdscr.addch(y, x, '*', curses.color_pair(frame % 3 + 4) | curses.A_BOLD)
                except curses.error:
                    continue  # Skip if star can't be placed
            
            # Draw congratulations text with centering and boundary checks
            for idx, line in enumerate(congratulations):
                y = max(1, min(h-2, h//2 - 4 + idx))  # Keep within bounds
                x = max(1, min(w-len(line)-1, w//2 - len(line)//2))
                try:
                    stdscr.addstr(y, x, line, curses.color_pair(frame % 3 + 4) | curses.A_BOLD)
                except curses.error:
                    continue
            
            # Draw credits with boundary checks
            for idx, line in enumerate(credits):
                y = max(1, min(h-2, h//2 + 2 + idx))
                x = max(1, min(w-len(line)-1, w//2 - len(line)//2))
                try:
                    stdscr.addstr(y, x, line, curses.color_pair(colors[frame % len(colors)]) | curses.A_BOLD)
                except curses.error:
                    continue
        except curses.error:
            pass  # Handle any remaining drawing errors
        
        stdscr.refresh()
        frame += 1
        
        # Check for key press with timeout
        stdscr.timeout(100)
        key = stdscr.getch()
        if key != -1:
            break
    
    stdscr.timeout(-1)  # Reset timeout

def get_player_name(stdscr):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    prompt = "Enter your name: "
    stdscr.addstr(h//2, w//2 - len(prompt)//2, prompt, curses.color_pair(8))  # Black text
    curses.echo()  # Show typing
    curses.curs_set(1)  # Show cursor
    name = ""
    while True:
        try:
            y = h//2
            x = w//2 - len(prompt)//2 + len(prompt)
            stdscr.addstr(y, x, " " * 20)  # Clear previous name
            stdscr.addstr(y, x, name)
            char = stdscr.getch()
            if char == ord('\n'):
                break
            elif char == ord('\b') or char == 127:  # Backspace
                name = name[:-1]
            elif len(name) < 20:  # Limit name length
                name += chr(char)
        except curses.error:
            pass
    
    curses.noecho()
    curses.curs_set(0)
    return name.strip()

def main(stdscr):
    # Initialize Pokémon-style colors
    curses.start_color()
    curses.use_default_colors()  # Enable default terminal colors
    
    # Theme colors
    BEIGE = 230  # Page color
    BROWN = 94   # Wall color
    
    # Initialize color pairs
    curses.init_pair(1, curses.COLOR_GREEN, BEIGE)     # Bush color
    curses.init_pair(2, curses.COLOR_YELLOW, BEIGE)    # Player color
    curses.init_pair(3, curses.COLOR_RED, BEIGE)       # Important elements
    curses.init_pair(4, curses.COLOR_WHITE, BEIGE)     # Path/text
    curses.init_pair(5, curses.COLOR_MAGENTA, BEIGE)   # Special effects
    curses.init_pair(6, curses.COLOR_BLUE, BEIGE)      # Water/special areas
    curses.init_pair(7, BROWN, BEIGE)                  # Walls
    curses.init_pair(8, curses.COLOR_BLACK, BEIGE)     # Regular text
    
    # Set background color
    stdscr.bkgd(' ', curses.color_pair(4))
    
    current_level = 1
    game_state = 'MENU'
    player_name = ""
    level = None  # Keep track of current level instance
    
    while True:
        if game_state == 'MENU':
            action = show_menu(stdscr)
            if action == 'QUIT':
                break
            elif action == 'START':
                player_name = get_player_name(stdscr)
                if not player_name:
                    player_name = "Player"
                current_level = 1
                game_state = 'PLAYING'
                continue
            elif action == 'REMOVE_BUSHES':
                if level:  # If level exists, remove all blocking bushes
                    level.blocking_bushes = []
                continue
            elif action == 'LEVEL_SELECT':
                selected_level = show_level_select(stdscr)
                if selected_level:
                    if not player_name:
                        player_name = get_player_name(stdscr)
                        if not player_name:
                            player_name = "Player"
                    current_level = selected_level
                    game_state = 'PLAYING'
                continue
        
        if game_state == 'PLAYING':
            level_class = load_level(current_level)
            if not level_class:
                show_end_credits(stdscr, player_name)
                break
            
            level = level_class(stdscr, player_name)
            while True:
                result = level.run()
                if result == 'QUIT':
                    game_state = 'MENU'
                    break
                elif result == 'NEXT_LEVEL':
                    current_level += 1
                    break
                elif result == 'RESTART':
                    game_state = 'MENU'
                    break
                elif result == 'REMOVE_BUSHES':  # Handle bush removal
                    level.blocking_bushes = []

if __name__ == '__main__':
    wrapper(main)