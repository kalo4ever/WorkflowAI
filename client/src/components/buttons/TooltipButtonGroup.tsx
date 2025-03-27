import { Fragment } from 'react';
import { Button } from '../ui/Button';
import { Separator } from '../ui/Separator';
import { SimpleTooltip } from '../ui/Tooltip';

export type TooltipButtonProps = {
  icon: React.ReactNode;
  text: string;
  onClick: () => void;
  disabled?: boolean;
};

function TooltipButton(props: TooltipButtonProps) {
  const { icon, text, onClick, disabled = false } = props;
  return (
    <Button variant='ghost' size='sm' onClick={onClick} icon={icon} disabled={disabled}>
      {text}
    </Button>
  );
}

type TooltipButtonGroupProps = {
  items: TooltipButtonProps[];
  children: React.ReactNode;
};

export function TooltipButtonGroup(props: TooltipButtonGroupProps) {
  const { items, children } = props;

  if (items.length === 0) {
    return <div>{children}</div>;
  }

  return (
    <SimpleTooltip
      asChild
      tooltipClassName='bg-white border border-gray-300 rounded-[2px] shadow-[0px_1px_3px_rgba(0,0,0,0.3)] p-1'
      side='top'
      align='end'
      tooltipDelay={250}
      content={
        <div className='flex items-center gap-0.5'>
          {items.map((item, index) => (
            <Fragment key={item.text}>
              {index > 0 && <Separator orientation='vertical' className='h-4' />}
              <TooltipButton {...item} />
            </Fragment>
          ))}
        </div>
      }
    >
      <div>{children}</div>
    </SimpleTooltip>
  );
}
