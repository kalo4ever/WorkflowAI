import { cx } from 'class-variance-authority';
import { useMemo } from 'react';
import { ObjectViewer } from '@/components/ObjectViewer/ObjectViewer';
import { InitInputFromSchemaMode, initInputFromSchema } from '@/lib/schemaUtils';
import { JsonSchema } from '@/types/json_schema';
import { collectUsedDefinitions } from './utils';

type TaskModalPreviewContentProps = {
  preview: JsonSchema | undefined;
  computedSchema: JsonSchema | undefined;
  className?: string;
  isLoadingPreviews: boolean;
  isLoadingNewSchema: boolean;
  inputPreviewRef?: React.LegacyRef<HTMLDivElement>;
};

export function TaskModalPreviewContent(props: TaskModalPreviewContentProps) {
  const { preview, computedSchema, className, isLoadingPreviews, isLoadingNewSchema, inputPreviewRef } = props;

  const usedDefs = useMemo(() => {
    if (!computedSchema) return undefined;
    const result = collectUsedDefinitions(computedSchema);
    return result;
  }, [computedSchema]);

  const voidInput = useMemo(() => {
    if (!computedSchema || !usedDefs) return undefined;
    return initInputFromSchema(computedSchema, usedDefs, InitInputFromSchemaMode.VOID);
  }, [computedSchema, usedDefs]);

  const loadingText = useMemo(() => {
    if (isLoadingNewSchema) {
      return 'Loading new schema...';
    }
    if (isLoadingPreviews && preview === undefined) {
      return 'Loading preview...';
    }
    return undefined;
  }, [isLoadingNewSchema, isLoadingPreviews, preview]);

  return (
    <div className={cx(className, 'border-t border-gray-200 border-dashed h-max relative')} ref={inputPreviewRef}>
      <div
        className='flex text-white w-full h-max items-center justify-center transition-[opacity,visibility] duration-300 ease-in-out'
        style={{ opacity: loadingText ? 0.0 : 1 }}
      >
        <ObjectViewer
          schema={computedSchema}
          defs={usedDefs}
          value={preview}
          voidValue={voidInput}
          editable={false}
          className='flex h-max w-full'
          showTypesForFiles={true}
          previewMode={true}
          noOverflow={true}
        />
      </div>
      {!!loadingText && (
        <div className='absolute inset-0 flex items-start'>
          <div className='px-4 py-3 text-gray-900 text-[13px] font-medium'>{loadingText}</div>
        </div>
      )}
    </div>
  );
}
