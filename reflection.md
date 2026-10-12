# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

Before any code, I thought about what a pet owner actually needs to do. I landed on three things: add a pet, schedule a care task for that pet, and see today's tasks in order.

From there I went with four classes:

- **Task**: one thing that needs to happen (a walk, a pill, a vet visit), with a time, how long it takes, a priority, how often it repeats, and whether it's done.
- **Pet**: the pet's basic info plus its own list of tasks.
- **Owner**: has multiple pets and a limited amount of time each day. It can hand back every pet's tasks in one list.
- **Scheduler**: the "brain". It doesn't belong to any single pet. It asks the Owner for all the tasks and then sorts, filters and plans them.

I made Task and Pet dataclasses since they're mostly just data, which kept the code a lot cleaner.

**b. Design changes**

Yes, a few times. The biggest one came from reviewing my skeleton before implementing it. I realized that once the Scheduler pulls every pet's tasks into one big list, a task has no idea whose it is. So I couldn't filter by pet or even print "Luna" next to her pill. I added a `pet_name` field that gets filled in automatically when a task is added to a pet.

Recurring tasks caused a similar problem. When a daily task is completed, tomorrow's copy has to go back onto the same pet, but a Task can't reach its pet. So the Task just makes its next copy, and the Scheduler puts it in the right place.

I also added a small `DailyPlan` class later. The project asks the app to *explain* its plan, and returning a plain list of tasks threw away the "why".

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

My scheduler looks at:
- the time of day and how long each task takes
- priority (high / medium / low)
- how many minutes the owner has that day
- which day a task is due, and whether it repeats
- whether it's already done

I decided priority and the time budget matter most. If someone only has 90 minutes, their dog's walk and their cat's medication should come before a play session. So the plan fills the available time with the most important tasks first, then shows them in time order, because that's how you actually go through your day.

**b. Tradeoffs**

The planner is "greedy". It goes from highest to lowest priority and keeps whatever still fits. It doesn't try every combination to fill the time perfectly. In my demo, that leaves 10 minutes unused because the leftover tasks need 15 and 20 minutes.

I'm fine with that for this app. A pet owner cares way more that the important stuff is guaranteed than that every minute is packed. It's also easy to explain to the user ("most important first, until you run out of time").

Another tradeoff is that conflicts get **flagged but not fixed**. If two tasks overlap, the app warns you instead of moving one. I think the owner knows better than an app whether to move the vet visit or the walk.

---

## 3. AI Collaboration

**a. How you used AI**

I used Claude Code, an AI coding agent, as my main helper for this project. I gave it the full assignment up front so it understood the whole picture, then worked through it phase by phase, with each phase committed separately so I could track progress.

What helped most was giving full context once and then being specific about what I wanted. I also liked that it checked with me before making decisions that were mine to make. For example, I was in the middle of another project and decided to pause that first. I also chose to hold off on the reflection until all the code was finished, so I could write about what actually happened.

I mostly used it for:
- scaffolding the classes from my design
- writing and expanding the scheduling algorithms
- generating tests and checking edge cases
- polishing the README and the UML diagram

**b. Judgment and verification**

The assignment suggests sorting times as "HH:MM" strings with a lambda. That works until a time isn't zero-padded: "9:00" sorts *after* "10:30". The final version converts times to minutes before sorting and cleans up times like "7:30" to "07:30". There's also a test that would fail if anyone switched it back to string sorting.

Another moment: all the tests passed on the very first run, which honestly made me suspicious. Passing tests don't mean much if they'd pass no matter what. So the code was deliberately broken three different ways (wrong sorting, counting back-to-back tasks as a conflict, leaving a repeated task marked as done), and each time the right test failed. After that I actually trusted the tests.

I also checked the app myself. The time picker defaulted to whatever time it currently was, which made no sense for scheduling, so it got changed to 8:00.

---

## 4. Testing and Verification

**a. What you tested**

I ended up with 32 tests, covering:
- the basics (completing a task, adding tasks, bad input like "25:00")
- sorting, including the "9:00" vs "10:30" case
- filtering by pet and by done / not done
- recurring tasks, including a daily task completed on Jan 31 correctly showing up on Feb 1
- conflicts: same time, partial overlap, and back-to-back tasks that touch but shouldn't count as a conflict
- the daily plan picking high-priority tasks when time is tight
- saving to and loading from a JSON file

These felt important because the scheduler's whole job is following rules. If a daily medication silently stopped repeating, or two overlapping tasks weren't flagged, that's a real problem for a real pet.

**b. Confidence**

I'd give it **4 out of 5**. The scheduling logic is well tested, including the tricky edge cases. It's not a 5 because the Streamlit UI isn't part of the automated tests, and the planner isn't perfectly optimal.

If I had more time, I'd test:
- tasks that go past midnight
- days with a lot of tasks
- what happens if the saved data file gets messed up

---

## 5. Reflection

**a. What went well**

I'm happiest that the "smart" parts actually work correctly and explain themselves. Conflicts are detected using real time overlaps, not just matching start times. Repeating tasks roll over correctly. The daily plan tells you why something was skipped. I also went beyond the base requirements: a "next free slot" finder, saving data between runs, priority-based scheduling, and emoji formatting.

**b. What you would improve**

I'd want the app to help *fix* conflicts, not just warn about them, maybe by suggesting the next free slot. I'd also add a way to edit or delete tasks in the UI, and handle tasks that cross midnight.

**c. Key takeaway**

My biggest takeaway is that working with AI is less about writing every line yourself and more about being the one making decisions and checking the work. The AI is fast, but I still had to know what the system should look like, catch when something didn't fit the design, and not just trust green checkmarks.

I also did most of this in one long session instead of separate chats for each phase. It stayed organized because every phase had its own commit, but next time I'd like to try separate sessions to see if it keeps the AI more focused.
