import curses
import random

class Level:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.init_colors()
        curses.curs_set(0)
        self.h, self.w = stdscr.getmaxyx()
        self.player_y, self.player_x = self.h//2, self.w//2
        self.entrance_y = 1
        self.entrance_x = self.w - 10  # Move entrance more to the left
        self.entrance_width = 3
        self.bushes = self.create_bushes()
        self.level_number = 1  # Add level number

    def init_colors(self):
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Bush
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Player
        curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)  # Entrance

    def create_bushes(self):
        bushes = []
        for _ in range(20):
            bush_y = random.randint(1, self.h - 3)
            bush_x = random.randint(1, self.w - 3)
            # Avoid placing bushes in the entrance area
            if not (bush_y == self.entrance_y and 
                   self.entrance_x <= bush_x <= self.entrance_x + self.entrance_width):
                bushes.append((bush_y, bush_x))
        return bushes

    def draw_borders(self):
        h, w = self.stdscr.getmaxyx()
        # Draw horizontal borders (avoid last column)
        for x in range(w-1):
            self.stdscr.addch(0, x, '_')
            if x < w-2:  # Avoid bottom-right corner
                self.stdscr.addch(h-1, x, '_')
        # Draw vertical borders (avoid last row)
        for y in range(h-1):
            self.stdscr.addch(y, 0, '|')
            if y < h-2:  # Avoid bottom-right corner
                self.stdscr.addch(y, w-2, '|')

    def draw_entrance(self):
        try:
            # Draw the entrance frame
            self.stdscr.addstr(self.entrance_y, self.entrance_x - 4, "____", curses.color_pair(3))
            self.stdscr.addstr(self.entrance_y, self.entrance_x + self.entrance_width, "____", curses.color_pair(3))
            
            # Draw the vertical bars
            self.stdscr.addch(self.entrance_y + 1, self.entrance_x - 1, '|', curses.color_pair(3))
            self.stdscr.addch(self.entrance_y + 1, self.entrance_x + self.entrance_width, '|', curses.color_pair(3))
            
            # Clear the entrance space
            for x in range(self.entrance_width):
                self.stdscr.addch(self.entrance_y, self.entrance_x + x, ' ', curses.color_pair(3))
        except curses.error:
            pass  # Safely handle any drawing errors

    def run(self):
        while True:
            try:
                self.stdscr.clear()
                self.draw_borders()
                
                # Draw level number in top-left corner
                self.stdscr.addstr(1, 2, f"Level {self.level_number}", 
                                curses.color_pair(2) | curses.A_BOLD)
                
                self.draw_entrance()  # Draw entrance before other elements
                
                # Draw bushes
                for bush_y, bush_x in self.bushes:
                    self.stdscr.addch(bush_y, bush_x, '*', 
                                    curses.color_pair(1) | curses.A_BOLD)
                
                # Draw player
                self.stdscr.addch(self.player_y, self.player_x, '@', 
                                curses.color_pair(2) | curses.A_BOLD)
                
                # Move level completion check before refresh
                if (self.player_y == self.entrance_y + 1 and 
                    self.entrance_x <= self.player_x <= self.entrance_x + self.entrance_width):
                    return 'NEXT_LEVEL'
                    
                self.stdscr.refresh()
                
                # Handle movement
                key = self.stdscr.getch()
                old_y, old_x = self.player_y, self.player_x
                
                # Update movement controls to include arrows
                if (key == ord('w') or key == curses.KEY_UP) and self.player_y > 1:
                    self.player_y -= 1
                elif (key == ord('s') or key == curses.KEY_DOWN) and self.player_y < self.h - 3:
                    self.player_y += 1
                elif (key == ord('a') or key == curses.KEY_LEFT) and self.player_x > 1:
                    self.player_x -= 1
                elif (key == ord('d') or key == curses.KEY_RIGHT) and self.player_x < self.w - 3:
                    self.player_x += 1
                elif key == ord('q'):
                    return 'QUIT'
                elif key == ord('r'):
                    return 'RESTART'
                    
                # Check for collisions
                if (self.player_y, self.player_x) in self.bushes:
                    self.player_y, self.player_x = old_y, old_x
                    
            except curses.error:
                continue

# ...existing code...
