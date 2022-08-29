import { Form, Select, Button } from 'antd';
import { Link } from 'react-router-dom';
import { PlusOutlined } from '@ant-design/icons';
import { DocDocumentLocation } from './types';
import { DocumentFamily } from '../document_family/types';
import { useGetDocumentFamiliesQuery } from '../document_family/documentFamilyApi';
import { TextEllipsis, ListViewItem } from '../../../components';

interface DocDocumentLocationRowPropTypes {
  documentType: string;
  location: DocDocumentLocation;
  index: number;
  onShowDocumentFamilyCreate: (location: DocDocumentLocation) => void;
}

export const DocDocumentLocationRow = ({
  documentType,
  location,
  index,
  onShowDocumentFamilyCreate,
}: DocDocumentLocationRowPropTypes) => {
  const { data = [] } = useGetDocumentFamiliesQuery({
    siteId: location.site_id,
    documentType,
  });

  const options = data.map((item: DocumentFamily) => ({ value: item._id, label: item.name }));

  return (
    <div>
      {/* Our header is separate due to styles */}
      <div className="p-2 bg-slate-50">
        <Link className="text-lg" target="_blank" to={`/sites/${location.site_id}/view`}>
          <TextEllipsis text={location.site_name || 'N/A'} />
        </Link>
      </div>

      {/* Our body */}
      <div className="pl-2">
        <ListViewItem label="Base URL">
          <Link target="_blank" to={location.base_url}>
            <TextEllipsis text={location.base_url} />
          </Link>
        </ListViewItem>

        <ListViewItem label="URL">
          <Link target="_blank" to={location.url}>
            <TextEllipsis text={location.url} rtl={true} />
          </Link>
        </ListViewItem>

        <ListViewItem label="Link Text">{location.link_text || 'N/A'}</ListViewItem>

        <Form.Item label="Document Family" name={['locations', index, 'document_family_id']}>
          <Select options={options} style={{ width: 'calc(100% - 96px', marginRight: '8px' }} />
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
