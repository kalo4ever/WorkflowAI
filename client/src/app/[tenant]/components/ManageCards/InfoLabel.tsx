import { Info16Regular } from '@fluentui/react-icons';

type InfoLabelProps = {
  text?: string;
  className?: string;
};

export function InfoLabel(props: InfoLabelProps) {
  const { text, className = 'px-4 py-3 flex w-full' } = props;

  if (!text) return null;

  return (
    <div className={className}>
      <div className='flex flex-row w-full items-center bg-indigo-50 rounded-[2px] border border-indigo-300'>
        <Info16Regular className='text-indigo-700 w-4 h-4 mx-3 flex-shrink-0' />
        <div className='text-[13px] font-normal text-indigo-700 pr-3 py-2'>{text}</div>
      </div>
    </div>
  );
}
