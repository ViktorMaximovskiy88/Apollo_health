import { useState, useEffect } from 'react';
import {
  Button,
  Modal,
  Form,
  Space,
  Input,
  Upload,
  DatePicker,
  Select,
  Tooltip,
  message,
  Checkbox,
  notification,
} from 'antd';
import { useForm } from 'antd/lib/form/Form';
import { UploadChangeParam } from 'antd/lib/upload';
import { UploadFile } from 'antd/lib/upload/interface';
import {
  UploadOutlined,
  QuestionCircleOutlined,
  LoadingOutlined,
  CheckCircleOutlined,
} from '@ant-design/icons';

import { prettyDate } from '../../common';
import { useAddDocumentMutation } from '../retrieved_documents/documentsApi';
import { baseApiUrl, client } from '../../app/base-api';
import { DocumentTypes, languageCodes } from '../retrieved_documents/types';
import { SiteDocDocument } from '../doc_documents/types';

interface AddDocumentModalPropTypes {
  oldVersion?: SiteDocDocument;
  setOpen: (open: boolean) => void;
  siteId: any;
  refetch?: any;
}

const buildInitialValues = (oldVersion?: SiteDocDocument) => {
  if (!oldVersion) {
    return {
      lang_code: 'en',
      internal_document: false,
    };
  }
  return {
    lang_code: oldVersion.lang_code,
    name: oldVersion.name,
    document_type: oldVersion.document_type,
    internal_document: oldVersion.internal_document,
    site_id: oldVersion.site_id,
    link_text: oldVersion.link_text,
    base_url: oldVersion.base_url,
    url: oldVersion.url,
  };
};

const displayDuplicateError = (error: any) => {
  notification.error({
    message: 'Document already exists',
    description: `Upload a new document or enter a new location.`,
  });
};

export function AddDocumentModal({
  oldVersion,
  setOpen,
  siteId,
  refetch,
}: AddDocumentModalPropTypes) {
  const [form] = useForm();
  const [addDoc] = useAddDocumentMutation();
  const [fileData, setFileData] = useState<any>();
  const [docTitle, setDocTitle] = useState('Add new document');

  const initialValues = buildInitialValues(oldVersion);
  if (docTitle !== 'Add New Version' && oldVersion) {
    setDocTitle('Add New Version');
  }

  /* eslint-disable no-template-curly-in-string */
  const validateMessages = {
    required: '${label} is required!',
    types: {
      url: '${label} is not a valid url!',
    },
  };
  /* eslint-enable no-template-curly-in-string */

  async function saveDocument(newDocument: any) {
    try {
      newDocument.site_id = siteId;
      if (oldVersion) {
        newDocument.upload_new_version_for_id = oldVersion._id;
        if (oldVersion.internal_document) {
          newDocument.internal_document = oldVersion.internal_document;
        } else {
          newDocument.internal_document = false;
        }
      }
      newDocument.url = form.getFieldValue('url');
      newDocument.base_url = form.getFieldValue('base_url') ?? newDocument.url;
      newDocument.link_text = form.getFieldValue('link_text');

      // For some reason, fileData never updates if browser auto fills.
      fileData.url = form.getFieldValue('url');
      fileData.base_url = form.getFieldValue('base_url') ?? newDocument.url;
      fileData.link_text = form.getFieldValue('link_text');
      fileData.metadata.link_text = newDocument.link_text;
      delete newDocument.link_text;
      delete newDocument.document_file;

      try {
        const response = await addDoc({
          ...newDocument,
          ...fileData,
        });
        if (refetch) {
          refetch();
        }
        if ('error' in response && response.error) {
          displayDuplicateError(response);
        } else {
          setOpen(false);
        }
      } catch (error: any) {
        notification.error({
          message: error.data.detail,
          description: `Upload a new document or enter a new location.`,
        });
      }
    } catch (error) {
      message.error('We could not save this document');
    }
  }
  function onCancel() {
    setOpen(false);
  }

  function setLocationValuesFromResponse(responseData: any) {
    form.setFieldsValue({
      base_url: responseData.base_url,
      url: responseData.url,
      link_text: responseData.link_text,
    });
  }

  return (
    <Modal open={true} title={docTitle} onCancel={onCancel} width={1000} footer={null}>
      <Form
        layout="vertical"
        form={form}
        requiredMark={false}
        initialValues={initialValues}
        validateMessages={validateMessages}
        onFinish={saveDocument}
      >
        <div className="flex grow space-x-3">
          <UploadItem
            form={form}
            setFileData={setFileData}
            siteId={siteId}
            setLocationValuesFromResponse={setLocationValuesFromResponse}
          />
          <InternalDocument oldVersion={oldVersion} />
        </div>

        <div className="flex grow space-x-3">
          <Form.Item
            className="grow"
            name="name"
            label="Document Name"
            rules={[{ required: true }]}
          >
            <Input />
          </Form.Item>
          <DocumentTypeItem />
          <LanguageItem />
        </div>
        <div className="flex grow space-x-3">
          <Form.Item className="grow" name="base_url" label="Base Url" rules={[{ type: 'url' }]}>
            <Input type="url" />
          </Form.Item>
          <Form.Item className="grow" name="link_text" label="Link Text">
            <Input />
          </Form.Item>
          <Form.Item
            className="grow"
            name="url"
            label="Link Url"
            rules={[{ type: 'url', required: true }]}
          >
            <Input type="url" />
          </Form.Item>
        </div>
        <DateItems />
        <Form.Item>
          <Space>
            <Button type="primary" htmlType="submit">
              Save
            </Button>
            <Button onClick={onCancel} htmlType="submit">
              Cancel
            </Button>
          </Space>
        </Form.Item>
      </Form>
    </Modal>
  );
}

function UploadItem(props: any) {
  const { setFileData, siteId, setLocationValuesFromResponse } = props;
  const [token, setToken] = useState('');
  const [fileName, setFileName] = useState('');
  const [uploadStatus, setUploadStatus] = useState('');

  useEffect(() => {
    client.getTokenSilently().then((t) => setToken(t));
  }, [setToken]);

  const onChange = (info: UploadChangeParam<UploadFile<unknown>>) => {
    const { file } = info;
    setFileName(file.name);
    if (file.status === 'uploading') {
      setUploadStatus('uploading');
    }
    if (file.status === 'done') {
      const response: any = file.response;
      if (response.error) {
        setUploadStatus('');
        message.error(response.error);
      } else if (response.success) {
        setUploadStatus('done');
        setLocationValuesFromResponse(response.data);
        setFileData(response.data);
      }
    }
  };

  return (
    <div className="flex grow space-x-4">
      <Form.Item
        name="document_file"
        label="Document File"
        rules={[{ required: uploadStatus === 'done' ? false : true }]}
      >
        <Upload
          name="file"
          accept=".pdf,.xlsx,.docx"
          action={`${baseApiUrl}/documents/upload/${siteId}`}
          headers={{
            Authorization: `Bearer ${token}`,
          }}
          showUploadList={false}
          onChange={onChange}
        >
          {uploadStatus === 'uploading' ? (
            <Button style={{ marginRight: '10px' }} icon={<LoadingOutlined />}>
              Uploading {fileName}...
            </Button>
          ) : uploadStatus === 'done' ? (
            <Button style={{ marginRight: '10px' }} icon={<CheckCircleOutlined />}>
              {fileName} uploaded!
            </Button>
          ) : (
            <Button style={{ marginRight: '10px' }} icon={<UploadOutlined />}>
              Click to Upload
            </Button>
          )}
        </Upload>
        <Tooltip placement="right" title="Only upload .pdf, .xlsx and .docx">
          <QuestionCircleOutlined />
        </Tooltip>
      </Form.Item>
    </div>
  );
}

function InternalDocument(props: any) {
  const { oldVersion } = props;

  return (
    <>
      <div className="mt-1">Internal Document&nbsp;</div>
      <Form.Item valuePropName="checked" className="grow" name="internal_document">
        <Checkbox disabled={oldVersion ? true : false} />
      </Form.Item>
    </>
  );
}

function DocumentTypeItem() {
  return (
    <Form.Item
      className="grow"
      name="document_type"
      label="Document Type"
      rules={[{ required: true }]}
    >
      <Select options={DocumentTypes} />
    </Form.Item>
  );
}

function LanguageItem() {
  return (
    <Form.Item className="grow" name="lang_code" label="Language" rules={[{ required: true }]}>
      <Select options={languageCodes} />
    </Form.Item>
  );
}

function DateItems(props: any) {
  let fields = [
    [
      {
        name: 'effective_date',
        title: 'Effective Date',
      },
    ],
    [
      {
        name: 'last_reviewed_date',
        title: 'Last Reviewed Date',
      },
      {
        name: 'last_updated_date',
        title: 'Last Updated Date',
      },
      {
        name: 'next_review_date',
        title: 'Next Review Date',
      },
    ],
    [
      {
        name: 'next_update_date',
        title: 'Next Update Date',
      },
      {
        name: 'first_created_date',
        title: 'First Created Date',
      },
      {
        name: 'published_date',
        title: 'Published Date',
      },
    ],
  ];
  return (
    <>
      {fields.map((section, i) => {
        return (
          <div key={i} className="flex grow space-x-3">
            {section.map((field) => {
              return (
                <Form.Item key={field.name} name={field.name} className="grow" label={field.title}>
                  <DatePicker
                    mode="date"
                    showTime={false}
                    style={{ width: '100%' }}
                    format={(value) => prettyDate(value.toDate())}
                  />
                </Form.Item>
              );
            })}
          </div>
        );
      })}
    </>
  );
}
