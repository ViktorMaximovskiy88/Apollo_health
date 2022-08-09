import { Form, Input } from 'antd';
import { useLazyGetDocumentFamilyByNameQuery } from './documentFamilyApi';

export const Name = () => {
  const [getDocumentFamilyByName] = useLazyGetDocumentFamilyByNameQuery();

  const mustBeUnique = () => ({
    async validator(_: any, name: string) {
      if (!name) return;
      const { data: documentFamily } = await getDocumentFamilyByName(name);
      if (documentFamily) {
        return Promise.reject(
          new Error(`Document Family Name "${documentFamily.name}" already exists!`)
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
