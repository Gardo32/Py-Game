import curses
import random

class Level:
    def __init__(self, stdscr, player_name="Player"):
        self.stdscr = stdscr
        self.init_colors()
        curses.curs_set(0)
        self.h, self.w = stdscr.getmaxyx()
        self.player_y = self.h - 4  # Set player start position inside maze
        self.player_x = 4  # A few spaces from left wall
        self.entrance_y = self.h // 2  # Middle vertical position
        self.entrance_x = self.w // 2  # Middle horizontal position
        self.entrance_width = 3
        self.level_number = 2
        self.path_tiles = set()  # Path tiles
        self.wall_tiles = set()  # Wall tiles
        self.generate_path()
        self.bushes = self.create_bushes()
        self.blocking_bushes = self.place_blocking_bushes()
        self.player_name = player_name
        self.bush_questions = {
            "Print Hello World": "print('HW')",
            "Calculate 2+2 and print result": "print(4)",
        }
        self.bush_count = 0  # Track which bush is being broken

    def init_colors(self):
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)

    def create_bushes(self):
        bushes = []
        for _ in range(20):
            bush_y = random.randint(1, self.h - 3)
            bush_x = random.randint(1, self.w - 3)
            pos = (bush_y, bush_x)
            if (pos not in self.path_tiles and 
                pos not in self.wall_tiles):
                bushes.append(pos)
        return bushes

    def generate_path(self):
        self.path_tiles.clear()
        self.wall_tiles.clear()
        
        # Starting area (where player spawns)
        current_y = self.h - 4
        current_x = 4
        
        # Add spawn area to path
        self.path_tiles.add((current_y, current_x))
        
        # First corridor right
        while current_x < self.w - 8:
            self.path_tiles.add((current_y, current_x))
            current_x += 1
            
        # Go up along right side
        while current_y > self.h//3:
            self.path_tiles.add((current_y, current_x))
            current_y -= 1
            
        # Go left (U-turn)
        while current_x > self.entrance_x:
            self.path_tiles.add((current_y, current_x))
            current_x -= 1
            
        # Turn down towards entrance
        while current_y < self.entrance_y + 1:
            self.path_tiles.add((current_y, current_x))
            current_y += 1
            
        # Add final position
        self.path_tiles.add((current_y, current_x))
        
        # Generate walls and ensure spawn point is clear
        self.generate_walls()
        self.wall_tiles.discard((self.player_y, self.player_x))
        self.path_tiles.add((self.player_y, self.player_x))

    def add_side_paths(self):
        # Add some dead ends and alternative paths
        for _ in range(3):
            start_points = list(self.path_tiles)
            if start_points:
                start = random.choice(start_points)
                current_y, current_x = start
                length = random.randint(3, 6)
                direction = random.choice([(0,1), (0,-1), (1,0), (-1,0)])
                
                for _ in range(length):
                    new_y = current_y + direction[0]
                    new_x = current_x + direction[1]
                    if 2 < new_y < self.h-3 and 2 < new_x < self.w-3:
                        self.path_tiles.add((new_y, new_x))
                        current_y, current_x = new_y, new_x

    def generate_walls(self):
        # Generate walls around all paths
        for y, x in list(self.path_tiles):
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    wall_pos = (y+dy, x+dx)
                    # Don't add walls near the entrance
                    if (wall_pos not in self.path_tiles and
                        not (self.entrance_y <= wall_pos[0] <= self.entrance_y + 1 and
                             self.entrance_x - 1 <= wall_pos[1] <= self.entrance_x + self.entrance_width + 1)):
                        self.wall_tiles.add(wall_pos)
        
        # Make sure entrance area is clear
        entrance_area = [(y, x) 
                        for y in range(self.entrance_y, self.entrance_y + 2)
                        for x in range(self.entrance_x - 1, self.entrance_x + self.entrance_width + 1)]
        for pos in entrance_area:
            self.wall_tiles.discard(pos)

    def manhattan_distance(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def is_valid_bush_position(self, pos, existing_bushes, min_distance=4):
        # Check distance from entrance
        if abs(pos[0] - self.entrance_y) <= 2 and abs(pos[1] - self.entrance_x) <= 2:
            return False
            
        # Check distance from other bushes (must be at least min_distance away)
        for bush in existing_bushes:
            if self.manhattan_distance(pos, bush["pos"]) < min_distance:
                return False
                
        return True

    def place_blocking_bushes(self):
        blocking_bushes = []
        # Get path points excluding spawn area
        path_points = [(y, x) for y, x in self.path_tiles 
                      if self.manhattan_distance((y, x), (self.player_y, self.player_x)) > 4]
        
        # Sort path points by distance from start
        path_points.sort(key=lambda pos: self.manhattan_distance(pos, (self.player_y, self.player_x)))
        
        # Try to place bushes ensuring minimum random distance
        bush_number = 1
        for pos in path_points:
            min_distance = random.randint(10, 20)  # Random minimum distance between 10-20 blocks
            if self.is_valid_bush_position(pos, blocking_bushes, min_distance):
                blocking_bushes.append({"pos": pos, "number": bush_number})
                bush_number += 1
                if bush_number > 5:  # Stop after placing 5 bushes
                    break
                    
        return blocking_bushes

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
            # Clear entrance area first
            for y in range(self.entrance_y, self.entrance_y + 2):
                for x in range(self.entrance_x - 1, self.entrance_x + self.entrance_width + 1):
                    self.stdscr.addch(y, x, ' ')
            
            # Draw entrance frame
            self.stdscr.addstr(self.entrance_y, self.entrance_x - 4, "____", curses.color_pair(3))
            self.stdscr.addstr(self.entrance_y, self.entrance_x + self.entrance_width, "____", curses.color_pair(3))
            self.stdscr.addch(self.entrance_y + 1, self.entrance_x - 1, '|', curses.color_pair(3))
            self.stdscr.addch(self.entrance_y + 1, self.entrance_x + self.entrance_width, '|', curses.color_pair(3))
        except curses.error:
            pass

    def try_break_bush(self, pos):
        from editor import Editor
        # Find the bush number for this position
        for bush in self.blocking_bushes:
            if bush["pos"] == pos:
                bush_id = f"bush{bush['number']}"
                editor = Editor(self.stdscr, 2, bush_id)  # Level 2
                return editor.run()
        return False

    def run(self):
        while True:
            try:
                self.stdscr.clear()
                self.draw_borders()
                
                # Draw walls first
                for y, x in self.wall_tiles:
                    if 0 < y < self.h-1 and 0 < x < self.w-1:
                        self.stdscr.addch(y, x, '#', curses.color_pair(3) | curses.A_BOLD)
                
                # Draw level number and player name in top-left corner
                self.stdscr.addstr(1, 2, f"Level {self.level_number} - {self.player_name}", 
                                curses.color_pair(2) | curses.A_BOLD)
                
                self.draw_entrance()
                
                # Draw regular bushes
                for bush_y, bush_x in self.bushes:
                    self.stdscr.addch(bush_y, bush_x, '*', 
                                    curses.color_pair(1) | curses.A_BOLD)
                
                # Draw numbered blocking bushes
                for bush in self.blocking_bushes:
                    y, x = bush["pos"]
                    self.stdscr.addch(y, x, str(bush["number"])[0], 
                                    curses.color_pair(1) | curses.A_BOLD)
                
                # Draw player with ♣ symbol
                self.stdscr.addch(self.player_y, self.player_x, '♣', 
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
                        bush_pos = bush["pos"]  # Extract the position tuple from the dictionary
                        if abs(bush_pos[0] - pos[0]) <= 1 and abs(bush_pos[1] - pos[1]) <= 1:
                            if self.try_break_bush(bush_pos):
                                self.blocking_bushes.remove(bush)  # Remove the whole bush dictionary
                elif key == ord('q'):
                    return 'QUIT'
                
                # Check collisions in this order:
                new_pos = (self.player_y, self.player_x)
                
                # 1. Wall collision
                if new_pos in self.wall_tiles:
                    self.player_y, self.player_x = old_y, old_x
                
                # 2. Regular bush collision (can walk through)
                if new_pos in self.bushes:
                    self.bushes.remove(new_pos)  # Remove bush when walking through
                
                # 3. Blocking bush collision (must destroy first)
                blocking_positions = [b["pos"] for b in self.blocking_bushes]  # Get positions from dictionary
                if new_pos in blocking_positions:
                    self.player_y, self.player_x = old_y, old_x  # Can't walk through
                
                # Level completion check
                if (self.player_y == self.entrance_y + 1 and 
                    self.entrance_x <= self.player_x <= self.entrance_x + self.entrance_width):
                    return 'NEXT_LEVEL'
                
                self.stdscr.refresh()
                    
            except curses.error:
                continue
