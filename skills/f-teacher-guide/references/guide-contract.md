# Student Guide Contract

## Audience and time

Declare the audience baseline, scheduled hours, prerequisite time outside class, and a conservative completion route. A required classroom path should fit the weakest plausible student who completed the prerequisites.

## Package root

- Use one English ASCII root directory per distributable archive.
- Keep all required inputs, code, data, guides, record templates, verification scripts, and reference evidence inside that root.
- Commands begin from the package root unless a step explicitly changes directory.
- Distinguish bundled inputs from generated outputs. Generated paths such as `results/`, `ros2_ws/build/`, `ros2_ws/install/`, and `ros2_ws/log/` need not exist before execution.
- Never reference another experiment root, a teacher's absolute workstation path, or a hidden dependency.

## Step anatomy

Every required step contains:

1. a concrete student-facing title;
2. the purpose in plain language;
3. the exact starting terminal/application state;
4. exact commands or click sequence in execution order;
5. an observable success criterion with filenames, output text, window state, or numeric range;
6. one focused screenshot or result image that matches that criterion;
7. a recovery path based on the first meaningful failure;
8. the output that feeds the next step.

## Command granularity

- Present exactly one executable command in each code block or numbered command row.
- Keep every command on one physical line. Do not use line-continuation backslashes in student-facing commands.
- Do not join distinct student actions with `&&`, `;`, or an explanatory shell comment. Split `cd`, environment activation, build, inspection, and launch into separate numbered commands.
- Pair each command with its own starting state and immediate observable result. When a command intentionally keeps running, say which terminal owns it and how the student knows it is ready.
- The test ledger must execute the exact displayed command string. It may provide the surrounding test fixture, such as an isolated `HOME`, but must not rewrite, normalize, shorten, or replace the command.

Do not ask students to infer omitted setup, silently switch terminals, overwrite a baseline with a comparison, edit result JSON by hand, or install packages ad hoc into the wrong environment.

## Evidence labels

- Real execution output: say it is captured from the executed package.
- Real GUI/RViz screenshot: say it is an actual capture and ensure the visible state proves the claim.
- Expected-success reference: use only when the target platform cannot be executed locally; label it explicitly and avoid machine-specific version claims.

## Assessment

Use deterministic acceptance where possible: resource check, build exit code, named output files, numeric thresholds, schema validation, and a structured record. For a two-hour introductory practice, one baseline plus one single-variable comparison can be sufficient. For a four-hour experiment, normally require a baseline plus at least three additional levels of one variable, a result table or trend plot, and questions that require the student to describe the observed trend, identify an exception or turning point, and justify a parameter choice. Give the run values and exact modification method, but do not state the expected direction or answer.

## Real-machine gate

- Test from a freshly extracted final archive, not from the development tree.
- Record machine/OS, target platform, Conda environment, archive SHA-256, and start/end time.
- Execute all required command rows in order and record exit status plus expected evidence for each.
- An actual GUI/device step requires visible-state evidence. A running process, config-file parse, or `--help` output is only a partial check.
- If the intended classroom platform cannot be tested, mark that platform-sensitive step unverified and do not claim full completion.
