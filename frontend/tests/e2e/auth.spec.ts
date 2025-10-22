import { test, expect } from '@playwright/test'

test.describe('Landing', () => {
  test('renders hero section', async ({ page }) => {
    await page.goto('/')
    await expect(page.getByText('AI TravelTailor')).toBeVisible()
  })
})
