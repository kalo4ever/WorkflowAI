import { EnvironmentIcon } from '@/components/icons/EnvironmentIcon';
import { SimpleTooltip } from '@/components/ui/Tooltip';
import { formatJoinedEnvironments } from '@/lib/environmentUtils';
import { VersionEnvironment } from '@/types/workflowAI';

type TaskRunEnvironmentsProps = {
  environments?: VersionEnvironment[];
  name?: string;
};

export function TaskRunEnvironments(props: TaskRunEnvironmentsProps) {
  const { environments, name = 'Version' } = props;

  return (
    <SimpleTooltip
      content={`${name} currently in ${formatJoinedEnvironments(environments)}.`}
      side='top'
      align='center'
    >
      <div className='flex flex-row gap-1 px-1.5 py-1 rounded-[2px] bg-gray-700 text-white items-center'>
        {!!environments &&
          environments.map((environment) => (
            <div className='flex items-start justify-center text-white' key={environment}>
              <EnvironmentIcon environment={environment} className='w-4 h-4' />
            </div>
          ))}
      </div>
    </SimpleTooltip>
  );
}
