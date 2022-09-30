import ReactDataGrid from '@inovua/reactdatagrid-community';
import NumberFilter from '@inovua/reactdatagrid-community/NumberFilter';
import { TypeSingleSortInfo, TypeSingleFilterValue } from '@inovua/reactdatagrid-community/types';
import { useCallback } from 'react';
import { useLazyGetExtractionTaskResultsQuery, useGetExtractionTaskQuery } from './extractionsApi';

export function ExtractionResultsDataTable({
  extractionId,
  delta,
}: {
  extractionId?: string;
  delta?: boolean;
}) {
  const [getResultsFn] = useLazyGetExtractionTaskResultsQuery();
  const { data: extractionTask } = useGetExtractionTaskQuery(extractionId);

  const loadData = useCallback(
    async (tableInfo: any) => {
      let sortInfo: TypeSingleSortInfo[] = tableInfo.sortInfo;
      sortInfo = sortInfo.map((info) => {
        if (info.name.startsWith('t_')) {
          return { ...info, name: `translation.${info.name.replace(/^t_/, '')}` };
        } else if (info.name === 'page' || info.name === 'row') {
          return info;
        } else {
          return { ...info, name: `result.${info.name}` };
        }
      });
      let filterValue: TypeSingleFilterValue[] = tableInfo.filterValue;
      filterValue = filterValue.map((filter) => {
        if (filter.name.startsWith('t_')) {
          return { ...filter, name: `translation.${filter.name.replace(/^t_/, '')}` };
        } else if (filter.name === 'page' || filter.name === 'row') {
          return filter;
        } else {
          return { ...filter, name: `result.${filter.name}` };
        }
      });

      const { data } = await getResultsFn({
        id: extractionId,
        ...tableInfo,
        sortInfo,
        filterValue,
        delta,
      });
      const extractions = data?.data || [];
      const count = data?.total || 0;
      const formattedExtractions = extractions.map(({ page, row, result, translation }) => {
        const translatedPrefixedKeys: any = {};
        if (translation) {
          for (const [key, value] of Object.entries(translation)) {
            translatedPrefixedKeys[`t_${key}`] = value;
          }
        }
        return { page, row, ...result, ...translatedPrefixedKeys };
      });
      return { data: formattedExtractions, count };
    },
    [extractionId, getResultsFn, delta]
  );

  if (!extractionTask) return null;

  const header = extractionTask.header || [];

  const translatedColumns = [
    {
      header: 'Name',
      name: 't_name',
      defaultFlex: 1,
      minWidth: 200,
    },
    {
      header: 'Drug ID',
      name: 't_code',
      group: 'translated',
    },
    {
      header: 'RXCUI',
      name: 't_rxcui',
      group: 'translated',
      render: ({ value }: { value: string }) => {
        return (
          <a
            target="_blank"
            rel="noreferrer"
            href={`https://mor.nlm.nih.gov/RxNav/search?searchBy=RXCUI&searchTerm=${value}`}
          >
            {value}
          </a>
        );
      },
    },
    {
      header: 'Tier',
      name: 't_tier',
    },
    {
      header: 'PA',
      name: 't_pa',
      render: ({ value }: { value: boolean }) => (value ? 'True' : ''),
    },
    {
      header: 'QL',
      name: 't_ql',
      render: ({ value }: { value: boolean }) => (value ? 'True' : ''),
    },
    {
      header: 'QL Note',
      name: 't_qln',
    },
    {
      header: 'ST',
      name: 't_st',
      render: ({ value }: { value: boolean }) => (value ? 'True' : ''),
    },
    {
      header: 'ST Note',
      name: 't_stn',
    },
    {
      header: 'SP',
      name: 't_sp',
      render: ({ value }: { value: boolean }) => (value ? 'True' : ''),
    },
  ];
  const columns: any[] = [
    {
      header: 'Page',
      name: 'page',
      group: 'raw',
      type: 'number',
      filterEditor: NumberFilter,
    },
    {
      header: 'Row',
      name: 'row',
      group: 'raw',
      type: 'number',
      filterEditor: NumberFilter,
    },
  ];
  header.forEach((h) => {
    columns.push({
      header: h,
      name: h,
      group: 'raw',
    });
  });
  translatedColumns.forEach((c) => {
    columns.push({
      group: 'translated',
      ...c,
    });
  });

  const groups = [
    { header: 'Raw', name: 'raw' },
    { header: 'Translated', name: 'translated' },
  ];

  const fixedFilters: any[] = [
    { name: 'page', operator: 'eq', type: 'number', value: null },
    { name: 'row', operator: 'eq', type: 'number', value: null },
    { name: 't_tier', operator: 'eq', type: 'number', value: null },
    { name: 't_name', operator: 'contains', type: 'string', value: '' },
    { name: 't_code', operator: 'contains', type: 'string', value: '' },
  ];
  const defaultFilterValue = header
    .map((name) => ({ name, operator: 'contains', type: 'string', value: '' }))
    .concat(fixedFilters);
  const defaultSortInfo = [
    { name: 'page', dir: 1 as 1 | -1 | 0 },
    { name: 'row', dir: 1 as 1 | -1 | 0 },
  ];

  return (
    <ReactDataGrid
      dataSource={loadData}
      columns={columns}
      className="h-full"
      rowHeight={50}
      groups={groups}
      pagination
      defaultFilterValue={defaultFilterValue}
      defaultSortInfo={defaultSortInfo}
    />
  );
}
