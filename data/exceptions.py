class BedRequestError(Exception):
    """Processing an exception when requesting an API."""

    def __init__(self, message, response):
        """Initialization sending Exception."""
        self.message = message
        self.response_status = response.status_code
        super().__init__(self.message)

    def __str__(self):
        """Display."""
        return f'{self.message} {self.response_status}'


class IncorrectDataError(Exception):
    """Exception handling with API response data."""

    pass


class StatusHomeworkError(Exception):
    """Exceptions caused during data parsing."""

    pass
