import { Form, Input } from 'antd';
import { Rule } from 'antd/lib/form';
import { useParams } from 'react-router-dom';
import { useGetDocDocumentQuery } from './docDocumentApi';
import { useLazyGetDocumentFamilyByNameQuery } from './documentFamilyApi';

export const Name = () => {
  const [getDocumentFamilyByName] = useLazyGetDocumentFamilyByNameQuery();
  const { docDocumentId: docId } = useParams();
  const { data: doc } = useGetDocDocumentQuery(docId);
  const siteId = doc?.site_id;

  const mustBeUnique = () => ({
    async validator(_: Rule, name: string) {
      if (!name) return;
      if (!siteId) return Promise.reject(new Error(`Site ID not found. Please try again.`));
      const { data: documentFamily } = await getDocumentFamilyByName({ name, siteId });
      if (documentFamily) {
        return Promise.reject(
          new Error(`Document Family Name "${documentFamily.name}" already exists on this site!`)
        );
      }
      return Promise.resolve();
    },
  });

  return (
    <div className="flex space-x-8">
      <Form.Item
        name="name"
        label="Document Family Name"
        className="flex-1"
        rules={[mustBeUnique, { required: true, message: 'Please input a Document Family Name!' }]}
        required
      >
        <Input />
      </Form.Item>
    </div>
  );
};
