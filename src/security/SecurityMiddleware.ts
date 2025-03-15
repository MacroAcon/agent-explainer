import { NextApiRequest, NextApiResponse } from 'next';
import { z } from 'zod';

export interface SecurityConfig {
  enableCSP: boolean;
  enableXSS: boolean;
  enableHSTS: boolean;
  rateLimitRequests: number;
  rateLimitWindow: number; // in seconds
}

const securityHeadersSchema = z.object({
  'Content-Security-Policy': z.string(),
  'X-XSS-Protection': z.string(),
  'X-Frame-Options': z.string(),
  'X-Content-Type-Options': z.string(),
  'Strict-Transport-Security': z.string(),
  'Referrer-Policy': z.string(),
});

export class SecurityMiddleware {
  private static instance: SecurityMiddleware;
  private config: SecurityConfig;
  private requestCounts: Map<string, number>;
  private lastReset: number;

  private constructor() {
    this.config = {
      enableCSP: true,
      enableXSS: true,
      enableHSTS: true,
      rateLimitRequests: 100,
      rateLimitWindow: 60,
    };
    this.requestCounts = new Map();
    this.lastReset = Date.now();
  }

  public static getInstance(): SecurityMiddleware {
    if (!SecurityMiddleware.instance) {
      SecurityMiddleware.instance = new SecurityMiddleware();
    }
    return SecurityMiddleware.instance;
  }

  public getSecurityHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      'X-Frame-Options': 'DENY',
      'X-Content-Type-Options': 'nosniff',
      'Referrer-Policy': 'strict-origin-when-cross-origin',
    };

    if (this.config.enableCSP) {
      headers['Content-Security-Policy'] = this.getCSPPolicy();
    }

    if (this.config.enableXSS) {
      headers['X-XSS-Protection'] = '1; mode=block';
    }

    if (this.config.enableHSTS) {
      headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains';
    }

    return headers;
  }

  private getCSPPolicy(): string {
    return [
      "default-src 'self'",
      "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
      "style-src 'self' 'unsafe-inline'",
      "img-src 'self' data: https:",
      "font-src 'self'",
      "connect-src 'self' https:",
      "media-src 'self'",
      "object-src 'none'",
      "frame-src 'self'",
      "worker-src 'self'",
      "manifest-src 'self'",
    ].join('; ');
  }

  public checkRateLimit(ip: string): boolean {
    const now = Date.now();
    if (now - this.lastReset > this.config.rateLimitWindow * 1000) {
      this.requestCounts.clear();
      this.lastReset = now;
    }

    const count = this.requestCounts.get(ip) || 0;
    if (count >= this.config.rateLimitRequests) {
      return false;
    }

    this.requestCounts.set(ip, count + 1);
    return true;
  }

  public validateRequest(req: NextApiRequest): boolean {
    // Validate request origin
    const origin = req.headers.origin;
    if (origin && !this.isValidOrigin(origin)) {
      return false;
    }

    // Validate content type for POST requests
    if (req.method === 'POST' && !this.isValidContentType(req)) {
      return false;
    }

    return true;
  }

  private isValidOrigin(origin: string): boolean {
    const allowedOrigins = [
      'http://localhost:3000',
      'https://your-production-domain.com',
    ];
    return allowedOrigins.includes(origin);
  }

  private isValidContentType(req: NextApiRequest): boolean {
    const contentType = req.headers['content-type'];
    return contentType === 'application/json';
  }

  public applySecurityHeaders(res: NextApiResponse): void {
    const headers = this.getSecurityHeaders();
    Object.entries(headers).forEach(([key, value]) => {
      res.setHeader(key, value);
    });
  }

  public validateOrigin(origin: string | null): boolean {
    if (!origin) return true; // Allow requests without origin
    const allowedOrigins = [
      'http://localhost:3000',
      'https://your-production-domain.com',
    ];
    return allowedOrigins.includes(origin);
  }

  public validateContentType(contentType: string | null, method: string): boolean {
    if (method !== 'POST') return true;
    return contentType === 'application/json';
  }
}

export const securityMiddleware = SecurityMiddleware.getInstance(); 