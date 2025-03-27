import { useEffect, useRef, useState } from 'react';

type Refs = {
  containerRef: React.RefObject<HTMLElement>;
  inputSchemaRef: React.RefObject<HTMLElement>;
  inputPreviewRef: React.RefObject<HTMLElement>;
};

export function useResizeHeight({ containerRef, inputSchemaRef, inputPreviewRef }: Refs) {
  const sizesRef = useRef({
    containerHeight: 0,
    inputSchemaHeight: 0,
    inputPreviewHeight: 0,
  });

  const [inputHeight, setInputHeight] = useState(0);
  const [areRefsReady, setAreRefsReady] = useState(false);

  useEffect(() => {
    if (areRefsReady) return;

    const checkRefs = () => {
      if (containerRef.current && inputSchemaRef.current && inputPreviewRef.current) {
        setAreRefsReady(true);
        return true;
      }
      return false;
    };

    if (checkRefs()) return;

    const interval = setInterval(checkRefs, 100);
    return () => clearInterval(interval);
  }, [areRefsReady, containerRef, inputSchemaRef, inputPreviewRef]);

  useEffect(() => {
    if (!areRefsReady) return;

    const calculateHeight = () => {
      const newHeight = Math.max(
        sizesRef.current.inputSchemaHeight + 84,
        sizesRef.current.inputPreviewHeight + 84,
        sizesRef.current.containerHeight / 2.0
      );

      if (newHeight !== inputHeight) {
        setInputHeight(newHeight);
      }
    };

    const resizeObserver = new ResizeObserver((entries) => {
      for (const entry of entries) {
        if (entry.target === containerRef.current) {
          sizesRef.current.containerHeight = entry.contentRect.height;
        }
        if (entry.target === inputSchemaRef.current) {
          sizesRef.current.inputSchemaHeight = entry.contentRect.height;
        }
        if (entry.target === inputPreviewRef.current) {
          sizesRef.current.inputPreviewHeight = entry.contentRect.height;
        }
      }
      calculateHeight();
    });

    if (containerRef.current) {
      resizeObserver.observe(containerRef.current);
    }
    if (inputSchemaRef.current) {
      resizeObserver.observe(inputSchemaRef.current);
    }
    if (inputPreviewRef.current) {
      resizeObserver.observe(inputPreviewRef.current);
    }

    return () => resizeObserver.disconnect();
  }, [areRefsReady, containerRef, inputSchemaRef, inputPreviewRef, inputHeight]);

  return inputHeight;
}
