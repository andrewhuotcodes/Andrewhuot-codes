# Project: Andrewhuot-codes

Personal planning and documentation repository.

## Stack

- Format: Markdown documents
- Version control: Git

## Workflow

- Always verify markdown formatting renders correctly before committing
- Use descriptive commit messages summarizing content changes
- Keep documents well-structured with clear headings and consistent formatting

## Code Style

- Use ATX-style headers (`#`, `##`, `###`) not Setext
- Use hyphens (`-`) for unordered lists, not asterisks
- Use fenced code blocks with language identifiers when applicable
- One blank line between sections, no trailing whitespace
- Tables must have aligned columns and header separators

---

# Claude Code Power-User Guide

> State-of-the-art techniques for maximizing Claude Code output.
> Updated for Claude Opus 4.6 and Claude Code 2026.

## 1. Writing an Effective CLAUDE.md

CLAUDE.md is loaded at the start of every session. It is the single highest-leverage configuration point. Every line competes for attention in the context window.

### Structure: WHAT, WHY, HOW

| Section | Purpose |
|---------|---------|
| **WHAT** | Tech stack, project structure, codebase map. Critical in monorepos. |
| **WHY** | Purpose of the project and its components. |
| **HOW** | Build commands, test runners, verification steps, branch conventions. |

### Rules of Thumb

- IMPORTANT: Keep it under 300 lines. Bloated files cause Claude to ignore instructions.
- Ask for each line: "Would removing this cause Claude to make mistakes?" If not, cut it.
- Use emphasis (`IMPORTANT`, `YOU MUST`) for critical rules to improve adherence.
- Do not duplicate what Claude can infer from reading code (standard conventions, obvious patterns).
- Do not use CLAUDE.md as a linter. Use hooks or real linters instead.
- Use `@path/to/file` imports to reference external docs without bloating the root file.
- Check CLAUDE.md into git so the whole team benefits. It compounds in value over time.

### Progressive Disclosure

Store detailed instructions in separate files and reference them:

```markdown
# CLAUDE.md
See @docs/architecture.md for system design.
See @docs/testing.md for test conventions.
See @docs/api-conventions.md for REST patterns.
```

Claude reads these on demand, keeping the context window lean.

### Placement Hierarchy

| Location | Scope |
|----------|-------|
| `~/.claude/CLAUDE.md` | All sessions, all projects |
| `./CLAUDE.md` | Project root (shared via git) |
| `./CLAUDE.local.md` | Project root (gitignored, personal overrides) |
| `./subdir/CLAUDE.md` | Pulled in when Claude works in that directory |

### Custom Compaction

Add compaction instructions so critical context survives summarization:

```markdown
When compacting, always preserve the full list of modified files,
test commands, and any architectural decisions made this session.
```

## 2. Skills

Skills extend Claude's knowledge with domain-specific info and reusable workflows. Unlike CLAUDE.md (loaded every session), skills load on demand.

### Create a Skill

Add a `SKILL.md` file in `.claude/skills/<skill-name>/`:

```markdown
# .claude/skills/fix-issue/SKILL.md
---
name: fix-issue
description: Fix a GitHub issue end-to-end
disable-model-invocation: true
---
Analyze and fix the GitHub issue: $ARGUMENTS.

1. Use `gh issue view` to get issue details
2. Search codebase for relevant files
3. Implement the fix
4. Write and run tests
5. Ensure linting and type checking pass
6. Commit with a descriptive message
7. Push and create a PR
```

Invoke with `/fix-issue 1234`.

### Useful Skill Ideas

- `/deploy` - Run deployment pipeline with safety checks
- `/review-pr <number>` - Structured PR review with security, performance, and test lenses
- `/build-feature <spec>` - Orchestrate feature implementation from spec to PR
- `/migrate <from> <to>` - Framework or library migration workflow
- `/investigate <symptom>` - Structured debugging workflow

## 3. Custom Subagents

Subagents run in their own context with scoped tools. They handle focused tasks without cluttering your main conversation.

### Define a Subagent

```markdown
# .claude/agents/security-reviewer.md
---
name: security-reviewer
description: Reviews code for security vulnerabilities
tools: Read, Grep, Glob, Bash
model: opus
---
You are a senior security engineer. Review code for:
- Injection vulnerabilities (SQL, XSS, command injection)
- Authentication and authorization flaws
- Secrets or credentials in code
- Insecure data handling

Provide specific line references and suggested fixes.
```

### Other Useful Subagents

- **test-writer** - Generates tests for changed files
- **doc-writer** - Produces documentation from code
- **perf-analyzer** - Profiles and identifies bottlenecks
- **migration-checker** - Validates migration safety

## 4. Ralph Wiggum Loops

The Ralph Wiggum technique is an autonomous iteration loop. Claude repeatedly works on a task, attempts to exit, gets intercepted by a stop hook, and re-reads the prompt to continue refining.

### Setup

```bash
/plugin install ralph-loop@claude-plugins-official
```

### Usage

```bash
/ralph-loop "Implement the auth module with full test coverage. \
Run tests after each change. Fix all failures." \
--completion-promise "ALL_TESTS_PASSING" \
--max-iterations 15
```

### Best Practices

- IMPORTANT: Always set `--max-iterations` as a safety net.
- Define explicit, verifiable completion criteria (test pass, build success, lint clean).
- Break complex tasks into sequential phases rather than one monolithic prompt.
- Use for mechanical, well-defined work: migrations, test writing, bug fixes, boilerplate.
- Avoid for subjective design decisions or tasks requiring human judgment.
- Run overnight with `--max-iterations` for large-scale automation ("all-in-AFK").

### Advanced Patterns

- **Parallel worktrees**: Run multiple Ralph loops on different features simultaneously using `git worktree`.
- **Multi-phase chains**: Queue sequential loops (phase 1: scaffold, phase 2: implement, phase 3: test).

## 5. Agent Teams

Agent teams coordinate multiple Claude Code instances with shared tasks, messaging, and a team lead.

### Enable

```json
// settings.json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

### Architecture

| Component | Role |
|-----------|------|
| **Team lead** | Creates team, spawns teammates, coordinates work |
| **Teammates** | Independent Claude instances working on assigned tasks |
| **Task list** | Shared work items teammates claim and complete |
| **Mailbox** | Inter-agent messaging system |

### Example: Feature Implementation Team

```
Create an agent team to build the payment integration:
- Teammate 1: Backend API endpoints (use Sonnet)
- Teammate 2: Frontend components (use Sonnet)
- Teammate 3: Integration tests (use Sonnet)
- Lead: Coordinate on Opus, require plan approval before implementation
```

### Example: Parallel Code Review

```
Create an agent team to review PR #142:
- Reviewer 1: Security implications
- Reviewer 2: Performance impact
- Reviewer 3: Test coverage and edge cases
Synthesize findings when all reviewers finish.
```

### Example: Competing Hypotheses Debugging

```
Users report the app crashes on login. Spawn 4 teammates to investigate
different hypotheses. Have them debate and disprove each other's theories.
Update findings when consensus emerges.
```

### Best Practices

- Use **delegate mode** (Shift+Tab) to prevent the lead from implementing instead of coordinating.
- Size tasks as self-contained units producing a clear deliverable (a function, a test file, a review).
- Avoid file conflicts: each teammate should own a different set of files.
- Mix models: Opus for the lead (strategic), Sonnet for teammates (execution).
- 5-6 tasks per teammate keeps productivity high and allows reassignment.
- Use plan approval for risky tasks: "Require plan approval before making changes."
- Pre-approve common permissions before spawning to reduce prompt interruptions.

## 6. Combining Ralph Loops + Agent Teams

The hybrid pattern covers both creative and mechanical work:

| Track | Technique | Purpose |
|-------|-----------|---------|
| **Docs/Design** | Agent Teams | Creative decisions, API design, test strategy with human review |
| **Implementation** | Ralph Loops | Mechanical iteration in isolated worktrees until tests pass |
| **Validation** | Build-validator subagent | Verifies the integrated result |

Orchestrate via a custom skill (`/build-feature`) that acts as the team lead.

## 7. Hooks

Hooks run scripts automatically at specific points in Claude's workflow. Unlike CLAUDE.md instructions (advisory), hooks are deterministic.

### Useful Hook Patterns

```bash
# Run eslint after every file edit
claude hooks add PostToolUse "eslint --fix $FILE" --tool Edit

# Block writes to sensitive directories
claude hooks add PreToolUse "exit 1" --tool Edit --pattern "migrations/*"

# Auto-format on save
claude hooks add PostToolUse "prettier --write $FILE" --tool Write
```

### Agent Team Hooks

- **TeammateIdle**: Runs when a teammate finishes. Exit code 2 sends feedback and keeps them working.
- **TaskCompleted**: Runs when a task is marked complete. Exit code 2 prevents completion.

## 8. Workflow Patterns

### Explore > Plan > Implement > Commit

1. **Explore** (Plan Mode): Read files, understand the codebase.
2. **Plan** (Plan Mode): Create a detailed implementation plan. Press Ctrl+G to edit.
3. **Implement** (Normal Mode): Execute the plan with test verification.
4. **Commit**: Descriptive message and PR.

### Writer/Reviewer Pattern

| Session A (Writer) | Session B (Reviewer) |
|---------------------|----------------------|
| Implement the feature | Review for edge cases, security, patterns |
| Address review feedback | Verify fixes |

### Interview-Driven Development

```
I want to build [feature]. Interview me using the AskUserQuestion tool.
Ask about technical implementation, UX, edge cases, and tradeoffs.
Keep going until we've covered everything, then write a spec to SPEC.md.
```

Start a fresh session to implement the spec with clean context.

### Fan-Out Pattern

```bash
for file in $(cat files.txt); do
  claude -p "Migrate $file from framework A to B. Return OK or FAIL." \
    --allowedTools "Edit,Bash(git commit *)"
done
```

### Model Mixing

- **Opus** for planning, architecture, complex reasoning
- **Sonnet** for focused implementation, execution, and batch work

Switch with `/model` during a session. Plan on Opus, implement on Sonnet.

## 9. Context Management

Context is the most important resource. Performance degrades as the window fills.

- `/clear` between unrelated tasks
- `/compact <focus>` to summarize with specific focus (e.g., `/compact Focus on API changes`)
- `/rewind` to restore conversation and code state to any checkpoint
- Use subagents for research to keep the main context clean
- Scope investigations: "Use a subagent to investigate how auth handles token refresh"
- Track context usage with a custom status line

## 10. Common Anti-Patterns to Avoid

| Anti-Pattern | Fix |
|-------------|-----|
| Kitchen sink session (mixing unrelated tasks) | `/clear` between tasks |
| Correcting over and over (>2 corrections) | `/clear` and write a better prompt |
| Over-specified CLAUDE.md (>300 lines) | Prune ruthlessly, use skills for specifics |
| Trust-then-verify gap | Always provide tests, scripts, or screenshots |
| Infinite exploration | Scope investigations or use subagents |
| Skipping verification | Include `run tests` in every implementation prompt |
