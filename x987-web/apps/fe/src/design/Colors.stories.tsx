import type { Meta, StoryObj } from '@storybook/react'
import { ramps } from './tokens/colors'
import { ColorSwatch } from '../components/ColorSwatch'

const meta: Meta = {
  title: 'Design/Colors',
  parameters: {
    layout: 'fullscreen',
    docs: {
      description: {
        component:
          'Brand color palette generated with OKLCH for perceptual uniformity. Each ramp provides 100–900 steps; use opacity for “dim” variants.'
      },
      source: { type: 'code' }
    }
  }
}

export default meta

type Story = StoryObj

export const Palette: Story = {
  parameters: { controls: { hideNoControlsWarning: true } },
  render: () => (
    <div className="p-6 space-y-6">
      {ramps.map(([name, ramp]) => (
        <section key={name}>
          <h3 className="text-base font-semibold mb-3 capitalize">{name}</h3>
          <div className="flex flex-wrap gap-4">
            {Object.entries(ramp).map(([k, hex]) => (
              <ColorSwatch key={k} hex={hex as string} token={`${name}-${k}`} />
            ))}
          </div>
        </section>
      ))}
    </div>
  )
}
