import { useState } from "react";
import { Button, Modal, Form, Space, Input, Upload, DatePicker, Select, Tooltip, message } from 'antd';
import { useForm } from 'antd/lib/form/Form';
import type { UploadProps } from 'antd';
import type { UploadFile } from 'antd/es/upload/interface';
import { UploadOutlined, QuestionCircleOutlined } from '@ant-design/icons';
import { prettyDate } from '../../common';

interface AddDocumentModalPropTypes {
  visible: boolean;
  setVisible: (visible: boolean) => void;
  siteId: any;
}

export function AddDocumentModal({
    visible,
    setVisible,
    siteId,
}: AddDocumentModalPropTypes) {
    const [form] = useForm();
    const [fileList, setFileList] = useState<UploadFile>()
    const initialValues = {
        "language":"English"
    }
    function saveDocument(){




    }
    return (
        <Modal
          visible={visible}
          title="Add new document"
          onCancel={() => setVisible(false)}
          width={1000}
          footer={null}
        >
            <Form
                layout="vertical"
                form={form}
                requiredMark={false}
                initialValues={initialValues}
                onFinish={saveDocument}>
                <UploadItem fileList={fileList} setFileList={setFileList} />
                <div className="flex grow space-x-3">
                    <Form.Item className="grow" name="name" label="Document Name" rules={[{ required: true }]}>
                        <Input />
                    </Form.Item>
                    <DocumentTypeItem />
                    <LanguageItem />
                </div>
                <div className="flex grow space-x-3">
                    <Form.Item className="grow" name="link_text" label="Link Text" rules={[{ required: true }]}>
                        <Input />
                    </Form.Item>
                    <Form.Item className="grow" name="url" label="Link Url">
                        <Input />
                    </Form.Item>
                </div>
                <DateItems />
              <Form.Item>
                <Space>
                  <Button type="primary" htmlType="submit">
                    Save
                  </Button>
                    <Button onClick={() => setVisible(false)} htmlType="submit">Cancel</Button>
                </Space>
              </Form.Item>
            </Form>
        </Modal>
    );
}


function UploadItem(props: any) {
    const { fileList, setFileList } = props;

    const uploadProps: UploadProps = {
      name: 'file',
      accept:".pdf, .xlsx, .docx",
      multiple: false,
      maxCount:1,
      onChange(info) {
        if (info.file.status !== 'uploading') {
          console.log(info.file, info.fileList);
        }
        if (info.file.status === 'done') {
          message.success(`${info.file.name} file uploaded successfully`);
        } else if (info.file.status === 'error') {
          message.error(`${info.file.name} file upload failed.`);
        }
      },
      progress: {
        strokeColor: {
          '0%': '#108ee9',
          '100%': '#87d068',
        },
        strokeWidth: 3,
        format: percent => percent && `${parseFloat(percent.toFixed(2))}%`,
      },
    };

    return (
        <Form.Item name="files" label={
          <>
            <span style={{"marginRight":"5px"}}>Upload Document</span>
            <Tooltip placement="right" title="Only upload .pdf, .xlsx and .docx"><QuestionCircleOutlined /></Tooltip>
          </>
        } rules={[{ required: true }]}>
            <Upload {...uploadProps} fileList={fileList}>
                <Button icon={<UploadOutlined />}>Click to Upload</Button>
            </Upload>
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
    },{
        "name":"last_reviewed_date",
        "title":"Last Reviewed Date"
    },{
        "name":"last_updated_date",
        "title":"Last Updated Date"
    }],[{
        "name":"next_review_date",
        "title":"Next Review Date"
    },{
        "name":"next_update_date",
        "title":"Next Update Date"
    },{
        "name":"first_created_date",
        "title":"First Created Date"
    }],[{
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




















