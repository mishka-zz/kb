# Setting kb up in a project

Written for the agent asked to do it. `README.md` says what kb is for; read it
first, then `SKILL.md`, which is how the record is worked once it is here.
Below, `<kb>` is the directory holding this file and `<project>` the root of
the project taking kb on.

**Stop and ask** if `<project>/kb/` already exists and holds anything but a
record (a record is a `kb/` with a `project.md`), or if the user has not said
they want kb here. If `<project>/kb/project.md` already exists, kb is already
set up: check it (step 6) rather than install it again.

## 1. Reach the tool without copying it

The tool stays in `<kb>` and serves every project on the machine; a copy inside
a project would drift from it. Reach it one of two ways:

- **A link in the project** - `<project>/tools/kb -> <kb>`, relative where the
  two sit side by side. The command is then `tools/kb/kb.py`, which also works
  for anyone who clones the project next to a checkout of kb.
- **`kb` on the path** - `ln -s <kb>/kb.py ~/bin/kb`, or any directory on
  `PATH`. Machine-wide; ask before writing outside the project.

`kb.py` runs by its own `#!/usr/bin/env python3` line, so nothing that calls it
names an interpreter. It needs Python 3.9 or later and nothing else.

Below, `kb` means whichever command you chose.

## 2. Copy the skeleton

```
cp -R <kb>/kb.skel <project>/kb
```

It brings `project.md`, the queue directories (`noted/`, `analyzed/`,
`scoped/`, `done/`, `moot/`, `refused/`), `archive/`, the guidelines under
`known/guidelines/` and `run/`. Leave the guidelines as they are: each is tagged
`carried` until this project meets its own occasion for it.

## 3. Fill in `kb/project.md`

The head between the `---` lines is the only thing the tool reads from the
project. Every field is optional and comma-separated, and a path is written from
`<project>`. `schema.md` defines each; choose them by looking at the project:

| field | what to put there |
|---|---|
| `owned` | the top-level directories and files of the project's own code, tests, docs and vendored text - whatever a note may cite as `path` or `path::name` |
| `outside` | those of `owned` a checkout may lack: separate repositories, submodules, trees cloned on demand |
| `citers` | documents outside `kb/` that may carry a `[[id]]` reference - usually the agent instruction file |
| `documents` | documents read for what is true now - the agent instruction, a specification - so their citations are checked too; never an archive or a dated plan |
| `source` | code and docs that `kb note` and `kb find` search beside the notes |
| `skip` | directory names to pass over inside those - `vendor`, `node_modules`, `.venv` |
| `theirs` | subjects under `known/` about software the project depends on but does not own; empty until the first such note |
| `figure` | a regular expression for a measured quantity in the project's units; empty takes the default |
| `runners` | which test files the notes may cite, and what runs them - step 4 |

Under the head, replace the skeleton's prose with a few paragraphs a reader of
the record needs and the project's agent instruction does not give: which
trees are released separately, what the project measures and in what units,
which software it depends on and cannot change.

## 4. Running cited tests, if the project has tests

A note can rest on a test - `test: tests/test_cache.py::test_expiry` - and
`kb stale` re-runs it. How a test is run belongs to the project, so the record
holds a command for it under `kb/run/`. `kb/run/README.md` is the contract:
`--probe` once, then `<path> [<name>]` per test from `<project>`, exit 0 for
passed, 77 for skipped, anything else for failed, the last line printed being
the reason.

Write one command per kind of test the project has, make it executable, and
name it in `runners` as a filename pattern and the command:

```
runners: test_*.py run-pytest, *_test.go run-go-test
```

`run-program` in `kb/run/` is a sample for tests that are programs of their
own; keep it if it fits, delete it if not. `kb stale --dry-run` shows what would
run, without running it. With `runners` empty, `kb stale` runs nothing and
says so.

## 5. Point the project's agent at it

Add to the project's agent instruction (`CLAUDE.md`, `AGENTS.md`, or whatever
its agent reads), near the top, with the command from step 1:

````markdown
## The record

`kb/` is this project's record: what it has learned and what is still open.
Before the first piece of work in a session, run both:

```
tools/kb/kb.py rules   # every guideline
tools/kb/kb.py         # where things stand
```

`tools/kb/SKILL.md` is how to work the record; read it before writing to it.
````

Then add that instruction file to `citers` and `documents` in `kb/project.md`.
Anything the record's procedure should know about this project - which tree is
a release boundary, what a change there costs - goes in that instruction or in
`kb/project.md`, never in `<kb>`.

If the agent loads skills from a directory, a link to `<kb>` named `kb` there
makes `SKILL.md` the `kb` skill in every project on the machine. It is
machine-wide: ask first.

## 6. Check it

```
kb check            # ends "walkable" when the record is sound
kb                  # where things stand
kb stale --dry-run  # if runners is set
```

Mend `project.md` until `kb check` is clean. Whether `kb/` is committed with the
project is the user's call; kb works either way, and where it is committed a
pre-commit hook running `kb check` is the one way it runs unasked.

Then tell the user what you set up, which command reaches kb, and what you put
in `project.md`.
