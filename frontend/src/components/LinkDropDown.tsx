import { DownOutlined } from '@ant-design/icons';
import classNames from 'classnames';
import { useEffect, useState, useRef } from 'react';

export function LinkDropDown({
  selectedOption,
  options,
  onSelect,
  width = 'w-full',
}: {
  selectedOption: any;
  options: any[];
  onSelect: any;
  width?: string;
}) {
  const [open, setOpen] = useState(false);
  const controlElement = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handler(e: any) {
      let internalClick = false;
      for (const el of e.path) {
        if (el === controlElement.current) {
          internalClick = true;
          break;
        }
      }
      if (!internalClick) {
        setOpen(false);
      } else {
        document.addEventListener('click', handler, { once: true });
      }
    }

    document.addEventListener('click', handler, { once: true });

    return () => {
      document.removeEventListener('click', handler);
    };
  }, [open, controlElement]);

  return (
    <div className="relative" ref={controlElement}>
      <div
        onClick={() => setOpen(!open)}
        className={classNames(
          'text-sky-600 flex items-center justify-between select-none cursor-pointer',
          width
        )}
      >
        <div>{selectedOption?.label}</div>
        <div className="mx-2">
          <DownOutlined />
        </div>
      </div>

      <div
        className={classNames(
          'bg-white border border-slate-200 border-solid absolute z-40',
          width,
          !open && ['hidden']
        )}
      >
        {options.map((option, index) => (
          <div
            className="cursor-pointer text-slate-800 p-2 border border-slate-50 border-solid hover:bg-slate-50 hover:text-sky-800"
            key={index}
            onClick={() => {
              onSelect(option, index);
              setOpen(false);
            }}
          >
            {option.label}
          </div>
        ))}
      </div>
    </div>
  );
}
