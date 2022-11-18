import { useMemo } from 'react';
import { DocumentFamily } from './types';

import SelectFilter from '@inovua/reactdatagrid-community/SelectFilter';
import {
  DocumentTypes,
  FieldGroupsOptions,
  getFieldGroupLabel,
  getLegacyRelevanceLable,
  LegacyRelevanceOptions,
} from '../../retrieved_documents/types';
import { ChangeLogModal } from '../../change-log/ChangeLogModal';
import { useGetChangeLogQuery } from './documentFamilyApi';
import { TypeColumn } from '@inovua/reactdatagrid-community/types';
import { Link } from 'react-router-dom';
import { useSiteSelectOptions } from '../DocDocumentsDataTable';
import { RemoteColumnFilter } from '../../../components/RemoteColumnFilter';

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
      name: 'site_ids',
      defaultFlex: 1,
      minWidth: 200,
      filterEditor: RemoteColumnFilter,
      filterEditorProps: {
        fetchOptions: siteOptions,
        mode: 'multiple',
      },
      render: ({ data: docFam }: { data: DocumentFamily }) => {
        return docFam.site_ids
          .map((s) => sitesNamesById[s])
          .filter((e) => {
            return e != null;
          })
          .join(', ');
      },
    },
    {
      header: 'Legacy Relevance',
      name: 'legacy_relevance',
      filterEditor: SelectFilter,
      minWidth: 200,
      filterEditorProps: {
        multiple: true,
        wrapMultiple: false,
        dataSource: LegacyRelevanceOptions,
      },
      render: ({ data: docFam }: { data: DocumentFamily }) => {
        return docFam.legacy_relevance.map(getLegacyRelevanceLable).join(', ');
      },
    },
    {
      header: 'Field Group',
      name: 'field_groups',
      filterEditor: SelectFilter,
      minWidth: 300,
      filterEditorProps: {
        multiple: true,
        wrapMultiple: false,
        dataSource: FieldGroupsOptions,
      },
      render: ({ data: docFam }: { data: DocumentFamily }) => {
        return docFam.field_groups.map(getFieldGroupLabel).join(', ');
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
