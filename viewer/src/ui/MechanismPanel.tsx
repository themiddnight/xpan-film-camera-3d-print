import { useLayoutEffect, useRef, useSyncExternalStore } from 'react'
import { useViewer } from '../state/viewer'
import type { Mechanism } from '../types'

const SLIDER_STEP = 0.001

/**
 * One slider and play button per mechanism. The slider and readout are uncontrolled and painted
 * straight from the motion value, so a playing mechanism re-renders nothing in React.
 */
function MechanismRow({ mechanism }: { mechanism: Mechanism }) {
  const { motion } = useViewer()
  const { id, label, readout } = mechanism
  const playing = useSyncExternalStore(motion.subscribePlaying, () => motion.isPlaying(id))
  const slider = useRef<HTMLInputElement>(null)
  const output = useRef<HTMLOutputElement>(null)

  useLayoutEffect(() => {
    const paint = (value: number) => {
      // A cyclic mechanism shows its place within the current turn; whole turns are the frame count.
      const shown = motion.isCyclic(id) ? value - Math.floor(value) : value
      if (slider.current) slider.current.value = String(shown)
      if (output.current && readout) output.current.textContent = `${(shown * readout.per_unit).toFixed(1)} ${readout.unit}`
    }
    paint(motion.get(id))
    return motion.subscribeValue(id, paint)
  }, [motion, id, readout])

  return (
    <div className="mech">
      <div className="mech-head">
        <span>{label}</span>
        <button className={playing ? 'on' : ''} aria-pressed={playing} onClick={() => motion.setPlaying(id, !playing)}>
          {playing ? 'Pause' : 'Play'}
        </button>
      </div>
      <input
        ref={slider} type="range" min={0} max={1} step={SLIDER_STEP} defaultValue={0} aria-label={label}
        onChange={e => {
          const v = e.currentTarget.valueAsNumber
          motion.setByUser(id, motion.isCyclic(id) ? Math.floor(motion.get(id)) + v : v)
        }}
      />
      {readout && <output ref={output} className="sub" />}
    </div>
  )
}

export function MechanismPanel() {
  const mechanisms = useViewer().motion.mechanisms.filter(m => !m.internal)
  if (mechanisms.length === 0) return null
  return (
    <section>
      <h2>Mechanisms</h2>
      {mechanisms.map(m => <MechanismRow key={m.id} mechanism={m} />)}
    </section>
  )
}
