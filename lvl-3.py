import curses
import random

class Level:
    def __init__(self, stdscr, player_name="Player"):
        self.stdscr = stdscr
        self.init_colors()
        curses.curs_set(0)
        self.h, self.w = stdscr.getmaxyx()
        self.player_y = self.h - 4  # Set player start position
        self.player_x = 4
        
        # Place entrance on right side
        self.entrance_y = random.randint(2, self.h - 4)
        self.entrance_x = self.w - 10  # Fixed x position on right side
        self.entrance_width = 3
        self.level_number = 3
        self.path_tiles = set()
        self.wall_tiles = set()
        self.generate_path()  # Generate the path first
        self.bushes = self.create_bushes()
        self.blocking_bushes = self.place_blocking_bushes()
        self.player_name = player_name
        self.bush_count = 0  # Track which bush is being broken

    def init_colors(self):
        curses.start_color()
        curses.use_default_colors()
        
        # Theme colors
        BEIGE = 230  # Page color
        BROWN = 94   # Wall color
        
        # Initialize color pairs
        curses.init_pair(1, curses.COLOR_GREEN, BEIGE)     # Bush color
        curses.init_pair(2, curses.COLOR_BLACK, BEIGE)     # Player color (changed to black)
        curses.init_pair(3, curses.COLOR_RED, BEIGE)       # Important elements
        curses.init_pair(4, curses.COLOR_WHITE, BEIGE)     # Path/text
        curses.init_pair(5, curses.COLOR_MAGENTA, BEIGE)   # Special effects
        curses.init_pair(6, curses.COLOR_BLUE, BEIGE)      # Water/special areas
        curses.init_pair(7, BROWN, BEIGE)                  # Walls
        curses.init_pair(8, curses.COLOR_BLACK, BEIGE)     # Regular text
        
        # Set background color
        self.stdscr.bkgd(' ', curses.color_pair(4))

    def manhattan_distance(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def is_valid_bush_position(self, pos, existing_bushes, min_distance=4):
        # Only check distance from other bushes, since we already filtered path points
        for bush in existing_bushes:
            if self.manhattan_distance(pos, bush["pos"]) < min_distance:
                return False
        return True

    def place_blocking_bushes(self):
        blocking_bushes = []
        # Get path points excluding spawn area and entrance
        path_points = [(y, x) for y, x in self.path_tiles 
                      if self.manhattan_distance((y, x), (self.player_y, self.player_x)) > 4 and
                      not (abs(y - self.entrance_y) <= 2 and abs(x - self.entrance_x) <= 2)]
        
        # Sort path points by distance from start
        path_points.sort(key=lambda pos: self.manhattan_distance(pos, (self.player_y, self.player_x)))
        
        # Try to place bushes ensuring minimum random distance
        bush_number = 1
        for pos in path_points:
            min_distance = random.randint(10, 20)
            if self.is_valid_bush_position(pos, blocking_bushes, min_distance):
                blocking_bushes.append({"pos": pos, "number": bush_number})
                bush_number += 1
                if bush_number > 5:  # Stop after placing 5 bushes
                    break
                    
        return blocking_bushes

    def create_bushes(self):
        bushes = []
        for _ in range(20):
            bush_y = random.randint(1, self.h - 3)
            bush_x = random.randint(1, self.w - 3)
            pos = (bush_y, bush_x)
            if not (bush_y == self.entrance_y and 
                   self.entrance_x <= bush_x <= self.entrance_x + self.entrance_width):
                bushes.append(pos)
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
        try:
            # Draw entrance frame
            self.stdscr.addstr(self.entrance_y, self.entrance_x - 4, "____", curses.color_pair(3))
            self.stdscr.addstr(self.entrance_y, self.entrance_x + self.entrance_width, "____", curses.color_pair(3))
            self.stdscr.addch(self.entrance_y + 1, self.entrance_x - 1, '|', curses.color_pair(3))
            self.stdscr.addch(self.entrance_y + 1, self.entrance_x + self.entrance_width, '|', curses.color_pair(3))
            
            # Clear entrance space
            for x in range(self.entrance_width):
                self.stdscr.addch(self.entrance_y, self.entrance_x + x, ' ', curses.color_pair(3))
        except curses.error:
            pass

    def try_break_bush(self, pos):
        from editor import Editor
        # Find the bush number for this position
        for bush in self.blocking_bushes:
            if bush["pos"] == pos:
                bush_id = f"bush{bush['number']}"
                editor = Editor(self.stdscr, self.level_number, bush_id)  # Use self.level_number instead of hardcoded 3
                return editor.run()
        return False

    def generate_path(self):
        self.path_tiles.clear()
        self.wall_tiles.clear()
        
        current_y = self.player_y
        current_x = self.player_x
        target_y = self.entrance_y + 1  # Target is one below entrance
        target_x = self.entrance_x
        
        # Add starting position
        self.path_tiles.add((current_y, current_x))
        
        # Generate path with 90-degree turns
        while (current_y, current_x) != (target_y, target_x):
            # Decide movement direction (vertical or horizontal)
            if random.choice([True, False]) and current_y != target_y:
                # Move vertically
                step = 1 if target_y > current_y else -1
                while current_y != target_y:
                    current_y += step
                    self.path_tiles.add((current_y, current_x))
                    # Random chance to stop and make a turn
                    if random.random() < 0.3 and current_y != target_y:
                        break
            elif current_x != target_x:
                # Move horizontally
                step = 1 if target_x > current_x else -1
                while current_x != target_x:
                    current_x += step
                    self.path_tiles.add((current_y, current_x))
                    # Random chance to stop and make a turn
                    if random.random() < 0.3 and current_x != target_x:
                        break
        
        # Ensure the entrance position is in the path
        self.path_tiles.add((target_y, target_x))
        
        # Generate walls around path
        for y, x in list(self.path_tiles):
            for dy, dx in [(-1,0), (1,0), (0,-1), (0,1)]:
                wall_pos = (y+dy, x+dx)
                if wall_pos not in self.path_tiles:
                    self.wall_tiles.add(wall_pos)
        
        # Clear walls around entrance
        entrance_area = [(y, x) 
                        for y in range(self.entrance_y, self.entrance_y + 2)
                        for x in range(self.entrance_x - 1, self.entrance_x + self.entrance_width + 1)]
        for pos in entrance_area:
            self.wall_tiles.discard(pos)
            if pos[0] == self.entrance_y + 1:  # Add floor tiles at entrance
                self.path_tiles.add(pos)

    def run(self):
        while True:
            try:
                self.stdscr.clear()
                self.draw_borders()
                
                # Update text color for level info
                self.stdscr.addstr(1, 2, f"Level {self.level_number} - {self.player_name}", 
                                curses.color_pair(8) | curses.A_BOLD)
                
                # Draw walls with brown color
                for y, x in self.wall_tiles:
                    if 0 < y < self.h-1 and 0 < x < self.w-1:
                        self.stdscr.addch(y, x, '#', curses.color_pair(7) | curses.A_BOLD)
                
                # Draw path tiles
                for y, x in self.path_tiles:
                    if 0 < y < self.h-1 and 0 < x < self.w-1:
                        self.stdscr.addch(y, x, '.', curses.color_pair(4))
                
                self.draw_entrance()
                
                # Draw regular bushes (green)
                for bush_y, bush_x in self.bushes:
                    self.stdscr.addch(bush_y, bush_x, '♣', 
                                    curses.color_pair(1) | curses.A_BOLD)
                
                # Draw numbered blocking bushes with black numbers
                for bush in self.blocking_bushes:
                    y, x = bush["pos"]
                    self.stdscr.addch(y, x, str(bush["number"])[0], 
                                    curses.color_pair(8) | curses.A_BOLD)
                
                # Draw player with black color
                self.stdscr.addch(self.player_y, self.player_x, '☺', 
                                curses.color_pair(2) | curses.A_BOLD)
                
                self.stdscr.refresh()
                
                key = self.stdscr.getch()
                old_y, old_x = self.player_y, self.player_x
                
                if key == 16:  # Ctrl+P
                    self.blocking_bushes = []  # Clear special bushes
                    continue
                
                # Update movement controls
                if (key == ord('w') or key == curses.KEY_UP) and self.player_y > 1:
                    self.player_y -= 1
                elif (key == ord('s') or key == curses.KEY_DOWN) and self.player_y < self.h - 3:
                    self.player_y += 1
                elif (key == ord('a') or key == curses.KEY_LEFT) and self.player_x > 1:
                    self.player_x -= 1
                elif (key == ord('d') or key == curses.KEY_RIGHT) and self.player_x < self.w - 3:
                    self.player_x += 1
                elif key == ord('f'):  # Destroy bush
                    pos = (self.player_y, self.player_x)
                    for bush in list(self.blocking_bushes):
                        bush_pos = bush["pos"]
                        if abs(bush_pos[0] - pos[0]) <= 1 and abs(bush_pos[1] - pos[1]) <= 1:
                            if self.try_break_bush(bush_pos):
                                self.blocking_bushes.remove(bush)
                elif key == ord('q'):
                    return 'QUIT'
                elif key == ord('r'):
                    return 'RESTART'
                
                # Check collisions
                new_pos = (self.player_y, self.player_x)
                if new_pos in [b["pos"] for b in self.blocking_bushes]:
                    self.player_y, self.player_x = old_y, old_x
                
                # Add wall collision check
                if new_pos in self.wall_tiles:
                    self.player_y, self.player_x = old_y, old_x
                
                # Level completion check
                if (self.player_y == self.entrance_y + 1 and 
                    self.entrance_x <= self.player_x <= self.entrance_x + self.entrance_width):
                    return 'NEXT_LEVEL'
                
                self.stdscr.refresh()
                    
            except curses.error:
                continue
