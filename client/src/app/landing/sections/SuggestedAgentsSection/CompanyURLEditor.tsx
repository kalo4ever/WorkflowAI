import { useCallback, useState } from 'react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { useRedirectWithParams } from '@/lib/queryString';
import { capitalizeCompanyURL, isCompanyURL } from '../untils';

type CompanyURLEditorProps = {
  companyURL: string;
  supportEditing: boolean;
};

export function CompanyURLEditor(props: CompanyURLEditorProps) {
  const { companyURL, supportEditing } = props;

  const [mode, setMode] = useState<'edit' | 'save'>('edit');
  const [text, setText] = useState(companyURL);

  const redirectWithParams = useRedirectWithParams();

  const onSave = useCallback(async () => {
    if (text.length === 0) {
      return;
    }

    const normalizedText = text.toLowerCase();

    setMode('edit');

    if (normalizedText === companyURL) {
      return;
    }

    if (isCompanyURL(normalizedText)) {
      redirectWithParams({
        params: {
          companyURL: normalizedText,
          descriptionOrCompanyURL: undefined,
        },
      });
      return;
    }

    redirectWithParams({
      params: {
        companyURL: undefined,
        descriptionOrCompanyURL: normalizedText,
      },
    });
  }, [redirectWithParams, text, companyURL]);

  return (
    <div className='flex flex-row items-center gap-2'>
      {mode === 'edit' || !supportEditing ? (
        <div className='text-[24px] font-semibold'>
          {capitalizeCompanyURL(companyURL)}
        </div>
      ) : (
        <Input
          value={text}
          onChange={(event) => setText(event.target.value)}
          autoFocus={true}
          className='text-[13px] text-gray-900 max-h-[34px] w-[240px] font-normal py-0 pr-0 pl-3 rounded-[2px]'
          onKeyDown={(event) => {
            if (event.key === 'Enter') {
              onSave();
            }
          }}
        />
      )}

      {supportEditing && (
        <Button
          variant='newDesignGray'
          onClick={() => (mode === 'edit' ? setMode('save') : onSave())}
          size='none'
          className='py-2 px-3'
        >
          {mode === 'edit' ? 'Edit' : 'Save'}
        </Button>
      )}
    </div>
  );
}
