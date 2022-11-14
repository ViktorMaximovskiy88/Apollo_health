import ReactDataGrid from '@inovua/reactdatagrid-community';
import { Button, Popconfirm, Tag } from 'antd';
import { Link } from 'react-router-dom';
import { useCallback } from 'react';
import {
  setUserTableFilter,
  setUserTableSort,
  setUserTableLimit,
  setUserTableSkip,
  userTableState,
} from './userSlice';
import { MainLayout } from '../../components';
import { ButtonLink } from '../../components/ButtonLink';
import { ChangeLogModal } from '../change-log/ChangeLogModal';
import { User } from './types';
import { useDeleteUserMutation, useGetChangeLogQuery, useGetUsersQuery } from './usersApi';
import { useDispatch, useSelector } from 'react-redux';
import { TypeFilterValue, TypeSortInfo } from '@inovua/reactdatagrid-community/types';
import SelectFilter from '@inovua/reactdatagrid-community/SelectFilter';

import { useDataTableSort } from '../../common/hooks/use-data-table-sort';
import { useDataTableFilter } from '../../common/hooks/use-data-table-filter';

const useControlledPagination = () => {
  const tableState = useSelector(userTableState);

  const dispatch = useDispatch();
  const onLimitChange = useCallback(
    (limit: number) => dispatch(setUserTableLimit(limit)),
    [dispatch]
  );
  const onSkipChange = useCallback((skip: number) => dispatch(setUserTableSkip(skip)), [dispatch]);

  const controlledPaginationProps = {
    pagination: true,
    limit: tableState.pagination.limit,
    onLimitChange,
    skip: tableState.pagination.skip,
    onSkipChange,
  };
  return controlledPaginationProps;
};

export const useSiteFilter = () => {
  const { filter: filterValue }: { filter: TypeFilterValue } = useSelector(userTableState);
  const dispatch = useDispatch();
  const onFilterChange = useCallback(
    (filter: TypeFilterValue) => {
      dispatch(setUserTableFilter(filter));
    },
    [dispatch]
  );
  const filterProps = {
    defaultFilterValue: filterValue,
    filterValue,
    onFilterValueChange: onFilterChange,
  };
  return filterProps;
};

export const useSiteSort = () => {
  const { sort: sortInfo }: { sort: TypeSortInfo } = useSelector(userTableState);

  const dispatch = useDispatch();
  const onSortChange = useCallback(
    (sortInfo: TypeSortInfo) => {
      dispatch(setUserTableSort(sortInfo));
    },
    [dispatch]
  );
  const sortProps = {
    defaultSortInfo: sortInfo,
    sortInfo,
    onSortInfoChange: onSortChange,
  };
  return sortProps;
};

export function UsersHomePage() {
  const { data: users } = useGetUsersQuery();
  const [deleteUser] = useDeleteUserMutation();
  const formattedUsers = users?.filter((u) => !u.disabled).map((u) => ({ ...u, key: u._id })) || [];

  const newColumns = [
    {
      defaultFlex: 1,
      minWidth: 300,
      header: 'Name',
      name: 'full_name',
      render: ({ data: user }: { data: User }) => {
        return <ButtonLink to={`${user._id}/edit`}>{user.full_name}</ButtonLink>;
      },
    },
    {
      header: 'Email',
      name: 'email',
      defaultFlex: 1,
      minWidth: 300,
    },
    {
      header: 'Admin',
      name: 'is_admin',
      defaultFlex: 1,
      minWidth: 80,
      render: ({ data: user }: { data: User }) => {
        if (user.is_admin) return <Tag>Admin</Tag>;
        return <Tag>Not Admin</Tag>;
      },
      filterEditor: SelectFilter,
      filterEditorProps: {
        placeholder: 'All',
        dataSource: [
          {
            id: true,
            label: 'Admin',
          },
          {
            id: false,
            label: 'Not Admin',
          },
        ],
      },
    },
    {
      header: 'Actions',
      name: 'action',
      render: ({ data: user }: { data: User }) => {
        return (
          <>
            <ChangeLogModal target={user} useChangeLogQuery={useGetChangeLogQuery} />
            <Popconfirm
              title={`Are you sure you want to delete '${user.full_name}'?`}
              okText="Yes"
              cancelText="No"
              onConfirm={() => deleteUser(user)}
            >
              <ButtonLink danger>Delete</ButtonLink>
            </Popconfirm>
          </>
        );
      },
    },
  ];

  const filterProps = useDataTableFilter(userTableState, setUserTableFilter);
  const sortProps = useDataTableSort(userTableState, setUserTableSort);
  const controlledPagination = useControlledPagination();
  return (
    <MainLayout
      sectionToolbar={
        <>
          <Link className="ml-auto" to="new">
            <Button>Create User</Button>
          </Link>
        </>
      }
    >
      <ReactDataGrid
        {...filterProps}
        {...sortProps}
        {...controlledPagination}
        dataSource={formattedUsers}
        columns={newColumns}
        rowHeight={50}
        columnUserSelect
      />
    </MainLayout>
  );
}
