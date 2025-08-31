export interface RankingRecord {
  [key: string]: any
  year?: string
  model_trim?: string
  asking_price_usd?: string
  mileage?: string
  total_options_msrp?: string
  options_list?: string | string[]
  exterior_color_name?: string
  interior_color_name?: string
  listing_url?: string
  source_url?: string
  deal_delta_usd?: string
}

export interface RankingResponse {
  filename: string
  count: number
  data: RankingRecord[]
}
