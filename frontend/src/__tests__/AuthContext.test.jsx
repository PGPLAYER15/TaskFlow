import { renderHook, act, waitFor } from '@testing-library/react'
import { AuthProvider, useAuth } from '../context/AuthContext'

const wrapper = ({ children }) => <AuthProvider>{children}</AuthProvider>
const json = (data, ok = true) => ({ ok, json: async () => data })

describe('AuthContext', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.stubGlobal('fetch', vi.fn())
    vi.spyOn(console, 'error').mockImplementation(() => {})
  })
  afterEach(() => vi.unstubAllGlobals())

  it('sin token guardado: no autenticado y deja de cargar', async () => {
    const { result } = renderHook(() => useAuth(), { wrapper })

    await waitFor(() => expect(result.current.isLoading).toBe(false))
    expect(result.current.isAuthenticated).toBe(false)
    expect(fetch).not.toHaveBeenCalled()
  })

  it('con token válido carga el usuario desde /auth/me', async () => {
    localStorage.setItem('token', 'tok')
    fetch.mockResolvedValue(json({ id: 1, email: 'a@a.com' }))
    const { result } = renderHook(() => useAuth(), { wrapper })

    await waitFor(() => expect(result.current.isLoading).toBe(false))
    expect(result.current.user).toEqual({ id: 1, email: 'a@a.com' })
    expect(result.current.isAuthenticated).toBe(true)
    expect(fetch).toHaveBeenCalledWith('/api/auth/me', { headers: { Authorization: 'Bearer tok' } })
  })

  it('con token inválido lo elimina', async () => {
    localStorage.setItem('token', 'malo')
    fetch.mockResolvedValue(json({}, false))
    const { result } = renderHook(() => useAuth(), { wrapper })

    await waitFor(() => expect(result.current.isLoading).toBe(false))
    expect(localStorage.getItem('token')).toBeNull()
    expect(result.current.isAuthenticated).toBe(false)
  })

  it('login guarda el token, carga el usuario y envía el formulario OAuth2', async () => {
    fetch
      .mockResolvedValueOnce(json({ access_token: 'nuevo' }))
      .mockResolvedValueOnce(json({ id: 1, email: 'a@a.com' }))
    const { result } = renderHook(() => useAuth(), { wrapper })
    await waitFor(() => expect(result.current.isLoading).toBe(false))

    let user
    await act(async () => { user = await result.current.login('a@a.com', 'pw') })

    expect(user).toEqual({ id: 1, email: 'a@a.com' })
    expect(localStorage.getItem('token')).toBe('nuevo')
    expect(result.current.isAuthenticated).toBe(true)
    const [url, options] = fetch.mock.calls[0]
    expect(url).toBe('/api/auth/login')
    expect(options.body.get('username')).toBe('a@a.com')
    expect(options.body.get('password')).toBe('pw')
  })

  it('login fallido lanza el detalle del servidor y no guarda token', async () => {
    fetch.mockResolvedValueOnce(json({ detail: 'Credenciales inválidas' }, false))
    const { result } = renderHook(() => useAuth(), { wrapper })
    await waitFor(() => expect(result.current.isLoading).toBe(false))

    await expect(act(() => result.current.login('a@a.com', 'mal'))).rejects.toThrow('Credenciales inválidas')
    expect(localStorage.getItem('token')).toBeNull()
  })

  it('register envía JSON y devuelve el usuario creado', async () => {
    fetch.mockResolvedValueOnce(json({ id: 3 }))
    const { result } = renderHook(() => useAuth(), { wrapper })
    await waitFor(() => expect(result.current.isLoading).toBe(false))

    let created
    await act(async () => { created = await result.current.register('a@a.com', 'ana', 'secreto') })

    expect(created).toEqual({ id: 3 })
    expect(JSON.parse(fetch.mock.calls[0][1].body)).toEqual({ email: 'a@a.com', username: 'ana', password: 'secreto' })
  })

  it('logout elimina token y usuario', async () => {
    localStorage.setItem('token', 'tok')
    fetch.mockResolvedValue(json({ id: 1 }))
    const { result } = renderHook(() => useAuth(), { wrapper })
    await waitFor(() => expect(result.current.isAuthenticated).toBe(true))

    act(() => result.current.logout())

    expect(localStorage.getItem('token')).toBeNull()
    expect(result.current.user).toBeNull()
    expect(result.current.isAuthenticated).toBe(false)
  })

  it('useAuth fuera del provider lanza error', () => {
    expect(() => renderHook(() => useAuth())).toThrow(/AuthProvider/)
  })
})
