import { redirect } from 'next/navigation';
import { tenantSlug } from '@/lib/auth';
import { LandingPage } from './landing/LandingPage';

export async function generateMetadata() {
  return {
    title: 'WorkflowAI',
    description: 'An open-source platform for product and development teams to design, deploy and optimize AI agents.',
    openGraph: {
      title: 'WorkflowAI',
      description:
        'An open-source platform for product and development teams to design, deploy and optimize AI agents.',
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
