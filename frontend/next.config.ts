import path from "node:path";
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Standalone is for the Docker image. Vercel sets VERCEL=1 and its tracer
  // fails on next-server.js.nft.json when output: "standalone" is forced.
  ...(process.env.VERCEL ? {} : { output: "standalone" as const }),
  turbopack: {
    root: path.join(__dirname),
  },
};

export default nextConfig;
