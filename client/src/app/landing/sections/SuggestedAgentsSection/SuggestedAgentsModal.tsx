'use client';

import { Dismiss12Regular } from '@fluentui/react-icons';
import { Button } from '@/components/ui/Button';
import { Dialog, DialogContent } from '@/components/ui/Dialog';
import {
  SUGGESTED_AGENTS_MODAL_OPEN,
  useQueryParamModal,
} from '@/lib/globalModal';
import { useParsedSearchParams } from '@/lib/queryString';
import { SuggestedAgentsSection } from './SuggestedAgentsSection';

export function useSuggestedAgentsModal() {
  return useQueryParamModal(SUGGESTED_AGENTS_MODAL_OPEN);
}

export function SuggestedAgentsModal() {
  const { open, closeModal: onClose } = useSuggestedAgentsModal();
  const { companyURL } = useParsedSearchParams('companyURL');

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className='min-w-[90vw] h-[90vh] p-0'>
        <div className='flex flex-col h-full w-full overflow-hidden bg-custom-gradient-1 rounded-[3px]'>
          <div className='flex items-center px-4 justify-between h-[60px] flex-shrink-0 border-b border-gray-200 border-dashed'>
            <div className='flex items-center py-1.5 gap-4 text-gray-700 text-base font-medium font-lato'>
              <Button
                onClick={onClose}
                variant='newDesign'
                icon={<Dismiss12Regular className='w-3 h-3' />}
                className='w-7 h-7'
                size='none'
              />
              New AI Agent
            </div>
          </div>
          {!!companyURL && (
            <SuggestedAgentsSection
              companyURL={companyURL}
              landingPageMode={false}
            />
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
