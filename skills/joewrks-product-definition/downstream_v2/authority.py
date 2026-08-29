"""Closed M4 authority admission for the parallel downstream V2 package."""

import hashlib
import json

from state_validation_v2 import evaluate_closure_v2


ACTION_CONTRACT_VERSION = "joewrks.action-conformance/2.0"
SEMANTIC_REVIEW_VERSION = "joewrks.semantic-review/2.0"
REENTRY_VERSION = "joewrks.product-definition-reentry/1.0"


class DownstreamV2Error(ValueError):
    def __init__(self, code: str, detail: object):
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":"))


def sha256_json(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def canonical_state_sha256(state: dict[str, object]) -> str:
    return sha256_json(state)


def require_closed_authority(state: dict[str, object]) -> dict[str, object]:
    """Return the fixed M4 authority envelope or reject without changing state."""
    try:
        closure = evaluate_closure_v2(state)
        project = state.get("project") if isinstance(state, dict) else None
        approval = state.get("approval") if isinstance(state, dict) else None
        if not isinstance(project, dict) or not isinstance(approval, dict):
            raise ValueError("missing authority controls")
        if not (
            state.get("schema_version") == "0.2.0"
            and closure.get("closed") is True
            and closure.get("errors") == []
            and closure.get("definition_digest") is not None
            and project.get("definition_status") == "CLOSED"
            and approval.get("status") == "APPROVED"
            and approval.get("approved_revision") == project.get("definition_revision")
            and approval.get("approved_definition_digest") == closure.get("definition_digest")
        ):
            raise ValueError("M4 closure is not current")
        contracts = project["closure_contract"]
        return {
            "state_schema_version": "0.2.0",
            "product_slug": project["slug"],
            "approved_revision": approval["approved_revision"],
            "approved_definition_digest": approval["approved_definition_digest"],
            "approved_manifest_digest": approval["approved_manifest_digest"],
            "product_binding_contract": contracts["product_binding_contract"],
            "ux_binding_contract": contracts["ux_binding_contract"],
            "snapshot_state_sha256": canonical_state_sha256(state),
        }
    except (KeyError, TypeError, ValueError, AttributeError) as error:
        raise DownstreamV2Error("PRODUCT_DEFINITION_NOT_CLOSED", str(error)) from error
