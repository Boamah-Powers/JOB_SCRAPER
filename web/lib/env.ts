/**
 * Load environment variables from shared parent directory
 * This allows both the scraper and web app to use the same .env file
 */
import { config } from 'dotenv';
import { resolve } from 'path';

// Load shared .env from parent directory (job_scraper/.env)
config({ path: resolve(__dirname, '../.env') });

// Also load local overrides if they exist
config({ path: resolve(__dirname, '.env.local'), override: true });
