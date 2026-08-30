"""Canonical field references shared by 2.1 review and runtime metadata."""

import re
from urllib.parse import quote, unquote_to_bytes


_COLLECTIONS = {"actions", "lifecycles"}
_FIELD_NAME = re.compile(r"^[^/\s]+$")


def encode_item_id(item_id: str) -> str:
    """Encode one exact item identity as an unambiguous UTF-8 path segment."""
    return quote(item_id, safe="", encoding="utf-8", errors="surrogatepass")


def canonical_field_ref(collection: str, item_id: str, field_name: str) -> str:
    """Return the canonical field reference for an exact contract item."""
    return f"{collection}/{encode_item_id(item_id)}/{field_name}"


def parse_canonical_field_ref(field_ref: object) -> tuple[str, str, str]:
    """Parse only the canonical encoding produced by ``canonical_field_ref``."""
    if not isinstance(field_ref, str):
        raise ValueError("INVALID_CANONICAL_FIELD_REFERENCE")
    parts = field_ref.split("/")
    if (
        len(parts) != 3
        or parts[0] not in _COLLECTIONS
        or not parts[1]
        or _FIELD_NAME.fullmatch(parts[2]) is None
    ):
        raise ValueError("INVALID_CANONICAL_FIELD_REFERENCE")
    try:
        item_id = unquote_to_bytes(parts[1]).decode(
            "utf-8",
            errors="surrogatepass",
        )
    except UnicodeDecodeError as error:
        raise ValueError("INVALID_CANONICAL_FIELD_REFERENCE") from error
    if encode_item_id(item_id) != parts[1]:
        raise ValueError("INVALID_CANONICAL_FIELD_REFERENCE")
    return parts[0], item_id, parts[2]


__all__ = [
    "canonical_field_ref",
    "encode_item_id",
    "parse_canonical_field_ref",
]
