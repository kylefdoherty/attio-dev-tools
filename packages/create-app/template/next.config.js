/** @type {import('next').NextConfig} */
const nextConfig = {
  // Attio avatar images
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "**.attio.com",
      },
    ],
  },
};

module.exports = nextConfig;
