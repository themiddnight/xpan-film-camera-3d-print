// Page script for the film-transport figure. Inlined after the kit, the lathe module, model.mjs and pose.mjs.
const DATA = __DATA__;
const pose = makePose(K, G, M, DATA.P, DATA.S);
const stage = document.querySelector(".ft-stage");
const readout = document.querySelector("[data-readout]");
const status = document.querySelector("[data-status]");
const still = matchMedia("(prefers-reduced-motion: reduce)");
const part = (name) => stage.querySelector(`[data-part="${name}"]`);
const el = Object.fromEntries(
  ["teeth-back", "teeth-front", "teeth-tips", "film", "film-clip", "film-rims", "roll", "pocket-clip", "pocket", "pocket-rim", "hub-dot", "lever", "lever-end", "nub-clip", "nub", "spring", "button-low", "button-high", "flange-holes", "knurl", "knob-top"].map((name) => [name, part(name)]),
);

const orient = (pts) => {
  let area = 0;
  pts.forEach(([x, y], i) => {
    const [x2, y2] = pts[(i + 1) % pts.length];
    area += x * y2 - x2 * y;
  });
  return area < 0 ? [...pts].reverse() : pts;
};
const button = (press, z0, z1) => {
  const at = M.BUTTON.at;
  return K.solidSvg(K.cylinder(-at[1] * DATA.S, -at[0] * DATA.S, M.BUTTON.r * DATA.S, (z0 - press) * DATA.S, (z1 - z0) * DATA.S, DATA.P, 40, 0.5), { tone: "hi", crease: "lo" });
};
const set = (node, html) => {
  if (node.__html !== html) {
    node.innerHTML = html;
    node.__html = html;
  }
};

function draw(state) {
  const teeth = pose.teeth(state);
  set(el["teeth-back"], teeth.back);
  set(el["teeth-front"], teeth.front);
  set(el["teeth-tips"], teeth.tips);
  const film = pose.film(state, DATA.X0);
  set(el.film, film.body);
  el["film-clip"].setAttribute("d", DATA.FILM_CLIP + film.holes);
  set(el["film-rims"], film.rims);
  set(el.roll, pose.roll(state, DATA.X0));
  const pocket = pose.pocket(state);
  el["pocket-clip"].setAttribute("d", pocket.clip);
  set(el.pocket, pocket.svg);
  el["pocket-rim"].setAttribute("d", pocket.rim);
  set(el["hub-dot"], pose.hubMarks(state));
  const pawl = pose.pawl(state, DATA.LEVER_SPLIT);
  set(el.lever, pawl.lever);
  set(el["lever-end"], pawl.leverEnd);
  set(el.nub, pawl.nub);
  el["nub-clip"].setAttribute("d", K.pathOf(orient(pocket.rimPts), true) + (pawl.abovePts.length >= 3 ? K.pathOf(orient(pawl.abovePts), true) : ""));
  const spring = pose.spring(state, DATA.SHELF_Z, DATA.SPRING_S);
  set(el.spring, K.lineSvg(spring.back, { tone: "lo" }) + K.lineSvg(spring.front, { tone: "mid" }));
  // the button rests on the pawl's far end, so it sits as low as that end
  const press = (state.lift * M.ARM_BUTTON) / M.ARM;
  set(el["button-low"], button(press, DATA.BUTTON_LOW[0], DATA.BUTTON_LOW[1] + press));
  set(el["button-high"], button(press, DATA.BUTTON_HIGH[0] + press, DATA.BUTTON_HIGH[1]));
  set(el["flange-holes"], pose.flangeHoles(state, DATA.FLANGE_TOP));
  const knob = pose.knob(state, DATA.KNOB_Z);
  set(el.knurl, knob.knurl);
  set(el["knob-top"], knob.pointer + knob.shaft);
}

const WORDS = { locked: "locked", released: "button pressed, pawl lifted", riding: "pawl riding on the cam", clicked: "click: pawl in the pocket, one frame advanced" };
let cycle = null; // seconds into the running advance cycle
let done = false; // a cycle has finished and its turn is not yet folded into the base
const base = { spool: 0, knob: 0 };
const shown = { lift: 0, rollR: M.rollRadius(M.WOUND0) };
let phase = "locked";
let touring = !still.matches;
let wait = 1.4;
let frame = 0;
let last = 0;
let visible = false;
let resume = 0;

function target() {
  const c = cycle !== null ? M.cycleAt(cycle) : M.cycleAt(done ? M.CYCLE : 0);
  return { c, s: M.stateOf(c) };
}

function start() {
  if (cycle !== null) return;
  if (done) {
    const end = M.stateOf(M.cycleAt(M.CYCLE));
    base.spool += end.spool;
    base.knob += end.knob;
  }
  done = false;
  cycle = 0;
}

function finishNow() {
  start();
  cycle = null;
  done = true;
}

function say(next) {
  if (next === phase) return;
  phase = next;
  status.textContent = WORDS[next];
}

function render(dt, calm) {
  const { c, s } = target();
  // the tip falls into the pocket under its spring in a few milliseconds: that is the click
  if (calm || s.lift >= shown.lift) shown.lift = s.lift;
  else shown.lift += (s.lift - shown.lift) * (1 - Math.exp(-dt / 0.018));
  if (Math.abs(shown.lift - s.lift) < 1e-3) shown.lift = s.lift;
  if (calm || s.rollR >= shown.rollR) shown.rollR = s.rollR;
  else shown.rollR += (s.rollR - shown.rollR) * (1 - Math.exp(-dt / 0.5));
  if (Math.abs(shown.rollR - s.rollR) < 1e-4) shown.rollR = s.rollR;
  draw({ ...s, lift: shown.lift, rollR: shown.rollR, spool: base.spool + s.spool, knob: base.knob + s.knob });
  const text = M.readoutOf(s, cycle !== null ? c.phase : "locked");
  if (readout.textContent !== text) readout.textContent = text;
  say(cycle !== null ? c.phase : "locked");
  return shown.lift !== s.lift || shown.rollR !== s.rollR;
}

function tick(now) {
  const dt = last ? Math.min((now - last) / 1000, 1 / 30) : 1 / 60;
  last = now;
  const calm = still.matches;
  if (cycle !== null) {
    cycle += dt;
    if (cycle >= M.CYCLE) {
      cycle = null;
      done = true;
      wait = 0.6;
    }
  } else if (touring && !calm) {
    wait -= dt;
    if (wait <= 0) start();
  }
  const easing = render(dt, calm);
  const busy = cycle !== null || (touring && !calm) || easing;
  frame = visible && busy ? requestAnimationFrame(tick) : 0;
}

const run = () => {
  if (!frame && visible) {
    last = 0;
    frame = requestAnimationFrame(tick);
  }
};

function act() {
  touring = false;
  clearTimeout(resume);
  resume = setTimeout(() => {
    touring = !still.matches;
    wait = 0.4;
    run();
  }, 3600);
  if (still.matches) {
    if (cycle === null) finishNow();
    render(0, true);
    return;
  }
  start();
  run();
}

new IntersectionObserver((entries) => {
  visible = entries[entries.length - 1].isIntersecting;
  if (visible) run();
}, { rootMargin: "120px 0px" }).observe(stage);

stage.addEventListener("click", act);
stage.addEventListener("keydown", (event) => {
  if (event.key !== " " && event.key !== "Enter") return;
  event.preventDefault();
  act();
});
stage.addEventListener("pointerenter", () => {
  touring = false;
  clearTimeout(resume);
});
stage.addEventListener("pointerleave", () => {
  clearTimeout(resume);
  resume = setTimeout(() => {
    touring = !still.matches;
    wait = 0.4;
    run();
  }, 3600);
});
stage.addEventListener("focus", () => {
  status.textContent = WORDS[phase];
});
render(0, true);
