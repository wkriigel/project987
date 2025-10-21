import React from 'react'
import { Layout, Space, Button, Tooltip, Divider } from 'antd'
import { DownloadOutlined, BookOutlined, PlusSquareOutlined, SearchOutlined } from '@ant-design/icons'
import { roles } from '../design/tokens/roles'

const { Header } = Layout

export function HeaderBar({
  title = 'x987',
  subtitle = 'Web',
  onExport,
  onBookmarklet,
  onBookmarkletFull,
  onBookmarkletInspect
}: {
  title?: string
  subtitle?: string
  onExport?: () => void
  onBookmarklet?: () => void
  onBookmarkletFull?: () => void
  onBookmarkletInspect?: () => void
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
      <div className="w-full flex items-center justify-between px-3 h-14">
        <div className="flex items-baseline gap-2 font-semibold tracking-tight">
          <span className="text-base">{title}</span>
          <span className="text-xs opacity-60">{subtitle}</span>
        </div>
        <Space size="small" align="center">
          <Tooltip title="Export filtered rows as JSON">
            <Button size="small" icon={<DownloadOutlined />} onClick={onExport}>
              Export JSON
            </Button>
          </Tooltip>
          <Divider type="vertical" style={{ height: 22, margin: '0 6px' }} />
          <Tooltip title="Open Import VIN Options bookmarklet">
            <Button size="small" icon={<BookOutlined />} onClick={onBookmarklet}>
              Import VIN Options
            </Button>
          </Tooltip>
          <Tooltip title="Open Manual Add bookmarklet">
            <Button size="small" icon={<PlusSquareOutlined />} onClick={onBookmarkletFull}>
              Manual Add
            </Button>
          </Tooltip>
          <Tooltip title="Open Inspect VIN bookmarklet">
            <Button size="small" icon={<SearchOutlined />} onClick={onBookmarkletInspect}>
              Inspect VIN
            </Button>
          </Tooltip>
        </Space>
      </div>
    </Header>
  )
}
