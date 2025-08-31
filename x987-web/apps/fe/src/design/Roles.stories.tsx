import type { Meta, StoryObj } from '@storybook/react'
import { roles } from './tokens/roles'
import { ColorSwatch } from '../components/ColorSwatch'

const meta: Meta = {
  title: 'Design/Roles',
  parameters: {
    layout: 'padded',
    docs: {
      description: {
        component: 'Semantic roles mapped to brand palette for consistent usage across components.'
      },
      source: { type: 'code' }
    }
  }
}

export default meta

type Story = StoryObj

export const RolePalette: Story = {
  parameters: { controls: { hideNoControlsWarning: true } },
  render: () => (
    <div className="space-y-6">
      <section>
        <h3 className="text-base font-semibold mb-3">Background</h3>
        <div className="flex flex-wrap gap-4">
          {Object.entries(roles.bg).map(([name, hex]) => (
            <ColorSwatch key={name} hex={hex as string} token={`bg.${name}`} />
          ))}
        </div>
      </section>
      <section>
        <h3 className="text-base font-semibold mb-3">Text</h3>
        <div className="flex flex-wrap gap-4">
          {Object.entries(roles.text).map(([name, hex]) => (
            <ColorSwatch key={name} hex={hex as string} token={`text.${name}`} />
          ))}
        </div>
      </section>
      <section>
        <h3 className="text-base font-semibold mb-3">Highlight</h3>
        <div className="flex flex-wrap gap-4">
          {Object.entries(roles.highlight).map(([name, hex]) => (
            <ColorSwatch key={name} hex={hex as string} token={`highlight.${name}`} />
          ))}
        </div>
      </section>
      <section>
        <h3 className="text-base font-semibold mb-3">Accents</h3>
        <div className="flex flex-wrap gap-4">
          {Object.entries(roles.accent).map(([name, hex]) => (
            <ColorSwatch key={name} hex={hex as string} token={`accent.${name}`} />
          ))}
        </div>
      </section>
      <section>
        <h3 className="text-base font-semibold mb-3">Status</h3>
        <div className="flex flex-wrap gap-4">
          {Object.entries(roles.status).map(([name, hex]) => (
            <ColorSwatch key={name} hex={hex as string} token={`status.${name}`} />
          ))}
        </div>
      </section>
    </div>
  )
}
