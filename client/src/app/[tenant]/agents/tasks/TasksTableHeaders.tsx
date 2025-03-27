import { TableViewHeaderEntry } from '@/components/ui/TableView';

export function TasksTableHeaders() {
  return (
    <>
      <TableViewHeaderEntry title='AI agent' className='pl-2 flex-1' />
      <TableViewHeaderEntry title='Runs in last 7d' className='w-[100px]' />
      <TableViewHeaderEntry title='Cost' className='w-[57px]' />
    </>
  );
}
