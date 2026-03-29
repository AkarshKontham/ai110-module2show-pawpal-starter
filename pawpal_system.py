from datetime import date, timedelta


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
        self.last_completed_date: str | None = None  # ISO date string (YYYY-MM-DD)
        self.start_time: int | None = None           # minutes from start of schedule (set by Scheduler)

    def complete(self, today: str | None = None) -> None:
        """Marks the task as completed and records the completion date.
        Accepts an ISO date string (YYYY-MM-DD); defaults to today's real date."""
        self.completed = True
        self.last_completed_date = today or date.today().isoformat()

    def reset(self) -> None:
        """Clears the completed flag so the task appears as pending again."""
        self.completed = False

    def is_due(self, today: str | None = None) -> bool:
        """Returns True if this task should be reset and rescheduled based on its frequency."""
        if self.frequency == "as needed":
            return False  # never auto-reset; user controls manually
        if self.last_completed_date is None:
            return True
        today_str = today or date.today().isoformat()
        if self.frequency == "daily":
            return self.last_completed_date < today_str
        if self.frequency == "weekly":
            last = date.fromisoformat(self.last_completed_date)
            today_date = date.fromisoformat(today_str)
            return (today_date - last).days >= 7
        return True

    def next_occurrence(self) -> "Task":
        """Returns a new pending Task instance with the same attributes, for the next occurrence.
        Only meaningful for 'daily' and 'weekly' frequencies."""
        return Task(
            title=self.title,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            frequency=self.frequency,
            category=self.category,
        )

    def is_high_priority(self) -> bool:
        """Returns True if this task's priority is 'high'."""
        return self.priority == "high"

    def to_dict(self) -> dict:
        """Returns a plain dictionary of all task fields, suitable for display or serialisation."""
        return {
            "title": self.title,
            "duration_minutes": self.duration_minutes,
            "priority": self.priority,
            "frequency": self.frequency,
            "category": self.category,
            "completed": self.completed,
            "last_completed": self.last_completed_date or "never",
            "start_time": self.start_time,
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
        """Sorts tasks by priority first (high → medium → low), then by duration ascending.
        The secondary sort ensures shorter tasks fill remaining budget slots when priorities tie."""
        return sorted(tasks, key=lambda t: (self.PRIORITY_ORDER.get(t.priority, 3), t.duration_minutes))

    def build_schedule(self) -> list[Task]:
        """Fits as many pending tasks as possible into the owner's time budget, highest priority first.
        Assigns start_time (minutes from schedule start) to each scheduled task."""
        pending = self.owner.get_all_pending_tasks()
        sorted_tasks = self._sorted_tasks(pending)

        scheduled = []
        time_remaining = self.owner.available_minutes
        elapsed = 0
        for task in sorted_tasks:
            if task.duration_minutes <= time_remaining:
                task.start_time = elapsed
                scheduled.append(task)
                elapsed += task.duration_minutes
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

    def get_tasks_for_pet(self, pet_name: str) -> list[Task]:
        """Returns all tasks belonging to a specific pet by name."""
        for pet in self.owner.get_pets():
            if pet.name == pet_name:
                return pet.get_tasks()
        return []

    def get_tasks_by_status(self, completed: bool) -> list[Task]:
        """Returns all tasks across all pets filtered by completion status."""
        return [t for t in self.owner.get_all_tasks() if t.completed == completed]

    def detect_conflicts(self) -> list[str]:
        """Returns a list of warning strings for scheduling conflicts found across all tasks."""
        conflicts = []
        all_tasks = self.owner.get_all_tasks()

        # Duplicate task titles (same name used more than once)
        seen_titles: set[str] = set()
        duplicate_titles: set[str] = set()
        for t in all_tasks:
            if t.title in seen_titles:
                duplicate_titles.add(t.title)
            seen_titles.add(t.title)
        for title in duplicate_titles:
            conflicts.append(f"Duplicate task title '{title}' — mark_completed will only update the first match.")

        # High-priority tasks alone exceed the time budget
        high_priority_total = sum(t.duration_minutes for t in all_tasks if t.priority == "high")
        if high_priority_total > self.owner.available_minutes:
            conflicts.append(
                f"High-priority tasks total {high_priority_total} min but budget is "
                f"{self.owner.available_minutes} min — some high-priority tasks will be skipped."
            )

        # Any single task that can never fit in the budget
        for t in all_tasks:
            if t.duration_minutes > self.owner.available_minutes:
                conflicts.append(
                    f"Task '{t.title}' ({t.duration_minutes} min) exceeds the full "
                    f"{self.owner.available_minutes}-min budget and will never be scheduled."
                )

        return conflicts

    def detect_time_conflicts(self, scheduled: list[Task]) -> list[str]:
        """Checks all pairs of scheduled tasks for overlapping time windows.
        Returns a warning string for each conflict found; never raises an exception."""
        warnings = []
        for i in range(len(scheduled)):
            for j in range(i + 1, len(scheduled)):
                a, b = scheduled[i], scheduled[j]
                if a.start_time is None or b.start_time is None:
                    continue
                a_end = a.start_time + a.duration_minutes
                b_end = b.start_time + b.duration_minutes
                # Overlap condition: each window starts before the other ends
                if a.start_time < b_end and b.start_time < a_end:
                    warnings.append(
                        f"Time conflict: '{a.title}' (min {a.start_time}–{a_end}) "
                        f"overlaps with '{b.title}' (min {b.start_time}–{b_end})."
                    )
        return warnings

    def mark_completed(self, title: str, today: str | None = None) -> bool:
        """Marks the first matching incomplete task as completed.
        For 'daily' and 'weekly' tasks, automatically adds a new pending instance
        to the same pet for the next occurrence. Returns True if a task was found."""
        for pet in self.owner.get_pets():
            for task in pet.get_tasks():
                if task.title == title and not task.completed:
                    task.complete(today)
                    if task.frequency in ("daily", "weekly"):
                        pet.add_task(task.next_occurrence())
                    return True
        return False

    def reset_all(self, today: str | None = None) -> None:
        """Resets completion status only for tasks that are due again based on their frequency.
        Pass an ISO date string (YYYY-MM-DD) for today, or omit to use the real current date."""
        for task in self.owner.get_all_tasks():
            if task.is_due(today):
                task.reset()
