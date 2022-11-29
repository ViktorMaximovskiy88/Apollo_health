import { useEffect, useRef, useState } from 'react';

/**
 * Ideally you can pass in a function or just use this to trigger
 * another function due to a change (something went horribly wrong with the useCallback)
 * also makes it weird to switch arg postition... lets just play nice for now.
 * @param interval
 * @param future
 * @returns
 */
const useInterval = (interval: number, active: boolean = true, future?: Promise<any>) => {
  useEffect(() => {});
  let timer = useRef<NodeJS.Timeout>();
  const [isActive, setActive] = useState<boolean>(active);
  const [watermark, setWatermark] = useState<Date>();

  function startInterval() {
    setActive(true);
    timer.current = setInterval(() => {
      setWatermark(new Date());
    }, interval);
  }

  function stopInterval() {
    setActive(false);
    clearInterval(timer.current);
  }

  useEffect(() => {
    if (isActive) {
      startInterval();
    } else {
      stopInterval();
    }
    return () => stopInterval();
  }, [isActive]);

  return {
    setActive,
    isActive,
    watermark,
  };
};

export default useInterval;
