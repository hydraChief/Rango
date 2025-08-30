class Position:
    def __init__(self, index, line, col, filename, text):
        self.index = index
        self.line = line
        self.col = col
        self.filename = filename
        self.text = text

    def copy(self):
        return Position(self.index, self.line, self.col, self.filename, self.text)