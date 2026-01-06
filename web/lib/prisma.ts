/**
 * Prisma Client Singleton
 * Prevents multiple instances in development (hot reload)
 * Configured for Prisma 7 with Neon adapter
 */
import './env'
import { PrismaClient } from '@prisma/client'
import { PrismaNeon } from '@prisma/adapter-neon'

// Load shared .env from parent directory

const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClient | undefined
}

// Create connection for Neon
const connectionString = process.env.DATABASE_URL

if (!connectionString) {
  throw new Error('DATABASE_URL environment variable is not set')
}

const adapter = new PrismaNeon({ connectionString })

export const prisma =
  globalForPrisma.prisma ??
  new PrismaClient({
    adapter,
    log: process.env.NODE_ENV === 'development' ? ['query', 'error', 'warn'] : ['error'],
  })

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma
