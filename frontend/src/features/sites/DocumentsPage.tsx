import { Popconfirm, Button, Table } from 'antd';
import Title from 'antd/lib/typography/Title';
import { prettyDate } from '../../common';
import { Link, useParams, useSearchParams } from 'react-router-dom';
import { ButtonLink } from '../../components/ButtonLink';
import { ChangeLogModal } from '../change_log/ChangeLogModal';
import {
  useDeleteDocumentMutation,
  useGetDocumentsQuery,
} from '../documents/documentsApi';
import { RetrievedDocument } from '../documents/types';
import { useGetChangeLogQuery } from './sitesApi';

export function DocumentsPage() {
  const [searchParams] = useSearchParams();
  const params = useParams();
  const [deleteDocument] = useDeleteDocumentMutation();
  const scrapeTaskId = searchParams.get('scrape_task_id');
  const siteId = params.siteId;
  const { data: documents } = useGetDocumentsQuery(
    {
      scrape_task_id: scrapeTaskId,
      site_id: siteId,
    },
    { pollingInterval: 5000 }
  );

  const columns = [
    {
      title: 'Collection Time',
      key: 'collection_time',
      render: (doc: RetrievedDocument) => {
        return prettyDate(doc.collection_time);
      },
    },
    {
      title: 'Name',
      key: 'name',
      filterSearch: true,
      render: (doc: RetrievedDocument) => {
        return <Link to={`${doc._id}/edit`}>{doc.name}</Link>;
      },
    },
    {
      title: 'Document Type',
      key: 'document_type',
      render: (doc: RetrievedDocument) => {
        return <>{doc.document_type}</>;
      },
    },
    {
      title: 'Doc Type Confidence',
      key: 'doc_type_confidence',
      render: (doc: RetrievedDocument) => {
        return (
          <>
            {doc.doc_type_confidence &&
              `${Math.round(100 * doc.doc_type_confidence)}%`}
          </>
        );
      },
    },
    {
      title: 'Effective Date',
      key: 'effective_date',
      render: (doc: RetrievedDocument) => {
        if (!doc.effective_date) return null;
        return prettyDate(doc.effective_date);
      },
    },
    {
      title: 'URL',
      key: 'url',
      render: (doc: RetrievedDocument) => {
        return (
          <div className="w-48 whitespace-nowrap text-ellipsis overflow-hidden">
            <a target="_blank" rel="noreferrer" href={doc.url}>
              {doc.url}
            </a>
          </div>
        );
      },
    },
    {
      title: 'Actions',
      key: 'action',
      render: (doc: RetrievedDocument) => {
        return (
          <>
            <ChangeLogModal
              target={doc}
              useChangeLogQuery={useGetChangeLogQuery}
            />
            <Popconfirm
              title={`Are you sure you want to delete '${doc.name}'?`}
              okText="Yes"
              cancelText="No"
              onConfirm={() => deleteDocument(doc)}
            >
              <ButtonLink danger>Delete</ButtonLink>
            </Popconfirm>
          </>
        );
      },
    },
  ];
  return (
    <div>
      <div className="flex">
        <Title className="inline-block" level={4}>
          Documents
        </Title>
        <Button className="ml-auto">Create Document</Button>
      </div>
      <Table
        dataSource={documents}
        columns={columns}
        rowKey={(doc) => doc._id}
      />
    </div>
  );
}
