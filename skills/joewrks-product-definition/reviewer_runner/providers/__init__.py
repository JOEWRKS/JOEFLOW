"""The one explicitly registered production inference adapter."""

from .anthropic import AnthropicBackend
from .anthropic_admission import (
    build_anthropic_backend_configuration,
    unprovisioned_anthropic_admission,
)


REGISTERED_PRODUCTION_ADAPTERS: tuple[AnthropicBackend, ...] = (
    AnthropicBackend(
        build_anthropic_backend_configuration(unprovisioned_anthropic_admission())
    ),
)


__all__ = ("REGISTERED_PRODUCTION_ADAPTERS",)
