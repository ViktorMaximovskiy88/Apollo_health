import { Form } from 'antd';
import { useGetDocDocumentQuery } from './docDocumentApi';

const BaseUrl = () => {
  const form = Form.useFormInstance();
  const docId = form.getFieldValue('docId');
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
  const form = Form.useFormInstance();
  const docId = form.getFieldValue('docId');
  const { data: doc } = useGetDocDocumentQuery(docId);
  if (!doc) return null;

  return <Form.Item label="Link Text">{doc.link_text}</Form.Item>;
};

const LinkUrl = () => {
  const form = Form.useFormInstance();
  const docId = form.getFieldValue('docId');
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
