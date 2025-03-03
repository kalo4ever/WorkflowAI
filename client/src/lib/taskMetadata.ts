import { SerializableTask } from '@/types/workflowAI';

export function getTaskDescription(task: SerializableTask | undefined) {
  const versions = task?.versions;
  if (!versions || versions.length === 0) {
    return undefined;
  }
  const description = versions.find(
    (version) => !!version.description
  )?.description;
  return !!description ? description : undefined;
}
