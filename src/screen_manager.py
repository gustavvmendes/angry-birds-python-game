class ScreenManager:
    def __init__(self):
        self.state = 0

    def change(self, new_state):
        self.state = new_state

    def current(self):
        return self.state