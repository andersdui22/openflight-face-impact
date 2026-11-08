# OPENFLIGHT FACE IMPACT - PROJECT LAW V1

Version: 1.0 · 2026-11-08
Status: ADOPTED for this project by Anders Nørgaard's approval of Gate 01
(`Det er godkendt. Fortsæt`, 2026-11-08).
Authority: the user's Initial Work Handoff V1 and the currently approved
Active Change Gate. Phase 0 does not authorize later product phases.

## 1. Mission and scope

Develop a standalone Windows desktop application using one ELP OV9281 USB camera to determine and visualize clubface impact location. Reuse appropriate OpenFlight Python, React/Electron, capture, calibration and geometry work before writing equivalents.

Allowed domains are Windows bootstrap, USB camera acquisition, calibration, impact-frame acquisition, clubhead geometry/pose, ball and face localization, impact calculation/visualization, tests, CI and approved packaging. ConnectorNext, MLM2PRO, Bluetooth protocols, radar hardware requirements and unrelated OpenFlight work are outside scope. Retaining upstream source files for history is not permission to develop their out-of-scope subsystems.

## 2. Authority and approval

After creation, verified GitHub state is authoritative for repository contents, branches, PRs, checks and HEADs. A handoff is a dated snapshot. User instructions and explicit authorizations remain authoritative for scope and permissions.

The Active Change Gate must identify its approval evidence, base SHA, allowed files/behaviors, excluded work, acceptance criteria and stop conditions. A proposed or expired gate grants no implementation permission. No production-code change is allowed before a read-only startup audit and explicit approval of the relevant gate.

Approval of one gate does not approve another gate. A gate does not implicitly authorize merging, publishing, releases, physical tests, destructive operations or sending messages to third parties. Initial repository creation and baseline seeding must be expressly included in Gate 01 approval; seeding is not permission for later merges.

## 3. Evidence before implementation

For each task: state the concrete problem, inspect the existing implementation and tests, search for duplicates, collect technical evidence, identify the smallest justified change and record remaining unknowns. Source presence, PR prose, author test reports, CI and physical measurements are distinct evidence classes.

UNKNOWN remains UNKNOWN. Never substitute zero, a generic category model, assumed speed, nominal lens, square face or inferred orientation for missing measurements without an explicit label and uncertainty policy. A converged fit, plausible overlay, generated clip or passing unit test is not physical accuracy evidence.

Record repository, immutable SHA, path, relevant lines or symbol, observation, evidence class and scope of inference. Record source asset origin, license, hash, units, handedness and transforms. Do not assume Discord statements, branch names or screenshots imply merged public code.

## 4. Protect existing behavior and provenance

Preserve existing proven behavior and test expectations. Make only necessary local structural changes. No broad refactor, wholesale rewrite, opportunistic dependency upgrade, unrelated cleanup, public-contract change or renaming outside an approved gate.

Maintain upstream Git history, origin reference, attribution and applicable AGPL-3.0-or-later terms. Track third-party code, assets and notices separately. Never redistribute the restricted 690CB STL/NPZ or revive a retired mesh as canonical truth without a new asset admission decision. Models are not physically verified merely because their files parse.

Use non-destructive Git operations. No force-push, history rewrite, destructive reset/clean, remote branch deletion, overwriting others' work or bypassing protections. If destructive work becomes necessary, stop for specific approval. Work on the approved project repository only; ConnectorNext remains untouched.

## 5. Anti-duplication and architecture

Before adding a function, module, UI or framework, search official main, admitted experimental code, tests and the candidate register. Reuse or narrowly adapt equivalent code when technically and legally suitable. Record why a new implementation is necessary when reuse is rejected.

Keep one React/Electron UI and the existing service/store/API conventions. Keep acquisition, estimation, orchestration and persistence responsibilities explicit. UI components may render and manage interaction; new measurement/business logic belongs in backend services or suitable pure domain modules. Do not force an unrelated framework or duplicate an entire backend/UI to create the Windows entry point.

One acquisition owner supplies preview and buffered frames. Post-shot processing must not own or block camera acquisition. Slow analysis has bounded queues/cancellation and shot/session identity checks. Hardware-specific metadata must retain honest timing semantics; a host-arrival clock must not be called a sensor-exposure timestamp.

## 6. Read-only startup audit

Every successor session, and every resumed implementation gate after remote drift, must read Project Law, the Active Change Gate, handoff, baseline registry and relevant local instructions. Verify current remote default/head and gate-branch SHA, repository cleanliness, open PRs, CI/checks on their exact SHAs, relevant commits and source/asset dependencies.

Reconcile differences before editing. If changes are outside the approved scope, approval is missing, evidence is inconsistent or a dependency/license is unknown, fail closed on that action. Continue independent authorized read-only work and document the blocker; do not silently open a new gate.

## 7. Implementation and verification

Every change has a documented purpose, meaningful tests appropriate to its behavior, and recorded evidence. Run focused tests first, then relevant regression checks and GitHub CI. Classify failures as introduced, pre-existing, environmental, unavailable hardware or unknown; supply evidence rather than weakening tests.

Existing skips, mocks and fixtures must remain visible. Do not claim functional Windows coverage from a React build, physical camera coverage from mocks, or Face Impact precision from syntax/geometry tests. A test requiring restricted or absent data must fail or skip with the true reason; never manufacture expected measurements.

Use CI economically: inspect existing same-SHA results, consolidate a coherent change before requesting a run, and rerun only when a change or diagnosed transient failure justifies it. Never trigger a release workflow under test authorization.

## 8. Same-SHA closeout

Before closing a gate, fetch the remote gate HEAD and verify it is the exact SHA reviewed and tested. Record PR head/base, required checks, job conclusions and artifact provenance. If source or configuration changes after tests, rerun the affected checks on the new SHA.

A build is identified by app SHA, source/asset/dependency manifests and build workflow/run. CI test success is not merge approval. Artifacts created by different SHAs must not be mixed. An open draft PR is not a closed gate or release.

Close only when the acceptance criteria are satisfied or an explicitly approved amendment defines the disposition of a known baseline limitation. Record remaining out-of-gate unknowns without implying they passed.

## 9. Golden Baselines

No Golden baseline exists at project initialization. An immutable upstream source snapshot is a SOURCE_BASELINE, not GOLDEN_PHYSICAL.

A Golden nomination needs explicit user approval plus a reproducible evidence bundle: app SHA, hardware and lens IDs, resolution/mode, exposure/gain and timing source, calibration identity, environment, test procedure, independent reference, attempt denominator, outcomes and known limits.

Protect Golden references against overwrite and deletion. Future changes must run the applicable regressions. Simulated tests alone never establish startup, camera acquisition, live-preview, calibration, impact detection, physical geometry, physical Face Impact or Windows-package Golden status.

## 10. Physical work, merges and releases

Stop for explicit authorization before a physical hardware test. Agree the procedure and required user participation; do not access a local camera or ask for swings under a software-only gate. Do not claim background execution when the Work session ends.

Never merge, enable auto-merge, publish or release without explicit authorization naming the concrete action and reviewed result. Release readiness requires a same-SHA build, relevant CI, documented clean-Windows checks, applicable physical acceptance, source availability and licensing/notices.

## 11. Knowledge rebuild and future handoff

Maintain concise evidence, decision, candidate, test and baseline registers alongside the code. Keep implemented, experimental, missing and unverified states separate. Record retracted findings and corrected replacements without carrying forward invalid conclusions.

Every handoff records repository/branch; verified remote HEAD and time; law version; gate and authorization; open PRs; latest same-SHA CI; completed phases; Golden baselines; tests/evidence; unresolved questions; blockers; and the next authorized task. Include exact commands or procedures where needed, but no credentials.

A successor must verify GitHub and reconcile drift before acting. If authority or evidence cannot be rebuilt, permitted activity is read-only investigation and reporting until resolved.

## 12. Amendment

Only an explicit user-approved amendment changes this law or expands a gate. Record the previous version, reason, decision and effective scope. Neither urgency, a long plan nor a green CI run grants authority to waive these rules.
