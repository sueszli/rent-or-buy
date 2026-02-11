Quality:

- Match existing code style and architectural patterns.
- Zero Technical Debt: Fix issues immediately. Never rely on future refactoring.
- Keep it simple: No code > Obvious code > Clever code. Do not abstract prematurely.
- Locality over DRY: Prioritize code locality. Keep related logic close together even if it results in slight duplication. Prefer lambdas/inline logic over tiny single-use functions (<5 LoC). Minimize variable scope.
- Self-Describing Code: Minimize comments. Use descriptive variable names and constant intermediary variables to explain where possible.
- Guard-First Logic: Handle edge cases, invalid inputs and errors at the start of functions. Return early to keep the "happy path" at the lowest indentation level.
- Flat Structure: Keep if/else blocks small. Avoid nesting beyond two levels if possible.
- Centralize Control Flow: Branching logic belongs in parents. Leaf functions should be pure logic.
- Fail Fast: Detect unexpected conditions immediately. Raise Exceptions rather than corrupt state.

Testing:

- Contract based testing: use the `deal` library to specify contracts for each function. Prefer `deal.pure` functions. Use single-character variable names for contract arguments where possible.
- Use assert statements for simple checks.

Pre commit:

```bash
make precommit
```

Running code:

```bash
uv run src/main.py
```
