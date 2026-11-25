import { render, screen } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import ProtectedRoute from '../components/ProtectedRoute'
import { useAuth } from '../context/AuthContext'

vi.mock('../context/AuthContext', () => ({ useAuth: vi.fn() }))

const renderRoute = () =>
  render(
    <MemoryRouter initialEntries={['/private']}>
      <Routes>
        <Route path="/login" element={<div>Pantalla de login</div>} />
        <Route
          path="/private"
          element={
            <ProtectedRoute>
              <div>Contenido privado</div>
            </ProtectedRoute>
          }
        />
      </Routes>
    </MemoryRouter>
  )

describe('ProtectedRoute', () => {
  it('sin token redirige a /login', () => {
    useAuth.mockReturnValue({ isAuthenticated: false, isLoading: false })
    renderRoute()

    expect(screen.getByText('Pantalla de login')).toBeInTheDocument()
    expect(screen.queryByText('Contenido privado')).not.toBeInTheDocument()
  })

  it('con token muestra el contenido', () => {
    useAuth.mockReturnValue({ isAuthenticated: true, isLoading: false })
    renderRoute()

    expect(screen.getByText('Contenido privado')).toBeInTheDocument()
  })

  it('mientras carga no redirige', () => {
    useAuth.mockReturnValue({ isAuthenticated: false, isLoading: true })
    renderRoute()

    expect(screen.getByText('Cargando...')).toBeInTheDocument()
    expect(screen.queryByText('Pantalla de login')).not.toBeInTheDocument()
  })
})
