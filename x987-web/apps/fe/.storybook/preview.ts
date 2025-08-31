import type { Preview } from '@storybook/react'
// Load global styles so Tailwind utility classes work in stories
import '../src/styles/tailwind.css'
import 'antd/dist/reset.css'

const preview: Preview = {
  parameters: {
    docs: {
      source: {
        type: 'code',
        state: 'open'
      }
    }
  }
}

export default preview
