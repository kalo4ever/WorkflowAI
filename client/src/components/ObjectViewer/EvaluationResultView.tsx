import { XCircle } from 'lucide-react';
import {
  HoverCard,
  HoverCardContent,
  HoverCardTrigger,
} from '@/components/ui/HoverCard';

type EvaluationResultViewProps = {
  error?: string;
  className?: string;
};

export function EvaluationResultView(props: EvaluationResultViewProps) {
  const { error, className } = props;
  if (!error) {
    return null;
  }
  return (
    <div className={className}>
      <HoverCard>
        <HoverCardContent className='px-[10px] py-[6px] bg-slate-700 text-white text-[14px] h-fit font-light items-center justify-center rounded-[14px] overflow-y-auto'>
          {error}
        </HoverCardContent>
        <HoverCardTrigger>
          <XCircle size={24} className='text-red-600' strokeWidth={2} />
        </HoverCardTrigger>
      </HoverCard>
    </div>
  );
}
