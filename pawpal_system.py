class Owner:
    def __init__(self, name: str, available_minutes: int):
        self.name = name
        self.available_minutes = available_minutes

    def get_available_time(self) -> int:
        return self.available_minutes


class Pet:
    def __init__(self, name: str, species: str, owner: Owner):
        self.name = name
        self.species = species
        self.owner = owner
        self._tasks = []

    def get_tasks(self) -> list:
        return self._tasks


class Task:
    def __init__(self, title: str, duration_minutes: int, priority: str, category: str = ""):
        self.title = title
        self.duration_minutes = duration_minutes
        self.priority = priority
        self.category = category

    def is_high_priority(self) -> bool:
        return self.priority == "high"

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "duration_minutes": self.duration_minutes,
            "priority": self.priority,
            "category": self.category,
        }


class Schedule:
    def __init__(self):
        self.tasks = []
        self.total_duration = 0
        self.explanation = ""

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)
        self.total_duration += task.duration_minutes

    def get_total_duration(self) -> int:
        return self.total_duration

    def display(self) -> str:
        if not self.tasks:
            return "No tasks scheduled."
        lines = []
        for task in self.tasks:
            lines.append(f"- {task.title} ({task.duration_minutes} min) [{task.priority}]")
        if self.explanation:
            lines.append(f"\nReasoning: {self.explanation}")
        return "\n".join(lines)


class Scheduler:
    def __init__(self, available_minutes: int, tasks: list):
        self.available_minutes = available_minutes
        self.tasks = tasks

    def prioritize(self, tasks: list) -> list:
        priority_order = {"high": 0, "medium": 1, "low": 2}
        return sorted(tasks, key=lambda t: priority_order.get(t.priority, 3))

    def run(self) -> Schedule:
        schedule = Schedule()
        time_remaining = self.available_minutes

        for task in self.prioritize(self.tasks):
            if task.duration_minutes <= time_remaining:
                schedule.add_task(task)
                time_remaining -= task.duration_minutes

        schedule.explanation = self.explain(schedule)
        return schedule

    def explain(self, schedule: Schedule) -> str:
        if not schedule.tasks:
            return "No tasks fit within the available time."
        names = [t.title for t in schedule.tasks]
        return (
            f"Scheduled {len(schedule.tasks)} task(s) using "
            f"{schedule.get_total_duration()} of {self.available_minutes} available minutes, "
            f"prioritized by importance: {', '.join(names)}."
        )
