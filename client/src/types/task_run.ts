import { SchemaNodeType } from '@/lib/schemaUtils';
import { ReasoningStep, Run } from './workflowAI';
import { api__routers__runs_by_id__TranscriptionResponse } from './workflowAI';

export interface TaskRun extends Run {
  // id is actually always present in the TaskRun object
  id: string;
}

export type GeneralizedTaskInput = Record<string, unknown> | SchemaNodeType[];

// There are 2 `TranscriptionResponse` types backend side.
// The old one returns transcriptions by keypath for a given run, we should switch to the
// pure transcription call -> api__routers__transcriptions__TranscriptionResponse
export type RunTranscriptionResponse = api__routers__runs_by_id__TranscriptionResponse;

export type TaskOutput = Record<string, unknown>;

// An interface that merges both ToolCall from streamed chunks and final runs
export interface ToolCallPreview {
  id: string;
  name: string;
  status?: 'in_progress' | 'success' | 'failed';
  input_preview: string;
  output_preview?: string | null;
}

export interface StreamedChunk {
  output: Record<string, unknown> | undefined;
  toolCalls: Array<ToolCallPreview> | undefined;
  reasoningSteps: ReasoningStep[] | undefined;
}
