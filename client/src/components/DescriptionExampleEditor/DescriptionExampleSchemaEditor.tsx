import { cx } from 'class-variance-authority';
import { useCallback } from 'react';
import { SchemaEditorField } from '@/lib/schemaEditorUtils';
import { EnumMultiSelect } from '../ui/EnumMultiSelect';
import { Input } from '../ui/Input';

type DescriptionExampleSchemaEditorProps = {
  splattedSchema: SchemaEditorField;
  setSplattedSchema: (splattedSchema: SchemaEditorField) => void;
  isArrayItem?: boolean;
  showExamples?: boolean;
};

export function DescriptionExampleSchemaEditor(
  props: DescriptionExampleSchemaEditorProps
) {
  const {
    splattedSchema,
    setSplattedSchema,
    isArrayItem = false,
    showExamples = false,
  } = props;
  const { keyName, fields, description, examples, type } = splattedSchema;
  const isRoot = keyName === '';

  const onDescriptionChange = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      setSplattedSchema({
        ...splattedSchema,
        description: event.target.value,
      });
    },
    [splattedSchema, setSplattedSchema]
  );

  const isExamplesSupported = type === 'string';

  const onExampleChange = useCallback(
    (newExamples: string[]) => {
      setSplattedSchema({
        ...splattedSchema,
        examples: newExamples,
      });
    },
    [splattedSchema, setSplattedSchema]
  );

  return (
    <div className='w-full flex flex-col gap-2 text-sm font-medium text-slate-500'>
      {!isRoot && (
        <>
          <div className='text-slate-700'>
            {isArrayItem ? `[${keyName}] item` : `${keyName}:`}
          </div>
          <div className='w-full flex gap-2 items-center'>
            <div className='w-[100px]'>description:</div>
            <Input
              value={description}
              onChange={onDescriptionChange}
              placeholder='Enter description (optional)'
              className='w-full'
            />
          </div>
          {showExamples && isExamplesSupported && (
            <div className='w-full flex gap-2 items-center'>
              <div className='w-[100px]'>examples:</div>
              <EnumMultiSelect
                onChange={onExampleChange}
                enumValues={(examples || []) as string[]}
                className='w-full'
              />
            </div>
          )}
        </>
      )}
      {!!fields && fields.length > 0 && (
        <div className={cx('flex flex-col gap-2', !isRoot && 'pl-4')}>
          {fields.map((field) => (
            <DescriptionExampleSchemaEditor
              key={field.keyName}
              splattedSchema={field}
              isArrayItem={type === 'array'}
              showExamples={showExamples}
              setSplattedSchema={(newSplattedSchema) => {
                setSplattedSchema({
                  ...splattedSchema,
                  fields: splattedSchema.fields?.map((splattedField) =>
                    splattedField.keyName === field.keyName
                      ? newSplattedSchema
                      : splattedField
                  ),
                });
              }}
            />
          ))}
        </div>
      )}
    </div>
  );
}
