import type { Meta, StoryObj } from '@storybook/react';
import { apiSnippetsFixture } from '@/tests/fixtures/apiSnippets';
import { CodeLanguage, InstallInstruction } from '@/types/snippets';
import { CodeBlock } from './CodeBlock';

const meta = {
  title: 'ui/CodeBlock',
  component: CodeBlock,
  tags: ['autodocs'],
  argTypes: {},
  parameters: {
    layout: 'centered',
  },
} satisfies Meta<typeof CodeBlock>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    language: CodeLanguage.BASH,
    snippet: 'npm run dev',
  },
};

export const TypeScript: Story = {
  args: {
    language: CodeLanguage.TYPESCRIPT,
    snippet: apiSnippetsFixture[InstallInstruction.INSTALL].code,
  },
};
