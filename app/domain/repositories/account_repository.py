from typing import Protocol

from app.domain.models.account import Account


class AccountRepository(Protocol):
    def save(self, account: Account) -> None: ...

    def get_by_email(self, email: str) -> Account | None: ...

    def get_by_id(self, account_id: str) -> Account | None: ...
