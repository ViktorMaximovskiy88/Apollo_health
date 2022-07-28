import { Form, Button, DatePicker } from 'antd';
import { DateTime } from 'luxon';
import { Dropdown, Menu } from 'antd';
import { useState } from 'react';
import { prettyDate, prettyFromISO, dateToMoment } from '../common';
import { FormInstance } from 'antd';
import { DownOutlined } from '@ant-design/icons';
import classNames from 'classnames';

export function ListDatePicker(props: {
  className?: string;
  dateList?: string[];
  form: FormInstance;
  defaultValue?: string;
  label: string;
  name: string;
  disabled?: boolean;
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
    disabled = false,
    onChange = () => {},
  } = props;

  const defaultDate = dateToMoment(defaultValue);
  const [value, setValue] = useState(defaultDate);

  const dateOptions = (dateList || [])
    .map((d) => ({
      key: prettyFromISO(d, DateTime.DATE_MED, false),
      label: prettyFromISO(d, DateTime.DATE_MED, false),
    }))
    .sort((a, b) => +new Date(b.key) - +new Date(a.key));

  const menu = (
    <Menu
      onClick={(e: any) => {
        const value = dateToMoment(e.key);
        setValue(value);
        form.setFieldsValue({
          [name]: value,
        });
      }}
      items={dateOptions}
    />
  );

  return (
    <Form.Item name={name} className={classNames(className)} label={label} style={style}>
      <DatePicker
        disabled={disabled}
        style={{ borderTopRightRadius: 0, borderBottomRightRadius: 0 }}
        defaultValue={defaultDate}
        value={value}
        onChange={(value: any) => {
          setValue(value);
          form.setFieldsValue({
            [name]: value,
          });
          onChange();
        }}
        format={(value) => prettyDate(value.toDate())}
      />

      <Dropdown
        disabled={disabled || dateOptions.length === 0}
        overlay={menu}
        trigger={['click']}
        placement="bottomRight"
      >
        <Button
          style={{
            borderLeft: 'none',
            borderTopLeftRadius: 0,
            borderBottomLeftRadius: 0,
          }}
        >
          <DownOutlined />
        </Button>
      </Dropdown>
    </Form.Item>
  );
}
