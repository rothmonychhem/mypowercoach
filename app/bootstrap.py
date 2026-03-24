from app.dependencies import get_account_service, get_database, get_exercise_repository
from app.domain.services.exercise_selector import (
    REQUIRED_SELECTOR_SLOTS,
    catalog_exercises,
    validate_catalog,
)


TEST_ACCOUNTS = (
    ("coach@gmail.com", "coach123"),
    ("rothmony.chhem@gmail.com", "gym123"),
)


def bootstrap_application() -> None:
    database = get_database()
    database.initialize()
    catalog_issues = validate_catalog()
    if catalog_issues:
        issue_summary = "; ".join(
            f"{slot_key}: {', '.join(messages)}"
            for slot_key, messages in catalog_issues.items()
        )
        raise RuntimeError(f"Exercise catalog is incomplete: {issue_summary}")

    exercise_repository = get_exercise_repository()
    exercise_repository.save_many(catalog_exercises())
    seeded_slots = set(exercise_repository.list_slot_keys())
    missing_slots = sorted(set(REQUIRED_SELECTOR_SLOTS) - seeded_slots)
    if missing_slots:
        raise RuntimeError(
            f"Exercise catalog seeding is incomplete. Missing selector slots: {', '.join(missing_slots)}"
        )

    account_service = get_account_service()
    for email, password in TEST_ACCOUNTS:
        account_service.ensure_seed_account(email=email, password=password)
