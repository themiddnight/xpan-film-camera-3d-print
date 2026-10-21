// Geometry of the parts that move, drawn for one state of the model.
// The build calls it for the rest pose and the page calls the same source every frame.
// It takes the kit (k), the lathe module (G), the model (M), the projection (P) and the scale (S, world units per mm).

export function makePose(k, G, M, P, S) {
  const TAU = Math.PI * 2;
  const W = ([X, Y, Z]) => [-Y * S, -X * S, Z * S];
  const dirW = ([X, Y, Z]) => [-Y, -X, Z];
  const at = (p) => k.iso(W(p), P);
  const V = G.viewOf(P);
  const faces = (n) => G.dot3(dirW(n), V);
  const path3 = (points, closed = false) => k.pathOf(points.map(at), closed);
  const ringW = (points) => points.map(([X, Y]) => [-Y * S, -X * S]);
  const prismZ = (points, z0, z1, options = {}) => k.extrude(ringW(points), z0 * S, (z1 - z0) * S, P, options);
  const wrap = (a) => a - TAU * Math.round(a / TAU);
  const { FILM, SPROCKET, CAM, PAWL, SPOOL, KNOB } = M;
  const HALF = FILM.width / 2;
  const T = FILM.thickness;

  // Film path, measured along the film centreline from the cut end at x0.
  function filmGeometry(rollR, x0) {
    const path = M.filmPath(rollR);
    const rp = SPROCKET.pitchR;
    const a = SPROCKET.x - x0;
    const w = path.wrap * rp;
    const f = path.free;
    const dir = [Math.cos(path.leave + Math.PI / 2), Math.sin(path.leave + Math.PI / 2)];
    const rb = path.rb;
    const out = [Math.cos(path.leave), Math.sin(path.leave)];
    // centre point, unit normal toward the face that is visible from the rear-right
    function frameAt(s) {
      if (s <= a) return { c: [x0 + s, SPROCKET.y - rp], n: [0, -1], seg: 0 };
      if (s <= a + w) {
        const phi = -Math.PI / 2 + (s - a) / rp;
        return { c: [SPROCKET.x + rp * Math.cos(phi), SPROCKET.y + rp * Math.sin(phi)], n: [Math.cos(phi), Math.sin(phi)], seg: 1 };
      }
      if (s <= a + w + f) {
        const u = s - a - w;
        return { c: [path.from[0] + dir[0] * u, path.from[1] + dir[1] * u], n: out, seg: 2 };
      }
      const psi = path.arrive - (s - a - w - f) / rb;
      return { c: [SPOOL.x + rb * Math.cos(psi), SPOOL.y + rb * Math.sin(psi)], n: [Math.cos(psi), Math.sin(psi)], seg: 3 };
    }
    return { path, a, w, f, rb, end: a + w + f, frameAt };
  }

  function centreline(geo, from, to, step = 0.5) {
    const marks = [from, geo.a, geo.a + geo.w, to].filter((s) => s >= from && s <= to);
    const out = [];
    for (let i = 0; i < marks.length - 1; i++) {
      const span = marks[i + 1] - marks[i];
      const count = Math.max(1, Math.ceil(span / step));
      for (let j = i === 0 ? 0 : 1; j <= count; j++) out.push(geo.frameAt(marks[i] + (span * j) / count));
    }
    return out;
  }

  // The visible face of the film, offset half a thickness from the centreline toward the viewer.
  const faceOf = ({ c, n }) => {
    const sign = faces([n[0], n[1], 0]) >= 0 ? 1 : -1;
    return { p: [c[0] + (n[0] * T * sign) / 2, c[1] + (n[1] * T * sign) / 2], n: [n[0] * sign, n[1] * sign] };
  };

  function perfOutline(sc, zc, from, to, geo) {
    const half = [FILM.perfAlong / 2, FILM.perfAcross / 2];
    const r = FILM.perfCorner;
    const pts = [];
    const corners = [
      [half[0] - r, half[1] - r, 0],
      [-half[0] + r, half[1] - r, Math.PI / 2],
      [-half[0] + r, -half[1] + r, Math.PI],
      [half[0] - r, -half[1] + r, (3 * Math.PI) / 2],
    ];
    for (const [cx, cz, start] of corners) for (let i = 0; i <= 3; i++) {
      const t = start + (i / 3) * (Math.PI / 2);
      pts.push([sc + cx + r * Math.cos(t), zc + cz + r * Math.sin(t)]);
    }
    const clipped = pts.map(([s, z]) => [Math.min(to, Math.max(from, s)), z]);
    const cut = clipped.some(([s], i) => s !== pts[i][0]);
    const world = clipped.map(([s, z]) => {
      const face = faceOf(geo.frameAt(s));
      return [face.p[0], face.p[1], z];
    });
    return { d: path3(world, true), cut };
  }

  // The film strip from its cut end at the bridge to where it meets the roll, with both perforation rows.
  function film(state, x0) {
    const geo = filmGeometry(state.rollR, x0);
    const line = centreline(geo, 0, geo.end);
    const outer = line.map(({ c, n }) => [c[0] + (n[0] * T) / 2, c[1] + (n[1] * T) / 2]);
    const inner = line.map(({ c, n }) => [c[0] - (n[0] * T) / 2, c[1] - (n[1] * T) / 2]);
    const ring = [...outer, ...inner.reverse()];
    const body = k.solidSvg(prismZ(ring, -HALF, HALF, { convex: false }), { tone: "hi", crease: "lo" });
    const c0 = geo.a + (M.TOOTH_PHASE + Math.PI / 2) * SPROCKET.pitchR;
    const phase = ((c0 + state.film) % FILM.pitch + FILM.pitch) % FILM.pitch;
    const holes = [];
    const rims = [];
    for (let s = phase - FILM.pitch; s < geo.end + FILM.pitch; s += FILM.pitch) {
      if (s + FILM.perfAlong / 2 < 0 || s - FILM.perfAlong / 2 > geo.end) continue;
      for (const zc of [-FILM.perfRow, FILM.perfRow]) {
        const hole = perfOutline(s, zc, 0, geo.end, geo);
        holes.push(hole.d);
        if (!hole.cut) rims.push(hole.d);
      }
    }
    // the holes are cut out of the strip with an even-odd clip, so the hub and teeth behind show through them
    return { geo, body, holes: holes.join(""), rims: k.lineSvg(rims.join(""), { tone: "mid" }), ring };
  }

  // Perforation centres on the visible strip, with the film's tangent and normal there, for the audit's hole cuts.
  function perfCentres(state, x0) {
    const geo = filmGeometry(state.rollR, x0);
    const c0 = geo.a + (M.TOOTH_PHASE + Math.PI / 2) * SPROCKET.pitchR;
    const phase = ((c0 + state.film) % FILM.pitch + FILM.pitch) % FILM.pitch;
    const out = [];
    for (let s = phase; s < geo.end; s += FILM.pitch) {
      const f = geo.frameAt(s);
      for (const zc of [-FILM.perfRow, FILM.perfRow]) out.push({ c: [f.c[0], f.c[1], zc], n: f.n, t: [-f.n[1], f.n[0]] });
    }
    return out;
  }

  // The wound roll: the outer layer carries perforations that turn with the spool.
  function roll(state, x0) {
    const geo = filmGeometry(state.rollR, x0);
    const R = state.rollR + T;
    const body = k.solidSvg(k.cylinder(-SPOOL.y * S, -SPOOL.x * S, R * S, -HALF * S, FILM.width * S, P, 96), { tone: "hi", crease: "lo" });
    const c0 = geo.a + (M.TOOTH_PHASE + Math.PI / 2) * SPROCKET.pitchR;
    const phase = ((c0 + state.film) % FILM.pitch + FILM.pitch) % FILM.pitch;
    const list = [];
    const startS = geo.end;
    const turn = TAU * geo.rb;
    let s = phase + Math.ceil((startS - phase) / FILM.pitch) * FILM.pitch;
    for (; s < startS + turn; s += FILM.pitch) {
      const psi = geo.path.arrive - (s - startS) / geo.rb;
      const facing = faces([Math.cos(psi), Math.sin(psi), 0]);
      if (facing < 0.05) continue;
      const alpha = Math.min(1, Math.max(0, (facing - 0.05) / 0.45));
      const pts = [];
      const half = [FILM.perfAlong / 2, FILM.perfAcross / 2];
      const r = FILM.perfCorner;
      for (const zc of [-FILM.perfRow, FILM.perfRow]) {
        const ring = [];
        for (const [cx, cz, start] of [[half[0] - r, half[1] - r, 0], [-half[0] + r, half[1] - r, Math.PI / 2], [-half[0] + r, -half[1] + r, Math.PI], [half[0] - r, -half[1] + r, 1.5 * Math.PI]]) {
          for (let i = 0; i <= 3; i++) {
            const t = start + (i / 3) * (Math.PI / 2);
            const ds = cx + r * Math.cos(t);
            const ang = psi - ds / R;
            ring.push([SPOOL.x + R * Math.cos(ang), SPOOL.y + R * Math.sin(ang), zc + cz + r * Math.sin(t)]);
          }
        }
        pts.push(path3(ring, true));
      }
      list.push([pts.join(""), alpha]);
    }
    const holes = list.map(([d, alpha]) => `<path class="ft-void" d="${d}" fill-opacity="${alpha.toFixed(2)}"/>`).join("");
    return body + holes + k.fadedSvg(list, { tone: "mid" });
  }

  // Teeth turned away are drawn behind the hub; the rest in front of it and behind the film, showing through the perforations.
  const toothGroup = (phi) => (faces([Math.cos(phi), Math.sin(phi), 0]) < 0 ? "back" : "front");

  // One tooth as a tapered prism between two radii: 1.4 along the film at the root, 1.0 at the tip.
  function toothRing(phi, ra, rb) {
    const t = SPROCKET.tooth;
    const n = [Math.cos(phi), Math.sin(phi)];
    const tg = [-n[1], n[0]];
    const r0 = SPROCKET.hubR - 0.02;
    const r1 = SPROCKET.hubR + t.height;
    const half = (r) => (t.along + ((t.tip - t.along) * (r - r0)) / (r1 - r0)) / 2;
    const c = [SPROCKET.x, SPROCKET.y];
    return [
      [c[0] + n[0] * ra - tg[0] * half(ra), c[1] + n[1] * ra - tg[1] * half(ra)],
      [c[0] + n[0] * ra + tg[0] * half(ra), c[1] + n[1] * ra + tg[1] * half(ra)],
      [c[0] + n[0] * rb + tg[0] * half(rb), c[1] + n[1] * rb + tg[1] * half(rb)],
      [c[0] + n[0] * rb - tg[0] * half(rb), c[1] + n[1] * rb - tg[1] * half(rb)],
    ];
  }

  // Where a tooth's centre line crosses the film's outer face: on the wrap that face is a cylinder,
  // before and after it the face is the plane of the straight film.
  function filmFaceR(phi, leave) {
    const face = SPROCKET.hubR + T;
    const rel = wrap(phi);
    const before = rel + Math.PI / 2;
    const after = rel - leave;
    if (before >= 0 && after <= 0) return face;
    return face / Math.cos(before < 0 ? before : after);
  }

  // Fourteen teeth on the lower perforation row. Each is drawn behind the film and seen through its hole;
  // the part of an engaged tooth that stands proud of the film is drawn again in front of it.
  const TOOTH_R = [SPROCKET.hubR - 0.02, SPROCKET.hubR + SPROCKET.tooth.height];
  const TOOTH_Z = [-FILM.perfRow - SPROCKET.tooth.across / 2, -FILM.perfRow + SPROCKET.tooth.across / 2];
  function toothParts(theta, rollR) {
    const leave = M.filmPath(rollR).leave;
    const out = [];
    for (let i = 0; i < M.TEETH; i++) {
      const phi = M.TOOTH_PHASE + theta + (i * TAU) / M.TEETH;
      const group = toothGroup(phi);
      const cut = filmFaceR(phi, leave);
      const proud = group === "front" && cut > 0 && cut < TOOTH_R[1] - 0.02;
      out.push({ i, phi, group, body: toothRing(phi, TOOTH_R[0], proud ? cut : TOOTH_R[1]), tip: proud ? toothRing(phi, cut, TOOTH_R[1]) : null });
    }
    return out;
  }

  function teeth(state) {
    const groups = { back: [], front: [], tips: [] };
    const solid = (ring) => k.solidSvg(prismZ(ring, TOOTH_Z[0], TOOTH_Z[1], { convex: true }), { tone: "hi", crease: "lo" });
    for (const part of toothParts(state.theta, state.rollR)) {
      groups[part.group].push(solid(part.tip ? toothRing(part.phi, TOOTH_R[0], TOOTH_R[1]) : part.body));
      if (part.tip) groups.tips.push(solid(part.tip));
    }
    return { back: groups.back.join(""), front: groups.front.join(""), tips: groups.tips.join("") };
  }

  // The pocket in the cam's top face, and the index dot on the top hub, both turning with the sprocket.
  function pocketRing(theta, z) {
    const p = CAM.pocket;
    const ang = M.POCKET_ANGLE + theta;
    const n = [Math.cos(ang), Math.sin(ang)];
    const tg = [-n[1], n[0]];
    const c = [SPROCKET.x + n[0] * p.r, SPROCKET.y + n[1] * p.r];
    const r = 0.35;
    const half = [p.radial / 2, p.width / 2];
    const pts = [];
    for (const [cx, cy, start] of [[half[0] - r, half[1] - r, 0], [-half[0] + r, half[1] - r, Math.PI / 2], [-half[0] + r, -half[1] + r, Math.PI], [half[0] - r, -half[1] + r, 1.5 * Math.PI]]) {
      for (let i = 0; i <= 3; i++) {
        const t = start + (i / 3) * (Math.PI / 2);
        const u = cx + r * Math.cos(t);
        const v = cy + r * Math.sin(t);
        pts.push([c[0] + n[0] * u + tg[0] * v, c[1] + n[1] * u + tg[1] * v, z]);
      }
    }
    return pts;
  }

  function pocket(state) {
    const top = pocketRing(state.theta, CAM.z1);
    const floor = pocketRing(state.theta, CAM.z1 - CAM.pocket.depth);
    const walls = [];
    const n = top.length;
    for (let i = 0; i < n; i++) {
      const j = (i + 1) % n;
      const ex = top[j][0] - top[i][0];
      const ey = top[j][1] - top[i][1];
      // inward-facing wall normal: the pocket ring runs counter-clockwise in camera plan
      const nn = [-ey, ex, 0];
      if (faces(nn) <= 0) continue;
      const shade = Math.min(3, G.toneOf(dirW(nn), P));
      walls.push(`<path class="iso-shade" data-shade="${shade}" d="${path3([top[i], top[j], floor[j], floor[i]], true)}"/>`);
    }
    return {
      clip: path3(top, true),
      svg: `<path class="ft-void" d="${path3(floor, true)}"/>${walls.join("")}`,
      rim: path3(top, true),
      rimPts: top.map(at),
    };
  }

  function hubMarks(state) {
    const ang = M.INDEX_ANGLE + state.theta;
    const r = 2.4;
    return k.dotsSvg([at([SPROCKET.x + r * Math.cos(ang), SPROCKET.y + r * Math.sin(ang), CAM.hubTop])], { size: 0.9, tone: "hi" });
  }

  // The pawl lever tips about its horizontal pin: the tip lifts as far as the button end drops.
  function pawlFrame(lift) {
    const d = [PAWL.tip[0] - PAWL.pivot[0], PAWL.tip[1] - PAWL.pivot[1]];
    const len = Math.hypot(d[0], d[1]);
    const dn = [d[0] / len, d[1] / len];
    const beta = Math.asin(Math.min(1, lift / M.ARM));
    const a = G.unit3(dirW([dn[0] * Math.cos(beta), dn[1] * Math.cos(beta), Math.sin(beta)]));
    const u = G.unit3(dirW([-dn[1], dn[0], 0]));
    const v = G.cross3(a, u);
    const up = v[2] > 0 ? v : G.mul3(v, -1);
    const o = W([PAWL.pivot[0], PAWL.pivot[1], PAWL.z0 + PAWL.thick / 2]);
    return { o, a, u, v: up, beta };
  }

  const LEVER = { s0: -7.2, s1: 6.9, half: 1.5 };
  const NUB = { s0: M.ARM - 0.8, s1: M.ARM + 0.8, half: PAWL.tipWidth / 2, depth: 2.0 };

  // split: where the lever passes under the top plate on its way to the button (negative, toward the button)
  const LEVER_SECTION = [[-LEVER.half * S, -(PAWL.thick / 2) * S], [LEVER.half * S, -(PAWL.thick / 2) * S], [LEVER.half * S, (PAWL.thick / 2) * S], [-LEVER.half * S, (PAWL.thick / 2) * S]];
  function pawl(state, split) {
    const F = pawlFrame(state.lift);
    const lever = G.prismOf(F, LEVER_SECTION, split * S, LEVER.s1 * S, P);
    const leverEnd = G.prismOf(F, LEVER_SECTION, LEVER.s0 * S, split * S, P);
    const down = G.mul3(F.v, -1);
    const nubFrame = { o: G.add3(F.o, G.mul3(F.v, -(PAWL.thick / 2) * S)), a: down, u: F.u, v: F.a };
    const nubPoly = [[-NUB.half * S, NUB.s0 * S], [NUB.half * S, NUB.s0 * S], [NUB.half * S, NUB.s1 * S], [-NUB.half * S, NUB.s1 * S]];
    const nub = G.prismOf(nubFrame, nubPoly, 0, NUB.depth * S, P);
    // the part of the nub above the cam face is never hidden by the cam; below it shows only through the pocket
    const corners = [];
    for (const [x, y] of nubPoly) for (const s of [0, NUB.depth * S]) {
      corners.push(G.add3(nubFrame.o, G.add3(G.mul3(nubFrame.a, s), G.add3(G.mul3(nubFrame.u, x), G.mul3(nubFrame.v, y)))));
    }
    const camTop = CAM.z1 * S;
    const above = [];
    const edges = [[0, 1], [2, 3], [4, 5], [6, 7], [0, 2], [2, 4], [4, 6], [6, 0], [1, 3], [3, 5], [5, 7], [7, 1]];
    for (const p of corners) if (p[2] >= camTop) above.push(p);
    for (const [i, j] of edges) {
      const p = corners[i];
      const q = corners[j];
      if ((p[2] - camTop) * (q[2] - camTop) < 0) above.push(G.lerp3(p, q, (camTop - p[2]) / (q[2] - p[2])));
    }
    const hull = above.length >= 3 ? G.hullOf(above.map((p) => k.iso(p, P))) : [];
    return {
      lever: k.solidSvg(lever, { tone: "hi", lit: true }),
      leverEnd: k.solidSvg(leverEnd, { tone: "hi", lit: true }),
      nub: k.solidSvg(nub, { tone: "hi", lit: true }),
      abovePts: hull,
      low: corners.some((p) => p[2] < camTop - 0.01),
      frame: F,
    };
  }

  const springAt = (s) => {
    const d = [PAWL.end[0] - PAWL.pivot[0], PAWL.end[1] - PAWL.pivot[1]];
    const len = Math.hypot(d[0], d[1]);
    return [PAWL.pivot[0] + (d[0] / len) * s, PAWL.pivot[1] + (d[1] / len) * s];
  };

  // The pawl spring: 0.3 wire, 3.5 OD, between the shelf and the underside of the button end.
  function spring(state, seat, s) {
    const top = PAWL.z0 - s * (state.lift / M.ARM);
    const c = springAt(s);
    return helix(c, 1.6, seat, top, 6);
  }

  function helix(c, r, z0, z1, turns, steps = 20) {
    const back = [];
    const front = [];
    let run = [];
    let near = null;
    const count = Math.round(turns * steps);
    for (let i = 0; i <= count; i++) {
      const t = (i / count) * turns * TAU;
      const p = [c[0] + r * Math.cos(t), c[1] + r * Math.sin(t), z0 + ((z1 - z0) * i) / count];
      const f = faces([Math.cos(t), Math.sin(t), 0]) > 0;
      if (near === null) near = f;
      const flat = at(p);
      if (f !== near) {
        run.push(flat);
        (near ? front : back).push(k.pathOf(run));
        run = [flat];
        near = f;
        continue;
      }
      run.push(flat);
    }
    if (run.length > 1) (near ? front : back).push(k.pathOf(run));
    return { back: back.join(""), front: front.join("") };
  }

  // Knurl and marks on the advance knob, turning with the knob.
  function knob(state, z0) {
    const z1 = z0 + KNOB.h;
    const list = [];
    const count = 48;
    for (let i = 0; i < count; i++) {
      const t = state.knob + (i * TAU) / count;
      const n = [Math.cos(t), Math.sin(t), 0];
      const f = faces(n);
      if (f <= 0.02) continue;
      const alpha = Math.min(1, (f - 0.02) / 0.4);
      list.push([path3([[SPOOL.x + KNOB.r * n[0], SPOOL.y + KNOB.r * n[1], z0 + 1.2], [SPOOL.x + KNOB.r * n[0], SPOOL.y + KNOB.r * n[1], z1 - 1.2]]), alpha]);
    }
    const t = state.knob + M.KNOB_MARK;
    const n = [Math.cos(t), Math.sin(t)];
    const pointer = path3([[SPOOL.x + 3.0 * n[0], SPOOL.y + 3.0 * n[1], z1], [SPOOL.x + (KNOB.r - 1.6) * n[0], SPOOL.y + (KNOB.r - 1.6) * n[1], z1]]);
    const flat = [];
    for (let i = 0; i <= 24; i++) {
      // the shaft end with the flat filed for the epoxy, flush with the knob top
      const a = state.knob + (i / 24) * TAU;
      const ca = Math.cos(a - state.knob);
      const rr = ca > Math.cos(Math.PI / 5) ? (SPOOL.shaftR * Math.cos(Math.PI / 5)) / ca : SPOOL.shaftR;
      flat.push([SPOOL.x + rr * Math.cos(a), SPOOL.y + rr * Math.sin(a), z1]);
    }
    return {
      knurl: k.fadedSvg(list, { tone: "lo" }),
      pointer: k.lineSvg(pointer, { tone: "hi" }),
      shaft: k.lineSvg(path3(flat, true), { tone: "mid" }),
    };
  }

  // Three lightening holes in the spool's top flange, turning with the spool.
  function flangeHoles(state, z) {
    const out = [];
    for (let i = 0; i < 3; i++) {
      const t = state.spool + (i * TAU) / 3 + 0.4;
      const c = [SPOOL.x + 9.6 * Math.cos(t), SPOOL.y + 9.6 * Math.sin(t)];
      const pts = [];
      for (let j = 0; j < 20; j++) {
        const a = (j / 20) * TAU;
        pts.push([c[0] + 1.6 * Math.cos(a), c[1] + 1.6 * Math.sin(a), z]);
      }
      out.push(path3(pts, true));
    }
    return `<path class="ft-void" d="${out.join("")}"/>` + k.lineSvg(out.join(""), { tone: "lo" });
  }

  return { LEVER_SECTION, W, at, path3, prismZ, ringW, faces, toothGroup, toothParts, TOOTH_Z, springAt, pocketRing, perfCentres, filmGeometry, film, roll, teeth, pocket, hubMarks, pawl, pawlFrame, spring, helix, knob, flangeHoles, LEVER, NUB };
}
