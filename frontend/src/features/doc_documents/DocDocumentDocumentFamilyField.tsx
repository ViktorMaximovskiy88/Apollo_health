import { useCallback, useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Form, Button, FormInstance } from 'antd';
import { PlusOutlined, EditOutlined } from '@ant-design/icons';
import { DocumentFamily } from './document_family/types';
import { DocumentFamilyCreateDrawer } from './document_family/DocumentFamilyCreateDrawer';
import {
  useGetDocumentFamilyQuery,
  useLazyGetDocumentFamiliesQuery,
} from './document_family/documentFamilyApi';
import { useGetDocDocumentQuery } from './docDocumentApi';
import { RemoteSelect } from '../../components';

interface DocDocumentLocationsPropTypes {
  onFieldChange: () => void;
}

const useOnDocTypeChangeClearDocumentFamily = (
  setCurrentOption: (newCurrentOption?: { label: string; value: string }) => void
) => {
  const { docDocumentId: docId } = useParams();
  const { data: doc } = useGetDocDocumentQuery(docId);
  const document_type_selected = Form.useWatch('document_type');

  useEffect(() => {
    if (!doc?.document_type) return;
    if (doc.document_type === document_type_selected) {
      setCurrentOption(
        doc.document_family
          ? { value: doc.document_family._id, label: doc.document_family.name }
          : undefined
      );
      return;
    }
    setCurrentOption(undefined);
  }, [doc?.document_family, doc?.document_type, document_type_selected, setCurrentOption]);
};

export const useFetchDocFamilyOptions = (form?: FormInstance) => {
  const document_type_selected = Form.useWatch('document_type', form);
  const [getDocumentFamilies] = useLazyGetDocumentFamiliesQuery();

  const fetchDocFamilyOptions = useCallback(
    async (search: string) => {
      const { data } = await getDocumentFamilies({
        limit: 20,
        skip: 0,
        sortInfo: { name: 'name', dir: 1 },
        filterValue: [
          { name: 'name', operator: 'contains', type: 'string', value: search },
          { name: 'document_type', operator: 'eq', type: 'select', value: document_type_selected },
        ],
      });
      if (!data) return [];
      return data.data.map((item: DocumentFamily) => ({ value: item._id, label: item.name }));
    },
    [getDocumentFamilies, document_type_selected]
  );
  return fetchDocFamilyOptions;
};

export const DocDocumentDocumentFamilyField = ({
  onFieldChange,
}: DocDocumentLocationsPropTypes) => {
  const { docDocumentId: docId } = useParams();
  const { data: doc } = useGetDocDocumentQuery(docId);

  const form = Form.useFormInstance();
  const [isNewVisible, setIsNewVisible] = useState<boolean>(false);
  const [isEditVisible, setIsEditVisible] = useState<boolean>(false);
  const document_type_selected = Form.useWatch('document_type');
  const document_family_id = Form.useWatch('document_family_id');

  const [docFamilyData, setDocFamilyData] = useState<any>(undefined);
  let { data: docFamData } = useGetDocumentFamilyQuery(document_family_id, {
    skip: !document_family_id,
  });

  const [currentOption, setCurrentOption] = useState<any | undefined>(
    doc?.document_family
      ? { value: doc.document_family._id, label: doc.document_family.name }
      : undefined
  );

  useOnDocTypeChangeClearDocumentFamily(setCurrentOption);

  const fetchDocFamilyOptions = useFetchDocFamilyOptions();

  const additionalOptions = currentOption ? [currentOption] : [];

  useEffect(() => {
    if (document_family_id) {
      setDocFamilyData(docFamData);
    }
  }, [document_family_id, docFamData]);

  return (
    <Form.Item label="Document Family">
      <div className="flex space-x-2 pt-1">
        <Form.Item noStyle name="document_family_id">
          <RemoteSelect
            allowClear
            className="flex-grow ant-select-expandable"
            initialOptions={currentOption ? [currentOption] : []}
            fetchOptions={fetchDocFamilyOptions}
            value={currentOption}
            onDeselect={() => {
              form.setFieldsValue({ document_family_id: null });
              setCurrentOption(undefined);
            }}
            onSelect={(document_family_id: any, option: any) => {
              setCurrentOption(option);
              form.setFieldsValue({ document_family_id });
              onFieldChange();
            }}
            additionalOptions={additionalOptions}
          />
        </Form.Item>
        {document_family_id && (
          <Button
            type="dashed"
            className="mr-2"
            onClick={() => {
              setIsEditVisible(true);
            }}
          >
            <EditOutlined />
            Edit
          </Button>
        )}
        <DocumentFamilyCreateDrawer
          documentFamilyData={docFamilyData}
          documentType={docFamilyData?.document_type}
          open={isEditVisible}
          onSave={(documentFamily: DocumentFamily) => {
            setCurrentOption({ label: documentFamily.name, value: documentFamily._id }); // update label if changed
            onFieldChange();
            setIsEditVisible(false);
          }}
          onClose={() => {
            setIsEditVisible(false);
          }}
          mask={false}
        />

        <Button
          type="dashed"
          onClick={() => {
            setIsNewVisible(true);
          }}
        >
          <PlusOutlined />
          New
        </Button>
        <DocumentFamilyCreateDrawer
          documentType={document_type_selected ? document_type_selected : doc?.document_type}
          open={isNewVisible}
          onSave={(documentFamily: DocumentFamily) => {
            setCurrentOption({ value: documentFamily._id, label: documentFamily.name });
            form.setFieldsValue({ document_family_id: documentFamily._id });
            onFieldChange();
            setIsNewVisible(false);
          }}
          onClose={() => {
            setIsNewVisible(false);
          }}
          mask={false}
        />
      </div>
    </Form.Item>
  );
};
