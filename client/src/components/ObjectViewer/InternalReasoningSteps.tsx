import {
  ChevronDown20Regular,
  ChevronUp20Regular,
  SpinnerIos16Regular,
  StreamOutputRegular,
} from '@fluentui/react-icons';
import { last } from 'lodash';
import { useMemo } from 'react';
import { useToggle } from 'usehooks-ts';
import { ToolCallPreview } from '@/types';
import { ReasoningStep } from '@/types/workflowAI';
import { SimpleTooltip } from '../ui/Tooltip';

type Step = {
  title: string | undefined;
  explaination: string | undefined;
};

type InternalReasoningStepsProps = {
  steps: ReasoningStep[] | undefined;
  streamLoading?: boolean;
  toolCalls: Array<ToolCallPreview> | undefined;
  defaultOpen?: boolean;
};

export function InternalReasoningSteps(props: InternalReasoningStepsProps) {
  const { steps, streamLoading, toolCalls, defaultOpen = false } = props;
  const [open, toggleOpen] = useToggle(defaultOpen);

  const mergedSteps: Step[] = useMemo(() => {
    const result: Step[] = [];

    toolCalls?.forEach((preview) => {
      result.push({
        title: preview.name,
        explaination: preview.input_preview,
      });
    });

    steps?.forEach((step) => {
      result.push({
        title: step.title ?? undefined,
        explaination: step.step ?? undefined,
      });
    });

    return result;
  }, [steps, toolCalls]);

  const loadingTitle = useMemo(() => {
    if (!streamLoading || mergedSteps.length === 0) return undefined;
    const lastStep = last(mergedSteps);
    if (!lastStep) return undefined;

    if (lastStep.title) return `${lastStep.title}...`;

    return lastStep.explaination;
  }, [mergedSteps, streamLoading]);

  const suffix = useMemo(() => {
    if (steps && steps.length > 0) {
      if (mergedSteps.length === 1) return 'step';
      return 'steps';
    }

    if (mergedSteps.length === 1) return 'tool call';
    return 'tool calls';
  }, [mergedSteps, steps]);

  if (!!loadingTitle) {
    return (
      <div className='flex items-center gap-2 px-4 py-2 text-gray-700 text-xsm border-b'>
        <SpinnerIos16Regular className='text-gray-400 animate-spin' />
        {loadingTitle}
      </div>
    );
  }

  if (mergedSteps.length === 0) return null;

  const Icon = open ? ChevronUp20Regular : ChevronDown20Regular;
  const tooltipContent = open ? 'Hide all steps' : 'View all steps';
  return (
    <div className='flex flex-col border-b pb-2'>
      <div className='flex items-center justify-between px-4 pt-2 cursor-pointer' onClick={toggleOpen}>
        <div className='flex items-center gap-2 text-gray-700 text-xsm'>
          <StreamOutputRegular className='w-4 h-4 text-gray-400' />
          {`Created output in ${mergedSteps.length} ${suffix}`}
        </div>
        <SimpleTooltip content={tooltipContent}>
          <Icon className='w-4 h-4 text-gray-500' />
        </SimpleTooltip>
      </div>
      {open && (
        <div className='pl-6 py-2'>
          <div className='flex flex-col text-gray-700 text-xsm border-l px-3 gap-2'>
            {mergedSteps.map((step, idx) => (
              <div key={idx} className='flex flex-col'>
                {step.title && <div className='font-medium'>{step.title}</div>}
                <div>{step.explaination}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
