import { Form, Button, Input, Row, Col } from 'antd';
import { Link } from 'react-router-dom';
import { EditOutlined, PlusOutlined } from '@ant-design/icons';
import { DocDocumentLocation } from '../doc_documents/locations/types';
import { PayerFamily as PayerFamilyType } from '../payer-family/types';
import { useLazyGetPayerFamiliesQuery } from '../payer-family/payerFamilyApi';
import { RemoteSelect, TextEllipsis } from '../../components';
import { LinkIcon } from '../../components/LinkIcon';
import { useCallback } from 'react';

export const useFetchPayerFamilyOptions = () => {
  const [getPayerFamilies] = useLazyGetPayerFamiliesQuery();
  const fetchPayerFamilyOptions = useCallback(
    async (search: string) => {
      const { data } = await getPayerFamilies({
        limit: 50,
        skip: 0,
        sortInfo: { name: 'name', dir: 1 },
        filterValue: [{ name: 'name', operator: 'contains', type: 'string', value: search }],
      });
      if (!data) return [];
      return data.data.map((item: PayerFamilyType) => ({ value: item._id, label: item.name }));
    },
    [getPayerFamilies]
  );
  return fetchPayerFamilyOptions;
};

interface DocDocumentLocationFormTypes {
  location: DocDocumentLocation;
  index: number;
  onShowPayerFamilyCreate: (location: DocDocumentLocation) => void;
  onShowPayerFamilyEdit: (location: DocDocumentLocation) => void;
  currentOption?: { value: string; label: string };
  setCurrentOption: (newCurrentOption: { value: string; label: string } | undefined) => void;
}

const PayerFamily = ({
  location,
  index,
  onShowPayerFamilyCreate,
  onShowPayerFamilyEdit,
  currentOption,
  setCurrentOption,
}: DocDocumentLocationFormTypes) => {
  const form = Form.useFormInstance();

  const updatedLocation = Form.useWatch(['locations', index]);

  const fetchPayerFamilyOptions = useFetchPayerFamilyOptions();

  return (
    <Form.Item label="Payer Family">
      <div className="flex space-x-2 pt-1 multi-line-select">
        <Form.Item noStyle name={['locations', index, 'payer_family_id']}>
          <RemoteSelect
            className="flex-grow"
            allowClear
            initialOptions={currentOption ? [currentOption] : []}
            fetchOptions={fetchPayerFamilyOptions}
            value={currentOption}
            onClear={() => {
              const locations = form.getFieldValue('locations');
              locations[index].payer_family_id = undefined;
              setCurrentOption(undefined);
              form.setFieldsValue({ locations });
            }}
            onSelect={(payerFamilyId: any, option: any) => {
              const locations = form.getFieldValue('locations');
              locations[index].payer_family_id = payerFamilyId;
              setCurrentOption(option);
              form.setFieldsValue({ locations });
            }}
          />
        </Form.Item>
        {updatedLocation?.payer_family_id ? (
          <Button
            className="mr-3"
            onClick={() => {
              onShowPayerFamilyEdit(updatedLocation);
            }}
            type="dashed"
          >
            <EditOutlined />
            Edit
          </Button>
        ) : null}
        <Button
          onClick={() => {
            onShowPayerFamilyCreate(location);
          }}
          type="dashed"
        >
          <PlusOutlined />
          New
        </Button>
      </div>
    </Form.Item>
  );
};

export function DocDocumentLocationForm({
  location,
  index,
  onShowPayerFamilyCreate,
  onShowPayerFamilyEdit,
  currentOption,
  setCurrentOption,
}: DocDocumentLocationFormTypes) {
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

        <PayerFamily
          key={location.site_id}
          index={index}
          location={location}
          onShowPayerFamilyCreate={onShowPayerFamilyCreate}
          onShowPayerFamilyEdit={onShowPayerFamilyEdit}
          currentOption={currentOption}
          setCurrentOption={setCurrentOption}
        />
      </div>
    </div>
  );
}
