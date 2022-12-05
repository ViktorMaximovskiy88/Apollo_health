import DateFilter from '@inovua/reactdatagrid-community/DateFilter';
import SelectFilter from '@inovua/reactdatagrid-community/SelectFilter';
import { Tag } from 'antd';
import { useCallback } from 'react';
import { useSelector } from 'react-redux';
import { docDocumentTableState } from './docDocumentsSlice';
import { prettyDateTimeFromISO, prettyDateUTCFromISO } from '../../common';
import { ButtonLink } from '../../components';
import { ChangeLogModal } from '../change-log/ChangeLogModal';
import { Site } from '../sites/types';
import { useGetChangeLogQuery } from './docDocumentApi';
import { DocDocument } from './types';
import { DocumentTypes } from '../retrieved_documents/types';
import {
  ApprovalStatus,
  approvalStatusDisplayName,
  approvalStatusStyledDisplay,
} from '../../common/approvalStatus';
import { RemoteColumnFilter } from '../../components/RemoteColumnFilter';
import { useGetSiteQuery, useLazyGetSitesQuery } from '../sites/sitesApi';
import {
  useGetPayerFamilyQuery,
  useLazyGetPayerFamiliesQuery,
} from '../payer-family/payerFamilyApi';
import {
  useGetDocumentFamilyQuery,
  useLazyGetDocumentFamiliesQuery,
} from './document_family/documentFamilyApi';

export function useSiteSelectOptions() {
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
      return data.data.map((site) => ({ label: site.name, value: site._id, id: site._id }));
    },
    [getSites]
  );

  const res = useSelector(docDocumentTableState);
  const siteFilter = res.filter.find((f) => f.name === 'locations.site_id');
  const { data: site } = useGetSiteQuery(siteFilter?.value, { skip: !siteFilter?.value });
  const initialSiteOptions = site ? [{ value: site._id, label: site.name }] : [];

  return { siteOptions, initialSiteOptions };
}

function useDocumentFamilySelectOptions() {
  const [getDocumentFamilies] = useLazyGetDocumentFamiliesQuery();
  const documentFamilyOptions = useCallback(
    async (search: string) => {
      const { data } = await getDocumentFamilies({
        limit: 20,
        skip: 0,
        sortInfo: { name: 'name', dir: 1 },
        filterValue: [{ name: 'name', operator: 'contains', type: 'string', value: search }],
      });
      if (!data) return [];
      return data.data.map((df) => ({ label: df.name, value: df._id }));
    },
    [getDocumentFamilies]
  );

  const res = useSelector(docDocumentTableState);
  const documentFamilyFilter = res.filter.find((f) => f.name === 'document_family_id');
  const { data: documentFamily } = useGetDocumentFamilyQuery(
    documentFamilyFilter?.value ?? undefined,
    { skip: !documentFamilyFilter?.value }
  );
  const initialDocumentFamilyOptions = documentFamily
    ? [{ value: documentFamily._id, label: documentFamily.name }]
    : [];

  return { documentFamilyOptions, initialDocumentFamilyOptions };
}

function usePayerFamilySelectOptions() {
  const [getPayerFamilies] = useLazyGetPayerFamiliesQuery();
  const payerFamilyOptions = useCallback(
    async (search: string) => {
      const { data } = await getPayerFamilies({
        limit: 20,
        skip: 0,
        sortInfo: { name: 'name', dir: 1 },
        filterValue: [{ name: 'name', operator: 'contains', type: 'string', value: search }],
      });
      if (!data) return [];
      return data.data.map((pf) => ({ label: pf.name, value: pf._id }));
    },
    [getPayerFamilies]
  );

  const res = useSelector(docDocumentTableState);
  const payerFamilyFilter = res.filter.find((f) => f.name === 'locations.payer_family_id');
  const { data: payerFamily } = useGetPayerFamilyQuery(payerFamilyFilter?.value ?? undefined, {
    skip: !payerFamilyFilter?.value,
  });
  const initialPayerFamilyOptions = payerFamily
    ? [{ value: payerFamily._id, label: payerFamily.name }]
    : [];

  return { payerFamilyOptions, initialPayerFamilyOptions };
}

const colors = ['magenta', 'blue', 'green', 'orange', 'purple'];

export const useColumns = ({
  siteNamesById,
  payerFamilyNamesById,
  documentFamilyNamesById,
}: {
  siteNamesById: { [id: string]: string };
  payerFamilyNamesById: { [id: string]: string };
  documentFamilyNamesById: { [id: string]: string };
}) => {
  const { siteOptions, initialSiteOptions } = useSiteSelectOptions();
  const { payerFamilyOptions, initialPayerFamilyOptions } = usePayerFamilySelectOptions();
  const { documentFamilyOptions, initialDocumentFamilyOptions } = useDocumentFamilySelectOptions();

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
      header: 'Link Text',
      name: 'locations.link_text',
      render: ({ data: docDocument }: { data: DocDocument }) => {
        const linkTexts = docDocument.locations.map((location) => location.link_text);
        return <>{linkTexts.join(', ')}</>;
      },
      minWidth: 300,
    },
    {
      header: 'Sites',
      name: 'locations.site_id',
      minWidth: 200,
      filterEditor: RemoteColumnFilter,
      filterEditorProps: {
        fetchOptions: siteOptions,
        initialOptions: initialSiteOptions,
      },
      defaultFlex: 1,
      render: ({ data }: { data: { locations: { site_id: string }[] } }) => {
        return data.locations
          .filter((s) => siteNamesById[s.site_id])
          .map((s) => siteNamesById[s.site_id])
          .join(', ');
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
        return prettyDateUTCFromISO(doc.final_effective_date);
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
      header: 'Document Family',
      name: 'document_family_id',
      minWidth: 200,
      filterEditor: RemoteColumnFilter,
      filterEditorProps: {
        fetchOptions: documentFamilyOptions,
        initialOptions: initialDocumentFamilyOptions,
      },
      defaultFlex: 1,
      render: ({ data: { document_family_id } }: { data: DocDocument }) => {
        return document_family_id ? documentFamilyNamesById[document_family_id] : null;
      },
    },
    {
      header: 'Payer Families',
      name: 'locations.payer_family_id',
      minWidth: 200,
      filterEditor: RemoteColumnFilter,
      filterEditorProps: {
        fetchOptions: payerFamilyOptions,
        initialOptions: initialPayerFamilyOptions,
      },
      defaultFlex: 1,
      render: ({ data }: { data: { locations: { payer_family_id: string }[] } }) => {
        return data.locations
          .filter((s) => payerFamilyNamesById[s.payer_family_id])
          .map((s) => payerFamilyNamesById[s.payer_family_id])
          .join(', ');
      },
    },
    {
      header: 'Status',
      name: 'status',
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
        return approvalStatusStyledDisplay(doc.status);
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
      header: 'Family Status',
      name: 'family_status',
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
        return approvalStatusStyledDisplay(doc.family_status);
      },
    },
    {
      header: 'Content Extraction Status',
      name: 'content_extraction_status',
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
        return approvalStatusStyledDisplay(doc.content_extraction_status);
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
      render: ({ value: is_current_version }: { value: boolean }) => {
        return <>{is_current_version ? 'True' : 'False'}</>;
      },
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
