# Presentation Page Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A public, scroll-driven presentation page for the camera, built from CAD data, with the existing viewer kept as a private workshop entry.

**Architecture:** CAD exports two new manifest blocks (`features`, `spec_sheet`) from params. The Vite project gets two entries: `index.html` (presentation, the only public entry) and `workshop.html` (today's viewer). The presentation renders one fixed canvas split by drei `View`, one `Viewer` instance per view, staged by chapter and figure data that a validator checks against the manifest.

**Tech Stack:** build123d (Python 3.12, uv), Vite 8, React 19, react-three-fiber 9, drei 10, three 0.186, vitest, marked, Playwright (Chromium), `@fontsource-variable/archivo`.

**Spec:** `docs/superpowers/specs/2026-10-24-presentation-design.md`

## Global Constraints

- Every number and position shown on the page comes from `cad/params.py` through the manifest. No dimension is typed in web code or markdown.
- New npm dependencies are pinned to exact versions that pnpm's minimum release age policy accepts. Do not turn the policy off.
- Copy is English, sentence case, plain verbs. No all-caps labels except the film edge printing on the navigator. No monospace data labels. No `→` on links.
- Colour tokens: Seamless `#D5D8D8`, PETG `#000000`, Brass `#A4823F`, Drawing white `#FFFFFF`, Dimension blue `#2C5A86`, Film base `#3A3A38`.
- Font: Archivo only, self-hosted (`@fontsource-variable/archivo`); headings use the extended width, body the normal width, dimensions use tabular figures.
- Phones: 375 px wide must work with no sideways page scroll; one-finger drag scrolls the page unless "Explore" is on.
- `prefers-reduced-motion`: nothing autoplays and camera moves cut instead of easing.
- The public build (`pnpm --dir viewer build:public`) contains no workshop page or workshop-only code.
- Warnings from build, typecheck, tests or the browser console are fixed or suppressed at the narrowest scope with a reason (user rule).
- Comments only for a non-obvious why.

## Review Focus

1. A chapter names a part, feature or mechanism that a CAD rename removed. Expected: the page shows an error naming the chapter and the missing reference, never a blank stage. (Task 2 test.)
2. A visitor scrolls fast past several chapters. Expected: only the last chapter's shot and motion apply; earlier tweens and motions stop. (Task 4 browser check.)
3. A phone visitor drags on the 3D stage. Expected: the page scrolls; orbit only after tapping Explore. (Task 4 browser check at 375 px.)
4. WebGL is unavailable. Expected: every chapter shows its still and its text; the maker half reads normally. (Task 6 Playwright run with WebGL disabled.)
5. A part GLB fails to load. Expected: the rest of the stage renders and pins on the missing part are hidden, with one console error naming the part. (Task 3 check.)

---

### Task 1: CAD feature anchors and spec sheet

**Files:**
- Create: `cad/features.py`, `cad/spec_sheet.py`, `cad/check_areas/presentation.py`, `cad/tests/test_presentation.py`
- Modify: `cad/export.py` (manifest gains `features` and `spec_sheet`), `cad/checks.py` / `cad/tests/test_checks.py` only as the existing area registration pattern requires

**Interfaces:**
- Produces in `manifest.json`:
  - `features: [{ id: str, label: str, part: str, point: [x, y, z] }]` with `point` in camera mm coordinates at the part's rest pose.
  - `spec_sheet: [{ id: str, label: str, value: float, unit: str, section: "specs" | "interface", status: "locked" | "draft", source: str }]`. `source` names the params path (for example `optics.pinhole_d`) or `derived:<formula name>`.
- `features.py`: `FEATURES: tuple[Feature, ...]`, `Feature(id, label, part, point: Callable[[Camera], tuple[float, float, float]])`, `feature_entries(c: Camera) -> list[dict]`.
- `spec_sheet.py`: `SPEC_SHEET: tuple[SpecEntry, ...]`, `spec_entries(c: Camera) -> list[dict]`.

Features to define (ids are the contract with Task 4 and 5): `sprocket`, `cam_notch`, `pawl`, `release_button`, `advance_knob`, `rewind_knob`, `film_gate`, `cassette`, `rear_cover_latch`, `dark_slide`, `slot_velvet`, `pinhole`, `shutter_lock`, `shutter_tabs`, `viewfinder_front`, `viewfinder_rear`, `body_hook_rail`, `body_latch_pin`, `m42_mount`, `tripod_nut`. Each anchor sits on the visible surface a reader would point at.

Spec entries: frame width and height, aspect ratio (derived), perforation pitch, perforations per frame, advance per frame, sprocket teeth, sprocket pitch diameter, frames per 36-exposure roll (derived, from the film length param if one exists, else omit), pinhole diameter, pinhole-to-film distance, f-number (derived: distance / diameter, about f/167), lens mount thread and pitch, minimum image circle (derived: frame diagonal, about 69.3 mm) as `interface`, and the body interface values (hook rail, latch pin diameter, datum face, M42 seat position relative to the film plane) as `interface` + `draft`.

- [ ] **Step 1: Write seeds in `cad/tests/test_presentation.py`** following the `SEEDS` pattern of `cad/tests/test_pinhole.py`: an anchor moved 3 mm off its part's surface, a feature naming a part not in `PARTS`, two features with one id, a spec entry whose `source` names a missing param, a derived f-number that no longer matches distance / diameter.
- [ ] **Step 2: Run `uv run python cad/tests/test_checks.py`.** Expected: the new seeds fail to be caught (checks do not exist yet).
- [ ] **Step 3: Implement `features.py`, `spec_sheet.py` and the checks in `check_areas/presentation.py`** (anchor within 0.5 mm of its built part's surface, unique ids, part exists, sources resolve, derived values match). Anchor points are computed from params, no literal coordinates.
- [ ] **Step 4: Wire `export.py`** to write both blocks.
- [ ] **Step 5: Run** `uv run python cad/export.py`, `uv run python cad/checks.py` (ALL PASS) and `uv run python cad/tests/test_checks.py` (every seed caught).
- [ ] **Step 6: Commit** `cad: feature anchors and spec sheet in the manifest`.

### Task 2: Two entries, manifest parsing and the story validator

**Files:**
- Create: `viewer/workshop.html` (today's `index.html` content, title "X-Pan workshop"), `viewer/src/workshop/main.tsx` (today's `src/main.tsx`), `viewer/src/presentation/main.tsx`, `viewer/src/presentation/story.ts` (types), `viewer/src/presentation/validate.ts`, `viewer/src/presentation/validate.test.ts`, `viewer/scripts/check-public.mjs`
- Modify: `viewer/index.html` (becomes the presentation entry, title "X-Pan pinhole camera"), `viewer/vite.config.ts`, `viewer/package.json`, `viewer/src/types.ts`, `viewer/src/manifest.ts`, `AGENTS.md` (viewer commands and URLs)
- Move workshop-only UI (`src/App.tsx`, `src/ui/`) under `src/workshop/`. Shared code (`scene/`, `state/`, `manifest.ts`, `types.ts`, `ErrorBoundary.tsx`) stays where it is.

**Interfaces:**
- `types.ts`: `Feature { id, label, part, point: Vec3 }`, `SpecEntry { id, label, value, unit, section: 'specs' | 'interface', status: 'locked' | 'draft', source }`; `Manifest` gains `features: readonly Feature[]` and `spec_sheet: readonly SpecEntry[]`, parsed strictly in `manifest.ts`.
- `story.ts`:
  ```ts
  type ShotDirection = readonly [number, number, number]
  interface Staging {
    shot: { direction: ShotDirection; frame: readonly (string | Group)[]; distance?: number }
    scene?: { hide?: readonly string[]; ghost?: readonly string[]; explode?: number; section?: Section }
    pose?: Readonly<Record<string, number>>
    motion?: { cycle: string } | { keys: readonly CycleKey[] }
    pins?: readonly string[]
  }
  interface Chapter extends Staging { id: string; title: string; text: string }
  interface Figure extends Staging { id: string; caption: string }
  ```
- `validate.ts`: `validateStory(manifest: Manifest, chapters: readonly Chapter[], figures: readonly Figure[]): string[]`. Each message reads `chapter <id>: unknown part "<name>"` (or feature, mechanism, cycle, group). Empty array means valid.
- `package.json` scripts: `dev` (serves both; `/` is the presentation, `/workshop.html` the workshop), `build` (both entries to `dist/`), `build:public` (index.html only to `dist-public/`, then `node scripts/check-public.mjs`), `test` (`vitest run`), `typecheck`.
- `check-public.mjs`: exits 1 if `dist-public/` contains `workshop.html` or any JS chunk containing a workshop-only marker (export a `WORKSHOP_MARKER` string constant from `src/workshop/main.tsx` and search for it).
- `.gitignore`: add `viewer/dist-public/`.

- [ ] **Step 1: Write `validate.test.ts`**: `validateStory` on the real `../out/manifest.json` with the real chapters and figures returns `[]` (until Task 4 and 5 exist, use a one-chapter fixture); a chapter pinning feature `"no_such_feature"` returns exactly `['chapter fixture: unknown feature "no_such_feature"']`; likewise an unknown part in `shot.frame`, an unknown mechanism in `pose`, an unknown cycle in `motion`.
- [ ] **Step 2: Run `pnpm --dir viewer test`.** Expected: FAIL (module missing).
- [ ] **Step 3: Implement** types, parser, validator, entries, scripts. `presentation/main.tsx` renders a placeholder that loads the manifest and shows validator errors if any.
- [ ] **Step 4: Run** `pnpm --dir viewer typecheck`, `pnpm --dir viewer test`, `pnpm --dir viewer build`, `pnpm --dir viewer build:public`. Expected: all pass with no warnings; `dist-public/` has `index.html` and no `workshop.html`.
- [ ] **Step 5: Check the workshop still works** at `/workshop.html` in the browser pane (parts load, Advance one frame runs).
- [ ] **Step 6: Commit** `viewer: presentation and workshop entries, story validator`.

### Task 3: Staged views on one canvas

**Files:**
- Create: `viewer/src/scene/PartsScene.tsx` (parts, lights, MotionDriver, ClipSync for one `Viewer`, no grid, no controls), `viewer/src/presentation/StagedView.tsx`, `viewer/src/presentation/staging.ts`, `viewer/src/presentation/Pins.tsx`, `viewer/src/presentation/ShotRig.tsx`
- Modify: `viewer/src/scene/Viewport.tsx` (workshop canvas uses `PartsScene` plus its grid, controls and `CameraRig`)

**Interfaces:**
- `applyStaging(viewer: Viewer, staging: Staging): void` sets part views, explode, section and pose values on that viewer.
- `shotFor(viewer: Viewer, shot: Staging['shot'], aspect: number): { position: Vector3; target: Vector3 }` frames the named parts or groups from rest-pose boxes, as `CameraRig` does.
- `<StagedView track={RefObject<HTMLElement>} viewer={Viewer} staging={Staging} interactive={boolean} />` renders a drei `View` bound to `track`, with its own camera, `PartsScene`, `ShotRig` (eases to the shot over 0.8 s, cuts under reduced motion) and `Pins`.
- `<Pins viewer={Viewer} ids={readonly string[]} compact={boolean} />` places each pin at `node.matrix × feature.point`, so pins follow mechanisms. A pin on a part that failed to load is not rendered.
- Every view's viewer comes from `createViewer(manifest, MANIFEST_URL)`; GLBs are shared through drei's `useGLTF` cache.
- The presentation `<Canvas>` uses `frameloop="demand"`, `dpr={[1, 1.5]}` on phones, no shadows, and calls `invalidate()` while a tween or motion runs.

- [ ] **Step 1:** Extract `PartsScene` from `Viewport`; run the workshop in the browser pane and confirm it looks and works as before.
- [ ] **Step 2:** Implement staging, `StagedView`, `ShotRig`, `Pins`. Mount two test views in `presentation/main.tsx` (iso whole camera; mechanism cutaway playing the `frame` cycle) to prove independent mechanism state.
- [ ] **Step 3:** In the browser pane, confirm both views render, the cycle moves only the second, pins track the sprocket as it turns, and blocking one GLB (rename it in `out/glb/` temporarily, then restore) leaves the rest rendering with one console error.
- [ ] **Step 4: Commit** `viewer: staged views on a shared canvas`.

### Task 4: Showcase

**Files:**
- Create: `viewer/src/presentation/chapters.ts`, `viewer/src/presentation/Showcase.tsx`, `viewer/src/presentation/FilmStripNav.tsx`, `viewer/src/presentation/PlaybackBar.tsx`, `viewer/src/presentation/useActiveChapter.ts`, `viewer/src/presentation/presentation.css`
- Modify: `viewer/src/presentation/main.tsx`, `viewer/package.json` (`@fontsource-variable/archivo`)

**Interfaces:**
- `CHAPTERS: readonly Chapter[]` in spec order: `hero`, `format`, `modules`, `advance`, `loading`, `dark-slide`, `shutter`, `viewfinder`, `swap-body`. Stagings use the mechanisms already in the manifest (`advance`, `release`, `turn_buttons`, `cover`, `dark_slide`, `slide_stow`, `shutter_lock`, `shutter`, `finder_rear`, `finder_front`, `body_detach`) and the `frame` cycle. Numbers in copy come from `spec_sheet` through a `spec(id)` helper, never literals.
- `useActiveChapter(ids: readonly string[]): string` uses an IntersectionObserver on the chapter text blocks; the block crossing the vertical middle wins.
- On a chapter change: stop the running motion, apply the staging, ease the shot, then autoplay the motion once (not under reduced motion). `PlaybackBar` offers play, pause, replay and a scrub slider for the active motion.
- `FilmStripNav`: a negative strip with perforations, one 65:24 frame per chapter, edge-printed frame numbers; the active frame sits in a gate mark; tapping scrolls to that chapter. Bottom edge on phones.
- Desktop: drag orbits, wheel scrolls the page. Phones: canvas has `touch-action: pan-y` and orbit off until "Explore" is on.
- Hero shows load progress until every part has loaded or failed.
- Layout and tokens per the spec's Visual direction.

- [ ] **Step 1:** Add chapters to the `validate.test.ts` real-manifest case; run `pnpm --dir viewer test` (passes once chapters exist and are valid).
- [ ] **Step 2:** Implement the showcase.
- [ ] **Step 3:** In the browser pane at desktop size and at 375 × 812: every chapter's shot, pins and motion; navigator jumps; fast scroll from hero to swap-body leaves only the last chapter's staging; reduced motion (emulate) cuts and does not autoplay; no console errors or warnings; `document.documentElement.scrollWidth <= innerWidth`.
- [ ] **Step 4: Commit** `viewer: presentation showcase`.

### Task 5: Maker half

**Files:**
- Create: `viewer/src/presentation/content/*.md` (specifications, film-transport, interface, design-your-own, bom, printing, decisions), `viewer/src/presentation/figures.ts`, `viewer/src/presentation/MakerDoc.tsx`, `viewer/src/presentation/SpecTable.tsx`, `viewer/src/presentation/BomTable.tsx`
- Modify: `viewer/package.json` (`marked`), `viewer/src/presentation/main.tsx`

**Interfaces:**
- Placeholders in markdown: `{{figure:<id>}}`, `{{spec:specs}}`, `{{spec:interface}}`, `{{bom}}`, `{{value:<spec id>}}` (inline number with unit). `MakerDoc` splits rendered markdown at placeholders and mounts the matching component.
- `FIGURES: readonly Figure[]` with ids `transport-cutaway`, `interface-rail`, `interface-m42`; each a `StagedView` in a document box (interactive orbit on desktop only).
- `BomTable` reads `docs/bom.md` via `?raw`, parses the Parts table and shows Part, Qty, Spec and Used for. Thai search terms and THB prices are left out of the public page.
- The film-transport section embeds `docs/figures/film-transport/film-transport-light.html` if it bundles cleanly as an asset; otherwise it shows a Playwright still of that page made in Task 6.
- The Interface section carries a visible "Draft. Not locked until a test print confirms it." note. Printing and assembly shows its headings and "Coming after the test print."
- The Workshop link renders only when `import.meta.env.DEV`.
- Drawing-sheet styling per the spec; wide tables scroll inside a wrapper.

- [ ] **Step 1:** Add figures to the validator test; run tests.
- [ ] **Step 2:** Implement the maker half.
- [ ] **Step 3:** Browser pane at desktop and 375 px: every placeholder resolved (no `{{` text on the page), tables match `spec_sheet`, BOM rows match `docs/bom.md`, no sideways scroll, no console warnings.
- [ ] **Step 4: Commit** `viewer: maker documentation half`.

### Task 6: Playwright stills, fallback and the verification run

**Files:**
- Create: `viewer/scripts/stills.mjs`, `viewer/scripts/verify.mjs`, `viewer/src/presentation/NoWebGL.tsx`
- Modify: `viewer/package.json` (`playwright` devDependency; scripts `stills`, `verify`), `viewer/index.html` (`og:image` → `stills/hero.png`, description meta), `AGENTS.md`

**Interfaces:**
- The presentation reads `?still=<chapter id>`: renders only that chapter's staging at rest of its motion end, hides UI, and sets `window.stillReady = true` when parts are loaded and the frame is drawn.
- `stills.mjs` starts the Vite dev server (stills must exist before `build:public` copies `out/` into the site), captures each chapter at 1600 × 900 into `out/stills/<id>.png` (gitignored with `out/`), and the film-transport page if Task 5 needed it.
- Without WebGL, `NoWebGL` replaces the stage with `stills/<id>.png` per chapter.
- `verify.mjs` drives the built public site at 1440 × 900 and 375 × 812: screenshots every chapter into `out/verify/`, fails on any console error or warning, on sideways scroll, on unresolved placeholders, and on a missing still; reruns with WebGL disabled and with reduced motion; records load time and the frame rate during the `advance` motion.

- [ ] **Step 1:** `pnpm --dir viewer exec playwright install chromium`.
- [ ] **Step 2:** Implement still mode, `NoWebGL`, `stills.mjs`, `verify.mjs`.
- [ ] **Step 3:** Run `pnpm --dir viewer stills && pnpm --dir viewer build:public && pnpm --dir viewer verify` (`verify` serves `dist-public/` with `vite preview`). Expected: exit 0; review every screenshot by eye.
- [ ] **Step 4: Commit** `viewer: chapter stills, no-WebGL fallback and a verification run`.
