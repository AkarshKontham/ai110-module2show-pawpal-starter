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
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

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
