import { cx } from 'class-variance-authority';
import { Loader2 } from 'lucide-react';
import Image from 'next/image';
import { useCallback, useMemo } from 'react';
import { TaskVersionBadgeContainer } from '@/components/TaskIterationBadge/TaskVersionBadgeContainer';
import { TaskVersionTooltip } from '@/components/v2/TaskVersions/TaskVersionTooltip';
import { environmentsForVersion, formatSemverVersion } from '@/lib/versionUtils';
import { VersionResult, VersionV1 } from '@/types/workflowAI';
import { BenchmarkReviewsEntry } from './BenchmarkReviewsEntry';
import { BenchmarkVersionEnvironments } from './BenchmarkVersionEnvironments';
import { findScore } from './utils';

type ReviewsViewProps = {
  review: VersionResult;
  onClick: (state: 'positive' | 'negative' | 'unsure') => void;
};

function ReviewsView(props: ReviewsViewProps) {
  const { review, onClick } = props;
  return (
    <div className='flex flex-row gap-2 font-lato items-center'>
      <BenchmarkReviewsEntry
        count={review.positive_review_count}
        state='positive'
        onClick={() => onClick('positive')}
        userCount={review.positive_user_review_count}
        aiCount={review.positive_review_count - review.positive_user_review_count}
        alwaysShowCount={true}
      />
      <BenchmarkReviewsEntry
        count={review.negative_review_count}
        state='negative'
        onClick={() => onClick('negative')}
        userCount={review.negative_user_review_count}
        aiCount={review.negative_review_count - review.negative_user_review_count}
        alwaysShowCount={true}
      />
      <BenchmarkReviewsEntry count={review.unsure_review_count} state='unsure' onClick={() => onClick('unsure')} />
      {review.in_progress_review_count > 0 && <Loader2 className='h-4 w-4 animate-spin text-gray-400' />}
    </div>
  );
}

type ValueViewProps = {
  value: string | number | undefined;
  highlighted?: boolean;
  isLoading?: boolean;
};

function ValueView(props: ValueViewProps) {
  const { value, highlighted = false, isLoading = false } = props;
  return (
    <div className='flex flex-row gap-1 items-center'>
      <div
        className={cx(
          'text-gray-700 text-[13px] font-medium px-1.5 py-0.5 rounded-[2px] w-fit font-lato',
          highlighted && 'bg-green-100 border border-green-200'
        )}
      >
        {value ?? '-'}
      </div>
      {isLoading && <Loader2 className='h-4 w-4 animate-spin text-gray-400' />}
    </div>
  );
}

type BenchmarkRowProps = {
  benchmarkResult: VersionResult;
  version: VersionV1 | undefined;
  iconURL: string | undefined;
  isBestPrice: boolean;
  isBestDuration: boolean;
  isBestScore: boolean;
  onClone: (versionId: string) => void;
  onTryInPlayground: (versionId: string) => void;
  onViewCode: (version: VersionV1) => void;
  onDeploy: (versionId: string | undefined) => void;
  onOpenTaskRuns: (version: string, state: 'positive' | 'negative' | 'unsure') => void;
  isInDemoMode: boolean;
};

export function BenchmarkRow(props: BenchmarkRowProps) {
  const {
    version,
    iconURL,
    benchmarkResult,
    isBestPrice,
    isBestDuration,
    isBestScore,
    onClone,
    onTryInPlayground,
    onViewCode,
    onDeploy,
    onOpenTaskRuns,
    isInDemoMode,
  } = props;
  const environments = useMemo(() => environmentsForVersion(version), [version]);

  const onOpenTaskRunsTapped = useCallback(
    (state: 'positive' | 'negative' | 'unsure') => {
      if (!version) {
        return;
      }

      const badgeText = formatSemverVersion(version);

      if (!badgeText) {
        return;
      }

      onOpenTaskRuns(badgeText, state);
    },
    [onOpenTaskRuns, version]
  );

  if (!version) {
    return null;
  }

  const cost = benchmarkResult.average_cost_usd;
  const duration = benchmarkResult.average_duration_seconds;
  const accuracy = findScore(benchmarkResult);

  return (
    <TaskVersionTooltip
      key={benchmarkResult.iteration}
      onClone={() => onClone(version.id)}
      onTryInPlayground={() => onTryInPlayground(version.id)}
      onViewCode={() => onViewCode(version)}
      onDeploy={() => onDeploy(version.id)}
      isInDemoMode={isInDemoMode}
    >
      <div className='flex flex-row py-2.5 rounded-[2px] hover:bg-gray-100/60 items-center'>
        <div className='flex flex-row gap-2 items-start justify-between min-w-[84px]'>
          <div className='flex flex-row gap-2 items-center pl-2'>
            <TaskVersionBadgeContainer version={version} side='right' />
          </div>
        </div>
        <div className='flex flex-row gap-2 items-center justify-start w-[300px] shrink-0 h-full'>
          <div className='flex flex-row gap-2 items-center mr-2'>
            {!!environments && environments.length > 0 && <BenchmarkVersionEnvironments environments={environments} />}
            {!!iconURL && (
              <Image src={iconURL} alt='' width={14} height={14} className='w-[14px] h-[14px] flex-shrink-0' />
            )}
            {!!version.model && <div className='truncate text-gray-700 text-[13px] font-normal'>{version.model}</div>}
          </div>
        </div>
        <div className='flex-1 min-w-[110px]'>
          <ReviewsView review={benchmarkResult} onClick={(state) => onOpenTaskRunsTapped(state)} />
        </div>
        <div className='flex-1 min-w-[110px]'>
          <ValueView
            value={`${(accuracy * 100).toFixed(0)}%`}
            highlighted={isBestScore}
            isLoading={benchmarkResult.in_progress_review_count > 0}
          />
        </div>
        <div className='flex-1 min-w-[110px]'>
          <ValueView
            value={!!cost ? `$${(cost * 1000).toFixed(2)}` : undefined}
            highlighted={isBestPrice}
            isLoading={benchmarkResult.in_progress_review_count > 0}
          />
        </div>
        <div className='flex-1 min-w-[110px]'>
          <ValueView
            value={!!duration ? `${duration.toFixed(2)}s` : undefined}
            highlighted={isBestDuration}
            isLoading={benchmarkResult.in_progress_review_count > 0}
          />
        </div>
      </div>
    </TaskVersionTooltip>
  );
}
