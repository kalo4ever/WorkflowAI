import { redirect } from 'next/navigation';
import { tenantSlug } from '@/lib/auth';
import { LandingPage } from './landing/LandingPage';

export async function generateMetadata() {
  return {
    title: 'WorkflowAI | Build AI features your users will love.',
    description:
      'WorkflowAI is an open-source platform where product and engineering teams collaborate to build and iterate on AI features.',
    openGraph: {
      title: 'WorkflowAI | Build AI features your users will love.',
      description:
        'WorkflowAI is an open-source platform where product and engineering teams collaborate to build and iterate on AI features.',
      images: [
        {
          url: 'https://workflowai.blob.core.windows.net/workflowai-public/preview.jpg',
          width: 720,
          height: 438,
          alt: 'WorkflowAI',
        },
      ],
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
