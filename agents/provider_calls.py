"""Provider selection and generation helpers for review-stage agents."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Literal, cast

from anthropic import Anthropic
from google import genai
from google.genai import types
from openai import OpenAI

from utils.attachments import (
    PreparedAttachment,
    data_url_for_attachment,
    model_image_attachments,
)
from utils.config import Settings

ProviderName = Literal["openai", "anthropic", "gemini"]

AUTO_PROVIDER_ORDER: tuple[ProviderName, ...] = ("openai", "anthropic", "gemini")
PROVIDER_ENV_VARS = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "gemini": "GEMINI_API_KEY",
}


def provider_env_var(provider: str) -> str:
    """Return the API-key environment variable for a provider."""

    return PROVIDER_ENV_VARS.get(provider, "OPENAI_API_KEY")


def has_provider_key(settings: Settings, provider: ProviderName) -> bool:
    """Return whether a provider has a usable API key."""

    if provider == "openai":
        return bool(settings.openai_api_key)
    if provider == "anthropic":
        return bool(settings.anthropic_api_key)
    if provider == "gemini":
        return bool(settings.gemini_api_key)
    return False


def available_providers(settings: Settings) -> tuple[ProviderName, ...]:
    """Return configured providers in automatic fallback order."""

    return tuple(
        provider
        for provider in AUTO_PROVIDER_ORDER
        if has_provider_key(settings, provider)
    )


def resolve_provider_sequence(
    settings: Settings,
    requested_provider: str,
) -> tuple[ProviderName, ...]:
    """Return the provider sequence to try for a review-stage call."""

    if requested_provider == "auto":
        return available_providers(settings)
    if requested_provider not in PROVIDER_ENV_VARS:
        return available_providers(settings)

    provider = cast(ProviderName, requested_provider)
    if has_provider_key(settings, provider):
        return (provider,)
    return ()


def missing_any_provider_message() -> str:
    """Return a clear message when no review provider can run."""

    return (
        "缺少可用 API Key，请至少在 .env 文件中配置 "
        "OPENAI_API_KEY、ANTHROPIC_API_KEY 或 GEMINI_API_KEY。"
    )


def gemini_retry_attempts(provider_max_retries: int) -> int:
    """Convert retry count into Gemini HTTP attempts including the first request."""

    return max(1, provider_max_retries + 1)


def build_openai_user_content(
    user_prompt: str,
    attachments: Sequence[PreparedAttachment] | None = None,
) -> Any:
    """Build OpenAI Responses content with optional image inputs."""

    image_attachments = model_image_attachments(attachments, provider="openai")
    if not image_attachments:
        return user_prompt

    return [
        {"type": "input_text", "text": user_prompt},
        *[
            {
                "type": "input_image",
                "image_url": data_url_for_attachment(attachment),
            }
            for attachment in image_attachments
        ],
    ]


def build_anthropic_user_content(
    user_prompt: str,
    attachments: Sequence[PreparedAttachment] | None = None,
) -> Any:
    """Build Anthropic Messages content with optional image inputs."""

    image_attachments = model_image_attachments(attachments, provider="anthropic")
    if not image_attachments:
        return user_prompt

    return [
        {"type": "text", "text": user_prompt},
        *[
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": attachment.mime_type,
                    "data": data_url_for_attachment(attachment).split(",", maxsplit=1)[
                        1
                    ],
                },
            }
            for attachment in image_attachments
        ],
    ]


def build_gemini_contents(
    user_prompt: str,
    attachments: Sequence[PreparedAttachment] | None = None,
) -> Any:
    """Build Gemini contents with optional image parts."""

    image_attachments = model_image_attachments(attachments, provider="gemini")
    if not image_attachments:
        return user_prompt

    return [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=user_prompt),
                *[
                    types.Part.from_bytes(
                        data=attachment.content,
                        mime_type=attachment.mime_type,
                    )
                    for attachment in image_attachments
                ],
            ],
        )
    ]


def generate_with_provider(
    *,
    settings: Settings,
    provider: ProviderName,
    system_prompt: str,
    user_prompt: str,
) -> str:
    """Generate text with the selected provider."""

    if provider == "openai":
        openai_client = OpenAI(
            api_key=settings.openai_api_key,
            timeout=settings.request_timeout_seconds,
            max_retries=settings.provider_max_retries,
        )
        openai_response = openai_client.responses.create(
            model=settings.openai_model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_output_tokens=settings.max_output_tokens,
        )
        return openai_response.output_text.strip()

    if provider == "anthropic":
        anthropic_client = Anthropic(
            api_key=settings.anthropic_api_key,
            timeout=settings.request_timeout_seconds,
            max_retries=settings.provider_max_retries,
        )
        anthropic_response = anthropic_client.messages.create(
            model=settings.claude_model,
            max_tokens=settings.max_output_tokens,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": user_prompt,
                }
            ],
        )
        return "".join(
            block.text for block in anthropic_response.content if block.type == "text"
        ).strip()

    gemini_client = genai.Client(
        api_key=settings.gemini_api_key,
        http_options=types.HttpOptions(
            timeout=int(settings.request_timeout_seconds * 1000),
            retry_options=types.HttpRetryOptions(
                attempts=gemini_retry_attempts(settings.provider_max_retries),
            ),
        ),
    )
    gemini_response = gemini_client.models.generate_content(
        model=settings.gemini_model,
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            max_output_tokens=settings.max_output_tokens,
        ),
    )
    response_text = gemini_response.text
    if isinstance(response_text, str):
        return response_text.strip()
    return ""
