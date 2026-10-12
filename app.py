import datetime as dt

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.caption("Plan your pets' care for the day.")

# Streamlit reruns this script on every click, so keep the Owner in session_state
# ("the vault") and only create it the first time.
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan")
owner: Owner = st.session_state.owner

st.subheader("👤 Owner")
owner.name = st.text_input("Owner name", value=owner.name)

st.subheader("🐶 Add a pet")
with st.form("add_pet", clear_on_submit=True):
    pet_name = st.text_input("Pet name")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    age = st.number_input("Age (years)", min_value=0, max_value=40, value=1)
    if st.form_submit_button("Add pet"):
        if not pet_name.strip():
            st.error("Please enter a pet name.")
        else:
            try:
                owner.add_pet(Pet(pet_name.strip(), species, int(age)))
                st.success(f"Added {pet_name.strip()}!")
            except ValueError as err:
                st.error(str(err))

st.subheader("📝 Schedule a task")
if not owner.pets:
    st.info("Add a pet first.")
else:
    with st.form("add_task", clear_on_submit=True):
        pet_choice = st.selectbox("Pet", [p.name for p in owner.pets])
        description = st.text_input("Task", value="Morning walk")
        time = st.time_input("Time", value=dt.time(8, 0))
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        if st.form_submit_button("Add task"):
            pet = owner.get_pet(pet_choice)
            pet.add_task(Task(description, time.strftime("%H:%M"), int(duration), priority))
            st.success(f"Scheduled '{description}' for {pet_choice}.")

st.subheader("📅 Today's schedule")
scheduler = Scheduler(owner)
tasks = scheduler.build_daily_plan()
if tasks:
    st.table(
        [
            {"Time": t.time, "Pet": t.pet_name, "Task": t.description,
             "Minutes": t.duration_minutes, "Priority": t.priority}
            for t in tasks
        ]
    )
else:
    st.info("No tasks for today yet.")
