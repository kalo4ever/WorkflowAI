import { TaskEnvironmentBadge } from '@/components/v2/TaskEnvironmentBadge';
import { VersionEnvironment } from '@/types/workflowAI';

type BenchmarkVersionEnvironmentsProps = {
  environments?: VersionEnvironment[];
};

export function BenchmarkVersionEnvironments(
  props: BenchmarkVersionEnvironmentsProps
) {
  const { environments } = props;

  return (
    <div className='flex flex-row gap-1'>
      {!!environments &&
        environments.map((environment) => (
          <div className='w-fit' key={environment}>
            <TaskEnvironmentBadge
              environment={environment}
              showIconOnly={environments.length > 1}
            />
          </div>
        ))}
    </div>
  );
}
