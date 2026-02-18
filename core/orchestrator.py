"""
Orchestrator — Central nervous system of JARVIS.
Manages the Input → Brain → Output loop with support for
both voice and text input modes.
"""
import time
import threading


class Orchestrator:
    def __init__(self, listener, brain, speaker, memory=None):
        self.listener = listener
        self.brain = brain
        self.speaker = speaker
        self.memory = memory
        self.is_running = False
        self.mode = "voice"  # "voice" or "text"

    def start(self):
        """Start the main JARVIS loop."""
        self.is_running = True
        self.speaker.speak("Systems online. All modules nominal. How may I help you?")

        # Start text input listener on a separate thread
        text_thread = threading.Thread(target=self._text_input_loop, daemon=True)
        text_thread.start()

        # Main voice loop
        self._voice_loop()

    def _voice_loop(self):
        """Continuously listen for voice input."""
        while self.is_running:
            try:
                user_input = self.listener.listen()

                if user_input:
                    self._process(user_input, source="voice")

                    # Check for exit commands
                    if any(w in user_input.lower() for w in ["shutdown", "exit", "quit", "goodbye"]):
                        self.stop()
                        break

            except Exception as e:
                print(f"[Loop Error] {e}")

            time.sleep(0.1)

    def _text_input_loop(self):
        """Listen for typed input in the terminal (runs on a background thread)."""
        while self.is_running:
            try:
                text = input()  # Blocking read from stdin
                if text.strip():
                    self._process(text.strip(), source="text")

                    if any(w in text.lower() for w in ["shutdown", "exit", "quit", "goodbye"]):
                        self.stop()
                        break
            except (EOFError, KeyboardInterrupt):
                break

    def _process(self, user_input, source="voice"):
        """Process user input through the brain and speak the response."""
        print(f"\n{'🎤' if source == 'voice' else '⌨️ '}  You: {user_input}")
        print("🧠 Thinking...")

        response = self.brain.generate_response(user_input)

        print(f"🤖 JARVIS: {response}")
        self.speaker.speak(response)

    def stop(self):
        """Gracefully shut down."""
        self.is_running = False
        print("\n[JARVIS] Shutting down. Goodbye.")
