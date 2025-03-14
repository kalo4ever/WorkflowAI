import type { Meta, StoryObj } from '@storybook/react';
import { TaskID, TaskSchemaID, TenantID } from '@/types/aliases';
import { TaskSchemaBadge } from './TaskSchemaBadge';

const meta = {
  title: 'Components/TaskSchemaBadge',
  component: TaskSchemaBadge,
  tags: ['autodocs'],
  argTypes: {},
  parameters: {
    layout: 'centered',
  },
} satisfies Meta<typeof TaskSchemaBadge>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    tenant: '1' as TenantID,
    taskId: '1' as TaskID,
    schemaId: '1' as TaskSchemaID,
  },
};
