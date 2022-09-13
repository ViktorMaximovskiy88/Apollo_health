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
  setVisible: (visible: boolean) => void;
  siteId: any;
}

export function AddDocumentModal({ oldVersion, setVisible, siteId }: AddDocumentModalPropTypes) {
  const [form] = useForm();
  const [addDoc] = useAddDocumentMutation();
  const [fileData, setFileData] = useState<any>();
  let initialValues: any = {
    lang_code: 'en',
  };
  if (oldVersion) {
    const { site_id, link_text, base_url, url } = oldVersion;
    initialValues = {
      lang_code: oldVersion.lang_code,
      name: oldVersion.name,
      document_type: oldVersion.document_type,
      locations: [{ site_id, link_text, base_url, url }],
    };
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
      newDocument.base_url = newDocument.base_url ?? newDocument.url;
      //  we nuked this relationship
      // if (scrapeTasks) {
      //   newDocument.scrape_task_id = scrapeTasks[0]._id;
      // }
      // used to determine how we handle this request if new_version or new document
      if (oldVersion) {
        newDocument._id = oldVersion._id;
        newDocument.last_collected_date = oldVersion.last_collected_date;
      }
      fileData.metadata.link_text = newDocument.link_text;
      delete newDocument.link_text;
      delete newDocument.document_file;

      await addDoc({
        ...newDocument,
        ...fileData,
      });
      setVisible(false);
    } catch (error) {
      message.error('We could not save this document');
    }
  }
  function onCancel() {
    setVisible(false);
  }
  return (
    <Modal visible={true} title="Add new document" onCancel={onCancel} width={1000} footer={null}>
      <Form
        layout="vertical"
        form={form}
        requiredMark={false}
        initialValues={initialValues}
        validateMessages={validateMessages}
        onFinish={saveDocument}
      >
        <UploadItem form={form} setFileData={setFileData} />
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
  const { setFileData } = props;
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
        setFileData(response.data);
      }
    }
  };

  return (
    <Form.Item
      name="document_file"
      label="Document File"
      rules={[{ required: uploadStatus === 'done' ? false : true }]}
    >
      <Upload
        name="file"
        accept=".pdf,.xlsx,.docx"
        action={`${baseApiUrl}/documents/upload`}
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
