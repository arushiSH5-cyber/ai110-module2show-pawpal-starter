"""Tests for the PawPal+ logic layer (pawpal_system.py)."""

from datetime import date

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task

DAY = date(2026, 1, 31)  # a fixed day (end of month) keeps date math deterministic


def make_owner(minutes: int = 120) -> tuple[Owner, Pet, Pet]:
    owner = Owner("Jordan", available_minutes=minutes)
    mochi, luna = Pet("Mochi", "dog"), Pet("Luna", "cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)
    return owner, mochi, luna


def task(desc: str, time: str, minutes: int = 15, priority: str = "medium",
         frequency: str = "once", day: date = DAY) -> Task:
    return Task(desc, time, minutes, priority, frequency, due_date=day)


# ---- basics ---------------------------------------------------------------------------------

def test_mark_complete_changes_status():
    t = Task("Morning walk", "07:30")
    assert t.completed is False
    t.mark_complete()
    assert t.completed is True


def test_adding_task_increases_pet_task_count():
    pet = Pet("Mochi", "dog")
    assert len(pet.tasks) == 0
    pet.add_task(Task("Breakfast", "08:00"))
    assert len(pet.tasks) == 1
    assert pet.tasks[0].pet_name == "Mochi"


def test_owner_collects_tasks_from_all_pets():
    owner, mochi, luna = make_owner()
    mochi.add_task(task("Walk", "07:00"))
    luna.add_task(task("Pill", "09:00"))
    assert {t.description for t in owner.get_all_tasks()} == {"Walk", "Pill"}


def test_duplicate_pet_names_rejected_and_lookup_is_case_insensitive():
    owner, _, _ = make_owner()
    with pytest.raises(ValueError):
        owner.add_pet(Pet("mochi", "dog"))
    assert owner.get_pet("LUNA").name == "Luna"
    assert owner.get_pet("Rex") is None


def test_empty_cases():
    owner = Owner("Sam")
    s = Scheduler(owner)
    assert owner.get_all_tasks() == []
    assert s.get_todays_tasks(DAY) == []
    assert s.detect_conflicts([]) == []
    plan = s.plan_day(DAY)
    assert plan.scheduled == [] and plan.skipped == []
    owner.add_pet(Pet("Rex", "dog"))  # a pet with no tasks
    assert s.build_daily_plan(DAY) == []


@pytest.mark.parametrize("kwargs", [
    {"time": "25:00"}, {"time": "7.30"}, {"time": "noon"}, {"priority": "urgent"},
    {"frequency": "monthly"}, {"duration_minutes": 0},
])
def test_invalid_task_fields_rejected(kwargs):
    base = {"description": "x", "time": "08:00"}
    with pytest.raises(ValueError):
        Task(**(base | kwargs))


def test_time_is_normalized():
    assert Task("x", "7:05").time == "07:05"


# ---- sorting --------------------------------------------------------------------------------

def test_sort_by_time_is_chronological_not_alphabetical():
    tasks = [task("C", "18:00"), task("A", "9:00"), task("B", "10:30"), task("Z", "00:15")]
    assert [t.description for t in Scheduler.sort_by_time(tasks)] == ["Z", "A", "B", "C"]


def test_sort_by_time_keeps_insertion_order_for_ties():
    first, second = task("first", "08:00"), task("second", "08:00")
    assert Scheduler.sort_by_time([first, second]) == [first, second]


def test_sort_by_priority_then_time():
    tasks = [task("low early", "06:00", priority="low"),
             task("high late", "20:00", priority="high"),
             task("high early", "07:00", priority="high"),
             task("medium", "05:00", priority="medium")]
    assert [t.description for t in Scheduler.sort_by_priority(tasks)] == [
        "high early", "high late", "medium", "low early"]


# ---- filtering ------------------------------------------------------------------------------

def test_filter_by_pet_and_status():
    owner, mochi, luna = make_owner()
    walk, pill, play = task("Walk", "07:00"), task("Pill", "09:00"), task("Play", "18:00")
    mochi.add_task(walk)
    luna.add_task(pill)
    luna.add_task(play)
    pill.mark_complete()
    s = Scheduler(owner)
    assert s.filter_tasks(pet_name="luna") == [pill, play]
    assert s.filter_tasks(completed=True) == [pill]
    assert s.filter_tasks(pet_name="Luna", completed=False) == [play]
    assert s.filter_tasks() == [walk, pill, play]
    assert s.filter_tasks(pet_name="Rex") == []


# ---- recurring tasks ------------------------------------------------------------------------

def test_completing_daily_task_creates_next_day_task():
    owner, mochi, _ = make_owner()
    breakfast = task("Breakfast", "08:00", frequency="daily")
    mochi.add_task(breakfast)
    upcoming = Scheduler(owner).mark_task_complete(breakfast)
    assert breakfast.completed is True
    assert upcoming is not None and upcoming in mochi.tasks
    assert upcoming.due_date == date(2026, 2, 1)  # crosses the month boundary correctly
    assert upcoming.completed is False
    assert (upcoming.description, upcoming.time, upcoming.pet_name) == ("Breakfast", "08:00", "Mochi")
    assert len(mochi.tasks) == 2


def test_completing_weekly_task_creates_task_seven_days_later():
    owner, mochi, _ = make_owner()
    bath = task("Bath", "10:00", frequency="weekly")
    mochi.add_task(bath)
    assert Scheduler(owner).mark_task_complete(bath).due_date == date(2026, 2, 7)


def test_completing_one_off_task_creates_nothing():
    owner, mochi, _ = make_owner()
    vet = task("Vet", "10:00")
    mochi.add_task(vet)
    assert Scheduler(owner).mark_task_complete(vet) is None
    assert mochi.tasks == [vet] and vet.completed


def test_next_occurrence_is_independent_copy():
    t = task("Walk", "07:00", frequency="daily")
    nxt = t.next_occurrence()
    nxt.description = "changed"
    assert t.description == "Walk"


# ---- conflicts ------------------------------------------------------------------------------

def test_exact_same_time_is_flagged():
    owner, mochi, luna = make_owner()
    mochi.add_task(task("Walk", "09:00", 30))
    luna.add_task(task("Pill", "09:00", 5))
    warnings = Scheduler(owner).detect_conflicts(owner.get_all_tasks())
    assert len(warnings) == 1
    assert "Walk" in warnings[0] and "Pill" in warnings[0] and "Mochi and Luna" in warnings[0]


def test_partial_overlap_same_pet_is_flagged():
    owner, mochi, _ = make_owner()
    mochi.add_task(task("Walk", "08:00", 30))
    mochi.add_task(task("Groom", "08:20", 15))
    (warning,) = Scheduler(owner).detect_conflicts(owner.get_all_tasks())
    assert "both for Mochi" in warning


def test_back_to_back_tasks_do_not_conflict():
    owner, mochi, _ = make_owner()
    mochi.add_task(task("Walk", "08:00", 30))
    mochi.add_task(task("Breakfast", "08:30", 10))
    assert Scheduler(owner).detect_conflicts(owner.get_all_tasks()) == []


def test_conflicts_ignore_other_days_and_completed_tasks():
    owner, mochi, luna = make_owner()
    mochi.add_task(task("Walk", "08:00", 30))
    luna.add_task(task("Pill", "08:00", 5, day=date(2026, 2, 1)))
    done = task("Old walk", "08:10", 10)
    done.mark_complete()
    mochi.add_task(done)
    assert Scheduler(owner).detect_conflicts(owner.get_all_tasks()) == []


def test_three_overlapping_tasks_give_three_warnings():
    owner, mochi, _ = make_owner()
    for name in ("A", "B", "C"):
        mochi.add_task(task(name, "10:00", 20))
    assert len(Scheduler(owner).detect_conflicts(owner.get_all_tasks())) == 3


# ---- daily plan -----------------------------------------------------------------------------

def test_plan_prefers_high_priority_within_time_budget():
    owner, mochi, luna = make_owner(minutes=40)
    mochi.add_task(task("Play", "07:00", 30, "low"))
    mochi.add_task(task("Walk", "18:00", 30, "high"))
    luna.add_task(task("Pill", "09:00", 5, "high"))
    plan = Scheduler(owner).plan_day(DAY)
    assert [t.description for t in plan.scheduled] == ["Pill", "Walk"]  # time order
    assert [t.description for t in plan.skipped] == ["Play"]
    assert "only 5 min left" in plan.explain(plan.skipped[0])
    assert plan.minutes_used == 35


def test_plan_skips_completed_and_other_days():
    owner, mochi, _ = make_owner()
    done = task("Done", "07:00")
    done.mark_complete()
    mochi.add_task(done)
    mochi.add_task(task("Tomorrow", "07:00", day=date(2026, 2, 1)))
    mochi.add_task(task("Today", "08:00"))
    assert [t.description for t in Scheduler(owner).build_daily_plan(DAY)] == ["Today"]


def test_zero_budget_schedules_nothing():
    owner, mochi, _ = make_owner(minutes=0)
    mochi.add_task(task("Walk", "07:00"))
    plan = Scheduler(owner).plan_day(DAY)
    assert plan.scheduled == [] and len(plan.skipped) == 1


# ---- extensions: next available slot & JSON persistence -------------------------------------

def test_next_available_slot():
    owner, mochi, luna = make_owner()
    s = Scheduler(owner)
    assert s.next_available_slot(30, DAY) == "07:00"  # empty day
    mochi.add_task(task("Walk", "07:00", 30))
    luna.add_task(task("Pill", "07:40", 5))
    assert s.next_available_slot(10, DAY) == "07:30"  # fits the 10-minute gap
    assert s.next_available_slot(15, DAY) == "07:45"  # gap too small; goes after the pill
    assert s.next_available_slot(60, DAY, day_end="08:00") is None  # day is full


def test_next_slot_ignores_completed_tasks():
    owner, mochi, _ = make_owner()
    done = task("Walk", "07:00", 60)
    done.mark_complete()
    mochi.add_task(done)
    assert Scheduler(owner).next_available_slot(30, DAY) == "07:00"


def test_json_round_trip(tmp_path):
    owner, mochi, luna = make_owner(minutes=75)
    walk = task("Walk", "07:00", 30, "high", "daily")
    walk.task_type = "walk"
    walk.mark_complete()
    mochi.add_task(walk)
    luna.add_task(task("Pill", "09:00", 5, "high"))
    path = tmp_path / "data.json"
    owner.save_to_json(path)
    loaded = Owner.load_from_json(path)
    assert loaded.name == "Jordan" and loaded.available_minutes == 75
    assert [p.name for p in loaded.pets] == ["Mochi", "Luna"]
    assert loaded.get_all_tasks() == owner.get_all_tasks()  # dataclass equality: every field
    assert loaded.get_pet("Mochi").tasks[0].due_date == DAY


def test_load_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        Owner.load_from_json(tmp_path / "nope.json")
