import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      exclude: [
        'node_modules/',
        'src/test/',
        '**/*.d.ts',
        '**/*.config.*',
        '**/mockData*',
        'src/frontend/content/**',
        'gatsby-*.js',
        'public/**',
        '.cache/**',
      ],
      thresholds: {
        lines: 90,
        functions: 90,
        branches: 90,
        statements: 90,
      },
    },
    include: ['src/**/*.{test,spec}.{ts,tsx}'],
    exclude: ['node_modules', '.cache', 'public'],
  },
  resolve: {
    alias: {
      '@components': path.resolve(__dirname, './src/frontend/components'),
      '@hooks': path.resolve(__dirname, './src/frontend/hooks'),
      '@utils': path.resolve(__dirname, './src/frontend/utils'),
      '@styles': path.resolve(__dirname, './src/frontend/styles'),
      '@config': path.resolve(__dirname, './src/frontend/config'),
      '@images': path.resolve(__dirname, './src/frontend/images'),
      '@fonts': path.resolve(__dirname, './src/frontend/fonts'),
      '@pages': path.resolve(__dirname, './src/frontend/pages'),
    },
  },
});
