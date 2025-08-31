import { Card, Space, Typography } from 'antd'
import { roles } from '../design/tokens/roles'
import { thresholdSpecs, describeBands } from '../design/thresholds'
import { Chip } from './Chip'

const { Text, Link } = Typography

export function SummaryHeader({
  displayedCount,
  filename,
  unknownLinks
}: {
  displayedCount: number
  filename?: string
  unknownLinks?: string[]
}) {
  const links = unknownLinks || []
  return (
    <Card>
      <Space size="large" wrap>
        <div>
          <div className="text-xs text-gray-400">Items displayed</div>
          <Chip text={displayedCount} bg={roles.bg.emphasis as string} color={roles.text.primary as string} />
        </div>
        <div>
          <div className="text-xs text-gray-400">Thresholds (teal/green)</div>
          <div className="text-[11px] leading-5 text-gray-300">
            <div>
              <span className="text-gray-400">Price T=</span>{thresholdSpecs.price.threshold.toLocaleString()} • {describeBands(thresholdSpecs.price).join(' | ')}
            </div>
            <div>
              <span className="text-gray-400">Miles T=</span>{thresholdSpecs.miles.threshold.toLocaleString()} • {describeBands(thresholdSpecs.miles).join(' | ')}
            </div>
            <div>
              <span className="text-gray-400">MSRP T=</span>{thresholdSpecs.msrp.threshold.toLocaleString()} • {describeBands(thresholdSpecs.msrp).join(' | ')}
            </div>
          </div>
        </div>
        <div>
          <div className="text-xs text-gray-400">Source CSV</div>
          <div className="text-sm font-medium">{filename || '—'}</div>
        </div>
        {links.length > 0 && (
          <div>
            <div className="text-xs text-gray-400">Unknown year</div>
            <div className="text-sm">
              {links.slice(0, 5).map((u, i) => (
                <span key={i}>
                  <a className="underline" href={u} target="_blank" rel="noreferrer">
                    {u.replace(/^https?:\/\//, '').split('/')[0]}
                  </a>
                  {i < Math.min(4, links.length - 1) ? ' • ' : ''}
                </span>
              ))}
              {links.length > 5 && <span> +{links.length - 5} more</span>}
            </div>
          </div>
        )}
      </Space>
    </Card>
  )
}
