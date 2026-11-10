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
