export function scrollTo(
  scrollContainerRef: React.RefObject<HTMLDivElement>,
  targetContainerRef: React.RefObject<HTMLDivElement>,
  offset: number = 0
) {
  if (scrollContainerRef.current && targetContainerRef.current) {
    const containerTop = scrollContainerRef.current.getBoundingClientRect().top;
    const top = targetContainerRef.current.getBoundingClientRect().top;
    scrollContainerRef.current.scrollTo({
      top: top - containerTop + scrollContainerRef.current.scrollTop - offset,
      behavior: 'smooth',
    });
  }
}
