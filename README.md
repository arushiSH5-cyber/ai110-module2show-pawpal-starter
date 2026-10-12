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
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | | e.g., by priority, duration |
| Filtering | | e.g., skip tasks if time runs out |
| Conflict handling | | e.g., overlapping time slots |
| Recurring tasks | | e.g., daily vs. weekly |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
