import { headers } from 'next/headers';
import { BACKEND_API_URL } from '@/lib/constants';
import { TaskSchemaParams } from '@/lib/routeFormatter';
import { getTaskDescription } from '@/lib/taskMetadata';
import { SerializableTask } from '@/types/workflowAI';

function getAppBaseURL() {
  const fromEnv = process.env.NEXT_PUBLIC_WORKFLOWAI_APP_URL;
  if (fromEnv) {
    return fromEnv;
  }
  const headersList = headers();
  const requestUrl = headersList.get('x-request-url');
  if (requestUrl) {
    return new URL(requestUrl).origin;
  }
  return '';
}

export async function generateMetadata({ params }: { params: TaskSchemaParams }) {
  const { tenant, taskId } = params;

  try {
    const task: SerializableTask = await fetch(`${BACKEND_API_URL}/${tenant}/agents/${taskId}`).then((res) =>
      res.json()
    );

    const description = getTaskDescription(task);
    const baseUrl = getAppBaseURL();

    const previewImageUrl = `${baseUrl}/api/agents/images/${tenant}/${taskId}`;

    return {
      openGraph: {
        description,
        images: [previewImageUrl],
      },
      twitter: {
        card: 'summary_large_image',
        title: task.name,
        description,
        images: [previewImageUrl],
      },
    };
  } catch (error) {
    console.error(error);
    return {
      openGraph: {},
    };
  }
}
export default function Layout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <div className='flex flex-1 overflow-y-auto w-full h-full'>{children}</div>;
}
