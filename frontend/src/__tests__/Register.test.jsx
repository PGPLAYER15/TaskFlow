import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import Register from '../pages/register/Register'
import { useAuth } from '../context/AuthContext'

vi.mock('../context/AuthContext', () => ({ useAuth: vi.fn() }))
const mockNavigate = vi.fn()
vi.mock('react-router-dom', async (importOriginal) => ({
  ...(await importOriginal()),
  useNavigate: () => mockNavigate,
}))

const fill = async (user, { password = 'secreto123', confirm = 'secreto123' } = {}) => {
  await user.type(screen.getByLabelText('Nombre de usuario'), 'ana')
  await user.type(screen.getByLabelText(/correo/i), 'ana@example.com')
  await user.type(screen.getByLabelText('Contraseña'), password)
  await user.type(screen.getByLabelText(/confirmar contraseña/i), confirm)
  await user.click(screen.getByRole('button', { name: /registr|crear/i }))
}

describe('Register', () => {
  let register
  beforeEach(() => {
    vi.clearAllMocks()
    register = vi.fn().mockResolvedValue({})
    useAuth.mockReturnValue({ register })
    render(<MemoryRouter><Register /></MemoryRouter>)
  })

  it('registra con (email, username, password) y navega a /login', async () => {
    await fill(userEvent.setup())

    expect(register).toHaveBeenCalledWith('ana@example.com', 'ana', 'secreto123')
    expect(mockNavigate).toHaveBeenCalledWith('/login')
  })

  it('rechaza contraseñas que no coinciden', async () => {
    await fill(userEvent.setup(), { confirm: 'otra-cosa' })

    expect(await screen.findByText('Las contraseñas no coinciden')).toBeInTheDocument()
    expect(register).not.toHaveBeenCalled()
  })

  it('rechaza contraseñas de menos de 6 caracteres', async () => {
    await fill(userEvent.setup(), { password: '123', confirm: '123' })

    expect(await screen.findByText(/al menos 6 caracteres/)).toBeInTheDocument()
    expect(register).not.toHaveBeenCalled()
  })

  it('muestra el error del servidor y no navega', async () => {
    register.mockRejectedValue(new Error('Email ya registrado'))
    await fill(userEvent.setup())

    expect(await screen.findByText('Email ya registrado')).toBeInTheDocument()
    expect(mockNavigate).not.toHaveBeenCalled()
  })
})
