import pygame
import time
import os
import threading

global is_paused, is_stopped, music_index
is_paused = False
is_stopped = False
music_index = 0

# Validate the music directory
music_dir = os.getenv('music_dir')  
if not music_dir or not os.path.isdir(music_dir):
    raise ValueError("Invalid or missing 'music_dir' environment variable!")

# Only load supported audio files (.mp3, .wav)
songs = [song for song in os.listdir(music_dir) if song.lower().endswith(('.mp3', '.wav'))]
if not songs:
    raise ValueError("No compatible audio files found in the specified 'music_dir'!")

# Initialize Pygame and Pygame mixer
pygame.mixer.quit()  # Ensure no previous mixer is running
pygame.init()

# Initialize the mixer with specific settings
try:
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    print("Pygame mixer initialized successfully.")
except pygame.error as e:
    print(f"Failed to initialize Pygame mixer: {e}")
    exit(1)

def check_song_end():
    while True:
        if not pygame.mixer.music.get_busy() and not is_paused and not is_stopped:
            play_next_song()
        time.sleep(1)

def play_song(index):
    global is_stopped
    try:
        is_stopped = False
        song_path = os.path.join(music_dir, songs[index])
        if os.path.isfile(song_path):
            pygame.mixer.music.load(song_path)
            pygame.mixer.music.play()
            print(f"Now playing: {songs[index]}")
            threading.Thread(target=check_song_end, daemon=True).start()
        else:
            print(f"File not found: {song_path}")
            play_next_song()
    except pygame.error as e:
        print(f"Error playing song: {e}")
        print("Switching to next song...")
        play_next_song()

def stop_music():
    global is_stopped
    pygame.mixer.music.stop()
    is_stopped = True

def play_next_song():
    global music_index
    music_index = (music_index + 1) % len(songs)
    play_song(music_index)

def play_previous_song():
    global music_index
    music_index = (music_index - 1) % len(songs)
    play_song(music_index)

def pause_music():
    global is_paused
    if is_paused:
        pygame.mixer.music.unpause()
        is_paused = False
    else:
        pygame.mixer.music.pause()
        is_paused = True

def main():
    if pygame.mixer.get_init() is None:
        print("Pygame mixer was not initialized. Exiting...")
        return
    
    play_song(music_index)

    # Add an event loop to keep the program running
    print("Press [CTRL+C] to stop the music player.")
    try:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    stop_music()
                    pygame.quit()
                    return
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Music player stopped.")
        stop_music()
        pygame.quit()

if __name__ == "__main__":
    main()
