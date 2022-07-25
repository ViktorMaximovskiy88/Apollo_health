import { Form, Button, Select, DatePicker } from 'antd';
import { Dropdown, Menu } from 'antd';
import moment from 'moment';
import { useState } from 'react';
import { prettyDate, prettyFromISO, prettyDateFromISO, dateToMoment } from '../common';
import { FormInstance } from 'antd';
import { DownOutlined } from '@ant-design/icons';

function ButtonFocus(hasFocus: boolean) {
  return hasFocus
    ? {
        borderColor: '#40a9ff',
        boxShadow: '0 0 0 2px rgb(24 144 255 / 20%)',
        clipPath: 'inset(-5px -5px -5px 0px)',
        outline: 0,
      }
    : {};
}

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
    onChange = () => {},
    disabled = false,
  } = props;

  const [hasFocus, setHasFocus] = useState(false);

  const defaultDate = dateToMoment(defaultValue);
  const [value, setValue] = useState(defaultDate);

  const dateOptions = (dateList || [])
    .map((d) => ({
      key: prettyDateFromISO(d),
      label: prettyDateFromISO(d),
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
    <div className="flex">
      <Form.Item className={className} label={label} style={style}>
        <DatePicker
          name={name}
          disabled={disabled}
          style={{ borderRight: 'none', borderTopRightRadius: 0, borderBottomRightRadius: 0 }}
          defaultValue={defaultDate}
          value={value}
          onChange={(value: any) => {
            setValue(value);
            form.setFieldsValue({
              [name]: value,
            });
          }}
          format={(value) => prettyDate(value.toDate())}
          onFocus={() => {
            setHasFocus(true);
          }}
          onBlur={() => {
            setHasFocus(false);
          }}
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
              ...ButtonFocus(hasFocus),
            }}
          >
            <DownOutlined />
          </Button>
        </Dropdown>
      </Form.Item>
    </div>
  );
}
