"""
System Control Tool — Open apps, run commands, control the Mac.
"""
import subprocess
import os


# Common app name aliases → actual macOS app names
APP_ALIASES = {
    "chrome": "Google Chrome",
    "google chrome": "Google Chrome",
    "browser": "Google Chrome",
    "safari": "Safari",
    "finder": "Finder",
    "terminal": "Terminal",
    "code": "Visual Studio Code",
    "vscode": "Visual Studio Code",
    "vs code": "Visual Studio Code",
    "spotify": "Spotify",
    "music": "Music",
    "notes": "Notes",
    "calendar": "Calendar",
    "mail": "Mail",
    "messages": "Messages",
    "slack": "Slack",
    "discord": "Discord",
    "zoom": "zoom.us",
    "teams": "Microsoft Teams",
    "word": "Microsoft Word",
    "excel": "Microsoft Excel",
    "powerpoint": "Microsoft PowerPoint",
    "photoshop": "Adobe Photoshop",
    "figma": "Figma",
    "notion": "Notion",
    "telegram": "Telegram",
    "whatsapp": "WhatsApp",
    "settings": "System Preferences",
    "system preferences": "System Preferences",
    "system settings": "System Settings",
    "preview": "Preview",
    "photos": "Photos",
    "facetime": "FaceTime",
    "maps": "Maps",
    "calculator": "Calculator",
    "activity monitor": "Activity Monitor",
    "xcode": "Xcode",
    "iterm": "iTerm",
    "iterm2": "iTerm",
    "obs": "OBS",
    "vlc": "VLC",
    "postman": "Postman",
}


class SystemControlTool:
    def __init__(self):
        self.name = "system_control"
        self.description = "Open applications, control system functions on macOS"

    def open_application(self, app_name):
        """Open a macOS application by name."""
        # Resolve alias
        resolved = APP_ALIASES.get(app_name.lower(), app_name)

        try:
            result = subprocess.run(
                ["open", "-a", resolved],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                return f"Opening {resolved} for you, Sir."
            else:
                # Try the raw name as-is
                result2 = subprocess.run(
                    ["open", "-a", app_name],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result2.returncode == 0:
                    return f"Opening {app_name} for you, Sir."
                else:
                    return f"I couldn't find an application called '{app_name}'. Is it installed?"

        except subprocess.TimeoutExpired:
            return f"The request to open {resolved} timed out."
        except Exception as e:
            return f"Error opening application: {e}"

    def close_application(self, app_name):
        """Quit a macOS application."""
        resolved = APP_ALIASES.get(app_name.lower(), app_name)
        try:
            subprocess.run(
                ["osascript", "-e", f'quit app "{resolved}"'],
                capture_output=True,
                text=True,
                timeout=10
            )
            return f"Closing {resolved}."
        except Exception as e:
            return f"Error closing application: {e}"

    def get_running_apps(self):
        """List currently running applications."""
        try:
            result = subprocess.run(
                ["osascript", "-e",
                 'tell application "System Events" to get name of every process whose background only is false'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                apps = result.stdout.strip()
                return f"Currently running: {apps}"
            return "Could not retrieve running applications."
        except Exception as e:
            return f"Error: {e}"

    def set_volume(self, level):
        """Set system volume (0-100)."""
        try:
            # macOS volume is 0-7 internally, but osascript uses 0-100
            level = max(0, min(100, int(level)))
            subprocess.run(
                ["osascript", "-e", f"set volume output volume {level}"],
                capture_output=True,
                timeout=5
            )
            return f"Volume set to {level}%."
        except Exception as e:
            return f"Error setting volume: {e}"

    def toggle_dark_mode(self):
        """Toggle macOS dark mode."""
        try:
            subprocess.run(
                ["osascript", "-e",
                 'tell app "System Events" to tell appearance preferences to set dark mode to not dark mode'],
                capture_output=True,
                timeout=5
            )
            return "Dark mode toggled."
        except Exception as e:
            return f"Error toggling dark mode: {e}"

    def lock_screen(self):
        """Lock the Mac screen."""
        try:
            # Method 1: Use Ctrl+Cmd+Q shortcut via AppleScript (locks without sleeping)
            result = subprocess.run(
                ["osascript", "-e",
                 'tell application "System Events" to keystroke "q" using {command down, control down}'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return "Screen locked, Sir."

            # Method 2: Fallback — sleep display (also locks if password-on-wake is enabled)
            subprocess.run(
                ["pmset", "displaysleepnow"],
                capture_output=True,
                timeout=5
            )
            return "Screen locked, Sir."
        except Exception as e:
            return f"Error locking screen: {e}"

    def wake_screen(self):
        """Wake the Mac screen from sleep/lock."""
        try:
            # Simulate a key press to wake the display
            subprocess.run(
                ["caffeinate", "-u", "-t", "2"],
                capture_output=True,
                timeout=5
            )
            return "Waking the screen now, Sir."
        except Exception as e:
            return f"Error waking screen: {e}"
