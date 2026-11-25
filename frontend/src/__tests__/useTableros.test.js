import { renderHook, act, waitFor } from '@testing-library/react'
import { useTableros } from '../hooks/useTableros'
import { fetchTableros } from '../services/TableroService'

vi.mock('../services/TableroService', () => ({ fetchTableros: vi.fn() }))

describe('useTableros', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.spyOn(console, 'log').mockImplementation(() => {})
    vi.spyOn(console, 'error').mockImplementation(() => {})
  })

  it('carga los tableros al montar', async () => {
    fetchTableros.mockResolvedValue([{ id: 1, title: 'A' }])
    const { result } = renderHook(() => useTableros())

    expect(result.current.loading).toBe(true)
    await waitFor(() => expect(result.current.loading).toBe(false))
    expect(result.current.tableros).toEqual([{ id: 1, title: 'A' }])
    expect(result.current.error).toBeNull()
  })

  it('expone un error si la carga falla', async () => {
    fetchTableros.mockRejectedValue(new Error('fail'))
    const { result } = renderHook(() => useTableros())

    await waitFor(() => expect(result.current.loading).toBe(false))
    expect(result.current.error).toBeTruthy()
    expect(result.current.tableros).toEqual([])
  })

  it('addTablero agrega un tablero a la lista', async () => {
    fetchTableros.mockResolvedValue([])
    const { result } = renderHook(() => useTableros())
    await waitFor(() => expect(result.current.loading).toBe(false))

    act(() => result.current.addTablero({ id: 2, title: 'B' }))

    expect(result.current.tableros).toEqual([{ id: 2, title: 'B' }])
  })
})
