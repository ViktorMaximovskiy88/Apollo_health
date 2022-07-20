import { Form, Radio, Select, DatePicker } from 'antd';
import type { RadioChangeEvent } from 'antd';
import moment from 'moment';
import { useState } from 'react';
import { prettyDate, prettyDateFromISO, dateToMoment } from '../common';
import { FormInstance } from 'antd';

export function ListDatePicker(props: {
  className?: string;
  dateList?: string[];
  form: FormInstance;
  defaultValue?: string;
  label: string;
  name: string;
  style?: object;
  onChange?: Function;
}) {
  /*
   *  Togglable date picker to select a custom date, or a date from a predefined list.
   */
  const {
    className,
    dateList,
    form,
    defaultValue,
    label,
    name,
    style,
    onChange = () => {},
  } = props;

  const existsInList = (dateList || []).find((date) => date === defaultValue);

  const [selectionMethod, setSelectionMethod] = useState(existsInList ? 'list' : 'custom');

  function onSelectionMethodChange(e: RadioChangeEvent) {
    setSelectionMethod(e.target.value);
  }

  function handleOnChange(value?: moment.Moment | string | null) {
    const update: any = {};
    if (moment.isMoment(value)) {
      // if receiving value from date picker
      update[name] = value.utc().startOf('day').toISOString();
    } else if (value === undefined) {
      update[name] = null;
    } else {
      update[name] = value;
    }
    form.setFieldsValue(update);
    onChange();
  }

  const dateOptions = (dateList || [])
    .map((d) => ({
      value: d,
      label: prettyDateFromISO(d),
    }))
    .sort((a, b) => +new Date(b.value) - +new Date(a.value));

  const defaultDate = dateToMoment(defaultValue);

  return (
    <Form.Item className={className} label={label} style={style}>
      <Radio.Group
        className="mb-1"
        onChange={onSelectionMethodChange}
        defaultValue={selectionMethod}
      >
        <Radio value="list">From List</Radio>
        <Radio value="custom">Custom</Radio>
      </Radio.Group>

      <Form.Item name={name} noStyle preserve>
        {selectionMethod === 'list' && (
          <Select
            allowClear
            defaultValue={existsInList ? defaultValue : null}
            options={dateOptions}
            onChange={(value) => handleOnChange(value)}
          />
        )}

        {selectionMethod === 'custom' && (
          <DatePicker
            style={{ width: '100%' }}
            defaultValue={defaultDate}
            format={(value) => prettyDate(value.toDate())}
            onChange={(value) => handleOnChange(value)}
          />
        )}
      </Form.Item>
    </Form.Item>
  );
}
