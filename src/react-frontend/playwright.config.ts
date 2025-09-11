import { defineConfig, devices } from '@playwright/test';
import path from 'path';

const PORT = process.env.PORT || 3000;
const BASE_URL = process.env.BASE_URL || `http://localhost:${PORT}`;

export default defineConfig({
  testDir: './tests',
  testMatch: ['**/*.spec.ts'],
  fullyParallel: false, // Visual tests should run sequentially for consistency
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: 1, // Single worker for visual consistency
  reporter: [
    ['html', { outputFolder: 'playwright-report', open: 'never' }],
    ['json', { outputFile: 'test-results/results.json' }],
    ['junit', { outputFile: 'test-results/junit.xml' }],
    ['list']
  ],

  use: {
    baseURL: BASE_URL,
    trace: 'retain-on-failure',
    screenshot: {
      mode: 'only-on-failure',
      fullPage: true
    },
    video: 'retain-on-failure',
    actionTimeout: 10000,
    navigationTimeout: 30000,

    // Visual testing specific settings
    ignoreHTTPSErrors: true,
    locale: 'en-US',
    timezoneId: 'America/New_York',
    
    // Consistent viewport for visual tests
    viewport: { width: 1280, height: 720 },
  },

  projects: [
    {
      name: 'chromium',
      use: { 
        ...devices['Desktop Chrome'],
        // Force consistent rendering
        deviceScaleFactor: 1,
        hasTouch: false,
        isMobile: false,
        // CI-specific optimizations
        launchOptions: {
          args: [
            '--disable-animations', 
            '--disable-web-security',
            '--disable-features=TranslateUI',
            '--disable-ipc-flooding-protection',
            ...(process.env.CI ? [
              '--no-sandbox',
              '--disable-setuid-sandbox',
              '--disable-dev-shm-usage',
              '--disable-accelerated-2d-canvas',
              '--no-first-run',
              '--no-zygote',
              '--single-process',
              '--disable-gpu'
            ] : [])
          ],
        },
      },
    },
    // Only include other browsers in non-CI environments
    ...(process.env.CI ? [] : [
      {
        name: 'firefox',
        use: { 
          ...devices['Desktop Firefox'],
          deviceScaleFactor: 1,
          hasTouch: false,
          isMobile: false,
        },
      },
      {
        name: 'webkit',
        use: { 
          ...devices['Desktop Safari'],
          deviceScaleFactor: 1,
          hasTouch: false,
          isMobile: false,
        },
      },
      {
        name: 'mobile-chrome',
        use: { 
          ...devices['Pixel 5'],
          deviceScaleFactor: 2,
        },
      },
      {
        name: 'mobile-safari',
        use: { 
          ...devices['iPhone 13'],
          deviceScaleFactor: 3,
        },
      },
      {
        name: 'tablet',
        use: { 
          ...devices['iPad (gen 7)'],
          deviceScaleFactor: 2,
        },
      },
    ]),
  ],

  webServer: {
    command: process.env.CI 
      ? 'npm run build && npx serve -s build -l 3000'
      : 'npm start',
    port: Number(PORT),
    reuseExistingServer: !process.env.CI,
    timeout: process.env.CI ? 180000 : 120000, // More time for build in CI
    stdout: 'pipe',
    stderr: 'pipe',
    env: {
      ...process.env,
      BROWSER: 'none', // Prevent react-scripts from opening browser
      HOST: '0.0.0.0', // Bind to all interfaces
    },
  },

  // Visual testing specific configuration
  expect: {
    // Timeout for assertions
    timeout: 10000,

    // Visual comparison settings
    toHaveScreenshot: {
      // Maximum difference in pixels
      maxDiffPixels: 100,
      
      // Threshold for pixel difference (0-1)
      threshold: 0.2,
      
      // Animation handling
      animations: 'disabled',
      
      // Consistent screenshot naming
      scale: 'css',
    },
  },

  // Output directories
  outputDir: 'test-results',
  
  // Screenshot storage
  snapshotDir: './tests/visual/__screenshots__',
  snapshotPathTemplate: '{snapshotDir}/{testFileDir}/{testFileName}-snapshots/{arg}-{projectName}-{platform}{ext}',
});