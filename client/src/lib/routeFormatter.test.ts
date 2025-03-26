import { TaskID, TaskSchemaID } from '@/types/aliases';
import { replaceTaskId, replaceTaskSchemaId, replaceTenant } from './routeFormatter';

describe('replaceTenant', () => {
  it.each([
    ['https://app.workflowai.com/tenant1', 'https://app.workflowai.com/tenant1'],
    ['https://app.workflowai.com/workflowai.com/hello', 'https://app.workflowai.com/workflowai/hello'],
    [
      'https://app.workflowai.com/workflowai.com/hello/workflowai.com/world',
      'https://app.workflowai.com/workflowai/hello/workflowai.com/world',
    ],
    [
      'https://app.workflowai.com/workflowai/hello/workflowai.com/world',
      'https://app.workflowai.com/workflowai/hello/workflowai.com/world',
    ],
    ['https://app.workflowai.com/workflowai.com/hello?foo=bar', 'https://app.workflowai.com/workflowai/hello?foo=bar'],
  ])('should replace only the tenant in the path', (url, expectedURL) => {
    const newURL = replaceTenant(url, 'workflowai.com', 'workflowai');
    expect(newURL).toBe(expectedURL);
  });
});

describe('replaceTaskSchemaId', () => {
  it.each([
    ['/tenant1/tasks/task1/1/playground', '2', '/tenant1/tasks/task1/2/playground'],
    ['/tenant1/tasks/task1/1/examples/example1', '2', '/tenant1/tasks/task1/2/examples/example1'],
  ])('should replace the task schema id in the path', (url, taskSchemaId, expectedURL) => {
    const newURL = replaceTaskSchemaId(url, taskSchemaId as TaskSchemaID);
    expect(newURL).toBe(expectedURL);
  });
});

describe('replaceTaskId', () => {
  it.each([
    ['/tenant1/tasks/task1/1/playground', 'task2', '1', '/tenant1/tasks/task2/1/playground'],
    ['/tenant1/tasks/task1/1/examples/example1', 'task2', '1', '/tenant1/tasks/task2/1/examples/example1'],
    ['/tenant1/tasks/task1/1/examples/example1', 'task2', '2', '/tenant1/tasks/task2/2/examples/example1'],
  ])('should replace the task id in the path', (url, taskId, taskSchemaId, expectedURL) => {
    const newURL = replaceTaskId(url, taskId as TaskID, taskSchemaId as TaskSchemaID);
    expect(newURL).toBe(expectedURL);
  });
});
