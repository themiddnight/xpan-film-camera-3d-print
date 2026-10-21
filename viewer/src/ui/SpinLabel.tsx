import { useEffect, useState, type MutableRefObject } from 'react'

const REFRESH_MS = 100

/** Film advanced so far; polls the spin angle itself so only this label re-renders while spinning. */
export function SpinLabel({ spinning, spinAngle, filmAdvanceMm }: {
  spinning: boolean
  spinAngle: MutableRefObject<number>
  filmAdvanceMm: number
}) {
  const [turns, setTurns] = useState(0)

  useEffect(() => {
    if (!spinning) return
    const id = setInterval(() => setTurns(spinAngle.current / (2 * Math.PI)), REFRESH_MS)
    return () => clearInterval(id)
  }, [spinning, spinAngle])

  return (
    <div className="sub">
      {turns === 0
        ? `One full turn advances ${filmAdvanceMm}mm of film.`
        : `${turns.toFixed(2)} turns = ${(turns * filmAdvanceMm).toFixed(1)}mm of film`}
    </div>
  )
}
