# PawPal+ Class Diagram

```mermaid
classDiagram
    class Owner {
        +String name
        +int available_minutes
        +get_available_time() int
    }

    class Pet {
        +String name
        +String species
        +Owner owner
        +get_tasks() list
    }

    class Task {
        +String title
        +int duration_minutes
        +String priority
        +String category
        +is_high_priority() bool
        +to_dict() dict
    }

    class Schedule {
        +list tasks
        +int total_duration
        +String explanation
        +add_task(task) None
        +get_total_duration() int
        +display() str
    }

    class Scheduler {
        +int available_minutes
        +list tasks
        +run() Schedule
        +prioritize(tasks) list
        +explain(schedule) str
    }

    Owner "1" --> "1" Pet : owns
    Pet "1" --> "many" Task : has
    Scheduler --> Schedule : produces
    Scheduler ..> Task : uses
    Scheduler ..> Owner : reads constraints from
```

## Arrow Key

| Arrow | Meaning |
|-------|---------|
| `-->` | Solid arrow — ownership or composition. One object holds a direct reference to another. |
| `..>` | Dashed arrow — usage dependency. One object uses another temporarily but does not own it. |
| `"1" --> "1"` | One-to-one relationship (e.g. one Owner owns one Pet). |
| `"1" --> "many"` | One-to-many relationship (e.g. one Pet has many Tasks). |
