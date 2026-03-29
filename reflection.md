# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

The three core actions a user should be able to perform in PawPal+ are:

1. **Set up their pet profile** — A user should be able to enter basic information about themselves and their pet (name, pet type, time available per day) so the app understands the context and constraints it is working within.

2. **Add and manage care tasks** — A user should be able to create, edit, and remove pet care tasks (such as walks, feeding, or medication), specifying at minimum how long each task takes and how important it is, so the scheduler has the right inputs to work with.

3. **Generate and review a daily plan** — A user should be able to ask the app to produce a recommended daily schedule based on their available time and task priorities, and see a clear explanation of why those tasks were chosen and in what order.

- Briefly describe your initial UML design.
  - Five classes connected by ownership and usage relationships: Owner → Pet → Task, with a Scheduler that reads constraints from Owner and Tasks to produce a Schedule.
- What classes did you include, and what responsibilities did you assign to each?
  - **Owner** — stores the owner's name and daily time budget.
  - **Pet** — stores pet info and links the owner to their tasks.
  - **Task** — stores a single care activity (title, duration, priority, category).
  - **Schedule** — holds the ordered output of a scheduling run and an explanation.
  - **Scheduler** — sorts tasks by priority, fits them into the time budget, and produces a Schedule.

**b. Design changes**

- Did your design change during implementation?
  - Yes
- If yes, describe at least one change and why you made it.
  - Claude code helped me realize a scheduler object would be helpful and make sure that tasks are sorted properly and make sense within the overall schedule, helping make the app more organized
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
  - **Time budget** — the owner sets a daily available minutes value, and the scheduler will never exceed it. Tasks that do not fit are skipped entirely.
  - **Priority** — each task is labeled high, medium, or low. The scheduler always places high-priority tasks first so that critical care (medication, feeding) is not pushed out by optional activities.
  - **Duration** — within the same priority level, shorter tasks are scheduled before longer ones so that more tasks can fit into the remaining time.
  - **Completion status** — already-completed tasks are excluded from the schedule. Recurring tasks (daily/weekly) are automatically reset when they are due again, so they re-enter the schedule on the correct day without manual intervention.
- How did you decide which constraints mattered most?
  - Time and priority were the most important because they directly affect pet welfare — a pet cannot skip medication because the owner ran out of time. Duration as a tiebreaker and recurrence handling were added second because they improve how many tasks actually get done each day without changing the core priority logic.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
  - The scheduler uses a greedy, single-track algorithm: it sorts all tasks by priority (then shortest duration), then walks the list and assigns each task the next available time slot — one after another. This means `detect_time_conflicts()` will never report a conflict in a normally-built schedule, because tasks are placed sequentially by construction and cannot overlap. A more realistic model would build a separate time track per pet (so Dog A's walk and Cat B's feeding run in parallel), which would expose genuine conflicts when the owner cannot physically do two things at once.
- Why is that tradeoff reasonable for this scenario?
  - For a single owner managing one or two pets, a sequential schedule is simple to read and easy to follow — the owner just works down the list. The complexity of parallel per-pet tracks is not worth the added confusion for the target user. The `detect_time_conflicts()` method is still correct and useful: it is ready to catch real overlaps if start times are ever assigned manually or if a multi-track scheduler is added later, without any changes to its logic.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
