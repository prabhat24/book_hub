class NotValidISBN(Exception):
    def __init__(self, version, message):
        self.version = version
        super().__init__(message)

    def __str__(self):
        return f'NotValidISBN_{self.version} -> {self.message}'