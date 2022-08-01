import ReactDataGrid from '@inovua/reactdatagrid-community';
import { ReactNode, useCallback, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  setSiteTableFilter,
  setSiteTableSort,
  setSiteTableLimit,
  setSiteTableSkip,
  siteTableState,
} from './sitesSlice';
import { GridPaginationToolbar } from '../../components';
import { useDeleteSiteMutation, useLazyGetSitesQuery } from './sitesApi';
import { useInterval } from '../../common/hooks';
import {
  TypeFilterValue,
  TypePaginationProps,
  TypeSortInfo,
} from '@inovua/reactdatagrid-community/types';
import { useColumns } from './useSiteColumns';
import { useGetUsersQuery } from '../users/usersApi';

function disableLoadingMask(data: {
  visible: boolean;
  livePagination: boolean;
  loadingText: ReactNode | (() => ReactNode);
  zIndex: number;
}) {
  return <></>;
}

const useControlledPagination = ({
  isActive,
  setActive,
}: {
  isActive: boolean;
  setActive: (active: boolean) => void;
}) => {
  const tableState = useSelector(siteTableState);

  const dispatch = useDispatch();
  const onLimitChange = useCallback(
    (limit: number) => dispatch(setSiteTableLimit(limit)),
    [dispatch]
  );
  const onSkipChange = useCallback((skip: number) => dispatch(setSiteTableSkip(skip)), [dispatch]);

  const renderPaginationToolbar = useCallback(
    (paginationProps: TypePaginationProps) => {
      return (
        <GridPaginationToolbar
          paginationProps={{ ...paginationProps }}
          autoRefreshValue={isActive}
          autoRefreshClick={setActive}
        />
      );
    },
    [isActive, setActive]
  );

  const controlledPaginationProps = {
    pagination: true,
    limit: tableState.pagination.limit,
    onLimitChange,
    skip: tableState.pagination.skip,
    onSkipChange,
    renderPaginationToolbar,
  };
  return controlledPaginationProps;
};

export const useSiteFilter = () => {
  const { filter: filterValue }: { filter: TypeFilterValue } = useSelector(siteTableState);
  const dispatch = useDispatch();
  const onFilterChange = useCallback(
    (filter: TypeFilterValue) => dispatch(setSiteTableFilter(filter)),
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
  const { sort: sortInfo }: { sort: TypeSortInfo } = useSelector(siteTableState);
  const dispatch = useDispatch();
  const onSortChange = useCallback(
    (sortInfo: TypeSortInfo) => dispatch(setSiteTableSort(sortInfo)),
    [dispatch]
  );
  const sortProps = {
    defaultSortInfo: sortInfo,
    sortInfo,
    onSortInfoChange: onSortChange,
  };
  return sortProps;
};

interface SiteDataTablePropTypes {
  setLoading: (loading: boolean) => void;
}
export function SiteDataTable({ setLoading }: SiteDataTablePropTypes) {
  // Trigger update every 10 seconds by invalidating memoized callback
  const { isActive, setActive, watermark } = useInterval(10000);

  const [getSitesFn] = useLazyGetSitesQuery();

  const [deletedSite, setDeletedSite] = useState('');
  interface TableInfoType {
    limit: number;
    skip: number;
    sortInfo: TypeSortInfo;
    filterValue: TypeFilterValue;
  }
  const loadData = useCallback(
    async (tableInfo: TableInfoType) => {
      setLoading(true);
      const { data } = await getSitesFn(tableInfo);
      setLoading(false);
      const sites = data?.data ?? [];
      const count = data?.total ?? 0;
      return { data: sites, count };
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [getSitesFn, watermark, setLoading, deletedSite] // watermark is not inside useCallback
  );

  const { data: users } = useGetUsersQuery();
  const [deleteSite] = useDeleteSiteMutation();
  const columns = useColumns({ deleteSite, setDeletedSite, users });

  const filterProps = useSiteFilter();
  const sortProps = useSiteSort();
  const controlledPagination = useControlledPagination({ isActive, setActive });

  return (
    <ReactDataGrid
      dataSource={loadData}
      {...filterProps}
      {...sortProps}
      {...controlledPagination}
      columns={columns}
      rowHeight={50}
      renderLoadMask={disableLoadingMask}
      activateRowOnFocus={false}
    />
  );
}
