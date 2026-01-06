import Link from 'next/link';

export default function Home() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex flex-col items-center justify-center">
      <main className="max-w-7xl mx-auto px-2 sm:px-4 lg:px-6 py-8 text-center">
        <h1 className="text-5xl font-bold mb-4 text-gray-900 dark:text-white">
          Job Scraper
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-300 mb-8">
          Your intelligent job market tracking system
        </p>
        
        <div className="flex gap-4 justify-center">
          <Link
            href="/jobs"
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
          >
            Browse Jobs
          </Link>
        </div>
      </main>
    </div>
  );
}
