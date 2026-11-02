# kb

A project's memory, kept next to its code.

kb is a small command-line tool and a set of rules for keeping notes about a
project: what you have found out, what you tried and dropped, and what is still
open. The notes are plain Markdown files in a `kb/` folder, one note per file.

It is made for working with a coding agent. The agent writes and reads the
notes as it works. You can read them too: they are just text.

## Why

Code shows what a program does. It does not show:

- why it is done this way and not another;
- what was tried and did not work;
- what somebody else's library really does, as opposed to what its docs say;
- how sure you are of a number, and how you know.

That usually lives in old chats and in someone's head. An agent forgets it when
its context fills up. A person forgets it in a few months. Then the same
question gets answered again, or a rejected idea comes back.

kb keeps it in the project. Each note says what would prove it wrong: a test, a
measurement, a reason. `kb check` points out notes that refer to code which has
since changed or gone, and `kb stale` re-runs the tests notes rely on.

## The idea

An agent works best with context that is complete but narrow: everything the
task in hand needs, and nothing else. kb is built to hand it exactly that - the
project's rules, and the few notes linked to the task - rather than the whole
history.

But context can be wrong. A note was true the day it was written; since then the
code may have moved, or the measurement may have been off. So the agent is never
asked to obey a note. It is expected to doubt it, check it, and fix or close it
when it no longer holds. That is why every note says what would prove it wrong,
and why a corrected note is the record working, not failing.

## Your agent learns from its own work

After a long session, ask your agent for an after-action review (AAR): what it
expected, what actually happened, what would have been cheaper to know first,
and what applies beyond this task. The answers go into kb - as open questions,
and, when a lesson is general, as a guideline. The agent reads every guideline
at the start of the next session, so the same mistake is not made twice.

kb itself grew out of personal work on very large software projects that ran
for many months, and the guidelines a new project starts with were learned
there, this way.

## Use it when

- the project will take many sessions with an agent;
- the work involves finding things out: measuring, comparing, trying ideas;
- you depend on other people's software and learn how it behaves by testing it;
- you keep re-discovering the same facts, or re-proposing ideas already turned
  down.

## Don't use it when

- it is a short script or a one-off job;
- the code and its comments already say everything worth knowing;
- you only need a to-do list - an issue tracker is simpler;
- nobody will read it. Notes nobody looks at are just overhead.

## Getting started

Clone this repository once, anywhere on your machine. Then, in your project,
tell your agent something like:

> There is a tool in ~/src/kb. Read it, work out what it is, and set it up for
> this project.

The agent follows [INSTALL.md](INSTALL.md). From then on it starts each session
by reading the rules and the current state, and keeps the notes as it works.

You can use it by hand as well:

```
kb                      where things stand: what is open, what is known
kb note "a thought"     write something down
kb find cache timeout   search the notes
kb check                do the notes still match the code?
kb --help               everything else
```

## Related work

- [AGENTS.md](https://agents.md/) - the common place for instructions to a
  coding agent. kb sits beside it: the instruction says where things are, kb
  what is known and what is open.
- Gloaguen et al., [Evaluating AGENTS.md](https://arxiv.org/abs/2602.11988) -
  agents follow context files well, but the files rarely help and cost more: a
  standing context has to earn its place.
- Badhe, Tiwari and Chung, [SKILL.state](https://arxiv.org/abs/2608.26263) - a
  structured, editable record of progress instead of a context that keeps
  growing.
- Tang et al., [WikiSkill](https://arxiv.org/abs/2608.27454) - turning an
  agent's experience into a persistent wiki its later work draws on.
- Shinn et al., [Reflexion](https://arxiv.org/abs/2303.11366) - agents that get
  better by reflecting on their own failures.
- Michael Nygard, [Documenting Architecture Decisions](https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions) -
  decision records; a kb decision is a close relative.
- [After-action review](https://en.wikipedia.org/wiki/After-action_review) -
  the practice the review above is named after.
- [Cline Memory Bank](https://docs.cline.bot/prompting/cline-memory-bank) -
  Markdown files that carry a project's context across an agent's sessions.
- [Beads](https://github.com/steveyegge/beads) - an issue tracker built for
  coding agents: a graph of tasks rather than a record of what is known.
- [Obsidian](https://obsidian.md/) - a notes app over a folder of linked
  Markdown files, for a person's own knowledge.

## Read more

- [INSTALL.md](INSTALL.md) - setting kb up in a project (written for the agent)
- [SKILL.md](SKILL.md) - how to work with the notes (written for the agent)
- [schema.md](schema.md) - the file format
- [DESIGN.md](DESIGN.md) - why it works the way it does

Needs Python 3.9 or later on Linux, macOS or another POSIX system, and nothing
else. BSD 2-clause license, see [LICENSE](LICENSE); the skeleton a project
copies, `kb.skel/`, is 0BSD ([LICENSE.0BSD](LICENSE.0BSD)), so it is yours
once copied.
