import { LandingPage } from './landing/page';

export async function generateMetadata() {
  return {
    title: 'WorkflowAI',
    description:
      'An open-source platform for product and development teams to design, deploy and optimize AI agents.',
    openGraph: {
      title: 'WorkflowAI',
      description:
        'An open-source platform for product and development teams to design, deploy and optimize AI agents.',
    },
  };
}

export default function Page() {
  return <LandingPage />;
}
