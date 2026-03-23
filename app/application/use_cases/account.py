from hashlib import sha256
from uuid import uuid4

from app.domain.models.account import Account
from app.domain.repositories.account_repository import AccountRepository


class AccountService:
    def __init__(self, account_repository: AccountRepository, password_salt: str) -> None:
        self._account_repository = account_repository
        self._password_salt = password_salt

    def register(self, email: str, password: str) -> Account:
        normalized_email = email.strip().lower()
        existing = self._account_repository.get_by_email(normalized_email)
        if existing is not None:
            raise ValueError("An account with that email already exists.")

        account = Account(
            account_id=str(uuid4()),
            email=normalized_email,
            password_hash=self._hash_password(password),
        )
        self._account_repository.save(account)
        return account

    def sign_in(self, email: str, password: str) -> Account:
        normalized_email = email.strip().lower()
        account = self._account_repository.get_by_email(normalized_email)
        if account is None:
            raise ValueError("No account was found for that email.")
        if account.password_hash != self._hash_password(password):
            raise ValueError("The password is incorrect.")
        return account

    def ensure_seed_account(self, email: str, password: str) -> Account:
        normalized_email = email.strip().lower()
        existing = self._account_repository.get_by_email(normalized_email)
        if existing is not None:
            return existing

        account = Account(
            account_id=str(uuid4()),
            email=normalized_email,
            password_hash=self._hash_password(password),
        )
        self._account_repository.save(account)
        return account

    def _hash_password(self, password: str) -> str:
        raw = f"{self._password_salt}:{password}".encode("utf-8")
        return sha256(raw).hexdigest()
