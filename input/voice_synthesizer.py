"""
Voice Synthesizer — Text-to-Speech for JARVIS
Uses macOS native 'say' command for reliable, high-quality speech.
Falls back to pyttsx3 on other platforms.
"""
import subprocess
import platform
import shutil


class VoiceSynthesizer:
    def __init__(self):
        self.system = platform.system()

        if self.system == "Darwin" and shutil.which("say"):
            self.engine = "macos_say"
            # Available voices: Daniel (UK), Samantha (US), Alex (US)
            # Run `say -v '?'` in terminal to see all voices
            self.voice = "Daniel"  # British voice — very JARVIS-like
            self.rate = 180  # Words per minute
            print(f"  [TTS] Using macOS 'say' — voice: {self.voice}")
        else:
            self.engine = "pyttsx3"
            try:
                import pyttsx3
                self._pyttsx3 = pyttsx3.init()
                self._pyttsx3.setProperty('rate', 170)
                print("  [TTS] Using pyttsx3 engine")
            except Exception as e:
                self.engine = "none"
                print(f"  [TTS] WARNING: No TTS engine available — {e}")

    def speak(self, text):
        """Speak the given text aloud."""
        if not text:
            return

        try:
            if self.engine == "macos_say":
                self._speak_macos(text)
            elif self.engine == "pyttsx3":
                self._speak_pyttsx3(text)
            else:
                print(f"[TTS silent] {text}")
        except Exception as e:
            print(f"[TTS Error] {e}")
            # Always print as fallback
            print(f"[TTS fallback] {text}")

    def _speak_macos(self, text):
        """Use macOS native 'say' command — most reliable on Mac."""
        # Escape single quotes in text
        safe_text = text.replace("'", "'\\''")
        subprocess.run(
            ["say", "-v", self.voice, "-r", str(self.rate), safe_text],
            check=True
        )

    def _speak_pyttsx3(self, text):
        """Use pyttsx3 engine as fallback."""
        self._pyttsx3.say(text)
        self._pyttsx3.runAndWait()

    def set_voice(self, voice_name):
        """Change the macOS voice (e.g., 'Daniel', 'Samantha', 'Alex')."""
        if self.engine == "macos_say":
            self.voice = voice_name
            print(f"[TTS] Voice changed to: {voice_name}")

    def set_rate(self, rate):
        """Change speech rate (words per minute)."""
        self.rate = rate
        if self.engine == "pyttsx3":
            self._pyttsx3.setProperty('rate', rate)
