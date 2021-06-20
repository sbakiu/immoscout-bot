def verify_secret(q: str, secret: str) -> bool:
    """
    Verify the supplied secret is the one the application expects
    """
    return q == secret
