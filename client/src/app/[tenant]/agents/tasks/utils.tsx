import { filterActiveTasksIDs } from '@/lib/taskUtils';
import { SerializableTask } from '@/types/workflowAI';

export function filterTasks(tasks: SerializableTask[], searchQuery: string) {
  // If search query is empty, return all tasks
  if (!searchQuery.trim()) {
    return tasks;
  }

  // Split the search query into individual words and convert to lowercase
  const searchTerms = searchQuery
    .toLowerCase()
    .split(' ')
    .filter((term) => term.length > 0);

  if (searchTerms.length === 0) {
    return tasks;
  }

  // Filter tasks that match all search terms
  return tasks.filter((task) => {
    const key = `${task.name} ${task.id}`.toLowerCase();
    // Check if all search terms are included in the task name
    return searchTerms.every((term) => key.includes(term));
  });
}

export function sortTasks(tasks: SerializableTask[]) {
  const activeTasksIds = filterActiveTasksIDs(tasks);

  return tasks.sort((a, b) => {
    // First priority: run_count
    if (!!a.run_count && !!b.run_count) {
      return b.run_count - a.run_count;
    }

    if (!a.run_count && !!b.run_count) {
      return 1;
    }
    if (!!a.run_count && !b.run_count) {
      return -1;
    }

    // Second priority: active status
    const aIsActive = activeTasksIds.includes(a.id);
    const bIsActive = activeTasksIds.includes(b.id);

    if (aIsActive && !bIsActive) {
      return -1;
    }
    if (!aIsActive && bIsActive) {
      return 1;
    }

    // Last priority: alphabetical by name/id
    const aName = a.name.length === 0 ? a.id : a.name;
    const bName = b.name.length === 0 ? b.id : b.name;
    return aName.localeCompare(bName);
  });
}
