import { Modal, Button, Typography, Input, Space, message } from 'antd'
import { CopyOutlined } from '@ant-design/icons'
import { useMemo } from 'react'

const { Text } = Typography

export interface BookmarkletModalProps {
  open: boolean
  onClose: () => void
}

export function BookmarkletModal({ open, onClose }: BookmarkletModalProps) {
  const code = useMemo(() => makeBookmarklet(), [])

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
      title="VINAnalytics Bookmarklet"
      footer={<Button onClick={onClose}>Close</Button>}
    >
      <Space direction="vertical" style={{ width: '100%' }} size="small">
        <Text>
          Drag a new bookmark to your bookmarks bar, edit it, and paste the code below as the URL. On a VINAnalytics car page, click the bookmark to auto‑save to this app (no paste needed). The tab will close automatically (browser permitting) and you’ll be back here.
        </Text>
        <Input.TextArea value={code} readOnly autoSize={{ minRows: 8, maxRows: 14 }} />
        <Button icon={<CopyOutlined />} onClick={copy}>Copy Bookmarklet</Button>
        <Text type="secondary">Note: If VINAnalytics changes its layout, we can update this code here.</Text>
      </Space>
    </Modal>
  )
}

function makeBookmarklet(): string {
  const appOrigin = (typeof window !== 'undefined' && window.location && window.location.origin) ? window.location.origin : ''
  const js = `(()=>{try{const APP='${appOrigin}';const T=s=>String(s||'').replace(/\\s+/g,' ').trim();const root=document.querySelector('.v-info')||document.body;const Q=q=>Array.from(document.querySelectorAll(q));const getVIN=()=>{let vin='';const tr=[...root.querySelectorAll('tr')].find(tr=>/vin/i.test(T(tr.cells?.[0]?.textContent||'')));if(tr){vin=T(tr.cells?.[1]?.textContent||'');}if(!vin){const m=document.body.innerText.match(/\\b([A-HJ-NPR-Z0-9]{17})\\b/i);if(m) vin=m[1].toUpperCase();}return vin;};const toMoney=v=>{const n=Number(String(v||'').replace(/[^0-9.-]/g,''));return Number.isFinite(n)?Math.round(n):null};const getMSRP=()=>{const tr=[...root.querySelectorAll('tr')].find(tr=>/msrp/i.test(T(tr.cells?.[0]?.textContent||'')));if(tr) return toMoney(tr.cells?.[1]?.textContent||'');let total=null;const nodes=[...root.querySelectorAll('*')];for(const el of nodes){const txt=T(el.textContent||'');if(/msrp/i.test(txt)){const m=txt.match(/\\$?[0-9,.]+/g);if(m){for(const cand of m){const n=toMoney(cand);if(n!=null){total=n;break}}if(total!=null) break;}}}return total;};const isBase=(s)=>/^\\s*base\\s*:?\\s*$/i.test(T(s||''));const normCode=(s)=>T(s||'').toUpperCase().replace(/[^A-Z0-9]/g,'');const isOptCode=(s)=>/^[A-Z0-9]{1,4}$/i.test(T(s||''))||normCode(s)==='BASE';const tables=[...root.querySelectorAll('table')];const options=[];for(const tb of tables){const trs=[...tb.querySelectorAll('tr')];const skip=trs.some(tr=>/window sticker|build sheet|history|profile|logout|pricing details|vin stats/i.test(T(tr.textContent||'')));if(skip) continue;for(const tr of trs){const cells=[...tr.querySelectorAll('th,td')];if(cells.length>=2){const code=T(cells[0].textContent||'');const name=T(cells[1].textContent||'');if(isOptCode(code)&&name){options.push({code,name});}}}}const getCell=(label)=>{const re=new RegExp('^'+label+'\\\\s*:?$','i');const tr=[...root.querySelectorAll('tr')].find(tr=>re.test(T(tr.cells?.[0]?.textContent||'')));return tr?T(tr.cells?.[1]?.textContent||''):''};const readModelTag=()=>{const pick=(els)=>{for(const el of els){const txt=T(el.textContent||'');if(txt && /(911|Cayman|Boxster)/i.test(txt)) return txt;}return '';};let v=pick([document.querySelector('.v-model'),root.querySelector('.v-model'),document.querySelector('.vehicle-model'),document.querySelector('.v-header .v-model'),document.querySelector('.v-hero .v-model')].filter(Boolean));if(v) return v;v=pick(Q('h1'));if(v) return v;v=pick(Q('h2'));if(v) return v;const meta=(q)=>{const el=document.querySelector(q);return T((el&&el.content)||'');};let title=T(document.title||'');let m=title.match(/(?:Porsche\\s*)?(911|Cayman|Boxster)\\s*([^|\\/\\-]*)/i);if(m){return T((m[1]||'')+' '+(m[2]||''));}let metaT=meta('meta[property="og:title"]')||meta('meta[name="og:title"]')||meta('meta[name=description i]')||meta('meta[property="og:description"]')||meta('meta[name="twitter:title"]')||meta('meta[name="twitter:description"]');m=metaT.match(/(?:Porsche\\s*)?(911|Cayman|Boxster)\\s*([^|\\/\\-]*)/i);if(m){return T((m[1]||'')+' '+(m[2]||''));}return '';};function fromModelTag(tag){let s=T(tag);if(!s)return {model:'',trim:''};s=s.replace(/^Porsche\\s+/i,'');const parts=s.split(/\\s+/);const fam=(parts[0]||'').trim();const rest=parts.slice(1).join(' ').trim();if(/^(911|Cayman|Boxster)$/i.test(fam)){return {model:fam,trim:rest};}return {model:s,trim:''};}const modelTag=readModelTag();const vin=getVIN();const mt=fromModelTag(modelTag);const year=(()=>{const t=document.title||'';const m=t.match(/\\b(19|20)\\d{2}\\b/);return m?parseInt(m[0],10):null})();const exterior=getCell('Exterior');const interior=getCell('Interior');const baseRow=(options.find(o=>normCode(o.code)==='BASE')||{});const baseName=baseRow&&baseRow.name?T(baseRow.name):(()=>{const tr=[...root.querySelectorAll('tr')].find(tr=>isBase(tr.cells?.[0]?.textContent||''));return tr?T(tr.cells?.[1]?.textContent||''):''})();const payload={vin,totalMsrp:getMSRP(),options,year,model:mt.model,trim:mt.trim,exterior,interior,baseName,modelTag};const json=JSON.stringify(payload);const encode=(s)=>{try{return btoa(unescape(encodeURIComponent(s)));}catch(e){return btoa(s);}};if(APP){window.location.href=APP+'/ingest.html#'+encode(json);}else{alert('Missing app origin: open the Bookmarklet modal in the app and copy it again.');}}catch(e){alert('Bookmarklet failed: '+(e&&e.message||e));}})();`
  return `javascript:${js}`
}
