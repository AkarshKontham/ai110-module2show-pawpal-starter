# PawPal+ Class Diagram

```mermaid
classDiagram
    class Owner {
        +String name
        +int available_minutes
        -_pets : list
        +add_pet(pet) None
        +remove_pet(name) None
        +get_pets() list
        +get_all_tasks() list
        +get_all_pending_tasks() list
    }

    class Pet {
        +String name
        +String species
        -_tasks : list
        +add_task(task) None
        +remove_task(title) None
        +get_tasks() list
        +get_pending_tasks() list
    }

    class Task {
        +String title
        +int duration_minutes
        +String priority
        +String frequency
        +String category
        +bool completed
        +String last_completed_date
        +int start_time
        +complete(today) None
        +reset() None
        +is_due(today) bool
        +next_occurrence() Task
        +is_high_priority() bool
        +to_dict() dict
    }

    class Scheduler {
        +Owner owner
        +build_schedule() list
        +_sorted_tasks(tasks) list
        +explain(scheduled) str
        +get_tasks_for_pet(name) list
        +get_tasks_by_status(completed) list
        +mark_completed(title, today) bool
        +reset_all(today) None
        +detect_conflicts() list
        +detect_time_conflicts(scheduled) list
    }

    Owner "1" --> "many" Pet : owns
    Pet "1" --> "many" Task : has
    Scheduler --> Owner : owns
    Scheduler ..> Task : uses
    Task ..> Task : next_occurrence()
```

## Arrow Key

| Arrow | Meaning |
|-------|---------|
| `-->` | Solid arrow — ownership or composition. One object holds a direct reference to another. |
| `..>` | Dashed arrow — usage dependency. One object uses another temporarily but does not own it. |
| `"1" --> "1"` | One-to-one relationship (e.g. one Owner owns one Pet). |
| `"1" --> "many"` | One-to-many relationship (e.g. one Pet has many Tasks). |
