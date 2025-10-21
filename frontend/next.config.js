/** @type {import('next').NextConfig} */
const path = require('path')

const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: ['maps.googleapis.com', 'api.mapbox.com'],
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
  webpack: (config) => {
    config.resolve.alias['@shared-types'] = path.resolve(__dirname, '../shared/types')
    return config
  },
}

module.exports = nextConfig
