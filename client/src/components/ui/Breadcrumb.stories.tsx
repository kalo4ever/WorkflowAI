import type { Meta, StoryObj } from '@storybook/react';
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
} from '@/components/ui/Breadcrumb';

/**
 * Fast, composable, unstyled Breadcrumb for React.
 */
const meta = {
  title: 'ui/Breadcrumb',
  component: Breadcrumb,
  tags: ['autodocs'],
  argTypes: {},
  args: {},
  render: (args) => (
    <Breadcrumb {...args}>
      <BreadcrumbItem>
        <BreadcrumbLink href='/'>UI</BreadcrumbLink>
      </BreadcrumbItem>
      <BreadcrumbItem>
        <BreadcrumbLink href='/components'>Components</BreadcrumbLink>
      </BreadcrumbItem>
      <BreadcrumbItem isCurrentPage>
        <BreadcrumbLink href='/components/breadcrumb'>
          Breadcrumb
        </BreadcrumbLink>
      </BreadcrumbItem>
    </Breadcrumb>
  ),
  parameters: {
    layout: 'centered',
  },
} satisfies Meta<typeof Breadcrumb>;

export default meta;

type Story = StoryObj<typeof meta>;

/**
 * The default form of the Breadcrumb.
 */
export const Default: Story = {};

export const CustomSeparator: Story = {
  args: {
    separator: '/',
  },
};
