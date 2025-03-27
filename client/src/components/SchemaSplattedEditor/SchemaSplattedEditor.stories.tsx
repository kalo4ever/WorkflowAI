import type { Meta, StoryObj } from '@storybook/react';
import { useCallback, useMemo, useState } from 'react';
import { SchemaEditorField, fromSplattedEditorFieldsToSchema } from '@/lib/schemaEditorUtils';
import { arrayObjectSchemaFixture } from '@/tests/fixtures/schemaEditor/arrayObject';
import { defaultInputObjectSchemaFixture } from '@/tests/fixtures/schemaEditor/defaultInputObjects';
import { defaultOutputObjectSchemaFixture } from '@/tests/fixtures/schemaEditor/defaultOutputObject';
import { productionObjectsSchemaFixture } from '@/tests/fixtures/schemaEditor/productionObject';
import { refObjectDefinitionFixtures, refObjectsSchemaFixture } from '@/tests/fixtures/schemaEditor/refObjects';
import { simpleObjectSchemaFixture } from '@/tests/fixtures/schemaEditor/simpleObject';
import { unionObjectsSchemaFixture } from '@/tests/fixtures/schemaEditor/unionObjects';
import { JsonSchemaDefinitions } from '@/types';
import { CodeBlock } from '../CodeBlock';
import { SchemaSplattedEditor } from './SchemaSplattedEditor';

type WrapperProps = {
  splattedSchema: SchemaEditorField | undefined;
  definitions?: JsonSchemaDefinitions;
};

function Wrapper(props: WrapperProps) {
  const { splattedSchema: initialSplattedSchema } = props;
  const [splattedSchema, setSplattedSchema] = useState<SchemaEditorField | undefined>(initialSplattedSchema);
  const finalSchema = useMemo(() => {
    if (!splattedSchema) {
      return undefined;
    }
    const { schema } = fromSplattedEditorFieldsToSchema(splattedSchema);
    return schema;
  }, [splattedSchema]);

  const handleSetSplattedSchema = useCallback(
    (newSplattedSchema: SchemaEditorField | undefined) => {
      if (newSplattedSchema) {
        setSplattedSchema(newSplattedSchema);
      }
    },
    [setSplattedSchema]
  );

  return (
    <div className='flex gap-2 border w-full'>
      <div className='basis-1/3'>
        <SchemaSplattedEditor
          title='Schema'
          details='This is the information you provide to the LLM'
          splattedSchema={splattedSchema}
          setSplattedSchema={handleSetSplattedSchema}
        />
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
  title: 'Components/SchemaSplattedEditor/SchemaSplattedEditor',
  component: SchemaSplattedEditor,
  tags: ['autodocs'],
  argTypes: {},
  parameters: {
    layout: 'centered',
  },
  render: (props: WrapperProps) => <Wrapper {...props} />,
} satisfies Meta<typeof SchemaSplattedEditor>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    splattedSchema: simpleObjectSchemaFixture.splattedEditorFields,
    title: 'Schema',
    details: 'Details',
  },
};

export const ArrayObject: Story = {
  args: {
    splattedSchema: arrayObjectSchemaFixture.splattedEditorFields,
    title: 'Schema',
    details: 'Details',
  },
};

export const RefObject: Story = {
  args: {
    splattedSchema: refObjectsSchemaFixture.splattedEditorFields,
    definitions: refObjectDefinitionFixtures.originalDefinitions,
    title: 'Schema',
    details: 'Details',
  },
};

export const UnionObject: Story = {
  args: {
    splattedSchema: unionObjectsSchemaFixture.splattedEditorFields,
    title: 'Schema',
    details: 'Details',
  },
};

export const ComplexObject: Story = {
  args: {
    splattedSchema: productionObjectsSchemaFixture.splattedEditorFields,
    title: 'Schema',
    details: 'Details',
  },
};

export const DefaultInput: Story = {
  args: {
    splattedSchema: defaultInputObjectSchemaFixture.splattedEditorFields,
    title: 'Schema',
    details: 'Details',
  },
};

export const DefaultOutput: Story = {
  args: {
    splattedSchema: defaultOutputObjectSchemaFixture.splattedEditorFields,
    title: 'Schema',
    details: 'Details',
  },
};
