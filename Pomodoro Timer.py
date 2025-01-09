import customtkinter as ctk
from tkinter import messagebox
from threading import Thread
import requests
import time
import json
import os
import re
from pygame import mixer

# Function to format time in minutes and seconds
def format_time(time_left):
    minutes = time_left // 60
    seconds = time_left % 60
    return f"{minutes:02d}:{seconds:02d}"

class PomodoroApp:
    def __init__(self, master):
        self.master = master
        self.config_file = "config.json"  # Configuration file to save user settings

        self.work_time = 50 * 60  # Default work time in seconds
        self.break_time = 10 * 60  # Default break time in seconds
        self.paused = True  # Start with the timer paused
        self.working = True  # Initial state is working mode
        self.quote = ""  # Variable to store motivational quotes
        self.button_color = ""  # Variable to store button color
        # Dictionary to store predefined colors
        self.colors = {"Default": "#1f538d", "Red": "#C50000", "Blue": "#0300B6", "Green": "#028E02", "Pink": "#FF17ED"}
        self.theme_color = ""  # Variable to store the theme color

        # Load settings from config file
        self.load_settings()

        self.time_left = self.work_time  # Set initial time left to work time

        ctk.set_appearance_mode(self.theme_color)  # Set the theme color

        # Create the time label
        self.time_label = ctk.CTkLabel(master, text=format_time(self.time_left), font=('Helvetica', 48))
        self.time_label.pack(fill='both', expand=True)

        # Create the quote label
        self.quote_label = ctk.CTkLabel(master, text="", wraplength=350, font=('Helvetica', 16))
        self.quote_label.pack(pady=5, fill='both', expand=True)

        # Create the pause/start button
        self.pause_button = ctk.CTkButton(master, text="Start", fg_color=self.colors[self.button_color], command=self.pause)
        self.pause_button.pack(fill='both', padx=10, pady=7, expand=True)

        # Create the settings button
        self.settings_button = ctk.CTkButton(master, text="Settings", fg_color=self.colors[self.button_color], command=self.settings)
        self.settings_button.pack(fill='both', padx=10, pady=7, expand=True)

        self.update_time()  # Start updating the time
        self.update_quote()  # Fetch a motivational quote

        # Initialize mixer for playing sounds
        mixer.init()
        self.sound = mixer.Sound('chime.mp3')  # Load a sound file

        # Start the countdown thread
        self.thread = Thread(target=self.countdown)
        self.thread.start()

        # Bind the Enter key to the pause/start button
        self.master.bind('<Return>', self.handle_enter)
        self.master.bind('<Destroy>', self.on_destroy)

    def update_time(self):
        # Update the time label every 100 milliseconds
        self.time_label.configure(text=format_time(self.time_left))
        self.master.after(100, self.update_time)

    def update_main_buttons(self, color):
        # Update the color of the main buttons
        self.settings_button.configure(fg_color=self.colors[color])
        self.pause_button.configure(fg_color=self.colors[color])

    def update_theme(self, type):
        # Update the application theme
        self.theme_color = type
        ctk.set_appearance_mode(type)

    def handle_enter(self, event):
        # Handle the Enter key to start/pause the timer
        self.pause()

    def on_destroy(self, event):
        # Save settings when the application is closed
        self.save_settings_close()

    def adjust_window_size(self):
        # Adjust the window size based on the quote length
        self.quote_label.update_idletasks()  # Ensure the quote label size is updated
        quote_height = self.quote_label.winfo_height()
        new_height = 220 + (quote_height - 40)
        self.master.geometry(f'400x{new_height}')

    def update_quote(self):
        # Fetch a motivational quote from the API
        try:
            response = requests.get("https://api.quotable.io/quotes/random?tags=motivational")
            data = response.json()
            self.quote = data["content"] + " - " + data["author"]
            self.quote_label.configure(text=self.quote)
            self.master.after(100, self.adjust_window_size)  # Adjust window size after updating the quote
        except Exception as e:
            print(e)

    def countdown(self):
        # Countdown function running in a separate thread
        while True:
            if not self.paused:
                if self.time_left > 0:
                    self.time_left -= 1
                else:
                    # Switch between work time and break time
                    if self.working:
                        self.time_left = self.break_time
                        self.working = False
                    else:
                        self.time_left = self.work_time
                        self.working = True
                        self.update_quote()
                    self.sound.play()  # Play sound when switching
            time.sleep(1)

    def pause(self):
        # Toggle pause/start of the timer
        self.paused = not self.paused
        self.pause_button.configure(text="Pause" if not self.paused else "Start")

    def settings(self):
        # Create the settings window
        settings_window = ctk.CTkToplevel(self.master)
        settings_window.title('Settings')

        ctk.CTkLabel(settings_window, text="Work time (minutes): ").pack()
        work_entry = ctk.CTkEntry(settings_window)
        work_entry.insert(0, str(self.work_time // 60))
        work_entry.pack(expand=True)

        ctk.CTkLabel(settings_window, text="Break time (minutes):").pack()
        break_entry = ctk.CTkEntry(settings_window)
        break_entry.insert(0, str(self.break_time // 60))
        break_entry.pack(expand=True)

        ctk.CTkLabel(settings_window, text="Button Color:").pack()
        color_var = ctk.StringVar(value=self.button_color)
        color_menu = ctk.CTkOptionMenu(settings_window, variable=color_var, fg_color=self.colors[self.button_color],
                                       dropdown_fg_color=self.colors[self.button_color],
                                       values=list(self.colors.keys()))
        color_menu.pack(expand=True)

        ctk.CTkLabel(settings_window, text="Or, enter a custom hex color \nand give it a name:").pack(pady=10)
        hex_entry = ctk.CTkEntry(settings_window, placeholder_text="hex_code, name")
        hex_entry.pack(pady=5, expand=True)

        ctk.CTkLabel(settings_window, text="Theme:").pack()
        theme_var = ctk.StringVar(value=self.theme_color)
        theme_menu = ctk.CTkOptionMenu(settings_window, variable=theme_var, fg_color=self.colors[self.button_color],
                                       dropdown_fg_color=self.colors[self.button_color],
                                       values=["System", "Light", "Dark"])
        theme_menu.pack(expand=True)

        def save_settings():
            # Save settings from the settings window
            self.work_time = int(work_entry.get()) * 60
            self.break_time = int(break_entry.get()) * 60

            # Handle custom hex color input
            if hex_entry.get() != "":
                if len(hex_entry.get()) <= 8:
                    messagebox.showerror("Error", "Hex code entry must contain a hex code and a name!")
                hex_color_name = hex_entry.get().split(",")[1].strip()
                hex_color = hex_entry.get().split(",")[0].strip()
                if re.match(r'^#[0-9A-Fa-f]{6}$', hex_color):
                    self.button_color = hex_color_name
                    self.colors[hex_color_name] = hex_color
            else:
                self.button_color = color_var.get()

            # Reset the timer to the new settings
            if self.working:
                self.time_left = self.work_time
            else:
                self.time_left = self.break_time
            self.paused = True  # Pause the timer when settings are changed
            self.pause_button.configure(text="Start")

            # Update the button colors
            self.update_main_buttons(self.button_color)
            color_menu.configure(fg_color=self.colors[self.button_color])
            theme_menu.configure(fg_color=self.colors[self.button_color])
            self.update_theme(theme_var.get())

            settings_window.destroy()
            self.master.focus_set()  # Set focus back to the main window

        save_settings_button = ctk.CTkButton(settings_window, text="Save", fg_color=self.colors[self.button_color], command=save_settings)
        save_settings_button.pack(pady=20, padx=60, expand=True)

        # Bind the Enter key to the save button in the settings window
        settings_window.bind('<Return>', lambda event: save_settings())

    def save_settings_close(self):
        # Save settings to the config file when closing the application
        settings = {
            "work_time": self.work_time // 60,
            "break_time": self.break_time // 60,
            "button_color": self.button_color,
            "theme_color": self.theme_color,
            "colors": self.colors,
        }
        with open(self.config_file, "w") as f:
            json.dump(settings, f)
            f.close()

    def load_settings(self):
        # Load settings from the config file
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                settings = json.load(f)
                f.close()
            self.work_time = settings["work_time"] * 60
            self.break_time = settings["break_time"] * 60
            self.button_color = settings["button_color"]
            self.theme_color = settings["theme_color"]
            self.colors = settings["colors"]
        else:
            # Default settings if config file does not exist
            self.work_time = 50 * 60
            self.break_time = 10 * 60
            self.button_color = "Default"
            self.theme_color = "System"


# Initialize the application
root = ctk.CTk()
ctk.set_appearance_mode('System')  # Default appearance mode
ctk.set_default_color_theme('dark-blue')  # Default color theme
root.geometry('400x220')  # Initial window size
root.title("Evan's Pomodoro Studying Timer")
app = PomodoroApp(root)
root.mainloop()
