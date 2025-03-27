import { cx } from 'class-variance-authority';
import Image from 'next/image';
import { cn } from '@/lib/utils';

type CompliantInformationSectionEntryProps = {
  imageURL: string;
  title: string;
  body: string;
};

export function CompliantInformationSectionEntry(props: CompliantInformationSectionEntryProps) {
  const { imageURL, title, body } = props;
  return (
    <div className='flex flex-col bg-[#FAF7F5] rounded-[8px] p-11 gap-11'>
      <div className='relative w-full'>
        <div className='w-full' style={{ paddingTop: '50%' }}></div>
        <div className='absolute inset-0 flex items-center justify-center border border-gray-100 rounded-[4px]'>
          <Image src={imageURL} alt='Logo' key={imageURL} className='object-cover' height={232} width={458} />
        </div>
      </div>
      <div className='flex flex-col gap-2 w-full'>
        <div className='text-[20px] font-medium text-gray-900'>{title}</div>
        <div className='text-[16px] font-normal text-gray-500'>{body}</div>
      </div>
    </div>
  );
}

type CompliantInformationSectionProps = {
  className?: string;
};

export function CompliantInformationSection(props: CompliantInformationSectionProps) {
  const { className } = props;

  return (
    <div className={cn('flex flex-col gap-6 items-center px-16 w-full max-w-[1260px]', className)}>
      <div className={cx('grid grid-cols-1 sm:grid-cols-1 lg:grid-cols-2 gap-10')}>
        <CompliantInformationSectionEntry
          imageURL='https://workflowai.blob.core.windows.net/workflowai-public/landing/Compliant1.jpg'
          title='Your Data Belongs to You'
          body='We never use your data for LLM training, ensuring your information stays private and exclusively yours.'
        />
        <CompliantInformationSectionEntry
          imageURL='https://workflowai.blob.core.windows.net/workflowai-public/landing/Compliant2.jpg'
          title='SOC-2 Compliant'
          body='We ensure security and privacy standards, giving you confidence that your data is safe and handled responsibly.'
        />
      </div>
    </div>
  );
}
