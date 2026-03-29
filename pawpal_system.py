class Task:
    """A single pet care activity."""

    def __init__(self, title: str, duration_minutes: int, priority: str,
                 frequency: str = "daily", category: str = ""):
        self.title = title
        self.duration_minutes = duration_minutes
        self.priority = priority        # "high", "medium", "low"
        self.frequency = frequency      # "daily", "weekly", "as needed"
        self.category = category
        self.completed = False

    def complete(self) -> None:
        self.completed = True

    def reset(self) -> None:
        self.completed = False

    def is_high_priority(self) -> bool:
        return self.priority == "high"

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "duration_minutes": self.duration_minutes,
            "priority": self.priority,
            "frequency": self.frequency,
            "category": self.category,
            "completed": self.completed,
        }


class Pet:
    """A pet with its own list of care tasks."""

    def __init__(self, name: str, species: str):
        self.name = name
        self.species = species
        self._tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        self._tasks.append(task)

    def remove_task(self, title: str) -> None:
        self._tasks = [t for t in self._tasks if t.title != title]

    def get_tasks(self) -> list[Task]:
        return self._tasks

    def get_pending_tasks(self) -> list[Task]:
        return [t for t in self._tasks if not t.completed]


class Owner:
    """A pet owner who manages one or more pets."""

    def __init__(self, name: str, available_minutes: int):
        self.name = name
        self.available_minutes = available_minutes
        self._pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        self._pets.append(pet)

    def remove_pet(self, name: str) -> None:
        self._pets = [p for p in self._pets if p.name != name]

    def get_pets(self) -> list[Pet]:
        return self._pets

    def get_all_tasks(self) -> list[Task]:
        """Returns all tasks across every pet."""
        tasks = []
        for pet in self._pets:
            tasks.extend(pet.get_tasks())
        return tasks

    def get_all_pending_tasks(self) -> list[Task]:
        """Returns only incomplete tasks across every pet."""
        return [t for t in self.get_all_tasks() if not t.completed]


class Scheduler:
    """Retrieves, organizes, and schedules tasks across all of an owner's pets."""

    PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}

    def __init__(self, owner: Owner):
        self.owner = owner

    def _sorted_tasks(self, tasks: list[Task]) -> list[Task]:
        return sorted(tasks, key=lambda t: self.PRIORITY_ORDER.get(t.priority, 3))

    def build_schedule(self) -> list[Task]:
        """Fits as many pending tasks as possible into the owner's time budget, highest priority first."""
        pending = self.owner.get_all_pending_tasks()
        sorted_tasks = self._sorted_tasks(pending)

        scheduled = []
        time_remaining = self.owner.available_minutes
        for task in sorted_tasks:
            if task.duration_minutes <= time_remaining:
                scheduled.append(task)
                time_remaining -= task.duration_minutes

        return scheduled

    def explain(self, scheduled: list[Task]) -> str:
        """Returns a plain-language summary of the schedule."""
        if not scheduled:
            return "No tasks could be scheduled within the available time."
        total = sum(t.duration_minutes for t in scheduled)
        names = [t.title for t in scheduled]
        return (
            f"Scheduled {len(scheduled)} task(s) using {total} of "
            f"{self.owner.available_minutes} available minutes, "
            f"prioritized by importance: {', '.join(names)}."
        )

    def mark_completed(self, title: str) -> bool:
        """Marks the first matching task across all pets as completed. Returns True if found."""
        for task in self.owner.get_all_tasks():
            if task.title == title:
                task.complete()
                return True
        return False

    def reset_all(self) -> None:
        """Resets completion status on all tasks (e.g. start of a new day)."""
        for task in self.owner.get_all_tasks():
            task.reset()
