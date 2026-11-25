import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import Login from '../pages/login/Login'
import { useAuth } from '../context/AuthContext'

vi.mock('../context/AuthContext', () => ({ useAuth: vi.fn() }))

const mockNavigate = vi.fn()
vi.mock('react-router-dom', async (importOriginal) => ({
  ...(await importOriginal()),
  useNavigate: () => mockNavigate,
}))

const renderLogin = () =>
  render(
    <MemoryRouter>
      <Login />
    </MemoryRouter>
  )

describe('Login', () => {
  beforeEach(() => vi.clearAllMocks())

  it('al enviar llama a login(email, password) y navega a /', async () => {
    const login = vi.fn().mockResolvedValue({})
    useAuth.mockReturnValue({ login })
    const user = userEvent.setup()
    renderLogin()

    await user.type(screen.getByLabelText(/email|correo/i), 'ana@example.com')
    await user.type(screen.getByLabelText(/contraseña/i), 'secreto123')
    await user.click(screen.getByRole('button', { name: /iniciar sesión/i }))

    expect(login).toHaveBeenCalledTimes(1)
    expect(login).toHaveBeenCalledWith('ana@example.com', 'secreto123')
    expect(mockNavigate).toHaveBeenCalledWith('/')
  })

  it('muestra el error si login falla y no navega', async () => {
    const login = vi.fn().mockRejectedValue(new Error('Credenciales inválidas'))
    useAuth.mockReturnValue({ login })
    const user = userEvent.setup()
    renderLogin()

    await user.type(screen.getByLabelText(/email|correo/i), 'ana@example.com')
    await user.type(screen.getByLabelText(/contraseña/i), 'mala')
    await user.click(screen.getByRole('button', { name: /iniciar sesión/i }))

    expect(await screen.findByText('Credenciales inválidas')).toBeInTheDocument()
    expect(mockNavigate).not.toHaveBeenCalled()
  })
})
