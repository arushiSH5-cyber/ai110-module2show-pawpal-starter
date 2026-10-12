"""PawPal+ logic layer: owners, pets, care tasks, and the scheduler."""

from dataclasses import dataclass, field, replace
from datetime import date, timedelta

PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}
RECURRENCE = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}
FREQUENCIES = ("once", *RECURRENCE)


def to_minutes(hhmm: str) -> int:
    """Convert "HH:MM" (or "H:MM") to minutes after midnight; raises ValueError if invalid."""
    try:
        hours, minutes = (int(part) for part in hhmm.strip().split(":"))
    except ValueError:
        raise ValueError(f"Time must look like HH:MM, got {hhmm!r}") from None
    if not (0 <= hours < 24 and 0 <= minutes < 60):
        raise ValueError(f"Time out of range: {hhmm!r}")
    return hours * 60 + minutes


def to_hhmm(minutes: int) -> str:
    """Convert minutes after midnight back to zero-padded "HH:MM"."""
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


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

    def __post_init__(self) -> None:
        """Validate fields early so bad input fails loudly, not deep inside the scheduler."""
        self.time = to_hhmm(to_minutes(self.time))  # normalizes "7:30" -> "07:30"
        if self.priority not in PRIORITY_RANK:
            raise ValueError(f"priority must be one of {list(PRIORITY_RANK)}")
        if self.frequency not in FREQUENCIES:
            raise ValueError(f"frequency must be one of {list(FREQUENCIES)}")
        if self.duration_minutes <= 0:
            raise ValueError("duration_minutes must be positive")

    @property
    def start(self) -> int:
        """Start time in minutes after midnight."""
        return to_minutes(self.time)

    @property
    def end(self) -> int:
        """End time in minutes after midnight."""
        return self.start + self.duration_minutes

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def next_occurrence(self) -> "Task | None":
        """A fresh copy due on the next date for daily/weekly tasks; None for one-off tasks."""
        step = RECURRENCE.get(self.frequency)
        if step is None:
            return None
        return replace(self, due_date=self.due_date + step, completed=False)

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


@dataclass
class DailyPlan:
    """The result of planning a day: what fits, what was skipped, and why."""

    day: date
    scheduled: list[Task]
    skipped: list[Task]
    reasons: dict[int, str]  # id(task) -> explanation
    minutes_used: int
    minutes_available: int

    def explain(self, task: Task) -> str:
        """Why a task was scheduled or skipped."""
        return self.reasons.get(id(task), "")


class Scheduler:
    """The 'brain': retrieves, organizes, and manages tasks across all of an owner's pets."""

    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    # ---- retrieval --------------------------------------------------------------------------

    def get_todays_tasks(self, day: date | None = None) -> list[Task]:
        """All tasks due on the given day (default: today), across every pet."""
        day = day or date.today()
        return [t for t in self.owner.get_all_tasks() if t.due_date == day]

    # ---- sorting & filtering ----------------------------------------------------------------

    @staticmethod
    def sort_by_time(tasks: list[Task]) -> list[Task]:
        """Chronological order. Compares minutes, not strings, so "9:00" sorts before "10:00"."""
        return sorted(tasks, key=lambda t: t.start)

    @staticmethod
    def sort_by_priority(tasks: list[Task]) -> list[Task]:
        """High priority first; ties broken by time of day."""
        return sorted(tasks, key=lambda t: (PRIORITY_RANK[t.priority], t.start))

    def filter_tasks(
        self,
        tasks: list[Task] | None = None,
        pet_name: str | None = None,
        completed: bool | None = None,
    ) -> list[Task]:
        """Filter by pet name and/or completion status. None means "don't filter on this"."""
        tasks = self.owner.get_all_tasks() if tasks is None else tasks
        return [
            t
            for t in tasks
            if (pet_name is None or t.pet_name.lower() == pet_name.lower())
            and (completed is None or t.completed == completed)
        ]

    # ---- recurring tasks --------------------------------------------------------------------

    def mark_task_complete(self, task: Task) -> Task | None:
        """Complete a task; for daily/weekly tasks, add the next occurrence to the same pet."""
        task.mark_complete()
        upcoming = task.next_occurrence()
        if upcoming is None:
            return None
        pet = self.owner.get_pet(task.pet_name)
        if pet is None:
            raise ValueError(f"Task {task.description!r} is not attached to a known pet")
        pet.add_task(upcoming)
        return upcoming

    # ---- conflicts --------------------------------------------------------------------------

    def detect_conflicts(self, tasks: list[Task] | None = None) -> list[str]:
        """Warnings for tasks whose time windows overlap on the same day. Never raises.

        Compares every pair after sorting by start time and stops early once a later task
        starts after the current one ends, so typical days stay close to linear.
        """
        tasks = self.get_todays_tasks() if tasks is None else tasks
        pending = self.sort_by_time([t for t in tasks if not t.completed])
        warnings: list[str] = []
        for i, a in enumerate(pending):
            for b in pending[i + 1 :]:
                if b.start >= a.end:
                    break  # sorted: nothing later can overlap a
                if a.due_date != b.due_date:
                    continue
                who = (
                    f"both for {a.pet_name}"
                    if a.pet_name == b.pet_name
                    else f"{a.pet_name} and {b.pet_name} at once"
                )
                warnings.append(
                    f"⚠️ Conflict: '{a.description}' ({a.time}-{to_hhmm(a.end)}) overlaps "
                    f"'{b.description}' ({b.time}-{to_hhmm(b.end)}), {who}."
                )
        return warnings

    # ---- planning ---------------------------------------------------------------------------

    def plan_day(self, day: date | None = None) -> DailyPlan:
        """Choose today's tasks within the owner's available minutes.

        Greedy by priority (then time): high-priority care like meds and feeding is
        considered first; anything that no longer fits the time budget is skipped with a
        reason. The chosen tasks are returned in chronological order.
        """
        day = day or date.today()
        budget = self.owner.available_minutes
        used = 0
        scheduled: list[Task] = []
        skipped: list[Task] = []
        reasons: dict[int, str] = {}
        for task in self.sort_by_priority(self.filter_tasks(self.get_todays_tasks(day),
                                                            completed=False)):
            if used + task.duration_minutes <= budget:
                used += task.duration_minutes
                scheduled.append(task)
                reasons[id(task)] = (
                    f"{task.priority} priority; fits ({used}/{budget} min used)"
                )
            else:
                skipped.append(task)
                reasons[id(task)] = (
                    f"skipped: needs {task.duration_minutes} min but only "
                    f"{budget - used} min left today"
                )
        return DailyPlan(day, self.sort_by_time(scheduled), skipped, reasons, used, budget)

    def build_daily_plan(self, day: date | None = None) -> list[Task]:
        """Today's chosen tasks in time order (see plan_day for the reasoning)."""
        return self.plan_day(day).scheduled

    # ---- output -----------------------------------------------------------------------------

    def format_schedule(self, tasks: list[Task], title: str = "Today's Schedule") -> str:
        """Render tasks as a readable block of text for the terminal."""
        lines = [f"📅 {title} — {self.owner.name}", "-" * 56]
        lines += [t.label() for t in tasks] or ["(no tasks)"]
        return "\n".join(lines)
