import { Spin } from 'antd';
import Select, { SelectProps } from 'antd/lib/select';
import debounce from 'lodash/debounce';
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';

export interface RemoteSelectProps<ValueType = any>
  extends Omit<SelectProps<ValueType | ValueType[]>, 'options' | 'children'> {
  fetchOptions: (search: string) => Promise<ValueType[]>;
  initialOptions?: ValueType[];
  debounceTimeout?: number;
  additionalOptions?: ValueType[];
}

export function RemoteSelect<
  ValueType extends { key?: string; label: React.ReactNode; value: string | number } = any
>({
  fetchOptions,
  initialOptions = [],
  debounceTimeout = 300,
  notFoundContent = null,
  additionalOptions = [],
  ...props
}: RemoteSelectProps<ValueType>) {
  const [fetching, setFetching] = useState(false);
  const [options, setOptions] = useState<ValueType[] | undefined>();
  const fetchRef = useRef(0);

  useEffect(() => {
    setOptions((prevState) => {
      if (prevState && additionalOptions) {
        return [...prevState, ...additionalOptions];
      }

      return undefined;
    });
  }, [additionalOptions]);

  const debounceFetcher = useMemo(() => {
    const loadOptions = (value: string) => {
      fetchRef.current += 1;
      const fetchId = fetchRef.current;
      setOptions([]);
      setFetching(true);

      fetchOptions(value).then((newOptions) => {
        if (fetchId !== fetchRef.current) {
          return;
        }

        setOptions(newOptions);
        setFetching(false);
      });
    };

    return debounce(loadOptions, debounceTimeout);
  }, [fetchOptions, debounceTimeout]);

  const onBlur = useCallback(() => {
    setOptions([]);
    debounceFetcher('');
  }, [setOptions, debounceFetcher]);

  return (
    <Select
      showSearch
      filterOption={false}
      onSearch={debounceFetcher}
      onFocus={onBlur}
      notFoundContent={fetching ? <Spin size="small" /> : notFoundContent}
      loading={fetching}
      {...props}
      options={options || initialOptions}
    />
  );
}
