import ReactDataGrid from '@inovua/reactdatagrid-community';
import NumberFilter from '@inovua/reactdatagrid-community/NumberFilter';
import {
  TypeSingleSortInfo,
  TypeSingleFilterValue,
  TypeColumn,
} from '@inovua/reactdatagrid-community/types';
import { useCallback } from 'react';
import tw from 'twin.macro';
import { useLazyGetExtractionTaskResultsQuery, useGetExtractionTaskQuery } from './extractionsApi';

function rowStyle({ data }: { data: any }) {
  if (data.remove) {
    return tw`text-red-500 bg-red-100`;
  } else if (data.add) {
    return tw`text-green-500 bg-green-100`;
  } else if (data.edit) {
    return tw`text-blue-500 bg-blue-100`;
  }
  return {};
}

export function ExtractionResultsDataTable({
  extractionId,
  deltaSubset,
  fullSubset,
  delta,
}: {
  extractionId?: string;
  delta?: boolean;
  fullSubset?: string[];
  deltaSubset?: string[];
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
        deltaSubset,
        fullSubset,
      });
      const extractions = data?.data || [];
      const count = data?.total || 0;
      const formattedExtractions = extractions.map(
        ({ page, row, add, remove, edit, result, translation }) => {
          const translatedPrefixedKeys: any = {};
          if (translation) {
            for (const [key, value] of Object.entries(translation)) {
              translatedPrefixedKeys[`t_${key}`] = value;
            }
          }
          return { page, row, add, remove, edit, ...result, ...translatedPrefixedKeys };
        }
      );
      return { data: formattedExtractions, count };
    },
    [extractionId, getResultsFn, delta, deltaSubset, fullSubset]
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
    {
      header: 'DME',
      name: 't_dme',
      render: ({ value }: { value: boolean }) => (value ? 'True' : ''),
    },
    {
      header: 'SCO',
      name: 't_sco',
      render: ({ value }: { value: boolean }) => (value ? 'True' : ''),
    },
    {
      header: 'MB',
      name: 't_mb',
      render: ({ value }: { value: boolean }) => (value ? 'True' : ''),
    },
    {
      header: 'STPA',
      name: 't_stpa',
      render: ({ value }: { value: boolean }) => (value ? 'True' : ''),
    },
  ];
  const columns: TypeColumn[] = [
    {
      header: 'Page',
      name: 'page',
      defaultVisible: !delta,
      group: 'raw',
      type: 'number',
      filterEditor: NumberFilter,
    },
    {
      header: 'Row',
      name: 'row',
      defaultVisible: !delta,
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
  const defaultSortInfo = [{ name: 't_code', dir: 1 as 1 | -1 | 0 }];

  return (
    <ReactDataGrid
      dataSource={loadData}
      columns={columns}
      className="h-full"
      rowHeight={50}
      rowStyle={rowStyle}
      groups={groups}
      pagination
      defaultFilterValue={defaultFilterValue}
      defaultSortInfo={defaultSortInfo}
      columnUserSelect
    />
  );
}
