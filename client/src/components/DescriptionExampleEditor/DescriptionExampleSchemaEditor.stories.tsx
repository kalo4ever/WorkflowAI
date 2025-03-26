import type { Meta, StoryObj } from '@storybook/react';
import { useCallback, useMemo, useState } from 'react';
import { SchemaEditorField, fromSplattedEditorFieldsToSchema } from '@/lib/schemaEditorUtils';
import { simpleObjectSchemaFixture } from '@/tests/fixtures/schemaEditor/simpleObject';
import { CodeBlock } from '../CodeBlock';
import { DescriptionExampleSchemaEditor } from './DescriptionExampleSchemaEditor';

type WrapperProps = {
  splattedSchema: SchemaEditorField;
};

function Wrapper(props: WrapperProps) {
  const { splattedSchema: initialSplattedSchema } = props;
  const [splattedSchema, setSplattedSchema] = useState<SchemaEditorField>(initialSplattedSchema);
  const finalSchema = useMemo(() => {
    if (!splattedSchema) {
      return undefined;
    }
    const { schema } = fromSplattedEditorFieldsToSchema(splattedSchema);
    return schema;
  }, [splattedSchema]);

  const handleSetSplattedSchema = useCallback(
    (newSplattedSchema: SchemaEditorField) => {
      if (newSplattedSchema) {
        setSplattedSchema(newSplattedSchema);
      }
    },
    [setSplattedSchema]
  );

  return (
    <div className='flex gap-2 border w-full'>
      <div className='basis-1/3'>
        <DescriptionExampleSchemaEditor splattedSchema={splattedSchema} setSplattedSchema={handleSetSplattedSchema} />
      </div>
      <div className='flex flex-col gap-2 basis-1/3'>
        <div>Splatted Schema</div>
        <CodeBlock language='json' snippet={JSON.stringify(splattedSchema, null, 2)} />
      </div>
      <div className='flex flex-col gap-2 basis-1/3'>
        <div>Final Schema</div>
        <CodeBlock language='json' snippet={JSON.stringify(finalSchema, null, 2)} />
      </div>
    </div>
  );
}

const meta = {
  title: 'Components/DescriptionExampleSchemaEditor/DescriptionExampleSchemaEditor',
  component: DescriptionExampleSchemaEditor,
  tags: ['autodocs'],
  argTypes: {},
  parameters: {
    layout: 'centered',
  },
  render: (props: WrapperProps) => <Wrapper {...props} />,
} satisfies Meta<typeof DescriptionExampleSchemaEditor>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    splattedSchema: simpleObjectSchemaFixture.splattedEditorFields,
  },
};
