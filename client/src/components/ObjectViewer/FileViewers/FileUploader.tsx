import {
  ArrowUploadFilled,
  DocumentBulletListRegular,
} from '@fluentui/react-icons';
import { cx } from 'class-variance-authority';
import React, { useCallback, useMemo, useState } from 'react';
import { useRef } from 'react';
import { Loader } from '@/components/ui/Loader';
import { Progress } from '@/components/ui/Progress';
import { displayErrorToaster } from '@/components/ui/Sonner';

type FileUploadDragContentProps = {
  fileInputRef: React.RefObject<HTMLInputElement>;
  accept: string;
  text: string;
  handleImportClick: () => void;
  handleFileChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
};

function FileUploadDragContent(props: FileUploadDragContentProps) {
  const { fileInputRef, accept, text, handleImportClick, handleFileChange } =
    props;
  return (
    <div>
      <input
        type='file'
        ref={fileInputRef}
        accept={accept}
        onChange={handleFileChange}
        className='hidden'
      />
      <div
        onClick={handleImportClick}
        className='flex flex-col gap-1 items-center justify-center w-full h-full cursor-pointer'
      >
        <div className='flex items-center justify-center rounded-full text-white bg-gradient-image w-9 h-9 mb-2'>
          <ArrowUploadFilled className='w-5 h-5' />
        </div>
        <div className='text-sm font-medium text-gray-900 text-center'>
          Drag here or <span className='underline'>choose a file</span>
        </div>
        <div className='text-xs text-gray-500 font-normal text-center'>
          {text}
        </div>
      </div>
    </div>
  );
}

type FileUploadProgressProps = {
  progress?: number;
  fileName?: string;
};

function FileUploadProgress(props: FileUploadProgressProps) {
  const { progress, fileName } = props;
  const roundedProgress = progress ? Math.round(progress * 100) : undefined;
  return (
    <div className='flex items-center justify-start gap-2 h-full w-full'>
      <DocumentBulletListRegular className='shrink-0 w-5 h-5' />
      <div className='flex-1 flex flex-col gap-1 items-start text-gray-900 text-sm font-medium'>
        {fileName}
        {roundedProgress === 100 ? (
          <div className='flex items-center gap-2 text-gray-500'>
            <Loader size='xxsmall' />
            <div>Processing...</div>
          </div>
        ) : (
          <Progress value={roundedProgress} />
        )}
      </div>
    </div>
  );
}

type FileUploaderProps = {
  className?: string;
  onChange: (file: File) => void;
  accept: string;
  text: string;
  uploadProps?: {
    progress?: number;
    fileName?: string;
  };
};

export function FileUploader(props: FileUploaderProps) {
  const { className, onChange, accept, text, uploadProps } = props;

  const fileInputRef = useRef<HTMLInputElement>(null);

  const [isDragging, setIsDragging] = useState(false);
  const acceptedTypes = useMemo(() => accept.split(','), [accept]);

  const handleImportClick = useCallback(() => {
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    fileInputRef.current?.click();
  }, []);

  const handleDragEnter = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.stopPropagation();
    setIsDragging(false);
  }, []);

  const onChangeWithValidation = useCallback(
    (file: File) => {
      if (!acceptedTypes.includes(file.type)) {
        displayErrorToaster('Invalid file type');
        return;
      }
      onChange(file);
    },
    [onChange, acceptedTypes]
  );

  const handleDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();
      event.stopPropagation();
      setIsDragging(false);

      if (event.dataTransfer.files && event.dataTransfer.files.length > 0) {
        onChangeWithValidation(event.dataTransfer.files[0]);
        event.dataTransfer.clearData();
      }
    },
    [onChangeWithValidation]
  );

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      onChangeWithValidation(event.target.files[0]);
    }
  };

  const dragProps = !!uploadProps
    ? undefined
    : {
        onDragEnter: handleDragEnter,
        onDragOver: handleDragOver,
        onDragLeave: handleDragLeave,
        onDrop: handleDrop,
      };

  return (
    <div
      {...dragProps}
      className={cx(
        'h-[120px] flex flex-col w-full bg-white rounded-[2px] p-3 border border-gray-200 border-dashed font-lato',
        className,
        isDragging && !uploadProps && 'border-green-500'
      )}
    >
      {!!uploadProps ? (
        <FileUploadProgress {...uploadProps} />
      ) : (
        <FileUploadDragContent
          fileInputRef={fileInputRef}
          accept={accept}
          text={text}
          handleImportClick={handleImportClick}
          handleFileChange={handleFileChange}
        />
      )}
    </div>
  );
}
