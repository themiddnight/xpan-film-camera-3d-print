## Design decisions

Why the camera is built this way, for anyone extending it. Each choice trades cleverness for a part you can print, fit and tune by hand.

### Film transport

- **One sprocket, one tooth per perforation.** A full turn moves exactly one frame, with no gear train and no counter. The tooth count sets the advance, so a small error in the hub never adds up from frame to frame.
- **A one-notch cam.** It locks the sprocket after one turn, and is printed in one piece with the sprocket so the notch stays in step with the teeth.
- **A pawl on a sideways pivot.** A button pressed straight down can only lift a lever that pivots on a horizontal axis.
- **A felt-washer clutch on the take-up spool.** Without it, thumb torque goes into the perforations once the sprocket locks.
- **Rewind through the release button.** A quarter turn holds it down, so nobody has to hold it through twenty turns of the knob.
- **A foam pressure pad over the gate only.** The pad's drag must stay below the force at which the clutch slips.
- **Rails on the film edge band.** They keep clear of the perforations and the image.

### Film back

- **One printed shell.** The film rail and the chambers share one datum, so they cannot drift apart.
- **One rear cover on a bottom hinge.** It opens the whole film path and both chambers at once.
- **A dark slide cut from aluminium sheet.** It is flatter and tougher than a printed one. Its slot has flocked lips and a plug, because an open slot mouth leads straight to the gate.

### Body and modules

- **A modular camera.** The film back owns the film plane, so one back can serve several bodies.
- **Top hook, bottom latch.** Printable, secure and repeatable. The datum face positions the body and the latch only clamps it.
- **M42 for lens modules.** Bought caps give real threads, which printed ones do not.
- **A captured tripod nut.** Pinhole exposures are long, so the body needs a tripod. Nuts are easy to buy and inserts are not.

### Materials

- **Black PETG for every printed part,** sized to fit a small print bed because the printer is not chosen yet.
- **One size of stainless rod for every shaft and pin.** Dowel pins are too short for the long shafts.
