'use client';

import { useCallback, useMemo } from 'react';
import { Loader } from '@/components/ui/Loader';
import { PageContainer } from '@/components/v2/PageContainer';
import { useTaskSchemaParams } from '@/lib/hooks/useTaskParams';
import {
  useParsedSearchParams,
  useRedirectWithParams,
} from '@/lib/queryString';
import { useOrFetchTask, useOrFetchVersions } from '@/store';
import { VersionEntryContainer } from './VersionEntryContainer';
import { VersionFilterPicker } from './VersionFilterPicker';
import { filterVersions, numberOfVersions } from './utils';

export default function VersionsContainer() {
  const { tenant, taskId, taskSchemaId } = useTaskSchemaParams();

  const { task, isInitialized: isTaskInitialized } = useOrFetchTask(
    tenant,
    taskId
  );

  const {
    majorVersions,
    versions,
    isInitialized: areVersionsInitialized,
  } = useOrFetchVersions(tenant, taskId, taskSchemaId, true);

  const { filter } = useParsedSearchParams('filter');

  const filterOption: 'deployed' | 'favorite' | undefined = useMemo(() => {
    if (!filter) return undefined;
    switch (filter) {
      case 'deployed':
        return 'deployed';
      case 'favorites':
      case 'favorite':
        return 'favorite';
      default:
        return undefined;
    }
  }, [filter]);

  const redirectWithParams = useRedirectWithParams();

  const setFilterOption = useCallback(
    (filter: 'deployed' | 'favorite' | undefined) => {
      redirectWithParams({
        params: { filter },
      });
    },
    [redirectWithParams]
  );

  const allEntries = useMemo(
    () =>
      filterVersions({
        majorVersions,
        versions,
        filterOption: undefined,
      }),
    [majorVersions, versions]
  );

  const latestMajor = useMemo(() => {
    return allEntries[0]?.majorVersion.major;
  }, [allEntries]);

  const deployedEntries = useMemo(
    () =>
      filterVersions({
        majorVersions,
        versions,
        filterOption: 'deployed',
      }),
    [majorVersions, versions]
  );

  const favoriteEntries = useMemo(
    () =>
      filterVersions({
        majorVersions,
        versions,

        filterOption: 'favorite',
      }),
    [majorVersions, versions]
  );

  const entries = useMemo(() => {
    switch (filterOption) {
      case 'deployed':
        return deployedEntries;
      case 'favorite':
        return favoriteEntries;
      default:
        return allEntries;
    }
  }, [filterOption, deployedEntries, favoriteEntries, allEntries]);

  if (!areVersionsInitialized || !task) {
    return <Loader centered />;
  }

  return (
    <PageContainer
      task={task}
      isInitialized={isTaskInitialized}
      name='Versions'
      showCopyLink={false}
      rightBarChildren={
        <VersionFilterPicker
          schema_id={taskSchemaId}
          numberOfAllVersions={numberOfVersions(allEntries)}
          numberOfDeployedVersions={numberOfVersions(deployedEntries)}
          numberOfFavoriteVersions={numberOfVersions(favoriteEntries)}
          filterOption={filterOption}
          setFilterOption={setFilterOption}
        />
      }
    >
      <div className='flex flex-col h-full w-full overflow-y-auto font-lato px-4 py-4 gap-4'>
        {entries.map((entry, index) => (
          <VersionEntryContainer
            key={entry.majorVersion.major}
            entry={entry}
            previousEntry={entries[index + 1]}
            isLatest={entry.majorVersion.major === latestMajor}
            tenant={tenant}
            taskId={taskId}
            taskSchemaId={taskSchemaId}
            openSchemasByDefault={index === 0}
          />
        ))}
      </div>
    </PageContainer>
  );
}
