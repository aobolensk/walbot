import requests


class HTTPRequestException(Exception):
    """HTTP request error"""

    def __init__(self, response: requests.Response):
        self.status_code = response.status_code
        super().__init__(f"HTTP request failed with status code: {response.status_code}")
