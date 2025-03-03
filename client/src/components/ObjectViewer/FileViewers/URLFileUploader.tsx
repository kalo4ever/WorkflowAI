import { useCallback, useState } from 'react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';

type URLFileUploaderProps = {
  onLoad: (url: string) => void;
};

export function URLFileUploader(props: URLFileUploaderProps) {
  const { onLoad } = props;
  const [url, setUrl] = useState('');

  const onUrlChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setUrl(e.target.value);
  }, []);

  const onLoadClick = useCallback(() => {
    onLoad(url);
  }, [url, onLoad]);

  return (
    <div className='w-full flex items-center gap-2'>
      <Input
        type='text'
        placeholder='Or paste a URL here'
        value={url}
        onChange={onUrlChange}
        className='rounded-[2px] border-gray-300 h-9 font-lato font-normal text-[13px]'
      />
      <Button variant='newDesignIndigo' onClick={onLoadClick} disabled={!url}>
        Upload
      </Button>
    </div>
  );
}
