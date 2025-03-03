type ApiContentSectionItemProps = {
  title: string;
  children: React.ReactNode;
};

export function ApiContentSectionItem(props: ApiContentSectionItemProps) {
  const { children, title } = props;
  return (
    <div className='flex flex-col gap-3'>
      <div className='text-[13px] font-medium text-gray-900'>{title}</div>
      {children}
    </div>
  );
}
