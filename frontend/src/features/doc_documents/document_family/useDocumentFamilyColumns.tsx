import { useMemo } from 'react';
import { DocumentFamily } from './types';

import SelectFilter from '@inovua/reactdatagrid-community/SelectFilter';
import {
  DocumentTypes,
  FieldGroupsOptions,
  LegacyRelevanceOptions,
} from '../../retrieved_documents/types';
import { RemoteColumnFilter } from '../../../components/RemoteColumnFilter';
import { ChangeLogModal } from '../../change-log/ChangeLogModal';
import { useGetChangeLogQuery } from './documentFamilyApi';
import { TypeColumn } from '@inovua/reactdatagrid-community/types';
import { Link } from 'react-router-dom';
import { useSiteSelectOptions } from '../DocDocumentsDataTable';

export const createColumns = (
  siteOptions: (search: string) => Promise<{ label: string; value: string }[]>,
  sitesNamesById: { [key: string]: string }
) => {
  return [
    {
      header: 'Family Name',
      name: 'name',
      defaultFlex: 1,
      minWidth: 200,
      render: ({ data: docFam }: { data: DocumentFamily }) => {
        return <Link to={`/document-family/${docFam._id}`}>{docFam.name}</Link>;
      },
    },
    {
      header: 'Sites',
      name: 'site_id',
      filterEditor: RemoteColumnFilter,
      filterEditorProps: {
        fetchOptions: siteOptions,
      },
      render: ({ data: docFam }: { data: DocumentFamily }) => {
        return docFam.site_ids.map((s) => sitesNamesById[s]).join(', ');
      },
    },
    {
      header: 'Legacy Relevance',
      name: 'legacy_relevance',
      filterEditor: SelectFilter,
      minWidth: 300,
      filterEditorProps: {
        placeholder: 'All',
        dataSource: LegacyRelevanceOptions,
      },
      render: ({ data: docFam }: { data: DocumentFamily }) => {
        return docFam.legacy_relevance
          .map((val) => {
            val = val
              .toLocaleLowerCase()
              .split('_')
              .map((e) => e[0].toUpperCase() + e.slice(1))
              .join(' ');
            return val;
          })
          .join(', ');
      },
    },
    {
      header: 'Field Group',
      name: 'field_groups',
      filterEditor: SelectFilter,
      minWidth: 300,
      filterEditorProps: {
        multiple: true,
        dataSource: FieldGroupsOptions,
      },
      render: ({ data: docFam }: { data: DocumentFamily }) => {
        return docFam.field_groups
          .map((val) => {
            return val
              .toLocaleLowerCase()
              .split('_')
              .map((e) => e[0].toUpperCase() + e.slice(1))
              .join(' ');
          })
          .join(', ');
      },
    },
    {
      header: 'Document Type',
      name: 'document_type',
      filterEditor: SelectFilter,
      minWidth: 200,
      filterEditorProps: {
        placeholder: 'All',
        dataSource: DocumentTypes,
      },
    },
    {
      header: 'Actions',
      name: 'action',
      render: ({ data: docFamily }: { data: DocumentFamily }) => (
        <>
          <ChangeLogModal target={docFamily} useChangeLogQuery={useGetChangeLogQuery} />
        </>
      ),
    },
  ];
};

export const useDocumentFamilyColumns = (siteNamesById: {
  [key: string]: string;
}): TypeColumn[] => {
  const { siteOptions } = useSiteSelectOptions();
  return useMemo(() => {
    return createColumns(siteOptions, siteNamesById);
  }, [siteNamesById]);
};
