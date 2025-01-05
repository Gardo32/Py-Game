import curses
import tempfile
import os
import subprocess
import json

class Editor:
    def __init__(self, stdscr, level_num, bush_id, initial_code=None):
        self.stdscr = stdscr
        self.load_question(level_num, bush_id)
        self.code = self.pre_code.split('\n') if self.pre_code else [""]
        self.cursor_y = 0  # Track cursor position relative to code area
        self.cursor_x = 0
        self.scroll_y = 0
        self.saved_colors = self.save_colors()  # Save original colors
        self.insert_mode = True  # Toggle between insert and overwrite mode
        self.clipboard = ""  # For copy/paste operations
        self.selection_start = None  # For text selection
        
    def save_colors(self):
        # Save current color pairs
        saved = {}
        for i in range(1, 7):  # Save first 6 color pairs
            try:
                fg, bg = curses.pair_content(i)
                saved[i] = (fg, bg)
            except:
                pass
        return saved
        
    def restore_colors(self):
        # Restore original color pairs
        for pair_n, (fg, bg) in self.saved_colors.items():
            curses.init_pair(pair_n, fg, bg)

    def run(self):
        curses.curs_set(1)  # Show cursor
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)  # For instructions
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)  # For status
        
        while True:
            self.draw()
            key = self.stdscr.getch()
            
            if key == 27:  # ESC - clear selection or exit
                if self.selection_start is not None:
                    self.selection_start = None
                else:
                    self.restore_colors()
                    curses.curs_set(0)
                    return None
            elif key == curses.KEY_IC:  # Insert key
                self.insert_mode = not self.insert_mode
            elif key == 9:  # Tab key
                self.insert_tab()
            elif key == 10:  # Enter
                # Split line at cursor
                current_line = self.code[self.cursor_y]
                self.code[self.cursor_y] = current_line[:self.cursor_x]
                self.code.insert(self.cursor_y + 1, current_line[self.cursor_x:])
                self.cursor_y += 1
                self.cursor_x = 0
            elif key in (curses.KEY_BACKSPACE, 8, 127):  # Support multiple backspace keys
                if self.selection_start is not None:
                    self.delete_selection()
                else:
                    self.handle_backspace()
            elif key == curses.KEY_DC:  # Delete
                if self.selection_start is not None:
                    self.delete_selection()
                else:
                    self.handle_delete()
            elif key == 24:  # Ctrl+X - Cut or Exit
                if self.selection_start is not None:
                    self.cut_selection()
                else:
                    result = self.save_and_run()
                    if not result:
                        self.show_error_popup()
                        continue
                    self.restore_colors()
                    curses.curs_set(0)
                    return result
            elif key == 3:  # Ctrl+C - Copy
                self.copy_selection()
            elif key == 22:  # Ctrl+V - Paste
                self.paste_clipboard()
            elif key == 26:  # Ctrl+Z - Undo
                # TODO: Implement undo functionality
                pass
            elif key == curses.KEY_UP and self.cursor_y > 0:
                self.cursor_y -= 1
                self.cursor_x = min(self.cursor_x, len(self.code[self.cursor_y]))
            elif key == curses.KEY_DOWN and self.cursor_y < len(self.code) - 1:
                self.cursor_y += 1
                self.cursor_x = min(self.cursor_x, len(self.code[self.cursor_y]))
            elif key == curses.KEY_LEFT and self.cursor_x > 0:
                self.cursor_x -= 1
            elif key == curses.KEY_RIGHT:
                current_line = self.code[self.cursor_y]
                if self.cursor_x < len(current_line):
                    self.cursor_x += 1
            elif key == curses.KEY_HOME:
                if curses.keypad(self.stdscr, True):  # Check if CTRL is pressed
                    self.cursor_y = 0
                self.cursor_x = 0
            elif key == curses.KEY_END:
                if curses.keypad(self.stdscr, True):  # Check if CTRL is pressed
                    self.cursor_y = len(self.code) - 1
                self.cursor_x = len(self.code[self.cursor_y])
            elif 32 <= key <= 126:  # Printable characters
                if self.selection_start is not None:
                    self.delete_selection()
                if self.insert_mode:
                    self.insert_character(chr(key))
                else:
                    self.overwrite_character(chr(key))
            
            # Adjust scroll if needed
            h, _ = self.stdscr.getmaxyx()
            if self.cursor_y - self.scroll_y > h - 7:  # -7 for instructions and status
                self.scroll_y = self.cursor_y - (h - 7)
            elif self.cursor_y < self.scroll_y:
                self.scroll_y = self.cursor_y
                
    def draw(self):
        self.stdscr.clear()
        h, w = self.stdscr.getmaxyx()
        
        # Draw instructions (now properly formatted)
        for i, line in enumerate(self.instructions):
            if i >= 3: break  # Only show first 3 lines
            try:
                self.stdscr.addstr(i, 0, line[:w-1], curses.color_pair(1))
            except curses.error:
                pass
        
        # Draw separator
        self.stdscr.addstr(3, 0, "-" * (w-1), curses.color_pair(1))
        
        # Draw code
        visible_lines = h - 6  # Space for instructions and status
        for i, line in enumerate(self.code[self.scroll_y:self.scroll_y + visible_lines], 4):
            if i >= h-2: break
            self.stdscr.addstr(i, 0, line[:w-1])
            
        # Draw status bar
        status = " CTRL+X: Save and Run | ESC: Cancel | Tab: Indent | Arrows: Move | Home/End: Line Start/End "
        self.stdscr.addstr(h-1, 0, status[:w-1], curses.color_pair(2))
        
        # Position cursor
        self.stdscr.move(self.cursor_y - self.scroll_y + 4, self.cursor_x)
        self.stdscr.refresh()
        
    def save_and_run(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('\n'.join(self.code))
            temp_name = f.name
            
        try:
            result = subprocess.run(['python', temp_name], 
                                 capture_output=True, 
                                 text=True)
            os.unlink(temp_name)
            self.last_output = result.stdout.strip()  # Store the output
            return self.last_output == self.expected_output
        except Exception as e:
            os.unlink(temp_name)
            self.last_output = f"Error: {str(e)}"  # Store error message
            return False

    def handle_arrow_keys(self, key):
        old_y, old_x = self.cursor_y, self.cursor_x
        
        if key == curses.KEY_UP and self.cursor_y > 0:
            self.cursor_y -= 1
            self.cursor_x = min(self.cursor_x, len(self.code[self.cursor_y]))
        elif key == curses.KEY_DOWN and self.cursor_y < len(self.code) - 1:
            self.cursor_y += 1
            self.cursor_x = min(self.cursor_x, len(self.code[self.cursor_y]))
        elif key == curses.KEY_LEFT:
            if self.cursor_x > 0:
                self.cursor_x -= 1
            elif self.cursor_y > 0:
                self.cursor_y -= 1
                self.cursor_x = len(self.code[self.cursor_y])
        elif key == curses.KEY_RIGHT:
            if self.cursor_x < len(self.code[self.cursor_y]):
                self.cursor_x += 1
            elif self.cursor_y < len(self.code) - 1:
                self.cursor_y += 1
                self.cursor_x = 0

    def insert_character(self, char):
        line = self.code[self.cursor_y]
        self.code[self.cursor_y] = line[:self.cursor_x] + char + line[self.cursor_x:]
        self.cursor_x += 1

    def overwrite_character(self, char):
        line = self.code[self.cursor_y]
        if self.cursor_x < len(line):
            self.code[self.cursor_y] = line[:self.cursor_x] + char + line[self.cursor_x + 1:]
        else:
            self.code[self.cursor_y] = line[:self.cursor_x] + char
        self.cursor_x += 1

    def handle_backspace(self):
        if self.cursor_x > 0:
            line = self.code[self.cursor_y]
            # Check if deleting an indentation
            if self.cursor_x >= 4 and line[self.cursor_x-4:self.cursor_x].isspace():
                # Remove full tab (4 spaces)
                self.code[self.cursor_y] = line[:self.cursor_x-4] + line[self.cursor_x:]
                self.cursor_x -= 4
            else:
                # Regular single character delete
                self.code[self.cursor_y] = line[:self.cursor_x-1] + line[self.cursor_x:]
                self.cursor_x -= 1
        elif self.cursor_y > 0:
            # Join with previous line
            prev_line_length = len(self.code[self.cursor_y-1])
            self.code[self.cursor_y-1] += self.code[self.cursor_y]
            self.code.pop(self.cursor_y)
            self.cursor_y -= 1
            self.cursor_x = prev_line_length

    def handle_delete(self):
        line = self.code[self.cursor_y]
        if self.cursor_x < len(line):
            self.code[self.cursor_y] = line[:self.cursor_x] + line[self.cursor_x+1:]
        elif self.cursor_y < len(self.code) - 1:
            self.code[self.cursor_y] += self.code[self.cursor_y + 1]
            self.code.pop(self.cursor_y + 1)

    def cut_selection(self):
        if self.selection_start is not None:
            start_y, start_x = self.selection_start
            end_y, end_x = self.cursor_y, self.cursor_x
            if (end_y, end_x) < (start_y, start_x):
                start_y, start_x, end_y, end_x = end_y, end_x, start_y, start_x
            
            # Get selected text
            self.clipboard = self.get_selected_text(start_y, start_x, end_y, end_x)
            self.delete_selection()
            self.selection_start = None

    def copy_selection(self):
        if self.selection_start is not None:
            start_y, start_x = self.selection_start
            end_y, end_x = self.cursor_y, self.cursor_x
            if (end_y, end_x) < (start_y, start_x):
                start_y, start_x, end_y, end_x = end_y, end_x, start_y, start_x
            
            self.clipboard = self.get_selected_text(start_y, start_x, end_y, end_x)

    def paste_clipboard(self):
        if self.clipboard:
            lines = self.clipboard.split('\n')
            if len(lines) == 1:
                line = self.code[self.cursor_y]
                self.code[self.cursor_y] = line[:self.cursor_x] + self.clipboard + line[self.cursor_x:]
                self.cursor_x += len(self.clipboard)
            else:
                # Handle multiline paste
                current_line = self.code[self.cursor_y]
                new_lines = [
                    current_line[:self.cursor_x] + lines[0],
                    *lines[1:-1],
                    lines[-1] + current_line[self.cursor_x:]
                ]
                self.code[self.cursor_y:self.cursor_y+1] = new_lines
                self.cursor_y += len(lines) - 1
                self.cursor_x = len(lines[-1])

    def get_selected_text(self, start_y, start_x, end_y, end_x):
        if start_y == end_y:
            return self.code[start_y][start_x:end_x]
        
        selected = [self.code[start_y][start_x:]]
        for y in range(start_y + 1, end_y):
            selected.append(self.code[y])

    def insert_tab(self):
        """Insert 4 spaces for tab"""
        for _ in range(4):  # Standard Python indentation
            self.insert_character(' ')

    def show_error_popup(self):
        h, w = self.stdscr.getmaxyx()
        # Calculate popup dimensions
        msg = "Incorrect Code press any button to go back to editor"
        output_msg = f"Your output: {self.last_output}"  # Add output message
        box_width = max(len(msg), len(output_msg)) + 4
        box_height = 4  # Increased height for output
        start_y = h//2 - box_height//2
        start_x = w//2 - box_width//2

        # Save the screen content behind the popup
        popup_area = curses.newwin(box_height, box_width, start_y, start_x)
        popup_area.bkgd(' ', curses.color_pair(2))
        popup_area.border()
        popup_area.addstr(1, 2, msg)
        popup_area.addstr(2, 2, output_msg)  # Show user's output
        popup_area.refresh()
        
        # Wait for any key
        self.stdscr.getch()
        
        # Refresh the main screen to clear popup
        self.stdscr.touchwin()
        self.stdscr.refresh()

    def load_question(self, level_num, bush_id):
        try:
            with open('question_store.json', 'r') as f:
                questions = json.load(f)
                
            level_questions = questions[f"level{level_num}"]
            bush_data = level_questions[bush_id]
            
            # Format instructions into list for proper display
            self.instructions = [
                "Task Instructions:",
                bush_data["instructions"],
                "Expected Output: " + bush_data["expected_output"]
            ]
            self.pre_code = bush_data["pre_code"]
            self.expected_output = bush_data["expected_output"]
        except Exception as e:
            print(f"Error loading question: {e}")  # Debug print
            # Fallback to default if file/data not found
            self.instructions = [
                "Task Instructions:",
                "Print 'HW' to break the bush",
                "Expected Output: HW"
            ]
            self.pre_code = "print()"
            self.expected_output = "HW"