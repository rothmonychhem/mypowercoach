from typing import Protocol

from app.domain.models.athlete import AthleteProfile


class AthleteRepository(Protocol):
    def save(self, athlete: AthleteProfile) -> None: ...

    def get_by_account_id(self, account_id: str) -> AthleteProfile | None: ...
