"""Exception hierarchy for pyairkorea."""

from __future__ import annotations


class AirKoreaError(Exception):
    """Base exception for all pyairkorea errors."""


class AirKoreaAuthError(AirKoreaError):
    """Authentication failed or the service key is missing/invalid."""


class AirKoreaRequestError(AirKoreaError):
    """The request parameters are invalid or the API rejected the request."""


class AirKoreaNoDataError(AirKoreaRequestError):
    """The API returned its no-data result code."""


class AirKoreaRateLimitError(AirKoreaRequestError):
    """The API rejected the request due to quota or rate limits."""


class AirKoreaNetworkError(AirKoreaError):
    """A network error occurred while calling AirKorea."""


class AirKoreaServerError(AirKoreaError):
    """AirKorea returned a server-side or otherwise transient failure."""


class AirKoreaParseError(AirKoreaError):
    """An AirKorea response could not be parsed into the expected structure."""
