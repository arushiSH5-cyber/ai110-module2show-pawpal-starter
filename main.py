"""CLI demo for PawPal+: builds an owner with two pets and prints today's schedule."""

from pawpal_system import Owner, Pet, Scheduler, Task


def build_demo_owner() -> Owner:
    """Create a sample owner, pets, and tasks."""
    owner = Owner("Jordan", available_minutes=90)
    mochi = Pet("Mochi", "dog", age=3)
    luna = Pet("Luna", "cat", age=5)
    owner.add_pet(mochi)
    owner.add_pet(luna)

    mochi.add_task(Task("Morning walk", "07:30", 30, "high", "daily", "walk"))
    mochi.add_task(Task("Breakfast", "08:15", 10, "high", "daily", "feeding"))
    luna.add_task(Task("Thyroid pill", "09:00", 5, "high", "daily", "medication"))
    luna.add_task(Task("Feather wand play", "18:00", 15, "low", "once", "enrichment"))
    return owner


def main() -> None:
    owner = build_demo_owner()
    scheduler = Scheduler(owner)
    print(scheduler.format_schedule(scheduler.build_daily_plan()))


if __name__ == "__main__":
    main()
