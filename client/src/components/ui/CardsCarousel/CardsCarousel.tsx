import { useEffect, useRef, useState } from 'react';
import useMeasure from 'react-use-measure';
import { CardsCarouselHeader } from './CardsCarouselHeader';
import { CardsCarouselEntryContent, CarouselCard } from './CarouselCard';

const MARGIN = 1024;
const INNER_MARGIN = 24;
const MAX_CARD_WIDTH = 846;

function calculatePage(
  offset: number,
  cardWidth: number,
  carouselWidth: number | undefined,
  innerMargin: number
) {
  if (!carouselWidth) {
    return 0;
  }

  const notCountedFirstCardOverscroll = carouselWidth - cardWidth;
  const result =
    (offset + notCountedFirstCardOverscroll) / (cardWidth + innerMargin);

  if (result < 1) {
    const beginningForFirstCard = notCountedFirstCardOverscroll;
    const endingForFirstCard = cardWidth + innerMargin;
    const ditanceForFirstCard = endingForFirstCard - beginningForFirstCard;
    return offset / ditanceForFirstCard;
  }

  return result;
}

type CardsCarouselProps = {
  scrollContainerRef: React.RefObject<HTMLDivElement>;
  entryContent: CardsCarouselEntryContent[];
};

export function CardsCarousel(props: CardsCarouselProps) {
  const { scrollContainerRef, entryContent } = props;

  const headerContainerRef = useRef<HTMLDivElement | null>(null);
  const [measureRef, { width: carouselWidth }] = useMeasure();

  const horizontalContainerRef = useRef<HTMLDivElement>(null);
  const [isHorizontalScroll, setIsHorizontalScroll] = useState(false);

  const [currentPage, setCurrentPage] = useState(0);

  const cardWidth = Math.min(MAX_CARD_WIDTH, carouselWidth);

  useEffect(() => {
    const handlePageScroll = () => {
      const scrollContainer = scrollContainerRef.current;
      const horizontalContainer = horizontalContainerRef.current;
      const headerContainer = headerContainerRef.current;

      if (!headerContainer || !horizontalContainer || !scrollContainer) {
        return;
      }

      const containerTop =
        headerContainer.getBoundingClientRect().top -
        scrollContainer.getBoundingClientRect().top;

      const horizontalContainerHeight =
        horizontalContainer.getBoundingClientRect().height;

      if (
        containerTop <= -horizontalContainerHeight &&
        horizontalContainer.scrollLeft === 0
      ) {
        setIsHorizontalScroll(false);
        horizontalContainer.scrollTo({
          left: horizontalContainer.scrollWidth,
          behavior: 'instant',
        });
        return;
      }

      if (containerTop <= 0 && horizontalContainer.scrollLeft === 0) {
        setIsHorizontalScroll(true);
        return;
      }

      if (containerTop >= 0 && horizontalContainer.scrollLeft > 0) {
        setIsHorizontalScroll(true);
        return;
      }
    };

    const scrollContainer = scrollContainerRef.current;

    if (scrollContainer) {
      scrollContainer.addEventListener('scroll', handlePageScroll);
    }

    return () => {
      if (scrollContainer) {
        scrollContainer.removeEventListener('scroll', handlePageScroll);
      }
    };
  }, [scrollContainerRef, headerContainerRef]);

  useEffect(() => {
    const scrollContainer = scrollContainerRef.current;

    const handleWheelScroll = (event: WheelEvent) => {
      const horizontalContainer = horizontalContainerRef.current;
      const headerContainer = headerContainerRef.current;

      if (
        !headerContainer ||
        !horizontalContainer ||
        !isHorizontalScroll ||
        !scrollContainer
      ) {
        return;
      }

      event.preventDefault();

      const top = headerContainer.getBoundingClientRect().top;

      scrollContainer.scrollTo({
        top: top + scrollContainer.scrollTop,
        behavior: 'instant',
      });

      horizontalContainer.scrollLeft += event.deltaY;

      setCurrentPage(
        calculatePage(
          horizontalContainer.scrollLeft,
          cardWidth,
          carouselWidth,
          INNER_MARGIN
        )
      );

      if (horizontalContainer.scrollLeft === 0 && event.deltaY < 0) {
        setIsHorizontalScroll(false);
        return;
      }

      if (
        Math.ceil(horizontalContainer.scrollLeft) ===
        Math.ceil(
          horizontalContainer.scrollWidth - horizontalContainer.clientWidth
        )
      ) {
        setIsHorizontalScroll(false);
        return;
      }
    };

    if (scrollContainer) {
      scrollContainer.addEventListener('wheel', handleWheelScroll, {
        passive: false,
      });
    }

    return () => {
      if (scrollContainer) {
        scrollContainer.removeEventListener('wheel', handleWheelScroll);
      }
    };
  }, [
    isHorizontalScroll,
    scrollContainerRef,
    cardWidth,
    carouselWidth,
    headerContainerRef,
  ]);

  return (
    <div
      ref={(element) => {
        headerContainerRef.current = element;
        measureRef(element);
      }}
      className='flex flex-col gap-10 pt-9'
    >
      <CardsCarouselHeader cardContent={entryContent} page={currentPage} />
      <style>{`div::-webkit-scrollbar { display: none; }`}</style>
      <div
        ref={horizontalContainerRef}
        className={`flex gap-[${INNER_MARGIN}px] overflow-x-auto overflow-y-hidden`}
        style={{
          width: `calc(100% + ${MARGIN * 2}px)`,
          marginLeft: `-${MARGIN}px`,
          scrollbarWidth: 'none',
          msOverflowStyle: 'none',
          WebkitOverflowScrolling: 'touch',
        }}
      >
        <div
          className='flex gap-6 w-max h-full items-stretch'
          style={{
            paddingLeft: `${MARGIN}px`,
            paddingRight: `${MARGIN}px`,
          }}
        >
          {entryContent.map((entry, index) => (
            <CarouselCard
              key={index}
              entry={entry}
              width={cardWidth}
              isSelected={Math.floor(currentPage) === index}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
