import type { Meta, StoryObj } from '@storybook/react';
import { useToggle } from 'usehooks-ts';
import { SimpleRadioIndicator } from '@/components/ui/RadioGroup';

function Wrapper() {
  const [value, toggleValue] = useToggle(true);

  return (
    <div className='flex flex-col gap-2'>
      <SimpleRadioIndicator isSelected={value === true} onClick={toggleValue} />
      <SimpleRadioIndicator isSelected={value === false} onClick={toggleValue} />
    </div>
  );
}

/**
 * A set of checkable buttons—known as radio buttons—where no more than one of
 * the buttons can be checked at a time.
 */
const meta = {
  title: 'ui/RadioGroupSimple',
  component: SimpleRadioIndicator,
  tags: ['autodocs'],
  argTypes: {},
  args: {
    isSelected: false,
  },
  render: () => <Wrapper />,
} satisfies Meta<typeof SimpleRadioIndicator>;

export default meta;

type Story = StoryObj<typeof meta>;

/**
 * The default form of the radio group.
 */
export const Default: Story = {};
