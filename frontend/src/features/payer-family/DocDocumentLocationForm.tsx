import { Form, Select, Button, Input, Row, Col } from 'antd';
import { Link } from 'react-router-dom';
import { PlusOutlined } from '@ant-design/icons';
import { DocDocumentLocation } from '../doc_documents/locations/types';
import { PayerFamily } from '../payer-family/types';
import { useGetPayerFamiliesQuery } from '../payer-family/payerFamilyApi';
import { TextEllipsis } from '../../components';
import { LinkIcon } from '../../components/LinkIcon';
import { useMemo } from 'react';

interface DocDocumentLocationFormTypes {
  documentType: string;
  location: DocDocumentLocation;
  index: number;
  onShowPayerFamilyCreate: (location: DocDocumentLocation) => void;
}
const useGetPayerFamilies = () => {
  const args = useMemo(() => {
    return {
      limit: 1000,
      skip: 0,
      sortInfo: { name: 'name', dir: -1 as 1 | -1 | 0 },
      filterValue: [
        { name: 'name', operator: 'eq', type: 'string', value: '' },
        { name: 'document_type', operator: 'eq', type: 'string', value: '' },
      ],
    };
  }, []);
  return useGetPayerFamiliesQuery(args);
};
export const DocDocumentLocationForm = ({
  documentType,
  location,
  index,
  onShowPayerFamilyCreate,
}: DocDocumentLocationFormTypes) => {
  const form = Form.useFormInstance();

  const { data } = useGetPayerFamilies();
  const options = data?.data.map((item: PayerFamily) => ({ value: item._id, label: item.name }));
  const updatedLocation = Form.useWatch(['locations', index]);
  const baseUrl = Form.useWatch(['locations', index, 'base_url']);
  const url = Form.useWatch(['locations', index, 'url']);

  return (
    <div className="property-grid bg-white p-2 mb-4">
      {/* Our header is separate due to styles */}
      <div className="p-2">
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

        <Form.Item label="Payer Family" name={['locations', index, 'payer_family_id']}>
          <Select
            value={updatedLocation?.payer_family_id}
            onSelect={(payerFamilyId: string) => {
              const locations = form.getFieldValue('locations');
              locations[index].payer_family_id = payerFamilyId;
              form.setFieldsValue({ locations });
            }}
            options={options}
            style={{ width: 'calc(100% - 96px', marginRight: '8px' }}
          />
          <Button
            type="dashed"
            onClick={() => {
              onShowPayerFamilyCreate(location);
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
