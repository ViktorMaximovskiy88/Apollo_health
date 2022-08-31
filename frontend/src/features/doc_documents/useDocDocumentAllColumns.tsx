import DateFilter from '@inovua/reactdatagrid-community/DateFilter';
import SelectFilter from '@inovua/reactdatagrid-community/SelectFilter';
import { Tag } from 'antd';
import { prettyDateTimeFromISO } from '../../common';
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

const colors = ['magenta', 'blue', 'green', 'orange', 'purple'];

export const useDocDocumentAllColumns = () => [
  {
    header: 'Name',
    name: 'name',
    render: ({ data: doc }: { data: DocDocument }) => {
      return <ButtonLink to={`${doc._id}`}>{doc.name}</ButtonLink>;
    },
    defaultFlex: 1,
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
    name: 'link_text',
    render: ({ value: link_text }: { value: string }) => <>{link_text}</>,
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
