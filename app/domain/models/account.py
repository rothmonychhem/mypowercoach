from dataclasses import dataclass


@dataclass(slots=True)
class Account:
    account_id: str
    email: str
    password_hash: str
