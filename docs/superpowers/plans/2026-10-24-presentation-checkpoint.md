# Presentation work: checkpoint

Paused 2026-10-24 at the user's request (usage limit). Branch `presentation` in the worktree
`.worktrees/presentation`. Nothing is pushed. `parts-phase3-4` is untouched.

Spec: `docs/superpowers/specs/2026-10-24-presentation-design.md`.
Plan: `docs/superpowers/plans/2026-10-24-presentation.md`.

## Done and verified

| Commit | What | Verified |
|---|---|---|
| `929fe08` | Task 1: `features` and `spec_sheet` in the manifest, checks and 9 seeds | Export, `checks.py` ALL PASS, all 140 seeds caught (fork run on the merged branch) |
| `61b706e` | Task 2: `index.html` presentation and `workshop.html` workshop entries, strict manifest parsing, story validator, `build:public` with `check-public.mjs` | typecheck, 15 tests, both builds, public check proven to fail on planted files, workshop runs in the browser |
| `eee734a` | Task 3: `PartsScene`, `StageCanvas`, `StagedView`, `ShotRig`, `Pins`, `applyStaging`, `shotFor`, demand rendering, studio lighting | Two independent views, pins follow the sprocket, a missing GLB gives one console error and hides its pins, 0 draw calls when idle |
| `3ce8239` | Task 4: nine-chapter showcase, film-strip navigator, playback bar, Archivo, phone layout with Explore | Screenshots at 1440x900 and 375x812, fast-scroll leaves only the last chapter, reduced motion (matchMedia patched), no sideways scroll |
| `2b2b9c8` | Merge of `fast-seeds`: seed suite runs each seed's own checks in parallel (about 9 minutes) | Fork ran 128 checks + 140 seeds, ALL SEEDS CAUGHT |

## Done but not verified

- `b12511e` cad: `standard_frame_width` and `frames_per_roll` in the spec sheet, `FormatOverlay` reads the
  width from it, a new seed. Committed by the Task 5 subagent before it was stopped. Not yet run:
  `uv run python cad/export.py`, `uv run python cad/checks.py`, `uv run python cad/tests/test_checks.py`.

## In progress

- WIP commit after `b12511e`: Task 5 (maker half) partial work by a subagent that was stopped mid-task.
  Files: `MakerDoc.tsx`, `SpecTable.tsx`, `BomTable.tsx`, `bom.ts`, `content.ts`, `content/`,
  `figures.ts`, `FigureViews.tsx`, `Director.tsx`, `maker.ts`, tests, and edits to `Showcase.tsx`,
  `StageCanvas.tsx`, `main.tsx`, `presentation.css`, `validate.ts`, `vite.config.ts`, `package.json`
  (probably `marked`). State unknown: it was not typechecked or tested. Review it before building on it;
  squash it into the real Task 5 commit.

## Remaining

1. Verify `b12511e` (the three CAD commands above).
2. Finish Task 5 per the plan, plus two follow-ups:
   - Brass text contrast: `#A4823F` on white is about 3.3:1. Add a darker brass ink token for text,
     at least 4.5:1 on `#FFFFFF` and `#D5D8D8`. Keep Brass for pins and graphics.
   - Report text contrast on the seamless background.
3. Task 6: Playwright stills, no-WebGL fallback, `verify.mjs`. It must also cover what the hidden
   browser pane could not: a real touch scroll on the phone layout and the navigator's smooth scroll.
   Watch the draw-call count (about 2 per part per view) in the frame-rate measurement.
4. Final pass: deslop, no-comments, a whole-branch review, then the summary for the user.

## Notes for whoever resumes

- Run CAD commands only when no viewer delegate is mid-build; they share the CPU.
- Stop dev servers by PID, not `pkill -f vite`.
- Known warning: `THREE.Clock` deprecation from @react-three/fiber 9.8.2, left on purpose.
- Chunk-size limit in `viewer/vite.config.ts` sits just above today's public chunk (1,273 kB).
- The user's viewer tab from the start of the session (main checkout) was likely stopped by an earlier
  `pkill -f vite`.
- Branches `fast-seeds` and `presentation-fast-seeds` and worktrees `.worktrees/fast-seeds` and
  `.worktrees/pfs` came from the fork session. They can be removed once the user decides whether
  `fast-seeds` also goes into `parts-phase3-4`.
