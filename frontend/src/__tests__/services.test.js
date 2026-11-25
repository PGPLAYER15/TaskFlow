const { create } = vi.hoisted(() => ({
  create: vi.fn(() => ({
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    interceptors: { request: { use: vi.fn() } },
  })),
}))
vi.mock('axios', () => ({ default: { create } }))

import { updateCardCheckStatus } from '../services/CardService'
import { crearTablero as crearTableroBoard } from '../services/BoardService'
import {
  crearTablero,
  fetchTableros,
  fetchTablerobyID,
  fetchColumnas,
} from '../services/TableroService'

// Orden de importación = orden de creación de las instancias de axios
const [cardApi, boardApi, tableroApi] = create.mock.results.map((r) => r.value)
// Se capturan ahora: Vitest puede limpiar los mocks entre tests
const interceptors = [cardApi, boardApi, tableroApi].map((api) => api.interceptors.request.use.mock.calls[0][0])

describe('servicios HTTP', () => {
  beforeEach(() => vi.spyOn(console, 'error').mockImplementation(() => {}))

  it.each([
    ['CardService', 0],
    ['BoardService', 1],
    ['TableroService', 2],
  ])('%s adjunta el token Bearer a cada petición', (_name, index) => {
    const interceptor = interceptors[index]

    localStorage.setItem('token', 'abc')
    expect(interceptor({ headers: {} }).headers.Authorization).toBe('Bearer abc')

    localStorage.removeItem('token')
    expect(interceptor({ headers: {} }).headers.Authorization).toBeUndefined()
  })

  it('updateCardCheckStatus hace PUT con el check', async () => {
    cardApi.put.mockResolvedValue({})
    await updateCardCheckStatus(1, 2, 3, true)
    expect(cardApi.put).toHaveBeenCalledWith('/boards/1/lists/2/cards/3/', { check: true })
  })

  it('updateCardCheckStatus propaga el error', async () => {
    cardApi.put.mockRejectedValue(new Error('x'))
    await expect(updateCardCheckStatus(1, 2, 3, true)).rejects.toThrow('x')
  })

  it('crearTablero (Board y Tablero) hace POST /boards/ y devuelve data', async () => {
    const body = { title: 'T', description: 'D', color: '#fff' }
    boardApi.post.mockResolvedValue({ data: { id: 1 } })
    tableroApi.post.mockResolvedValue({ data: { id: 2 } })

    expect(await crearTableroBoard('T', 'D', '#fff')).toEqual({ id: 1 })
    expect(await crearTablero('T', 'D', '#fff')).toEqual({ id: 2 })
    expect(boardApi.post).toHaveBeenCalledWith('/boards/', body)
    expect(tableroApi.post).toHaveBeenCalledWith('/boards/', body)
  })

  it('fetchTableros, fetchTablerobyID y fetchColumnas usan las rutas correctas', async () => {
    tableroApi.get.mockResolvedValue({ data: 'ok' })

    expect(await fetchTableros()).toBe('ok')
    expect(await fetchTablerobyID(7)).toBe('ok')
    expect(await fetchColumnas(7)).toBe('ok')
    expect(tableroApi.get.mock.calls.map((c) => c[0])).toEqual(['/boards/', '/boards/7', '/boards/7/lists/'])
  })

  it('fetchTableros propaga el error', async () => {
    tableroApi.get.mockRejectedValueOnce(new Error('net'))
    await expect(fetchTableros()).rejects.toThrow('net')
  })
})
