import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    
    // Pagination
    const page = parseInt(searchParams.get('page') || '1');
    const limit = parseInt(searchParams.get('limit') || '20');
    const skip = (page - 1) * limit;
    
    // Search and filters
    const search = searchParams.get('search') || '';
    const location = searchParams.get('location') || '';
    const domain = searchParams.get('domain') || '';
    const sortBy = searchParams.get('sortBy') || 'scraped_at';
    const sortOrder = searchParams.get('sortOrder') || 'desc';
    
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
    
    // Fetch jobs with pagination
    const [jobs, totalCount] = await Promise.all([
      prisma.indeedJob.findMany({
        where,
        orderBy,
        skip,
        take: limit,
        select: {
          id: true,
          job_title: true,
          company_name: true,
          company_location: true,
          job_url: true,
          search_position: true,
          domain: true,
          scraped_at: true,
        },
      }),
      prisma.indeedJob.count({ where }),
    ]);
    
    // Calculate pagination metadata
    const totalPages = Math.ceil(totalCount / limit);
    const hasMore = page < totalPages;
    
    return NextResponse.json({
      jobs,
      pagination: {
        page,
        limit,
        totalCount,
        totalPages,
        hasMore,
      },
    });
  } catch (error) {
    console.error('Error fetching jobs:', error);
    return NextResponse.json(
      { error: 'Failed to fetch jobs' },
      { status: 500 }
    );
  }
}
