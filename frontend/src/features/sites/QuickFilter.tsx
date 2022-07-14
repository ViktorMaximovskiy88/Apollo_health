import { Button, Dropdown, Space, Menu, Tag } from 'antd';
import { SyncOutlined, DownOutlined } from '@ant-design/icons';
import {
  initialState,
  setSiteTableQuickFilter,
  setSiteTableSort,
  siteTableState,
} from '../../app/uiSlice';
import { useDispatch, useSelector } from 'react-redux';

enum QuickFilter {
  AssignedToMe = 'ASSIGNED_TO_ME',
  OnHoldLastSevenDaysAndUnassigned = 'ON_HOLD_LAST_SEVEN_DAYS_AND_UNASSIGNED',
  OnHoldLastSevenDays = 'ON_HOLD_LAST_SEVEN_DAYS',
}
function QuickFilterComponent() {
  const siteTable = useSelector(siteTableState);
  console.log(siteTable);
  const { quickFilter } = siteTable;
  const dispatch = useDispatch();
  const reset = () => {
    dispatch(setSiteTableSort(initialState.sites.table.sort));
    dispatch(
      setSiteTableQuickFilter({
        assignedToMe: false,
        setOnHoldLastSevenDays: false,
        unassigned: false,
      })
    );
  };
  const onMenuSelect = (key: QuickFilter) => {
    dispatch(setSiteTableSort({ name: 'last_run_time', dir: 1 }));
    switch (key) {
      case QuickFilter.OnHoldLastSevenDays:
        return dispatch(
          setSiteTableQuickFilter({
            assignedToMe: false,
            unassigned: false,
            onHoldLastSevenDays: true,
          })
        );
      case QuickFilter.OnHoldLastSevenDaysAndUnassigned:
        return dispatch(
          setSiteTableQuickFilter({
            assignedToMe: false,
            unassigned: true,
            onHoldLastSevenDays: true,
          })
        );
      case QuickFilter.AssignedToMe:
        return dispatch(
          setSiteTableQuickFilter({
            assignedToMe: true,
            unassigned: false,
            onHoldLastSevenDays: false,
          })
        );
    }
  };

  const menu = (
    <Menu
      onClick={({ key }) => onMenuSelect(key as QuickFilter)}
      items={[
        {
          key: QuickFilter.AssignedToMe,
          label: 'Assigned to me',
          disabled: true,
        },
        {
          key: QuickFilter.OnHoldLastSevenDaysAndUnassigned,
          label: 'On Hold last 7 days & Unassigned',
          disabled: true,
        },
        {
          key: QuickFilter.OnHoldLastSevenDays,
          label: 'On Hold last 7 days',
        },
      ]}
    />
  );
  return (
    <>
      {quickFilter.assignedToMe ? <Tag color="cyan">Assigned To Me</Tag> : null}
      {quickFilter.unassigned ? <Tag color="blue">Unassigned</Tag> : null}
      {quickFilter.onHoldLastSevenDays ? <Tag color="geekblue">On Hold Last 7 Days</Tag> : null}
      <Button onClick={reset}>
        <SyncOutlined />
      </Button>
      <Dropdown overlay={menu}>
        <Space>
          <Button>
            Quick Filters <DownOutlined className="text-sm" />
          </Button>
        </Space>
      </Dropdown>
    </>
  );
}

export { QuickFilterComponent as QuickFilter };
