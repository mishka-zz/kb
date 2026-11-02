# Running a cited test

A `test:` citation is evidence only while the test still passes, so `stale`
runs it. How a test is run - which toolchain, which interpreter, from which
directory - is the project's business rather than the tool's, so it lives here,
in a command the project owns, one per kind of file.

Which cited files are tests, and which command here runs each, is the
`runners` field of `kb/project.md`: a pattern matched against the file's name
and the name of a command in this directory, a pair at a time and tried in
order -

```
runners: test_*.py run-pytest, *_test.go run-go-test
```

`run-pytest` and `run-go-test` there are commands the project writes for
itself; none comes with kb. A path no pattern matches is a mention and run by nothing. A record without the
command a citation needs has that citation counted as not run, and so does
every citation in a record naming no runner.

`run-program` is a sample, for the plainest kind of test: an executable file
that exits 0 when it passes, 77 when it is skipped and anything else when it
fails. Route the files that are such programs to it - `*.test run-program` -
or write the command your test framework wants in its place.

## The contract

```
<command> --probe            once per run, before any test
<command> <path> [<name>]    once per cited test
```

Both are run from the project root - the directory holding `kb/`.

**`--probe`** asks whether the toolchain is there. Exit 0 and print what will
run the tests; exit anything else and print, on one line, why it is not. A
toolchain that is not there is then said once, and every test it owned is
counted as not run - rather than each of them going red over the same absence.

**`<path> [<name>]`** runs one citation. `<path>` is the file as the citation
writes it, from the project root. `<name>` is whatever followed the `::`, and is
absent when nothing did. What the command makes of the name is its own
business, but `kb check` holds a citation to it first: in a Python or Go file
the name must be defined there, and in a file of any other kind it must at
least appear in the file as a word. The exit status is the verdict:

| exit | verdict | |
|---|---|---|
| 0 | green | the test ran and passed |
| 77 | not run | it was skipped, or there was nothing to run it with |
| anything else | red | it failed, did not build, or ran nothing while saying `ok` |

The last line printed on standard output is what the verdict is reported
with; standard error is read only when nothing was printed on standard output.
Standard input is empty: a test that asks for input reads end of file. A skip is 77 and
never 0, because a skip is the absence of evidence and must not print like the
presence of it; a run that matched no test is red for the same reason.

A command neither times out nor retries. The caller holds the clock.
