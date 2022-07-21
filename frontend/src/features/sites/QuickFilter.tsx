import { Button, Dropdown, Space, Menu, Spin, Tag } from 'antd';
import { SyncOutlined, DownOutlined } from '@ant-design/icons';
import { DateTime } from 'luxon';
import isEqual from 'lodash/isEqual';
import some from 'lodash/some';
import { initialState, setSiteTableFilter, setSiteTableSort, siteTableState } from './sitesSlice';
import { useDispatch, useSelector } from 'react-redux';
import { SiteStatus } from './siteStatus';
import { TypeSingleFilterValue } from '@inovua/reactdatagrid-community/types';

enum QuickFilter {
  AssignedToMe = 'ASSIGNED_TO_ME',
  OnHoldLastSevenDaysAndUnassigned = 'ON_HOLD_LAST_SEVEN_DAYS_AND_UNASSIGNED',
  OnHoldLastSevenDays = 'ON_HOLD_LAST_SEVEN_DAYS',
}

const sevenDaysAgo = DateTime.now().minus({ days: 7 }).toFormat('yyyy-MM-dd');

const sevenDaysFilter = {
  name: 'last_run_time',
  operator: 'after',
  type: 'date',
  value: sevenDaysAgo,
};

const onHoldFilter = {
  name: 'status',
  operator: 'eq',
  type: 'string',
  value: SiteStatus.QualityHold,
};

function removeQuickFilters(filters: TypeSingleFilterValue[]): TypeSingleFilterValue[] {
  return filters.filter((f) => !isEqual(f, sevenDaysFilter) && !isEqual(f, onHoldFilter));
}

interface QuickFilterPropTypes {
  isLoading: boolean;
}
function QuickFilterComponent({ isLoading = false }: QuickFilterPropTypes) {
  const siteTable = useSelector(siteTableState);
  const dispatch = useDispatch();

  const reset = () => {
    dispatch(setSiteTableSort(initialState.table.sort));
    let filters = siteTable.filter.slice();
    filters = removeQuickFilters(filters);
    return dispatch(setSiteTableFilter(filters));
  };

  const onMenuSelect = (key: QuickFilter) => {
    dispatch(setSiteTableSort({ name: 'last_run_time', dir: 1 }));
    switch (key) {
      case QuickFilter.OnHoldLastSevenDays:
        return dispatch(setSiteTableFilter([...siteTable.filter, sevenDaysFilter, onHoldFilter]));
      case QuickFilter.OnHoldLastSevenDaysAndUnassigned:
        return; // TODO: update when assign functionality added
      case QuickFilter.AssignedToMe:
        return; // TODO: update when assign functionality added
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

  const assignedToMe = false; // TODO: update when assign functionality added
  const unassigned = false; // TODO: update when assign functionality added
  const onHold = some(siteTable.filter, onHoldFilter);
  const lastSevenDays = some(siteTable.filter, sevenDaysFilter);

  return (
    <>
      {isLoading ? (
        <Spin size="small" />
      ) : (
        <div /> /* to keep Tags from moving left and right on load */
      )}
      {assignedToMe ? <Tag color="geekblue">Assigned To Me</Tag> : null}
      {unassigned ? <Tag color="cyan">Unassigned</Tag> : null}
      {onHold ? <Tag color="blue">Quality Hold</Tag> : null}
      {lastSevenDays ? <Tag color="magenta">Last 7 Days</Tag> : null}
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
