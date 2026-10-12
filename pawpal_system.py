"""PawPal+ logic layer: owners, pets, care tasks, and the scheduler."""

from dataclasses import dataclass, field
from datetime import date


@dataclass
class Task:
    description: str
    time: str  # "HH:MM"
    duration_minutes: int = 15
    priority: str = "medium"  # low | medium | high
    frequency: str = "once"  # once | daily | weekly
    due_date: date = field(default_factory=date.today)
    completed: bool = False

    def mark_complete(self) -> None:
        raise NotImplementedError


@dataclass
class Pet:
    name: str
    species: str
    age: int = 0
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        raise NotImplementedError

    def remove_task(self, task: Task) -> None:
        raise NotImplementedError


class Owner:
    def __init__(self, name: str, available_minutes: int = 120) -> None:
        self.name = name
        self.available_minutes = available_minutes
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        raise NotImplementedError

    def get_pet(self, name: str) -> Pet | None:
        raise NotImplementedError

    def get_all_tasks(self) -> list[Task]:
        raise NotImplementedError


class Scheduler:
    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    def get_todays_tasks(self) -> list[Task]:
        raise NotImplementedError

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        raise NotImplementedError

    def filter_tasks(self, pet_name: str | None = None, completed: bool | None = None) -> list[Task]:
        raise NotImplementedError

    def detect_conflicts(self, tasks: list[Task]) -> list[str]:
        raise NotImplementedError

    def build_daily_plan(self) -> list[Task]:
        raise NotImplementedError
