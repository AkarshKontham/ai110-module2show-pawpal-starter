from pawpal_system import Owner, Pet, Task, Scheduler

# Create owner
jordan = Owner(name="Jordan", available_minutes=60)

# Create pets
mochi = Pet(name="Mochi", species="dog")
luna = Pet(name="Luna", species="cat")

# Add tasks to Mochi
mochi.add_task(Task(title="Morning walk", duration_minutes=20, priority="high", frequency="daily", category="exercise"))
mochi.add_task(Task(title="Feeding", duration_minutes=10, priority="high", frequency="daily", category="feeding"))

# Add tasks to Luna
luna.add_task(Task(title="Litter box cleaning", duration_minutes=10, priority="medium", frequency="daily", category="grooming"))
luna.add_task(Task(title="Playtime", duration_minutes=15, priority="low", frequency="daily", category="enrichment"))
luna.add_task(Task(title="Medication", duration_minutes=5, priority="high", frequency="daily", category="health"))

# Register pets with owner
jordan.add_pet(mochi)
jordan.add_pet(luna)

# Run scheduler
scheduler = Scheduler(owner=jordan)
scheduled_tasks = scheduler.build_schedule()

# Print today's schedule
print("=" * 40)
print(f"  Today's Schedule for {jordan.name}")
print("=" * 40)

for task in scheduled_tasks:
    pet_name = next(
        (p.name for p in jordan.get_pets() if task in p.get_tasks()), "Unknown"
    )
    print(f"  [{task.priority.upper()}] {task.title} — {task.duration_minutes} min ({pet_name})")

print("-" * 40)
print(scheduler.explain(scheduled_tasks))
print("=" * 40)
