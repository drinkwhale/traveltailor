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
  webpack: (config, { isServer }) => {
    config.resolve.alias['@shared-types'] = path.resolve(__dirname, '../shared/types')

    // PostHog가 클라이언트 사이드에서 Node.js 내장 모듈을 사용하려고 시도하는 것을 방지
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        'node:child_process': false,
        'node:fs': false,
        'node:path': false,
        'child_process': false,
        'fs': false,
      }
    }

    return config
  },
}

module.exports = nextConfig
