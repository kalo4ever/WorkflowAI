import type { Meta, StoryObj } from '@storybook/react';
import { Combobox } from '@/components/ui/Combobox';

const frameworks = [
  {
    value: 'next.js',
    label: 'Next.js',
  },
  {
    value: 'sveltekit',
    label: 'SvelteKit',
  },
  {
    value: 'nuxt.js',
    label: 'Nuxt.js',
  },
  {
    value: 'remix',
    label: 'Remix',
  },
  {
    value: 'astro',
    label: 'Astro',
  },
];

/**
 * A select that allows the user to search for an option.
 */
const meta: Meta<typeof Combobox> = {
  title: 'ui/Combobox',
  component: Combobox,
  tags: ['autodocs'],
  argTypes: {},
  args: {
    value: '',
    options: frameworks,
    placeholder: 'Search frameworks...',
    emptyMessage: 'No framework found',
  },
  render: (args) => <Combobox {...args} />,
  parameters: {
    layout: 'centered',
  },
} satisfies Meta<typeof Combobox>;

export default meta;

type Story = StoryObj<typeof meta>;

/**
 * The default form of the Combobox.
 */
export const Default: Story = {};

/**
 * Use the `noOptionsMessage` prop to display a message when there are no options.
 */
export const NoOptions: Story = {
  args: {
    noOptionsMessage: 'Select a framework...',
  },
};
