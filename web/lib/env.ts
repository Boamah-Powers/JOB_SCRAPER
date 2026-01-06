/**
 * Load environment variables from shared parent directory
 * This allows both the scraper and web app to use the same .env file
 */
import { resolve } from 'path';

import { loadEnvConfig } from '@next/env'
 
const projectDir = resolve(__dirname, '../')
loadEnvConfig(projectDir)