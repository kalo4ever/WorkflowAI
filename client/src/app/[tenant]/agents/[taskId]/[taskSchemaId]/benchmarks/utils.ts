import { VersionResult } from '@/types/workflowAI';

export type BenchmarkBestPicks = {
  bestScoreVersions: number[];
  bestDurationVersions: number[];
  bestPriceVersions: number[];
};

function pickBestOneYet(
  newValue: number | undefined | null,
  newKey: number,

  bestValue: number | undefined,
  bestKeys: number[],

  ascending: boolean
): { value: number | undefined; keys: number[] } {
  if (!newValue) {
    return { value: bestValue, keys: bestKeys };
  }

  if (!bestValue) {
    return { value: newValue, keys: [newKey] };
  }

  if ((ascending && newValue < bestValue) || (!ascending && newValue > bestValue)) {
    return { value: newValue, keys: [newKey] };
  }

  if (newValue === bestValue) {
    return { value: newValue, keys: [...bestKeys, newKey] };
  }

  return { value: bestValue, keys: bestKeys };
}

export function findScore(result: VersionResult): number {
  const totalReviews = result.positive_review_count + result.negative_review_count + result.unsure_review_count;

  if (totalReviews === 0) {
    return 0;
  }

  return Math.max(0, Math.min(1, result.positive_review_count / totalReviews));
}

export function findBestOnes(results: VersionResult[]): BenchmarkBestPicks {
  let bestScoreKeys: number[] = [];
  let bestDurationKeys: number[] = [];
  let bestPriceKeys: number[] = [];

  let bestScore: number | undefined;
  let bestDuration: number | undefined;
  let bestPrice: number | undefined;

  results.forEach((result) => {
    if (!result.iteration) {
      return;
    }

    const bestScoreResult = pickBestOneYet(findScore(result), result.iteration, bestScore, bestScoreKeys, false);
    bestScore = bestScoreResult.value;
    bestScoreKeys = bestScoreResult.keys;

    const bestDurationResult = pickBestOneYet(
      result.average_duration_seconds,
      result.iteration,
      bestDuration,
      bestDurationKeys,
      true
    );
    bestDuration = bestDurationResult.value;
    bestDurationKeys = bestDurationResult.keys;

    const bestPriceResult = pickBestOneYet(result.average_cost_usd, result.iteration, bestPrice, bestPriceKeys, true);
    bestPrice = bestPriceResult.value;
    bestPriceKeys = bestPriceResult.keys;
  });

  return {
    bestScoreVersions: bestScoreKeys,
    bestDurationVersions: bestDurationKeys,
    bestPriceVersions: bestPriceKeys,
  };
}

export function compareBenchmarkValues(
  lhs: number | undefined | null,
  rhs: number | undefined | null,
  alternativeResult?: number,
  ascending: boolean = true
): number {
  if (!lhs && !rhs && alternativeResult !== undefined) {
    return alternativeResult;
  }

  if (!lhs) {
    return 1;
  }

  if (!rhs) {
    return -1;
  }

  if (lhs === rhs && alternativeResult !== undefined) {
    return alternativeResult;
  }

  if (ascending) {
    return lhs - rhs;
  } else {
    return rhs - lhs;
  }
}

export enum BenchmarkResultsSortKey {
  Version = 'version',
  Price = 'price',
  Score = 'score',
  Latency = 'latency',
  Model = 'model',
}

export function sortBenchmarkResults(results: VersionResult[], sortMode: BenchmarkResultsSortKey): VersionResult[] {
  switch (sortMode) {
    case BenchmarkResultsSortKey.Version:
      return results.toSorted((lhs, rhs) => {
        if (!lhs.iteration || !rhs.iteration) {
          return 0;
        }
        return rhs.iteration - lhs.iteration;
      });

    case BenchmarkResultsSortKey.Model:
      return results.toSorted((lhs, rhs) => {
        if (!lhs.properties?.model || !rhs.properties?.model) {
          return 0;
        }
        return lhs.properties.model.localeCompare(rhs.properties.model);
      });

    case BenchmarkResultsSortKey.Price:
      return results.toSorted((lhs, rhs) => {
        if (!lhs.iteration || !rhs.iteration) {
          return 0;
        }

        return compareBenchmarkValues(lhs.average_cost_usd, rhs.average_cost_usd, lhs.iteration - rhs.iteration);
      });

    case BenchmarkResultsSortKey.Score:
      return results.toSorted((lhs, rhs) => {
        if (!lhs.iteration || !rhs.iteration) {
          return 0;
        }

        return compareBenchmarkValues(
          findScore(lhs),
          findScore(rhs),
          compareBenchmarkValues(lhs.average_cost_usd, rhs.average_cost_usd, lhs.iteration - rhs.iteration),
          false
        );
      });

    case BenchmarkResultsSortKey.Latency:
      return results.toSorted((lhs, rhs) => {
        if (!lhs.iteration || !rhs.iteration) {
          return 0;
        }
        return compareBenchmarkValues(
          lhs.average_duration_seconds,
          rhs.average_duration_seconds,
          lhs.iteration - rhs.iteration
        );
      });

    default:
      return results;
  }
}
