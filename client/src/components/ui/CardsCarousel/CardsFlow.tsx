import { useCallback, useEffect, useRef, useState } from 'react';
import { CardsCarouselEntryContent } from './CarouselCard';
import { CarouselFlowCard } from './CarouselFlowCard';

type CardsFlowProps = {
  scrollContainerRef: React.RefObject<HTMLDivElement>;
  entryContent: CardsCarouselEntryContent[];
};

export function CardsFlow(props: CardsFlowProps) {
  const { scrollContainerRef, entryContent } = props;
  const cardRefs = useRef<(HTMLDivElement | null)[]>([]);
  const [currentPage, setCurrentPage] = useState<number | undefined>(undefined);

  const handleScroll = useCallback(() => {
    const scrollContainer = scrollContainerRef.current;

    if (!scrollContainer) return;

    let page: number = -1;

    cardRefs.current.forEach((card, index) => {
      if (!card) return;

      const containerRect = scrollContainer.getBoundingClientRect();
      const cardRect = card.getBoundingClientRect();

      const middleY = containerRect.top + containerRect.height / 2;
      const begin = cardRect.top;
      const end = cardRect.bottom;

      if (index === 0 && page === -1 && begin < middleY) {
        page = 0;
      }

      if (end < middleY) {
        page += 1;
        return;
      }

      if (begin > middleY) {
        return;
      }

      const progress = (middleY - begin) / (end - begin);
      page += progress;
    });

    setCurrentPage(page);
  }, [scrollContainerRef, setCurrentPage]);

  useEffect(() => {
    const scrollContainer = scrollContainerRef.current;

    if (scrollContainer) {
      scrollContainer.addEventListener('scroll', handleScroll);
    }

    return () => {
      if (scrollContainer) {
        scrollContainer.removeEventListener('scroll', handleScroll);
      }
    };
  }, [scrollContainerRef, handleScroll]);

  return (
    <div className='flex flex-col'>
      {entryContent.map((entry, index) => (
        <div key={index} ref={(element) => (cardRefs.current[index] = element)}>
          <CarouselFlowCard
            entry={entry}
            page={index}
            currentPage={currentPage}
          />
        </div>
      ))}
    </div>
  );
}
