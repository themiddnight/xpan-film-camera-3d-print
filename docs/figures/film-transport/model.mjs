// Truth model of the right-hand film transport: sprocket, one-pocket cam, pawl and take-up.
// Camera coordinates in mm: X along film travel, +Y toward the front (pinhole), Z up.
// Source: docs/design/film-back.md sections 7, 8, 9, 14, 17.4, 17.6 and 17.7.
// Pure: no DOM, no kit. The build and the page both read it.

export const FILM = {
  width: 35.0,
  thickness: 0.13,
  pitch: 4.75,
  perfAlong: 1.981,
  perfAcross: 2.794,
  perfCorner: 0.5,
  perfRow: 14.09,
};

export const TEETH = 14;
export const FRAME = TEETH * FILM.pitch; // 66.5 mm, one sprocket turn

export const SPROCKET = {
  x: 55.0,
  y: 10.52,
  pitchR: 21.17 / 2,
  hubR: 21.04 / 2,
  reliefR: 19.0 / 2,
  reliefZ: 12.4,
  flangeR: 23 / 2,
  flangeT: 1.0,
  flangeGap: 35.4,
  tooth: { along: 1.4, tip: 1.0, across: 2.0, height: 0.7 },
  pinR: 1.5,
};

export const CAM = {
  r: 17 / 2,
  z0: 20,
  z1: 23,
  hubR: 8 / 2,
  hubTop: 32.0,
  pocket: { width: 2.2, radial: 2.4, depth: 1.8, r: 6.0 },
};

export const PAWL = {
  tip: [59.2, 14.8],
  pivot: [63.5, 19.0],
  end: [67.7, 23.2],
  thick: 2.0,
  z0: 23.2,
  tipWidth: 1.8,
};

export const BUTTON = { r: 3.0, at: PAWL.end, travel: 2.5 };

export const SPOOL = {
  x: 81.0,
  y: 12.0,
  coreR: 16 / 2,
  flangeR: 26 / 2,
  flangeT: 1.2,
  flangeGap: 35.6,
  shaftR: 1.5,
};

export const KNOB = { r: 26 / 2, h: 10 };

// Wound length at the start of this cycle: about 150 mm of leader plus six frames.
export const WOUND0 = 150 + 6 * FRAME;

const TAU = Math.PI * 2;
const wrap = (a) => a - TAU * Math.round(a / TAU);

// Pawl arms: pivot in the middle, so the tip lifts as far as the button end drops.
export const ARM = Math.hypot(PAWL.tip[0] - PAWL.pivot[0], PAWL.tip[1] - PAWL.pivot[1]);
export const ARM_BUTTON = Math.hypot(PAWL.end[0] - PAWL.pivot[0], PAWL.end[1] - PAWL.pivot[1]);

// The pocket sits under the pawl tip when the sprocket angle is a whole number of turns.
export const POCKET_ANGLE = Math.atan2(PAWL.tip[1] - SPROCKET.y, PAWL.tip[0] - SPROCKET.x);
// The pocket is aligned with a tooth gap, so the teeth sit half a pitch either side of it.
export const TOOTH_PHASE = POCKET_ANGLE + Math.PI / TEETH;
// The tip (1.8 wide) can drop only when it lies wholly over the pocket (2.2 wide).
export const DROP_SLACK = (CAM.pocket.width - PAWL.tipWidth) / 2;
// The painted dot on the top hub points at the fixed index mark on the top plate when the pocket is under the tip.
export const INDEX_ANGLE = (100 / 180) * Math.PI;
// Where the pointer on the advance knob starts (any angle: the knob has no index).
export const KNOB_MARK = -1.2;

export function rollRadius(wound) {
  return Math.sqrt(SPOOL.coreR ** 2 + (wound * FILM.thickness) / Math.PI);
}

// Spool turn for a wound length, from dL = R dθ with R² = Rc² + L·t/π.
export function spoolTurn(wound) {
  return (TAU / FILM.thickness) * (rollRadius(wound) - SPOOL.coreR);
}

// The S path: past the rear of the sprocket, round its +X side, across to the -X/front of the roll.
export function filmPath(rollR) {
  const ra = SPROCKET.pitchR;
  const rb = rollR + FILM.thickness / 2;
  const dx = SPOOL.x - SPROCKET.x;
  const dy = SPOOL.y - SPROCKET.y;
  const span = Math.hypot(dx, dy);
  const leave = Math.atan2(dy, dx) - Math.acos((ra + rb) / span);
  const arrive = leave + Math.PI;
  const from = [SPROCKET.x + ra * Math.cos(leave), SPROCKET.y + ra * Math.sin(leave)];
  const to = [SPOOL.x + rb * Math.cos(arrive), SPOOL.y + rb * Math.sin(arrive)];
  return {
    leave,
    arrive,
    wrap: leave + Math.PI / 2,
    from,
    to,
    free: Math.hypot(to[0] - from[0], to[1] - from[1]),
    rb,
  };
}

// Where the pawl tip has to be: in the pocket, or up on the cam face.
export function tipFloor(theta) {
  const offset = Math.abs(wrap(theta)) * CAM.pocket.r;
  return offset <= DROP_SLACK + 1e-9 ? 0 : CAM.pocket.depth;
}

export function stateOf({ theta, button, slip = 0 }) {
  const film = (theta / TAU) * FRAME;
  const wound = WOUND0 + film;
  const floor = tipFloor(theta);
  const lift = Math.max(button * (ARM / ARM_BUTTON), floor);
  return {
    theta,
    film,
    perfs: Math.min(TEETH, Math.round(film / FILM.pitch)),
    wound,
    rollR: rollRadius(wound),
    spool: -(spoolTurn(wound) - spoolTurn(WOUND0)),
    knob: -(spoolTurn(wound) - spoolTurn(WOUND0)) - slip,
    button,
    floor,
    lift,
  };
}

// One advance cycle, as a thumb does it (film-back.md 8.2 and 14):
// press the button, turn the knob, let go once the pocket has left the tip,
// keep turning while the tip rides the cam face, stop at the click.
const PRESS = [0.0, 0.55];
const TURN = [0.75, 4.75];
const RELEASE_AT = (40 / 360) * TAU;
const RELEASE_FOR = 0.45;
const SLIP_DEG = 9;
export const CLICK_HOLD = 1.2;
export const CYCLE = 6.6;

const smooth = (a, b, x) => {
  const t = Math.min(1, Math.max(0, (x - a) / (b - a)));
  return t * t * (3 - 2 * t);
};
const easeInOut = (t) => (t < 0.5 ? 4 * t * t * t : 1 - (-2 * t + 2) ** 3 / 2);
const thetaAt = (t) => TAU * easeInOut(Math.min(1, Math.max(0, (t - TURN[0]) / (TURN[1] - TURN[0]))));

function firstTime(test) {
  let lo = TURN[0];
  let hi = TURN[1];
  for (let i = 0; i < 60; i++) {
    const mid = (lo + hi) / 2;
    if (test(thetaAt(mid))) hi = mid;
    else lo = mid;
  }
  return hi;
}

export const T_RELEASE = firstTime((theta) => theta >= RELEASE_AT);
export const T_CLICK = firstTime((theta) => theta > Math.PI && tipFloor(theta) === 0);

export function cycleAt(t) {
  const theta = thetaAt(t);
  const pressed = smooth(PRESS[0], PRESS[1], t) * (1 - smooth(T_RELEASE, T_RELEASE + RELEASE_FOR, t));
  const button = BUTTON.travel * pressed;
  const slip = (SLIP_DEG / 360) * TAU * smooth(T_CLICK, T_CLICK + 0.5, t);
  let phase = "locked";
  if (t >= T_CLICK + CLICK_HOLD) phase = "locked";
  else if (t >= T_CLICK) phase = "clicked";
  else if (button > 0.02) phase = "released";
  else if (t > PRESS[1]) phase = "riding";
  return { theta, button, slip, phase };
}

export function readoutOf(state, phase) {
  return `perf ${state.perfs} / ${TEETH} · ${state.film.toFixed(1)} mm · ${phase}`;
}
