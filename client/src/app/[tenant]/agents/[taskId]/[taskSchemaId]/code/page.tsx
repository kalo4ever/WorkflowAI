import { generateMetadataWithTitle } from '@/lib/metadata';
import { TaskSchemaParams } from '@/lib/routeFormatter';
import { ApiContainer } from './ApiContainer';

export async function generateMetadata({
  params,
}: {
  params: TaskSchemaParams;
}) {
  return generateMetadataWithTitle('Code', params);
}

export default function BenchmarksPage() {
  return <ApiContainer />;
}
