def safe_domain_from_email(email: str) -> str | None:
    try:
        return email.split("@")[1] or None
    except (IndexError, AttributeError):
        return None
