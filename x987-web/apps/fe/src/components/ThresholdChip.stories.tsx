import type { Meta, StoryObj } from '@storybook/react'
import { ThresholdChip } from './ThresholdChip'

const meta: Meta<typeof ThresholdChip> = {
  title: 'UI/Chips/Chip/ThresholdChip',
  component: ThresholdChip,
  tags: ['autodocs'],
  parameters: {
    layout: 'padded',
    docs: {
      description: {
        component: 'Five-level chip per color (two light, three dark) using OKLCH ramps; pairs hue-consistent bg/fg for contrast.'
      },
      source: { type: 'code' }
    }
  }
}

export default meta

type Story = StoryObj<typeof ThresholdChip>

export const TealAndGreen: Story = {
  render: () => (
    <div className="space-y-6">
      <section>
        <h3 className="text-base font-semibold mb-3">Teal</h3>
        <div className="flex flex-wrap gap-2 items-center">
          <ThresholdChip color="teal" level="poor" text="poor" />
          <ThresholdChip color="teal" level="weak" text="weak" />
          <ThresholdChip color="teal" level="fair" text="fair" />
          <ThresholdChip color="teal" level="good" text="good" />
          <ThresholdChip color="teal" level="excellent" text="excellent" />
        </div>
      </section>
      <section>
        <h3 className="text-base font-semibold mb-3">Green (Olive/Forest)</h3>
        <div className="flex flex-wrap gap-2 items-center">
          <ThresholdChip color="green" level="poor" text="poor" />
          <ThresholdChip color="green" level="weak" text="weak" />
          <ThresholdChip color="green" level="fair" text="fair" />
          <ThresholdChip color="green" level="good" text="good" />
          <ThresholdChip color="green" level="excellent" text="excellent" />
        </div>
      </section>
    </div>
  )
}
