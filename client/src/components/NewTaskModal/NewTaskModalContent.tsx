import { cx } from 'class-variance-authority';
import { useRef } from 'react';
import { useResizeHeight } from '@/components/NewTaskModal/useResizeHeight';
import { Loader } from '@/components/ui/Loader';
import { SchemaEditorField } from '@/lib/schemaEditorUtils';
import { TenantID } from '@/types/aliases';
import { TaskSchemaID } from '@/types/aliases';
import { JsonSchema } from '@/types/json_schema';
import { SchemaSplattedEditor } from '../SchemaSplattedEditor/SchemaSplattedEditor';
import { TaskModalDoublePreview } from './Preview/TaskModalDoublePreview';
import { TaskConversation } from './TaskConversation';
import { ConversationMessage } from './TaskConversationMessage';

type NewTaskModalContentProps = {
  tenant: TenantID;
  taskSchemaId: TaskSchemaID;
  token: string | undefined;
  isInitialized: boolean;
  isEditMode: boolean;
  inputSplattedSchema: SchemaEditorField | undefined;
  setInputSplattedSchema: (splattedSchema: SchemaEditorField | undefined) => void;
  outputSplattedSchema: SchemaEditorField | undefined;
  setOutputSplattedSchema: (splattedSchema: SchemaEditorField | undefined) => void;
  open: boolean;
  loading: boolean;
  userMessage: string;
  userFirstName: string | undefined | null;
  messages: ConversationMessage[];
  setUserMessage: (message: string) => void;
  onSendIteration: () => Promise<void>;
  computedInputSchema: JsonSchema | undefined;
  computedOutputSchema: JsonSchema | undefined;
  noChangesDetected: boolean;
  showRetry: boolean;
  retry: () => void;
};

export function NewTaskModalContent(props: NewTaskModalContentProps) {
  const {
    isInitialized,
    isEditMode,
    inputSplattedSchema,
    setInputSplattedSchema,
    outputSplattedSchema,
    setOutputSplattedSchema,
    open,
    loading,
    userMessage,
    userFirstName,
    messages,
    setUserMessage,
    onSendIteration,
    computedInputSchema,
    computedOutputSchema,
    noChangesDetected,
    tenant,
    taskSchemaId,
    token,
    showRetry,
    retry,
  } = props;

  const containerRef = useRef<HTMLDivElement>(null);
  const inputSchemaRef = useRef<HTMLDivElement>(null);
  const inputPreviewRef = useRef<HTMLDivElement>(null);

  const inputHeight = useResizeHeight({
    containerRef,
    inputSchemaRef,
    inputPreviewRef,
  });

  if (!isInitialized) {
    return <Loader centered />;
  }

  if (!isEditMode && !inputSplattedSchema && !outputSplattedSchema) {
    return (
      <div className='flex-1 overflow-hidden'>
        <div
          className={cx(
            'h-full w-full',
            // This fixes a visual glitch when we close the edit task modal and the conversation appear for a moment
            !open && 'invisible'
          )}
        >
          <TaskConversation
            userMessage={userMessage}
            messages={messages}
            setUserMessage={setUserMessage}
            onSendIteration={onSendIteration}
            loading={loading}
            userFirstName={userFirstName}
            showRetry={showRetry}
            retry={retry}
          />
        </div>
      </div>
    );
  }

  return (
    <div className='flex flex-row w-full h-[calc(100%-60px)]' ref={containerRef}>
      <div className='flex flex-row w-[calc(100%-336px)] h-full overflow-y-auto overflow-x-hidden border-t border-gray-200 border-dashed'>
        <div className='flex flex-col w-[50%] h-max min-h-full border-r border-gray-200 border-dashed overflow-x-hidden'>
          <SchemaSplattedEditor
            title='Input Schema'
            details='This is the information you provide to the LLM'
            splattedSchema={inputSplattedSchema}
            setSplattedSchema={setInputSplattedSchema}
            style={{
              height: `${inputHeight}px`,
            }}
            contentRef={inputSchemaRef}
            className='flex w-full overflow-x-hidden'
          />
          <SchemaSplattedEditor
            title='Output Schema'
            details='This is the content you want the LLM to provide in return'
            splattedSchema={outputSplattedSchema}
            setSplattedSchema={setOutputSplattedSchema}
            disableImage
            disableAudio
            disableDocuments
            className='border-t border-gray-200 border-dashed'
          />
        </div>
        <TaskModalDoublePreview
          tenant={tenant}
          taskSchemaId={taskSchemaId}
          loading={loading}
          messages={messages}
          noChangesDetected={noChangesDetected}
          token={token}
          className='flex flex-col w-[50%] h-max min-h-full'
          computedInputSchema={computedInputSchema}
          computedOutputSchema={computedOutputSchema}
          inputPreviewRef={inputPreviewRef}
          inputHeight={inputHeight}
        />
      </div>

      <div className='w-[336px] h-full bg-white border-t border-l border-gray-200'>
        <TaskConversation
          userMessage={userMessage}
          messages={messages}
          setUserMessage={setUserMessage}
          onSendIteration={onSendIteration}
          loading={loading}
          userFirstName={userFirstName}
          showRetry={showRetry}
          retry={retry}
        />
      </div>
    </div>
  );
}
