import { Modal, Button, Typography, Input, Space, message } from 'antd'
import { CopyOutlined } from '@ant-design/icons'
import { useMemo } from 'react'
import { makeInspectVinBookmarklet } from '../lib/bookmarklet'

const { Text } = Typography

export interface BookmarkletModalInspectProps {
  open: boolean
  onClose: () => void
}

export function BookmarkletModalInspect({ open, onClose }: BookmarkletModalInspectProps) {
  const code = useMemo(() => makeInspectVinBookmarklet(), [])

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
      title="Inspect VIN Bookmarklet"
      footer={<Button onClick={onClose}>Close</Button>}
    >
      <Space direction="vertical" style={{ width: '100%' }} size="small">
        <Text>Suggested bookmark name: <strong>x987 Inspect VIN</strong></Text>
        <div>
          <ol style={{ paddingLeft: 18, margin: 0 }}>
            <li>Drag a new bookmark to your bookmarks bar.</li>
            <li>Edit it and paste the code below as the URL.</li>
            <li>On any page, select a 17‑char VIN (or place the cursor in a VIN field) and click <em>x987 Inspect VIN</em>.</li>
            <li>It opens the corresponding VINAnalytics page in a new tab.</li>
          </ol>
        </div>
        <Input.TextArea value={code} readOnly autoSize={{ minRows: 6, maxRows: 12 }} />
        <Button icon={<CopyOutlined />} onClick={copy}>Copy Bookmarklet</Button>
        <Text type="secondary">Tip: If no VIN is selected, it scans the page for the first VIN or prompts to enter one.</Text>
      </Space>
    </Modal>
  )
}

