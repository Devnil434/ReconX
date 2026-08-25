import hashlib
import hmac

from app.api.routes.webhooks import verify_signature


def test_valid_webhook_signature():
    secret = "test_webhook_secret_key"
    body = b'{"event": "payment.captured", "payload": {}}'
    sig = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()

    assert verify_signature(body, sig, secret) is True


def test_invalid_webhook_signature():
    secret = "test_webhook_secret_key"
    body = b'{"event": "payment.captured", "payload": {}}'
    invalid_sig = "deadbeef1234567890abcdef"

    assert verify_signature(body, invalid_sig, secret) is False
