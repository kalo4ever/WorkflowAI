import { CheckmarkCircleFilled, InfoRegular, OpenRegular } from '@fluentui/react-icons';
import Image from 'next/image';
import { Button } from '@/components/ui/Button';
import { cn } from '@/lib/utils';

type EmptyStateComponentEntry = {
  title: string;
  subtitle: string;
  state?: boolean;
  imageURL: string;
};

type EmptyStateComponentEntryViewProps = {
  entry: EmptyStateComponentEntry;
};

function EmptyStateComponentEntryView(props: EmptyStateComponentEntryViewProps) {
  const { entry } = props;
  return (
    <div className='flex flex-col bg-white rounded-[2px] max-w-[324px]'>
      <Image src={entry.imageURL} alt={entry.title} width={324} height={174} />
      <div className='flex flex-col p-4 gap-2 bg-white border-l border-r border-b border-gray-200 h-full'>
        <div className='flex flex-row gap-[10px] items-center'>
          {entry.state === true && <CheckmarkCircleFilled className='text-gray-200 w-6 h-6' />}
          {entry.state === false && <div className='w-[19px] h-[19px] rounded-full border border-gray-200' />}
          <div
            className={cn(
              'text-[16px] font-semibold ',
              entry.state === true ? 'line-through text-gray-400' : 'text-gray-700'
            )}
          >
            {entry.title}
          </div>
        </div>
        <div className='text-[13px] font-normal text-gray-500'>{entry.subtitle}</div>
      </div>
    </div>
  );
}

type EmptyStateComponentProps = {
  title: string;
  subtitle: string;
  info: string;
  documentationLink: string | undefined;
  entries: EmptyStateComponentEntry[];
};

export function EmptyStateComponent(props: EmptyStateComponentProps) {
  const { title, subtitle, info, documentationLink, entries } = props;
  return (
    <div className='flex flex-col h-full w-full overflow-hidden font-lato sm:px-24 px-2 sm:py-10 py-4 items-center'>
      <div className='text-[20px] font-medium text-gray-900'>{title}</div>
      <div className='text-[16px] font-normal text-gray-500 text-center max-w-[880px] pt-1'>{subtitle}</div>
      <div className='flex flex-wrap w-full gap-4 justify-center pt-10'>
        {entries.map((entry) => (
          <EmptyStateComponentEntryView key={entry.title} entry={entry} />
        ))}
      </div>
      <div className='flex flex-row gap-1 pt-12 items-center'>
        <InfoRegular className='text-gray-500 w-3 h-3' />
        <div className='text-[13px] font-normal text-gray-500'>{info}</div>
      </div>
      {documentationLink && (
        <Button
          variant='link'
          className='flex flex-row gap-1 pt-5 items-center'
          toRoute={documentationLink}
          openInNewTab={true}
        >
          <OpenRegular className='text-gray-800 w-4 h-4' />
          <div className='text-[13px] font-semibold text-gray-800 underline'>Read documentation</div>
        </Button>
      )}
    </div>
  );
}

{
  /* <h1 className='text-2xl font-bold'>{props.title}</h1>
      <p className='text-sm text-gray-500'>{props.subtitle}</p>
      <p className='text-sm text-gray-500'>{props.info}</p>
      {props.documentationLink && (
        <a href={props.documentationLink} className='text-sm text-gray-500'>
          {props.documentationLink}
        </a>
      )} */
}
