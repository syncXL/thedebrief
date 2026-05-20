# services/retry.py
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)
import logging
from google.genai.errors import ServerError, ClientError
from openrouter.errors import ResponseValidationError

logger = logging.getLogger(__name__)



llm_retry = retry(
    retry=retry_if_exception_type((
        ServerError,
        ClientError,
        ResponseValidationError,
    )),
    wait=wait_exponential(multiplier=2, min=50, max=120),  # respect the 48s retry delay
    stop=stop_after_attempt(5),
    before_sleep=before_sleep_log(logger, logging.WARNING))

