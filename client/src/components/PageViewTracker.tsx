'use client';

import * as amplitude from '@amplitude/analytics-browser';
import { usePathname } from 'next/navigation';
import { ReactNode, useEffect } from 'react';
import { detectDevice } from '@/lib/detectDevice';
import { useTaskParams } from '@/lib/hooks/useTaskParams';
import { detectPage } from '@/lib/pageDetection';
import { useOrFetchTask } from '@/store';
import { SerializableTask } from '@/types/workflowAI';
import { useAuth } from '../lib/AuthContext';

function checkTaskVisibility(task: SerializableTask | undefined): 'public' | 'private' | undefined {
  if (!task) {
    return undefined;
  }
  return !!task.is_public ? 'public' : 'private';
}

interface PageViewTrackerProps {
  children: ReactNode;
}

export function PageViewTracker(props: PageViewTrackerProps) {
  const { children } = props;

  const pathname = usePathname();
  const { tenant, taskId } = useTaskParams();
  const { isSignedIn } = useAuth();
  const { task } = useOrFetchTask(tenant, taskId);

  const taskOrganizationNameTaskName = `${tenant ?? ''}/${taskId ?? ''}`;

  const taskVisibility = checkTaskVisibility(task);

  useEffect(() => {
    if (isSignedIn === undefined) {
      // Before sending the event let's first get the signed in status
      return;
    }

    if (taskId !== undefined) {
      // In case the page is for a Task, let's wait for the data about the task before sending the event
      if (taskVisibility === undefined) {
        return;
      }
    }

    const userDevice = detectDevice();
    const pageSection = detectPage(pathname);

    amplitude.track('user.viewed.webpage', {
      url_path: window.location.href,
      task_organization_id: tenant,
      task_organization_name_task_name: taskOrganizationNameTaskName,
      user_logged_in: isSignedIn,
      task_visibility: taskVisibility,
      user_device: userDevice,
      page_section: pageSection,
    });
  }, [tenant, pathname, isSignedIn, taskOrganizationNameTaskName, taskVisibility, taskId]);

  return <>{children}</>;
}
