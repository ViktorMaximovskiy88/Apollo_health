import { useState, useEffect } from "react";
import { Button, Modal, Form, Space, Input, Upload, DatePicker, Select, Tooltip, message } from 'antd';
import { useForm } from 'antd/lib/form/Form';
import { UploadChangeParam } from 'antd/lib/upload';
import { UploadFile } from 'antd/lib/upload/interface';

import { UploadOutlined, QuestionCircleOutlined, LoadingOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { prettyDate } from '../../common';
import { useAddDocumentMutation } from "../retrieved_documents/documentsApi"
import { baseApiUrl, client, fetchWithAuth } from '../../app/base-api';

interface AddDocumentModalPropTypes {
  setVisible: (visible: boolean) => void;
  siteId: any;
}

export function AddDocumentModal({
    setVisible,
    siteId,
}: AddDocumentModalPropTypes) {
    const [form] = useForm();
    const initialValues = {
        "lang_code":"English"
    }
    const validateMessages = {
        required: '${label} is required!',
        types: {
          url: '${label} is not a valid url!',
        },
    };
    function saveDocument(){
        

        



    }
    function onCancel(){
        setVisible(false);
    }
    return (
        <Modal
          visible={true}
          title="Add new document"
          onCancel={onCancel}
          width={1000}
          footer={null}
        >
            <Form
                layout="vertical"
                form={form}
                requiredMark={false}
                initialValues={initialValues}
                validateMessages={validateMessages}
                onFinish={saveDocument}>
                <UploadItem />
                <div className="flex grow space-x-3">
                    <Form.Item className="grow" name="name" label="Document Name" rules={[{ required: true }]}>
                        <Input />
                    </Form.Item>
                    <DocumentTypeItem />
                    <LanguageItem />
                </div>
                <div className="flex grow space-x-3">
                    <Form.Item className="grow" name="link_text" label="Link Text">
                        <Input />
                    </Form.Item>
                    <Form.Item className="grow" name="url" label="Link Url">
                        <Input type="url" />
                    </Form.Item>
                </div>
                <DateItems />
              <Form.Item>
                <Space>
                  <Button type="primary" htmlType="submit">
                    Save
                  </Button>
                  <Button onClick={onCancel} htmlType="submit">Cancel</Button>
                </Space>
              </Form.Item>
            </Form>
        </Modal>
    );
}


function UploadItem(props: any) {
    const [ addDoc ] = useAddDocumentMutation();
    const [token, setToken] = useState('');
    const [fileName, setFileName] = useState('');
    const [uploadStatus, setUploadStatus] = useState('');

    useEffect(() => {
        client.getTokenSilently().then((t) => setToken(t));
    }, [setToken]);

    const onChange = (info: UploadChangeParam<UploadFile<unknown>>) => {
        setFileName(info.file.name);
        if (info.file.status === 'uploading') {
          setUploadStatus("uploading");
        }
        if (info.file.status === 'done') {
          setUploadStatus("done");
        }
    };

    return (
        <Form.Item name="document_file" label="Document File" rules={[{ required: true }]}>
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
                {
                    uploadStatus == "uploading" ? 
                    <Button style={{marginRight:"10px"}} icon={<LoadingOutlined />}>Uploading {fileName}...</Button>
                    : 
                    uploadStatus == "done" ?
                    <Button style={{marginRight:"10px"}} icon={<CheckCircleOutlined />}>{fileName} uploaded!</Button>
                    :
                    <Button style={{marginRight:"10px"}} icon={<UploadOutlined />}>Click to Upload</Button>
                }
            </Upload>
            <Tooltip placement="right" title="Only upload .pdf, .xlsx and .docx"><QuestionCircleOutlined /></Tooltip>
        </Form.Item>
    )
}

function DocumentTypeItem(){
    const documentTypes = [
      { value: 'Authorization Policy', label: 'Authorization Policy' },
      { value: 'Provider Guide', label: 'Provider Guide' },
      { value: 'Treatment Request Form', label: 'Treatment Request Form' },
      { value: 'Payer Unlisted Policy', label: 'Payer Unlisted Policy' },
      { value: 'Covered Treatment List', label: 'Covered Treatment List' },
      { value: 'Regulatory Document', label: 'Regulatory Document' },
      { value: 'Formulary', label: 'Formulary' },
      { value: 'Internal Reference', label: 'Internal Reference' },
    ];
    return (
        <Form.Item className="grow" name="document_type" label="Document Type" rules={[{ required: true }]}>
            <Select options={documentTypes} />
        </Form.Item>
    )
}

function LanguageItem(){
    const languageCodes = [
        { value: 'en', label: 'English' },
        { value: 'es', label: 'Spanish' },
        { value: 'other', label: 'Other' },
    ];
    return (
        <Form.Item className="grow" name="lang_code" label="Language" rules={[{ required: true }]}>
            <Select options={languageCodes} />
        </Form.Item>
    )
}

function DateItems(props: any) {
    let fields = [[{
        "name":"effective_date",
        "title":"Effective Date"
    }],[{
        "name":"last_reviewed_date",
        "title":"Last Reviewed Date"
    },{
        "name":"last_updated_date",
        "title":"Last Updated Date"
    },{
        "name":"next_review_date",
        "title":"Next Review Date"
    }],[{
        "name":"next_update_date",
        "title":"Next Update Date"
    },{
        "name":"first_created_date",
        "title":"First Created Date"
    },{
        "name":"published_date",
        "title":"Published Date"
    }]]
    return (
        <>
            {
                fields.map((section,i) => {
                    return (
                        <div key={i} className="flex grow space-x-3">
                            {
                                section.map(field => {
                                    return (
                                        <Form.Item 
                                            key={field.name} 
                                            name={field.name} 
                                            className="grow"
                                            label={field.title}>
                                            <DatePicker 
                                                style={{width:"100%"}}
                                                format={(value) => prettyDate(value.toDate())} 
                                                />
                                        </Form.Item>
                                    )
                                })
                            }
                        </div>      
                    )
                })
            }
        </>
    )
}



















