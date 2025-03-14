import { useRedirectWithParams } from '@/lib/queryString';
import { RunItemV1, VersionV1 } from '@/types/workflowAI';
import { TaskRunTableRow } from './TaskRunTableRow';

type TaskRunTableProps = {
  runItems: RunItemV1[];
  versionsDictionary: Record<string, VersionV1>;
  isInitialized: boolean;
  redirectWithParams: ReturnType<typeof useRedirectWithParams>;
};

export function TaskRunTableContent(props: TaskRunTableProps) {
  const { runItems, versionsDictionary, redirectWithParams } = props;

  return (
    <div className='flex flex-col w-full h-full overflow-y-auto pb-2 px-2 border-l border-r border-b rounded-[2px] border-gray-200 bg-gradient-to-b from-white/50 to-white/0'>
      {runItems.map((runItem) => {
        return (
          <TaskRunTableRow
            key={runItem.id}
            runItem={runItem}
            version={
              !!runItem.version.id
                ? versionsDictionary[runItem.version.id]
                : undefined
            }
            redirectWithParams={redirectWithParams}
          />
        );
      })}
    </div>
  );
}
