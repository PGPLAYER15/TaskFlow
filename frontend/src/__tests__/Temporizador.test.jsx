import { render, screen } from '@testing-library/react'
import Temporizador from '../components/Temporizador/Temporizador'

describe('Temporizador', () => {
  it('formatea minutos y segundos con dos dígitos', () => {
    render(<Temporizador minutes={5} seconds={7} isWorking />)
    expect(screen.getByText('05:07')).toBeInTheDocument()
    expect(screen.getByText('Tiempo de trabajo')).toBeInTheDocument()
  })

  it('muestra "Tiempo de descanso" cuando no está trabajando', () => {
    render(<Temporizador minutes={25} seconds={0} isWorking={false} />)
    expect(screen.getByText('25:00')).toBeInTheDocument()
    expect(screen.getByText('Tiempo de descanso')).toBeInTheDocument()
  })
})
