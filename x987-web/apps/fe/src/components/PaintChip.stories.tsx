import type { Meta, StoryObj } from '@storybook/react'
import { PaintChip, PaintChipExterior, PaintChipInterior } from './PaintChip'
import { exteriorPaint, interiorPaint } from '../design/paint/colors'

const meta: Meta<typeof PaintChip> = {
  title: 'UI/Chips/Chip/PaintChip',
  component: PaintChip,
  tags: ['autodocs'],
  args: {
    exteriorName: 'meteor gray',
    interiorName: 'black',
  },
  parameters: {
    docs: { source: { type: 'code' } }
  }
}

export default meta

type Story = StoryObj<typeof PaintChip>

export const Default: Story = {}

export const WithLabel: Story = {
  args: { label: 'Meteor Gray / Black' }
}

export const FullWidth: Story = {
  args: { size: 'full' }
}

export const ExteriorPalette: Story = {
  render: () => (
    <div className="grid grid-cols-2 gap-2 max-w-[560px]">
      {Object.entries(exteriorPaint).map(([name, hex]) => (
        <PaintChipExterior key={name} name={name} hex={hex} />
      ))}
    </div>
  )
}

export const InteriorPalette: Story = {
  render: () => (
    <div className="grid grid-cols-2 gap-2 max-w-[560px]">
      {Object.entries(interiorPaint).map(([name, hex]) => (
        <PaintChipInterior key={name} name={name} hex={hex} />
      ))}
    </div>
  )
}
