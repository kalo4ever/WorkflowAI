import { generateMetadataWithTitle } from '@/lib/metadata';
import { TaskSchemaParams } from '@/lib/routeFormatter';
import { CostContainer } from './CostContainer';

export async function generateMetadata({ params }: { params: TaskSchemaParams }) {
  return generateMetadataWithTitle('Cost', params);
}

export default function CostPage() {
  return <CostContainer />;
}
