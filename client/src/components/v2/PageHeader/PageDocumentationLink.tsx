import { InfoRegular } from '@fluentui/react-icons';
import { Button } from '@/components/ui/Button';
import { cn } from '@/lib/utils';

type PageDocumentationLinkProps = {
  name: string | React.ReactNode;
  documentationLink?: string;
  className?: string;
};

export function PageDocumentationLink(props: PageDocumentationLinkProps) {
  const { name, documentationLink, className } = props;

  return (
    <div className={cn('flex flex-row items-center', className)}>
      <div className='ml-3 text-[13px] font-semibold text-gray-900'>{name}</div>
      {documentationLink && (
        <Button
          variant='text'
          icon={<InfoRegular className='w-4 h-4' />}
          toRoute={documentationLink}
          target='_blank'
          rel='noopener noreferrer'
          size='none'
          className='text-indigo-500 items-center w-6 h-6'
        />
      )}
    </div>
  );
}
