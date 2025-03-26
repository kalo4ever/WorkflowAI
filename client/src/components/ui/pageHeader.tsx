type PageHeaderProps = {
  icon?: React.ReactNode;
  title: string;
  children?: React.ReactNode;
  rightMargin?: number;
};

export function PageHeader(props: PageHeaderProps) {
  const { icon, title, children, rightMargin = 32 } = props;
  return (
    <div className={`flex felx-col items-center py-[16px] pr-[${rightMargin}px] gap-2`}>
      <div className='flex flex-row gap-2 text-slate-700 items-center'>
        {!!icon && icon}
        <div className='text-[32px] font-medium'>{title}</div>
      </div>
      <div className='flex-1 flex gap-2 justify-end items-center'>{children}</div>
    </div>
  );
}
