import { QuestionCircleRegular } from '@fluentui/react-icons';
import { Loader2 } from 'lucide-react';
import { ObjectViewer } from '@/components/ObjectViewer/ObjectViewer';
import { TaskOutputViewer } from '@/components/ObjectViewer/TaskOutputViewer';
import { cn } from '@/lib/utils';
import { SuggestedAgentPreview } from '@/store/suggested_agents';
import { JsonSchema } from '@/types';

type SuggestedAgentDetailsTooltipContentProps = {
  preview: SuggestedAgentPreview | undefined;
  className?: string;
};

export function SuggestedAgentDetailsTooltipContent(
  props: SuggestedAgentDetailsTooltipContentProps
) {
  const { preview, className } = props;

  const inputSchema = preview?.agent_input_schema as JsonSchema;
  const outputSchema = preview?.agent_output_schema as JsonSchema;

  if (!preview) {
    return (
      <div className='flex w-full h-[120px] items-center justify-center'>
        <Loader2 className='h-6 w-6 animate-spin text-gray-300' />
      </div>
    );
  }

  return (
    <div
      className={cn(
        'flex flex-row flex-1 w-full px-4 overflow-hidden',
        className
      )}
    >
      <div className='flex flex-row flex-1 w-full items-stretch justify-center text-start border-t border-l border-r border-gray-200 rounded-t-[2px] bg-gradient-to-b from-white/90 to-white-0'>
        <div className='flex flex-col w-[50%] border-r border-gray-200 border-dashed'>
          <div className='px-4 py-2 border-b border-gray-200 border-dashed font-semibold text-[16px] text-gray-900'>
            Input
          </div>
          <ObjectViewer
            value={preview.agent_input_example}
            schema={inputSchema}
            defs={inputSchema?.$defs}
            className='w-full flex-1 overflow-y-auto'
            hideCopyValue={true}
            showTypesForFiles={true}
          />
        </div>
        <div className='flex flex-col w-[50%]'>
          <div className='px-4 py-2 border-b border-gray-200 border-dashed font-semibold text-[16px] text-gray-900'>
            Output
          </div>
          <TaskOutputViewer
            value={preview.agent_output_example}
            noOverflow
            schema={outputSchema}
            defs={outputSchema?.$defs}
            className='w-full flex-1 overflow-y-auto'
            errorsByKeypath={undefined}
            hideCopyValue={true}
            showTypesForFiles={true}
          />
        </div>
      </div>
    </div>
  );
}

type SuggestedAgentDetailsTooltipProps = {
  preview: SuggestedAgentPreview | undefined;
};

export function SuggestedAgentDetailsTooltip(
  props: SuggestedAgentDetailsTooltipProps
) {
  const { preview } = props;

  return (
    <div className='flex w-full flex-1 flex-col bg-custom-gradient-1 text-gray-900 overflow-hidden'>
      <div className='flex w-full px-4 py-[14px] border-b border-gray-200 border-dashed text-[16px] font-semibold text-gray-900'>
        Preview
      </div>
      <SuggestedAgentDetailsTooltipContent preview={preview} className='pt-4' />
      <div className='flex flex-row gap-2 w-full py-3 px-4 text-[13px] font-regular text-indigo-500 items-center bg-indigo-50 border-indigo-200 border-t'>
        <QuestionCircleRegular className='w-5 h-5' />
        <div className='flex flex-col flex-1'>
          <div className='flex font-medium w-full text-indigo-700'>
            Does the data format look off?
          </div>
          <div className='flex w-full'>
            For example, are you trying to input an image instead of text? You
            can edit the schema later.
          </div>
        </div>
      </div>
    </div>
  );
}
