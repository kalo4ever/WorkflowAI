import { generateMetadataWithTitle } from '@/lib/metadata';
import { TaskSchemaParams } from '@/lib/routeFormatter';
import { BenchmarksContainer } from './BenchmarksContainer';

export async function generateMetadata({ params }: { params: TaskSchemaParams }) {
  return generateMetadataWithTitle('Benchmarks', params);
}

export default function BenchmarksPage() {
  return <BenchmarksContainer />;
}
