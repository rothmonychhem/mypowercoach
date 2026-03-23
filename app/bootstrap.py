from app.dependencies import get_account_service, get_database


TEST_ACCOUNTS = (
    ("coach@gmail.com", "coach123"),
    ("rothmony.chhem@gmail.com", "gym123"),
)


def bootstrap_application() -> None:
    database = get_database()
    database.initialize()

    account_service = get_account_service()
    for email, password in TEST_ACCOUNTS:
        account_service.ensure_seed_account(email=email, password=password)
