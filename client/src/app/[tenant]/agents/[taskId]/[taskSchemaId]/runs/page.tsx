import { generateMetadataWithTitle } from '@/lib/metadata';
import { TaskSchemaParams } from '@/lib/routeFormatter';
import { TaskRunsContainer } from './TaskRunsContainer';

export async function generateMetadata({ params }: { params: TaskSchemaParams }) {
  return generateMetadataWithTitle('Runs', params);
}

export default function RunsPage() {
  return <TaskRunsContainer />;
}
