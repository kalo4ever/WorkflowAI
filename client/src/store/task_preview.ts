import { enableMapSet, produce } from 'immer';
import { create } from 'zustand';
import { SSEClient } from '@/lib/api/client';
import { Method } from '@/lib/api/client';
import { TaskSchemaID, TenantID } from '@/types/aliases';
import {
  ChatMessage,
  GenerateTaskPreviewRequest,
  TaskPreview,
} from '@/types/workflowAI';
import { buildTaskPreviewScopeKey, rootTaskPathNoProxy } from './utils';

enableMapSet();

interface TaskPreviewState {
  generatedInputByScope: Map<string, Record<string, unknown>>;
  generatedOutputByScope: Map<string, Record<string, unknown>>;
  finalGeneratedInputByScope: Map<string, Record<string, unknown>>;
  finalGeneratedOutputByScope: Map<string, Record<string, unknown>>;
  isLoadingByScope: Map<string, boolean>;
  isInitialiazedByScope: Map<string, boolean>;
  inputBySchemaId: Map<TaskSchemaID, Record<string, unknown>>;
  outputBySchemaId: Map<TaskSchemaID, Record<string, unknown>>;

  generateTaskPreview(
    tenant: TenantID | undefined,
    chatMessages: ChatMessage[] | undefined,
    inputSchema: Record<string, unknown>,
    outputSchema: Record<string, unknown>,
    currentInputPreview: Record<string, unknown> | undefined,
    currentOutputPreview: Record<string, unknown> | undefined,
    token: string | undefined
  ): Promise<void>;

  saveTaskPreview(
    schemaID: TaskSchemaID,
    input: Record<string, unknown> | undefined,
    output: Record<string, unknown> | undefined
  ): Promise<void>;
}

export const useTaskPreview = create<TaskPreviewState>((set, get) => ({
  generatedInputByScope: new Map(),
  generatedOutputByScope: new Map(),
  finalGeneratedInputByScope: new Map(),
  finalGeneratedOutputByScope: new Map(),
  isLoadingByScope: new Map(),
  isInitialiazedByScope: new Map(),
  inputBySchemaId: new Map(),
  outputBySchemaId: new Map(),

  saveTaskPreview: async (
    schemaId: TaskSchemaID,
    input: Record<string, unknown> | undefined,
    output: Record<string, unknown> | undefined
  ): Promise<void> => {
    set(
      produce((state: TaskPreviewState) => {
        if (input === undefined) {
          state.inputBySchemaId.delete(schemaId);
        } else {
          state.inputBySchemaId.set(schemaId, input);
        }

        if (output === undefined) {
          state.outputBySchemaId.delete(schemaId);
        } else {
          state.outputBySchemaId.set(schemaId, output);
        }
      })
    );
  },

  generateTaskPreview: async (
    tenant: TenantID | undefined,
    chatMessages: ChatMessage[] | undefined,
    inputSchema: Record<string, unknown>,
    outputSchema: Record<string, unknown>,
    previousInputPreview: Record<string, unknown> | undefined,
    previousOutputPreview: Record<string, unknown> | undefined,
    token: string | undefined
  ): Promise<void> => {
    const scopeKey = buildTaskPreviewScopeKey({
      inputSchema,
      outputSchema,
    });

    if (get().isLoadingByScope.get(scopeKey)) return;

    set(
      produce((state: TaskPreviewState) => {
        state.isLoadingByScope.set(scopeKey, true);
      })
    );

    const onMessage = (message: { preview: TaskPreview }) => {
      set(
        produce((state: TaskPreviewState) => {
          state.generatedInputByScope.set(scopeKey, message.preview.input);
          state.generatedOutputByScope.set(scopeKey, message.preview.output);
        })
      );
    };

    try {
      const currentPreview: TaskPreview | undefined =
        previousInputPreview && previousOutputPreview
          ? {
              input: previousInputPreview,
              output: previousOutputPreview,
            }
          : undefined;

      const request: GenerateTaskPreviewRequest = {
        chat_messages: chatMessages ?? [],
        task_input_schema: inputSchema,
        task_output_schema: outputSchema,
        current_preview: currentPreview,
      };

      const result = await SSEClient<
        GenerateTaskPreviewRequest,
        { preview: TaskPreview }
      >(
        `${rootTaskPathNoProxy(tenant)}/schemas/preview`,
        Method.POST,
        token,
        request,
        onMessage
      );

      set(
        produce((state: TaskPreviewState) => {
          state.generatedInputByScope.set(scopeKey, result.preview.input);
          state.generatedOutputByScope.set(scopeKey, result.preview.output);
          state.finalGeneratedInputByScope.set(scopeKey, result.preview.input);
          state.finalGeneratedOutputByScope.set(
            scopeKey,
            result.preview.output
          );
        })
      );
    } catch (error) {
      console.error('Failed to generate schema preview', error);
    }

    set(
      produce((state: TaskPreviewState) => {
        state.isLoadingByScope.set(scopeKey, false);
        state.isInitialiazedByScope.set(scopeKey, true);
      })
    );
    return;
  },
}));
