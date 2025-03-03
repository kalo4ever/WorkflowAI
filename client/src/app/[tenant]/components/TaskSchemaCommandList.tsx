import { Check } from 'lucide-react';
import { TaskSchemaBadgeContainer } from '@/components/TaskSchemaBadge/TaskSchemaBadgeContainer';
import { CommandItem } from '@/components/ui/Command';
import { CommandGroup } from '@/components/ui/Command';
import { CommandList } from '@/components/ui/Command';
import { Separator } from '@/components/ui/Separator';
import { cn } from '@/lib/utils';
import { TaskSchemaID } from '@/types/aliases';

type TaskSchemaCommandListProps = {
  title: string;
  taskSchemaIds: TaskSchemaID[] | undefined;
  currentTaskSchemaId: TaskSchemaID | undefined;
  activeSchemaIds: TaskSchemaID[] | undefined;
  onTaskSchemaChange: (value: TaskSchemaID) => void;
  setOpen: (value: boolean) => void;
  className?: string;
};

export function TaskSchemaCommandList(props: TaskSchemaCommandListProps) {
  const {
    title,
    taskSchemaIds,
    currentTaskSchemaId,
    activeSchemaIds,
    onTaskSchemaChange,
    setOpen,
    className,
  } = props;

  if (!taskSchemaIds || taskSchemaIds.length === 0) return null;

  return (
    <>
      <div
        className={cn(
          'text-indigo-600 text-xs font-medium font-lato px-3 pt-2.5',
          className
        )}
      >
        {title}
      </div>
      <div className='flex flex-col pb-1'>
        <CommandList className='max-h-max'>
          <CommandGroup>
            {taskSchemaIds.map((schemaId) => (
              <CommandItem
                className='flex items-center gap-2'
                key={schemaId}
                onSelect={() => {
                  if (schemaId !== currentTaskSchemaId) {
                    onTaskSchemaChange(schemaId);
                  }
                  setOpen(false);
                }}
              >
                <Check
                  size={16}
                  className={cn(
                    'text-indigo-600 shrink-0',
                    currentTaskSchemaId === schemaId
                      ? 'opacity-100'
                      : 'opacity-0'
                  )}
                />
                <TaskSchemaBadgeContainer
                  schemaId={schemaId}
                  isActive={activeSchemaIds?.includes(schemaId)}
                />
              </CommandItem>
            ))}
          </CommandGroup>
        </CommandList>
      </div>
    </>
  );
}

type TaskSchemaCommandListsProps = {
  taskSchemaIds: TaskSchemaID[] | undefined;
  hiddenSchemaIds: TaskSchemaID[] | undefined;
  activeSchemaIds: TaskSchemaID[] | undefined;
  currentTaskSchemaId: TaskSchemaID | undefined;
  onTaskSchemaChange: (value: TaskSchemaID) => void;
  setOpen: (value: boolean) => void;
};

export function TaskSchemaCommandLists(props: TaskSchemaCommandListsProps) {
  const {
    taskSchemaIds,
    hiddenSchemaIds,
    activeSchemaIds,
    currentTaskSchemaId,
    onTaskSchemaChange,
    setOpen,
  } = props;

  if (
    (!taskSchemaIds || taskSchemaIds.length === 0) &&
    (!hiddenSchemaIds || hiddenSchemaIds.length === 0)
  )
    return null;

  return (
    <>
      {taskSchemaIds && taskSchemaIds.length > 0 && (
        <TaskSchemaCommandList
          title={'SCHEMAS'}
          taskSchemaIds={taskSchemaIds}
          currentTaskSchemaId={currentTaskSchemaId}
          activeSchemaIds={activeSchemaIds}
          onTaskSchemaChange={onTaskSchemaChange}
          setOpen={setOpen}
        />
      )}
      {hiddenSchemaIds && hiddenSchemaIds.length > 0 && (
        <TaskSchemaCommandList
          title={'ARCHIVED'}
          taskSchemaIds={hiddenSchemaIds}
          currentTaskSchemaId={currentTaskSchemaId}
          activeSchemaIds={activeSchemaIds}
          onTaskSchemaChange={onTaskSchemaChange}
          setOpen={setOpen}
          className={
            taskSchemaIds && taskSchemaIds.length > 0
              ? 'border-t border-gray-200 border-dashed'
              : undefined
          }
        />
      )}
      <Separator />
    </>
  );
}
