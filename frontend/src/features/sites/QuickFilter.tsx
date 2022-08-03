import { Button, Dropdown, Space, Menu, Spin, Tag } from 'antd';
import { SyncOutlined, DownOutlined } from '@ant-design/icons';
import { DateTime } from 'luxon';
import isEqual from 'lodash/isEqual';
import some from 'lodash/some';
import { initialState, setSiteTableFilter, setSiteTableSort, siteTableState } from './sitesSlice';
import { useDispatch, useSelector } from 'react-redux';
import { SiteStatus } from './siteStatus';
import { TypeSingleFilterValue } from '@inovua/reactdatagrid-community/types';
import { useCurrentUser } from '../../common/hooks/use-current-user';

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

const unassignedFilter = { name: 'assignee', operator: 'empty', type: 'string', value: '' };

const buildAssignedToMeFilter = (userId?: string) => ({
  name: 'assignee',
  operator: 'eq',
  type: 'select',
  value: userId ?? 'WILL_BE_CURRENT_USER_ID',
});

function removeQuickFilters(
  filters: TypeSingleFilterValue[],
  assignedToMeFilter: TypeSingleFilterValue
): TypeSingleFilterValue[] {
  return filters.filter(
    (f) =>
      !isEqual(f, sevenDaysFilter) &&
      !isEqual(f, onHoldFilter) &&
      !isEqual(f, unassignedFilter) &&
      !isEqual(f, assignedToMeFilter)
  );
}

interface QuickFilterPropTypes {
  isLoading: boolean;
}
function QuickFilterComponent({ isLoading = false }: QuickFilterPropTypes) {
  const siteTable = useSelector(siteTableState);
  const dispatch = useDispatch();
  const currentUser = useCurrentUser();
  const assignedToMeFilter = buildAssignedToMeFilter(currentUser?._id);

  const reset = () => {
    dispatch(setSiteTableSort(initialState.table.sort));
    const filters = removeQuickFilters(siteTable.filter.slice(), assignedToMeFilter);
    return dispatch(setSiteTableFilter(filters));
  };

  const onMenuSelect = (key: QuickFilter) => {
    dispatch(setSiteTableSort({ name: 'last_run_time', dir: 1 }));
    const filters = removeQuickFilters(siteTable.filter.slice(), assignedToMeFilter);
    switch (key) {
      case QuickFilter.OnHoldLastSevenDays:
        return dispatch(setSiteTableFilter([...filters, sevenDaysFilter, onHoldFilter]));
      case QuickFilter.OnHoldLastSevenDaysAndUnassigned:
        return dispatch(
          setSiteTableFilter([...filters, sevenDaysFilter, onHoldFilter, unassignedFilter])
        );
      case QuickFilter.AssignedToMe:
        return dispatch(setSiteTableFilter([...filters, assignedToMeFilter]));
    }
  };

  const menu = (
    <Menu
      onClick={({ key }) => onMenuSelect(key as QuickFilter)}
      items={[
        {
          key: QuickFilter.AssignedToMe,
          label: 'Assigned to me',
        },
        {
          key: QuickFilter.OnHoldLastSevenDaysAndUnassigned,
          label: 'On Hold last 7 days & Unassigned',
        },
        {
          key: QuickFilter.OnHoldLastSevenDays,
          label: 'On Hold last 7 days',
        },
      ]}
    />
  );

  const assignedToMe = some(siteTable.filter, assignedToMeFilter);
  const unassigned = some(siteTable.filter, unassignedFilter);
  const onHold = some(siteTable.filter, onHoldFilter);
  const lastSevenDays = some(siteTable.filter, sevenDaysFilter);

  return (
    <>
      {isLoading ? (
        <Spin size="small" />
      ) : (
        <div /* to keep Tags from moving left and right on load */ />
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
