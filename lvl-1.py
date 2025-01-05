import curses
import random

class Level:
    def __init__(self, stdscr, player_name="Player"):
        self.stdscr = stdscr
        self.init_colors()
        curses.curs_set(0)
        self.h, self.w = stdscr.getmaxyx()
        self.player_y, self.player_x = self.h - 2, 2  # Start at bottom left
        self.entrance_y = 1  # Keep entrance at top
        self.entrance_x = self.w - 10
        self.entrance_width = 3
        self.level_number = 1
        self.path_tiles = set()  # Path tiles
        self.wall_tiles = set()  # Wall tiles
        self.generate_path()
        self.bushes = self.create_bushes()
        self.blocking_bushes = self.place_blocking_bushes()
        self.player_name = player_name
        self.bush_questions = {
            "Print 'HW' to break the bush": "print('HW')",
        }
        self.bush_count = 0  # Track which bush is being broken

    def init_colors(self):
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Bush
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Player
        curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)  # Entrance

    def generate_path(self):
        current_y = self.h - 2
        current_x = 2
        
        # First straight up
        target_y = self.h - 8
        while current_y > target_y:
            self.path_tiles.add((current_y, current_x))
            current_y -= 1
            
        # Go right
        target_x = current_x + 10
        while current_x < target_x:
            self.path_tiles.add((current_y, current_x))
            current_x += 1
            
        # Go up again
        target_y = current_y - 6
        while current_y > target_y:
            self.path_tiles.add((current_y, current_x))
            current_y -= 1
            
        # Final approach to entrance
        while current_x < self.entrance_x:
            self.path_tiles.add((current_y, current_x))
            current_x += 1
        while current_y > self.entrance_y + 1:
            self.path_tiles.add((current_y, current_x))
            current_y -= 1
            
        self.path_tiles.add((current_y, current_x))
        
        # Generate walls
        for y, x in list(self.path_tiles):
            if (y, x-1) not in self.path_tiles:
                self.wall_tiles.add((y, x-1))
            if (y, x+1) not in self.path_tiles:
                self.wall_tiles.add((y, x+1))
            if (y-1, x) not in self.path_tiles:
                self.wall_tiles.add((y-1, x))
            if (y+1, x) not in self.path_tiles:
                self.wall_tiles.add((y+1, x))

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
            min_distance = random.randint(10, 20)  # Changed range to 10-20 blocks
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
            if (not (bush_y == self.entrance_y and 
                self.entrance_x <= bush_x <= self.entrance_x + self.entrance_width) and 
                pos not in self.path_tiles and 
                pos not in self.wall_tiles):
                bushes.append(pos)
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

    def try_break_bush(self, pos):
        from editor import Editor
        # Find the bush number for this position
        for bush in self.blocking_bushes:
            if bush["pos"] == pos:
                bush_id = f"bush{bush['number']}"
                editor = Editor(self.stdscr, 1, bush_id)
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
                
                # Draw player
                self.stdscr.addch(self.player_y, self.player_x, '♣', 
                                curses.color_pair(2) | curses.A_BOLD)
                
                # Move level completion check before refresh
                if (self.player_y == self.entrance_y + 1 and 
                    self.entrance_x <= self.player_x <= self.entrance_x + self.entrance_width):
                    return 'NEXT_LEVEL'
                    
                self.stdscr.refresh()
                
                # Handle movement
                key = self.stdscr.getch()
                
                if key == 16:  # Ctrl+P
                    self.blocking_bushes = []  # Clear special bushes
                    continue
                
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
                    
                # Check for collisions
                new_pos = (self.player_y, self.player_x)
                if new_pos in self.wall_tiles or new_pos in [b["pos"] for b in self.blocking_bushes]:
                    self.player_y, self.player_x = old_y, old_x
                    
            except curses.error:
                continue

def manhattan_distance(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

# ...existing code...
