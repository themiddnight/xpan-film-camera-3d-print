import { useEffect, useState, useSyncExternalStore } from 'react'
import type { KeyPlayer } from '../state/cycle'
import type { CycleCounter } from '../types'
import type { Transport } from './scrollMotion'

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

/** Play, pause, replay and seek on the player itself, for a figure's motion. */
export function playerTransport(player: KeyPlayer): Transport {
  return {
    subscribe: player.subscribe,
    isPlaying: () => player.getStatus().running,
    play: () => player.resume(),
    pause: () => player.pauseRun(),
    replay: () => player.restart(),
    seek: t => player.seek(t),
  }
}

/**
 * Play, pause, replay and a scrub slider for a motion, with the phase it is in. `transport` decides
 * what the buttons move: the player, or the page scroll for a chapter. `counter` adds the live film
 * readout of the frame advance. `hint` shows before the motion has started.
 */
export function PlaybackBar({ player, transport, counter, label, hint }: {
  player: KeyPlayer
  transport: Transport
  counter: CycleCounter | null
  label: string
  hint: string
}) {
  const status = useSyncExternalStore(player.subscribe, player.getStatus)
  const playing = useSyncExternalStore(transport.subscribe, transport.isPlaying)
  const { time, moved } = usePlayhead(player, counter)
  return (
    <div className="playback" role="group" aria-label={label}>
      <div className="playback-controls">
        <button
          type="button" className="playback-button"
          aria-label={playing ? 'Pause' : 'Play'}
          onClick={() => (playing ? transport.pause() : transport.play())}
        >
          {playing ? <PauseIcon /> : <PlayIcon />}
        </button>
        <button type="button" className="playback-button" aria-label="Replay" onClick={transport.replay}>
          <ReplayIcon />
        </button>
        <input
          className="playback-scrub" type="range" aria-label="Scrub"
          min={0} max={player.duration} step={0.01} value={time}
          onChange={e => transport.seek(Number(e.target.value))}
        />
      </div>
      <p className="playback-phase" aria-live="polite">
        {time === 0 && !playing ? hint : sentence(status.phase)}
      </p>
      {counter && <p className="playback-readout">{counterText(counter, moved)}</p>}
    </div>
  )
}
