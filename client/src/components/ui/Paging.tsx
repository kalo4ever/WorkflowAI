import { cx } from 'class-variance-authority';
import { useCallback, useMemo } from 'react';
import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from '@/components/ui/Pagination';

type PagingProps = {
  numberOfPages: number;
  currentPage: number;
  onPageSelected: (index: number) => void;
  className?: string;
};

const MAXIMAL_NUMBER_OF_PAGES_ON_LEFT_SIDE = 5;
const MAXIMAL_NUMBER_OF_PAGES_ON_RIGHT_SIDE = 1;

export function Paging(props: PagingProps) {
  const { numberOfPages, currentPage, onPageSelected, className } = props;

  /*
  This is a paging component that is used to paginate through a list of items.
  We have three sections:
  - Front pages: the first MAXIMAL_NUMBER_OF_PAGES_ON_LEFT_SIDE pages
  - Middle pages: the pages in between the front and back pages, separated by potential ellipsises
  - Back pages: the last MAXIMAL_NUMBER_OF_PAGES_ON_RIGHT_SIDE pages
  */

  const frontPages: number[] = useMemo(() => {
    const result: number[] = [];
    for (
      let index = 0;
      result.length < MAXIMAL_NUMBER_OF_PAGES_ON_LEFT_SIDE &&
      index < numberOfPages;
      index++
    ) {
      result.push(index);
    }
    return result;
  }, [numberOfPages]);

  const lastFrontPage = frontPages[frontPages.length - 1] ?? 0;

  const middlePages: number[] = useMemo(() => {
    const result: number[] = [];

    if (currentPage - 1 > lastFrontPage) {
      result.push(currentPage - 1);
    }

    if (currentPage > lastFrontPage) {
      result.push(currentPage);
    }

    if (currentPage + 1 > lastFrontPage && currentPage + 1 < numberOfPages) {
      result.push(currentPage + 1);
    }

    return result;
  }, [numberOfPages, currentPage, lastFrontPage]);

  const firstMiddlePage = middlePages[0] ?? lastFrontPage;
  const lastMiddlePage = middlePages[middlePages.length - 1] ?? lastFrontPage;

  const backPages: number[] = useMemo(() => {
    const result: number[] = [];
    for (
      let index = numberOfPages - 1;
      index >= 0 &&
      index > lastFrontPage &&
      index > lastMiddlePage &&
      result.length < MAXIMAL_NUMBER_OF_PAGES_ON_RIGHT_SIDE;
      index--
    ) {
      result.unshift(index);
    }
    return result;
  }, [numberOfPages, lastFrontPage, lastMiddlePage]);

  const firstBackPage = backPages[0] ?? lastMiddlePage;

  const onPreviousePage = useCallback(() => {
    const newPage = currentPage - 1;
    if (newPage >= 0 && newPage < numberOfPages) {
      onPageSelected(newPage);
    }
  }, [numberOfPages, currentPage, onPageSelected]);

  const onNextPage = useCallback(() => {
    const newPage = currentPage + 1;
    if (newPage >= 0 && newPage < numberOfPages) {
      onPageSelected(newPage);
    }
  }, [numberOfPages, currentPage, onPageSelected]);

  if (numberOfPages < 2) {
    return null;
  }

  const shouldShowFrontThreeDots = firstMiddlePage > lastFrontPage + 1;
  const shouldShowBackThreeDots = firstBackPage > lastMiddlePage + 1;

  const shouldShowPreviouse = numberOfPages > 1;
  const shouldShowNext = numberOfPages > 1;

  const getItemClassName = (isActive: boolean, isDisabled?: boolean) =>
    cx('rounded-[2px]', {
      'bg-gray-200 border border-gray-300 shadow-inner hover:bg-gray-200 cursor-pointer':
        isActive && !isDisabled,
      'bg-white shadow-sm border border-gray-200 hover:bg-gray-100 cursor-pointer':
        !isActive && !isDisabled,
      'bg-gray-100/60 text-gray-300': isDisabled,
    });

  return (
    <div className={cx('flex w-full', className)}>
      <Pagination className='text-gray-800 font-lato text-xs font-semibold items-start justify-center'>
        <PaginationContent>
          {shouldShowPreviouse && (
            <PaginationItem>
              <PaginationPrevious
                onClick={onPreviousePage}
                className={getItemClassName(false, currentPage === 0)}
              />
            </PaginationItem>
          )}

          {frontPages.map((page) => (
            <PaginationItem key={page}>
              <PaginationLink
                onClick={() => {
                  onPageSelected(page);
                }}
                isActive={currentPage === page}
                className={getItemClassName(currentPage === page)}
              >
                {page + 1}
              </PaginationLink>
            </PaginationItem>
          ))}

          {shouldShowFrontThreeDots && (
            <PaginationItem>
              <PaginationEllipsis />
            </PaginationItem>
          )}

          {middlePages.map((page) => (
            <PaginationItem key={page}>
              <PaginationLink
                onClick={() => {
                  onPageSelected(page);
                }}
                isActive={currentPage === page}
                className={getItemClassName(currentPage === page)}
              >
                {page + 1}
              </PaginationLink>
            </PaginationItem>
          ))}

          {shouldShowBackThreeDots && (
            <PaginationItem>
              <PaginationEllipsis />
            </PaginationItem>
          )}

          {backPages.map((page) => (
            <PaginationItem key={page}>
              <PaginationLink
                onClick={() => {
                  onPageSelected(page);
                }}
                isActive={currentPage === page}
                className={getItemClassName(currentPage === page)}
              >
                {page + 1}
              </PaginationLink>
            </PaginationItem>
          ))}

          {shouldShowNext && (
            <PaginationItem>
              <PaginationNext
                onClick={onNextPage}
                className={getItemClassName(
                  false,
                  currentPage === numberOfPages - 1
                )}
              />
            </PaginationItem>
          )}
        </PaginationContent>
      </Pagination>
    </div>
  );
}
