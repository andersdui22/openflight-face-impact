# Phase 2 Gates 10–11 — Windows packaging and UI acceptance

**Status: implementation in progress; NOT accepted or released.**
User authorized completing Gates 09–11 as one development batch on 2026-11-10, with CI fixes afterwards. No merges, releases or physical tests authorized.

## Gate 10 — Windows double-click EXE
- `scripts/build-face-impact-windows.ps1` builds Vite UI and stages a **portable Electron folder** containing `OpenFlight Face Impact.exe`, bundled UI and Electron runtime.
- `ui/electron/main.js` opens local `dist/index.html` when running as a packaged/portable app; existing dev URL behavior retained. `ui/vite.config.ts` uses relative assets for `file://` loading.
- `.github/workflows/gate10-windows-portable.yml` provides a **manually triggered** Windows runner build, structural validation and development-only downloadable artifact. No automatic publishing.
- This is **not** a one-file installer: users must retain the whole folder. It does **not** bundle or start the Python backend, capture real ELP OV9281 images or validate impact measurements. Offline Face Impact demo and navigation need Windows runtime smoke testing.
- **Outstanding evidence:** actual Windows workflow run, EXE startup smoke test, dashboard rendering, offline navigation, and file URL security/asset validation. Do not claim Windows packaging verified until tested.

## Gate 11 — visual and functional acceptance checklist
- Six named panels: Side Impact, Front Impact, Top Impact, Impact Distribution, Camera Preview, Shot Replay.
- Settings tabs, local reset and navigation function or are explicitly disabled where hardware is unavailable.
- Gate09 demo mode enter/add/reset/exit, distribution circles, shot history and statistics are explicitly simulated; real metrics remain `not measured`.
- Playwright `ui/tests/e2e/gate09-simulated-session.spec.ts` and earlier Gate07/08 E2E cover browser UI behavior. E2E passed on `2bb8e76271ef4bef217edfab9b92f8c110db5e94` before Gate10 changes.
- **Outstanding evidence:** new exact-HEAD CI, Windows packaging workflow run, Windows EXE GUI smoke test and screenshot review. The PR screenshot-in-description check remains deferred **not waived**.
- No physical ELP camera tests in Phase 2. No release or merge without separate authorization.

## CI evidence — 2026-11-10
- Exact verified code SHA: `9c54404e37bec28e8f7b215f26d276a0a2dc69fa`.
- GitHub Actions Windows portable workflow run `42810519769`: **success**.
- Windows artifact: `gate10-windows-portable-development-only`, artifact ID `13761873646`, size 161,503,560 bytes. This is a folder-based Electron distribution, **not** a one-file executable or installer.
- Same-SHA successful checks: `portable-exe`, `e2e`, `format`, `lint`, UI build, UI unit, Python 3.10/3.11/3.12, pylint, Windows diagnostics, PR quality.
- `PR description completeness` still fails due to the screenshot requirement expressly deferred by the user. Not bypassed or waived.
- The Windows job validates build and package file structure; **it does not launch the GUI or test the Windows user experience**. This remains an acceptance gap. Real camera capture, measurements, and Python backend packaging are out of scope.
- Gate11 cannot be declared fully accepted without appropriate runtime/visual evidence. No merge or release.

## Gate 11 verified packaged Windows renderer smoke (2026-11-10)
- Exact code SHA: `1dbf9d41d553790db4a15c61a1f85ab1aaef6110`.
- Workflow: https://github.com/andersdui22/openflight-face-impact/actions/runs/42838234719 — **success**.
- `Gate 11 packaged EXE renderer smoke` step: **success**. The packaged `OpenFlight Face Impact.exe` was started on a GitHub-hosted Windows runner; the renderer reported all six dashboard panels. This is automated runtime evidence, **not** a user-observed physical-device test.
- Screenshot evidence artifact: `gate11-windows-dashboard-screenshot`, ID `13774303142`, 12,885 bytes. The artifact was uploaded successfully; visual content has not been independently reviewed in this audit.
- Portable development-only EXE artifact: `gate10-windows-portable-development-only`, ID `13774068585`, 161,504,268 bytes.
- All same-SHA technical checks passed: `portable-exe`, `e2e`, `format`, `lint`, UI build/unit, Python 3.10/3.11/3.12, pylint and Windows diagnostics.
- `PR description completeness` remains **failure** solely with the previously deferred screenshot-in-description requirement; do not waive or claim it passed.
- Remaining limits: no real ELP camera validation, no Python backend bundled in portable EXE, no physical Windows machine acceptance, no merge/release. Gate11 acceptance still requires final governance closeout decision; this documentation commit requires fresh exact-HEAD CI verification.
