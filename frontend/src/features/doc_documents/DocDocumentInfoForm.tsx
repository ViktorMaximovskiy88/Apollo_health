import { Form, Input, FormInstance, Select, Button } from 'antd';
import { Hr } from '../../components';
import { DocDocument } from './types';
import { DateFields } from './DocDocumentDateFields';
import { DocumentClassification } from './DocDocumentClassificationFields';
import { ExtractionFields } from './DocDocumentExtractionFields';
import { UrlFields } from './DocDocumentUrlFields';
import { PlusOutlined } from '@ant-design/icons';

const Name = () => (
  <Form.Item name="name" label="Name" required={true}>
    <Input />
  </Form.Item>
);

const DocumentFamily = () => {
  const { Option } = Select;
  const children = [];

  for (let i = 10; i < 36; i++) {
    children.push(<Option key={i.toString(36) + i}>{i.toString(36) + i}</Option>);
  }

  const handleChange = (value: string[]) => {
    console.log(`selected ${value}`);
  };
  return (
    <div className="flex space-x-8">
      <Form.Item name="document_family" label="Document Family" className="flex-1">
        <Select
          mode="multiple"
          allowClear
          placeholder="Please select"
          defaultValue={['a10', 'c12']}
          onChange={handleChange}
        >
          {children}
        </Select>
      </Form.Item>
      <Button className="flex-1 my-7" type="dashed">
        <PlusOutlined />
        Add New Document Family
      </Button>
    </div>
  );
};

export function DocDocumentInfoForm(props: {
  doc: DocDocument;
  form: FormInstance;
  onFieldChange: Function;
}) {
  const { doc } = props;
  return (
    <>
      <Name />
      <Hr />
      <DocumentClassification doc={doc} />
      <Hr />
      <DocumentFamily />
      <Hr />
      <DateFields {...props} />
      <Hr />
      <ExtractionFields doc={doc} />
      <Hr />
      <UrlFields doc={doc} />
    </>
  );
}
