import { cx } from 'class-variance-authority';
import { useMemo } from 'react';
import { Badge } from '@/components/ui/Badge';
import { FieldType } from '@/lib/schemaUtils';
import { cn } from '@/lib/utils';
import { JsonValueSchema } from '@/types';
import { SimpleTooltip } from '../ui/Tooltip';
import { HTMLValueViewer } from './HTMLValueViewer';

const TOOLTIP_DELAY = 100;

type FieldDescriptionExamplesProps = {
  schema: JsonValueSchema | undefined;
  fieldType: FieldType | undefined;
  className?: string;
  showExamples: boolean;
  onShowEditDescriptionModal?: () => void;
};

export function FieldDescriptionExamples(props: FieldDescriptionExamplesProps) {
  const { schema, fieldType, className, showExamples, onShowEditDescriptionModal } = props;
  const description = schema?.description;
  const examples = schema?.examples;

  const descriptionContent = useMemo(() => {
    return (
      <div className='flex items-center gap-2'>
        <SimpleTooltip
          content={!!onShowEditDescriptionModal ? 'Edit' : undefined}
          align='start'
          side='top'
          tooltipDelay={TOOLTIP_DELAY}
        >
          <div
            className={cn(
              'text-gray-500 font-normal text-[13px]',
              !!onShowEditDescriptionModal &&
                'cursor-pointer hover:underline hover:underline-offset-4 hover:decoration-dashed'
            )}
            onClick={onShowEditDescriptionModal}
          >
            description:
          </div>
        </SimpleTooltip>
        <div className={'flex-1 flex'}>
          {description ? (
            <Badge variant='secondary' className='font-medium text-[13px]'>
              {description}
            </Badge>
          ) : (
            <div className='text-gray-500 font-normal text-[16px]'>-</div>
          )}
        </div>
      </div>
    );
  }, [description, onShowEditDescriptionModal]);

  const examplesContent = useMemo(() => {
    const isExamplesSupported = fieldType === 'string' || fieldType === 'html';
    const isEnum = !!schema && 'enum' in schema;
    if (!showExamples || !isExamplesSupported || isEnum || !examples || examples.length === 0) {
      return null;
    }
    return (
      <div className='flex items-center gap-2'>
        <SimpleTooltip
          content={!!onShowEditDescriptionModal ? 'Edit' : undefined}
          align='start'
          side='top'
          tooltipDelay={TOOLTIP_DELAY}
        >
          <div
            className={cn(
              'text-gray-500 font-normal text-[13px]',
              !!onShowEditDescriptionModal &&
                'cursor-pointer hover:underline hover:underline-offset-4 hover:decoration-dashed'
            )}
            onClick={onShowEditDescriptionModal}
          >
            examples:
          </div>
        </SimpleTooltip>
        {fieldType === 'string' ? (
          <div className={cx('flex-1 flex items-center gap-1')}>
            {examples.map((example, index) => (
              <Badge key={index} variant='secondary' className='font-medium text-[13px]'>
                {example as string}
              </Badge>
            ))}
          </div>
        ) : (
          <HTMLValueViewer value={examples[0] as string} keyPath='' defs={undefined} />
        )}
      </div>
    );
  }, [examples, fieldType, showExamples, schema, onShowEditDescriptionModal]);

  if (!schema) {
    return null;
  }

  return (
    <div className={cx('flex flex-col gap-2', className)}>
      {descriptionContent}
      {examplesContent}
    </div>
  );
}
