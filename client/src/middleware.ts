// eslint-disable-next-line no-restricted-imports
import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server';
import { NextMiddleware } from 'next/server';
import { DISABLE_AUTHENTICATION } from './lib/constants';

const isProtectedRoute = createRouteMatcher(['/api/clerk(.*)']);

function buildMiddleware(): NextMiddleware {
  if (DISABLE_AUTHENTICATION) {
    return () => {};
  }
  return clerkMiddleware((auth, req) => {
    if (!auth().userId && isProtectedRoute(req)) {
      return auth().redirectToSignIn();
    }
  });
}

export default buildMiddleware();

export const config = {
  // The following matcher runs middleware on all routes
  // except static assets.
  matcher: ['/((?!.*\\..*|_next).*)', '/', '/(api|trpc)(.*)'],
};
