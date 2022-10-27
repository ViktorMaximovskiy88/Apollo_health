import { useCallback, useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Form, Select, Button, Spin } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { DocumentFamily } from './document_family/types';
import { DocumentFamilyCreateModal } from './document_family/DocumentFamilyCreateModal';
import { useLazyGetDocumentFamiliesQuery } from './document_family/documentFamilyApi';
import { useGetDocDocumentQuery } from './docDocumentApi';

interface Option {
  value: string;
  label: string;
}

const useOptions = () => {
  const form = Form.useFormInstance();
  const documentType = Form.useWatch('document_type');
  const [getDocumentFamilies] = useLazyGetDocumentFamiliesQuery();
  const [options, setOptions] = useState<Option[]>([]);
  const [loading, setLoading] = useState(false);

  const selectedInOptions = useCallback(
    (options: Option[]) => {
      const documentFamilyId = form.getFieldValue('document_family_id');
      return options.map((option: Option) => option.value).includes(documentFamilyId);
    },
    [form]
  );

  useEffect(() => {
    setLoading(true);
    getDocumentFamilies({ documentType }).then(({ data }) => {
      const options =
        data?.data.map((item: DocumentFamily) => ({
          value: item._id,
          label: item.name,
        })) ?? [];

      setOptions(options);

      if (!selectedInOptions(options)) {
        form.setFieldValue('document_family_id', null);
      }

      setLoading(false);
    });
  }, [documentType, form, getDocumentFamilies, selectedInOptions]);
  return { options, loading };
};

export const DocDocumentInfoFormFamilyField = ({
  onFieldChange,
}: {
  onFieldChange: () => void;
}) => {
  const { docDocumentId: docId } = useParams();
  const { data: doc } = useGetDocDocumentQuery(docId);

  const form = Form.useFormInstance();
  const [isVisible, setIsVisible] = useState<boolean>(false);

  const { options, loading } = useOptions();
  const document_family_id = Form.useWatch('document_family_id');

  return (
    <div>
      <Form.Item
        label={
          <>
            Document Family <Spin className="ml-1" spinning={loading} size="small" />
          </>
        }
        name="document_family_id"
      >
        <Select
          value={document_family_id}
          onSelect={(documentFamilyId: string) => {
            form.setFieldsValue({ document_family_id: documentFamilyId });
            onFieldChange();
          }}
          options={options}
          style={{ width: 'calc(100% - 96px)', marginRight: '8px' }}
        />
        <Button
          type="dashed"
          onClick={() => {
            setIsVisible(true);
          }}
        >
          <PlusOutlined />
          New
        </Button>
      </Form.Item>

      <DocumentFamilyCreateModal
        documentType={doc?.document_type}
        open={isVisible}
        onSave={(documentFamilyId: string) => {
          setIsVisible(false);
        }}
        onClose={() => {
          setIsVisible(false);
        }}
      />
    </div>
  );
};
