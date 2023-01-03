import { useMemo } from 'react';
import DateFilter from '@inovua/reactdatagrid-community/DateFilter';
import SelectFilter from '@inovua/reactdatagrid-community/SelectFilter';
import BoolFilter from '@inovua/reactdatagrid-community/BoolFilter';
import { LinkOutlined, CheckCircleFilled } from '@ant-design/icons';
import { prettyDateUTCFromISO } from '../../common';
import { DocDocument, SiteDocDocument } from './types';
import { Link, useLocation, useParams, Location } from 'react-router-dom';
import { DocumentTypes } from '../retrieved_documents/types';
import { RemoteColumnFilter } from '../../components/RemoteColumnFilter';
import { ManualCollectionValidationButtons } from './manual_collection/ManualCollectionValidationButtons';
import { useDocumentFamilySelectOptions } from './document_family/documentFamilyHooks';
import { useGetSiteQuery } from '../sites/sitesApi';
import { CollectionMethod } from '../sites/types';
import { usePayerFamilySelectOptions } from '../payer-family/payerFamilyHooks';

interface CreateColumnsType {
  handleNewVersion?: (data: SiteDocDocument) => void;
  documentFamilyOptions: (search: string) => Promise<
    {
      label: string;
      value: string;
    }[]
  >;
  payerFamilyOptions: (search: string) => Promise<
    {
      label: string;
      value: string;
    }[]
  >;
  initialDocumentFamilyOptions: {
    value: string;
    label: string;
  }[];
  initialPayerFamilyOptions: {
    value: string;
    label: string;
  }[];
  documentFamilyNamesById: {
    [id: string]: string;
  };
  payerFamilyNamesById: {
    [id: string]: string;
  };
  isManualCollection: boolean;
  location: Location;
}

export enum TextAlignType {
  Start = 'start',
  End = 'end',
  Left = 'left',
  Right = 'right',
  Center = 'center',
}

const InternalDocs = [
  { id: true, value: true, label: 'true' },
  { id: false, value: false, label: 'false' },
];

export function priorityStyle(priority: number): React.ReactElement {
  switch (true) {
    case priority == 0:
      return <span className="text-blue-500">Low</span>;
    case priority == 1:
      return <span className="text-green-500">Medium</span>;
    case priority >= 2:
      return <span className="text-red-500">High</span>;
    default:
      return <span className="text-blue-500">Low</span>;
  }
}

export const createColumns = ({
  handleNewVersion,
  documentFamilyOptions,
  initialDocumentFamilyOptions,
  payerFamilyOptions,
  initialPayerFamilyOptions,
  documentFamilyNamesById,
  payerFamilyNamesById,
  isManualCollection,
  location,
}: CreateColumnsType) => [
  {
    header: 'Last Collected',
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
    render: ({ data: doc }: { data: SiteDocDocument }) => {
      if (!doc.last_collected_date) return null;
      return prettyDateUTCFromISO(doc.last_collected_date);
    },
  },
  {
    header: 'Document Name',
    name: 'name',
    defaultFlex: 1,
    minWidth: 300,
    filterSearch: true,
    render: ({ data: doc }: { data: SiteDocDocument }) => {
      return (
        <Link to={`/documents/${doc._id}?prevLocation=${location.pathname + location.search}`}>
          {doc.name}
        </Link>
      );
    },
  },
  {
    header: 'Link Text',
    name: 'link_text',
    minWidth: 200,
    render: ({ value: link_text }: { value: string }) => <>{link_text}</>,
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
    render: ({ data: doc }: { data: SiteDocDocument }) => {
      if (doc.final_effective_date) {
        return prettyDateUTCFromISO(doc.final_effective_date);
      }
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
    header: 'Payer Family',
    name: 'payer_family_id',
    minWidth: 200,
    filterEditor: RemoteColumnFilter,
    filterEditorProps: {
      fetchOptions: payerFamilyOptions,
      initialOptions: initialPayerFamilyOptions,
    },
    defaultFlex: 1,
    render: ({ data: { payer_family_id } }: { data: SiteDocDocument }) => {
      return payer_family_id ? payerFamilyNamesById[payer_family_id] : null;
    },
  },
  {
    header: 'Internal',
    name: 'internal_document',
    width: 100,
    filterEditor: BoolFilter,
    textAlign: TextAlignType.Center,
    filterEditorProps: {
      placeholder: 'All',
      dataSource: InternalDocs,
    },
    render: ({ value: internal_document }: { value: boolean }) => {
      return internal_document ? <CheckCircleFilled /> : null;
    },
  },
  {
    header: 'URL',
    name: 'url',
    width: 80,
    filterSearch: true,
    render: ({ data: doc }: { data: SiteDocDocument }) => {
      return (
        <>
          <a className="mx-2" href={doc.url} target="_blank" rel="noreferrer">
            <LinkOutlined />
          </a>
        </>
      );
    },
  },
  {
    header: 'Priority',
    name: 'priority',
    width: 90,
    render: ({ data: doc }: { data: SiteDocDocument }) => {
      return priorityStyle(doc.priority);
    },
  },
  {
    header: 'Validation',
    name: 'validation',
    minWidth: 230,
    visible: isManualCollection,
    render: ({ data: doc }: { data: SiteDocDocument }) => {
      return (
        <>
          {handleNewVersion ? (
            <ManualCollectionValidationButtons doc={doc} handleNewVersion={handleNewVersion} />
          ) : null}
        </>
      );
    },
  },
];

interface UseColumnsType {
  handleNewVersion?: (data: SiteDocDocument) => void;
  documentFamilyNamesById: {
    [id: string]: string;
  };
  payerFamilyNamesById: {
    [id: string]: string;
  };
}

export const useSiteDocDocumentColumns = ({
  handleNewVersion,
  documentFamilyNamesById,
  payerFamilyNamesById,
}: UseColumnsType) => {
  const { documentFamilyOptions, initialDocumentFamilyOptions } = useDocumentFamilySelectOptions();
  const { payerFamilyOptions, initialPayerFamilyOptions } =
    usePayerFamilySelectOptions('payer_family_id');
  const { siteId } = useParams();
  const { data: site } = useGetSiteQuery(siteId);
  const location = useLocation();
  return useMemo(
    () =>
      createColumns({
        handleNewVersion,
        documentFamilyOptions,
        initialDocumentFamilyOptions,
        payerFamilyOptions,
        initialPayerFamilyOptions,
        documentFamilyNamesById,
        payerFamilyNamesById,
        isManualCollection: site?.collection_method === CollectionMethod.Manual,
        location,
      }),
    [
      documentFamilyNamesById,
      payerFamilyNamesById,
      documentFamilyOptions,
      payerFamilyOptions,
      handleNewVersion,
      initialDocumentFamilyOptions,
      initialPayerFamilyOptions,
      site?.collection_method,
      location,
    ]
  );
};
