# ai_model/context_manager.py
class ContextManager:
    def __init__(self, max_history=5):
        self.max_history = max_history
        self.history = []

    def update_history(self, user_input, assistant_response):
        self.history.append({"user": user_input, "assistant": assistant_response})
        if len(self.history) > self.max_history:
            self.history.pop(0)

    def get_context(self):
        context = ""
        for turn in self.history:
            context += f"User: {turn['user']}\nAssistant: {turn['assistant']}\n"
        return context
