import { Button, Popconfirm, Table } from "antd";
import Title from "antd/lib/typography/Title";
import { format, parseISO } from "date-fns";
import { useSearchParams } from "react-router-dom";
import { ButtonLink } from "../../components/ButtonLink";
import { ChangeLogModal } from "../change_log/ChangeLogModal";
import { useDeleteDocumentMutation, useGetChangeLogQuery, useGetDocumentsQuery } from "./documentsApi";
import { RetrievedDocument } from "./types";

export function DocumentsHomePage() {
  const [searchParams] = useSearchParams()
  const [deleteDocument] = useDeleteDocumentMutation()
  const scrapeTaskId = searchParams.get('scrape_task_id')
  const { data: documents } = useGetDocumentsQuery({ scrape_task_id: scrapeTaskId })

  const columns = [{
      title: 'Collection Time',
      key: 'collection_time',
      render: (doc: RetrievedDocument) => {
        return <>{format(parseISO(doc.collection_time), 'yyyy-MM-dd p')}</>;
      },
  }, {
      title: 'Name',
      key: 'name',
      filterSearch: true,
      render: (doc: RetrievedDocument) => {
        return <>{doc.name}</>
      }
  }, {
      title: 'Document Type',
      key: 'document_type',
      render: (doc: RetrievedDocument) => {
          if (doc.document_type === 'PA') {
              return <>Prior Authorization</>
          } else if (doc.document_type === 'ST') {
              return <>Step Therapy</>
          } else if (doc.document_type === 'Formulary') {
              return <>Formulary</>
          } else {
              return null
          }
      }
  }, {
  }, {
      title: 'Effective Date',
      key: 'effective_date',
      render: (doc: RetrievedDocument) => {
        if (!doc.effective_date) return null;
        return <>{format(parseISO(doc.effective_date), 'yyyy-MM-dd')}</>
      }
  }, {
      title: 'URL',
      key: 'url',
      render: (doc: RetrievedDocument) => {
        return <a target="_blank" rel="noreferrer" href={doc.url}>Link</a>
      }
  }, {
      title: 'Actions',
      key: 'action',
      render: (doc: RetrievedDocument) => {
        return (
          <>
            <ButtonLink to={`${doc._id}/edit`}>Edit</ButtonLink>
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
    } ]
  return (
    <div>
      <div className="flex">
        <Title className="inline-block" level={4}>Documents</Title>
        <Button className="ml-auto">Create Document</Button>
      </div>
      <Table dataSource={documents} columns={columns} rowKey={(doc) => doc._id}/>
    </div>
  );
}
