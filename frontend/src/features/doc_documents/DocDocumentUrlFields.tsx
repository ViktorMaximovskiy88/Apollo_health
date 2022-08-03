import { Form } from 'antd';
import { DocDocument } from './types';

const BaseUrl = ({ doc }: { doc: DocDocument }) => (
  <Form.Item name="base_url" label="Base URL">
    {doc.base_url && (
      <a target="_blank" href={doc.base_url} rel="noreferrer">
        {doc.base_url}
      </a>
    )}
  </Form.Item>
);
const LinkText = ({ doc }: { doc: DocDocument }) => (
  <Form.Item name="link_text" label="Link Text">
    {doc.link_text}
  </Form.Item>
);
const LinkUrl = ({ doc }: { doc: DocDocument }) => (
  <Form.Item className="grow" name="url" label="Link URL">
    {doc.url && (
      <a target="_blank" href={doc.url} rel="noreferrer">
        {doc.url}
      </a>
    )}
  </Form.Item>
);

export const UrlFields = ({ doc }: { doc: DocDocument }) => (
  <>
    <BaseUrl doc={doc} />
    <LinkText doc={doc} />
    <LinkUrl doc={doc} />
  </>
);
