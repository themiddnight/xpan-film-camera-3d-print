import { useEffect, useLayoutEffect, useRef, useSyncExternalStore } from 'react'
import type { CyclePlayer } from '../state/cycle'
import { useViewer, useViewerState } from '../state/viewer'

/** Space runs the first cycle, as on the anatomy figure, unless a form control has the keyboard. */
function useSpaceKey(player: CyclePlayer, enabled: boolean) {
  useEffect(() => {
    if (!enabled) return
    const onKey = (e: KeyboardEvent) => {
      if (e.code !== 'Space' || e.repeat) return
      const target = e.target as HTMLElement | null
      if (target?.closest('input, select, textarea, button')) return
      e.preventDefault()
      player.run()
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [player, enabled])
}

function CycleRow({ player, keyboard }: { player: CyclePlayer; keyboard: boolean }) {
  const { motion, actions } = useViewer()
  const status = useSyncExternalStore(player.subscribe, player.getStatus)
  const focus = useViewerState(s => s.focus?.cycle === player.cycle.id)
  const readout = useRef<HTMLOutputElement>(null)
  const { counter, label } = player.cycle
  useSpaceKey(player, keyboard)

  // Painted straight from the motion value, so the count runs every frame without a React render.
  useLayoutEffect(() => {
    const paint = (value: number) => {
      if (!readout.current) return
      // A finished advance reads as the full frame it just moved, not as zero of the next one.
      const frame = Math.max(1, Math.ceil(value - 1e-6))
      const within = value - (frame - 1)
      const count = Math.floor(within * counter.count_per_unit + 1e-6)
      readout.current.textContent =
        `frame ${frame} · ${counter.count_label} ${count} / ${counter.count_per_unit} · ${(within * counter.per_unit).toFixed(1)} ${counter.unit}`
    }
    paint(motion.get(counter.mechanism))
    return motion.subscribeValue(counter.mechanism, paint)
  }, [motion, counter])

  const toggleFocus = () => actions.setFocus(player, !focus)

  return (
    <div className="cycle">
      <div className="btns">
        <button className="primary" onClick={() => player.run()} disabled={status.running}>{label}</button>
        <button className={status.looping ? 'on' : ''} aria-pressed={status.looping} onClick={() => player.setLooping(!status.looping)}>
          Loop
        </button>
        <button className={focus ? 'on' : ''} aria-pressed={focus} onClick={toggleFocus} title="Ghost the parts that hide the mechanism">
          Show mechanism
        </button>
      </div>
      <output ref={readout} className="readout" />
      <div className="sub">Phase: <strong>{status.phase}</strong>{keyboard ? ' · Space runs one cycle' : ''}</div>
    </div>
  )
}

export function CyclePanel() {
  const { cycles } = useViewer()
  if (cycles.length === 0) return null
  return (
    <section>
      <h2>Operate</h2>
      {cycles.map((c, i) => <CycleRow key={c.cycle.id} player={c} keyboard={i === 0} />)}
    </section>
  )
}
