from app.domain.models.account import Account
from app.domain.models.athlete import AthleteProfile


class InMemoryAccountRepository:
    def __init__(self) -> None:
        self._accounts_by_id: dict[str, Account] = {}
        self._account_ids_by_email: dict[str, str] = {}

    def add(self, account: Account) -> None:
        self._accounts_by_id[account.account_id] = account
        self._account_ids_by_email[account.email] = account.account_id

    def get_by_email(self, email: str) -> Account | None:
        account_id = self._account_ids_by_email.get(email.lower())
        if account_id is None:
            return None
        return self._accounts_by_id.get(account_id)

    def get_by_id(self, account_id: str) -> Account | None:
        return self._accounts_by_id.get(account_id)


class InMemoryAthleteRepository:
    def __init__(self) -> None:
        self._athletes_by_account_id: dict[str, AthleteProfile] = {}

    def save(self, athlete: AthleteProfile) -> None:
        self._athletes_by_account_id[athlete.account_id] = athlete

    def get_by_account_id(self, account_id: str) -> AthleteProfile | None:
        return self._athletes_by_account_id.get(account_id)
