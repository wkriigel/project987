export interface RankingRecord {
  [key: string]: any
  year?: string
  model?: string
  trim?: string
  asking_price_usd?: string
  mileage?: string
  total_options_msrp?: string
  options_list?: string | string[]
  exterior?: string
  interior?: string
  listing_url?: string
  source_url?: string
  deal_delta_usd?: string
}

export interface RankingResponse {
  filename: string
  count: number
  data: RankingRecord[]
}
