import type { Meta, StoryObj } from '@storybook/react';
import { useCallback, useState } from 'react';
import { DynamicWidthInput } from './DynamicWidthInput';

type WrapperProps = {
  value: string;
};

function Wrapper(props: WrapperProps) {
  const [value, setValue] = useState(props.value);

  const onChange = useCallback((newValue: string) => {
    setValue(newValue);
  }, []);

  return <DynamicWidthInput value={value} onChange={onChange} />;
}

const meta = {
  title: 'Components/SchemaSplattedEditor/DynamicWidthInput',
  component: DynamicWidthInput,
  tags: ['autodocs'],
  argTypes: {},
  parameters: {
    layout: 'centered',
  },
  render: (props) => <Wrapper {...props} />,
} satisfies Meta<typeof DynamicWidthInput>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: { value: 'Default' },
};
