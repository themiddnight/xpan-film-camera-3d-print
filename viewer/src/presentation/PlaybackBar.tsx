import { useEffect, useState, useSyncExternalStore } from 'react'
import type { KeyPlayer } from '../state/cycle'
import type { CycleCounter } from '../types'

/** What the readout says while the frame advance runs: film moved and perforations counted. */
function counterText(counter: CycleCounter, moved: number): string {
  const perfs = Math.min(counter.count_per_unit, Math.floor(moved * counter.count_per_unit + 1e-6))
  return `${(moved * counter.per_unit).toFixed(1)} ${counter.unit} of film, ${perfs} of ${counter.count_per_unit} perforations`
}

function sentence(phase: string): string {
  return phase.charAt(0).toUpperCase() + phase.slice(1)
}

/** Follows the player's time and readout every animation frame while it is mounted. */
function usePlayhead(player: KeyPlayer, counter: CycleCounter | null) {
  const [now, setNow] = useState({ time: player.time, moved: counter ? player.progress(counter.mechanism) : 0 })
  useEffect(() => {
    let frame = 0
    const read = () => {
      const time = player.time
      const moved = counter ? player.progress(counter.mechanism) : 0
      setNow(prev => (prev.time === time && prev.moved === moved ? prev : { time, moved }))
      frame = requestAnimationFrame(read)
    }
    read()
    return () => cancelAnimationFrame(frame)
  }, [player, counter])
  return now
}

const PlayIcon = () => <svg viewBox="0 0 16 16" aria-hidden="true"><path d="M4 2.5v11l9-5.5z" /></svg>
const PauseIcon = () => <svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3.5 2.5h3v11h-3zM9.5 2.5h3v11h-3z" /></svg>
const ReplayIcon = () => (
  <svg viewBox="0 0 16 16" aria-hidden="true">
    <path d="M8 2.5a5.5 5.5 0 1 1-5.2 3.7" fill="none" stroke="currentColor" strokeWidth="1.6" />
    <path d="M1.6 2.2l1.4 4.5 4.3-1.9z" />
  </svg>
)

/**
 * Play, pause, replay and a scrub slider for the active chapter's motion, with the phase it is in.
 * `counter` adds the live film readout of the frame advance.
 */
export function PlaybackBar({ player, counter, label }: { player: KeyPlayer; counter: CycleCounter | null; label: string }) {
  const status = useSyncExternalStore(player.subscribe, player.getStatus)
  const { time, moved } = usePlayhead(player, counter)
  return (
    <div className="playback" role="group" aria-label={label}>
      <div className="playback-controls">
        <button
          type="button" className="playback-button"
          aria-label={status.running ? 'Pause' : 'Play'}
          onClick={() => (status.running ? player.pauseRun() : player.resume())}
        >
          {status.running ? <PauseIcon /> : <PlayIcon />}
        </button>
        <button type="button" className="playback-button" aria-label="Replay" onClick={() => player.restart()}>
          <ReplayIcon />
        </button>
        <input
          className="playback-scrub" type="range" aria-label="Scrub"
          min={0} max={player.duration} step={0.01} value={time}
          onChange={e => player.seek(Number(e.target.value))}
        />
      </div>
      <p className="playback-phase" aria-live="polite">
        {time === 0 && !status.running ? 'Press play to watch it move' : sentence(status.phase)}
      </p>
      {counter && <p className="playback-readout">{counterText(counter, moved)}</p>}
    </div>
  )
}
