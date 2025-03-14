import { List, LucideIcon, Table } from 'lucide-react';
import { SelectableFieldType } from '@/lib/schemaEditorUtils';

type FieldTypeIconProps = {
  type: SelectableFieldType;
  onClick: () => void;
};

export function FieldTypeIcon(props: FieldTypeIconProps) {
  const { type, onClick } = props;

  let Icon: LucideIcon | undefined;
  if (type === 'object' || type === 'array') {
    Icon = List;
  } else if (type === 'enum') {
    Icon = Table;
  }

  if (!Icon) {
    return null;
  }

  return (
    <div
      className='border border-gray-200 flex items-center justify-center w-6 h-6 rounded-[2px] text-gray-500 cursor-pointer bg-white'
      onClick={onClick}
    >
      <Icon size={12} />
    </div>
  );
}
