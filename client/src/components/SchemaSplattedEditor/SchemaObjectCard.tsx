import { cx } from 'class-variance-authority';
import { Plus } from 'lucide-react';
import { Button } from '../ui/Button';

type SchemaObjectCardProps = {
  children: React.ReactNode;
  onAddField: (() => void) | undefined;
  className?: string;
};

export function SchemaObjectCard(props: SchemaObjectCardProps) {
  const { children, onAddField, className } = props;
  return (
    <div className={cx('w-fit', className)}>
      <div className='rounded-[2px] border border-gray-300 overflow-hidden'>
        <div className='p-2 bg-gray-100 text-gray-500 font-medium text-sm border-b border-gray-200 font-lato'>
          Object
        </div>
        <div className='flex flex-col bg-white'>
          <div className='p-2'>{children}</div>
          {onAddField && (
            <Button
              lucideIcon={Plus}
              variant='subtle'
              onClick={onAddField}
              className='w-fit ml-4 mb-2 mr-2 rounded-[2px] bg-gray-100 hover:bg-gray-200 text-gray-500 text-sm font-semibold font-lato'
            >
              Add New Field to Object
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
