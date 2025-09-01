import React from 'react'
import { Select, Typography } from 'antd'
import { roles } from '../design/tokens/roles'

export type FilterSelectOption = {
  label: React.ReactNode
  value: string | number
  disabled?: boolean
}

export type FilterSelectOptionGroup = {
  label: React.ReactNode
  options: FilterSelectOption[]
}

export type FilterSelectProps = {
  label?: string
  value: string | number
  onChange: (val: string | number) => void
  options: Array<FilterSelectOption | FilterSelectOptionGroup>
  disabled?: boolean
  className?: string
  allowClear?: boolean
  placeholder?: string
  size?: 'small' | 'middle' | 'large'
  showSearch?: boolean
  dropdownMatchSelectWidth?: boolean | number
}

// Generic, labeled single-select for top-of-table filters.
export function FilterSelect({
  label,
  value,
  onChange,
  options,
  disabled,
  className,
  allowClear,
  placeholder,
  size = 'middle',
  showSearch = true,
  dropdownMatchSelectWidth
}: FilterSelectProps) {
  return (
    <div className={`flex flex-col gap-1 ${className || ''}`.trim()}>
      {label ? (
        <Typography.Text style={{ color: roles.text.muted as string }}>{label}</Typography.Text>
      ) : null}
      <Select
        size={size}
        disabled={disabled}
        value={value}
        onChange={onChange}
        allowClear={allowClear}
        placeholder={placeholder}
        className="w-full min-w-[160px]"
        showSearch={showSearch}
        optionFilterProp="label"
        dropdownMatchSelectWidth={dropdownMatchSelectWidth}
        options={options as any}
      />
    </div>
  )
}
