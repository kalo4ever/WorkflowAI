import { redirect } from 'next/navigation';
import { tenantSlug } from '@/lib/auth';
import { LandingPage } from './landing/page';

export async function generateMetadata() {
  return {
    title: 'WorkflowAI | Build AI features your users will love.',
    description:
      'WorkflowAI is an open-source platform where product and engineering teams collaborate to build and iterate on AI features.',
    openGraph: {
      title: 'WorkflowAI | Build AI features your users will love.',
      description:
        'WorkflowAI is an open-source platform where product and engineering teams collaborate to build and iterate on AI features.',
    },
  };
}

export default async function Page() {
  const tenant = await tenantSlug();
  // If the user is logged in, redirect to the dashboard
  if (tenant) {
    redirect(`/${tenant}/agents`);
    return null;
  }
  return <LandingPage />;
}
