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
import moment from 'moment';

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

const displayDuplicateError = (err_msg: string) => {
  notification.error({
    message: err_msg,
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
  const [oldLocationSiteId, setOldLocationSiteId] = useState('');
  const [oldLocationDocId, setOldLocationDocId] = useState('');
  const [isEditingDocFromOtherSite, setIsEditingDocFromOtherSite] = useState(false);

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

      if (oldLocationSiteId) {
        newDocument.prev_location_site_id = oldLocationSiteId;
        newDocument.prev_location_doc_id = oldLocationDocId;
      }

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
          displayDuplicateError('Document exists on this site');
        } else {
          setOpen(false);
        }
      } catch (error: any) {
        notification.error({
          message: error.data.detail,
          description: 'Upload a new document or enter a new location.',
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
      name: responseData.doc_name,
      base_url: responseData.base_url,
      document_type: responseData.document_type,
      lang_code: responseData.lang_code,
      effective_date: convertDate(responseData.effective_date),
      last_reviewed_date: convertDate(responseData.last_reviewed_date),
      last_updated_date: convertDate(responseData.last_updated_date),
      next_review_date: convertDate(responseData.next_review_date),
      next_update_date: convertDate(responseData.next_update_date),
      published_date: convertDate(responseData.published_date),
    });
    if (responseData.prev_location_doc_id) {
      displayDuplicateError('Document exists on other site');
      setOldLocationSiteId(responseData.prev_location_site_id);
      setOldLocationDocId(responseData.prev_location_doc_id);
      setIsEditingDocFromOtherSite(true);
    } else {
      setIsEditingDocFromOtherSite(false);
    }
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
        <UploadItem
          form={form}
          setFileData={setFileData}
          siteId={siteId}
          setLocationValuesFromResponse={setLocationValuesFromResponse}
        />

        <div className="flex grow space-x-3">
          <Form.Item
            className="grow"
            style={{ width: '50%' }}
            name="name"
            label="Document Name"
            rules={[{ required: true }]}
          >
            <Input disabled={isEditingDocFromOtherSite ? true : false} />
          </Form.Item>
          <DocumentTypeItem isEditingDocFromOtherSite={isEditingDocFromOtherSite} />
          <LanguageItem isEditingDocFromOtherSite={isEditingDocFromOtherSite} />
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
        <DateItems oldVersion={oldVersion} isEditingDocFromOtherSite={isEditingDocFromOtherSite} />
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
    <div className="flex grow space-x-1">
      <Form.Item
        name="document_file"
        rules={[{ required: uploadStatus === 'done' ? false : true }]}
        label="Document File"
        style={{ width: '100%' }}
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
            <Button icon={<LoadingOutlined />}>Uploading {fileName}...</Button>
          ) : uploadStatus === 'done' ? (
            <Button style={{ whiteSpace: 'normal' }} icon={<CheckCircleOutlined />}>
              {fileName} uploaded!
            </Button>
          ) : (
            <Button style={{ whiteSpace: 'normal' }} icon={<UploadOutlined />}>
              Click to Upload
            </Button>
          )}
        </Upload>
        <Tooltip placement="top" title="Only upload .pdf, .xlsx and .docx">
          <QuestionCircleOutlined style={{ marginLeft: '10px', marginTop: '5px' }} />
        </Tooltip>
      </Form.Item>
    </div>
  );
}

function InternalDocument(props: any) {
  const { oldVersion, isEditingDocFromOtherSite } = props;

  return (
    <>
      <Form.Item
        style={{ marginTop: '30px', paddingLeft: '5px', width: '33%' }}
        valuePropName="checked"
        name="internal_document"
      >
        <Checkbox disabled={isEditingDocFromOtherSite || oldVersion ? true : false}>
          Internal Document
        </Checkbox>
      </Form.Item>
    </>
  );
}

function DocumentTypeItem(props: any) {
  const { isEditingDocFromOtherSite } = props;

  return (
    <Form.Item
      className="grow"
      name="document_type"
      label="Document Type"
      rules={[{ required: true }]}
    >
      <Select
        showSearch
        options={DocumentTypes}
        disabled={isEditingDocFromOtherSite ? true : false}
      />
    </Form.Item>
  );
}

function LanguageItem(props: any) {
  const { isEditingDocFromOtherSite } = props;

  return (
    <Form.Item className="grow" name="lang_code" label="Language" rules={[{ required: true }]}>
      <Select
        showSearch
        options={languageCodes}
        disabled={isEditingDocFromOtherSite ? true : false}
      />
    </Form.Item>
  );
}

function convertDate(date?: string) {
  if (date) return moment(date);
  return undefined;
}

function DateItems(props: any) {
  const { oldVersion, isEditingDocFromOtherSite } = props;

  let fields = [
    [
      {
        name: 'effective_date',
        title: 'Effective Date',
      },
      {
        name: 'internal_document',
        title: 'Internal Document',
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
              if (field.name === 'internal_document') {
                return (
                  <InternalDocument
                    oldVersion={oldVersion}
                    isEditingDocFromOtherSite={isEditingDocFromOtherSite}
                  />
                );
              } else {
                return (
                  <Form.Item
                    key={field.name}
                    name={field.name}
                    className="grow"
                    label={field.title}
                  >
                    <DatePicker
                      style={{ width: '100%' }}
                      className="grow"
                      mode="date"
                      showTime={false}
                      format={(value) => prettyDate(value.toDate())}
                      disabled={isEditingDocFromOtherSite ? true : false}
                    />
                  </Form.Item>
                );
              }
            })}
          </div>
        );
      })}
    </>
  );
}
