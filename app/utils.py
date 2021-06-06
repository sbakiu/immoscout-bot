def verify_secret(q, secret):
    """
    Verify the supplied secret is the one the application expects
    """
    return q == secret
