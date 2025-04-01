import { Link16Regular } from '@fluentui/react-icons';
import { useCopyCurrentUrl } from '@/lib/hooks/useCopy';
import { cn } from '@/lib/utils';
import { SerializableTask } from '@/types/workflowAI';
import { Button } from '../ui/Button';
import { Loader } from '../ui/Loader';
import { ExtendedBordersContainer } from './ExtendedBordersContainer';
import { PageHeader } from './PageHeader';

type PageContainerProps = {
  children: React.ReactNode;
  rightBarChildren?: React.ReactNode;
  rightBarText?: string;
  task: SerializableTask | undefined;
  isInitialized: boolean;
  name: string | React.ReactNode;
  showCopyLink?: boolean;
  showBottomBorder?: boolean;
  extraButton?: React.ReactNode;
  showSchema?: boolean;
  documentationLink?: string;
};

export function PageContainer(props: PageContainerProps) {
  const {
    children,
    rightBarChildren,
    rightBarText,
    task,
    isInitialized,
    name,
    showCopyLink = false,
    showBottomBorder = true,
    extraButton,
    showSchema = true,
    documentationLink,
  } = props;

  const copyUrl = useCopyCurrentUrl();

  if (!isInitialized) {
    return <Loader centered />;
  }

  if (!task) {
    return (
      <div className='flex flex-col h-full w-full font-lato p-6'>
        <ExtendedBordersContainer className='flex flex-col h-full w-full' borderColor='gray-100' margin={24}>
          <div
            className={cn(
              'flex items-center h-[48px] w-full flex-shrink-0 px-4 font-semibold text-base text-gray-700',
              showBottomBorder && 'border-b border-dashed border-gray-200'
            )}
          >
            {name}
          </div>
          <div className='flex h-[calc(100%-48px)] w-full'>{children}</div>
        </ExtendedBordersContainer>
      </div>
    );
  }

  return (
    <div className='flex flex-col h-full w-full font-lato p-6'>
      <ExtendedBordersContainer className='flex flex-col h-full w-full' borderColor='gray-100' margin={24}>
        <PageHeader
          task={task}
          name={name}
          documentationLink={documentationLink}
          className={cn(
            'flex items-center gap-2 h-[60px] flex-shrink-0 overflow-hidden',
            showBottomBorder && 'border-b border-dashed border-gray-200'
          )}
          showSchema={showSchema}
        >
          {!!rightBarText && <div className='text-gray-500 text-xs pr-1'>{rightBarText}</div>}
          {!!documentationLink && (
            <Button variant='newDesign' toRoute={documentationLink} target='_blank' rel='noopener noreferrer'>
              Documentation
            </Button>
          )}
          {extraButton}
          {showCopyLink && (
            <Button variant='newDesign' icon={<Link16Regular />} onClick={copyUrl} className='w-9 h-9 px-0 py-0' />
          )}
          {rightBarChildren}
        </PageHeader>
        <div className='flex h-[calc(100%-60px)] w-full'>{children}</div>
      </ExtendedBordersContainer>
    </div>
  );
}
