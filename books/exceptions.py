class NotValidISBN(Exception):
    def __init__(self, version, message):
        self.version = version
        self.message = message
        super().__init__(message)

    def __str__(self):
        return f'NotValidISBN_{self.version} -> {self.message}'


class ReviewsIntegrityError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)

    def __str__(self):
        return f'Integrity error no more reviews allowed -> {self.message}'
