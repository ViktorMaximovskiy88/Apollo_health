import { Table } from 'antd';
import Title from 'antd/lib/typography/Title';
import { format, parseISO } from 'date-fns';
import { Link, useParams, useSearchParams } from 'react-router-dom';
import { ChangeLogModal } from '../change_log/ChangeLogModal';
import { useGetDocumentsQuery } from '../documents/documentsApi';
import { RetrievedDocument } from '../documents/types';
import { useGetChangeLogQuery } from '../sites/sitesApi';

export function ExtractionsPage() {
  const [searchParams] = useSearchParams();
  const params = useParams();
  const scrapeTaskId = searchParams.get('scrape_task_id');
  const siteId = params.siteId;
  const { data: documents } = useGetDocumentsQuery({
    scrape_task_id: scrapeTaskId,
    site_id: siteId,
    automated_content_extraction: true,
  });

  const columns = [
    {
      title: 'Collection Time',
      key: 'collection_time',
      render: (doc: RetrievedDocument) => {
        return <>{format(parseISO(doc.collection_time), 'yyyy-MM-dd p')}</>;
      },
    },
    {
      title: 'Name',
      key: 'name',
      filterSearch: true,
      render: (doc: RetrievedDocument) => {
        return <Link to={`document/${doc._id}`}>{doc.name}</Link>;
      },
    },
    {
      title: 'Document Type',
      key: 'document_type',
      render: (doc: RetrievedDocument) => {
        if (doc.document_type === 'PA') {
          return <>Prior Authorization</>;
        } else if (doc.document_type === 'ST') {
          return <>Step Therapy</>;
        } else if (doc.document_type === 'Formulary') {
          return <>Formulary</>;
        } else {
          return null;
        }
      },
    },
    {
      title: 'Effective Date',
      key: 'effective_date',
      render: (doc: RetrievedDocument) => {
        if (!doc.effective_date) return null;
        return <>{format(parseISO(doc.effective_date), 'yyyy-MM-dd')}</>;
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
          </>
        );
      },
    },
  ];
  return (
    <div>
      <div className="flex">
        <Title className="inline-block" level={4}>
          Extractions
        </Title>
      </div>
      <Table
        dataSource={documents}
        columns={columns}
        rowKey={(doc) => doc._id}
      />
    </div>
  );
}
