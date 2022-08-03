import { useMemo } from 'react';
import DateFilter from '@inovua/reactdatagrid-community/DateFilter';
import SelectFilter from '@inovua/reactdatagrid-community/SelectFilter';
import { Button } from 'antd';
import { prettyDateTimeFromISO } from '../../common';
import { ButtonLink } from '../../components/ButtonLink';
import { DocDocument } from "./types";
import { Link } from 'react-router-dom';

interface CreateColumnsType {
}
export const createColumns = ({
}: CreateColumnsType) => {
  return [
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
      header: 'Document Name',
      key: 'name',
      defaultFlex: 1,
      filterSearch: true,
      render: ({ data: doc }: { data: DocDocument }) => {
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
      header: 'Link Text',
      name: 'link_text',
      minWidth: 200,
      render: ({ value: link_text }: { value: string }) => <>{link_text}</>,
    },
    {
      header: 'Effective Date',
      name: 'effective_date',
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
        if (!doc.effective_date) return null;
        return prettyDateTimeFromISO(doc.effective_date);
      },
    },
    {
      header: 'Url',
      key: 'url',
      minWidth: 200,
      filterSearch: true,
      render: ({ data: doc }: { data: DocDocument }) => {
        return <Link to={`${doc._id}/edit`}>{doc.url}</Link>;
      },
    },
    {
      header: 'Actions',
      name: 'action',
      minWidth: 200,
      render: ({ data: site }: { data: DocDocument }) => {
        return (
          <>
            
          </>
        );
      },
    },
  ]
};

export const useDocumentColumns = () =>
  useMemo(
    () => createColumns({}),
    []
  );
