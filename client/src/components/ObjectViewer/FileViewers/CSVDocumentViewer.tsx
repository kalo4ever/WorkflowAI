import { cx } from 'class-variance-authority';
import { maxBy } from 'lodash';
import { useMemo } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/Table';

const COMMON_DELIMITERS = [',', ';', '\t', '|'];

type CSVDocumentViewerProps = {
  decodedText: string;
  className?: string;
};

export function CSVDocumentViewer(props: CSVDocumentViewerProps) {
  const { decodedText, className } = props;

  const delimiter = useMemo(() => {
    const delimiterCounts = COMMON_DELIMITERS.map((d) => ({
      delimiter: d,
      count: (decodedText.match(new RegExp(`[${d}]`, 'g')) || []).length,
    }));
    return maxBy(delimiterCounts, 'count')?.delimiter;
  }, [decodedText]);

  const rows = useMemo(() => {
    return decodedText.split('\n').filter((row) => row.length > 0);
  }, [decodedText]);

  const headers = useMemo(() => {
    if (!delimiter) return [];
    return rows[0].split(delimiter);
  }, [rows, delimiter]);

  if (!delimiter) return decodedText;

  return (
    <div
      className={cx(
        'rounded-md border max-h-inherit [&>div]:border-0 [&>div]:max-h-inherit',
        className
      )}
    >
      <Table>
        <TableHeader>
          <TableRow>
            {headers.map((header) => (
              <TableHead key={header}>{header}</TableHead>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody>
          {rows.slice(1).map((row) => (
            <TableRow key={row}>
              {row.split(delimiter).map((cell) => (
                <TableCell key={cell}>{cell}</TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
