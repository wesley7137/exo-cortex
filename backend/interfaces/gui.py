# interfaces/gui.py
import tkinter as tk
from tkinter import scrolledtext
from ai_model.integrations_manager import AIAssistant
from cortex.cortex import KnowledgeIngestion
import threading

class ExoCortexGUI:
    def __init__(self, user_id):
        self.user_id = user_id
        self.assistant = AIAssistant(user_id)
        self.ingestion = KnowledgeIngestion(user_id)
        self.window = tk.Tk()
        self.window.title("Exo Cortex Assistant")

        # Conversation Display
        self.chat_display = scrolledtext.ScrolledText(self.window, wrap=tk.WORD)
        self.chat_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # User Input
        self.user_input = tk.Entry(self.window, width=80)
        self.user_input.pack(side=tk.LEFT, padx=10, pady=10)
        self.user_input.bind("<Return>", self.send_message)

        # Send Button
        self.send_button = tk.Button(self.window, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.LEFT, padx=5)

        # Voice Button
        self.voice_button = tk.Button(self.window, text="Voice Input", command=self.voice_input)
        self.voice_button.pack(side=tk.LEFT, padx=5)

    def send_message(self, event=None):
        user_text = self.user_input.get()
        if user_text.strip():
            self.chat_display.insert(tk.END, f"You: {user_text}\n")
            self.user_input.delete(0, tk.END)
            threading.Thread(target=self.get_response, args=(user_text,)).start()

    def get_response(self, user_text):
        response = self.assistant.generate_response(user_text)
        self.chat_display.insert(tk.END, f"Assistant: {response}\n")

    def voice_input(self):
        from interfaces.voice_interface import VoiceInterface
        voice_interface = VoiceInterface()
        user_text = voice_interface.listen()
        if user_text:
            self.chat_display.insert(tk.END, f"You (Voice): {user_text}\n")
            threading.Thread(target=self.get_response, args=(user_text,)).start()

    def run(self):
        self.window.mainloop()

# To run the GUI
if __name__ == "__main__":
    gui = ExoCortexGUI(user_id=123)  # Replace with actual user ID
    gui.run()
