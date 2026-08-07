# Project Instructions for AI Agents

This file provides instructions and context for AI coding agents working on this project.

<!-- BEGIN BEADS INTEGRATION v:1 profile:minimal hash:7510c1e2 -->
## Beads Issue Tracker

This project uses **bd (beads)** for issue tracking. Run `bd prime` to see full workflow context and commands.

### Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --claim  # Claim work
bd close <id>         # Complete work
```

### Rules

- Use `bd` for ALL task tracking — do NOT use TodoWrite, TaskCreate, or markdown TODO lists
- Run `bd prime` for detailed command reference and session close protocol
- Use `bd remember` for persistent knowledge — do NOT use MEMORY.md files

**Architecture in one line:** issues live in a local Dolt DB; sync uses `refs/dolt/data` on your git remote; `.beads/issues.jsonl` is a passive export. See https://github.com/gastownhall/beads/blob/main/docs/SYNC_CONCEPTS.md for details and anti-patterns.

## Session Completion

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **PUSH TO REMOTE** - This is MANDATORY:
   ```bash
   git pull --rebase
   git push
   git status  # MUST show "up to date with origin"
   ```
5. **Clean up** - Clear stashes, prune remote branches
6. **Verify** - All changes committed AND pushed
7. **Hand off** - Provide context for next session

**CRITICAL RULES:**
- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds
<!-- END BEADS INTEGRATION -->


## WSL Environment

This project's tooling (including `bd`) lives inside **WSL**. Claude Code on this machine runs on Windows (PowerShell/win32), so `bd` must be invoked via the WSL wrapper — it is not on the Windows PATH.

### Invoking bd from Windows (win32 / PowerShell)

Always use the full WSL path:

```powershell
wsl bash -c '/home/morgan/go/bin/bd <command>'
```

Examples:

```powershell
wsl bash -c '/home/morgan/go/bin/bd ready'
wsl bash -c '/home/morgan/go/bin/bd show hq-i31'
wsl bash -c '/home/morgan/go/bin/bd create --title="..." --description="..." --type=task --priority=2'
wsl bash -c '/home/morgan/go/bin/bd close hq-i31'
```

### Invoking bd from WSL (linux / bash)

If Claude Code is running inside WSL, `bd` is available directly (the shell profile adds `/home/morgan/go/bin` to PATH):

```bash
bd <command>
```

### Notes

- Hooks in `.claude/settings.json` use `wsl bash -c '/home/morgan/go/bin/bd prime -C /mnt/d/programming/darklands_util'` — required for Windows (PowerShell) sessions
- `.beads/` directory should be `chmod 700` (WSL warns otherwise)

## Local Project References

Related projects on this machine. When the user pastes a path like `../vvendigo/darklands` or similar, these are the sibling directories they're referencing:

| Path | What it is |
|---|---|
| `D:\programming\vvendigo\Darklands` | Community reverse-engineering research: Python parsers (`reader_lst.py`, `reader_map.py`, `format_cty.py`, etc.), LZW/RLE decompression, and community notes from bay12forums, olemars, quadko, up-to-date, and wallace.net subdirs |
| `D:\programming\darklandscompanion` | Local copy of the [illusium77/darklandscompanion](https://github.com/illusium77/darklandscompanion) .NET solution — source of the saint prayer data used in `SaintData.kt` |
| `D:\programming\darkland_reference` | Archive files: original patches, zip utilities, a few save games, and `project_analysis.md` |

When the user pastes content from these paths, treat it as reference material for the Darklands binary format. The Python scripts in `vvendigo/Darklands` are especially useful as working format decoders to cross-reference against the Kotlin parsers in this project.

## Build & Test

```bash
# Maven (Kotlin)
mvn compile
mvn test
mvn exec:java   # runs Main.kt
```

## Architecture Overview

Kotlin/Maven utility that parses 1992 DOS RPG *Darklands* binary files and exports to JSON. Entry point: `src/main/kotlin/bm/darkland/Main.kt`. Game binary files live in `DARKLAND/`. See `README.md` for full file format notes and parser status.

## Conventions & Patterns

_Add your project-specific conventions here_
