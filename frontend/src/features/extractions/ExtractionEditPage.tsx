import ReactDataGrid from '@inovua/reactdatagrid-community';
import Title from 'antd/lib/typography/Title';
import NumberFilter from '@inovua/reactdatagrid-community/NumberFilter';
import { useParams } from 'react-router-dom';
import { useGetExtractionTaskQuery, useLazyGetExtractionTaskResultsQuery } from './extractionsApi';
import { useCallback } from 'react';
import { TypeSingleSortInfo, TypeSingleFilterValue } from '@inovua/reactdatagrid-community/types';

export function ExtractionEditPage() {
  const { extractionId } = useParams();
  const [getResultsFn] = useLazyGetExtractionTaskResultsQuery();
  const { data: extractionTask } = useGetExtractionTaskQuery(extractionId);

  const loadData = useCallback(
    async (tableInfo: any) => {
      let sortInfo: TypeSingleSortInfo[] = tableInfo.sortInfo;
      sortInfo = sortInfo.map((info) => {
        if (info.name.startsWith('t_')) {
          return { ...info, name: `translation.${info.name.replace(/^t_/, '')}` };
        } else if (info.name === 'page' || info.name == 'row') {
          return info;
        } else {
          return { ...info, name: `result.${info.name}` };
        }
      });
      let filterValue: TypeSingleFilterValue[] = tableInfo.filterValue;
      filterValue = filterValue.map((filter) => {
        if (filter.name.startsWith('t_')) {
          return { ...filter, name: `translation.${filter.name.replace(/^t_/, '')}` };
        } else if (filter.name === 'page' || filter.name == 'row') {
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
    [extractionId, getResultsFn]
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
      header: 'Code',
      name: 't_code',
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
    },
    {
      header: 'QL',
      name: 't_ql',
    },
    {
      header: 'ST',
      name: 't_st',
    },
    {
      header: 'SP',
      name: 't_sp',
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
    <>
      <div className="flex">
        <Title className="inline-block" level={4}>
          Extraction Results
        </Title>
      </div>
      <ReactDataGrid
        dataSource={loadData}
        columns={columns}
        rowHeight={50}
        groups={groups}
        pagination
        defaultFilterValue={defaultFilterValue}
        defaultSortInfo={defaultSortInfo}
      />
    </>
  );
}
