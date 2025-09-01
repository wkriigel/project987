import type { StorybookConfig } from '@storybook/react-vite'

const config: StorybookConfig = {
  stories: [
    '../src/**/*.stories.@(ts|tsx|mdx)',
    '../src/**/*.docs.@(ts|tsx|mdx)'
  ],
  addons: ['@storybook/addon-essentials'],
  framework: {
    name: '@storybook/react-vite',
    options: {}
  },
  core: {},
  docs: { autodocs: 'tag' },
  // Sort stories by high-level groups, then alphabetical
  // Groups: Guides, UI, Inputs, (others)
  // Nested arrays define explicit order within a group.
  // Everything else falls back to alpha via 'locale'.
  features: {},
  typescript: {},
}

export default config
