# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🧩 Implementation Summary

PawPal+ keeps its logic in `pawpal_system.py`, separate from the Streamlit UI:

- **`Task`** (dataclass): one care activity, with a description, `HH:MM` time, duration, priority, frequency, type, due date and completion status. `mark_complete()` flips its status.
- **`Pet`** (dataclass): a pet's details plus its list of tasks. `add_task()` also stamps the pet's name on the task, so merged schedules know whose task it is.
- **`Owner`**: holds several pets and the minutes available per day. `get_all_tasks()` returns every pet's tasks together.
- **`Scheduler`**: the "brain". It reads tasks only through `Owner.get_all_tasks()`, so it works across all pets, then picks today's tasks and formats the schedule.

`main.py` is a CLI demo that builds an owner with two pets and prints today's schedule.

## 🖥️ Sample Output

Output of `python main.py`:

```
📅 Today's Schedule — Jordan
--------------------------------------------------------
⬜ 07:30  🦮 Morning walk (Mochi, 30 min, high)
⬜ 08:15  🍽️ Breakfast (Mochi, 10 min, high)
⬜ 09:00  💊 Thyroid pill (Luna, 5 min, high)
⬜ 18:00  🧸 Feather wand play (Luna, 15 min, low)
```

## 🧪 Testing PawPal+

```bash
python -m pytest        # add -v to see each test name
```

`tests/test_pawpal.py` has 28 tests covering:

- **Core classes**: `mark_complete()`, adding tasks to a pet, `Owner.get_all_tasks()` across pets, duplicate pet names, case-insensitive pet lookup, and input validation (bad times, priorities, frequencies, durations).
- **Sorting**: chronological order (`"9:00"` before `"10:30"`, which plain string sorting gets wrong), stable order for ties, and priority-then-time.
- **Filtering**: by pet, by completion status, by both, and an unknown pet.
- **Recurrence**: a daily task completed on Jan 31 creates a fresh, incomplete copy for Feb 1 (month boundary); weekly adds 7 days; one-off tasks create nothing; the new task is an independent copy.
- **Conflicts**: exact same time, partial overlap for the same pet, back-to-back tasks that touch but don't overlap, other days and completed tasks ignored, and three tasks at once giving three warnings.
- **Daily plan**: high priority wins within the time budget, skipped tasks are explained, completed and future tasks are excluded, and a zero budget schedules nothing.
- **Edge cases**: an owner with no pets and a pet with no tasks.

To check the tests themselves, I temporarily broke the code three ways (string-based time sort, back-to-back counted as a conflict, a recurring copy left marked complete). Each change made the matching test fail.

Sample test output:

```
============================= test session starts ==============================
configfile: pytest.ini
testpaths: tests
collecting ... collected 28 items

tests/test_pawpal.py::test_mark_complete_changes_status PASSED           [  3%]
tests/test_pawpal.py::test_adding_task_increases_pet_task_count PASSED   [  7%]
tests/test_pawpal.py::test_owner_collects_tasks_from_all_pets PASSED     [ 10%]
tests/test_pawpal.py::test_duplicate_pet_names_rejected_and_lookup_is_case_insensitive PASSED [ 14%]
tests/test_pawpal.py::test_empty_cases PASSED                            [ 17%]
tests/test_pawpal.py::test_invalid_task_fields_rejected[kwargs0] PASSED  [ 21%]
tests/test_pawpal.py::test_invalid_task_fields_rejected[kwargs1] PASSED  [ 25%]
tests/test_pawpal.py::test_invalid_task_fields_rejected[kwargs2] PASSED  [ 28%]
tests/test_pawpal.py::test_invalid_task_fields_rejected[kwargs3] PASSED  [ 32%]
tests/test_pawpal.py::test_invalid_task_fields_rejected[kwargs4] PASSED  [ 35%]
tests/test_pawpal.py::test_invalid_task_fields_rejected[kwargs5] PASSED  [ 39%]
tests/test_pawpal.py::test_time_is_normalized PASSED                     [ 42%]
tests/test_pawpal.py::test_sort_by_time_is_chronological_not_alphabetical PASSED [ 46%]
tests/test_pawpal.py::test_sort_by_time_keeps_insertion_order_for_ties PASSED [ 50%]
tests/test_pawpal.py::test_sort_by_priority_then_time PASSED             [ 53%]
tests/test_pawpal.py::test_filter_by_pet_and_status PASSED               [ 57%]
tests/test_pawpal.py::test_completing_daily_task_creates_next_day_task PASSED [ 60%]
tests/test_pawpal.py::test_completing_weekly_task_creates_task_seven_days_later PASSED [ 64%]
tests/test_pawpal.py::test_completing_one_off_task_creates_nothing PASSED [ 67%]
tests/test_pawpal.py::test_next_occurrence_is_independent_copy PASSED    [ 71%]
tests/test_pawpal.py::test_exact_same_time_is_flagged PASSED             [ 75%]
tests/test_pawpal.py::test_partial_overlap_same_pet_is_flagged PASSED    [ 78%]
tests/test_pawpal.py::test_back_to_back_tasks_do_not_conflict PASSED     [ 82%]
tests/test_pawpal.py::test_conflicts_ignore_other_days_and_completed_tasks PASSED [ 85%]
tests/test_pawpal.py::test_three_overlapping_tasks_give_three_warnings PASSED [ 89%]
tests/test_pawpal.py::test_plan_prefers_high_priority_within_time_budget PASSED [ 92%]
tests/test_pawpal.py::test_plan_skips_completed_and_other_days PASSED    [ 96%]
tests/test_pawpal.py::test_zero_budget_schedules_nothing PASSED          [100%]

============================== 28 passed in 0.03s ==============================
```

**Confidence level: ★★★★☆ (4/5).** Every scheduling rule above is tested, including the edge cases where it's easiest to slip up. It isn't 5/5 because the Streamlit UI is only checked by hand and with Streamlit's `AppTest`, not in the suite. The greedy planner can also leave unused minutes that a different combination of tasks would have filled.

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()`, `Scheduler.sort_by_priority()` | Sorts by minutes after midnight (via `Task.start`), not raw strings, so `"8:15"` comes before `"10:00"`. Priority sort: high → medium → low, then by time. |
| Filtering | `Scheduler.filter_tasks(tasks, pet_name=..., completed=...)` | Filter by pet (case-insensitive) and/or completion status; `None` means "don't filter on this". |
| Conflict handling | `Scheduler.detect_conflicts()` | Flags tasks whose **time windows overlap** (start + duration) on the same day, whether for the same pet or for different pets (one owner can't be in two places). Returns warning strings and never raises. Sorting first lets it stop early per task. |
| Recurring tasks | `Task.next_occurrence()`, `Scheduler.mark_task_complete()` | Completing a `daily` or `weekly` task automatically adds a fresh copy to the same pet, due `today + timedelta(days=1)` or `weeks=1`. One-off tasks just complete. |
| Daily plan within time budget | `Scheduler.plan_day()` → `DailyPlan` (`build_daily_plan()` returns just the tasks) | Greedy: considers high-priority tasks first and keeps each one that still fits the owner's `available_minutes`. Skipped tasks get a reason (`DailyPlan.explain()`), and the chosen tasks are shown in time order. |
| Input validation | `Task.__post_init__`, `to_minutes()` | Rejects bad times (`"25:00"`), priorities, frequencies and durations; normalizes `"7:30"` to `"07:30"`. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
