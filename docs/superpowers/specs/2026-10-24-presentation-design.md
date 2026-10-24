# Presentation page: design

Date: 2026-10-24. Status: approved in chat.

## Goal

A public, scroll-driven page that explains the camera. The top half is a showcase for
anyone who likes film cameras. The bottom half is technical content for makers who want
to build the camera or design their own body or lens module.

The existing viewer stays as a private review tool ("workshop"). The public build
contains only the presentation.

## Decisions

| Topic | Decision |
|---|---|
| Audience | Both: showcase on top, maker content below |
| Language | English |
| Hosting | Not published yet. The public build must work as a static site |
| Mobile | Must work well on phones |
| Interface spec | Included as a draft, marked "not locked" until a test print confirms it. No STEP download yet |
| Approach | Same Vite project, shared scene code, two entries |
| Stills | Playwright renders a still per chapter (no-WebGL fallback and og:image) and drives verification |
| Branch | `presentation`, from `parts-phase3-4` |
| Font | Archivo, self-hosted |

## 1. Page structure and content

### Showcase (top half)

One full-screen 3D stage. Each chapter has 1 to 3 sentences. A film-strip navigator
jumps to any chapter.

| Chapter | 3D scene | Copy and pins |
|---|---|---|
| Hero | Camera turning slowly, iso view | Project name. The camera is the subject; no stat row |
| The format | A glowing 65 x 24 frame in the gate, a 36 x 24 frame outline for comparison | Panoramic frames on ordinary 135 film, about 19-20 per roll. Frame size and ratio appear here |
| Three modules | Exploded film back, body, pinhole module | Pin per layer; tapping a layer highlights it |
| One turn, one frame | Mechanism cutaway, full frame-advance cycle with moving film | Pins on the 14-tooth sprocket, cam and pawl, release button; live mm readout |
| Loading film | Turn the latches, open the cover, cassette in, close | The order a user follows |
| Dark slide | Pull the slide and stow it on the cover | Velvet light trap at the slot mouth |
| Pinhole and shutter | Close on the front; unlock and open the shutter | 0.30 mm pinhole, 50 mm to film, f/167 |
| Viewfinder | Unfold the front and rear finder frames | How to frame a shot |
| Swap the body | Swing the body off its latch | Bridge to the maker half: design your own body or lens |

### Maker half (bottom)

A document with small 3D figures.

1. Specifications: the locked values, generated from params.
2. How the film transport works: the existing film-transport figure plus a 3D cutaway.
3. Interface spec (draft, not locked): film back to body (top hook rail, 3 mm bottom latch
   pin, velvet datum face, coordinate system) and body to lens (M42 x 1, distance to film,
   minimum image circle 69.3 mm). Every value comes from params. A 3D figure highlights
   the interface faces.
4. Design your own module: constraints (most 35 mm lenses do not cover a 65 x 24 frame;
   areas a body must not touch) and module ideas (body with a built-in shutter, reflex or
   WLF body, lens module).
5. Bill of materials: read from `docs/bom.md`.
6. Printing and assembly: headings only, marked "coming after the test print".
7. Design decisions: a summary of the decision log for people extending the design.
8. Workshop: a link to the full viewer, shown in dev only.

Left out of the first version: a long "why XPan" section (folded into The format),
license and downloads (not published yet), and an exposure calculator (later).

## 2. Data

Rule: every number and position comes from CAD. The web side writes words and stages
scenes.

### Feature anchors (CAD)

- `cad/features.py` lists the features that get a pin: `id`, `label`, the part it sits
  on, and an anchor point computed from params.
- `export.py` writes them to `manifest.json` as `features`. The viewer attaches each pin
  to its part's node, so pins move with mechanisms.
- `checks.py` checks that every anchor lies on its part's surface within a tolerance,
  that ids are unique and that the part exists. Each check has a seeded error in
  `cad/tests/`.

### Spec sheet (CAD)

- `cad/spec_sheet.py` picks which params to publish, with a label, unit, section
  (`specs` or `interface`) and status (`locked` or `draft`). Derived values (image circle,
  f-number) are computed there from params.
- `export.py` writes it to the manifest as `spec_sheet`. The web only displays it.
- Checks: every entry names an existing param and derived values match their formula.

### Chapters (web)

`viewer/src/presentation/chapters.ts` holds the chapters as data:

- `id`, `title`, `text`
- `shot`: a view direction and the parts or groups to frame; distance comes from bounds,
  as in `CameraRig`
- `scene`: hidden parts, ghosted parts, explode amount, section plane
- `pose`: mechanism values on entry
- `motion`: a manifest cycle id or inline `CycleKey`s, played by the existing cycle player
- `pins`: feature ids

On load, every part, feature and mechanism a chapter or figure names is checked against
the manifest. A wrong name shows an error that names the chapter and the reference.

### Maker content (web)

- Prose lives in markdown files under `viewer/src/presentation/content/`, rendered with
  `marked` (pinned).
- The BOM is read from `docs/bom.md`.
- Placeholders such as `{{figure:interface-rail}}` and `{{spec:interface}}` become
  components.
- A figure uses the same `shot`, `scene` and `pose` shape as a chapter.

Data flow: `params.py` to `features.py` and `spec_sheet.py` to `manifest.json` to
chapters, figures and tables.

## 3. Rendering, mobile and visual direction

### Entries and builds

- `presentation.html` is the public page; `workshop.html` is the review viewer.
- `pnpm --dir viewer dev` serves both.
- `build:public` builds only the presentation entry. A check after the build proves no
  workshop page or code is in the output.
- The GLB of every part the presentation loads can be downloaded by visitors. A part
  that must stay private must not be loaded at all.

### One canvas

- One WebGL canvas fixed behind the page. drei `View` splits it into the full-screen
  stage and the small figures, which track boxes in the document.
- GLBs load once; views share geometry and materials but each view has its own
  mechanism state.

### Scroll and chapters

- An IntersectionObserver picks the chapter whose text is in the middle of the screen.
  The camera eases to the new shot over about 0.8 s and mechanisms move to the chapter
  pose.
- Animation is not tied to scroll position. A chapter's motion plays once on entry, with
  play, pause, replay and a scrub slider.
- With `prefers-reduced-motion`, nothing autoplays and the camera cuts to each shot.

### Interaction

- Film-strip navigator: bottom edge on phones, side or bottom on desktop.
- Desktop: drag to orbit; the wheel scrolls the page, it does not zoom. Phone: one finger
  scrolls the page; an "Explore" button enables orbit.
- Pins are attached to part nodes. Phones show a dot that expands on tap; desktop shows a
  short label. No occlusion test; each chapter pins only what its shot shows, and
  screenshots confirm it.

### Layout

- Desktop: full-screen stage, chapter text as a card in a left column.
- Phone: full-screen stage, text card at the bottom over a soft fade. The maker half is
  one column; wide tables scroll inside themselves and the page never scrolls sideways.
- Text is left aligned, about 70 characters per line at most.

### Visual direction

- The showcase sits on a light studio seamless, so the black PETG camera keeps its form.
- The maker half reads as an engineering drawing sheet: white paper, black ink, drafting
  blue for dimensions and links.
- The one bold element is the film-strip navigator: a black-and-white negative strip with
  real perforations, one 65:24 frame per chapter and edge-printed frame numbers. The
  current chapter advances into the gate.
- No stat row in the hero, no all-caps eyebrows (except the film edge printing), no card
  grid in the maker half, no monospace labels.

| Token | Hex | Use |
|---|---|---|
| Seamless | `#D5D8D8` | Showcase background |
| PETG | `#000000` | Main text |
| Brass | `#A4823F` | Highlighted part, pins (the brass pinhole shim) |
| Drawing white | `#FFFFFF` | Maker half background |
| Dimension blue | `#2C5A86` | Dimension lines, links |
| Film base | `#3A3A38` | Film-strip navigator |

Type: Archivo only. Extended width for headings, normal width for body text, tabular
figures for dimensions.

### Performance and fallback

- DPR capped at 1.5 on phones, no shadows, `frameloop="demand"`.
- The hero shows load progress until the parts arrive.
- No GLB compression until a measurement shows it is needed (4.1 MB today).
- Without WebGL each chapter shows its pre-rendered still. The hero still is the og:image.

## 4. Testing

- CAD: feature and spec-sheet checks, each with a seeded error.
- Web: typecheck; vitest tests prove the chapter validator accepts the real manifest and
  catches a seeded wrong name.
- Public build: a script fails if any workshop page or code is in the output.
- Browser: every chapter at desktop and 375 px width, with screenshots; pins visible,
  motion plays, navigator jumps; no console errors or new warnings; no sideways scroll;
  reduced motion and no-WebGL work. Load time and frame rate are measured and reported as
  estimates, because phone emulation does not throttle the GPU.
- Playwright renders the chapter stills and the verification screenshots, so both can be
  rerun.
