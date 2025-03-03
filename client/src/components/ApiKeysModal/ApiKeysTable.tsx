import { Delete16Filled } from '@fluentui/react-icons';
import dayjs from 'dayjs';
import { orderBy } from 'lodash';
import { useCallback, useMemo, useState } from 'react';
import { Badge } from '@/components/ui/Badge';
import { User } from '@/types/user';
import { APIKeyResponse } from '@/types/workflowAI';
import { AlertDialog } from '../ui/AlertDialog';
import { UserAvatar } from '../ui/Avatar/UserAvatar';
import { Button } from '../ui/Button';
import { LoginSignUpPlaceholder } from '../ui/LoginSignUpPlaceholder';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../ui/Table';

function formatDate(date: string | null) {
  if (!date) {
    return '';
  }
  return dayjs(date).format('MMM D, YYYY');
}

const rowClassNames = 'grid grid-cols-[200px_120px_120px_120px_150px_80px]';

type ApiKeyRowProps = {
  apiKey: APIKeyResponse;
  user: User | undefined;
  setDeleteId: (id: string) => void;
};

function ApiKeyRow(props: ApiKeyRowProps) {
  const { apiKey, user, setDeleteId } = props;

  const handleDelete = useCallback(
    () => setDeleteId(apiKey.id),
    [setDeleteId, apiKey.id]
  );

  return (
    <TableRow className={rowClassNames}>
      <TableCell>
        <div className='truncate' title={apiKey.name}>
          {apiKey.name}
        </div>
      </TableCell>
      <TableCell>
        {!!user && (
          <UserAvatar
            tooltipText={`${user.firstName} ${user.lastName}`}
            user={user}
          />
        )}
      </TableCell>
      <TableCell>{formatDate(apiKey.created_at)}</TableCell>
      <TableCell>{formatDate(apiKey.last_used_at)}</TableCell>
      <TableCell>
        <Badge variant='tertiaryWithHover'>{apiKey.partial_key}</Badge>
      </TableCell>
      <TableCell>
        <Button
          icon={<Delete16Filled />}
          variant='destructive'
          onClick={handleDelete}
          size='icon-sm'
        />
      </TableCell>
    </TableRow>
  );
}

type ApiKeysModalContentProps = {
  apiKeys: APIKeyResponse[];
  usersByID: Record<string, User>;
  onDelete: (id: string) => Promise<void>;
  isLogged: boolean;
};

export function ApiKeysTable(props: ApiKeysModalContentProps) {
  const { apiKeys, usersByID, onDelete, isLogged } = props;
  const [deleteId, setDeleteId] = useState<string | null>(null);

  const orderedApiKeys = useMemo(
    () => orderBy(apiKeys, ['created_at'], ['desc']),
    [apiKeys]
  );

  const onConfirmDelete = useCallback(async () => {
    if (!deleteId) {
      return;
    }
    await onDelete(deleteId);
    setDeleteId(null);
  }, [deleteId, onDelete]);

  const onCancelDelete = useCallback(() => {
    setDeleteId(null);
  }, [setDeleteId]);

  if (!isLogged) {
    return <LoginSignUpPlaceholder className='w-[500px] flex-1' />;
  }

  if (apiKeys.length === 0) {
    return (
      <div className='flex-1 w-[500px] flex items-center justify-center text-gray-500'>
        <div className='text-lg'>No Secret Keys found</div>
      </div>
    );
  }

  return (
    <>
      <Table className='h-full overflow-auto' gridMode>
        <TableHeader>
          <TableRow className={rowClassNames}>
            <TableHead>Name</TableHead>
            <TableHead>Created By</TableHead>
            <TableHead>Created On</TableHead>
            <TableHead>Last Used</TableHead>
            <TableHead>Secret Key</TableHead>
            <TableHead></TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {orderedApiKeys.map((apiKey) => (
            <ApiKeyRow
              key={apiKey.id}
              apiKey={apiKey}
              user={usersByID[apiKey.created_by?.user_id ?? '']}
              setDeleteId={setDeleteId}
            />
          ))}
        </TableBody>
      </Table>
      <AlertDialog
        open={!!deleteId}
        title='Revoke Secret Key'
        text="This API key will immediately be disabled. API requests made using this key will be rejected, which could cause any systems still depending on it to break. Once revoked, you'll no longer be able to view or modify this API key."
        confrimationText='Revoke Key'
        onConfirm={onConfirmDelete}
        onCancel={onCancelDelete}
        destructive
      />
    </>
  );
}
