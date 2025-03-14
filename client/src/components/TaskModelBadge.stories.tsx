import type { Meta, StoryObj } from '@storybook/react';
import { TaskModelBadge } from './TaskModelBadge';

const meta = {
  title: 'Components/TaskModelBadge',
  component: TaskModelBadge,
  tags: ['autodocs'],
  argTypes: {},
  parameters: {
    layout: 'centered',
  },
} satisfies Meta<typeof TaskModelBadge>;

export default meta;

type Story = StoryObj<typeof meta>;

export const OpenAI: Story = {
  args: {
    model: 'gpt-4-turbo-2024-04-09',
    providerId: 'openai',
  },
};

export const AzureOpenAI: Story = {
  args: {
    model: 'azure-gpt-4-turbo-2024-04-09',
    providerId: 'azure_openai',
  },
};

export const Google: Story = {
  args: {
    model: 'google-gpt-4-turbo-2024-04-09',
    providerId: 'google',
  },
};

export const Groq: Story = {
  args: {
    model: 'groq-gpt-4-turbo-2024-04-09',
    providerId: 'groq',
  },
};

export const Anthropic: Story = {
  args: {
    model: 'anthropic-gpt-4-turbo-2024-04-09',
    providerId: 'anthropic',
  },
};

export const WithoutProvider: Story = {
  args: {
    model: 'gpt-4-turbo-2024-04-09',
  },
};
