import os
import threading
from dotenv import load_dotenv

load_dotenv()


class GroqKeyManager:

    def __init__(self):
        self.keys = [
            os.getenv("GROQ_API_KEY_1"),
            os.getenv("GROQ_API_KEY_2"),
            os.getenv("GROQ_API_KEY_3"),
            os.getenv("GROQ_API_KEY_4"),
            os.getenv("GROQ_API_KEY_5"),

        ]

        self.keys = [key for key in self.keys if key]

        if not self.keys:
            raise ValueError("No Groq API keys found")

        self.current_index = 0
        self.lock = threading.Lock()

    def get_key(self):
        with self.lock:
            return self.keys[self.current_index]

    def next_key(self):
        with self.lock:
            self.current_index = (
                self.current_index + 1
            ) % len(self.keys)

            return self.keys[self.current_index]


groq_key_manager = GroqKeyManager()