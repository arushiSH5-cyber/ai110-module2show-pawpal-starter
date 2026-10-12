import datetime as dt
from pathlib import Path

import streamlit as st

from pawpal_system import TASK_EMOJI, Owner, Pet, Scheduler, Task

DATA_FILE = Path("data.json")

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.caption("Plan your pets' care for the day — sorted, conflict-checked, and explained.")

# Streamlit reruns this script on every click, so keep the Owner in session_state
# ("the vault"). On the very first run, restore it from data.json if it exists.
if "owner" not in st.session_state:
    try:
        st.session_state.owner = Owner.load_from_json(DATA_FILE)
    except (FileNotFoundError, ValueError, KeyError):
        st.session_state.owner = Owner("Jordan", available_minutes=120)
owner: Owner = st.session_state.owner
scheduler = Scheduler(owner)


def save() -> None:
    """Persist after every change so pets and tasks survive restarts."""
    owner.save_to_json(DATA_FILE)


# ---- sidebar: owner -------------------------------------------------------------------------
with st.sidebar:
    st.header("👤 Owner")
    name = st.text_input("Name", value=owner.name)
    minutes = st.number_input("Minutes available today", 0, 24 * 60, owner.available_minutes, 15)
    if name != owner.name or minutes != owner.available_minutes:
        owner.name, owner.available_minutes = name, int(minutes)
        save()
    st.caption(f"{len(owner.pets)} pet(s) · {len(owner.get_all_tasks())} task(s) · saved to {DATA_FILE}")

# ---- add pet --------------------------------------------------------------------------------
with st.expander("🐶 Add a pet", expanded=not owner.pets):
    with st.form("add_pet", clear_on_submit=True):
        pet_name = st.text_input("Pet name")
        c1, c2 = st.columns(2)
        species = c1.selectbox("Species", ["dog", "cat", "rabbit", "bird", "other"])
        age = c2.number_input("Age (years)", min_value=0, max_value=40, value=1)
        if st.form_submit_button("Add pet"):
            if not pet_name.strip():
                st.error("Please enter a pet name.")
            else:
                try:
                    owner.add_pet(Pet(pet_name.strip(), species, int(age)))
                    save()
                    st.success(f"Added {pet_name.strip()}! 🎉")
                except ValueError as err:
                    st.error(str(err))

# ---- add task -------------------------------------------------------------------------------
with st.expander("📝 Schedule a task", expanded=bool(owner.pets)):
    if not owner.pets:
        st.info("Add a pet first.")
    else:
        with st.form("add_task", clear_on_submit=True):
            c1, c2 = st.columns(2)
            pet_choice = c1.selectbox("Pet", [p.name for p in owner.pets])
            task_type = c2.selectbox("Type", list(TASK_EMOJI), format_func=lambda k: f"{TASK_EMOJI[k]} {k}")
            description = st.text_input("Task", value="Morning walk")
            c1, c2, c3 = st.columns(3)
            when = c1.time_input("Time", value=dt.time(8, 0), step=dt.timedelta(minutes=5))
            duration = c2.number_input("Minutes", min_value=1, max_value=240, value=20)
            day = c3.date_input("Date", value=dt.date.today())
            c1, c2 = st.columns(2)
            priority = c1.selectbox("Priority", ["high", "medium", "low"])
            frequency = c2.selectbox("Repeats", ["once", "daily", "weekly"])
            if st.form_submit_button("Add task"):
                task = Task(description.strip() or "Task", when.strftime("%H:%M"), int(duration),
                            priority, frequency, task_type, due_date=day)
                owner.get_pet(pet_choice).add_task(task)
                save()
                st.success(f"Scheduled {TASK_EMOJI[task_type]} '{task.description}' for {pet_choice} at {task.time}.")
                clashes = [w for w in scheduler.detect_conflicts(scheduler.get_todays_tasks(day))
                           if f"'{task.description}'" in w]
                for w in clashes:
                    st.warning(w)
        free = scheduler.next_available_slot(int(30))
        st.caption(f"💡 Next free 30-minute slot today: **{free or 'none left'}**")

# ---- schedule view --------------------------------------------------------------------------
st.header("📅 Schedule")
c1, c2, c3, c4 = st.columns([1.2, 1, 1, 1.2])
view_day = c1.date_input("Day", value=dt.date.today(), key="view_day")
pet_filter = c2.selectbox("Pet", ["All"] + [p.name for p in owner.pets])
status_filter = c3.selectbox("Status", ["All", "To do", "Done"])
sort_mode = c4.selectbox("Sort by", ["Time", "Priority, then time"])

day_tasks = scheduler.get_todays_tasks(view_day)
shown = scheduler.filter_tasks(
    day_tasks,
    pet_name=None if pet_filter == "All" else pet_filter,
    completed={"All": None, "To do": False, "Done": True}[status_filter],
)
shown = scheduler.sort_by_time(shown) if sort_mode == "Time" else scheduler.sort_by_priority(shown)

conflicts = scheduler.detect_conflicts(day_tasks)
if conflicts:
    st.warning(f"**{len(conflicts)} scheduling conflict(s)** — you can't be in two places at once:")
    for w in conflicts:
        st.markdown(f"- {w.removeprefix('⚠️ ')}")
elif day_tasks:
    st.success("✅ No conflicts — every task has its own time.")

if not shown:
    st.info("No tasks match. Add one above, or change the filters.")
else:
    st.table([
        {
            "": "✅" if t.completed else "⬜",
            "Time": f"{t.time}–{t.end // 60:02d}:{t.end % 60:02d}",
            "Pet": t.pet_name,
            "Task": f"{TASK_EMOJI.get(t.task_type, '🐾')} {t.description}",
            "Priority": {"high": "🔴 high", "medium": "🟠 medium", "low": "🟢 low"}[t.priority],
            "Repeats": t.frequency,
        }
        for t in shown
    ])
    todo = [t for t in shown if not t.completed]
    if todo:
        c1, c2 = st.columns([3, 1])
        labels = {f"{t.time} · {t.pet_name} · {t.description}": t for t in todo}
        pick = c1.selectbox("Mark a task done", list(labels), label_visibility="collapsed")
        if c2.button("✅ Done"):
            nxt = scheduler.mark_task_complete(labels[pick])
            save()
            msg = f"Marked '{labels[pick].description}' done."
            if nxt:
                msg += f" 🔁 Next one added for {nxt.due_date:%a %b %d} at {nxt.time}."
            st.session_state.flash = msg
            st.rerun()
if msg := st.session_state.pop("flash", None):
    st.success(msg)

# ---- daily plan -----------------------------------------------------------------------------
st.header("🧠 Today's plan")
st.caption(
    "Picks the most important tasks first (high → low priority) until your available "
    "minutes run out, then lists them in time order — and explains every decision."
)
plan = scheduler.plan_day(view_day)
if not plan.scheduled and not plan.skipped:
    st.info("Nothing left to plan for this day.")
else:
    budget = max(plan.minutes_available, 1)
    st.progress(min(plan.minutes_used / budget, 1.0),
                text=f"{plan.minutes_used} of {plan.minutes_available} minutes planned")
    for t in plan.scheduled:
        st.markdown(f"**{t.time}** · {TASK_EMOJI.get(t.task_type, '🐾')} {t.description} "
                    f"({t.pet_name}) — _{plan.explain(t)}_")
    if plan.skipped:
        st.warning("Didn't fit today:\n\n" + "\n".join(
            f"- {t.description} ({t.pet_name}): {plan.explain(t).removeprefix('skipped: ')}"
            for t in plan.skipped))
