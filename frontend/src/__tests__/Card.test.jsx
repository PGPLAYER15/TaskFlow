import { render, screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { DndContext } from '@dnd-kit/core'
import Card from '../components/Card/Card'

vi.mock('../services/CardService', () => ({
  updateCardCheckStatus: vi.fn().mockResolvedValue({}),
}))

const renderCard = (props = {}) => {
  const onDelete = vi.fn().mockResolvedValue()
  const onEdit = vi.fn().mockResolvedValue()
  render(
    <DndContext>
      <Card
        board_id={1}
        id={10}
        columnaId={5}
        title="Mi tarjeta"
        check={false}
        onDelete={onDelete}
        onEdit={onEdit}
        {...props}
      />
    </DndContext>
  )
  return { onDelete, onEdit }
}

describe('Card', () => {
  it('renderiza el título', () => {
    renderCard()
    expect(screen.getByText('Mi tarjeta')).toBeInTheDocument()
  })

  it('el botón de borrar aparece al hacer hover sobre la tarjeta', async () => {
    renderCard()
    const user = userEvent.setup()
    const deleteBtn = () => screen.queryByRole('button', { name: /borrar tarjeta/i })

    expect(deleteBtn()).not.toBeInTheDocument()

    await user.hover(screen.getByText('Mi tarjeta'))

    expect(deleteBtn()).toBeVisible()
  })

  it('el botón de borrar desaparece al quitar el hover', async () => {
    renderCard()
    const user = userEvent.setup()

    await user.hover(screen.getByText('Mi tarjeta'))
    await user.unhover(screen.getByText('Mi tarjeta'))

    expect(screen.queryByRole('button', { name: /borrar tarjeta/i })).not.toBeInTheDocument()
  })

  it('borrar pide confirmación y luego llama a onDelete(columnaId, id)', async () => {
    const { onDelete } = renderCard()
    const user = userEvent.setup()

    await user.hover(screen.getByText('Mi tarjeta'))
    // fireEvent: user.click mueve el puntero y en jsdom dispara mouseleave
    fireEvent.click(screen.getByRole('button', { name: /borrar tarjeta/i }))
    expect(onDelete).not.toHaveBeenCalled()
    await user.click(screen.getByRole('button', { name: /sí, eliminar/i }))

    expect(onDelete).toHaveBeenCalledWith(5, 10)
  })
})
