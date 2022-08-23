import ReactDataGrid from '@inovua/reactdatagrid-community';
import { useCallback } from 'react';
import {
  setTranslationTableFilter,
  setTranslationTableSort,
  setTranslationTableLimit,
  setTranslationTableSkip,
  translationTableState,
} from './translationSlice';
import { ButtonLink } from '../../components';
import { ChangeLogModal } from '../change-log/ChangeLogModal';
import { Site } from '../sites/types';
import { useGetChangeLogQuery, useLazyGetTranslationConfigsQuery } from './translationApi';
import { useDataTableSort } from '../../common/hooks/use-data-table-sort';
import { useDataTableFilter } from '../../common/hooks/use-data-table-filter';
import { TranslationConfig } from './types';
import { useDataTablePagination } from '../../common/hooks/use-data-table-pagination';

const columns = [
  {
    header: 'Name',
    name: 'name',
    render: ({ data: doc }: { data: TranslationConfig }) => {
      return <ButtonLink to={`${doc._id}`}>{doc.name}</ButtonLink>;
    },
    defaultFlex: 1,
  },
  {
    header: 'Actions',
    name: 'action',
    minWidth: 180,
    render: ({ data: site }: { data: Site }) => {
      return (
        <>
          <ChangeLogModal target={site} useChangeLogQuery={useGetChangeLogQuery} />
        </>
      );
    },
  },
];

export function TranslationsDataTable() {
  const [getTranslationsFn] = useLazyGetTranslationConfigsQuery();

  const loadData = useCallback(
    async (tableInfo: any) => {
      const { data } = await getTranslationsFn(tableInfo);
      const sites = data?.data ?? [];
      const count = data?.total ?? 0;
      return { data: sites, count };
    },
    [getTranslationsFn]
  );

  const filterProps = useDataTableFilter(translationTableState, setTranslationTableFilter);
  const sortProps = useDataTableSort(translationTableState, setTranslationTableSort);
  const paginationProps = useDataTablePagination(
    translationTableState,
    setTranslationTableLimit,
    setTranslationTableSkip
  );

  return (
    <ReactDataGrid
      dataSource={loadData}
      {...filterProps}
      {...sortProps}
      {...paginationProps}
      columns={columns}
      rowHeight={50}
      activateRowOnFocus={false}
    />
  );
}
