"""Several expected exceptions in the front service."""


class FrontException(Exception):
    """Base exception for front exceptions."""


class ListensError(FrontException):
    """Exception raised upon encountering an error in the listens domain."""


class MusicError(FrontException):
    """Exception raised upon encountering an error in the music domain."""


class SunlightError(FrontException):
    """Exception raised upon encountering an error in the sunlight domain."""
