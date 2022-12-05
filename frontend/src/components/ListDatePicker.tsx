import { Button, DatePicker } from 'antd';
import { DateTime } from 'luxon';
import { Dropdown, Menu } from 'antd';
import { prettyDate, prettyFromISO, dateToMoment } from '../common';
import { DownOutlined } from '@ant-design/icons';

export function ListDatePicker(props: {
  dateList?: string[];
  disabled?: boolean;
  value?: string;
  onChange?: Function;
}) {
  /*
   *  Togglable date picker to select a custom date, or a date from a predefined list.
   */
  const { dateList, value, disabled = false, onChange = () => {} } = props;

  const valueDate = dateToMoment(value);

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
        onChange(value);
      }}
      items={dateOptions}
    />
  );

  return (
    <>
      <DatePicker
        disabled={disabled}
        style={{ borderTopRightRadius: 0, borderBottomRightRadius: 0 }}
        value={valueDate}
        onChange={(value: any) => {
          onChange(value);
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
    </>
  );
}
