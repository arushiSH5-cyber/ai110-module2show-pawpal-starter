"""CLI demo for PawPal+: sorting, filtering, recurring tasks, conflicts, and daily planning."""

from pawpal_system import Owner, Pet, Scheduler, Task


def build_demo_owner() -> Owner:
    """Create a sample owner with two pets; tasks are added out of time order on purpose."""
    owner = Owner("Jordan", available_minutes=90)
    mochi = Pet("Mochi", "dog", age=3)
    luna = Pet("Luna", "cat", age=5)
    owner.add_pet(mochi)
    owner.add_pet(luna)

    luna.add_task(Task("Feather wand play", "18:00", 15, "low", "once", "enrichment"))
    mochi.add_task(Task("Breakfast", "8:15", 10, "high", "daily", "feeding"))
    luna.add_task(Task("Thyroid pill", "09:00", 5, "high", "daily", "medication"))
    mochi.add_task(Task("Morning walk", "07:30", 30, "high", "daily", "walk"))
    mochi.add_task(Task("Vet check-up", "09:00", 45, "medium", "once", "appointment"))
    mochi.add_task(Task("Brush coat", "19:30", 20, "low", "weekly", "grooming"))
    return owner


def section(title: str) -> None:
    print(f"\n=== {title} ===")


def main() -> None:
    owner = build_demo_owner()
    scheduler = Scheduler(owner)
    today = scheduler.get_todays_tasks()

    section("Tasks as added (unsorted)")
    for t in today:
        print(t.label())

    section("Sorted by time")
    print(scheduler.format_schedule(scheduler.sort_by_time(today)))

    section("Filtered: Luna only")
    for t in scheduler.sort_by_time(scheduler.filter_tasks(today, pet_name="Luna")):
        print(t.label())

    section("Conflict check")
    for warning in scheduler.detect_conflicts(today) or ["No conflicts 🎉"]:
        print(warning)

    section("Recurring task: complete Mochi's breakfast")
    breakfast = next(t for t in today if t.description == "Breakfast")
    upcoming = scheduler.mark_task_complete(breakfast)
    print(f"Done: {breakfast.label()}")
    print(f"Next one created for {upcoming.due_date.isoformat()}: {upcoming.label()}")

    section("Filtered: still to do today")
    for t in scheduler.sort_by_time(scheduler.filter_tasks(today, completed=False)):
        print(t.label())

    section(f"Daily plan (priority first, {owner.available_minutes} min available)")
    plan = scheduler.plan_day()
    print(scheduler.format_schedule(plan.scheduled, "Today's Plan"))
    for t in plan.scheduled:
        print(f"  • {t.description}: {plan.explain(t)}")
    for t in plan.skipped:
        print(f"  ✗ {t.description}: {plan.explain(t)}")


if __name__ == "__main__":
    main()
