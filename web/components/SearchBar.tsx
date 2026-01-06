'use client';

import { useRouter, useSearchParams } from 'next/navigation';
import { useState, useEffect } from 'react';
import { Search, MapPin, Filter, ChevronDown, ChevronUp } from 'lucide-react';

interface SearchBarProps {
  initialSearch?: string;
  initialLocation?: string;
  initialDomain?: string;
}

export default function SearchBar({
  initialSearch = '',
  initialLocation = '',
  initialDomain = '',
}: SearchBarProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  
  const [search, setSearch] = useState(initialSearch);
  const [location, setLocation] = useState(initialLocation);
  const [domain, setDomain] = useState(initialDomain);
  const [showFilters, setShowFilters] = useState(false);
  
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    
    const params = new URLSearchParams(searchParams);
    
    if (search) params.set('search', search);
    else params.delete('search');
    
    if (location) params.set('location', location);
    else params.delete('location');
    
    if (domain) params.set('domain', domain);
    else params.delete('domain');
    
    // Reset to page 1 when searching
    params.set('page', '1');
    
    router.push(`/jobs?${params.toString()}`);
  };
  
  const handleClear = () => {
    setSearch('');
    setLocation('');
    setDomain('');
    router.push('/jobs');
  };
  
  return (
    <form onSubmit={handleSearch} className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4 sm:p-6 mb-8">
      <div className="flex flex-col lg:grid lg:grid-cols-3 gap-3 mb-4">
        {/* Search Input - Always visible */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder="Job title or company..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
          />
        </div>
        
        {/* Toggle Filters Button - Mobile only */}
        <button
          type="button"
          onClick={() => setShowFilters(!showFilters)}
          className="lg:hidden flex items-center justify-center gap-2 px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 text-sm font-medium transition-colors"
        >
          <Filter className="w-4 h-4" />
          {showFilters ? 'Hide Filters' : 'Show Filters'}
          {showFilters ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>
        
        {/* Additional Filters - Collapsible on mobile, always visible on desktop */}
        <div className={`lg:contents ${showFilters ? 'contents' : 'hidden lg:contents'}`}>
          {/* Location Filter */}
          <div className="relative">
            <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Location..."
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
            />
          </div>
          
          {/* Source Filter */}
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <select
              value={domain}
              onChange={(e) => setDomain(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white appearance-none text-sm"
            >
              <option value="">All Sources</option>
              <option value="uk">🇬🇧 UK</option>
              <option value="ae">🇦🇪 UAE</option>
              <option value="sg">🇸🇬 Singapore</option>
            </select>
          </div>
        </div>
      </div>
      
      <div className="flex flex-col sm:flex-row gap-2 sm:gap-3">
        <button
          type="submit"
          className="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors text-sm"
        >
          Search
        </button>
        <button
          type="button"
          onClick={handleClear}
          className="px-6 py-2.5 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg font-medium transition-colors text-sm"
        >
          Clear
        </button>
      </div>
    </form>
  );
}
