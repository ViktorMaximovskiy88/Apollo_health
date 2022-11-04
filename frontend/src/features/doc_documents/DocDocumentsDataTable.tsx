import ReactDataGrid from '@inovua/reactdatagrid-community';
import DateFilter from '@inovua/reactdatagrid-community/DateFilter';
import SelectFilter from '@inovua/reactdatagrid-community/SelectFilter';
import { Tag } from 'antd';
import { useCallback, useMemo, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  setDocDocumentTableFilter,
  setDocDocumentTableSort,
  docDocumentTableState,
  setDocDocumentTableLimit,
  setDocDocumentTableSkip,
} from './docDocumentsSlice';
import { prettyDateTimeFromISO, prettyFromISO } from '../../common';
import { ButtonLink, GridPaginationToolbar } from '../../components';
import { ChangeLogModal } from '../change-log/ChangeLogModal';
import { Site } from '../sites/types';
import { useGetChangeLogQuery, useLazyGetDocDocumentsQuery } from './docDocumentApi';
import { DocDocument } from './types';
import { useInterval } from '../../common/hooks';
import { DocumentTypes } from '../retrieved_documents/types';
import {
  ApprovalStatus,
  approvalStatusDisplayName,
  approvalStatusStyledDisplay,
} from '../../common/approvalStatus';
import { TypePaginationProps } from '@inovua/reactdatagrid-community/types';
import { useDataTableSort } from '../../common/hooks/use-data-table-sort';
import { useDataTableFilter } from '../../common/hooks/use-data-table-filter';
import { RemoteColumnFilter } from '../../components/RemoteColumnFilter';
import { useGetSiteQuery, useGetSitesQuery, useLazyGetSitesQuery } from '../sites/sitesApi';
import { DateTime } from 'luxon';

const colors = ['magenta', 'blue', 'green', 'orange', 'purple'];

function useSiteSelectOptions() {
  const [getSites] = useLazyGetSitesQuery();
  const siteOptions = useCallback(
    async (search: string) => {
      const { data } = await getSites({
        limit: 20,
        skip: 0,
        sortInfo: { name: 'name', dir: 1 },
        filterValue: [{ name: 'name', operator: 'contains', type: 'string', value: search }],
      });
      if (!data) return [];
      return data.data.map((site) => ({ label: site.name, value: site._id }));
    },
    [getSites]
  );
  return { siteOptions };
}

function useGetSiteNamesById() {
  const [siteIds, setSiteIds] = useState<string[]>([]);
  const { data: sites } = useGetSitesQuery(
    {
      filterValue: [{ name: '_id', operator: 'eq', type: 'string', value: siteIds }],
    },
    { skip: siteIds.length === 0 }
  );
  const siteNamesById = useMemo(() => {
    const map: { [key: string]: string } = {};
    sites?.data.forEach((site) => {
      map[site._id] = site.name;
    });
    return map;
  }, [sites]);
  return { setSiteIds, siteNamesById };
}

const useColumns = (siteNamesById: { [key: string]: string }) => {
  const { siteOptions } = useSiteSelectOptions();
  const res = useSelector(docDocumentTableState);
  const siteFilter = res.filter.find((f) => f.name === 'locations.site_id');
  const { data: site } = useGetSiteQuery(siteFilter?.value, { skip: !siteFilter?.value });
  const initialOptions = site ? [{ value: site._id, label: site.name }] : [];
  return [
    {
      header: 'Name',
      name: 'name',
      render: ({ data: doc }: { data: DocDocument }) => {
        return <ButtonLink to={`${doc._id}`}>{doc.name}</ButtonLink>;
      },
      defaultFlex: 1,
      minWidth: 300,
    },
    {
      header: 'Sites',
      name: 'locations.site_id',
      filterEditor: RemoteColumnFilter,
      filterEditorProps: {
        fetchOptions: siteOptions,
        initialOptions,
      },
      defaultFlex: 1,
      render: ({ data }: { data: { locations: { site_id: string }[] } }) => {
        return data.locations.map((s) => siteNamesById[s.site_id]).join(', ');
      },
    },
    {
      header: 'Final Effective Date',
      name: 'final_effective_date',
      minWidth: 200,
      filterEditor: DateFilter,
      filterEditorProps: () => {
        return {
          dateFormat: 'YYYY-MM-DD',
          highlightWeekends: false,
          placeholder: 'Select Date',
        };
      },
      render: ({ data: doc }: { data: DocDocument }) => {
        if (!doc.final_effective_date) return null;
        return prettyFromISO(doc.final_effective_date, DateTime.DATE_MED, false);
      },
    },
    {
      header: 'First Collected Date',
      name: 'first_collected_date',
      minWidth: 200,
      filterEditor: DateFilter,
      filterEditorProps: () => {
        return {
          dateFormat: 'YYYY-MM-DD',
          highlightWeekends: false,
          placeholder: 'Select Date',
        };
      },
      render: ({ data: doc }: { data: DocDocument }) => {
        if (!doc.first_collected_date) return null;
        return prettyDateTimeFromISO(doc.first_collected_date);
      },
    },
    {
      header: 'Last Collected Date',
      name: 'last_collected_date',
      minWidth: 200,
      filterEditor: DateFilter,
      filterEditorProps: () => {
        return {
          dateFormat: 'YYYY-MM-DD',
          highlightWeekends: false,
          placeholder: 'Select Date',
        };
      },
      render: ({ data: doc }: { data: DocDocument }) => {
        if (!doc.last_collected_date) return null;
        return prettyDateTimeFromISO(doc.last_collected_date);
      },
    },
    {
      header: 'Classification Status',
      name: 'classification_status',
      minWidth: 200,
      filterEditor: SelectFilter,
      filterEditorProps: {
        placeholder: 'All',
        dataSource: Object.values(ApprovalStatus).map((status) => ({
          id: status,
          label: approvalStatusDisplayName(status),
        })),
      },
      render: ({ data: doc }: { data: DocDocument }) => {
        return approvalStatusStyledDisplay(doc.classification_status);
      },
    },
    {
      header: 'Document Type',
      name: 'document_type',
      minWidth: 200,
      filterEditor: SelectFilter,
      filterEditorProps: {
        placeholder: 'All',
        dataSource: DocumentTypes,
      },
      render: ({ value: document_type }: { value: string }) => {
        return <>{document_type}</>;
      },
    },
    {
      header: 'Link Text',
      name: 'locations.link_text',
      render: ({ data: docDocument }: { data: DocDocument }) => {
        const linkTexts = docDocument.locations.map((location) => location.link_text);
        return <>{linkTexts.join(', ')}</>;
      },
    },
    {
      header: 'Current Version',
      name: 'is_current_version',
      filterEditor: SelectFilter,
      filterEditorProps: {
        placeholder: true,
        dataSource: [
          {
            id: true,
            label: 'True',
          },
          {
            id: false,
            label: 'False',
          },
        ],
      },
      render: ({ value: is_current_version }: { value: boolean }) => <>{is_current_version}</>,
    },
    {
      header: 'Tags',
      name: 'tags',
      render: ({ data: doc }: { data: DocDocument }) => {
        return doc.tags
          .filter((tag) => tag)
          .map((tag) => {
            const simpleHash = tag
              .split('')
              .map((c) => c.charCodeAt(0))
              .reduce((a, b) => a + b);
            const color = colors[simpleHash % colors.length];
            return (
              <Tag color={color} key={tag}>
                {tag}
              </Tag>
            );
          });
      },
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
};

const useControlledPagination = ({
  isActive,
  setActive,
}: {
  isActive: boolean;
  setActive: (active: boolean) => void;
}) => {
  const tableState = useSelector(docDocumentTableState);
  const dispatch = useDispatch();

  const onLimitChange = useCallback(
    (limit: number) => dispatch(setDocDocumentTableLimit(limit)),
    [dispatch]
  );
  const onSkipChange = useCallback(
    (skip: number) => dispatch(setDocDocumentTableSkip(skip)),
    [dispatch]
  );

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

function uniqueSiteIds(items: DocDocument[]) {
  const usedSiteIds: { [key: string]: boolean } = {};
  items.forEach((item) => item.locations.forEach((l) => (usedSiteIds[l.site_id] = true)));
  return Object.keys(usedSiteIds);
}

export function DocDocumentsDataTable() {
  // Trigger update every 10 seconds by invalidating memoized callback
  const { isActive, setActive, watermark } = useInterval(10000);

  const [getDocDocumentsFn] = useLazyGetDocDocumentsQuery();
  const { setSiteIds, siteNamesById } = useGetSiteNamesById();

  const loadData = useCallback(
    async (tableInfo: any) => {
      const { data } = await getDocDocumentsFn(tableInfo);
      const docDocuments = data?.data ?? [];
      const count = data?.total ?? 0;
      if (docDocuments) setSiteIds(uniqueSiteIds(docDocuments));
      return { data: docDocuments, count };
    },
    [getDocDocumentsFn, setSiteIds, watermark] // eslint-disable-line react-hooks/exhaustive-deps
  );

  const filterProps = useDataTableFilter(docDocumentTableState, setDocDocumentTableFilter);
  const sortProps = useDataTableSort(docDocumentTableState, setDocDocumentTableSort);
  const controlledPagination = useControlledPagination({ isActive, setActive });
  const columns = useColumns(siteNamesById);

  return (
    <ReactDataGrid
      dataSource={loadData}
      {...filterProps}
      {...sortProps}
      {...controlledPagination}
      columns={columns}
      rowHeight={50}
      renderLoadMask={() => <></>}
      activateRowOnFocus={false}
    />
  );
}
