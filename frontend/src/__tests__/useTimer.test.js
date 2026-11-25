import { renderHook, act } from '@testing-library/react'
import useTimer from '../hooks/useTimer'

describe('useTimer', () => {
  beforeEach(() => vi.useFakeTimers())
  afterEach(() => vi.useRealTimers())

  it('empieza en 25:00, en modo trabajo y sin correr', () => {
    const { result } = renderHook(() => useTimer())
    expect(result.current).toMatchObject({ minutes: 25, seconds: 0, isWorking: true, isActive: false })
  })

  it('iniciar descuenta segundos y pausar detiene el reloj', () => {
    const { result } = renderHook(() => useTimer())

    act(() => result.current.iniciar())
    act(() => vi.advanceTimersByTime(1000))
    expect(result.current).toMatchObject({ minutes: 24, seconds: 59, isActive: true })

    act(() => result.current.pausar())
    act(() => vi.advanceTimersByTime(5000))
    expect(result.current).toMatchObject({ minutes: 24, seconds: 59, isActive: false })
  })

  it('reiniciar vuelve a 25:00 y detiene el reloj', () => {
    const { result } = renderHook(() => useTimer())

    act(() => result.current.iniciar())
    act(() => vi.advanceTimersByTime(3000))
    act(() => result.current.reiniciar())

    expect(result.current).toMatchObject({ minutes: 25, seconds: 0, isWorking: true, isActive: false })
  })
})
