import { Button, Dropdown, Space, Menu, Tag } from 'antd';
import { SyncOutlined, DownOutlined } from '@ant-design/icons';
import { setSiteTableQuickFilter, siteTableState } from '../../app/uiSlice';
import { useDispatch, useSelector } from 'react-redux';

enum QuickFilter {
  AssignedToMe = 'ASSIGNED_TO_ME',
  FailedLastSevenDaysAndUnassigned = 'FAILED_LAST_SEVEN_DAYS_AND_UNASSIGNED',
  FailedLastSevenDays = 'FAILED_LAST_SEVEN_DAYS',
}
function QuickFilterComponent() {
  const { quickFilter } = useSelector(siteTableState);
  const dispatch = useDispatch();
  const reset = () => {
    dispatch(
      setSiteTableQuickFilter({
        assignedToMe: false,
        setFailedLastSevenDays: false,
        unassigned: false,
      })
    );
  };
  const onMenuSelect = (key: QuickFilter) => {
    switch (key) {
      case QuickFilter.FailedLastSevenDays:
        return dispatch(
          setSiteTableQuickFilter({
            assignedToMe: false,
            unassigned: false,
            failedLastSevenDays: true,
          })
        );
      case QuickFilter.FailedLastSevenDaysAndUnassigned:
        return dispatch(
          setSiteTableQuickFilter({
            assignedToMe: false,
            unassigned: true,
            failedLastSevenDays: true,
          })
        );
      case QuickFilter.AssignedToMe:
        return dispatch(
          setSiteTableQuickFilter({
            assignedToMe: true,
            unassigned: false,
            setFailedLastSevenDays: false,
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
          key: QuickFilter.FailedLastSevenDaysAndUnassigned,
          label: 'Failed last 7 days & Unassigned',
          disabled: true,
        },
        {
          key: QuickFilter.FailedLastSevenDays,
          label: 'Failed last 7 days',
        },
      ]}
    />
  );
  return (
    <>
      {quickFilter.assignedToMe ? <Tag color="cyan">Assigned To Me</Tag> : null}
      {quickFilter.unassigned ? <Tag color="blue">Unassigned</Tag> : null}
      {quickFilter.failedLastSevenDays ? <Tag color="geekblue">Failed Last Seven Days</Tag> : null}
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
