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

# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

PRIORITY_BADGE = {"high": "🔴 High", "medium": "🟡 Medium", "low": "🟢 Low"}


def _task_rows(tasks: list[Task]) -> list[dict]:
    """Format a list of tasks for display in st.dataframe."""
    return [
        {
            "Task":          t.title,
            "Priority":      PRIORITY_BADGE.get(t.priority, t.priority.capitalize()),
            "Duration (min)": t.duration_minutes,
            "Frequency":     t.frequency,
            "Category":      t.category or "—",
            "Status":        "✅ Done" if t.completed else "🕐 Pending",
        }
        for t in tasks
    ]


def _schedule_rows(tasks: list[Task]) -> list[dict]:
    """Format scheduled tasks (with assigned start_time) for display."""
    return [
        {
            "Task":          t.title,
            "Priority":      PRIORITY_BADGE.get(t.priority, t.priority.capitalize()),
            "Duration (min)": t.duration_minutes,
            "Time Window":   f"min {t.start_time} – min {t.start_time + t.duration_minutes}",
            "Frequency":     t.frequency,
            "Category":      t.category or "—",
        }
        for t in tasks
    ]


# ---------------------------------------------------------------------------
# Owner & Pet setup
# ---------------------------------------------------------------------------
st.subheader("Owner & Pet Info")
owner_name        = st.text_input("Owner name", value="Jordan")
available_minutes = st.number_input("Minutes available today", min_value=1, max_value=480, value=60)
pet_name          = st.text_input("Pet name", value="Mochi")
species           = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Save Owner & Pet"):
    pet   = Pet(name=pet_name, species=species)
    owner = Owner(name=owner_name, available_minutes=int(available_minutes))
    owner.add_pet(pet)
    st.session_state.owner = owner
    st.session_state.pet   = pet
    st.success(f"Saved {owner_name} and {pet_name} the {species}.")

st.divider()

# ---------------------------------------------------------------------------
# Add Task
# ---------------------------------------------------------------------------
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

# Current tasks — sorted by priority then duration via Scheduler
if st.session_state.owner is not None:
    tasks = st.session_state.pet.get_tasks()
    if tasks:
        scheduler    = Scheduler(owner=st.session_state.owner)
        sorted_tasks = scheduler._sorted_tasks(tasks)
        st.caption("Tasks sorted by priority (high → low), then shortest first within each priority.")
        st.dataframe(_task_rows(sorted_tasks), use_container_width=True, hide_index=True)
    else:
        st.info("No tasks yet. Add one above.")

st.divider()

# ---------------------------------------------------------------------------
# Filter Tasks
# ---------------------------------------------------------------------------
st.subheader("Filter Tasks")

if st.session_state.owner is not None:
    scheduler = Scheduler(owner=st.session_state.owner)

    col_a, col_b = st.columns(2)
    with col_a:
        pet_names  = [p.name for p in st.session_state.owner.get_pets()]
        filter_pet = st.selectbox("Filter by pet", ["All pets"] + pet_names)
    with col_b:
        filter_status = st.selectbox("Filter by status", ["All", "Pending", "Completed"])

    if filter_pet == "All pets":
        filtered = st.session_state.owner.get_all_tasks()
    else:
        filtered = scheduler.get_tasks_for_pet(filter_pet)

    if filter_status == "Pending":
        filtered = scheduler.get_tasks_by_status(completed=False)
        if filter_pet != "All pets":
            filtered = [t for t in filtered if t in scheduler.get_tasks_for_pet(filter_pet)]
    elif filter_status == "Completed":
        filtered = scheduler.get_tasks_by_status(completed=True)
        if filter_pet != "All pets":
            filtered = [t for t in filtered if t in scheduler.get_tasks_for_pet(filter_pet)]

    if filtered:
        sorted_filtered = scheduler._sorted_tasks(filtered)
        st.dataframe(_task_rows(sorted_filtered), use_container_width=True, hide_index=True)
    else:
        st.info("No tasks match the selected filters.")
else:
    st.info("Save an Owner & Pet above to enable filters.")

st.divider()

# ---------------------------------------------------------------------------
# Generate Schedule
# ---------------------------------------------------------------------------
st.subheader("Build Schedule")

if st.button("Generate schedule"):
    if st.session_state.owner is None:
        st.warning("Please save an Owner & Pet first.")
    elif not st.session_state.pet.get_tasks():
        st.warning("Add at least one task before generating a schedule.")
    else:
        scheduler   = Scheduler(owner=st.session_state.owner)
        today_str   = date.today().isoformat()
        scheduler.reset_all(today=today_str)

        # --- Conflict warnings (detect_conflicts + detect_time_conflicts) ---
        conflicts = scheduler.detect_conflicts()
        for conflict in conflicts:
            st.warning(f"⚠️ {conflict}")

        scheduled = scheduler.build_schedule()

        if scheduled:
            time_conflicts = scheduler.detect_time_conflicts(scheduled)
            for conflict in time_conflicts:
                st.warning(f"⚠️ {conflict}")

            if not conflicts and not time_conflicts:
                st.success("No scheduling conflicts detected.")

            # --- Budget metrics ---
            time_used      = sum(t.duration_minutes for t in scheduled)
            time_remaining = st.session_state.owner.available_minutes - time_used

            m1, m2, m3 = st.columns(3)
            m1.metric("Tasks scheduled", len(scheduled))
            m2.metric("Minutes used",    time_used)
            m3.metric("Minutes remaining", time_remaining)

            # --- Schedule table ---
            st.dataframe(_schedule_rows(scheduled), use_container_width=True, hide_index=True)

            # --- Plain-language explanation ---
            st.info(scheduler.explain(scheduled))
        else:
            st.warning("No tasks fit within the available time.")
