# Project scaffold file
"""
LLM client for the AI Resume Screening & Interview System.

Responsibilities:
- Communicate with an LLM provider
- Support configurable API endpoints/models
- Handle authentication
- Retry transient failures
- Enforce request timeouts
- Generate plain-text responses
- Generate structured JSON responses
- Provide async support
- Keep provider-specific logic isolated
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Sequence

import httpx

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------
# Exceptions
# ----------------------------------------------------------------------


class LLMClientError(Exception):
    """Base exception for LLM client errors."""


class LLMConfigurationError(
    LLMClientError
):
    """Raised when LLM configuration is invalid."""


class LLMAuthenticationError(
    LLMClientError
):
    """Raised when authentication fails."""


class LLMRateLimitError(
    LLMClientError
):
    """Raised when the provider rate-limits the request."""


class LLMTimeoutError(
    LLMClientError
):
    """Raised when an LLM request times out."""


class LLMProviderError(
    LLMClientError
):
    """Raised when the provider returns an error."""


class LLMResponseError(
    LLMClientError
):
    """Raised when the provider response is invalid."""


# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------


@dataclass
class LLMConfig:
    """
    Runtime configuration for an LLM provider.

    The default API format is compatible with
    OpenAI-style /chat/completions endpoints.
    """

    api_key: str
    model: str

    base_url: str = (
        "https://api.openai.com/v1"
    )

    temperature: float = 0.2

    max_tokens: int = 2000

    timeout: float = 60.0

    max_retries: int = 3

    retry_delay: float = 1.0

    organization: Optional[str] = None

    headers: Dict[str, str] = field(
        default_factory=dict
    )

    def validate(self) -> None:
        if not self.api_key:
            raise LLMConfigurationError(
                "LLM API key is required."
            )

        if not self.model:
            raise LLMConfigurationError(
                "LLM model is required."
            )

        if not self.base_url:
            raise LLMConfigurationError(
                "LLM base URL is required."
            )

        if not 0 <= self.temperature <= 2:
            raise LLMConfigurationError(
                "Temperature must be between 0 and 2."
            )

        if self.max_tokens <= 0:
            raise LLMConfigurationError(
                "max_tokens must be greater than zero."
            )

        if self.timeout <= 0:
            raise LLMConfigurationError(
                "timeout must be greater than zero."
            )

        if self.max_retries < 0:
            raise LLMConfigurationError(
                "max_retries cannot be negative."
            )


# ----------------------------------------------------------------------
# Message
# ----------------------------------------------------------------------


@dataclass
class LLMMessage:
    """Represents a chat message."""

    role: str
    content: str

    def to_dict(self) -> Dict[str, str]:
        return {
            "role": self.role,
            "content": self.content,
        }


# ----------------------------------------------------------------------
# Response
# ----------------------------------------------------------------------


@dataclass
class LLMResponse:
    """Normalized LLM response."""

    content: str

    model: Optional[str] = None

    finish_reason: Optional[str] = None

    usage: Dict[str, Any] = field(
        default_factory=dict
    )

    raw_response: Dict[str, Any] = field(
        default_factory=dict
    )

    @property
    def prompt_tokens(self) -> int:
        return int(
            self.usage.get(
                "prompt_tokens",
                0,
            )
            or 0
        )

    @property
    def completion_tokens(self) -> int:
        return int(
            self.usage.get(
                "completion_tokens",
                0,
            )
            or 0
        )

    @property
    def total_tokens(self) -> int:
        return int(
            self.usage.get(
                "total_tokens",
                0,
            )
            or 0
        )


# ----------------------------------------------------------------------
# LLM Client
# ----------------------------------------------------------------------


class LLMClient:
    """
    Generic LLM client.

    Designed around OpenAI-compatible APIs so that the application
    can switch providers without changing the AI business logic.

    Example:

        config = LLMConfig(
            api_key="...",
            model="gpt-4.1-mini",
        )

        client = LLMClient(config)

        response = client.generate(
            system_prompt="You are a recruiter.",
            user_prompt="Analyze this resume.",
        )

        print(response.content)
    """

    def __init__(
        self,
        config: LLMConfig,
        client: Optional[
            httpx.Client
        ] = None,
        async_client: Optional[
            httpx.AsyncClient
        ] = None,
    ) -> None:

        config.validate()

        self.config = config

        self._client = client
        self._async_client = async_client

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(
        self,
        user_prompt: str,
        system_prompt: Optional[str] = None,
        messages: Optional[
            Sequence[
                Mapping[str, str]
            ]
        ] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[
            Dict[str, Any]
        ] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """
        Generate a response synchronously.
        """

        request_messages = (
            self._build_messages(
                user_prompt=user_prompt,
                system_prompt=system_prompt,
                messages=messages,
            )
        )

        payload = self._build_payload(
            messages=request_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=response_format,
            **kwargs,
        )

        return self._request(
            payload
        )

    async def agenerate(
        self,
        user_prompt: str,
        system_prompt: Optional[str] = None,
        messages: Optional[
            Sequence[
                Mapping[str, str]
            ]
        ] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[
            Dict[str, Any]
        ] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """
        Generate a response asynchronously.
        """

        request_messages = (
            self._build_messages(
                user_prompt=user_prompt,
                system_prompt=system_prompt,
                messages=messages,
            )
        )

        payload = self._build_payload(
            messages=request_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=response_format,
            **kwargs,
        )

        return await self._async_request(
            payload
        )

    def generate_text(
        self,
        user_prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """Convenience method returning only generated text."""

        response = self.generate(
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            **kwargs,
        )

        return response.content

    async def agenerate_text(
        self,
        user_prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """Async convenience method returning only text."""

        response = await self.agenerate(
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            **kwargs,
        )

        return response.content

    def generate_json(
        self,
        user_prompt: str,
        system_prompt: Optional[str] = None,
        schema: Optional[
            Dict[str, Any]
        ] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Generate and parse a JSON response.

        A JSON object is returned.
        """

        response_format = {
            "type": "json_object"
        }

        if schema:
            response_format = {
                "type": "json_schema",
                "json_schema": {
                    "name": "response",
                    "strict": True,
                    "schema": schema,
                },
            }

        response = self.generate(
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            response_format=response_format,
            **kwargs,
        )

        return self._parse_json(
            response.content
        )

    async def agenerate_json(
        self,
        user_prompt: str,
        system_prompt: Optional[str] = None,
        schema: Optional[
            Dict[str, Any]
        ] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Async JSON generation."""

        response_format = {
            "type": "json_object"
        }

        if schema:
            response_format = {
                "type": "json_schema",
                "json_schema": {
                    "name": "response",
                    "strict": True,
                    "schema": schema,
                },
            }

        response = await self.agenerate(
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            response_format=response_format,
            **kwargs,
        )

        return self._parse_json(
            response.content
        )

    # ------------------------------------------------------------------
    # Message Building
    # ------------------------------------------------------------------

    @staticmethod
    def _build_messages(
        user_prompt: str,
        system_prompt: Optional[str],
        messages: Optional[
            Sequence[
                Mapping[str, str]
            ]
        ],
    ) -> List[Dict[str, str]]:

        if messages:
            result = [
                {
                    "role": str(
                        message["role"]
                    ),
                    "content": str(
                        message["content"]
                    ),
                }
                for message in messages
            ]

            if system_prompt:
                result.insert(
                    0,
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                )

            if user_prompt:
                result.append(
                    {
                        "role": "user",
                        "content": user_prompt,
                    }
                )

            return result

        result = []

        if system_prompt:
            result.append(
                {
                    "role": "system",
                    "content": system_prompt,
                }
            )

        result.append(
            {
                "role": "user",
                "content": user_prompt,
            }
        )

        return result

    # ------------------------------------------------------------------
    # Payload
    # ------------------------------------------------------------------

    def _build_payload(
        self,
        messages: Sequence[
            Mapping[str, str]
        ],
        temperature: Optional[float],
        max_tokens: Optional[int],
        response_format: Optional[
            Dict[str, Any]
        ],
        **kwargs: Any,
    ) -> Dict[str, Any]:

        payload: Dict[str, Any] = {
            "model": self.config.model,
            "messages": list(messages),
            "temperature": (
                self.config.temperature
                if temperature is None
                else temperature
            ),
            "max_tokens": (
                self.config.max_tokens
                if max_tokens is None
                else max_tokens
            ),
        }

        if response_format:
            payload[
                "response_format"
            ] = response_format

        payload.update(
            kwargs
        )

        return payload

    # ------------------------------------------------------------------
    # Headers
    # ------------------------------------------------------------------

    def _headers(
        self,
    ) -> Dict[str, str]:

        headers = {
            "Authorization": (
                f"Bearer {self.config.api_key}"
            ),
            "Content-Type": (
                "application/json"
            ),
        }

        if self.config.organization:
            headers[
                "OpenAI-Organization"
            ] = self.config.organization

        headers.update(
            self.config.headers
        )

        return headers

    # ------------------------------------------------------------------
    # URL
    # ------------------------------------------------------------------

    def _endpoint(
        self,
    ) -> str:

        base = (
            self.config.base_url
            .rstrip("/")
        )

        return (
            f"{base}/chat/completions"
        )

    # ------------------------------------------------------------------
    # Sync Request
    # ------------------------------------------------------------------

    def _request(
        self,
        payload: Dict[str, Any],
    ) -> LLMResponse:

        last_error: Optional[
            Exception
        ] = None

        for attempt in range(
            self.config.max_retries + 1
        ):

            try:

                if self._client:
                    response = self._client.post(
                        self._endpoint(),
                        headers=self._headers(),
                        json=payload,
                        timeout=self.config.timeout,
                    )

                else:
                    with httpx.Client(
                        timeout=self.config.timeout
                    ) as client:

                        response = client.post(
                            self._endpoint(),
                            headers=self._headers(),
                            json=payload,
                        )

                return self._handle_response(
                    response
                )

            except LLMAuthenticationError:
                raise

            except LLMResponseError:
                raise

            except LLMRateLimitError as exc:
                last_error = exc

                if attempt >= self.config.max_retries:
                    raise

                self._sleep(
                    attempt
                )

            except LLMTimeoutError as exc:
                last_error = exc

                if attempt >= self.config.max_retries:
                    raise

                self._sleep(
                    attempt
                )

            except (
                httpx.HTTPError,
                LLMProviderError,
            ) as exc:

                last_error = exc

                if attempt >= self.config.max_retries:
                    raise LLMProviderError(
                        str(exc)
                    ) from exc

                self._sleep(
                    attempt
                )

        raise LLMClientError(
            "LLM request failed."
        ) from last_error

    # ------------------------------------------------------------------
    # Async Request
    # ------------------------------------------------------------------

    async def _async_request(
        self,
        payload: Dict[str, Any],
    ) -> LLMResponse:

        last_error: Optional[
            Exception
        ] = None

        for attempt in range(
            self.config.max_retries + 1
        ):

            try:

                if self._async_client:
                    response = (
                        await self._async_client.post(
                            self._endpoint(),
                            headers=self._headers(),
                            json=payload,
                            timeout=self.config.timeout,
                        )
                    )

                else:
                    async with httpx.AsyncClient(
                        timeout=self.config.timeout
                    ) as client:

                        response = (
                            await client.post(
                                self._endpoint(),
                                headers=self._headers(),
                                json=payload,
                            )
                        )

                return self._handle_response(
                    response
                )

            except LLMAuthenticationError:
                raise

            except LLMResponseError:
                raise

            except LLMRateLimitError as exc:
                last_error = exc

                if attempt >= self.config.max_retries:
                    raise

                await self._async_sleep(
                    attempt
                )

            except LLMTimeoutError as exc:
                last_error = exc

                if attempt >= self.config.max_retries:
                    raise

                await self._async_sleep(
                    attempt
                )

            except (
                httpx.HTTPError,
                LLMProviderError,
            ) as exc:

                last_error = exc

                if attempt >= self.config.max_retries:
                    raise LLMProviderError(
                        str(exc)
                    ) from exc

                await self._async_sleep(
                    attempt
                )

        raise LLMClientError(
            "LLM request failed."
        ) from last_error

    # ------------------------------------------------------------------
    # Response Handling
    # ------------------------------------------------------------------

    def _handle_response(
        self,
        response: httpx.Response,
    ) -> LLMResponse:

        if response.status_code == 401:
            raise LLMAuthenticationError(
                "LLM authentication failed."
            )

        if response.status_code == 429:
            retry_after = (
                response.headers.get(
                    "Retry-After"
                )
            )

            message = (
                "LLM provider rate limit exceeded."
            )

            if retry_after:
                message += (
                    f" Retry after {retry_after} seconds."
                )

            raise LLMRateLimitError(
                message
            )

        if response.status_code >= 500:
            raise LLMProviderError(
                self._extract_error_message(
                    response
                )
            )

        if response.status_code >= 400:
            raise LLMProviderError(
                self._extract_error_message(
                    response
                )
            )

        try:
            data = response.json()

        except ValueError as exc:
            raise LLMResponseError(
                "LLM returned invalid JSON."
            ) from exc

        return self._parse_response(
            data
        )

    # ------------------------------------------------------------------
    # Response Parsing
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_response(
        data: Mapping[str, Any],
    ) -> LLMResponse:

        try:
            choices = data[
                "choices"
            ]

            if not choices:
                raise LLMResponseError(
                    "LLM response contains no choices."
                )

            first_choice = choices[0]

            message = first_choice.get(
                "message",
                {},
            )

            content = message.get(
                "content"
            )

            if content is None:
                raise LLMResponseError(
                    "LLM response contains no content."
                )

            return LLMResponse(
                content=str(
                    content
                ),
                model=data.get(
                    "model"
                ),
                finish_reason=first_choice.get(
                    "finish_reason"
                ),
                usage=dict(
                    data.get(
                        "usage",
                        {},
                    )
                    or {}
                ),
                raw_response=dict(
                    data
                ),
            )

        except KeyError as exc:

            raise LLMResponseError(
                f"Invalid LLM response: missing {exc}"
            ) from exc

    # ------------------------------------------------------------------
    # JSON Parsing
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_json(
        content: str,
    ) -> Dict[str, Any]:

        cleaned = (
            content.strip()
        )

        # Remove markdown code fences if a model
        # returns them despite JSON mode.
        if cleaned.startswith(
            "```"
        ):

            lines = (
                cleaned.splitlines()
            )

            if lines:
                lines = lines[1:]

            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            cleaned = "\n".join(
                lines
            ).strip()

        try:
            result = json.loads(
                cleaned
            )

        except json.JSONDecodeError as exc:

            raise LLMResponseError(
                "LLM returned invalid JSON."
            ) from exc

        if not isinstance(
            result,
            dict,
        ):
            raise LLMResponseError(
                "Expected a JSON object from the LLM."
            )

        return result

    # ------------------------------------------------------------------
    # Error Extraction
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_error_message(
        response: httpx.Response,
    ) -> str:

        try:
            data = response.json()

            error = data.get(
                "error",
                data,
            )

            if isinstance(
                error,
                Mapping,
            ):
                message = error.get(
                    "message"
                )

                if message:
                    return str(
                        message
                    )

            return json.dumps(
                data
            )

        except (
            ValueError,
            TypeError,
        ):
            return (
                response.text
                or "Unknown LLM provider error."
            )

    # ------------------------------------------------------------------
    # Retry Helpers
    # ------------------------------------------------------------------

    def _sleep(
        self,
        attempt: int,
    ) -> None:

        delay = (
            self.config.retry_delay
            * (2**attempt)
        )

        # Prevent excessive retry delays.
        delay = min(
            delay,
            30.0,
        )

        logger.warning(
            "Retrying LLM request in %.2f seconds.",
            delay,
        )

        time.sleep(
            delay
        )

    async def _async_sleep(
        self,
        attempt: int,
    ) -> None:

        delay = (
            self.config.retry_delay
            * (2**attempt)
        )

        delay = min(
            delay,
            30.0,
        )

        logger.warning(
            "Retrying LLM request in %.2f seconds.",
            delay,
        )

        await asyncio.sleep(
            delay
        )

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def close(self) -> None:
        """Close a client supplied to the LLMClient."""

        if self._client:
            self._client.close()

    async def aclose(self) -> None:
        """Close an async client supplied to the LLMClient."""

        if self._async_client:
            await self._async_client.aclose()


# ----------------------------------------------------------------------
# Factory
# ----------------------------------------------------------------------


def create_llm_client(
    api_key: str,
    model: str,
    base_url: str = (
        "https://api.openai.com/v1"
    ),
    temperature: float = 0.2,
    max_tokens: int = 2000,
    timeout: float = 60.0,
    max_retries: int = 3,
    **kwargs: Any,
) -> LLMClient:
    """
    Create an LLM client from configuration values.
    """

    config = LLMConfig(
        api_key=api_key,
        model=model,
        base_url=base_url,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=timeout,
        max_retries=max_retries,
        **kwargs,
    )

    return LLMClient(
        config
    )


__all__ = [
    "LLMConfig",
    "LLMMessage",
    "LLMResponse",
    "LLMClient",
    "LLMClientError",
    "LLMConfigurationError",
    "LLMAuthenticationError",
    "LLMRateLimitError",
    "LLMTimeoutError",
    "LLMProviderError",
    "LLMResponseError",
    "create_llm_client",
]