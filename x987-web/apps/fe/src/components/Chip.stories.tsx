import type { Meta, StoryObj } from '@storybook/react'
import { Chip } from './Chip'
import { ThresholdChip } from './ThresholdChip'
import { PaintChip } from './PaintChip'

const meta: Meta<typeof Chip> = {
  title: 'UI/Chips/Chip',
  component: Chip,
  subcomponents: { ThresholdChip, PaintChip },
  tags: ['autodocs'],
  args: {
    text: 'Chip',
  },
  parameters: {
    docs: { source: { type: 'code' } }
  }
}

export default meta

type Story = StoryObj<typeof Chip>

export const Small: Story = {
  args: { size: 'sm' }
}

export const Medium: Story = {
  args: { size: 'md' }
}

export const Colored: Story = {
  args: { bg: '#3A4654', color: '#C9D1D9' }
}
