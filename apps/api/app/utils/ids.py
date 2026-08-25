import uuid


def generate_case_id() -> str:
    return (
        f"CASE-{uuid.uuid4().hex[:10].upper()}"
    )
