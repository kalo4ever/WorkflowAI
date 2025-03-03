import { generateMetadataWithTitle } from '@/lib/metadata';
import { TaskSchemaParams } from '@/lib/routeFormatter';
import ReviewsContainer from './ReviewsContainer';

export async function generateMetadata({
  params,
}: {
  params: TaskSchemaParams;
}) {
  return generateMetadataWithTitle('Versions', params);
}

export default function ReviewsPage() {
  return <ReviewsContainer />;
}
