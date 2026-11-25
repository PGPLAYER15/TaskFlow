import { renderHook, act } from '@testing-library/react'
import { useCard } from '../hooks/useCard'
import { updateCardCheckStatus } from '../services/CardService'

vi.mock('../services/CardService', () => ({ updateCardCheckStatus: vi.fn() }))

describe('useCard', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.spyOn(console, 'error').mockImplementation(() => {})
  })

  it('toggleCheck llama al servicio y cambia el estado', async () => {
    updateCardCheckStatus.mockResolvedValue()
    const { result } = renderHook(() => useCard(false))

    await act(() => result.current.toggleCheck(1, 2, 3))

    expect(updateCardCheckStatus).toHaveBeenCalledWith(1, 2, 3, true)
    expect(result.current.isChecked).toBe(true)
    expect(result.current.error).toBeNull()
  })

  it('si el servicio falla mantiene el estado y expone el error', async () => {
    updateCardCheckStatus.mockRejectedValue(new Error('boom'))
    const { result } = renderHook(() => useCard(false))

    await act(() => result.current.toggleCheck(1, 2, 3))

    expect(result.current.isChecked).toBe(false)
    expect(result.current.error).toMatch(/error al actualizar|Hubo un error/i)
  })
})
