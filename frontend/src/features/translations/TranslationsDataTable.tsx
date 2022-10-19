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
import { useGetChangeLogQuery, useLazyGetTranslationConfigsQuery } from './translationApi';
import { useDataTableSort, useDataTableFilter, useDataTablePagination } from '../../common/hooks';
import { TranslationConfig } from './types';
import { CopyTranslation } from './CopyTranslation';

const columns = [
  {
    header: 'Name',
    name: 'name',
    render: ({ data: translation }: { data: TranslationConfig }) => {
      return <ButtonLink to={`${translation._id}`}>{translation.name}</ButtonLink>;
    },
    defaultFlex: 1,
    minWidth: 300,
  },
  {
    header: 'Actions',
    name: 'action',
    minWidth: 180,
    render: ({ data: translation }: { data: TranslationConfig }) => {
      return (
        <>
          <ChangeLogModal target={translation} useChangeLogQuery={useGetChangeLogQuery} />
          <CopyTranslation translation={translation} />
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
    setTranslationTableSkip,
    undefined
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
