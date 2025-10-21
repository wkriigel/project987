import { Modal, Button, Typography, Input, Space, message } from 'antd'
import { CopyOutlined } from '@ant-design/icons'
import { useMemo } from 'react'
import { makeVaBookmarklet } from '../lib/bookmarklet'

const { Text } = Typography

export interface BookmarkletModalFullProps {
  open: boolean
  onClose: () => void
}

export function BookmarkletModalFull({ open, onClose }: BookmarkletModalFullProps) {
  const code = useMemo(() => makeVaBookmarklet('/ingest-full.html'), [])

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(code)
      message.success('Bookmarklet copied')
    } catch {
      message.error('Copy failed')
    }
  }

  return (
    <Modal
      open={open}
      onCancel={onClose}
      title="Manual Add Bookmarklet"
      footer={<Button onClick={onClose}>Close</Button>}
    >
      <Space direction="vertical" style={{ width: '100%' }} size="small">
        <Text>Suggested bookmark name: <strong>x987 Manual Add</strong></Text>
        <div>
          <ol style={{ paddingLeft: 18, margin: 0 }}>
            <li>Drag a new bookmark to your bookmarks bar.</li>
            <li>Edit it and paste the code below as the URL.</li>
            <li>On a VINAnalytics vehicle page, click <em>x987 Manual Add</em>.</li>
            <li>Paste the listing URL, and optionally price and miles.</li>
            <li>Click Save — it adds to the table and the tab auto‑closes.</li>
          </ol>
        </div>
        <Input.TextArea value={code} readOnly autoSize={{ minRows: 8, maxRows: 14 }} />
        <Button icon={<CopyOutlined />} onClick={copy}>Copy Bookmarklet</Button>
        <Text type="secondary">Note: This variant prompts for the listing URL before saving.</Text>
      </Space>
    </Modal>
  )
}
