from datetime import date

import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

# --- Session state initialization ---
if "owner" not in st.session_state:
    st.session_state.owner = None
if "pet" not in st.session_state:
    st.session_state.pet = None

# --- Owner & Pet setup ---
st.subheader("Owner & Pet Info")
owner_name = st.text_input("Owner name", value="Jordan")
available_minutes = st.number_input("Minutes available today", min_value=1, max_value=480, value=60)
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Save Owner & Pet"):
    pet = Pet(name=pet_name, species=species)
    owner = Owner(name=owner_name, available_minutes=int(available_minutes))
    owner.add_pet(pet)
    st.session_state.owner = owner
    st.session_state.pet = pet
    st.success(f"Saved {owner_name} and {pet_name} the {species}.")

st.divider()

# --- Add Task ---
st.subheader("Add a Task")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

col4, col5 = st.columns(2)
with col4:
    frequency = st.selectbox("Frequency", ["daily", "weekly", "as needed"])
with col5:
    category = st.text_input("Category (optional)", value="")

if st.button("Add task"):
    if st.session_state.pet is None:
        st.warning("Please save an Owner & Pet first.")
    else:
        task = Task(
            title=task_title,
            duration_minutes=int(duration),
            priority=priority,
            frequency=frequency,
            category=category,
        )
        st.session_state.pet.add_task(task)
        st.success(f"Added '{task_title}' ({frequency}) to {st.session_state.pet.name}.")

# Show current tasks
if st.session_state.pet is not None:
    tasks = st.session_state.pet.get_tasks()
    if tasks:
        st.write("Current tasks:")
        st.table([t.to_dict() for t in tasks])
    else:
        st.info("No tasks yet. Add one above.")

st.divider()

# --- Filter Tasks ---
st.subheader("Filter Tasks")

if st.session_state.owner is not None:
    scheduler = Scheduler(owner=st.session_state.owner)

    col_a, col_b = st.columns(2)
    with col_a:
        pet_names = [p.name for p in st.session_state.owner.get_pets()]
        filter_pet = st.selectbox("Filter by pet", ["All pets"] + pet_names)
    with col_b:
        filter_status = st.selectbox("Filter by status", ["All", "Pending", "Completed"])

    if filter_pet == "All pets":
        filtered = st.session_state.owner.get_all_tasks()
    else:
        filtered = scheduler.get_tasks_for_pet(filter_pet)

    if filter_status == "Pending":
        filtered = [t for t in filtered if not t.completed]
    elif filter_status == "Completed":
        filtered = [t for t in filtered if t.completed]

    if filtered:
        st.table([t.to_dict() for t in filtered])
    else:
        st.info("No tasks match the selected filters.")
else:
    st.info("Save an Owner & Pet above to enable filters.")

st.divider()

# --- Generate Schedule ---
st.subheader("Build Schedule")

if st.button("Generate schedule"):
    if st.session_state.owner is None:
        st.warning("Please save an Owner & Pet first.")
    elif not st.session_state.pet.get_tasks():
        st.warning("Add at least one task before generating a schedule.")
    else:
        scheduler = Scheduler(owner=st.session_state.owner)

        # Reset tasks that are due again today before scheduling
        today_str = date.today().isoformat()
        scheduler.reset_all(today=today_str)

        # Show any conflicts as warnings
        conflicts = scheduler.detect_conflicts()
        for conflict in conflicts:
            st.warning(f"⚠️ {conflict}")

        scheduled = scheduler.build_schedule()
        if scheduled:
            time_conflicts = scheduler.detect_time_conflicts(scheduled)
            for conflict in time_conflicts:
                st.warning(f"⚠️ {conflict}")
            st.success("Today's Schedule")
            st.table([t.to_dict() for t in scheduled])
            st.info(scheduler.explain(scheduled))
        else:
            st.warning("No tasks fit within the available time.")
