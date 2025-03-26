import { usePathname, useRouter } from 'next/navigation';
import { useCallback, useEffect, useState } from 'react';
import { useMemo } from 'react';
import { useIsAllowed } from '@/lib/hooks/useIsAllowed';
import { useLoggedInTenantID, useTaskParams } from '@/lib/hooks/useTaskParams';
import { replaceTaskId, replaceTaskSchemaId, replaceTenant, taskSchemaRoute } from '@/lib/routeFormatter';
import { getActiveSchemaIds, getHiddenSchemaIds, getVisibleSchemaIds } from '@/lib/taskUtils';
import { useOrFetchTask, useTasks } from '@/store';
import { TaskID, TaskSchemaID, TenantID } from '@/types/aliases';
import { SerializableTask } from '@/types/workflowAI';
import { SchemaSection } from './SchemasSection';
import { TaskComboboxOption, TaskSwitcher } from './TaskSwitcher';
import { TaskSwitcherMode } from './TaskSwitcher';

type TaskSwitcherContainerProps = {
  mode?: TaskSwitcherMode;
  tasks: SerializableTask[];
  open: boolean;
  setOpen: (value: boolean) => void;
  trigger?: React.ReactNode;
  titleForFeatures?: string;
};

export function TaskSwitcherContainer(props: TaskSwitcherContainerProps) {
  const { mode = TaskSwitcherMode.TASKS_AND_SCHEMAS, tasks, open, setOpen, trigger, titleForFeatures } = props;
  const { taskSchemaId, taskId, tenant } = useTaskParams();

  const fetchTask = useTasks((state) => state.fetchTask);
  const { task: currentTask } = useOrFetchTask(tenant, taskId);

  // Fetch the task when the popover is opened and the mode supports showing schemas
  useEffect(() => {
    if (open && !!taskId && (mode === TaskSwitcherMode.TASKS_AND_SCHEMAS || mode === TaskSwitcherMode.SCHEMAS)) {
      fetchTask(tenant, taskId);
    }
  }, [fetchTask, tenant, taskId, open, mode]);

  const router = useRouter();
  const pathname = usePathname();

  const loggedInTenant = useLoggedInTenantID();
  const { checkIfSignedIn } = useIsAllowed();

  const tasksFormattedOptions: TaskComboboxOption[] = useMemo(
    () =>
      tasks.map(({ name, id, is_public }) => {
        return {
          label: name,
          value: id,
          isPublic: is_public || false,
          key: `${name} ${id}`.toLowerCase(),
        };
      }),
    [tasks]
  );

  const visibleSchemaIds = useMemo(() => {
    return getVisibleSchemaIds(currentTask);
  }, [currentTask]);

  const hiddenSchemaIds = useMemo(() => {
    return getHiddenSchemaIds(currentTask);
  }, [currentTask]);

  const activeSchemaIds = useMemo(() => {
    return getActiveSchemaIds(currentTask);
  }, [currentTask]);

  const onTaskChange = useCallback(
    (newTaskId: TaskID) => {
      const newTask = tasks.find((task) => task.id === newTaskId);
      if (!newTask || !loggedInTenant) return;
      let newUrl: string;

      const newTaskSchemaId = `${getVisibleSchemaIds(newTask)[0] ?? getHiddenSchemaIds(newTask)[0]}` as TaskSchemaID;

      if (!!taskSchemaId) {
        // We want to replace the current task name in the URL
        // without changing the rest of the URL
        newUrl = currentTask
          ? replaceTaskId(pathname, newTaskId, newTaskSchemaId)
          : taskSchemaRoute(loggedInTenant, newTaskId, newTaskSchemaId);
      } else {
        newUrl = currentTask
          ? replaceTaskId(pathname, newTaskId)
          : taskSchemaRoute(loggedInTenant, newTaskId, newTaskSchemaId);
      }
      newUrl = replaceTenant(newUrl, tenant, loggedInTenant);
      router.push(newUrl);
    },
    [tasks, currentTask, pathname, loggedInTenant, router, taskSchemaId, tenant]
  );

  const onTaskSchemaChange = useCallback(
    (newTaskSchemaId: TaskSchemaID) => {
      if (!taskId) return;
      let newUrl: string;
      if (!taskSchemaId) {
        newUrl = taskSchemaRoute(loggedInTenant, taskId, newTaskSchemaId);
      } else {
        // The URL has the following format:
        // /[tenant]/tasks/[taskId]/[taskSchemaId]/...
        // We want to replace the taskSchemaId with the new one
        newUrl = replaceTaskSchemaId(pathname, newTaskSchemaId);
      }
      router.push(newUrl);
    },
    [pathname, router, taskId, loggedInTenant, taskSchemaId]
  );

  return (
    <TaskSwitcher
      mode={mode}
      trigger={trigger}
      taskOptions={tasksFormattedOptions}
      currentTask={currentTask}
      currentTaskSchemaId={taskSchemaId}
      taskSchemaIds={visibleSchemaIds}
      hiddenSchemaIds={hiddenSchemaIds}
      activeSchemaIds={activeSchemaIds}
      onTaskChange={onTaskChange}
      onTaskSchemaChange={onTaskSchemaChange}
      checkIfSignedIn={checkIfSignedIn}
      open={open}
      setOpen={setOpen}
      titleForFeatures={titleForFeatures}
    />
  );
}

type SchemaSelectorContainerProps = {
  tenant: TenantID;
  taskId: TaskID;
  selectedSchemaId: TaskSchemaID;
  setSelectedSchemaId?: (schemaId: TaskSchemaID) => void;
  showSlash?: boolean;
};

export function SchemaSelectorContainer(props: SchemaSelectorContainerProps) {
  const { selectedSchemaId, taskId, tenant, setSelectedSchemaId, showSlash } = props;

  const fetchTask = useTasks((state) => state.fetchTask);
  const { task: currentTask } = useOrFetchTask(tenant, taskId);

  const [open, setOpen] = useState(false);

  // Fetch the task when the popover is opened and the mode supports showing schemas
  useEffect(() => {
    if (open && !!taskId) {
      fetchTask(tenant, taskId);
    }
  }, [fetchTask, tenant, taskId, open]);

  const router = useRouter();
  const pathname = usePathname();

  const loggedInTenant = useLoggedInTenantID();
  const { checkIfSignedIn } = useIsAllowed();

  const visibleSchemaIds = useMemo(() => {
    return getVisibleSchemaIds(currentTask);
  }, [currentTask]);

  const hiddenSchemaIds = useMemo(() => {
    return getHiddenSchemaIds(currentTask);
  }, [currentTask]);

  const activeSchemaIds = useMemo(() => {
    return getActiveSchemaIds(currentTask);
  }, [currentTask]);

  const onTaskSchemaChange = useCallback(
    (newTaskSchemaId: TaskSchemaID) => {
      if (setSelectedSchemaId) {
        setSelectedSchemaId(newTaskSchemaId);
        return;
      }

      if (!taskId) return;
      let newUrl: string;
      if (!selectedSchemaId) {
        newUrl = taskSchemaRoute(loggedInTenant, taskId, newTaskSchemaId);
      } else {
        // The URL has the following format:
        // /[tenant]/tasks/[taskId]/[taskSchemaId]/...
        // We want to replace the taskSchemaId with the new one
        newUrl = replaceTaskSchemaId(pathname, newTaskSchemaId);
      }
      router.push(newUrl);
    },
    [pathname, router, taskId, loggedInTenant, selectedSchemaId, setSelectedSchemaId]
  );

  const isActive = useMemo(() => {
    if (!selectedSchemaId) return false;
    return activeSchemaIds.includes(selectedSchemaId);
  }, [activeSchemaIds, selectedSchemaId]);

  return (
    <TaskSwitcher
      mode={TaskSwitcherMode.SCHEMAS}
      trigger={
        <div>
          <SchemaSection taskSchemaId={selectedSchemaId} isSelected={open} isActive={isActive} showSlash={showSlash} />
        </div>
      }
      taskOptions={[]}
      currentTask={currentTask}
      currentTaskSchemaId={selectedSchemaId}
      taskSchemaIds={visibleSchemaIds}
      hiddenSchemaIds={hiddenSchemaIds}
      activeSchemaIds={activeSchemaIds}
      onTaskChange={() => {}}
      onTaskSchemaChange={onTaskSchemaChange}
      checkIfSignedIn={checkIfSignedIn}
      open={open}
      setOpen={setOpen}
    />
  );
}
