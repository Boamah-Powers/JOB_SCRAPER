import { prisma } from '@/lib/prisma';
import SearchBar from '@/components/SearchBar';
import Pagination from '@/components/Pagination';
import { ExternalLink } from 'lucide-react';
import { Prisma } from '@prisma/client';

interface SearchParams {
  page?: string;
  search?: string;
  location?: string;
  domain?: string;
  sortBy?: string;
  sortOrder?: string;
}

export default async function JobsPage({
  searchParams,
}: {
  searchParams: Promise<SearchParams>;
}) {
  const params = await searchParams;
  
  const page = parseInt(params.page || '1');
  const limit = 20;
  const skip = (page - 1) * limit;
  
  const search = params.search || '';
  const location = params.location || '';
  const domain = params.domain || '';
  const sortBy = params.sortBy || 'scraped_at';
  const sortOrder = (params.sortOrder || 'desc') as 'asc' | 'desc';
  
  // Build where clause
  const where: any = {};
  
  if (search) {
    where.OR = [
      { job_title: { contains: search, mode: 'insensitive' } },
      { company_name: { contains: search, mode: 'insensitive' } },
    ];
  }
  
  if (location) {
    where.company_location = { contains: location, mode: 'insensitive' };
  }
  
  if (domain) {
    where.domain = domain;
  }
  
  // Build orderBy clause
  const orderBy: any = {};
  orderBy[sortBy] = sortOrder;
  
  // Fetch jobs and total count
  const [jobs, totalCount] = await Promise.all([
    prisma.indeedJob.findMany({
      where,
      orderBy,
      skip,
      take: limit,
    }),
    prisma.indeedJob.count({ where }),
  ]) as [Prisma.IndeedJobGetPayload<{}>[], number];
  
  const totalPages = Math.ceil(totalCount / limit);
  
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-2 sm:px-4 lg:px-6 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
            Browse Jobs
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            Discover opportunities from multiple sources
          </p>
        </div>
        
        {/* Search and Filters */}
        <SearchBar
          initialSearch={search}
          initialLocation={location}
          initialDomain={domain}
        />
        
        {/* Results Summary */}
        <div className="mb-6 flex flex-col sm:flex-row sm:justify-between sm:items-center gap-3">
          <p className="text-gray-600 dark:text-gray-300 text-sm sm:text-base">
            {totalCount.toLocaleString()} jobs found
            {search && ` for "${search}"`}
            {location && ` in ${location}`}
          </p>
          
          <div className="flex gap-2">
            <select
              name="sortBy"
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm"
              defaultValue={sortBy}
            >
              <option value="scraped_at">Date Posted</option>
              <option value="company_name">Company</option>
              <option value="job_title">Job Title</option>
            </select>
          </div>
        </div>
        
        {/* Job Table */}
        {jobs.length > 0 ? (
          <>
            {/* Mobile Card View */}
            <div className="block lg:hidden space-y-4 mb-8">
              {jobs.map((job) => {
                const scrapedDate = new Date(job.scraped_at || Date.now());
                const daysAgo = Math.floor((Date.now() - scrapedDate.getTime()) / (1000 * 60 * 60 * 24));
                const dateDisplay = daysAgo === 0 ? 'Today' : daysAgo === 1 ? 'Yesterday' : `${daysAgo}d ago`;
                
                return (
                  <div key={job.id} className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
                    <div className="flex justify-between items-start mb-3">
                      <div className="flex-1">
                        <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-1">
                          {job.job_title}
                        </h3>
                        <p className="text-sm text-gray-600 dark:text-gray-300">{job.company_name}</p>
                      </div>
                      <span className="ml-2 px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 whitespace-nowrap">
                        {job.domain}
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400 mb-3">
                      <span>{job.company_location}</span>
                      <span>{dateDisplay}</span>
                    </div>
                    <a
                      href={job.job_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="w-full inline-flex items-center justify-center gap-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-colors"
                    >
                      View Job
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  </div>
                );
              })}
            </div>

            {/* Desktop Table View */}
            <div className="hidden lg:block bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden mb-8">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                  <thead className="bg-gray-50 dark:bg-gray-900">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        Job Title
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        Company
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        Location
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        Domain
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        Posted
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        Action
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                    {jobs.map((job) => {
                      const scrapedDate = new Date(job.scraped_at || Date.now());
                      const daysAgo = Math.floor((Date.now() - scrapedDate.getTime()) / (1000 * 60 * 60 * 24));
                      const dateDisplay = daysAgo === 0 ? 'Today' : daysAgo === 1 ? 'Yesterday' : `${daysAgo}d ago`;
                      
                      return (
                        <tr key={job.id} className="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm font-medium text-gray-900 dark:text-white">
                              {job.job_title}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm text-gray-900 dark:text-gray-300">
                              {job.company_name}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm text-gray-500 dark:text-gray-400">
                              {job.company_location}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                              {job.domain}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                            {dateDisplay}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                            <a
                              href={job.job_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300 inline-flex items-center gap-1"
                            >
                              View
                              <ExternalLink className="w-4 h-4" />
                            </a>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
            
            {/* Pagination */}
            <Pagination
              currentPage={page}
              totalPages={totalPages}
              totalCount={totalCount}
            />
          </>
        ) : (
          <div className="text-center py-12">
            <p className="text-gray-500 dark:text-gray-400 text-lg">
              No jobs found matching your criteria.
            </p>
            <p className="text-gray-400 dark:text-gray-500 mt-2">
              Try adjusting your search filters.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
