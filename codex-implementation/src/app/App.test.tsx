import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { App } from './App'

describe('App role shell', () => {
  it('exposes all four canonical roles as real navigation controls', () => {
    render(<App />)

    expect(screen.getAllByRole('button', { name: /workspace$/i })).toHaveLength(4)
    expect(screen.getByRole('button', { name: 'Employee workspace' })).toBeVisible()
    expect(screen.getByRole('button', { name: 'Manager workspace' })).toBeVisible()
    expect(screen.getByRole('button', { name: 'Finance workspace' })).toBeVisible()
    expect(screen.getByRole('button', { name: 'Admin workspace' })).toBeVisible()
  })
})
