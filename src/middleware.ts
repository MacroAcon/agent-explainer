import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { securityMiddleware } from './security/SecurityMiddleware'
import { environmentManager } from './config/environment'
import { privacyManager } from './security/PrivacyManager'

/**
 * Determines if a given API route should be protected with PII detection
 * and other security measures.
 * 
 * @param {string} pathname - The pathname of the request
 * @returns {boolean} True if the route should be protected, false otherwise
 */
function isProtectedApiRoute(pathname: string): boolean {
  // Add all API routes that handle potentially sensitive data
  return pathname.startsWith('/api/') && 
    (pathname.includes('/agent/') || 
     pathname.includes('/user/') || 
     pathname.includes('/data/'));
}

/**
 * Processes a request to mask any PII in the request body.
 * This function examines JSON payloads and applies PII detection
 * and masking algorithms before the request reaches API handlers.
 * 
 * @param {NextRequest} request - The incoming request object
 * @returns {Promise<NextRequest>} A request with PII masked in the body
 */
async function processPiiInRequest(request: NextRequest): Promise<NextRequest> {
  const contentType = request.headers.get('content-type') || '';
  
  // Only process JSON requests
  if (contentType.includes('application/json')) {
    try {
      const body = await request.json();
      const maskedBody = maskObjectPii(body);
      
      // Create a new request with the masked body
      const maskedRequest = new Request(request.url, {
        method: request.method,
        headers: request.headers,
        body: JSON.stringify(maskedBody),
      });
      
      // Copy all the properties from the original request
      Object.defineProperties(maskedRequest, {
        nextUrl: { value: request.nextUrl },
        geo: { value: request.geo },
        ip: { value: request.ip },
      });
      
      return maskedRequest as NextRequest;
    } catch (error) {
      console.error('Error processing request body:', error);
    }
  }
  
  return request;
}

/**
 * Processes a response to mask any PII in the response body.
 * This ensures that even if internal systems process PII, it is
 * masked before being sent back to the client.
 * 
 * @param {NextResponse} response - The outgoing response
 * @returns {Promise<NextResponse>} A response with PII masked in the body
 */
async function processPiiInResponse(response: NextResponse): Promise<NextResponse> {
  try {
    const contentType = response.headers.get('content-type') || '';
    
    // Only process JSON responses
    if (contentType.includes('application/json')) {
      const body = await response.json();
      const maskedBody = maskObjectPii(body);
      
      // Create a new response with the masked body
      const maskedResponse = NextResponse.json(maskedBody, {
        status: response.status,
        statusText: response.statusText,
        headers: response.headers,
      });
      
      return maskedResponse;
    }
  } catch (error) {
    console.error('Error processing response body:', error);
  }
  
  return response;
}

/**
 * Recursively mask PII in an object using the privacy manager
 */
function maskObjectPii(obj: any): any {
  if (obj === null || obj === undefined) {
    return obj;
  }
  
  if (typeof obj === 'string') {
    return privacyManager.maskPII(obj);
  }
  
  if (Array.isArray(obj)) {
    return obj.map(item => maskObjectPii(item));
  }
  
  if (typeof obj === 'object') {
    const result: Record<string, any> = {};
    
    for (const [key, value] of Object.entries(obj)) {
      result[key] = maskObjectPii(value);
    }
    
    return result;
  }
  
  return obj;
}

// Custom type for security headers
type SecurityHeaders = {
  'Content-Security-Policy'?: string;
  'X-XSS-Protection'?: string;
  'X-Frame-Options'?: string;
  'X-Content-Type-Options'?: string;
  'Strict-Transport-Security'?: string;
  'Referrer-Policy'?: string;
};

export async function middleware(request: NextRequest) {
  const response = NextResponse.next();
  
  // Apply security headers
  const securityHeaders = securityMiddleware.getSecurityHeaders();
  Object.entries(securityHeaders).forEach(([key, value]) => {
    response.headers.set(key, value);
  });

  // Check rate limiting
  const ip = request.ip || 'unknown';
  if (!securityMiddleware.checkRateLimit(ip)) {
    return new NextResponse('Too Many Requests', { status: 429 });
  }

  // Validate request origin and content type
  const origin = request.headers.get('origin');
  const contentType = request.headers.get('content-type');
  
  if (!securityMiddleware.validateOrigin(origin) || 
      !securityMiddleware.validateContentType(contentType, request.method)) {
    return new NextResponse('Forbidden', { status: 403 });
  }

  // Process PII in protected routes
  if (isProtectedApiRoute(request.nextUrl.pathname)) {
    const maskedRequest = await processPiiInRequest(request);
    const initialResponse = NextResponse.next({
      request: maskedRequest,
    });
    return processPiiInResponse(await initialResponse);
  }

  // Add environment-specific headers
  if (environmentManager.isDevelopment()) {
    response.headers.set('X-Development-Mode', 'true');
  }

  return response;
}

export const config = {
  matcher: [
    '/api/:path*',
    '/((?!_next/static|_next/image|favicon.ico).*)',
  ],
}; 