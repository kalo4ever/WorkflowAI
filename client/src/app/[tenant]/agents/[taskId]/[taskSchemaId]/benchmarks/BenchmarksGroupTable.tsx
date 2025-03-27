import { useCallback, useMemo, useState } from 'react';
import { TableView, TableViewHeaderEntry } from '@/components/ui/TableView';
import { VersionResult, VersionV1 } from '@/types/workflowAI';
import { BenchmarkRow } from './BenchmarkRow';
import { BenchmarkBestPicks, BenchmarkResultsSortKey, sortBenchmarkResults } from './utils';

type BenchmarksGroupTableProps = {
  versionByIteration: Record<number, VersionV1>;
  benchmarkResults: VersionResult[];
  bestOnes: BenchmarkBestPicks;
  onClone: (versionId: string) => void;
  onTryInPlayground: (versionId: string) => void;
  onViewCode: (version: VersionV1) => void;
  onDeploy: (versionId: string | undefined) => void;
  onOpenTaskRuns: (version: string, state: 'positive' | 'negative' | 'unsure') => void;
  findIconURLForModel: (name?: string) => string | undefined;
  isInDemoMode: boolean;
};

export function BenchmarksGroupTable(props: BenchmarksGroupTableProps) {
  const {
    benchmarkResults,
    versionByIteration,
    bestOnes,
    onClone,
    onTryInPlayground,
    onViewCode,
    onDeploy,
    onOpenTaskRuns,
    findIconURLForModel,
    isInDemoMode,
  } = props;

  const [sortMode, setSortMode] = useState<BenchmarkResultsSortKey>(BenchmarkResultsSortKey.Score);

  const [revertSortOrder, setRevertSortOrder] = useState(false);
  const sortedBenchmarkResults = useMemo(() => {
    const result = sortBenchmarkResults(benchmarkResults, sortMode);
    if (revertSortOrder) {
      return result.reverse();
    }
    return result;
  }, [benchmarkResults, sortMode, revertSortOrder]);

  const onSortModeChange = useCallback(
    (mode: BenchmarkResultsSortKey) => {
      if (sortMode === mode) {
        setRevertSortOrder((prev) => !prev);
        return;
      }

      setRevertSortOrder(false);
      setSortMode(mode);
    },
    [sortMode, setSortMode, setRevertSortOrder]
  );

  return (
    <div className='flex w-full p-4'>
      <TableView
        maxContentHeight={300}
        headers={
          <>
            <TableViewHeaderEntry
              title='Version'
              onClick={() => onSortModeChange(BenchmarkResultsSortKey.Version)}
              className='pl-2 min-w-[84px]'
            />
            <TableViewHeaderEntry
              title='Model'
              onClick={() => onSortModeChange(BenchmarkResultsSortKey.Model)}
              className='w-[300px] shrink-0'
            />
            <TableViewHeaderEntry
              title='Reviews'
              onClick={() => onSortModeChange(BenchmarkResultsSortKey.Score)}
              className='flex-1 min-w-[110px]'
            />
            <TableViewHeaderEntry
              title='Accuracy %'
              onClick={() => onSortModeChange(BenchmarkResultsSortKey.Score)}
              className='flex-1 min-w-[110px]'
            />
            <TableViewHeaderEntry
              title='Price per 1k'
              onClick={() => onSortModeChange(BenchmarkResultsSortKey.Price)}
              className='flex-1 min-w-[110px]'
            />
            <TableViewHeaderEntry
              title='Latency'
              onClick={() => onSortModeChange(BenchmarkResultsSortKey.Latency)}
              className='flex-1 min-w-[110px]'
            />
          </>
        }
      >
        {sortedBenchmarkResults.map((result) => {
          return (
            <BenchmarkRow
              key={result.iteration}
              benchmarkResult={result}
              version={versionByIteration[result.iteration]}
              iconURL={findIconURLForModel(versionByIteration[result.iteration]?.model)}
              isBestPrice={!!result.iteration ? bestOnes.bestPriceVersions.includes(result.iteration) : false}
              isBestDuration={!!result.iteration ? bestOnes.bestDurationVersions.includes(result.iteration) : false}
              isBestScore={!!result.iteration ? bestOnes.bestScoreVersions.includes(result.iteration) : false}
              onClone={onClone}
              onTryInPlayground={onTryInPlayground}
              onViewCode={onViewCode}
              onDeploy={onDeploy}
              onOpenTaskRuns={onOpenTaskRuns}
              isInDemoMode={isInDemoMode}
            />
          );
        })}
      </TableView>
    </div>
  );
}
