"""PawPal+ logic layer: owners, pets, care tasks, and the scheduler."""

from dataclasses import dataclass, field
from datetime import date

PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}
TASK_EMOJI = {
    "walk": "🦮",
    "feeding": "🍽️",
    "medication": "💊",
    "appointment": "🩺",
    "grooming": "✂️",
    "enrichment": "🧸",
    "other": "🐾",
}


@dataclass
class Task:
    """A single pet care activity scheduled at a time of day."""

    description: str
    time: str  # "HH:MM", 24-hour clock
    duration_minutes: int = 15
    priority: str = "medium"  # low | medium | high
    frequency: str = "once"  # once | daily | weekly
    task_type: str = "other"
    due_date: date = field(default_factory=date.today)
    completed: bool = False
    pet_name: str = ""  # set by Pet.add_task so merged schedules know whose task it is

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def label(self) -> str:
        """Return a short human-readable line for this task."""
        emoji = TASK_EMOJI.get(self.task_type, TASK_EMOJI["other"])
        status = "✅" if self.completed else "⬜"
        return (
            f"{status} {self.time}  {emoji} {self.description} "
            f"({self.pet_name}, {self.duration_minutes} min, {self.priority})"
        )


@dataclass
class Pet:
    """A pet and the care tasks that belong to it."""

    name: str
    species: str
    age: int = 0
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet and record the pet's name on it."""
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet if it is present."""
        if task in self.tasks:
            self.tasks.remove(task)


class Owner:
    """A pet owner who manages one or more pets and has limited time each day."""

    def __init__(self, name: str, available_minutes: int = 120) -> None:
        self.name = name
        self.available_minutes = available_minutes
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet; pet names must be unique for this owner."""
        if self.get_pet(pet.name) is not None:
            raise ValueError(f"{self.name} already has a pet named {pet.name}")
        self.pets.append(pet)

    def get_pet(self, name: str) -> Pet | None:
        """Find a pet by name (case-insensitive)."""
        return next((p for p in self.pets if p.name.lower() == name.lower()), None)

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]


class Scheduler:
    """The 'brain': retrieves, organizes, and manages tasks across all of an owner's pets."""

    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    def get_todays_tasks(self, day: date | None = None) -> list[Task]:
        """All tasks due on the given day (default: today), across every pet."""
        day = day or date.today()
        return [t for t in self.owner.get_all_tasks() if t.due_date == day]

    def build_daily_plan(self, day: date | None = None) -> list[Task]:
        """Today's tasks that still need doing."""
        return [t for t in self.get_todays_tasks(day) if not t.completed]

    def format_schedule(self, tasks: list[Task], title: str = "Today's Schedule") -> str:
        """Render tasks as a readable block of text for the terminal."""
        lines = [f"📅 {title} — {self.owner.name}", "-" * 56]
        lines += [t.label() for t in tasks] or ["(no tasks)"]
        return "\n".join(lines)
