import { defineConfig } from '@hey-api/openapi-ts';

const apiUrl = process.env.VITE_API_URL || 'https://seerynx.local';
const apiKey = process.env.OPENAPI_API_KEY || '';

export default defineConfig({
  input: {
    path: `${apiUrl}/api/openapi.json`,
    fetch: {
      headers: {
        'X-API-Key': apiKey,
      },
    },
  },
  output: {
    path: 'src/client',
    postProcess: ['prettier'],
  },
  plugins: [
    '@hey-api/client-fetch',
    '@tanstack/react-query',
  ],
});