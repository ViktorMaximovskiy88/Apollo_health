import { Form } from 'antd';
import { useParams } from 'react-router-dom';
import { useGetDocDocumentQuery } from './docDocumentApi';

const BaseUrl = () => {
  const { docDocumentId: docId } = useParams();
  const { data: doc } = useGetDocDocumentQuery(docId);
  if (!doc) return null;

  return (
    <Form.Item label="Base URL">
      {doc.base_url && (
        <a target="_blank" href={doc.base_url} rel="noreferrer">
          {doc.base_url}
        </a>
      )}
    </Form.Item>
  );
};

const LinkText = () => {
  const { docDocumentId: docId } = useParams();
  const { data: doc } = useGetDocDocumentQuery(docId);
  if (!doc) return null;

  return <Form.Item label="Link Text">{doc.link_text}</Form.Item>;
};

const LinkUrl = () => {
  const { docDocumentId: docId } = useParams();
  const { data: doc } = useGetDocDocumentQuery(docId);
  if (!doc) return null;

  return (
    <Form.Item className="grow" label="Link URL">
      {doc.url && (
        <a target="_blank" href={doc.url} rel="noreferrer">
          {doc.url}
        </a>
      )}
    </Form.Item>
  );
};

export const UrlFields = () => (
  <>
    <BaseUrl />
    <LinkText />
    <LinkUrl />
  </>
);
