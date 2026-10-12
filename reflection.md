# PawPal+ Project Reflection

> **How this reflection was written:** I built PawPal+ with Claude Code, an AI coding agent, in a single session. I asked the agent to draft this reflection from what actually happened in that session: my prompts, its work, and the checks it ran. I then reviewed it. Nothing below describes steps that didn't happen.

## 1. System Design

**a. Initial design**

I started with three core user actions: **add a pet**, **schedule a care task for a pet**, and **see today's tasks in order**. The first UML draft (`diagrams/uml_draft.mmd`) had four classes:

- **`Task`** (dataclass): one care activity, with description, `HH:MM` time, duration, priority, frequency, due date and completion status. It can mark itself complete.
- **`Pet`** (dataclass): a pet's name, species and age, plus its own list of tasks. It can add and remove tasks.
- **`Owner`**: has many pets and a daily time budget (`available_minutes`). `get_all_tasks()` returns every pet's tasks in one list.
- **`Scheduler`**: the "brain". It holds an `Owner` and reads all tasks through `get_all_tasks()`, so it works across every pet rather than one. It retrieves, sorts, filters, checks for conflicts and builds the day's plan.

Relationships: an Owner *has* many Pets, a Pet *owns* many Tasks, and the Scheduler *reads* from the Owner.

**b. Design changes**

Yes. Reviewing the skeleton before implementing it showed two gaps, and building the algorithms added a third change:

1. **`Task` didn't know which pet it belonged to.** Once the Scheduler merges every pet's tasks into one list, a task can't say "this is Luna's", which breaks filtering by pet and printing the pet name in the schedule. I added a `pet_name` field that `Pet.add_task()` fills in automatically.
2. **Recurring tasks needed a coordinator.** Completing a daily task must create tomorrow's copy *and attach it to the same pet*, but a `Task` has no reference to its pet. So `Task` only builds its next copy (`next_occurrence()`), and `Scheduler.mark_task_complete()` adds it to the right pet.
3. **A `DailyPlan` class appeared.** The README asks the app to *explain* its plan. Returning a plain list of tasks lost the reasons, so `plan_day()` returns a `DailyPlan` with the scheduled tasks, the skipped tasks, minutes used, and a reason for each task. `build_daily_plan()` still returns just the list for simple callers.

Smaller additions in the final UML (`diagrams/uml_final.mmd`): input validation in `Task.__post_init__`, `start`/`end` properties, and JSON save/load methods on `Owner`.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers:

- **Time of day and duration.** Each task covers a time window (start + duration), which is used for sorting and for spotting overlaps.
- **Priority** (high / medium / low).
- **The owner's available minutes** for the day.
- **Date and frequency.** Only tasks due on the chosen day count; daily and weekly tasks roll forward when completed.
- **Completion status.** Finished tasks don't take up time or cause conflicts.

**Priority** and the **time budget** matter most. A busy owner who can't do everything should still do the essentials (medication, feeding, the walk) before nice-to-haves like a play session. So `plan_day()` fills the available minutes with high-priority tasks first, then shows the chosen tasks back in time order, because that's how the owner actually lives their day.

**b. Tradeoffs**

**The planner is greedy.** It walks through tasks from highest to lowest priority and keeps each one that still fits the remaining minutes. It never searches every combination for the one that fills the time best. In the CLI demo, 10 of the 90 minutes stay unused because the two remaining low-priority tasks need 15 and 20 minutes.

This is reasonable here because a pet owner cares more that the *important* tasks are guaranteed than that every minute is packed. A greedy rule is also easy to explain ("high priority first, until time runs out"), which is the explanation the app shows. Exhaustive search would be slower and harder to justify to a user.

A second tradeoff: **conflicts are reported, not fixed.** `detect_conflicts()` checks overlapping time windows, not just identical start times, and works across pets because one owner can't be in two places. But it only warns; it doesn't move tasks. The owner knows better than the app whether the vet appointment or the walk should move.

---

## 3. AI Collaboration

**a. How you used AI**

I used **Claude Code** (an AI coding agent that can edit files, run commands and use git) for the whole build: design, implementation, tests, debugging, documentation and pushing to GitHub.

How I prompted it, step by step:

1. **I pasted the full assignment brief as my first prompt**, with no extra instructions, so the agent had complete context about every phase and requirement up front.
2. **The agent asked me clarifying questions before doing anything**, and I answered:
   - I was in the middle of another project (TrueFalse), so I chose to **pause it**. The agent saved its unfinished change safely with `git stash` instead of leaving it half-done.
   - I let the agent **fork the starter repo** to my GitHub account and clone it.
   - For this reflection, I said **"I'll tell you after, remind me."** I kept control of the graded writing until the code was finished, and the agent reminded me at the end.
3. While it worked, I gave **short, direct follow-ups**: *"let's push it on github"*, *"which files are missing?"*, and finally a request to write this reflection about how I prompted and how the work went.

How the agent worked through the phases:

- It followed the assignment **in phase order**, with **one git commit per phase** using the suggested messages ("chore: add class skeletons from UML", "feat: implement sorting, filtering, and conflict detection", "test: add automated test suite for PawPal+ system", and so on), so my history shows the real progression.
- Before writing code, it **reviewed the skeleton** and found the missing `pet_name` and the recurrence-coordination problem (section 1b).
- It ran `python main.py` and `python -m pytest` after every change, and drove the Streamlit app automatically with Streamlit's `AppTest` to check that adding pets and tasks, warnings, marking tasks done, and saving/reloading all worked.
- It added optional extensions 1–4 (next available slot, JSON persistence, priority scheduling, emoji output), each with tests.

The most helpful prompting style was **giving complete context once (the whole brief), then short, specific requests.** The second most useful thing was the agent asking questions about decisions that were mine to make (pausing my other project, forking, how to handle the reflection) instead of guessing.

**b. Judgment and verification**

- **Keeping control of the reflection.** When the agent offered to draft my reflection, I didn't accept right away. I said I'd decide later, because this part is graded on my own honest account. I only asked for a draft once the code was done and I knew what had actually happened.
- **Fixing an early design that would have failed.** Sorting `"HH:MM"` strings with `sorted()` and a `lambda` (the approach the assignment hints at) breaks when times aren't zero-padded: `"9:00"` sorts *after* `"10:30"`. The final version converts each time to minutes after midnight before sorting, normalizes `"7:30"` to `"07:30"`, and has a test that would fail with string sorting.
- **Not trusting a suite that passed on the first try.** All 28 tests passed on the first run, which can mean the tests are too weak. To verify them, the agent deliberately broke the code three ways: string-based sorting, counting back-to-back tasks as a conflict, and leaving a recurring task's next copy marked "completed". The matching test failed each time, and then the code was restored. That showed the tests actually catch these bugs.
- **Small catches during checks:** the app's time picker defaulted to the current time instead of a sensible 08:00, which was found while testing the UI and fixed. Also, the README test count was refreshed from 28 to 32 after the extension tests were added, so the documentation matches the real output.

---

## 4. Testing and Verification

**a. What you tested**

There are 32 tests in `tests/test_pawpal.py`:

- **Core behavior:** `mark_complete()`, adding tasks to a pet, collecting tasks across pets, rejecting duplicate pet names, and validating bad input (`"25:00"`, unknown priority or frequency, zero duration).
- **Sorting:** chronological order, including non-zero-padded times; ties keep their original order; priority-then-time.
- **Filtering:** by pet, by status, by both, and an unknown pet.
- **Recurrence:** a daily task completed on **Jan 31 creates Feb 1** (crossing a month boundary), weekly adds 7 days, one-off tasks create nothing, and the new task is a separate copy.
- **Conflicts:** same start time, partial overlap, back-to-back tasks (08:00–08:30 then 08:30) that should *not* conflict, other days and completed tasks ignored, and three overlapping tasks giving three warnings.
- **Planning:** high priority wins under a tight budget, skipped tasks get a reason, and a zero budget plans nothing.
- **Extensions:** next free slot, and a JSON save/load round trip compared field by field.

These matter because the scheduler's value is in its rules. A wrong sort, a missed conflict, or a recurring task that silently stops repeating (say, a daily pill) would directly hurt a pet. The edge cases are exactly where those rules are easiest to get wrong.

**b. Confidence**

**4 out of 5.** Every scheduling rule is tested, including tricky edges, and the mutation check showed the tests catch real bugs. It isn't 5 because the Streamlit UI was checked with `AppTest` and by hand rather than in the automated suite, and the greedy planner isn't optimal.

With more time, I would test:
- tasks that run past midnight (e.g. 23:50 for 20 minutes)
- many tasks in one day, for performance
- a `data.json` file that's corrupted or was edited by hand
- recurring tasks completed late (should the next one be "tomorrow" or "the day after the original due date"?)

---

## 5. Reflection

**a. What went well**

I'm most satisfied that the "smart" features are **correct, explained and verified**, not just present. Conflict detection uses real overlapping time windows, recurring tasks roll forward correctly across month boundaries, the plan explains why each task was kept or skipped, and the tests were themselves checked by deliberately breaking the code.

**b. What you would improve**

- Let the planner **resolve conflicts**, for example by suggesting a move with `next_available_slot()`, instead of only warning.
- Replace the greedy planner with one that packs the time budget better when priorities tie.
- Support tasks that cross midnight and per-pet time windows (e.g. "walks only in daylight").
- Add an edit button for tasks in the UI, which currently can only add tasks and mark them done.

**c. Key takeaway**

Being the "lead architect" with a powerful AI tool means **owning the decisions and the verification, not the typing.** The AI moved fast, but the useful moments were about judgment: giving it the full brief up front, deciding what to pause and what to keep for myself (like this reflection), checking that a design choice such as `pet_name` actually fit the system, and not trusting green tests until they were proven to fail on broken code.

I also learned that I used **one long session** instead of separate chat sessions per phase as the assignment suggests. It still stayed organized because each phase ended in its own commit. Next time I'd try separate sessions for planning, algorithms and testing, to compare how that changes the AI's focus.
