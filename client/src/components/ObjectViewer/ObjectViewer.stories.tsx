import { Meta, StoryObj } from '@storybook/react';
import { cloneDeep, set } from 'lodash';
import { useCallback, useState } from 'react';
import {
  InitInputFromSchemaMode,
  initInputFromSchema,
} from '@/lib/schemaUtils';
import {
  refObjectDefinitionFixtures,
  refObjectsSchemaFixture,
} from '@/tests/fixtures/schemaEditor/refObjects';
import { schemaMismatch } from '@/tests/fixtures/schemaMismatch';
import { taskSchemaFixture } from '@/tests/fixtures/taskSchema';
import { JsonObjectSchema } from '@/types';
import { ObjectViewer, ObjectViewerProps } from './ObjectViewer';

function Wrapper(props: ObjectViewerProps) {
  const [value, setValue] = useState<Record<string, unknown> | undefined>(
    cloneDeep(props.value)
  );

  const onEdit = useCallback((keyPath: string, newVal: unknown) => {
    setValue((prev) => {
      const newInput = { ...prev };
      set(newInput, keyPath, newVal);
      return newInput;
    });
  }, []);

  return (
    <ObjectViewer
      {...props}
      onEdit={onEdit}
      value={value}
      originalVal={props.value}
    />
  );
}

const meta = {
  title: 'Components/ObjectViewer/ObjectViewer',
  component: Wrapper,
  parameters: {
    layout: 'fullscreen',
  },
  tags: ['autodocs'],
  argTypes: {},
  render: (args) => (
    <div className='p-4'>
      <Wrapper {...args} />
    </div>
  ),
} satisfies Meta<typeof Wrapper>;

export default meta;

type Story = StoryObj<typeof meta>;

const {
  taskSchema,
  taskRun,
  taskSchemaImage,
  taskSchemaImageArray,
  taskInputImage,
} = taskSchemaFixture;

const schema = taskSchema.input_schema.json_schema;
const taskInput = taskRun.task_input;
const schemaArray = taskSchema.output_schema.json_schema;

export const Default: Story = {
  args: {
    value: taskInput,
    schema,
    defs: schema.$defs,
  },
};

export const Empty: Story = {
  args: {
    value: undefined,
    schema,
    defs: schema.$defs,
  },
};

export const ShowTypes: Story = {
  args: {
    value: undefined,
    schema,
    defs: schema.$defs,
    showTypes: true,
  },
};

export const Editable: Story = {
  args: {
    value: initInputFromSchema(
      refObjectsSchemaFixture.originalSchema as JsonObjectSchema,
      refObjectDefinitionFixtures.originalDefinitions,
      InitInputFromSchemaMode.VOID
    ),
    schema: refObjectsSchemaFixture.originalSchema,
    defs: refObjectDefinitionFixtures.originalDefinitions,
    editable: true,
  },
};

export const ArraySchema: Story = {
  args: {
    value: undefined,
    schema: schemaArray,
    defs: schemaArray.$defs,
    showTypes: true,
  },
};

export const SchemaWithImage: Story = {
  args: {
    value: undefined,
    schema: taskSchemaImage.json_schema,
    defs: taskSchemaImage.json_schema.$defs,
    showTypes: true,
  },
};

export const SchemaWithImageArray: Story = {
  args: {
    value: undefined,
    schema: taskSchemaImageArray.json_schema,
    defs: taskSchemaImageArray.json_schema.$defs,
    showTypes: true,
  },
};

export const SchemaWithImageAndValue: Story = {
  args: {
    value: taskInputImage,
    schema: taskSchemaImageArray.json_schema,
    defs: taskSchemaImageArray.json_schema.$defs,
  },
};

export const ProblematicOutput: Story = {
  args: {
    value: schemaMismatch.taskOutput,
    schema: schemaMismatch.taskSchema.json_schema,
    defs: schemaMismatch.taskSchema.json_schema.$defs,
  },
};

export const DefaultCollapsed: Story = {
  args: {
    value: taskInput,
    schema,
    defs: schema.$defs,
    defaultExpanded: false,
  },
};

export const WithFieldErrors: Story = {
  args: {
    value: taskInput,
    schema,
    defs: schema.$defs,
    errorsByKeypath: new Map([
      ['articles.0.id', 'Bool values do not match. Got True expected False.'],
      [
        'articles.0.title',
        'Bool values do not match. Got True expected False.',
      ],
    ]),
  },
};

export const DemoAllFields: Story = {
  args: {
    value: undefined,
    schema: refObjectsSchemaFixture.originalSchema,
    defs: refObjectDefinitionFixtures.originalDefinitions,
    showTypes: true,
  },
};
