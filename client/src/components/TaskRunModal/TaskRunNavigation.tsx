import { ChevronDown12Regular, ChevronUp12Regular, Dismiss12Regular } from '@fluentui/react-icons';
import { Button } from '@/components/ui/Button';

type TaskRunNavigationProps = {
  taskRunIndex: number;
  totalModalRuns: number;
  onPrev?: () => void;
  onNext?: () => void;
  onClose: () => void;
};

export function TaskRunNavigation(props: TaskRunNavigationProps) {
  const { taskRunIndex, totalModalRuns, onClose, onPrev, onNext } = props;
  return (
    <div className='flex flex-row gap-2 items-center w-full'>
      <Button
        onClick={onClose}
        variant='newDesign'
        icon={<Dismiss12Regular className='w-3 h-3' />}
        className='w-7 h-7'
        size='none'
      />

      <span className='text-gray-900 text-[16px] font-semibold px-2'>
        {totalModalRuns > 1 ? `Run ${taskRunIndex + 1} of ${totalModalRuns}` : 'Run'}
      </span>

      {totalModalRuns > 1 && (
        <>
          <Button
            disabled={!onPrev}
            onClick={onPrev}
            variant='newDesign'
            icon={<ChevronUp12Regular className='w-3 h-3' />}
            className='w-7 h-7'
            size='none'
          />
          <Button
            disabled={!onNext}
            onClick={onNext}
            variant='newDesign'
            icon={<ChevronDown12Regular className='w-3 h-3' />}
            className='w-7 h-7'
            size='none'
          />
        </>
      )}
    </div>
  );
}
