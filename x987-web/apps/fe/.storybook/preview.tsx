import React from 'react'
import type { Preview } from '@storybook/react'
// Load global styles so Tailwind utility classes work in stories
import '../src/styles/tailwind.css'
import 'antd/dist/reset.css'
import { ConfigProvider } from 'antd'
import { roles } from '../src/design/tokens/roles'

const preview: Preview = {
  parameters: {
    docs: {
      source: {
        type: 'code',
        state: 'open'
      }
    },
    options: {
      storySort: {
        order: ['Guides', 'UI', ['Chips', '...'], 'Inputs', '...'],
        method: 'alphabetical',
        locales: 'en-US'
      }
    },
    backgrounds: {
      default: 'Dark Surface',
      values: [
        { name: 'Dark Surface', value: String(roles.bg.surface) },
        { name: 'Dark Page', value: String(roles.bg.page) },
        { name: 'Light', value: '#ffffff' }
      ]
    }
  },
  decorators: [
    (Story) => (
      <ConfigProvider
        theme={{
          token: {
            colorBgBase: roles.bg.page as string,
            colorBgContainer: roles.bg.surface as string,
            colorTextBase: roles.text.primary as string,
            colorTextSecondary: roles.text.muted as string,
            colorBorder: roles.bg.surfaceAlt as string,
            colorPrimary: roles.accent.teal as string
          },
          components: {
            Table: {
              headerBg: roles.bg.surfaceAlt as string,
              headerColor: roles.text.primary as string,
              rowHoverBg: roles.bg.emphasis as string
            }
          }
        }}
      >
        <div style={{ padding: 16, background: String(roles.bg.surface) }}>
          <Story />
        </div>
      </ConfigProvider>
    )
  ]
}

export default preview
