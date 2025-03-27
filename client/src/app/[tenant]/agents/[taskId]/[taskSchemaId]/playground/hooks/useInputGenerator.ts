import { useCallback, useEffect, useRef } from 'react';
import { useState } from 'react';
import { toast } from 'sonner';
import { useTasks } from '@/store';
import { ToolCallName, usePlaygroundChatStore } from '@/store/playgroundChatStore';
import { GeneralizedTaskInput } from '@/types';
import { TaskID, TaskSchemaID, TenantID } from '@/types/aliases';
import { GeneratePlaygroundInputParams, RunTaskOptions } from './usePlaygroundPersistedState';

type InputGenerationIteration = {
  iteration: number;
  type: 'foreground' | 'background';
  pending: boolean;
};

type UseInputGeneratorProps = {
  handleRunTasks: (options: RunTaskOptions) => void;
  isInputGenerationSupported: boolean;
  preGeneratedInput: GeneralizedTaskInput | undefined;
  onResetTaskRunIds: () => void;
  saveToHistoryForInput: (input: GeneralizedTaskInput) => void;
  setGeneratedInput: (input: GeneralizedTaskInput | undefined) => void;
  setPreGeneratedInput: (input: GeneralizedTaskInput | undefined) => void;
  resetStreamedChunks: () => void;
  taskId: TaskID;
  taskSchemaId: TaskSchemaID;
  tenant: TenantID | undefined;
  voidInput: GeneralizedTaskInput | undefined;
  token: string | undefined;
};

export function useInputGenerator(props: UseInputGeneratorProps) {
  const {
    handleRunTasks,
    isInputGenerationSupported,
    preGeneratedInput,
    onResetTaskRunIds,
    saveToHistoryForInput,
    setGeneratedInput,
    setPreGeneratedInput,
    resetStreamedChunks,
    taskId,
    taskSchemaId,
    tenant,
    token,
    voidInput,
  } = props;
  const generatePlaygroundInput = useTasks((state) => state.generatePlaygroundInput);
  const generatePlaygroundInputWithText = useTasks((state) => state.generatePlaygroundInputWithText);
  const [inputLoading, setInputLoading] = useState(false);
  const abortController = useRef<AbortController | null>(null);

  // We want to avoid generating 2 inputs at the same time
  // because the simultaneous inputs might be identical.
  const currentIteration = useRef<InputGenerationIteration>({
    iteration: 0,
    type: 'foreground',
    pending: false,
  });

  const generateInputInBackground = useCallback(async () => {
    if (currentIteration.current?.pending || !isInputGenerationSupported) {
      return;
    }
    const iteration = currentIteration.current.iteration + 1;
    currentIteration.current = {
      iteration,
      type: 'background',
      pending: true,
    };
    const input = await generatePlaygroundInput(tenant, taskId, taskSchemaId, {}, token);
    if (currentIteration.current.type !== 'background' || currentIteration.current.iteration !== iteration) {
      return;
    }
    setPreGeneratedInput(input);
    currentIteration.current = {
      iteration,
      type: 'background',
      pending: false,
    };
  }, [isInputGenerationSupported, generatePlaygroundInput, setPreGeneratedInput, taskId, taskSchemaId, tenant, token]);

  useEffect(() => {
    if (!preGeneratedInput && isInputGenerationSupported) {
      generateInputInBackground();
    }
  }, [preGeneratedInput, generateInputInBackground, isInputGenerationSupported]);

  const cancelToolCall = usePlaygroundChatStore((state) => state.cancelToolCall);
  const markToolCallAsDone = usePlaygroundChatStore((state) => state.markToolCallAsDone);

  const handleGeneratePlaygroundInput = useCallback(
    async (params?: GeneratePlaygroundInputParams) => {
      const {
        externalVersion,
        externalInstructions,
        launchRuns = false,
        instructions,
        temperature,
        successMessage = 'Input generated successfully',
        inputText,
        baseInput,
      } = params || {};

      setGeneratedInput(voidInput);
      setInputLoading(true);
      resetStreamedChunks();
      onResetTaskRunIds();

      const currentAbortController = new AbortController();
      abortController.current = currentAbortController;

      const toastId = toast.loading('Generating input...');

      const onSuccess = (input: GeneralizedTaskInput | undefined) => {
        if (currentAbortController.signal.aborted) {
          cancelToolCall(ToolCallName.GENERATE_AGENT_INPUT);
          setInputLoading(false);
          setGeneratedInput(undefined);
          toast.dismiss(toastId);
          return;
        }

        setInputLoading(false);
        setGeneratedInput(input);

        if (input) {
          saveToHistoryForInput(input);
        }

        markToolCallAsDone(taskId, ToolCallName.GENERATE_AGENT_INPUT);

        if (launchRuns === true) {
          handleRunTasks({
            externalGeneratedInput: input,
            externalVersion,
            externalInstructions,
          });
        }

        toast.success(successMessage, { id: toastId });
      };

      const onError = () => {
        cancelToolCall(ToolCallName.GENERATE_AGENT_INPUT);

        if (currentAbortController.signal.aborted) {
          setInputLoading(false);
          setGeneratedInput(undefined);
          toast.dismiss(toastId);
          return;
        }

        setInputLoading(false);
        toast.error('Failed to generate input', { id: toastId });
      };

      // Input Generation with Text
      if (inputText) {
        const request = {
          inputs_text: inputText,
          base_input: baseInput,
        };

        try {
          const message = await generatePlaygroundInputWithText(
            tenant,
            taskId,
            taskSchemaId,
            request,
            token,
            setGeneratedInput,
            currentAbortController.signal
          );
          onSuccess(message);
          return;
        } catch {
          onError();
          return;
        }
      }

      // Input Generation with Pre-Generated Input
      if (instructions === undefined && temperature === undefined && !!preGeneratedInput) {
        setPreGeneratedInput(undefined);
        onSuccess(preGeneratedInput);
        return;
      }

      // Input Generation
      let message: GeneralizedTaskInput;

      const shouldGenerateInBackground =
        currentIteration.current.type === 'background' && currentIteration.current.pending;

      currentIteration.current = {
        iteration: shouldGenerateInBackground
          ? currentIteration.current.iteration
          : currentIteration.current.iteration + 1,
        type: 'foreground',
        pending: true,
      };

      const request = {
        instructions,
        group: {
          properties: {
            temperature,
          },
        },
        base_input: baseInput,
      };

      try {
        message = await generatePlaygroundInput(
          tenant,
          taskId,
          taskSchemaId,
          request,
          token,
          setGeneratedInput,
          currentAbortController.signal
        );
      } catch (error) {
        onError();
        return;
      } finally {
        currentIteration.current = {
          iteration: currentIteration.current.iteration,
          type: 'foreground',
          pending: false,
        };
      }

      if (shouldGenerateInBackground) {
        generateInputInBackground();
      }

      onSuccess(message);
    },
    [
      setGeneratedInput,
      voidInput,
      resetStreamedChunks,
      onResetTaskRunIds,
      preGeneratedInput,
      generatePlaygroundInputWithText,
      tenant,
      taskId,
      taskSchemaId,
      token,
      setPreGeneratedInput,
      generatePlaygroundInput,
      generateInputInBackground,
      saveToHistoryForInput,
      handleRunTasks,
      cancelToolCall,
      markToolCallAsDone,
    ]
  );

  const onStopGeneratingInput = useCallback(() => {
    if (abortController.current) {
      abortController.current.abort();
      abortController.current = null;
    }
  }, []);

  return {
    handleGeneratePlaygroundInput,
    inputLoading,
    onStopGeneratingInput,
  };
}
