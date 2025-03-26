'use client';

import { useRouter } from 'next/navigation';
import { useCallback } from 'react';
import { useHotkeys } from 'react-hotkeys-hook';
import { LuBook } from 'react-icons/lu';
import { useToggle } from 'usehooks-ts';
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from '@/components/ui/Command';
import { useDefaultRedirectRoute } from '@/lib/hooks/useTaskParams';
import { taskSchemaRoute } from '@/lib/routeFormatter';
import { getNewestSchemaId } from '@/lib/taskUtils';
import { useOrFetchTasks } from '@/store';
import { TaskID, TaskSchemaID, TenantID } from '@/types/aliases';

export function CommandK(props: { tenant: TenantID }) {
  const { tenant } = props;
  const { tasks } = useOrFetchTasks(tenant);
  const defaultRoute = useDefaultRedirectRoute();

  const [open, toggleOpen] = useToggle(false);
  const router = useRouter();
  useHotkeys('meta+k', () => toggleOpen());

  const redirectTo = useCallback(
    (path: string) => {
      toggleOpen();
      router.push(path);
    },
    [toggleOpen, router]
  );

  return (
    <CommandDialog open={open} onOpenChange={toggleOpen}>
      <CommandInput placeholder='Type a command or search...' />
      <CommandList>
        <CommandEmpty>No results found.</CommandEmpty>
        <CommandGroup heading='AI Agents'>
          {tasks.map((task) => (
            <CommandItem
              key={task.name}
              onSelect={() => {
                // Redirect to the first schema of the task
                // if it exists
                if (!task.versions.length) {
                  return;
                }
                const schemaId = getNewestSchemaId(task);
                redirectTo(taskSchemaRoute(tenant, task.id as TaskID, `${schemaId}` as TaskSchemaID));
              }}
            >
              <LuBook className='mr-2 h-4 w-4' />
              <span>{task.name}</span>
            </CommandItem>
          ))}
          <CommandItem onSelect={() => redirectTo(defaultRoute)}>
            <LuBook className='mr-2 h-4 w-4' />
            <span>All tasks</span>
          </CommandItem>
        </CommandGroup>
      </CommandList>
    </CommandDialog>
  );
}
