"""
LLM Engine — Brain of JARVIS
Supports OpenAI GPT (primary) with a local fallback for offline use.
Includes intent detection and tool routing for system commands.
"""
import os
import re
from datetime import datetime

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from tools.system_control import SystemControlTool


class LLMEngine:
    def __init__(self, memory=None):
        self.memory = memory
        self.client = None
        self.model = os.getenv("JARVIS_MODEL", "gpt-4o-mini")
        self.system_tool = SystemControlTool()

        if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            print(f"  [Brain] OpenAI connected — model: {self.model}")
        else:
            print("  [Brain] No OpenAI key — running in OFFLINE mode (local fallback)")

    def generate_response(self, user_input):
        """Generate a response — detects intents first, then uses LLM or fallback."""
        # Add user message to memory
        if self.memory:
            self.memory.add_user_message(user_input)

        # 1. Check for tool-actionable intents FIRST
        tool_response = self._detect_and_execute_tool(user_input)
        if tool_response:
            response = tool_response
        elif self.client:
            response = self._call_openai()
        else:
            response = self._local_fallback(user_input)

        # Store response in memory
        if self.memory:
            self.memory.add_assistant_message(response)

        return response

    # ─── Intent Detection & Tool Routing ──────────────────────────

    def _detect_and_execute_tool(self, text):
        """Detect if the user wants a system action and execute it."""
        text_lower = text.lower().strip()

        # ── Wake / Unlock Screen ── (must be checked BEFORE open-app)
        wake_phrases = [
            "open the mac", "open my mac", "open the screen", "open my screen",
            "wake up", "wake the screen", "wake my screen", "wake the mac",
            "unlock", "unlock screen", "unlock the screen", "unlock my mac",
            "turn on the screen", "turn on screen", "turn on the display",
        ]
        if any(phrase in text_lower for phrase in wake_phrases):
            return self.system_tool.wake_screen()

        # ── Open Application ──
        open_patterns = [
            r"(?:open|launch|start|run)\s+(.+?)(?:\s+(?:app|application|for me|please))?$",
            r"(?:can you |could you |please )?open\s+(.+)",
        ]
        for pattern in open_patterns:
            match = re.search(pattern, text_lower)
            if match:
                app_name = match.group(1).strip().rstrip(".")
                # Filter out non-app phrases
                skip_words = [
                    "it", "that", "this", "the", "a", "an",
                    "the mac", "my mac", "the screen", "my screen",
                    "the computer", "my computer", "the display",
                ]
                if app_name and app_name not in skip_words:
                    return self.system_tool.open_application(app_name)

        # ── Close Application ──
        close_patterns = [
            r"(?:close|quit|exit|kill|stop)\s+(.+?)(?:\s+(?:app|application|for me|please))?$",
        ]
        for pattern in close_patterns:
            match = re.search(pattern, text_lower)
            if match:
                app_name = match.group(1).strip().rstrip(".")
                if app_name and app_name not in ["it", "that", "this"]:
                    return self.system_tool.close_application(app_name)

        # ── Volume Control ──
        vol_match = re.search(r"(?:set |change )?volume\s+(?:to\s+)?(\d+)", text_lower)
        if vol_match:
            return self.system_tool.set_volume(vol_match.group(1))
        if "mute" in text_lower:
            return self.system_tool.set_volume(0)
        if "max volume" in text_lower or "full volume" in text_lower:
            return self.system_tool.set_volume(100)

        # ── Dark Mode ──
        if "dark mode" in text_lower:
            return self.system_tool.toggle_dark_mode()

        # ── Lock Screen ──
        if "lock" in text_lower and ("screen" in text_lower or "computer" in text_lower or "mac" in text_lower):
            return self.system_tool.lock_screen()

        # ── Running Apps ──
        if any(phrase in text_lower for phrase in ["running apps", "what's running", "active apps", "which apps"]):
            return self.system_tool.get_running_apps()

        return None  # No tool match — let LLM handle it

    # ─── OpenAI ───────────────────────────────────────────────────

    def _call_openai(self):
        """Call OpenAI API with full conversation history."""
        try:
            messages = self.memory.get_messages() if self.memory else [
                {"role": "system", "content": "You are JARVIS, an advanced AI assistant."},
            ]

            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=300,
                temperature=0.7,
            )
            return completion.choices[0].message.content.strip()

        except Exception as e:
            print(f"  [Brain] OpenAI error: {e}")
            return "I encountered an issue connecting to my neural network. Please check the API key."

    # ─── Offline Fallback ─────────────────────────────────────────

    def _local_fallback(self, text):
        """Smart rule-based fallback when no API key is available."""
        text_lower = text.lower()
        now = datetime.now()

        if any(w in text_lower for w in ["hello", "hi", "hey", "good morning", "good evening"]):
            hour = now.hour
            greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 17 else "Good evening"
            return f"{greeting}, Sir. All systems are operational. How may I assist you?"

        elif "time" in text_lower:
            return f"It is currently {now.strftime('%I:%M %p')}, Sir."

        elif "date" in text_lower or "today" in text_lower:
            return f"Today is {now.strftime('%A, %B %d, %Y')}, Sir."

        elif "name" in text_lower or "who are you" in text_lower:
            return "I am JARVIS — Just A Rather Very Intelligent System. At your service."

        elif any(w in text_lower for w in ["thanks", "thank you"]):
            return "You're most welcome, Sir."

        elif any(w in text_lower for w in ["bye", "goodbye", "shutdown", "exit", "quit"]):
            return "Goodbye, Sir. I'll be here when you need me."

        elif "weather" in text_lower:
            return "I don't have weather tools connected yet, Sir. That's coming in Phase 2."

        elif "capabilities" in text_lower or "what can you do" in text_lower:
            return (
                "I can hold a voice conversation, tell you the time and date, "
                "open and close applications on your Mac, control volume, "
                "toggle dark mode, and lock your screen. "
                "More capabilities like weather, calendar, and web browsing are coming soon."
            )

        else:
            return (
                f"I understand you said: '{text}'. "
                "I'm currently running in offline mode without my full neural network. "
                "Set the OPENAI_API_KEY in your .env file to unlock my full capabilities."
            )
