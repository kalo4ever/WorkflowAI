import { generateMetadataWithTitle } from '@/lib/metadata';
import { TaskSchemaParams } from '@/lib/routeFormatter';
import { FeedbackTableContainer } from './components/FeedbackTableContainer';

export async function generateMetadata({ params }: { params: TaskSchemaParams }) {
  return generateMetadataWithTitle('User Feedback', params);
}

export default function FeedbackPage() {
  return <FeedbackTableContainer />;
}
