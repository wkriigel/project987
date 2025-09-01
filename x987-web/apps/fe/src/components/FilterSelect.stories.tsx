import React, { useState } from 'react'
import type { Meta, StoryObj } from '@storybook/react'
import { FilterSelect } from './FilterSelect'

const meta: Meta<typeof FilterSelect> = {
  title: 'Inputs/Filters/FilterSelect',
  component: FilterSelect,
  tags: ['autodocs'],
  parameters: {
    layout: 'padded',
    docs: {
      description: {
        component: 'Generic labeled Select for top-of-table filters. Uses Ant Design + Tailwind, themed via roles.'
      },
      source: { type: 'code' }
    }
  }
}

export default meta

type Story = StoryObj<typeof FilterSelect>

export const Generation: Story = {
  render: () => {
    const [val, setVal] = useState<string>('all')
    return (
      <div className="p-4 bg-[#1F2937] text-[#C9D1D9] rounded">
        <FilterSelect
          label="Generation"
          value={val}
          onChange={(v) => setVal(String(v))}
          options={[
            { label: 'All', value: 'all' },
            { label: '987.1', value: '987.1' },
            { label: '987.2', value: '987.2' }
          ]}
        />
      </div>
    )
  }
}

export const Disabled: Story = {
  render: () => (
    <div className="p-4 bg-[#1F2937] text-[#C9D1D9] rounded">
      <FilterSelect
        label="Generation"
        value={'all'}
        onChange={() => {}}
        disabled
        options={[
          { label: 'All', value: 'all' },
          { label: '987.1', value: '987.1' },
          { label: '987.2', value: '987.2' }
        ]}
      />
    </div>
  )
}

export const ManyOptions: Story = {
  render: () => {
    const [val, setVal] = useState<string>('')
    const opts = Array.from({ length: 12 }).map((_, i) => ({ label: `Option ${i + 1}`, value: `opt-${i + 1}` }))
    return (
      <div className="p-4 bg-[#1F2937] text-[#C9D1D9] rounded">
        <FilterSelect
          label="Example"
          value={val || opts[0].value}
          onChange={(v) => setVal(String(v))}
          options={opts}
        />
      </div>
    )
  }
}

export const Grouped: Story = {
  render: () => {
    const [val, setVal] = useState<string>('all')
    const grouped = [
      { label: 'All (234)', value: 'all' },
      {
        label: 'Boxster/Cayman',
        options: [
          { label: '986 [1997-2004] (12)', value: 'bx-986' },
          { label: '987.1 [2005-2008] (48)', value: 'bx-987.1' },
          { label: '987.2 [2009-2012] (36)', value: 'bx-987.2' },
          { label: '981 [2013-2016] (22)', value: 'bx-981' },
          { label: '982 / 718 [2017-2025] (40)', value: 'bx-982/718' }
        ]
      },
      {
        label: '911',
        options: [
          { label: '996 [1999-2004] (9)', value: '911-996' },
          { label: '997.1 [2005-2008] (10)', value: '911-997.1' },
          { label: '997.2 [2009-2012] (8)', value: '911-997.2' },
          { label: '991.1 [2012-2016] (6)', value: '911-991.1' },
          { label: '991.2 [2017-2019] (4)', value: '911-991.2' },
          { label: '992 [2020-2025] (7)', value: '911-992' }
        ]
      }
    ]
    return (
      <div className="p-4 bg-[#1F2937] text-[#C9D1D9] rounded">
        <FilterSelect
          label="Generation"
          value={val}
          onChange={(v) => setVal(String(v))}
          options={grouped}
        />
      </div>
    )
  }
}
