import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Owner, Pet, Task, Scheduler


# --- Task tests ---

def test_task_is_high_priority():
    """A task with priority 'high' should return True from is_high_priority."""
    task = Task(title="Medication", duration_minutes=5, priority="high")
    assert task.is_high_priority() is True

def test_task_is_not_high_priority():
    """A task with priority 'low' should return False from is_high_priority."""
    task = Task(title="Playtime", duration_minutes=15, priority="low")
    assert task.is_high_priority() is False

def test_task_complete_and_reset():
    """Completing a task sets completed to True; resetting it returns completed to False."""
    task = Task(title="Walk", duration_minutes=20, priority="high")
    task.complete()
    assert task.completed is True
    task.reset()
    assert task.completed is False

def test_task_to_dict():
    """to_dict should return a dictionary with all task fields including completed status."""
    task = Task(title="Feeding", duration_minutes=10, priority="medium", frequency="daily", category="feeding")
    d = task.to_dict()
    assert d["title"] == "Feeding"
    assert d["duration_minutes"] == 10
    assert d["completed"] is False


# --- Pet tests ---

def test_pet_add_and_get_tasks():
    """Adding a task to a pet should make it retrievable via get_tasks."""
    pet = Pet(name="Mochi", species="dog")
    task = Task(title="Walk", duration_minutes=20, priority="high")
    pet.add_task(task)
    assert len(pet.get_tasks()) == 1

def test_pet_remove_task():
    """Removing a task by title should leave the pet with no tasks."""
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task(title="Walk", duration_minutes=20, priority="high"))
    pet.remove_task("Walk")
    assert len(pet.get_tasks()) == 0

def test_pet_get_pending_tasks():
    """get_pending_tasks should only return tasks that have not been completed."""
    pet = Pet(name="Luna", species="cat")
    t1 = Task(title="Medication", duration_minutes=5, priority="high")
    t2 = Task(title="Playtime", duration_minutes=15, priority="low")
    t1.complete()
    pet.add_task(t1)
    pet.add_task(t2)
    assert len(pet.get_pending_tasks()) == 1


# --- Owner tests ---

def test_owner_add_pet_and_get_all_tasks():
    """get_all_tasks should return tasks from all pets registered with the owner."""
    owner = Owner(name="Jordan", available_minutes=60)
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task(title="Walk", duration_minutes=20, priority="high"))
    owner.add_pet(pet)
    assert len(owner.get_all_tasks()) == 1

def test_owner_get_all_pending_tasks_excludes_completed():
    """get_all_pending_tasks should not include tasks that are already completed."""
    owner = Owner(name="Jordan", available_minutes=60)
    pet = Pet(name="Mochi", species="dog")
    t = Task(title="Walk", duration_minutes=20, priority="high")
    t.complete()
    pet.add_task(t)
    owner.add_pet(pet)
    assert len(owner.get_all_pending_tasks()) == 0


# --- Scheduler tests ---

def test_scheduler_respects_time_budget():
    """The scheduler should never schedule tasks that exceed the owner's available minutes."""
    owner = Owner(name="Jordan", available_minutes=30)
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task(title="Walk", duration_minutes=20, priority="high"))
    pet.add_task(Task(title="Bath", duration_minutes=40, priority="medium"))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    scheduled = scheduler.build_schedule()
    total = sum(t.duration_minutes for t in scheduled)
    assert total <= 30

def test_scheduler_high_priority_scheduled_first():
    """The scheduler should place high priority tasks before lower priority ones."""
    owner = Owner(name="Jordan", available_minutes=30)
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task(title="Playtime", duration_minutes=15, priority="low"))
    pet.add_task(Task(title="Medication", duration_minutes=5, priority="high"))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    scheduled = scheduler.build_schedule()
    assert scheduled[0].title == "Medication"

def test_scheduler_explain_returns_string():
    """explain should return a non-empty string describing the scheduled tasks."""
    owner = Owner(name="Jordan", available_minutes=60)
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task(title="Walk", duration_minutes=20, priority="high"))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    scheduled = scheduler.build_schedule()
    explanation = scheduler.explain(scheduled)
    assert isinstance(explanation, str)
    assert len(explanation) > 0

def test_scheduler_empty_when_no_time():
    """The scheduler should return an empty list when the owner has zero available minutes."""
    owner = Owner(name="Jordan", available_minutes=0)
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task(title="Walk", duration_minutes=20, priority="high"))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    scheduled = scheduler.build_schedule()
    assert scheduled == []


# --- Sorting correctness tests ---

def test_sort_chronological_order_by_start_time():
    """Scheduled tasks should be assigned start_times in strictly ascending order
    (each task starts after the previous one ends)."""
    owner = Owner(name="Jordan", available_minutes=90)
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task(title="Medication",  duration_minutes=5,  priority="high"))
    pet.add_task(Task(title="Grooming",    duration_minutes=30, priority="medium"))
    pet.add_task(Task(title="Playtime",    duration_minutes=20, priority="low"))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    scheduled = scheduler.build_schedule()
    start_times = [t.start_time for t in scheduled]
    assert start_times == sorted(start_times), (
        f"start_times not in ascending order: {start_times}"
    )

def test_sort_same_priority_shorter_task_first():
    """When two tasks share the same priority, the shorter one should be
    scheduled first (secondary sort: duration ascending)."""
    owner = Owner(name="Jordan", available_minutes=60)
    pet = Pet(name="Luna", species="cat")
    pet.add_task(Task(title="Long Groom",  duration_minutes=30, priority="medium"))
    pet.add_task(Task(title="Quick Brush", duration_minutes=10, priority="medium"))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    scheduled = scheduler.build_schedule()
    assert scheduled[0].title == "Quick Brush", (
        "Shorter same-priority task should be scheduled first"
    )

def test_sort_unknown_priority_scheduled_last():
    """A task with an unrecognised priority string should sort after low-priority
    tasks (falls into the default bucket 3)."""
    owner = Owner(name="Jordan", available_minutes=60)
    pet = Pet(name="Rex", species="dog")
    pet.add_task(Task(title="Walk",    duration_minutes=10, priority="low"))
    pet.add_task(Task(title="Mystery", duration_minutes=10, priority="unknown"))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    scheduled = scheduler.build_schedule()
    titles = [t.title for t in scheduled]
    assert titles.index("Walk") < titles.index("Mystery"), (
        "Unknown-priority task should appear after low-priority task"
    )


# --- Recurrence logic tests ---

def test_daily_task_creates_new_occurrence_after_completion():
    """Marking a daily task complete should add a new pending instance of that task
    to the pet, representing the next day's occurrence."""
    owner = Owner(name="Jordan", available_minutes=60)
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task(title="Feeding", duration_minutes=10, priority="high", frequency="daily"))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    scheduler.mark_completed("Feeding", today="2026-03-29")
    all_tasks = pet.get_tasks()
    pending = [t for t in all_tasks if not t.completed]
    assert len(pending) == 1, "A new pending occurrence should exist after completing a daily task"
    assert pending[0].title == "Feeding"

def test_daily_task_new_occurrence_is_not_completed():
    """The new occurrence spawned after completing a daily task must start as pending,
    not already completed."""
    owner = Owner(name="Jordan", available_minutes=60)
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task(title="Feeding", duration_minutes=10, priority="high", frequency="daily"))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    scheduler.mark_completed("Feeding", today="2026-03-29")
    new_task = [t for t in pet.get_tasks() if not t.completed][0]
    assert new_task.completed is False
    assert new_task.last_completed_date is None

def test_as_needed_task_does_not_create_new_occurrence():
    """Marking an 'as needed' task complete should NOT spawn a new pending instance."""
    owner = Owner(name="Jordan", available_minutes=60)
    pet = Pet(name="Luna", species="cat")
    pet.add_task(Task(title="Vet Visit", duration_minutes=60, priority="high", frequency="as needed"))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    scheduler.mark_completed("Vet Visit", today="2026-03-29")
    assert len(pet.get_tasks()) == 1, "'as needed' task should not spawn a new occurrence"

def test_completing_daily_task_twice_creates_only_one_extra_occurrence():
    """Calling mark_completed twice on the same title should only create one extra
    occurrence (the second call finds the new pending task and completes it,
    creating one more — total original=1 + two completions = 3 tasks, 1 pending)."""
    owner = Owner(name="Jordan", available_minutes=60)
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task(title="Feeding", duration_minutes=10, priority="high", frequency="daily"))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    scheduler.mark_completed("Feeding", today="2026-03-29")
    scheduler.mark_completed("Feeding", today="2026-03-30")
    pending = [t for t in pet.get_tasks() if not t.completed]
    assert len(pending) == 1, "Exactly one pending occurrence should exist after two sequential completions"


# --- Conflict detection tests ---

def test_detect_time_conflict_overlapping_tasks():
    """detect_time_conflicts should return a warning when two scheduled tasks
    have overlapping time windows."""
    owner = Owner(name="Jordan", available_minutes=60)
    pet = Pet(name="Mochi", species="dog")
    task_a = Task(title="Walk",     duration_minutes=20, priority="high")
    task_b = Task(title="Grooming", duration_minutes=20, priority="high")
    task_a.start_time = 0
    task_b.start_time = 10  # starts before Walk ends (0+20=20) → overlap
    pet.add_task(task_a)
    pet.add_task(task_b)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    warnings = scheduler.detect_time_conflicts([task_a, task_b])
    assert len(warnings) > 0, "Expected a time-conflict warning for overlapping tasks"

def test_detect_no_time_conflict_for_abutting_tasks():
    """Tasks that share an endpoint (A ends exactly when B starts) should NOT
    be flagged as conflicting — they abut but do not overlap."""
    owner = Owner(name="Jordan", available_minutes=60)
    pet = Pet(name="Mochi", species="dog")
    task_a = Task(title="Walk",     duration_minutes=20, priority="high")
    task_b = Task(title="Grooming", duration_minutes=20, priority="medium")
    task_a.start_time = 0
    task_b.start_time = 20  # starts exactly when Walk ends → no overlap
    pet.add_task(task_a)
    pet.add_task(task_b)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    warnings = scheduler.detect_time_conflicts([task_a, task_b])
    assert warnings == [], f"Abutting tasks should not conflict, but got: {warnings}"

def test_detect_conflict_duplicate_title():
    """detect_conflicts should flag when two tasks share the same title, since
    mark_completed only updates the first match."""
    owner = Owner(name="Jordan", available_minutes=60)
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task(title="Walk", duration_minutes=20, priority="high"))
    pet.add_task(Task(title="Walk", duration_minutes=20, priority="low"))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    conflicts = scheduler.detect_conflicts()
    assert any("Walk" in c for c in conflicts), (
        "Expected a duplicate-title conflict warning for 'Walk'"
    )

def test_detect_conflict_high_priority_exceeds_budget():
    """detect_conflicts should warn when the total duration of high-priority tasks
    alone exceeds the owner's available minutes."""
    owner = Owner(name="Jordan", available_minutes=30)
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task(title="Medication", duration_minutes=20, priority="high"))
    pet.add_task(Task(title="Walk",       duration_minutes=20, priority="high"))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    conflicts = scheduler.detect_conflicts()
    assert any("high-priority" in c for c in conflicts), (
        "Expected a budget-overload warning for high-priority tasks"
    )

def test_detect_no_conflict_empty_schedule():
    """detect_time_conflicts on an empty list should return no warnings."""
    owner = Owner(name="Jordan", available_minutes=60)
    owner.add_pet(Pet(name="Mochi", species="dog"))
    scheduler = Scheduler(owner)
    assert scheduler.detect_time_conflicts([]) == []
