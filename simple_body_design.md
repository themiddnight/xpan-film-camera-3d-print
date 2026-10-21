# Simple Body Design

**Module:** First active body module  
**Use case:** Pinhole camera body for the shared film back  
**Status:** Concept/spec extracted from the system design; detailed modeling not started

---

## 1. Purpose

The simple body is the first body module for the camera. It provides a light-tight 50mm-depth chamber between the M42 front mount and the film plane in the shared film back.

It intentionally avoids a mirror, ground glass, and coupled shutter system.

---

## 2. Core Parameters

| Parameter | Value | Notes |
|---|---:|---|
| Pinhole-to-film distance | 50.0mm | Critical optical distance |
| Pinhole diameter | 0.30mm | In pinhole module |
| Front mount | M42 x 1mm female | Receives pinhole/lens module |
| Film format | 65 x 24mm | Film back owns gate |
| Body-to-back lock | Top hook + bottom latch | Matches film back interface |
| Viewfinder | Foldable wire frame | Simple framing |
| Material | Black PETG | FDM |

---

## 3. Optical Layout

```
[M42 pinhole module] -> [50mm dark chamber] -> [film back gate / film plane]
```

The 50.0mm distance is measured from the pinhole plane to the film plane. The film plane belongs to the film back, so the body depth must be set from the body mating datum to the M42/pinhole module datum after the film back interface is finalized.

---

## 4. Body-to-Film-Back Interface

The simple body uses the shared film back interface:

- Top lip hooks into the film back top rail.
- Bottom latch hook catches the film back lower 3mm pin.
- Body pivots down and clamps against the film rail/body datum.
- Body does not contact cartridge or take-up chambers.

Detailed interface geometry is defined in [film_back_design.md](film_back_design.md).

---

## 5. Viewfinder

Initial viewfinder: foldable wire frame.

| Parameter | Value | Notes |
|---|---:|---|
| Rear-to-front frame distance | 80mm | Starting value |
| Front frame width | about 104mm | For 65mm width at 50mm distance |
| Front frame height | about 38mm | For 24mm height at 50mm distance |
| Rear frame opening | about 20 x 8mm | Eye reference |
| Wire diameter | 1.0-1.2mm | Steel wire |

---

## 6. Deferred Details

These will be finalized after the film back interface is modeled:

- Exact body depth from M42 seat to film plane.
- M42 mount reinforcement and thread strategy.
- Wire frame hinge detail.
- Body latch hook detail.
- Internal anti-reflection ribs/baffles.

