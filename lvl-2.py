import curses
import random

class Level:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.init_colors()
        curses.curs_set(0)
        self.h, self.w = stdscr.getmaxyx()
        self.player_y, self.player_x = self.h-2, 2
        self.entrance_y = 1
        self.entrance_x = self.w - 10
        self.entrance_width = 3
        self.level_number = 2
        self.bushes = self.create_bushes()

    def init_colors(self):
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)

    def create_bushes(self):
        bushes = []
        for _ in range(30):
            bush_y = random.randint(1, self.h - 3)
            bush_x = random.randint(1, self.w - 3)
            bushes.append((bush_y, bush_x))
        return bushes

    def draw_borders(self):
        h, w = self.stdscr.getmaxyx()
        for x in range(w-1):
            self.stdscr.addch(0, x, '_')
            if x < w-2:
                self.stdscr.addch(h-1, x, '_')
        for y in range(h-1):
            self.stdscr.addch(y, 0, '|')
            if y < h-2:
                self.stdscr.addch(y, w-2, '|')

    def draw_entrance(self):
        self.stdscr.addstr(self.entrance_y, self.entrance_x - 4, "____")
        for x in range(self.entrance_width):
            self.stdscr.addch(self.entrance_y, self.entrance_x + x, ' ')
        self.stdscr.addstr(self.entrance_y, self.entrance_x + self.entrance_width, "____")
        self.stdscr.addch(self.entrance_y + 1, self.entrance_x - 1, '|')
        self.stdscr.addch(self.entrance_y + 1, self.entrance_x + self.entrance_width, '|')

    def run(self):
        while True:
            try:
                self.stdscr.clear()
                self.draw_borders()
                
                self.stdscr.addstr(1, 2, f"Level {self.level_number}", 
                                curses.color_pair(2) | curses.A_BOLD)
                
                self.draw_entrance()
                
                for bush_y, bush_x in self.bushes:
                    self.stdscr.addch(bush_y, bush_x, '*', 
                                    curses.color_pair(1) | curses.A_BOLD)
                
                self.stdscr.addch(self.player_y, self.player_x, '@', 
                                curses.color_pair(2) | curses.A_BOLD)
                
                self.stdscr.refresh()
                
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
                
                if (self.player_y, self.player_x) in self.bushes:
                    self.player_y, self.player_x = old_y, old_x
                
                if (self.player_y == self.entrance_y + 1 and 
                    self.entrance_x <= self.player_x <= self.entrance_x + self.entrance_width):
                    return 'NEXT_LEVEL'
                    
            except curses.error:
                continue
