# Workflow Orchestration

## 1. Plan Node Default
- Enter plan mode for ANY non-trivial task (3+ steps or architectural decisions)
- If something goes sideways, STOP and re-plan immediately – don't keep pushing
- Use plan mode for verification steps, not just building
- Write detailed specs upfront to reduce ambiguity
- Before starting a new task, check always reference documentation in `documentation/codebase` to understand codebase architecture and conventions.

## 2. Subagent Strategy
- Use subagents liberally to keep main context window clean
- Offload research, exploration, and parallel analysis to subagents
- For complex problems, throw more compute at it via subagents
- One tack per subagent for focused execution

## 3. Self-Improvement Loop
- After ANY correction from the user: update `workflow/tasks/lessons.md` with the pattern
- Write rules for yourself that prevent the same mistake
- Ruthlessly iterate on these lessons until mistake rate drops
- Review lessons at session start for relevant project

## 4. Verification Before Done
- Never mark a task complete without proving it works
- Diff behavior between main and your changes when relevant
- Ask yourself: "Would a staff engineer approve this?"
- Run tests, check logs, demonstrate correctness

## 5. Demand Elegance (Balanced)
- For non-trivial changes: pause and ask "is there a more elegant way?"
- If a fix feels hacky: "Knowing everything I know now, implement the elegant solution"
- Skip this for simple, obvious fixes – don't over-engineer
- Challenge your own work before presenting it

## 6. Autonomous Bug Fixing
- When given a bug report: just fix it. Don't ask for hand-holding
- Point at logs, errors, failing tests – then resolve them
- Zero context switching required from the user
- Go fix failing CI tests without being told how


---

# Task Management

1. **Plan First**: Write plan to `workflow/tasks/todo.md` with checkable items.
2. **Verify Plan**: Check in before starting implementation
3. **Track Progress**: Mark items complete as you go
4. **Explain Changes**: High-level summary at each step
5. **Document Results**: Add review section to `workflow/tasks/todo.md`
6. **Capture Lessons**: Update `workflow/tasks/lessons.md` after corrections

---

# Core Principles

- **Simplicity First**: Make every change as simple as possible. Impact minimal code.
- **No Laziness**: Find root causes. No temporary fixes. Senior developer standards.
- **Minimal Impact**: Changes should only touch what's necessary. Avoid introducing bugs.



# Project Context
Architecture: @documentation/codebase/architecture.md
Conventions: @documentation/codebase/conventions.md

# Accumulated Lessons
@workflow/tasks/lessons.md

# Task Workflow
1. Write plan to `workflow/tasks/todo.md` with checkable items
2. Verify with user before implementing
3. Mark items complete as you progress
4. After any user correction, append the lesson to `workflow/tasks/lessons.md`


## Project Specific Guidelines

Give engine architeture examples so claude.md understands my logic in terms of framework/code logic architecture- modular systems modelling approach

engineering / modelling agent / systems engineer agent

Structure to code like the physical systems youre trying to model are build - parts (code lines and functions) which make up subcomponents (functions/classes) which again make up subsystems (classes) which finally make up a system (class) 

Think: 3 stage rocket - 3 individual systems - each of whixh consists of engines, actuators, gnc , airframe , - some of these consist of smaller subcomponents like nozzle , turbine, HX, airframe (fuel tank) - compressor (blades)

Each system/component etc has various properties (FlowState, Geometry, HXResult?, Properties/Specs/Characteristics (efficiency, mass, etc)

How to organise/categorise all possible spexs/properties logically and practically? 

Style

Inheritance 

Rather many scripts thab long scripts 

Modular

Represents the physical system im modelling

«Digital model»

Easy to read

Class

varianle_