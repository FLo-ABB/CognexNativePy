class CognexCommandError(Exception):
    """
    Exception raised when a Cognex command fails.

    Attributes:
        message (str): The error message associated with the exception.
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return str(self.message)
