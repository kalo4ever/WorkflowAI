'use client';

import * as amplitude from '@amplitude/analytics-browser';
import { BookFilled, ChatFilled, People16Filled } from '@fluentui/react-icons';
import { Plus } from 'lucide-react';
import Image from 'next/image';
import { usePathname, useRouter } from 'next/navigation';
import { useCallback, useEffect, useMemo } from 'react';
import GitHubSrc from '@/components/Images/GitHubIcon.png';
import { WorkflowAIIcon } from '@/components/Logos/WorkflowAIIcon';
import { Button } from '@/components/ui/Button';
import { ScrollArea } from '@/components/ui/ScrollArea';
import { SimpleTooltip } from '@/components/ui/Tooltip';
import { ExtendedBordersContainer } from '@/components/v2/ExtendedBordersContainer';
import { useAuth, useAuthUI } from '@/lib/AuthContext';
import {
  NEW_TASK_MODAL_OPEN,
  SUGGESTED_AGENTS_MODAL_OPEN,
  useQueryParamModal,
} from '@/lib/globalModal';
import { useDemoMode } from '@/lib/hooks/useDemoMode';
import { useRecentTasksHistory } from '@/lib/hooks/useRecentTasksHistory';
import { useLoggedInTenantID, useTaskParams } from '@/lib/hooks/useTaskParams';
import { detectPageIsUsingNewDesign } from '@/lib/pageDetection';
import { useParsedSearchParams } from '@/lib/queryString';
import {
  landingRoute,
  signUpRoute,
  taskRoute,
  taskSchemaRoute,
  tasksRoute,
} from '@/lib/routeFormatter';
import { getNewestSchemaId, isActiveTask } from '@/lib/taskUtils';
import { cn } from '@/lib/utils';
import { CURRENT_TENANT, useOrFetchTask, useOrFetchTasks } from '@/store';
import { TaskID, TaskSchemaID } from '@/types/aliases';
import { SerializableTask } from '@/types/workflowAI';
import { TasksSection } from '../../../components/TasksSection/TasksSection';
import { CreditsSection } from './CreditsSection';
import { SectionBlock, SectionItem, generateSections } from './SidebarSections';
import { UserMenu } from './userMenu';

export function SidebarLinks() {
  return (
    <div className='flex flex-row justify-between px-2.5 pb-2.5 pt-2.5 border-t border-gray-100 w-full overflow-hidden flex-shrink-0'>
      <SimpleTooltip
        content='Contact us at team@workflowai.support'
        tooltipDelay={100}
        tooltipClassName='m-1'
      >
        <Button
          variant='newDesignText'
          toRoute='mailto:team@workflowai.support'
          rel='noopener noreferrer'
          icon={<ChatFilled className='w-4 h-4' />}
          size='none'
          className='text-gray-700 hover:text-gray-700 hover:opacity-80 flex-shrink-0 w-7 h-7'
        />
      </SimpleTooltip>
      <SimpleTooltip
        content='Join our Community on GitHub'
        tooltipDelay={100}
        tooltipClassName='m-1'
      >
        <Button
          variant='newDesignText'
          toRoute='https://github.com/WorkflowAI/WorkflowAI/discussions'
          target='_blank'
          icon={<People16Filled className='w-[18px] h-[18px] text-gray-700' />}
          size='none'
          className='text-gray-700 hover:text-gray-700 hover:opacity-80 flex-shrink-0 w-7 h-7'
        />
      </SimpleTooltip>
      <SimpleTooltip content='Documentation' tooltipDelay={100}>
        <Button
          variant='newDesignText'
          toRoute='https://docs.workflowai.com/'
          target='_blank'
          rel='noopener noreferrer'
          icon={<BookFilled className='w-4 h-4' />}
          size='none'
          className='text-gray-700 hover:text-gray-700 hover:opacity-80 flex-shrink-0 w-7 h-7'
        />
      </SimpleTooltip>
      <SimpleTooltip content='Star on GitHub' tooltipDelay={100}>
        <Button
          variant='newDesignText'
          icon={<Image src={GitHubSrc} alt='GitHub' className='w-4 h-4' />}
          toRoute='https://github.com/WorkflowAI/workflowai'
          target='_blank'
          rel='noopener noreferrer'
          size='none'
          className='text-gray-700 hover:text-gray-700 hover:opacity-80 flex-shrink-0 w-7 h-7'
        />
      </SimpleTooltip>
    </div>
  );
}

export function Sidebar() {
  const { openModal: openNewTaskModal } =
    useQueryParamModal(NEW_TASK_MODAL_OPEN);

  const { openModal: openSuggestedAgentsModal } = useQueryParamModal(
    SUGGESTED_AGENTS_MODAL_OPEN
  );

  const { tenant, taskId, taskSchemaId } = useTaskParams();

  const { companyURL } = useParsedSearchParams('companyURL');

  const loggedInTenant = useLoggedInTenantID() ?? tenant;

  const { tasks, isInitialized } = useOrFetchTasks(
    loggedInTenant ?? CURRENT_TENANT
  );
  const { task: currentTask } = useOrFetchTask(tenant, taskId);

  const router = useRouter();

  const { recentTasks: recentTasksEntries, addRecentTask } =
    useRecentTasksHistory(tenant);

  useEffect(() => {
    if (!!taskId && !!taskSchemaId) {
      addRecentTask(taskId, taskSchemaId);
    }
  }, [taskId, taskSchemaId, addRecentTask]);

  const onTryInPlayground = useCallback(
    (task: SerializableTask, taskSchemaId?: TaskSchemaID) => {
      if (!!taskSchemaId) {
        router.push(taskSchemaRoute(tenant, task.id as TaskID, taskSchemaId));
      } else {
        router.push(taskRoute(tenant, task.id as TaskID));
      }
    },
    [router, tenant]
  );

  const pathname = usePathname();

  const { isSignedIn, user, hasOrganization } = useAuth();

  const { isInDemoMode, isLoggedOut } = useDemoMode();

  const onNewTask = useCallback(() => {
    if (isLoggedOut && !!companyURL) {
      openSuggestedAgentsModal();
    } else {
      amplitude.track('user.clicked.new_task');
      openNewTaskModal({
        mode: 'new',
        redirectToPlaygrounds: 'true',
      });
    }
  }, [openNewTaskModal, openSuggestedAgentsModal, companyURL, isLoggedOut]);

  const { openUserProfile, openOrganizationProfile, signOut } = useAuthUI();

  const routeBuilderWrapper = useCallback(
    (routeBuilder: SectionItem['routeBuilder']) => {
      if (!routeBuilder) {
        return tasksRoute(loggedInTenant, { [NEW_TASK_MODAL_OPEN]: true });
      }

      if (!!taskId) {
        const schemaId = taskSchemaId ?? getNewestSchemaId(currentTask);

        if (!!schemaId) {
          return routeBuilder(tenant, taskId, schemaId);
        }
      }

      if (!tasks || tasks.length === 0) {
        return tasksRoute(loggedInTenant, { [NEW_TASK_MODAL_OPEN]: true });
      }

      const defaultTask = tasks[0];
      const defaultTaskId = defaultTask.id as TaskID;
      const defaultTaskSchemaId = getNewestSchemaId(defaultTask);

      return routeBuilder(loggedInTenant, defaultTaskId, defaultTaskSchemaId);
    },
    [loggedInTenant, taskId, taskSchemaId, tasks, tenant, currentTask]
  );

  const showActivityIndicator = useMemo(() => {
    return isActiveTask(currentTask);
  }, [currentTask]);

  const sections = useMemo(() => {
    return generateSections(showActivityIndicator, isInDemoMode);
  }, [showActivityIndicator, isInDemoMode]);

  const useNewDesign = useMemo(() => {
    return detectPageIsUsingNewDesign(pathname);
  }, [pathname]);

  const routeForSignUp = signUpRoute();

  const routeForLogo = useMemo(() => {
    if (isLoggedOut) {
      return landingRoute({ companyURL });
    }

    return tasksRoute(tenant);
  }, [tenant, isLoggedOut, companyURL]);

  return (
    <div
      className={cn(
        'h-full font-lato flex',
        useNewDesign ? 'pl-6 pt-6 pb-6' : 'p-6'
      )}
    >
      <ExtendedBordersContainer
        className='flex-1 flex flex-col w-[172px]'
        borderColor='gray-100'
        margin={24}
      >
        {!!taskId ? (
          <>
            <Button variant='text' size='none' toRoute={routeForLogo}>
              <div className='flex items-center gap-2 px-[10px] py-[10px] flex-shrink-0'>
                <WorkflowAIIcon ratio={1.3} />
                <span className='font-sans text-[20px] bg-gradient-to-r from-[#8759E3] to-[#4235F8] text-transparent bg-clip-text'>
                  <span className='font-semibold'>Workflow</span>
                  <span className='font-normal'>AI</span>
                </span>
              </div>
            </Button>
            <ScrollArea className='flex-1'>
              <div className='flex flex-col gap-3'>
                {sections.map((section) => (
                  <SectionBlock
                    key={section.title}
                    title={section.title}
                    items={section.items}
                    showActivityIndicator={section.showActivityIndicator}
                    pathname={pathname}
                    routeBuilderWrapper={routeBuilderWrapper}
                  />
                ))}
              </div>
            </ScrollArea>
          </>
        ) : (
          <>
            <TasksSection
              tasks={tasks}
              recentTasksEntries={recentTasksEntries}
              isInitialized={isInitialized}
              onTryInPlayground={onTryInPlayground}
            />
          </>
        )}
        {isLoggedOut ? (
          <>
            <div className='px-2.5 w-full'>
              <Button
                className='w-full mt-3'
                variant='newDesignIndigo'
                icon={<Plus className='h-4 w-4' strokeWidth={2} />}
                onClick={onNewTask}
              >
                New
              </Button>
            </div>
            <div className='pb-6 px-2.5'>
              <Button
                className='w-full mt-3'
                variant='newDesignIndigo'
                toRoute={routeForSignUp}
              >
                Create Account
              </Button>
            </div>
          </>
        ) : (
          <>
            <div className='pb-3 px-2.5'>
              <Button
                className='w-full mt-3'
                variant='newDesignIndigo'
                icon={<Plus className='h-4 w-4' strokeWidth={2} />}
                onClick={onNewTask}
              >
                New
              </Button>
            </div>

            <div className='px-2.5 pb-2.5'>
              <div className='flex flex-col items-center w-full border rounded-[2px] border-gray-300 shadow-sm'>
                <UserMenu
                  user={user}
                  hasOrganization={hasOrganization}
                  openUserProfile={openUserProfile}
                  openOrganizationProfile={openOrganizationProfile}
                  signOut={signOut}
                />
                <CreditsSection tenant={tenant} isSignedIn={!!isSignedIn} />
              </div>
            </div>
          </>
        )}
        <SidebarLinks />
      </ExtendedBordersContainer>
    </div>
  );
}
