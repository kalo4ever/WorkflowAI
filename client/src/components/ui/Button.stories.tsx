import { AddCircleFilled } from '@fluentui/react-icons';
import { Meta, StoryObj } from '@storybook/react';
import { Mail } from 'lucide-react';
import { Button } from '@/components/ui/Button';

const meta: Meta<typeof Button> = {
  title: 'ui/Button',
  component: Button,
  tags: ['autodocs'],
  argTypes: {},
  args: {
    children: 'Save',
  },
  render: ({ children, ...rest }) => (
    <div className='flex items-center gap-2 whitespace-nowrap'>
      <div className='flex flex-col gap-2 items-start'>
        <div>Regular</div>
        <Button size='lg' {...rest}>
          {children}
        </Button>
        <Button {...rest}>{children}</Button>
        <Button size='sm' {...rest}>
          {children}
        </Button>
      </div>
      <div className='flex flex-col gap-2 items-start'>
        <div>Icon</div>
        <Button fluentIcon={AddCircleFilled} size='lg' {...rest}>
          {children}
        </Button>
        <Button fluentIcon={AddCircleFilled} {...rest}>
          {children}
        </Button>
        <Button fluentIcon={AddCircleFilled} size='sm' {...rest}>
          {children}
        </Button>
      </div>
      <div className='flex flex-col gap-2 items-start'>
        <div>Disabled</div>
        <Button size='lg' {...rest} disabled>
          {children}
        </Button>
        <Button {...rest} disabled>
          {children}
        </Button>
        <Button size='sm' {...rest} disabled>
          {children}
        </Button>
      </div>
      <div className='flex flex-col gap-2 items-start'>
        <div>Loading</div>
        <Button size='lg' {...rest} loading>
          {children}
        </Button>
        <Button {...rest} loading>
          {children}
        </Button>
        <Button size='sm' {...rest} loading>
          {children}
        </Button>
      </div>
      <div className='flex flex-col gap-2 items-start'>
        <div>Loading icon</div>
        <Button fluentIcon={AddCircleFilled} size='lg' {...rest} loading>
          {children}
        </Button>
        <Button fluentIcon={AddCircleFilled} {...rest} loading>
          {children}
        </Button>
        <Button fluentIcon={AddCircleFilled} size='sm' {...rest} loading>
          {children}
        </Button>
      </div>
      <div className='flex flex-col gap-2 items-start'>
        <div>F Icon</div>
        <Button size='icon-lg' fluentIcon={AddCircleFilled} {...rest} />
        <Button size='icon' fluentIcon={AddCircleFilled} {...rest} />
        <Button size='icon-sm' fluentIcon={AddCircleFilled} {...rest} />
      </div>
      <div className='flex flex-col gap-2 items-start'>
        <div>F Icon Dis</div>
        <Button size='icon-lg' fluentIcon={AddCircleFilled} {...rest} disabled />
        <Button size='icon' fluentIcon={AddCircleFilled} {...rest} disabled />
        <Button size='icon-sm' fluentIcon={AddCircleFilled} {...rest} disabled />
      </div>
      <div className='flex flex-col gap-2 items-start'>
        <div>F Icon Load</div>
        <Button size='icon-lg' fluentIcon={AddCircleFilled} {...rest} loading />
        <Button size='icon' fluentIcon={AddCircleFilled} {...rest} loading />
        <Button size='icon-sm' fluentIcon={AddCircleFilled} {...rest} loading />
      </div>
      <div className='flex flex-col gap-2 items-start'>
        <div>F Icon Circ</div>
        <Button shape='circle' size='icon-lg' fluentIcon={AddCircleFilled} {...rest} />
        <Button shape='circle' size='icon' fluentIcon={AddCircleFilled} {...rest} />
        <Button shape='circle' size='icon-sm' fluentIcon={AddCircleFilled} {...rest} />
      </div>
      <div className='flex flex-col gap-2 items-start'>
        <div>L Icon</div>
        <Button size='icon-lg' lucideIcon={Mail} {...rest} />
        <Button size='icon' lucideIcon={Mail} {...rest} />
        <Button size='icon-sm' lucideIcon={Mail} {...rest} />
      </div>
    </div>
  ),
};
export default meta;

type Story = StoryObj<typeof Button>;

export const Default: Story = {
  args: {
    variant: 'default',
  },
};

export const NewDesign: Story = {
  args: {
    variant: 'newDesign',
  },
};

export const NewDesignIndigo: Story = {
  args: {
    variant: 'newDesignIndigo',
  },
};

export const Ghost: Story = {
  args: {
    variant: 'ghost',
  },
};

export const Outline: Story = {
  args: {
    variant: 'outline',
  },
};

export const Subtle: Story = {
  args: {
    variant: 'subtle',
  },
};

export const Destructive: Story = {
  args: {
    variant: 'destructive',
  },
};

export const Link: Story = {
  args: {
    variant: 'link',
  },
};
