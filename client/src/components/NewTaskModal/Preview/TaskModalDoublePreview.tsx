import { useState } from 'react';
import { useEffect, useMemo } from 'react';
import { WORKFLOW_AI_USERNAME } from '@/lib/constants';
import { useOrFetchTaskPreview } from '@/store/fetchers';
import { TenantID } from '@/types/aliases';
import { TaskSchemaID } from '@/types/aliases';
import { JsonSchema } from '@/types/json_schema';
import { ChatMessage } from '@/types/workflowAI';
import { ConversationMessage } from '../TaskConversationMessage';
import { TaskModalInProgressHeader } from './TaskModalInProgressHeader';
import { TaskModalPreviewContent } from './TaskModalPreviewContent';

type TaskModalDoublePreviewProps = {
  tenant: TenantID;
  taskSchemaId: TaskSchemaID;
  loading: boolean;
  messages: ConversationMessage[];
  noChangesDetected: boolean;
  token: string | undefined;
  className?: string;
  computedInputSchema: JsonSchema | undefined;
  computedOutputSchema: JsonSchema | undefined;
  inputPreviewRef?: React.LegacyRef<HTMLDivElement>;
  inputHeight: number;
};

export function TaskModalDoublePreview(props: TaskModalDoublePreviewProps) {
  const {
    tenant,
    taskSchemaId,
    messages,
    loading,
    noChangesDetected,
    token,
    className,
    computedInputSchema,
    computedOutputSchema,
    inputPreviewRef,
    inputHeight,
  } = props;

  // We cannot use memos instead of states here since the we want the value to be updated after each loading but NOT be undefined while loading.

  const [chatMessages, setChatMessages] = useState<ChatMessage[] | undefined>(
    undefined
  );

  const [computedInputSchemaToUse, setComputedInputSchemaToUse] = useState<
    JsonSchema | undefined
  >(undefined);

  const [computedOutputSchemaToUse, setComputedOutputSchemaToUse] = useState<
    JsonSchema | undefined
  >(undefined);

  useEffect(() => {
    if (loading) {
      return;
    }
    setComputedInputSchemaToUse(computedInputSchema);
  }, [computedInputSchema, loading]);

  useEffect(() => {
    if (loading) {
      return;
    }
    setComputedOutputSchemaToUse(computedOutputSchema);
  }, [computedOutputSchema, loading]);

  useEffect(() => {
    if (loading) {
      return;
    }

    let chatMessages: ChatMessage[] | undefined = undefined;

    if (messages.length > 0) {
      chatMessages = messages.map((message) => ({
        role: message.username === WORKFLOW_AI_USERNAME ? 'ASSISTANT' : 'USER',
        content: message.message as string,
      }));
    }

    setChatMessages(chatMessages);
  }, [messages, loading]);

  const [previousInputPreview, setPreviousInputPreview] = useState<
    Record<string, unknown> | undefined
  >(undefined);

  const [previousOutputPreview, setPreviousOutputPreview] = useState<
    Record<string, unknown> | undefined
  >(undefined);

  const {
    generatedInput: previewInput,
    generatedOutput: previewOutput,
    finalGeneratedInput: finalPreviewInput,
    finalGeneratedOutput: finalPreviewOutput,
    inputBySchemaId: previewInputBySchemaId,
    outputBySchemaId: previewOutputBySchemaId,
    isLoading: isLoadingPreviews,
  } = useOrFetchTaskPreview(
    tenant,
    taskSchemaId,
    chatMessages,
    computedInputSchemaToUse as Record<string, unknown>,
    computedOutputSchemaToUse as Record<string, unknown>,
    previousInputPreview,
    previousOutputPreview,
    token,
    loading
  );

  const shouldShowIsLoadingPreviews = useMemo(() => {
    if (
      noChangesDetected &&
      !!previewInputBySchemaId &&
      !!previewOutputBySchemaId
    ) {
      return false;
    }
    return isLoadingPreviews;
  }, [
    isLoadingPreviews,
    noChangesDetected,
    previewInputBySchemaId,
    previewOutputBySchemaId,
  ]);

  useEffect(() => {
    if (loading) {
      return;
    }

    if (!!previewInputBySchemaId) {
      setPreviousInputPreview(previewInputBySchemaId);
    }
  }, [previewInputBySchemaId, loading]);

  useEffect(() => {
    if (loading) {
      return;
    }

    if (!!previewOutputBySchemaId) {
      setPreviousOutputPreview(previewOutputBySchemaId);
    }
  }, [previewOutputBySchemaId, loading]);

  useEffect(() => {
    if (loading) {
      return;
    }

    if (!!finalPreviewInput) {
      setPreviousInputPreview(finalPreviewInput);
    }
  }, [finalPreviewInput, loading]);

  useEffect(() => {
    if (loading) {
      return;
    }

    if (!!finalPreviewOutput) {
      setPreviousOutputPreview(finalPreviewOutput);
    }
  }, [finalPreviewOutput, loading]);

  const previewInputToShow = useMemo(() => {
    if (noChangesDetected) {
      return previewInputBySchemaId ?? finalPreviewInput ?? previewInput;
    }
    return previewInput;
  }, [
    previewInputBySchemaId,
    previewInput,
    finalPreviewInput,
    noChangesDetected,
  ]);

  const previewOutputToShow = useMemo(() => {
    if (noChangesDetected) {
      return previewOutputBySchemaId ?? finalPreviewOutput ?? previewOutput;
    }
    return previewOutput;
  }, [
    previewOutputBySchemaId,
    previewOutput,
    finalPreviewOutput,
    noChangesDetected,
  ]);

  return (
    <div className={className}>
      <div
        className='flex flex-col w-full'
        style={{
          height: `${inputHeight}px`,
        }}
      >
        <TaskModalInProgressHeader
          title='Input'
          inProgress={shouldShowIsLoadingPreviews && !loading}
          inProgressText='Loading Preview'
        />
        <TaskModalPreviewContent
          isLoadingPreviews={shouldShowIsLoadingPreviews}
          isLoadingNewSchema={loading}
          preview={previewInputToShow}
          computedSchema={computedInputSchemaToUse}
          className='flex w-full'
          inputPreviewRef={inputPreviewRef}
        />
      </div>
      <div className='flex flex-col w-full border-t border-gray-200 border-dashed'>
        <TaskModalInProgressHeader
          title='Output (Preview)'
          inProgress={shouldShowIsLoadingPreviews && !loading}
          inProgressText='Loading Preview'
        />
        <TaskModalPreviewContent
          isLoadingPreviews={shouldShowIsLoadingPreviews}
          isLoadingNewSchema={loading}
          preview={previewOutputToShow}
          computedSchema={computedOutputSchemaToUse}
          className='flex w-full'
        />
      </div>
    </div>
  );
}
