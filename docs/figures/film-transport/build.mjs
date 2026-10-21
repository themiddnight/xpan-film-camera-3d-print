// Builds the film-transport figure pages from model.mjs and pose.mjs with the anatomy kit.
// node docs/figures/film-transport/build.mjs [--light] [--audit]
// The kit is read from $ANATOMY_HOME, or ~/.claude/skills/anatomy.
import { readFileSync, writeFileSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import * as M from "./model.mjs";
import { makePose } from "./pose.mjs";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const HOME = process.env.ANATOMY_HOME ?? path.join(os.homedir(), ".claude/skills/anatomy");
const load = (file) => import(pathToFileURL(path.join(HOME, file)).href);
const k = await load("kit/iso-kit.mjs");
const G = await load("kit/lathe.mjs");
const A = await load("kit/audit.mjs");
const { kitScript } = await load("scripts/inline-kit.mjs");

const THEME = process.argv.includes("--light") ? "light" : "dark";
const WIDTH = 600;
const HEIGHT = 540;
const AZIMUTH = -28;
const ELEVATION = 54;
const S = 5; // world units per mm

const { FILM, SPROCKET: SP, CAM, PAWL, BUTTON, SPOOL, KNOB } = M;
const HALF = FILM.width / 2;

// Layout in camera mm (film-back.md 17.2, 17.4, 17.6, 17.7). Z: floor top -27, ceiling 28.5, top wall 31.5.
const X0 = 30; // the cutaway section plane through the bridge, where the film strip is cut
const FLOOR_Y0 = -4.8;
const FLOOR = { X: [X0, 97.5], Y: [FLOOR_Y0, 30], Z: [-30, -27] };
const FOOT = { Z: [-33, -30], r0: 3.0, r1: 2.3 };
const PLATE_Z = [28.5, 31.5];
const RULER = { X: [30.6, 97.1], Y: [-5.0, FLOOR_Y0], Z: [-29.7, -27.3], from: 30.6, ticks: 14 };
const SHELF = { X: [63.4, 70.2], Y: [20.6, 27], Z: [13, 16.5] };
const SPRING_S = 4.9; // pawl spring sits 4.9 mm from the pivot, under the button end
const CHEEK = { half: 1.9, shift: 0.6, gap: 1.7, t: 2.0, Z: [22.4, PLATE_Z[1]] };
const KNOB_Z = 31.8;
const BUTTON_TOP = 38.0;
const COLLAR = { rIn: BUTTON.r, rOut: 4.0, Z: [PLATE_Z[1], 33.0] };
const SPOOL_Z = { flange: SPOOL.flangeGap / 2, boss: [-27, -23], felt: [19.0, 19.8], collar: [19.8, 23.8], bush: [26.4, PLATE_Z[0]] };
const PIN = { boss: [-27, -22] };

const W = ([X, Y, Z]) => [-Y * S, -X * S, Z * S];
const dirW = ([X, Y, Z]) => [-Y, -X, Z];
const planC = (X, Y, r = 0) => ({ x: -Y[1] * S, y: -X[1] * S, w: (Y[1] - Y[0]) * S, d: (X[1] - X[0]) * S, r: r * S });
const ringW = (points) => points.map(([X, Y]) => [-Y * S, -X * S]);

// --- camera
const fitPoints = [
  ...k.boxCorners(planC(FLOOR.X, FLOOR.Y), FOOT.Z[0] * S, FLOOR.Z[1] * S),
  W([SPOOL.x - KNOB.r, SPOOL.y, KNOB_Z + KNOB.h]),
  W([SPOOL.x + KNOB.r, SPOOL.y, KNOB_Z + KNOB.h]),
  W([SPOOL.x, SPOOL.y + KNOB.r, KNOB_Z + KNOB.h]),
  W([X0, FLOOR.Y[1], PLATE_Z[1]]),
  W([97.5, FLOOR.Y[1], PLATE_Z[1]]),
  W([X0, 0, 28.5]),
];
const P = k.fitProjection(fitPoints, WIDTH, HEIGHT, { pad: 22, azimuth: AZIMUTH, elevation: ELEVATION });
const V = G.viewOf(P);
const KS = G.scaleOf(P);
const at = (p) => k.iso(W(p), P);
const path3 = (points, closed = false) => k.pathOf(points.map(at), closed);
const pose = makePose(k, G, M, P, S);

// --- drawing helpers that also record each part's true shape for the audit
const R = A.recorder(P);
const record = R.solid;
const items = [];
function put(name, ref, svg, shapes, extra = {}) {
  const item = R.put({ name, at: W(ref), bias: 0, svg, shapes, piece: "back", ...extra });
  items.push(item);
  return item;
}
const sol = (paths, style) => k.solidSvg(paths, style);
const Ln = (d, style) => k.lineSvg(d, style);
const dots = (points, style) => k.dotsSvg(points.map(at), style);

function box(name, X, Y, Z, { r = 0, steps = 4, bevel = 0, tone = "mid", inner = "", extra = "", meta = {}, lit = false } = {}) {
  const plan = planC(X, Y, r);
  const paths = k.slabOf(plan, Z[0] * S, (Z[1] - Z[0]) * S, P, steps, bevel);
  const shape = record(A.slab(plan, Z[0] * S, (Z[1] - Z[0]) * S, { name, ...meta }, steps));
  return put(name, [(X[0] + X[1]) / 2, (Y[0] + Y[1]) / 2, (Z[0] + Z[1]) / 2], sol(paths, { tone, inner, lit }) + extra, [shape]);
}

function prism(name, points, Z, { tone = "mid", extra = "", meta = {}, convex = true } = {}) {
  const ring = ringW(points);
  const paths = k.extrude(ring, Z[0] * S, (Z[1] - Z[0]) * S, P, { convex });
  const shape = record(A.extruded(ring, Z[0] * S, (Z[1] - Z[0]) * S, { name, ...meta }));
  const cx = points.reduce((a, p) => a + p[0], 0) / points.length;
  const cy = points.reduce((a, p) => a + p[1], 0) / points.length;
  return put(name, [cx, cy, (Z[0] + Z[1]) / 2], sol(paths, { tone }) + extra, [shape]);
}

// A vertical turned part, optionally bored for the pin or shaft it turns on.
const AXIS = (X, Y) => G.frameOf(W([X, Y, 0]), [0, 0, 1], [1, 0, 0], [0, 1, 0]);
function round(name, X, Y, r, Z, { bore = 0, tone = "mid", bevel = 0, steps = 0, inner = "", extra = "", meta = {}, lit = false, cut = null } = {}) {
  const [cx, cy] = W([X, Y, 0]);
  const count = steps || G.stepsFor(r * S, 24, 160, KS);
  const paths = k.cylinder(cx, cy, r * S, Z[0] * S, (Z[1] - Z[0]) * S, P, count, bevel);
  const shape = bore
    ? record(A.ring(AXIS(X, Y), Z[0] * S, Z[1] * S, bore * S, r * S, { name, ...meta, ...(cut ? { cut } : {}) }))
    : record(A.cylinder(cx, cy, r * S, Z[0] * S, (Z[1] - Z[0]) * S, { name, ...meta }));
  return put(name, [X, Y, (Z[0] + Z[1]) / 2], sol(paths, { tone, inner, lit }) + extra, [shape]);
}

const sideArc = (X, Y, r, Z, steps = 48) => k.sideArc(-Y * S, -X * S, r * S, Z * S, P, steps);
const ringTop = (X, Y, r, Z, steps = 48) => k.ring(-Y * S, -X * S, r * S, Z * S, P, steps);

// --- the floor section is the base: feet under it, a ruler at film pitch along its rear rim
const basePlan = planC(FLOOR.X, FLOOR.Y, 1.2);
const halo = `<path class="iso-halo" d="${k.haloOf(basePlan, FOOT.Z[0] * S, (FLOOR.Z[1] - FOOT.Z[0]) * S, P)}"/>`;
const feet = [
  [FLOOR.X[0] + 5, FLOOR.Y[0] + 5],
  [FLOOR.X[1] - 5, FLOOR.Y[0] + 5],
  [FLOOR.X[0] + 5, FLOOR.Y[1] - 5],
  [FLOOR.X[1] - 5, FLOOR.Y[1] - 5],
];
feet.forEach(([X, Y], i) => {
  round(`stand.foot${i}`, X, Y, FOOT.r0, [FOOT.Z[0], FOOT.Z[0] + 0.6], { tone: "lo", meta: { ground: true } });
  round(`stand.leg${i}`, X, Y, FOOT.r1, [FOOT.Z[0] + 0.6, FOOT.Z[1]], { tone: "lo", meta: { ground: true } });
});
// --- the shell: floor, bridge with fences, divider, front wall, a stub of the outer wall, and the cut top plate
{
  const screws = [[34, 26.6], [94.6, 26.6]];
  const groove = Ln(k.planOutline(k.insetPlan(basePlan, 0.8 * S), FLOOR.Z[1] * S, P, 4), { tone: "faint" }) +
    // the rear cover's seal groove along the rim: 2.2 mm wide, foam strip in its bottom (film-back.md 17.3)
    Ln(k.planOutline(planC([X0 + 1.6, FLOOR.X[1] - 1.6], [-3.6, -1.4], 0.4), FLOOR.Z[1] * S, P, 3), { tone: "lo" });
  box("stand.floor", FLOOR.X, FLOOR.Y, FLOOR.Z, { r: 1.2, steps: 4, bevel: 1.0, tone: "lo", meta: { ground: true }, extra: groove + Ln(screws.map(([X, Y]) => ringTop(X, Y, 1.0, FLOOR.Z[1], 18)).join(""), { tone: "lo" }) + dots(screws.map(([X, Y]) => [X, Y, FLOOR.Z[1]]), { size: 0.5 }) });
}
{
  // a scale plate on the rear edge of the floor: 4.75 mm ticks, a long one every 7 perforations, one 66.5 mm frame end to end
  const ticks = { minor: [], major: [] };
  for (let i = 0; i <= RULER.ticks; i++) {
    const X = RULER.from + i * FILM.pitch;
    const big = i % 7 === 0;
    (big ? ticks.major : ticks.minor).push(path3([[X, RULER.Y[0], RULER.Z[1]], [X, RULER.Y[0], RULER.Z[1] - (big ? 1.5 : 0.8)]]));
  }
  box("stand.ruler", [RULER.X[0] - 0.6, RULER.X[1] + 0.6], RULER.Y, RULER.Z, { steps: 2, tone: "lo", meta: { ground: true }, extra: Ln(ticks.minor.join(""), { tone: "lo" }) + Ln(ticks.major.join(""), { tone: "mid" }) });
}
{
  const slot = Ln(k.planOutline(planC([X0, 40], [1.4, 2.2], 0.2), 28.5 * S, P, 3), { tone: "lo" });
  box("shell.bridge", [X0, 40], [0.2, 4.2], [FLOOR.Z[1], 28.5], { steps: 2, bevel: 0.6, extra: slot });
  for (const [Z, name] of [[[HALF + 0.15, HALF + 2.3], "shell.fence.top"], [[-HALF - 2.3, -HALF - 0.15], "shell.fence.low"]]) {
    box(name, [X0, 40], [-0.8, 0.2], Z, { steps: 2 });
  }
  box("shell.divider", [40, 42.5], [0.2, 27], [FLOOR.Z[1], 28.5], { steps: 2, bevel: 0.6 });
  const boss = [[45.6, 24], [94.5 - 3.1, 24]];
  box("shell.front", [42.5, 97.5], [27, 30], [FLOOR.Z[1], PLATE_Z[0]], { steps: 2, bevel: 0.6 });
  boss.forEach(([X, Y], i) => round(`shell.boss${i}`, X, Y, 2.6, [FLOOR.Z[1], PLATE_Z[0]], { inner: Ln(sideArc(X, Y, 2.6, -12) + sideArc(X, Y, 2.6, 12), { tone: "faint" }) }));
  box("shell.wall", [94.5, 97.5], [-4.8, 27], [FLOOR.Z[1], -19], { steps: 2, bevel: 0.6 });
}
// Top plate, cut away over the sprocket and along the pawl so the cam, the pawl and its pivot show.
// It keeps the button collar and the knob bushing; the pawl's cheeks are lugs on the walls of the slot.
const CUT_R = 9.6;
const SLOT = { half: 3.7, end: 14.0 }; // the slot runs out from the sprocket axis along the pawl, stopping where the button collar begins
const RADIAL = (() => {
  const d = [PAWL.pivot[0] - SP.x, PAWL.pivot[1] - SP.y];
  const len = Math.hypot(d[0], d[1]);
  return { d: [d[0] / len, d[1] / len], u: [-d[1] / len, d[0] / len], pivot: len };
})();
const radial = (t, side) => [SP.x + RADIAL.d[0] * t + RADIAL.u[0] * side, SP.y + RADIAL.d[1] * t + RADIAL.u[1] * side];
const PLATE_RING = (() => {
  const pts = [[40, 30], [97.5, 30], [97.5, 3.2], [72.4, 3.2]];
  const mid = Math.atan2(RADIAL.d[1], RADIAL.d[0]);
  const spread = Math.asin(SLOT.half / CUT_R);
  const arc = (from, to, count) => {
    for (let i = 0; i <= count; i++) {
      const a = from + ((to - from) * i) / count;
      pts.push([SP.x + CUT_R * Math.cos(a), SP.y + CUT_R * Math.sin(a)]);
    }
  };
  arc((14 / 180) * Math.PI, mid - spread, 4);
  const foot = Math.sqrt(CUT_R ** 2 - SLOT.half ** 2);
  pts.push(radial(SLOT.end, -SLOT.half), radial(SLOT.end, SLOT.half), radial(foot, SLOT.half));
  arc(mid + spread, (116 / 180) * Math.PI, 16);
  pts.push([40, SP.y + CUT_R * Math.sin((116 / 180) * Math.PI)]);
  return pts.filter((p, i, list) => i === 0 || Math.hypot(p[0] - list[i - 1][0], p[1] - list[i - 1][1]) > 1e-6);
})();
// Cut a polygon by the half-plane where f(point) >= 0 (Sutherland-Hodgman, one edge).
function clipBy(points, f) {
  const out = [];
  for (let i = 0; i < points.length; i++) {
    const a = points[i];
    const b = points[(i + 1) % points.length];
    const fa = f(a);
    const fb = f(b);
    if (fa >= 0) out.push(a);
    if ((fa >= 0) !== (fb >= 0)) {
      const t = fa / (fa - fb);
      out.push([a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t]);
    }
  }
  return out;
}
const inside = (point, ring) => {
  let hit = false;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const [xi, yi] = ring[i];
    const [xj, yj] = ring[j];
    if (yi > point[1] !== yj > point[1] && point[0] < ((xj - xi) * (point[1] - yi)) / (yj - yi) + xi) hit = !hit;
  }
  return hit;
};
// The plate is drawn as three pieces, so the pawl can sit in its slot and run under the plate to the button:
// the far and near sides of the slot, and the piece beyond the slot's end that carries the button and the knob.
const along = (p) => (p[0] - SP.x) * RADIAL.d[0] + (p[1] - SP.y) * RADIAL.d[1];
const across = (p) => (p[0] - SP.x) * RADIAL.u[0] + (p[1] - SP.y) * RADIAL.u[1];
const PLATE_PIECES = {
  far: clipBy(clipBy(PLATE_RING, (p) => SLOT.end - along(p)), (p) => across(p)),
  near: clipBy(clipBy(PLATE_RING, (p) => SLOT.end - along(p)), (p) => -across(p)),
  end: clipBy(PLATE_RING, (p) => along(p) - SLOT.end),
};
{
  const z = PLATE_Z[1];
  const screws = [[44, 27.4], [94.6, 27.4], [94.6, 5.8], [60.2, 27.4]];
  const ia = M.INDEX_ANGLE;
  const indexPt = (r, side) => [SP.x + r * Math.cos(ia) - side * Math.sin(ia), SP.y + r * Math.sin(ia) + side * Math.cos(ia), z];
  // the fixed index mark: an engraved arrowhead on the plate's cut edge, pointing at the hub
  const index = [indexPt(CUT_R + 0.3, 0), indexPt(CUT_R + 2.4, 0.75), indexPt(CUT_R + 2.4, -0.75)];
  for (const [piece, ring] of Object.entries(PLATE_PIECES)) {
    const mine = screws.filter((p) => inside(p, ring));
    let extra = Ln(mine.map(([X, Y]) => ringTop(X, Y, 1.1, z, 18)).join(""), { tone: "lo" }) + dots(mine.map(([X, Y]) => [X, Y, z]), { size: 0.5 });
    if (inside(index[1], ring)) extra += Ln(path3(index, true), { tone: "hi" });
    if (inside([SPOOL.x, SPOOL.y], ring)) extra += Ln(ringTop(SPOOL.x, SPOOL.y, 3.4, z, 32), { tone: "lo" });
    prism(`shell.plate.${piece}`, ring, PLATE_Z, { convex: false, extra });
  }
}

// --- sprocket, one printed part with its cam, on a fixed 3 mm pin in a floor boss
round("sprocket.boss", SP.x, SP.y, 4.0, PIN.boss, { bevel: 0.6, extra: Ln(ringTop(SP.x, SP.y, 1.5, PIN.boss[1], 24), { tone: "lo" }) });
const flangeLowZ = [-SP.flangeGap / 2 - SP.flangeT, -SP.flangeGap / 2];
const flangeHighZ = [SP.flangeGap / 2, SP.flangeGap / 2 + SP.flangeT];
round("sprocket.pin", SP.x, SP.y, SP.pinR, [PIN.boss[1], flangeLowZ[0]], { tone: "mid", steps: 24 });
round("sprocket.flange.low", SP.x, SP.y, SP.flangeR, flangeLowZ, { bore: SP.pinR, tone: "hi", bevel: 0.5 });
const REST = M.stateOf({ theta: 0, button: 0 });
const teethRest = pose.teeth(REST);
// rest-pose teeth, recorded as their true prisms for the audit: an engaged tooth splits at the film's outer face
const TEETH_REST = pose.toothParts(0, REST.rollR);
const toothShapes = (which) =>
  TEETH_REST.filter((part) => (which === "tips" ? part.tip : part.group === which)).map((part) =>
    record(A.extruded(ringW(which === "tips" ? part.tip : part.body), pose.TOOTH_Z[0] * S, (pose.TOOTH_Z[1] - pose.TOOTH_Z[0]) * S, { name: `sprocket.tooth${part.i}${which === "tips" ? ".tip" : ""}`, owner: "sprocket" })),
  );
put("sprocket.teeth.back", [SP.x, SP.y + 6, -FILM.perfRow], `<g data-part="teeth-back">${teethRest.back}</g>`, toothShapes("back"));
round("sprocket.land.low", SP.x, SP.y, SP.hubR, [flangeLowZ[1], -SP.reliefZ], { bore: SP.pinR, tone: "hi", meta: { owner: "sprocket" } });
round("sprocket.relief", SP.x, SP.y, SP.reliefR, [-SP.reliefZ, SP.reliefZ], { bore: SP.pinR, tone: "hi", meta: { owner: "sprocket" } });
round("sprocket.land.high", SP.x, SP.y, SP.hubR, [SP.reliefZ, flangeHighZ[0]], { bore: SP.pinR, tone: "hi", meta: { owner: "sprocket" } });
put("sprocket.teeth.front", [SP.x - 6, SP.y - 6, -FILM.perfRow], `<g data-part="teeth-front">${teethRest.front}</g>`, toothShapes("front"));

// --- the film strip, cut at the bridge section, round the sprocket and into the roll
const filmRest = pose.film(REST, X0);
const FILM_CLIP = `M-60 -60H${WIDTH + 60}V${HEIGHT + 60}H-60Z`;
{
  // the perforations are real holes: the teeth pass through them
  const holes = pose.perfCentres(REST, X0).map(({ c, n, t }) => A.orientedBox(W(c), [dirW([t[0], t[1], 0]), dirW([0, 0, 1]), dirW([n[0], n[1], 0])], [(FILM.perfAlong / 2) * S, (FILM.perfAcross / 2) * S, 0.5 * S]));
  put("film", [SP.x, -0.07, 0], `<clipPath id="ft-film"><path data-part="film-clip" clip-rule="evenodd" d="${FILM_CLIP}${filmRest.holes}"/></clipPath><g clip-path="url(#ft-film)" data-part="film">${filmRest.body}</g><g data-part="film-rims">${filmRest.rims}</g>`, [record(A.extruded(ringW(filmRest.ring), -HALF * S, FILM.width * S, { name: "film", owner: "film", cut: holes }))]);
}
put("sprocket.teeth.tips", [SP.x + 6, SP.y - 9, -FILM.perfRow], `<g data-part="teeth-tips">${teethRest.tips}</g>`, toothShapes("tips"));
round("sprocket.flange.high", SP.x, SP.y, SP.flangeR, flangeHighZ, { bore: SP.pinR, tone: "hi", bevel: 0.5 });
round("sprocket.neck", SP.x, SP.y, 5.0, [flangeHighZ[1], CAM.z0], { bore: SP.pinR, tone: "hi", meta: { owner: "sprocket" } });
const pocketRest = pose.pocket(REST);
round("cam.disc", SP.x, SP.y, CAM.r, [CAM.z0, CAM.z1], {
  bore: SP.pinR,
  cut: A.extruded(ringW(pose.pocketRing(0, 0)), (CAM.z1 - CAM.pocket.depth) * S, (CAM.pocket.depth + 0.5) * S, { name: "cam.pocket" }),
  tone: "hi",
  bevel: 0.6,
  meta: { owner: "sprocket" },
  extra: `<clipPath id="ft-pocket"><path data-part="pocket-clip" d="${pocketRest.clip}"/></clipPath><g clip-path="url(#ft-pocket)" data-part="pocket">${pocketRest.svg}</g>${Ln(pocketRest.rim, { tone: "lit" }).replace("<path", '<path data-part="pocket-rim"')}`,
});

// --- pawl: lever on a horizontal pin between two cheeks hanging from the top plate
const pivotDir = (() => {
  const d = [PAWL.tip[0] - PAWL.pivot[0], PAWL.tip[1] - PAWL.pivot[1]];
  const len = Math.hypot(d[0], d[1]);
  return [d[0] / len, d[1] / len];
})();
const pinDir = [-pivotDir[1], pivotDir[0]];
const pivotZ = PAWL.z0 + PAWL.thick / 2;
const cheekRing = (side) => {
  const o = [PAWL.pivot[0] + pinDir[0] * side * (CHEEK.gap + CHEEK.t / 2) + pivotDir[0] * CHEEK.shift, PAWL.pivot[1] + pinDir[1] * side * (CHEEK.gap + CHEEK.t / 2) + pivotDir[1] * CHEEK.shift];
  const a = [pivotDir[0] * CHEEK.half, pivotDir[1] * CHEEK.half];
  const b = [pinDir[0] * CHEEK.t / 2, pinDir[1] * CHEEK.t / 2];
  return [[o[0] - a[0] - b[0], o[1] - a[1] - b[1]], [o[0] + a[0] - b[0], o[1] + a[1] - b[1]], [o[0] + a[0] + b[0], o[1] + a[1] + b[1]], [o[0] - a[0] + b[0], o[1] - a[1] + b[1]]];
};
const near = G.dot3(dirW([pinDir[0], pinDir[1], 0]), V) > 0 ? 1 : -1;
const pinFrame = G.frameAlong(W([PAWL.pivot[0], PAWL.pivot[1], pivotZ]), G.unit3(dirW([pinDir[0] * near, pinDir[1] * near, 0])));
const pinEnd = CHEEK.gap + CHEEK.t + 0.6;
const pinIn = CHEEK.gap + CHEEK.t;
put("pawl.pin.far", [PAWL.pivot[0] - pinDir[0] * near * 4, PAWL.pivot[1] - pinDir[1] * near * 4, pivotZ], sol(G.disc(-pinEnd * S, -pinIn * S, 1.5 * S, pinFrame, P), { tone: "mid" }), [record(A.disc(pinFrame, -pinEnd * S, -pinIn * S, 1.5 * S, { name: "pawl.pin.far", owner: "pawl" }))]);
prism("pawl.cheek.far", cheekRing(-near), CHEEK.Z, { meta: { owner: "pawl" } });
// the lever passes under the plate where the slot ends
const LEVER_SPLIT = -(SLOT.end - RADIAL.pivot);
const pawlRest = pose.pawl(REST, LEVER_SPLIT);
const nubClip = (pocketPts, abovePts) => {
  const orient = (pts) => {
    let area = 0;
    pts.forEach(([x, y], i) => {
      const [x2, y2] = pts[(i + 1) % pts.length];
      area += x * y2 - x2 * y;
    });
    return area < 0 ? [...pts].reverse() : pts;
  };
  return k.pathOf(orient(pocketPts), true) + (abovePts.length >= 3 ? k.pathOf(orient(abovePts), true) : "");
};
{
  const leverShapes = [record(A.prism(pose.pawlFrame(0), pose.LEVER_SECTION, LEVER_SPLIT * S, pose.LEVER.s1 * S, { name: "pawl.lever", owner: "pawl" }))];
  const leverEndShapes = [record(A.prism(pose.pawlFrame(0), pose.LEVER_SECTION, pose.LEVER.s0 * S, LEVER_SPLIT * S, { name: "pawl.lever.end", owner: "pawl" }))];
  put("pawl.lever", [PAWL.pivot[0], PAWL.pivot[1], pivotZ], `<g data-part="lever">${pawlRest.lever}</g>`, leverShapes);
  put("pawl.lever.end", [PAWL.end[0], PAWL.end[1], pivotZ], `<g data-part="lever-end">${pawlRest.leverEnd}</g>`, leverEndShapes);
  const F = pose.pawlFrame(0);
  const nubFrame = { o: G.add3(F.o, G.mul3(F.v, -(PAWL.thick / 2) * S)), a: G.mul3(F.v, -1), u: F.u, v: F.a };
  const nubShape = record(A.prism(nubFrame, [[-pose.NUB.half * S, pose.NUB.s0 * S], [pose.NUB.half * S, pose.NUB.s0 * S], [pose.NUB.half * S, pose.NUB.s1 * S], [-pose.NUB.half * S, pose.NUB.s1 * S]], 0, pose.NUB.depth * S, { name: "pawl.nub", owner: "pawl" }));
  put("pawl.nub", [PAWL.tip[0], PAWL.tip[1], CAM.z1], `<clipPath id="ft-nub"><path data-part="nub-clip" d="${nubClip(pocketRest.rimPts, pawlRest.abovePts)}"/></clipPath><g clip-path="url(#ft-nub)" data-part="nub">${pawlRest.nub}</g>`, [nubShape]);
}
prism("pawl.cheek.near", cheekRing(near), CHEEK.Z, { meta: { owner: "pawl" } });
put("pawl.pin.near", [PAWL.pivot[0] + pinDir[0] * near * 4, PAWL.pivot[1] + pinDir[1] * near * 4, pivotZ], sol(G.disc(pinIn * S, pinEnd * S, 1.5 * S, pinFrame, P), { tone: "mid", inner: "" }) + k.dotsSvg([k.iso(G.pointOf(pinFrame, pinEnd * S, 0, 0), P)], { size: 0.5 }), [record(A.disc(pinFrame, pinIn * S, pinEnd * S, 1.5 * S, { name: "pawl.pin.near", owner: "pawl" }))]);
box("pawl.shelf", SHELF.X, SHELF.Y, SHELF.Z, { r: 0.6, steps: 3, bevel: 0.5, extra: Ln(ringTop(...pose.springAt(SPRING_S), 2.0, SHELF.Z[1], 24), { tone: "lo" }) });
const springRest = pose.spring(REST, SHELF.Z[1], SPRING_S);
{
  const c = pose.springAt(SPRING_S);
  const top = PAWL.z0;
  put("pawl.spring", [c[0], c[1], (SHELF.Z[1] + top) / 2], `<g data-part="spring">${Ln(springRest.back, { tone: "lo" })}${Ln(springRest.front, { tone: "mid" })}</g>`, [record(A.ring(AXIS(c[0], c[1]), SHELF.Z[1] * S, top * S, 1.3 * S, 1.75 * S, { name: "pawl.spring", owner: "pawl" }))]);
}

// --- release button through its collar in the top plate
const buttonBody = (press, Z) => sol(k.cylinder(-BUTTON.at[1] * S, -BUTTON.at[0] * S, BUTTON.r * S, (Z[0] - press) * S, (Z[1] - Z[0]) * S, P, 40, 0.5), { tone: "hi", crease: "lo" });
put("button.low", [BUTTON.at[0], BUTTON.at[1], 27], `<g data-part="button-low">${buttonBody(0, [PAWL.z0 + PAWL.thick, PLATE_Z[0]])}</g>`, [record(A.cylinder(-BUTTON.at[1] * S, -BUTTON.at[0] * S, BUTTON.r * S, (PAWL.z0 + PAWL.thick) * S, (PLATE_Z[0] - PAWL.z0 - PAWL.thick) * S, { name: "button.low", owner: "button" }))]);
round("button.collar", BUTTON.at[0], BUTTON.at[1], COLLAR.rOut, COLLAR.Z, { bore: COLLAR.rIn, bevel: 0.4, meta: { owner: "button" } });
put("button.high", [BUTTON.at[0], BUTTON.at[1], 34], `<g data-part="button-high">${buttonBody(0, [COLLAR.Z[1], BUTTON_TOP])}</g>`, [record(A.cylinder(-BUTTON.at[1] * S, -BUTTON.at[0] * S, BUTTON.r * S, COLLAR.Z[1] * S, (BUTTON_TOP - COLLAR.Z[1]) * S, { name: "button.high", owner: "button" }))]);

// --- top hub with the index dot, standing through the cut-away plate
round("cam.hub", SP.x, SP.y, CAM.hubR, [CAM.z1, CAM.hubTop], { bore: SP.pinR, tone: "hi", bevel: 0.5, meta: { owner: "sprocket" }, extra: `<g data-part="hub-dot">${pose.hubMarks(REST)}</g>` });

// --- take-up spool on its shaft, with the felt clutch, and the advance knob
const SPL = SPOOL;
round("spool.boss", SPL.x, SPL.y, 4.0, SPOOL_Z.boss, { bevel: 0.5 });
{
  const helix = pose.helix([SPL.x, SPL.y], 2.5, SPOOL_Z.boss[1], -SPOOL_Z.flange - SPL.flangeT, 4);
  const shaft = sol(k.cylinder(-SPL.y * S, -SPL.x * S, SPL.shaftR * S, SPOOL_Z.boss[1] * S, (-SPOOL_Z.flange - SPL.flangeT - SPOOL_Z.boss[1]) * S, P, 24), { tone: "mid" });
  put("spool.clutch.spring", [SPL.x, SPL.y, -21], Ln(helix.back, { tone: "lo" }) + shaft + Ln(helix.front, { tone: "mid" }), [
    record(A.cylinder(-SPL.y * S, -SPL.x * S, SPL.shaftR * S, SPOOL_Z.boss[1] * S, (-SPOOL_Z.flange - SPL.flangeT - SPOOL_Z.boss[1]) * S, { name: "spool.shaft.low", owner: "spool" })),
    record(A.ring(AXIS(SPL.x, SPL.y), SPOOL_Z.boss[1] * S, (-SPOOL_Z.flange - SPL.flangeT) * S, 2.2 * S, 2.8 * S, { name: "spool.clutch.spring", owner: "spool" })),
  ]);
}
round("spool.flange.low", SPL.x, SPL.y, SPL.flangeR, [-SPOOL_Z.flange - SPL.flangeT, -SPOOL_Z.flange], { bore: SPL.shaftR, tone: "hi", bevel: 0.5, meta: { owner: "spool" } });
put("spool.roll", [SPL.x, SPL.y, 0], `<g data-part="roll">${pose.roll(REST, X0)}</g>`, [record(A.ring(AXIS(SPL.x, SPL.y), -HALF * S, HALF * S, SPL.shaftR * S, (REST.rollR + FILM.thickness) * S, { name: "spool.roll", owner: "film" }))]);
round("spool.flange.high", SPL.x, SPL.y, SPL.flangeR, [SPOOL_Z.flange, SPOOL_Z.flange + SPL.flangeT], { bore: SPL.shaftR, tone: "hi", bevel: 0.5, meta: { owner: "spool" }, extra: `<g data-part="flange-holes">${pose.flangeHoles(REST, SPOOL_Z.flange + SPL.flangeT)}</g>` });
round("spool.felt", SPL.x, SPL.y, 5.0, SPOOL_Z.felt, { bore: SPL.shaftR, tone: "lo", meta: { owner: "spool" } });
{
  // drive collar, fixed to the shaft by a set screw
  const screwAt = (() => {
    const t = Math.atan2(-V[0], -V[1]);
    return [SPL.x + 4.0 * Math.cos(t), SPL.y + 4.0 * Math.sin(t), (SPOOL_Z.collar[0] + SPOOL_Z.collar[1]) / 2];
  })();
  round("spool.collar", SPL.x, SPL.y, 4.0, SPOOL_Z.collar, { bore: SPL.shaftR, bevel: 0.4, meta: { owner: "spool" }, extra: dots([screwAt], { size: 0.8, tone: "hi" }) });
}
round("spool.shaft", SPL.x, SPL.y, SPL.shaftR, [SPOOL_Z.collar[1], SPOOL_Z.bush[0]], { meta: { owner: "spool" } });
round("spool.bushing", SPL.x, SPL.y, 3.2, SPOOL_Z.bush, { bore: SPL.shaftR, bevel: 0.4 });
round("knob.washer", SPL.x, SPL.y, 4.4, [PLATE_Z[1], KNOB_Z], { bore: SPL.shaftR, tone: "lo", meta: { owner: "knob" } });
{
  const knobRest = pose.knob(REST, KNOB_Z);
  const z1 = KNOB_Z + KNOB.h;
  const bands = Ln(sideArc(SPL.x, SPL.y, KNOB.r, KNOB_Z + 1.2, 96) + sideArc(SPL.x, SPL.y, KNOB.r, z1 - 1.2, 96), { tone: "faint" });
  const face = Ln(ringTop(SPL.x, SPL.y, KNOB.r - 1.6, z1, 96) + ringTop(SPL.x, SPL.y, 3.0, z1, 40), { tone: "lo" });
  round("knob", SPL.x, SPL.y, KNOB.r, [KNOB_Z, z1], {
    bore: SPL.shaftR,
    tone: "hi",
    bevel: 0.8,
    meta: { owner: "knob" },
    inner: `<g data-part="knurl">${knobRest.knurl}</g>` + bands,
    extra: face + `<g data-part="knob-top">${knobRest.pointer}${knobRest.shaft}</g>`,
  });
}

// --- settle the painter's order from the recorded shapes
A.settle(R, P);
R.items.sort((a, b) => a.key - b.key);
const groups = R.items.map((item) => `<g class="it" data-name="${item.name}">${item.svg}</g>`).join("");

const LABEL_TEXT =
  "A cutaway of the right-hand film transport of a 65 by 24 mm panoramic film back, on a display base. Film comes in from the left over the bridge, wraps the 14-tooth sprocket on its lower perforation row and winds on to the take-up spool. On top of the sprocket a cam disc has one pocket; a pawl lever on a pin drops its tip into the pocket and locks the sprocket after exactly one turn, 66.5 mm of film. A release button presses the far end of the pawl to lift the tip, and the advance knob turns the spool through a felt clutch.";

const svg = k.figureSvg({ width: WIDTH, height: HEIGHT, label: LABEL_TEXT, body: [halo, groups] });

const DATA = {
  P,
  S,
  X0,
  KNOB_Z,
  SHELF_Z: SHELF.Z[1],
  SPRING_S,
  BUTTON_LOW: [PAWL.z0 + PAWL.thick, PLATE_Z[0]],
  BUTTON_HIGH: [COLLAR.Z[1], BUTTON_TOP],
  FLANGE_TOP: SPOOL_Z.flange + SPL.flangeT,
  FILM_CLIP,
  LEVER_SPLIT,
};

const strip = (source) => source.replace(/^import .*$/gm, "").replace(/^export /gm, "");
const namesOf = (source) => [...source.matchAll(/^export (?:const|function|let) ([A-Za-z_$][\w$]*)/gm)].map((m) => m[1]);
const modelSource = readFileSync(path.join(HERE, "model.mjs"), "utf8");
const latheSource = readFileSync(path.join(HOME, "kit/lathe.mjs"), "utf8");
const poseSource = readFileSync(path.join(HERE, "pose.mjs"), "utf8");
const KIT_NAMES = ["iso", "pathOf", "extrude", "cylinder", "slabOf", "solidSvg", "lineSvg", "dotsSvg", "fadedSvg", "ring", "sideArc", "depthOf", "translateAlong", "cameraOf"];
const modules =
  `const M = (() => {${strip(modelSource)}\nreturn { ${namesOf(modelSource).join(", ")} };})();\n` +
  `const G = (() => {${strip(latheSource)}\nreturn { ${namesOf(latheSource).join(", ")} };})();\n` +
  `const K = { ${KIT_NAMES.join(", ")} };\n` +
  `${strip(poseSource)}\n`;

const LIVE = readFileSync(path.join(HERE, "live.js"), "utf8").replace("__DATA__", JSON.stringify(DATA));

const CSS = `
.ft-void{fill:var(--anatomy-shade-0);stroke:none}
.iso[data-theme="light"] .ft-void{fill:#cfcfcb}
.ft-stage [data-part="lever"] .iso-edge,.ft-stage [data-part="nub"] .iso-edge,.ft-stage [data-part="pocket-rim"]{stroke-width:1.15px}
.ft-stage{outline:none;cursor:pointer;touch-action:pan-y;-webkit-tap-highlight-color:transparent}
.ft-stage:focus-visible{outline:1px solid var(--anatomy-muted);outline-offset:6px}
.ft-sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
`;

const body =
  `<style>${CSS}</style>` +
  k.plateHtml({
    fig: "Fig 1",
    title: "One turn, one frame",
    hint: "Click or space · advance one frame",
    readout: M.readoutOf(REST, "locked"),
    keys: [
      { mark: "lit", label: "Pawl tip and cam pocket: the lock to watch" },
      { mark: "raised", label: "Sprocket, 14 teeth on the lower perforation row; take-up spool and knob" },
    ],
    caption:
      "The sprocket has 14 teeth on a 21.17 mm pitch circle, so one turn moves 14 perforations, 66.5 mm of film, and its cam's single pocket comes back under the pawl, which drops in and locks it.",
    body: `<div class="iso-stage ft-stage" tabindex="0" role="button" aria-label="Film transport. Press Space, Enter or click to press the release button and advance the film one frame.">${svg}<span class="ft-sr" role="status" aria-live="polite" data-status></span></div>`,
  });

const page = k.pageHtml({ title: "Film transport", theme: THEME, body, script: kitScript() + modules + LIVE });
const name = THEME === "light" ? "film-transport-light.html" : "film-transport.html";
writeFileSync(path.join(HERE, name), page);
console.log("wrote", name, `${(page.length / 1024).toFixed(0)} KB`, `${R.items.length} items`, `scale ${KS.toFixed(3)}`);

// The pawl tip sits inside the cam's pocket, a concave host no painter's order can draw; the page clips the tip
// to the pocket's rim below the cam face instead (pose.pawl and live.js), as content seen through an opening.
A.auditOrExit(R, P, { allow: [["cam.disc", "pawl.nub"]] });
