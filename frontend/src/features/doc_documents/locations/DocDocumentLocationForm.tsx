import { Form, Select, Button, Input, Row, Col } from 'antd';
import { Link } from 'react-router-dom';
import { PlusOutlined } from '@ant-design/icons';
import { DocDocumentLocation } from './types';
import { DocumentFamily } from '../document_family/types';
import { useGetDocumentFamiliesBySiteAndDocumentTypeQuery } from '../document_family/documentFamilyApi';
import { TextEllipsis } from '../../../components';

interface DocDocumentLocationFormTypes {
  documentType: string;
  location: DocDocumentLocation;
  index: number;
  onShowDocumentFamilyCreate: (location: DocDocumentLocation) => void;
}
export const DocDocumentLocationForm = ({
  documentType,
  location,
  index,
  onShowDocumentFamilyCreate,
}: DocDocumentLocationFormTypes) => {
  const form = Form.useFormInstance();
  const { data = [] } = useGetDocumentFamiliesBySiteAndDocumentTypeQuery({
    siteId: location.site_id,
    documentType,
  });

  const options = data.map((item: DocumentFamily) => ({ value: item._id, label: item.name }));
  const updatedLocation = Form.useWatch(['locations', index]);
  const baseUrl = Form.useWatch(['locations', index, 'base_url']);
  const url = Form.useWatch(['locations', index, 'url']);

  return (
    <div className="property-grid mb-4">
      {/* Our header is separate due to styles */}
      <div className="p-2 bg-slate-50">
        <Link className="text-lg" target="_blank" to={`/sites/${location.site_id}/view`}>
          <TextEllipsis text={location.site_name ?? ''} />
        </Link>
      </div>

      {/* Our body */}
      <div className="pl-2 mt-2">
        <Form.Item name={['locations', index, 'site_id']} noStyle={true}>
          <Input type={'hidden'} />
        </Form.Item>

        <Form.Item name={['locations', index, 'closest_heading']} noStyle={true}>
          <Input type={'hidden'} />
        </Form.Item>

        <Form.Item name={['locations', index, 'first_collected_date']} noStyle={true}>
          <Input type={'hidden'} />
        </Form.Item>

        <Form.Item name={['locations', index, 'last_collected_date']} noStyle={true}>
          <Input type={'hidden'} />
        </Form.Item>

        <Form.Item name={['locations', index, 'previous_doc_doc_id']} noStyle={true}>
          <Input type={'hidden'} />
        </Form.Item>

        <Row>
          <Col span={23}>
            <Form.Item label="Base URL" name={['locations', index, 'base_url']}>
              <Input readOnly={true} />
            </Form.Item>
          </Col>
          <Col span={1}>
            <Form.Item label=" ">
              <LinkIcon href={baseUrl} />
            </Form.Item>
          </Col>
        </Row>

        <Row>
          <Col span={23}>
            <Form.Item label="URL" name={['locations', index, 'url']}>
              <Input readOnly={true} />
            </Form.Item>
          </Col>
          <Col span={1}>
            <Form.Item label=" ">
              <LinkIcon href={url} />
            </Form.Item>
          </Col>
        </Row>

        <Form.Item label="Link Text" name={['locations', index, 'link_text']}>
          <Input readOnly={true} />
        </Form.Item>

        <Form.Item label="Document Family" name={['locations', index, 'document_family_id']}>
          <Select
            value={updatedLocation?.document_family_id}
            onSelect={(documentFamilyId: string) => {
              const locations = form.getFieldValue('locations');
              locations[index].document_family_id = documentFamilyId;
              form.setFieldsValue({ locations });
            }}
            options={options}
            style={{ width: 'calc(100% - 96px', marginRight: '8px' }}
          />
          <Button
            type="dashed"
            onClick={() => {
              onShowDocumentFamilyCreate(location);
            }}
          >
            <PlusOutlined />
            New
          </Button>
        </Form.Item>
      </div>
    </div>
  );
};
