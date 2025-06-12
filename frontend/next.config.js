/** @type {import('next').NextConfig} */
const nextConfig = {
  typescript: {
    ignoreBuildErrors: false,
  },
  eslint: {
    ignoreDuringBuilds: false,
  },
  async rewrites() {
    // When running in Docker, use service name; when running locally, use localhost
    const backendUrl = process.env.DOCKER_ENV === 'true' 
      ? 'http://backend_user:8000'
      : 'http://localhost:8000';
      
    return [
      {
        source: '/api/:path*',
        destination: `${backendUrl}/:path*`,
      },
    ];
  },
  trailingSlash: false, // Let backend handle trailing slashes
};

module.exports = nextConfig; 