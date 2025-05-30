import { TaskRun } from '@/types';

export type ContextWindowInformation = {
  inputTokens: string;
  outputTokens: string;
  percentage: string;
};

function formatTokenCount(count: number): string {
  if (count >= 1000) {
    return `${(count / 1000).toFixed(1)}k`;
  }
  return count.toFixed(0).toString();
}

export function getContextWindowInformation(taskRun: TaskRun | undefined): ContextWindowInformation | undefined {
  if (!taskRun) {
    return undefined;
  }

  const usage = taskRun.llm_completions?.[0].usage;

  if (!usage || !usage.prompt_token_count || !usage.completion_token_count || !usage.model_context_window_size) {
    return undefined;
  }

  const percentage = (usage.prompt_token_count + usage.completion_token_count) / usage.model_context_window_size;

  return {
    inputTokens: formatTokenCount(usage.prompt_token_count),
    outputTokens: formatTokenCount(usage.completion_token_count),
    percentage: `${Math.round(percentage * 100)}%`,
  };
}
