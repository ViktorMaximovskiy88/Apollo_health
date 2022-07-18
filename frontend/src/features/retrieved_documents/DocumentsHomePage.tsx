import { Button, Popconfirm, Table } from 'antd';
import { prettyDateFromISO, prettyDateTimeFromISO } from '../../common';
import { Link, useSearchParams } from 'react-router-dom';
import { ButtonLink } from '../../components/ButtonLink';
import { ChangeLogModal } from '../change-log/ChangeLogModal';
import {
  useDeleteDocumentMutation,
  useGetChangeLogQuery,
  useGetDocumentsQuery,
} from './documentsApi';
import { RetrievedDocument } from './types';
import { MainLayout } from '../../components';

export function DocumentsHomePage() {
  const [searchParams] = useSearchParams();
  const [deleteDocument] = useDeleteDocumentMutation();
  const scrapeTaskId = searchParams.get('scrape_task_id');
  const { data: documents } = useGetDocumentsQuery({
    scrape_task_id: scrapeTaskId,
  });

  const columns = [
    {
      title: 'Collection Time',
      key: 'first_collected_date',
      render: (doc: RetrievedDocument) => {
        return prettyDateTimeFromISO(doc.first_collected_date);
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
        return prettyDateFromISO(doc.effective_date); // this function may be broken. or just use pretty date? tbd
      },
    },
    {
      title: 'URL',
      key: 'url',
      render: (doc: RetrievedDocument) => {
        return (
          <a target="_blank" rel="noreferrer" href={doc.url}>
            Link
          </a>
        );
      },
    },
    {
      title: 'Actions',
      key: 'action',
      render: (doc: RetrievedDocument) => {
        return (
          <>
            <ButtonLink to={`${doc._id}/edit`}>Edit</ButtonLink>
            {doc.automated_content_extraction && (
              <ButtonLink to={`/extractions/?retrieved_document_id=${doc._id}`}>
                Extraction
              </ButtonLink>
            )}
            <ChangeLogModal target={doc} useChangeLogQuery={useGetChangeLogQuery} />
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
    <MainLayout
      pageTitle="Documents"
      pageToolbar={
        <>
          <Button className="ml-auto">Create Document</Button>
        </>
      }
    >
      <Table dataSource={documents} columns={columns} rowKey={(doc) => doc._id} />
    </MainLayout>
  );
}
