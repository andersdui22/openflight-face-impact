# Experimental source candidates

Pinned source is evidence for a future admission decision, not a dependency
of the current branch. None of these candidates has been imported.

| Candidate | Exact head | Status and relevant contents | Admission concern |
| --- | --- | --- | --- |
| [Upstream PR #245](https://github.com/open-flight/openflight/pull/245) | `c0da896d141c4b10e1db100d16b03403b406a7c2` | Open, unmerged; mesh normalization, calibrated projection and stationary-ball fit. | 690CB mesh absent/restricted; no shot-pipeline wiring. |
| [Upstream PR #250](https://github.com/open-flight/openflight/pull/250) | `8d244e25e41764bdeb5665a812af40ccf2e37b16` | Open draft, unmerged; stacked on #245; pose, angles, scoring. | Orientation/impact accuracy unvalidated; coordinate/handedness history matters. |
| `HarjotDhanota/openflight` `codex/integrate-continuation` | `f8be8a5f01cc78c945ae04d506d80270b7bcbf54` | Public integrated experimental checkpoint, 2026-10-25. | Interface dependencies and test coverage to inspect before selection. |
| `HarjotDhanota/openflight` `agent/inspection-camera-2026-11-06` | `ea95a64329e5bbea52f901e3badb1cb07995a6fc` | Public newer archival checkpoint with Face Impact UI, range and worker. | Commit explicitly says WIP; tests/hooks not run, no returned checks. |
| `HarjotDhanota/openflight` `feat/clubpose-impact-zone` | `8ad885522a985ca5fd25b0e64026d02e1730dea0` | Additional conditional clubpose geometry experiments. | No physical strike validation. |

PR #250 is stacked on #245 against an older base, and fork checkpoints may
contain later or divergent implementations. Compare complete dependency sets
and corrected findings by immutable SHA; never combine files by name alone.
The newer `resting_ball_range` route can estimate ball range from known ball
size and calibrated rays, but does not validate moving-head depth or impact.

The 690CB STL and normalized NPZ are **not distributable** under the
contributor's recorded admission boundary; a retired driver asset is not a
substitute. Real club models, lens calibration and reference data remain
unverified. Full inventory and evidence links: `docs/evidence/PHASE0_AUDIT.md`.
