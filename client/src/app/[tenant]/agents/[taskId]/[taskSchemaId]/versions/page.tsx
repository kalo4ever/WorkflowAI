import { generateMetadataWithTitle } from '@/lib/metadata';
import { TaskSchemaParams } from '@/lib/routeFormatter';
import VersionsContainer from './VersionsContainer';

export async function generateMetadata({ params }: { params: TaskSchemaParams }) {
  return generateMetadataWithTitle('Versions', params);
}

export default function VersionsPage() {
  return <VersionsContainer />;
}
