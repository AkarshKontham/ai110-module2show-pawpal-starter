# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

The scheduler has been extended with four improvements beyond basic priority ordering:

- **Sort by duration within priority** — when two tasks share the same priority, the shorter one is scheduled first. This fits more tasks into the available time budget instead of letting a long task block smaller ones behind it.

- **Recurring task support** — tasks track a `last_completed_date`. A `daily` task resets automatically the next day, a `weekly` task resets after 7 days, and an `as needed` task stays completed until the owner manually resets it. Completing a `daily` or `weekly` task via `mark_completed()` automatically creates a fresh pending instance for the next occurrence.

- **Filter by pet and status** — `Scheduler.get_tasks_for_pet(name)` returns all tasks for a specific pet; `Scheduler.get_tasks_by_status(completed)` filters across all pets by done or pending. Both filters are available as dropdowns in the UI.

- **Conflict detection** — two methods catch problems before they affect the owner:
  - `detect_conflicts()` warns about duplicate task titles, high-priority tasks that together exceed the time budget, and any single task that can never fit.
  - `detect_time_conflicts(scheduled)` checks every pair of scheduled tasks for overlapping time windows using each task's assigned `start_time`, and returns a plain warning string for each overlap found without crashing the app.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
