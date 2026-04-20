"""Share vault variables via signed, time-limited export bundles."""

import json
import time
import hashlib
import hmac
from typing import Optional

SHARE_VERSION = 1
DEFAULT_TTL_SECONDS = 3600  # 1 hour


class ShareError(Exception):
    pass


def _sign(payload: str, secret: str) -> str:
    """Return an HMAC-SHA256 hex digest of payload using secret."""
    return hmac.new(
        secret.encode(), payload.encode(), hashlib.sha256
    ).hexdigest()


def create_bundle(
    variables: dict,
    secret: str,
    ttl: int = DEFAULT_TTL_SECONDS,
    label: Optional[str] = None,
) -> str:
    """Serialize variables into a signed JSON bundle string.

    Args:
        variables: Mapping of key -> value to share.
        secret: Shared secret used for signing.
        ttl: Seconds until the bundle expires.
        label: Optional human-readable label.

    Returns:
        A JSON string representing the signed bundle.
    """
    if not variables:
        raise ShareError("Cannot create a bundle with no variables.")

    payload = {
        "version": SHARE_VERSION,
        "created_at": time.time(),
        "expires_at": time.time() + ttl,
        "label": label or "",
        "variables": variables,
    }
    payload_str = json.dumps(payload, sort_keys=True)
    signature = _sign(payload_str, secret)
    bundle = {"payload": payload_str, "signature": signature}
    return json.dumps(bundle)


def open_bundle(bundle_str: str, secret: str) -> dict:
    """Verify and deserialize a signed bundle.

    Args:
        bundle_str: The JSON string produced by create_bundle.
        secret: Shared secret used for verification.

    Returns:
        The variables dict from the bundle.

    Raises:
        ShareError: If the signature is invalid or the bundle has expired.
    """
    try:
        bundle = json.loads(bundle_str)
        payload_str = bundle["payload"]
        signature = bundle["signature"]
    except (json.JSONDecodeError, KeyError) as exc:
        raise ShareError("Malformed bundle.") from exc

    expected = _sign(payload_str, secret)
    if not hmac.compare_digest(expected, signature):
        raise ShareError("Bundle signature is invalid.")

    payload = json.loads(payload_str)
    if time.time() > payload["expires_at"]:
        raise ShareError("Bundle has expired.")

    return payload["variables"]
