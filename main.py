import curses
import random
from curses import wrapper
import importlib.util
import sys
import os

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

def show_menu(stdscr):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    menu_text = [
        "Welcome to the Game!",
        "Press 'S' to Start",
        "Press 'R' to Restart",
        "Press 'Q' to Quit"
    ]
    
    for idx, text in enumerate(menu_text):
        x = w//2 - len(text)//2
        y = h//2 - 2 + idx
        stdscr.addstr(y, x, text)
    
    stdscr.refresh()
    while True:
        key = stdscr.getch()
        if key in [ord('q'), ord('Q')]:
            return 'QUIT'
        elif key in [ord('s'), ord('S')]:
            return 'START'
        elif key in [ord('r'), ord('R')]:
            return 'RESTART'

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
        stdscr.addch(player_y, player_x, '@', curses.color_pair(2) | curses.A_BOLD)
        
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
            
        if (player_y, player_x) in bushes:
            player_y, player_x = old_y, old_x

def load_level(level_number):
    try:
        level_path = f"lvl-{level_number}.py"
        if not os.path.exists(level_path):
            return None
        spec = importlib.util.spec_from_file_location(f"level{level_number}", level_path)
        level = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(level)
        return level.Level
    except Exception as e:
        print(f"Error loading level: {e}")
        return None

def main(stdscr):
    # Initialize colors
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
    
    current_level = 1
    game_state = 'MENU'
    
    while True:
        if game_state == 'MENU':
            action = show_menu(stdscr)
            if action == 'QUIT':
                break
            elif action in ['START', 'RESTART']:
                current_level = 1
                game_state = 'PLAYING'
                continue
        
        if game_state == 'PLAYING':
            level_class = load_level(current_level)
            if not level_class:
                game_state = 'MENU'
                continue
            
            level = level_class(stdscr)
            result = level.run()
            
            if result == 'QUIT':
                break
            elif result == 'NEXT_LEVEL':
                current_level += 1
                continue  # Stay in PLAYING state
            elif result == 'RESTART':
                game_state = 'MENU'  # Go back to menu only on explicit restart

if __name__ == '__main__':
    wrapper(main)