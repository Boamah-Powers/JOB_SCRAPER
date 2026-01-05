# Job Scraper Web Interface

Next.js 14 web application for job browsing and application tracking.

## Tech Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Database**: PostgreSQL with Prisma ORM
- **Authentication**: NextAuth.js (Phase 2)
- **Package Manager**: pnpm

## Setup

### Prerequisites

- Node.js 18+ (installed via conda environment `web`)
- PostgreSQL database (shared with scraper)
- pnpm package manager

### Installation

1. **Activate conda environment:**
   ```bash
   conda activate web
   ```

2. **Install dependencies:**
   ```bash
   pnpm install
   ```

3. **Configure environment variables:**
   
   The web app uses shared database configuration from `job_scraper/.env`
   
   ```bash
   # Ensure the shared .env exists in the parent directory
   # This file should contain DATABASE_URL from the scraper setup
   
   # Create web-specific config
   cp .env.example .env.local
   ```
   
   Edit `.env.local` and set:
   - `NEXTAUTH_SECRET`: Generate with `openssl rand -base64 32`
   - `NEXTAUTH_URL`: Your app URL (http://localhost:3000 for dev)
   
   Note: `DATABASE_URL` is loaded from `../env` (shared with scraper)

4. **Generate Prisma client:**
   ```bash
   pnpm prisma generate
   ```

5. **Run database migrations:**
   ```bash
   pnpm prisma migrate dev
   ```

## Development

Start the development server:

```bash
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

```
web/
├── app/                 # Next.js App Router
│   ├── api/            # API routes
│   ├── jobs/           # Public job browsing pages
│   ├── dashboard/      # Protected dashboard
│   └── applications/   # Protected application tracking
├── components/          # Reusable React components
├── lib/                # Utility functions and configs
│   └── prisma.ts       # Prisma client singleton
├── prisma/
│   └── schema.prisma   # Database schema
└── public/             # Static assets
```

## Database Schema

### Tables

- **`users`**: User accounts with authentication
- **`indeed_jobs`**: Job postings (from scraper)
- **`applications`**: User's tracked applications
- **`application_status_history`**: Timeline of status changes

See `prisma/schema.prisma` for full schema.

## Available Scripts

- `pnpm dev`: Start development server
- `pnpm build`: Build for production
- `pnpm start`: Start production server
- `pnpm lint`: Run ESLint
- `pnpm prisma studio`: Open Prisma Studio (database GUI)
- `pnpm prisma generate`: Generate Prisma client
- `pnpm prisma migrate dev`: Run database migrations

## Features

### Public
- Browse all jobs with pagination
- Search by title, company, location
- Filter by source, location, date
- External links to job postings

### Protected
- User registration and login
- Save jobs for later
- Mark jobs as applied
- Track application status
- Add notes to applications
- View application dashboard with stats
- Application history timeline

## Learn More

- [Next.js Documentation](https://nextjs.org/docs)
- [Prisma Documentation](https://www.prisma.io/docs)
- [NextAuth.js Documentation](https://next-auth.js.org)

## License

MIT
