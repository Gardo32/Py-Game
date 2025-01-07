import pygame
import random
import threading
import time
import os
import csv

class MusicManager:
    def __init__(self):
        self.enabled = True
        self.current_music = None
        self.main_music_position = 0  # Track position in main music
        
        # Initialize pygame mixer
        try:
            pygame.mixer.init()
            pygame.mixer.music.set_volume(0.5)  # Set default volume
        except:
            print("Could not initialize sound system")
            self.enabled = False
            
        self.main_music_path = "music/Chill & Relaxing Pokémon Music Mix.mp3"
        self.battle_music_folder = "music/battle_mp3"  # Changed to MP3 folder
        self.load_available_battle_music()

    def load_available_battle_music(self):
        """Load all available MP3 files from battle music folder"""
        self.battle_tracks = []
        try:
            if os.path.exists(self.battle_music_folder):
                for file in os.listdir(self.battle_music_folder):
                    if file.endswith('.mp3'):
                        full_path = os.path.join(self.battle_music_folder, file)
                        self.battle_tracks.append(full_path)
                print(f"Found {len(self.battle_tracks)} battle music tracks")
            else:
                print(f"Battle music folder not found: {self.battle_music_folder}")
        except Exception as e:
            print(f"Error loading battle music: {e}")

    def toggle_music(self):
        self.enabled = not self.enabled
        if self.enabled:
            if self.current_music:
                pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()
            if self.current_music == "main":
                self.main_music_position = pygame.mixer.music.get_pos()

    def start_main_music(self):
        if not self.enabled:
            return
            
        try:
            pygame.mixer.music.load(self.main_music_path)
            pygame.mixer.music.play(-1, start=self.main_music_position/1000.0)  # Convert ms to seconds
            self.current_music = "main"
        except Exception as e:
            print(f"Error playing main music: {e}")

    def start_editor_music(self):
        if not self.enabled:
            return
            
        try:
            # Store main music position before switching
            if self.current_music == "main":
                self.main_music_position = pygame.mixer.music.get_pos()
            
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            
            if self.battle_tracks:
                track_path = random.choice(self.battle_tracks)
                print(f"Playing battle track: {os.path.basename(track_path)}")
                pygame.mixer.music.load(track_path)
                pygame.mixer.music.play()
                self.current_music = "editor"
            else:
                print("No battle music files found in:", self.battle_music_folder)
                print("Available files:", os.listdir(self.battle_music_folder) if os.path.exists(self.battle_music_folder) else "folder not found")
                self.resume_main_music()
        except Exception as e:
            print(f"Error playing editor music: {e}")
            self.resume_main_music()

    def resume_main_music(self):
        if not self.enabled:
            return
            
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            pygame.mixer.music.load(self.main_music_path)
            pygame.mixer.music.play(-1, start=self.main_music_position/1000.0)  # Resume from stored position
            self.current_music = "main"
        except Exception as e:
            print(f"Error resuming main music: {e}")

    def cleanup(self):
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            pygame.mixer.quit()
        except:
            pass
