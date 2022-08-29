import { Spin } from 'antd';
import Select, { SelectProps } from 'antd/lib/select';
import debounce from 'lodash/debounce';
import { useCallback, useMemo, useRef, useState } from 'react';

export interface RemoteSelectProps<ValueType = any>
  extends Omit<SelectProps<ValueType | ValueType[]>, 'options' | 'children'> {
  fetchOptions: (search: string) => Promise<ValueType[]>;
  initialOptions?: ValueType[];
  debounceTimeout?: number;
}

export function RemoteSelect<
  ValueType extends { key?: string; label: React.ReactNode; value: string | number } = any
>({
  fetchOptions,
  initialOptions = [],
  debounceTimeout = 300,
  notFoundContent = null,
  ...props
}: RemoteSelectProps<ValueType>) {
  const [fetching, setFetching] = useState(false);
  const [options, setOptions] = useState<ValueType[] | undefined>();
  const fetchRef = useRef(0);

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
