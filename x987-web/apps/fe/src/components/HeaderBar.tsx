import React from 'react'
import { Layout, Space, Button, Tooltip } from 'antd'
import { DownloadOutlined, BookOutlined } from '@ant-design/icons'
import { roles } from '../design/tokens/roles'

const { Header } = Layout

export function HeaderBar({
  title = 'x987',
  subtitle = 'Web',
  onExport,
  onBookmarklet
}: {
  title?: string
  subtitle?: string
  onExport?: () => void
  onBookmarklet?: () => void
}) {
  return (
    <Header
      style={{
        background: roles.bg.surfaceAlt as string,
        color: roles.text.primary as string,
        padding: 0,
        borderBottom: `1px solid ${roles.bg.surface as string}`,
        position: 'sticky',
        top: 0,
        zIndex: 100
      }}
    >
      <div className="max-w-7xl mx-auto w-full flex items-center justify-between px-3 h-14">
        <div className="flex items-baseline gap-2 font-semibold tracking-tight">
          <span className="text-base">{title}</span>
          <span className="text-xs opacity-60">{subtitle}</span>
        </div>
        <Space size="small">
          <Tooltip title="Export filtered rows as JSON">
            <Button size="small" icon={<DownloadOutlined />} onClick={onExport}>
              Export JSON
            </Button>
          </Tooltip>
          <Tooltip title="Open bookmarklet helper">
            <Button size="small" icon={<BookOutlined />} onClick={onBookmarklet}>
              Bookmarklet
            </Button>
          </Tooltip>
        </Space>
      </div>
    </Header>
  )
}
