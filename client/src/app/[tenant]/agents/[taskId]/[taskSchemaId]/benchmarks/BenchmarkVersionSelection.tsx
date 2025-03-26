import { Cloud16Regular, FluentIcon, Star16Regular, TimelineRegular } from '@fluentui/react-icons';
import { isEmpty } from 'lodash';
import { useCallback, useMemo } from 'react';
import { TaskVersionBadgeContainer } from '@/components/TaskIterationBadge/TaskVersionBadgeContainer';
import { SquareCheckbox } from '@/components/v2/Checkbox';
import { environmentsForVersion } from '@/lib/versionUtils';
import { VersionsPerEnvironment } from '@/store/versions';
import { VersionV1 } from '@/types/workflowAI';
import { BenchmarkVersionEnvironments } from './BenchmarkVersionEnvironments';

type BenchmarkVersionSelectionItemProps = {
  version: VersionV1;
  isSelected: boolean;
  onToggleIteration: (iteration?: number) => Promise<void>;
  showEnvironments: boolean;
};

function BenchmarkVersionSelectionItem(props: BenchmarkVersionSelectionItemProps) {
  const { version, isSelected, onToggleIteration, showEnvironments } = props;

  const environments = useMemo(() => {
    return environmentsForVersion(version);
  }, [version]);

  return (
    <div key={version.id} className='pl-2.5 py-1 flex gap-2 items-center hover:bg-gray-100 rounded-[2px]'>
      <SquareCheckbox checked={isSelected} onClick={() => onToggleIteration(version.iteration)} />
      <TaskVersionBadgeContainer version={version} side='right' />
      {!!showEnvironments && <BenchmarkVersionEnvironments environments={environments} />}
    </div>
  );
}

type BenchmarkVersionSelectionSectionProps = {
  versions: VersionV1[];
  benchmarkIterations: Set<number> | undefined;
  updateBenchmarkIterations: (iterations: Set<number>) => Promise<void>;
  title: string;
  icon: FluentIcon;
  showEnvironments?: boolean;
};

function BenchmarkVersionSelectionSection(props: BenchmarkVersionSelectionSectionProps) {
  const {
    versions,
    benchmarkIterations,
    updateBenchmarkIterations,
    title,
    icon: Icon,
    showEnvironments = false,
  } = props;

  const onToggleIteration = useCallback(
    async (iteration?: number) => {
      if (!iteration) return;

      const newSet = new Set(benchmarkIterations);
      if (benchmarkIterations?.has(iteration) === true) {
        newSet.delete(iteration);
      } else {
        newSet.add(iteration);
      }

      await updateBenchmarkIterations(newSet);
    },
    [updateBenchmarkIterations, benchmarkIterations]
  );

  const isSelected = useCallback(
    (iteration?: number) => {
      if (!iteration) {
        return false;
      }
      return benchmarkIterations?.has(iteration) ?? false;
    },
    [benchmarkIterations]
  );

  const noVersionsYet = versions.length === 0;

  return (
    <div className={'flex flex-col w-full gap-2 py-2 border-b border-gray-200 border-dashed last:border-b-0'}>
      {noVersionsYet && <div className='pl-3 font-semibold text-gray-500 text-[13px]'>No Version Yet</div>}
      {!noVersionsYet && (
        <div className='flex flex-col px-1'>
          <div className='flex flex-row gap-2 px-2 text-[13px] font-semibold text-gray-700 items-center pb-1'>
            <Icon className='w-4 h-4 text-gray-500' />
            <div>{title}</div>
          </div>

          {versions.map((version) => (
            <BenchmarkVersionSelectionItem
              key={version.id}
              version={version}
              isSelected={isSelected(version.iteration)}
              onToggleIteration={onToggleIteration}
              showEnvironments={showEnvironments}
            />
          ))}
        </div>
      )}
    </div>
  );
}

type BenchmarkVersionSelectionProps = {
  versions: VersionV1[];
  versionsPerEnvironment: VersionsPerEnvironment | undefined;
  benchmarkIterations: Set<number> | undefined;
  updateBenchmarkIterations: (iterations: Set<number>) => Promise<void>;
};

export function BenchmarkVersionSelection(props: BenchmarkVersionSelectionProps) {
  const { versions, versionsPerEnvironment, benchmarkIterations, updateBenchmarkIterations } = props;

  const versionsWithEnvironments = useMemo(() => {
    if (isEmpty(versionsPerEnvironment)) {
      return undefined;
    }

    const result = new Set<VersionV1>();
    Object.values(versionsPerEnvironment).forEach((versions) => {
      if (!!versions) {
        versions.forEach((version) => {
          result.add(version);
        });
      }
    });
    return Array.from(result);
  }, [versionsPerEnvironment]);

  const favoriteVersions = useMemo(() => versions.filter((version) => version.is_favorite), [versions]);

  const restVersions = useMemo(
    () =>
      versions.filter((version) => !favoriteVersions.includes(version) && !versionsWithEnvironments?.includes(version)),
    [versionsWithEnvironments, favoriteVersions, versions]
  );

  const commonProps = {
    versionsPerEnvironment,
    benchmarkIterations,
    updateBenchmarkIterations,
  };

  return (
    <div className='flex flex-col w-full h-full overflow-auto font-lato'>
      {versionsWithEnvironments && versionsWithEnvironments.length > 0 && (
        <BenchmarkVersionSelectionSection
          {...commonProps}
          versions={versionsWithEnvironments}
          title='Deployed'
          icon={Cloud16Regular}
          showEnvironments
        />
      )}

      {favoriteVersions.length > 0 && (
        <BenchmarkVersionSelectionSection
          {...commonProps}
          versions={favoriteVersions}
          title={`Favorites (${favoriteVersions.length})`}
          icon={Star16Regular}
        />
      )}

      {restVersions.length > 0 && (
        <BenchmarkVersionSelectionSection
          {...commonProps}
          versions={restVersions}
          title='All Versions'
          icon={TimelineRegular}
        />
      )}
    </div>
  );
}
