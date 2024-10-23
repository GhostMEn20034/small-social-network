class InvalidTokenType(Exception):
    """Exception raised for invalid token type errors."""
    def __init__(self, expected_type: str, actual_type: str):
        self.expected_type = expected_type
        self.actual_type = actual_type
        super().__init__(f"Invalid token type: expected '{expected_type}', got '{actual_type}'.")
