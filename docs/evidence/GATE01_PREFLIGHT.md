# Gate 01 preflight and verification record

Status: local preparation only, 2026-11-08. Do not mark the gate closed.

## Authorization and source

The user approved the concrete Gate 01 request with `Det er godkendt.
Fortsæt`. Source preflight: `open-flight/openflight` `main` ref returned
`a3ab081a8abff71fd344d4fd782412d624b99f3f`; local full-history partial
clone reports the same `HEAD`. PR #245 remained open at
`c0da896d141c4b10e1db100d16b03403b406a7c2`, PR #250 remained draft at
`8d244e25e41764bdeb5665a812af40ccf2e37b16`, and the public November
checkpoint remained `ea95a64329e5bbea52f901e3badb1cb07995a6fc`.

Target `andersdui22/openflight-face-impact` initially returned 404. The
connected installation lists only `andersdui22` as owner and only an
unrelated selected repository, which is outside scope and untouched. The
GitHub connector lacks repository creation. The browser login initially
failed in the chosen Google flow, then the user completed login. GitHub's
fork form created the new public repository from official main, copying the
main branch. The new fork reports that same baseline SHA and 1,369 commits.
The first branch attempt returned 403 `Resource not accessible by integration`,
and `git push --dry-run` had no terminal credentials. Anders then selected this
specific public fork in the existing GitHub installation without selecting
all repositories. The branch creation succeeded at the source SHA. The
foundation content has not yet been published.

## CI review and design

Existing source workflows: `pytest.yml` runs Python 3.10–3.12 tests on PR;
`ui-build.yml` runs UI build/lint/format/e2e; `pylint.yml` and `pr-checks.yml`
check source quality and PR metadata; `anti-slop.yml` is read-only audit mode.
`docs.yml` builds on docs PR and includes a GitHub Pages **deploy** job on
main push. The foundation diff removes that deployment job in this project.
The new foundation workflow adds a strict allowlist against the immutable
source commit, the existing UI unit tests on Linux, a Windows UI build and
focused pure geometry tests with an isolated uv environment. It has only
`contents: read` and no release or publishing steps. Existing PR checks supply
the broader Linux test/build coverage without duplicating jobs.

Windows diagnosis intentionally avoids the inherited project resolver because
`pyproject.toml` declares only Linux and macOS. The focused test uses existing
pure geometry code with `uv --no-project`; it does not imply the backend or
Electron app starts on Windows. Platform support belongs to a later gate.

## Local verification completed

- `git diff --check`: pass. `git diff --exit-code` against the immutable source
  commit for `src/openflight`, `ui`, `tests`, `config`, `scripts`,
  `pyproject.toml`, `uv.lock` and `LICENSE`: pass, no application or license
  delta. The full allowed diff contains 12 governance/documentation/CI files.
- `uv run --extra camera pytest tests/ -q --tb=short`: **2,079 passed,
  7 skipped, 9 warnings** on local Linux/Python 3.11 in 73.52 seconds. Skips
  and warnings remain reported, not reclassified as hardware coverage.
- `PYTHONPATH=src uv run --no-project --python 3.12 --with pytest --with
  numpy --with pyserial python -m pytest tests/test_camera_geometry.py -q`:
  **2 passed, 1 warning** on local Linux/Python 3.12. The first isolated run
  lacked `pyserial` and failed during package-import collection. The CI test
  command now declares that dependency; this was a test-environment setup
  error, not a product-code failure. Windows execution remains pending.
- `cd ui && npm ci && npm run test && npm run lint && npm run build && npm run
  format:check`: **48 test files and 248 UI tests passed; lint, build and
  formatting passed** on local Linux/Node 24.22.1.
- `uv run --group docs zensical build --clean --strict`: pass, no issues on
  local Linux. Foundation workflow parsed as `source-scope`, `ui-unit-linux`
  and `windows-diagnostics`. The removed Pages deployment job was the only
  publication step identified in the inherited workflows; the existing UI
  workflow may upload failed E2E test artifacts, not release binaries.

## Remote closeout still required

- Remote project baseline and foundation branch exist at the audited source
  SHA. Foundation content, PR, project check runs and final same SHA: **none**.
- Failures: classify as introduced/pre-existing/environmental/hardware/unknown.
- Physical camera test: not authorized; no result.
- Merge and release: not authorized.
