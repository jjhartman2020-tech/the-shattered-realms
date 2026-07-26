# Scripting

## Table of Contents

1. Purpose
2. Scripting Philosophy
3. Script Scope
4. Event-Driven Execution
5. Engine API
6. Script Safety
7. Performance
8. Debugging
9. Best Practices
10. Interaction With Other Systems
11. Summary

---

# Purpose

The Scripting framework defines how creators extend The Shattered Realms with custom logic while preserving engine stability and compatibility.

Scripts allow creators to implement unique mechanics, events, behaviors, and interactions that cannot be expressed through configuration alone.

The scripting system should complement the engine rather than replace its existing systems.

---

# Scripting Philosophy

Configuration should always be preferred over scripting when possible.

Creators should only write scripts when they require behavior beyond what the engine already supports.

Scripts should:

- Extend engine behavior.
- Reuse documented systems.
- Remain modular.
- Be predictable.
- Avoid modifying core engine functionality directly.

The engine should provide powerful scripting capabilities without requiring every campaign to include custom code.

---

# Script Scope

Scripts may control behavior that is unique to a campaign or content package.

Examples include:

- Custom quest logic.
- Puzzle mechanics.
- Interactive objects.
- Boss phases.
- Special abilities.
- World events.
- Dialogue conditions.
- Mini-games.
- Cutscene sequences.
- Dynamic environmental effects.

Scripts should not redefine systems already documented elsewhere unless the engine explicitly supports doing so.

---

# Event-Driven Execution

Scripts should respond to engine events instead of running continuously whenever possible.

Examples of events include:

- Campaign Started
- Player Joined
- Character Created
- Quest Accepted
- Quest Completed
- Dialogue Started
- Dialogue Ended
- Combat Started
- Combat Ended
- Character Defeated
- Item Acquired
- Item Used
- Enter Location
- Leave Location
- Time Advanced
- World Event Triggered

This event-driven approach improves performance, readability, and maintainability.

---

# Engine API

The engine should expose a documented scripting API that allows creators to safely interact with game systems.

Examples of supported actions include:

- Reading world data.
- Creating or removing entities.
- Updating quests.
- Modifying dialogue.
- Spawning encounters.
- Granting rewards.
- Changing reputation.
- Triggering world events.
- Scheduling future events.
- Reading campaign configuration.

The API should expose only supported functionality, preventing scripts from accessing internal engine components unnecessarily.

---

# Script Safety

Scripts should execute within a controlled environment.

The engine should:

- Validate scripts before execution.
- Prevent unauthorized access to engine internals.
- Restrict unsupported operations.
- Isolate script failures.
- Produce clear error reporting.

A failing script should not crash the entire campaign whenever recovery is possible.

---

# Performance

Scripts should be designed to minimize unnecessary resource usage.

Creators are encouraged to:

- Prefer event-driven logic.
- Avoid unnecessary repetition.
- Cache reusable information when appropriate.
- Limit expensive operations.
- Keep scripts focused on a single responsibility.

The engine may monitor script performance and report inefficient behavior to creators.

---

# Debugging

The engine should provide tools that simplify script development.

Useful debugging features include:

- Error messages.
- Stack traces.
- Event logs.
- Script logging.
- Validation reports.
- Performance metrics.
- Breakpoints (if supported by the scripting environment).

Debugging information should clearly identify the source of problems while remaining understandable to creators.

---

# Best Practices

Creators are encouraged to:

- Keep scripts modular.
- Reuse existing engine APIs.
- Avoid duplicating logic.
- Document complex behavior.
- Test edge cases.
- Separate configuration from code.
- Write scripts that remain compatible with future engine versions whenever practical.

Well-designed scripts should be easy to understand, maintain, and reuse.

---

# Interaction With Other Systems

The Scripting framework extends the engine without replacing existing systems.

Examples include:

- **Campaign Creation** organizes scripted campaigns.
- **Custom Content** supplies data consumed by scripts.
- **AI** interprets script-generated content within campaign rules.
- **Combat**, **World**, **Characters**, and **Quests** provide documented APIs that scripts may interact with.

Scripting adds custom behavior while preserving the responsibilities of every documented engine system.

---

# Summary

The Scripting framework provides creators with a safe, structured, and powerful way to extend The Shattered Realms.

By emphasizing event-driven execution, documented APIs, modular design, and strong engine safeguards, the framework enables highly customized experiences without sacrificing stability, compatibility, or maintainability.

Scripts should enhance the engine's capabilities while allowing the core systems to remain the authoritative source of game behavior.
