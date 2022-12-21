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
  notification,
  Switch,
  AutoComplete,
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

import { dateToMoment, prettyDateFromISO } from '../../common';
import { useAddDocumentMutation } from '../retrieved_documents/documentsApi';
import { baseApiUrl, client } from '../../app/base-api';
import { DocumentTypes, languageCodes } from '../retrieved_documents/types';
import { SiteDocDocument } from '../doc_documents/types';
import { useGetSiteQuery } from '../sites/sitesApi';

interface AddDocumentModalPropTypes {
  oldVersion?: SiteDocDocument;
  setOpen: (open: boolean) => void;
  siteId: any;
  refetch?: any;
}

const buildInitialValues = (oldVersion?: SiteDocDocument, baseUrlOptions?: any[]) => {
  if (!oldVersion) {
    const values = {
      lang_code: 'en',
      internal_document: false,
      base_url: '',
    };
    if (baseUrlOptions && baseUrlOptions.length > 0) {
      values.base_url = baseUrlOptions[0];
    }
    return values;
  }
  return {
    base_url: oldVersion.base_url,
    url: oldVersion.url,
    link_text: oldVersion.link_text,
    lang_code: oldVersion.lang_code,
    name: oldVersion.name,
    document_type: oldVersion.document_type,
    internal_document: oldVersion.internal_document,
    site_id: oldVersion.site_id,
  };
};

const displayDuplicateError = (err_msg: string) => {
  notification.error({
    message: err_msg,
  });
};

const setDatesToUtcStart = (newDocument: any) => {
  // fixes bug where dates are sent as the next day after 8pm Eastern
  const dates = [
    'effective',
    'last_reviewed',
    'next_update',
    'last_updated',
    'next_review',
    'first_created',
    'published',
  ];
  for (const date of dates) {
    if (!(date in newDocument)) {
      continue;
    }
    newDocument[`${date}_date`].utc(true).startOf('day');
  }
  return newDocument;
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
  const [existsOnThisSite, setExistsOnThisSite] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [baseUrlOptions, setBaseUrlOptions] = useState<{ value: string }[]>([]);
  const [initialBaseUrlOptions, setInitialBaseUrlOptions] = useState<{ value: string }[]>([]);

  // Set initial values.
  const { data: site } = useGetSiteQuery(siteId);
  if (site && site.base_urls.length > 0 && initialBaseUrlOptions.length === 0) {
    const base_urls = [] as any[];
    site.base_urls.map((base_url) => base_urls.push({ value: base_url.url }));
    setBaseUrlOptions(base_urls);
    setInitialBaseUrlOptions(base_urls);
  }
  const initialValues = buildInitialValues(oldVersion, baseUrlOptions);
  if (docTitle !== 'Add New Version' && oldVersion) {
    setDocTitle('Add New Version');
  }

  const onBaseUrlSearch = (searchText: string) => {
    if (searchText) {
      const newOptions = baseUrlOptions.filter((option) =>
        option.value.toUpperCase().includes(searchText.toUpperCase())
      );
      setBaseUrlOptions(newOptions);
    } else {
      setBaseUrlOptions(initialBaseUrlOptions);
    }
  };

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
      // Doc already exists on another site.
      if (oldLocationSiteId) {
        newDocument.prev_location_site_id = oldLocationSiteId;
        newDocument.prev_location_doc_id = oldLocationDocId;
      }
      newDocument.exists_on_this_site = existsOnThisSite;

      setDatesToUtcStart(newDocument);

      // For some reason, fileData never updates if browser auto fills.
      fileData.url = form.getFieldValue('url');
      fileData.base_url = form.getFieldValue('base_url') ?? newDocument.url;
      fileData.link_text = form.getFieldValue('link_text');
      delete newDocument.document_file;
      setIsLoading(true);

      try {
        const response = await addDoc({
          ...newDocument,
          ...fileData,
        });
        setIsLoading(false);
        if (refetch) {
          refetch();
        }
        if ('error' in response && response.error) {
          displayDuplicateError('Document exists on this site');
        } else {
          setOpen(false);
        }
      } catch (error: any) {
        setIsLoading(false);
        notification.error({
          message: error.data.detail,
          description: 'Upload a new document or enter a new location',
        });
      }
    } catch (error) {
      setIsLoading(false);
      message.error('We could not save this document');
      console.error(error);
    }
  }

  function onCancel() {
    setOpen(false);
  }

  // Doc exists on other site.
  // Since only location fields are editable, override other form values
  // with existing doc data.
  function setLocationValues(responseData: any) {
    if (responseData.prev_location_doc_id) {
      form.setFieldsValue({
        name: responseData.doc_name,
        document_type: responseData.document_type,
        lang_code: responseData.lang_code,
        effective_date: dateToMoment(responseData.effective_date),
        last_reviewed_date: dateToMoment(responseData.last_reviewed_date),
        last_updated_date: dateToMoment(responseData.last_updated_date),
        next_review_date: dateToMoment(responseData.next_review_date),
        next_update_date: dateToMoment(responseData.next_update_date),
        published_date: dateToMoment(responseData.published_date),
      });
      if (responseData.internal_document === true) {
        form.setFieldsValue({
          internal_document: responseData.internal_document,
        });
      }
      if (responseData.exists_on_this_site) {
        setExistsOnThisSite(true);
        displayDuplicateError('Document exists on this site');
      } else {
        setExistsOnThisSite(false);
        displayDuplicateError('Document exists on other site');
      }
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
        <div className="flex space-x-3">
          <UploadItem
            form={form}
            setFileData={setFileData}
            siteId={siteId}
            setLocationValues={setLocationValues}
          />
        </div>

        <div className="flex grow space-x-3">
          <Form.Item
            className="grow"
            style={{ width: '43%' }}
            name="name"
            label="Document Name"
            rules={[{ required: true }]}
          >
            <Input disabled={isEditingDocFromOtherSite ? true : false} />
          </Form.Item>
          <LanguageItem isEditingDocFromOtherSite={isEditingDocFromOtherSite} />
        </div>

        <div className="flex grow space-x-3">
          <DocumentTypeItem isEditingDocFromOtherSite={isEditingDocFromOtherSite} />
          <EffectiveDateItem isEditingDocFromOtherSite={isEditingDocFromOtherSite} />
          <InternalDocument
            oldVersion={oldVersion}
            isEditingDocFromOtherSite={isEditingDocFromOtherSite}
          />
        </div>

        <div className="flex grow space-x-3">
          <Form.Item label="Base Url" name="base_url" rules={[{ type: 'url' }]} className="grow">
            <AutoComplete onSearch={onBaseUrlSearch} options={baseUrlOptions} />
          </Form.Item>
        </div>
        <div className="flex grow space-x-3">
          <Form.Item className="grow" name="link_text" label="Link Text">
            <Input />
          </Form.Item>
        </div>
        <div className="flex grow space-x-3">
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
            <Button type="primary" disabled={isLoading} htmlType="submit">
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
  const { setFileData, siteId, setLocationValues } = props;
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
        setLocationValues(response.data);
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
        <Tooltip placement="top" title="Only upload .pdf, .xlsx and .docx">
          <QuestionCircleOutlined
            style={{ marginTop: '-26px', marginLeft: '105px', float: 'left' }}
          />
        </Tooltip>
        <Upload
          name="file"
          accept=".pdf,.xlsx,.docx,.xls,.doc"
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
      </Form.Item>
    </div>
  );
}

function InternalDocument(props: any) {
  const { oldVersion, isEditingDocFromOtherSite } = props;

  return (
    <>
      <Form.Item
        className="grow"
        style={{ width: '100%' }}
        valuePropName="checked"
        label="Internal"
        name="internal_document"
      >
        <Switch disabled={isEditingDocFromOtherSite || oldVersion ? true : false} />
      </Form.Item>
    </>
  );
}

function DocumentTypeItem(props: any) {
  const { isEditingDocFromOtherSite } = props;

  return (
    <Form.Item
      className="grow"
      style={{ width: '100%' }}
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

function EffectiveDateItem(props: any) {
  const { isEditingDocFromOtherSite } = props;

  return (
    <Form.Item
      className="grow"
      style={{ width: '100%' }}
      name="effective_date"
      label="Effective Date"
    >
      <DatePicker
        className="grow"
        style={{ width: '100%' }}
        mode="date"
        showTime={false}
        format={(value) => prettyDateFromISO(value.toISOString())}
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

function DateItems(props: any) {
  const { isEditingDocFromOtherSite } = props;

  let fields = [
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
                    className="grow"
                    style={{ width: '100%' }}
                    mode="date"
                    showTime={false}
                    format={(value) => prettyDateFromISO(value.toISOString())}
                    disabled={isEditingDocFromOtherSite ? true : false}
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
