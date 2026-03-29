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
