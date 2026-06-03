"""
Custom Exception Target Subclasses for the Movie Search System.

Provides explicit, domain-specific semantic error structures used during
interactive user interface parameter checks and dataset limit validations.
"""

class YearError(Exception):
    """Raised when an entered year falls outside database min/max boundaries."""

class GenreError(Exception):
    """Raised when a selected genre does not exist within known records."""

class RatingError(Exception):
    """Raised when a specified film rating notation is unrecognized."""

class ActorError(Exception):
    """Raised when an actor's name combination is not found in the dataset."""

class YearIndex(Exception):
    """Raised when the end-year parameter chronologically precedes the start-year."""
