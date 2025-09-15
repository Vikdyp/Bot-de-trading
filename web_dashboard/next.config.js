/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  async rewrites() {
    return [
      // Proxy côté serveur Next -> service api (docker)
      { source: '/api/:path*', destination: 'http://api:8000/:path*' },
    ];
  },
};
module.exports = nextConfig;
