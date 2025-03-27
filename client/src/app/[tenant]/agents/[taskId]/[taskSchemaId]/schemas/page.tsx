import { generateMetadataWithTitle } from '@/lib/metadata';
import { TaskSchemaParams } from '@/lib/routeFormatter';
import { SchemasContainer } from './schemasContainer';

export async function generateMetadata({ params }: { params: TaskSchemaParams }) {
  return generateMetadataWithTitle('Schemas', params);
}

export default function InputOutputPage() {
  return <SchemasContainer />;
}
