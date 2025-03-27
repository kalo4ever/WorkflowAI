import { KeyMultiple20Regular } from '@fluentui/react-icons';
import { cx } from 'class-variance-authority';
import { LayoutGrid } from 'lucide-react';

type SettingsSidebarItemProps = {
  icon: React.ReactNode;
  title: string;
  selected?: boolean;
  onClick?: () => void;
};

function SettingsSidebarItem(props: SettingsSidebarItemProps) {
  const { icon, title, selected, onClick } = props;
  return (
    <div
      className={cx(
        'flex items-center gap-2 p-2 cursor-pointer border-l-2 border-transparent transition-all hover:bg-indigo-50 hover:border-indigo-700 hover:text-indigo-700',
        selected ? 'bg-indigo-50 !border-indigo-700 text-indigo-700' : 'text-gray-600'
      )}
      onClick={onClick}
    >
      {icon}
      <div className='text-sm font-medium'>{title}</div>
    </div>
  );
}

type SettingsSidebarProps = {
  onOpenManageApiKeys: () => void;
};

export function SettingsSidebar(props: SettingsSidebarProps) {
  const { onOpenManageApiKeys } = props;
  return (
    <div className='h-full w-[240px] border-r flex flex-col py-3 px-5 text-slate-500'>
      <div className='text-2xl font-medium text-slate-900'>AI Agent Settings</div>
      <div className='text-xs text-slate-500 mb-3'>Manage your AI agent</div>
      <div className='flex flex-col gap-1'>
        <SettingsSidebarItem icon={<LayoutGrid size={24} />} title='General' selected />
        <SettingsSidebarItem icon={<KeyMultiple20Regular />} title='Manage Secret Keys' onClick={onOpenManageApiKeys} />
      </div>
    </div>
  );
}
