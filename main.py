"""
JARVIS AI Assistant — Main Entry Point
"""
import os
import sys
from dotenv import load_dotenv

# Ensure project root is on the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from input.voice_listener import VoiceListener
from input.voice_synthesizer import VoiceSynthesizer
from core.memory import ConversationMemory
from core.llm_engine import LLMEngine
from core.orchestrator import Orchestrator


BANNER = r"""
     ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗
     ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝
     ██║███████║██████╔╝██║   ██║██║███████╗
██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║
╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║
 ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝
   Just A Rather Very Intelligent System  v1.0
"""


def main():
    load_dotenv()
    print(BANNER)

    print("[Init] Loading components...")

    # 1. Memory
    memory = ConversationMemory(max_turns=20)
    print("  ✅ Memory Module")

    # 2. Brain (LLM)
    brain = LLMEngine(memory=memory)
    print("  ✅ Brain Module")

    # 3. Voice Input
    listener = VoiceListener()
    print("  ✅ Voice Listener")

    # 4. Voice Output
    speaker = VoiceSynthesizer()
    print("  ✅ Voice Synthesizer")

    # 5. Orchestrator
    orchestrator = Orchestrator(listener, brain, speaker, memory=memory)
    print("  ✅ Orchestrator")

    print("\n[JARVIS] All systems go. Listening for voice and text input.")
    print("[JARVIS] Type in terminal OR speak to interact. Say 'shutdown' to exit.\n")

    try:
        orchestrator.start()
    except KeyboardInterrupt:
        print("\n[JARVIS] Interrupted. Shutting down...")
        sys.exit(0)


if __name__ == "__main__":
    main()
