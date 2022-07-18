import requests


class HTTPRequestException(Exception):
    """HTTP error"""
    def __init__(self, response: requests.Response):
        super().__init__(f"HTTP request failed with status code: {response.status_code}")
