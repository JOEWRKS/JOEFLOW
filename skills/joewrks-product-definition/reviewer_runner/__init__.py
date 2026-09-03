"""Narrow, lazily loaded public API for isolated semantic-review execution."""

from importlib import import_module


_EXPORT_MODULES = {
    "RUNNER_CONTRACT_VERSION": "identity",
    "BackendDescriptor": "backend",
    "BackendEvent": "backend",
    "BackendIdentity": "identity",
    "BackendInvocationError": "backend",
    "BackendResponse": "backend",
    "BoundResponse": "response",
    "CanonicalRequest": "request",
    "CapabilityClass": "identity",
    "CapabilityObservation": "backend",
    "FrozenResponse": "response",
    "InputArtifact": "request",
    "InputCommitment": "identity",
    "IsolationReceipt": "preflight",
    "PreflightFreshness": "preflight",
    "PreflightResult": "preflight",
    "PreparedReview": "semantic_review",
    "ResponseIdentity": "identity",
    "RunIdentity": "identity",
    "RunOutcome": "controller",
    "RunnerReceipt": "identity",
    "RunnerState": "identity",
    "ToollessInferenceBackend": "backend",
    "execute_review": "controller",
    "prepare_semantic_review_v1": "semantic_review",
    "prepare_semantic_review_v21": "semantic_review",
}

__all__ = tuple(_EXPORT_MODULES)


def __getattr__(name: str):
    module_name = _EXPORT_MODULES.get(name)
    if module_name is None:
        raise AttributeError(name)
    value = getattr(import_module(f"{__name__}.{module_name}"), name)
    globals()[name] = value
    return value
