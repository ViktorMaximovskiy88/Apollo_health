import { prettyDateFromISO, prettyDateUTCFromISO } from '../../common';
import { Link } from 'react-router-dom';
import { ChangeLogModal } from '../change-log/ChangeLogModal';
import { RetrievedDocument } from '../retrieved_documents/types';
import { useGetChangeLogQuery } from '../sites/sitesApi';
import DateFilter from '@inovua/reactdatagrid-community/DateFilter';
import SelectFilter from '@inovua/reactdatagrid-community/SelectFilter';

export const useDocumentColumns = () => [
  {
    header: 'First Collected',
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
    render: ({ value: first_collected_date }: { value: string }) => {
      return prettyDateFromISO(first_collected_date);
    },
  },
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
    render: ({ value: last_collected_date }: { value: string }) => {
      return prettyDateFromISO(last_collected_date);
    },
  },
  {
    header: 'Link Text',
    name: 'link_text',
    render: ({ value: link_text }: { value: string }) => <>{link_text}</>,
  },
  {
    header: 'Name',
    name: 'name',
    defaultFlex: 1,
    render: ({ data: doc }: { data: RetrievedDocument }) => {
      return <Link to={`${doc._id}/edit`}>{doc.name}</Link>;
    },
  },
  {
    header: 'Document Type',
    name: 'document_type',
    minWidth: 200,
    filterEditor: SelectFilter,
    filterEditorProps: {
      placeholder: 'All',
      dataSource: [
        { id: 'Authorization Policy', label: 'Authorization Policy' },
        { id: 'Provider Guide', label: 'Provider Guide' },
        { id: 'Treatment Request Form', label: 'Treatment Request Form' },
        { id: 'Payer Unlisted Policy', label: 'Payer Unlisted Policy' },
        { id: 'Covered Treatment List', label: 'Covered Treatment List' },
        { id: 'Regulatory Document', label: 'Regulatory Document' },
        { id: 'Formulary', label: 'Formulary' },
        { id: 'Internal Reference', label: 'Internal Reference' },
      ],
    },
    render: ({ value: document_type }: { value: string }) => {
      return <>{document_type}</>;
    },
  },
  {
    header: 'Doc Type Confidence',
    name: 'doc_type_confidence',
    minWidth: 200,
    render: ({ value: doc_type_confidence }: { value?: number }) => {
      return <>{doc_type_confidence && `${Math.round(100 * doc_type_confidence)}%`}</>;
    },
  },
  {
    header: 'Effective Date',
    name: 'effective_date',
    render: ({ value: effective_date }: { value: string }) => {
      if (!effective_date) return null;
      return prettyDateUTCFromISO(effective_date);
    },
  },
  {
    header: 'URL',
    name: 'url',
    render: ({ value: url }: { value: string }) => {
      return (
        <div className="w-48 whitespace-nowrap text-ellipsis overflow-hidden">
          <a target="_blank" rel="noreferrer" href={url}>
            {url}
          </a>
        </div>
      );
    },
  },
  {
    header: 'Actions',
    name: 'action',
    render: ({ data: doc }: { data: RetrievedDocument }) => {
      return (
        <>
          <ChangeLogModal target={doc} useChangeLogQuery={useGetChangeLogQuery} />
        </>
      );
    },
  },
];
