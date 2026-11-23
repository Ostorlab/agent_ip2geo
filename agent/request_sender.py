"""Module responsible for sending HTTP requests"""

import json
import logging
from typing import Any

import requests
import tenacity

logger = logging.getLogger(__name__)


class AuthenticationError(Exception):
    """Authentication Error."""


def _log_failed_request(retry_state: tenacity.RetryCallState) -> None:
    """Log the request that failed after all retries; the caller gets None."""
    exception = retry_state.outcome.exception() if retry_state.outcome else None
    logger.warning(
        "request %s failed after %i attempts: %s",
        retry_state.args,
        retry_state.attempt_number,
        exception,
    )


@tenacity.retry(
    stop=tenacity.stop.stop_after_attempt(3),
    wait=tenacity.wait.wait_fixed(2),
    retry=tenacity.retry_if_exception_type(Exception),
    retry_error_callback=_log_failed_request,
)
def make_request(method: str, path: str, data: dict[str, str] | None = None) -> Any:
    """Sends an HTTP request.
    Args:
        method: One of HTTP requests, e.g., GET, POST.
        path: Where to send the request to.
        data: Dictionary of data to be sent in the request.
    Returns:
        JSON response if status code is 200, None if it is 201 or 204.
    Raises:
        AuthenticationError if request is not successful.
    """
    logger.info("request %s %s %s", method, path, data)
    response = requests.request(method, path, data=json.dumps(data), timeout=10)
    if response.status_code not in [200, 201, 204]:
        logger.error("received %i %s", response.status_code, response.content)
        raise AuthenticationError(response.reason)
    elif response.status_code == 200:
        return response.json()
    else:
        return None
