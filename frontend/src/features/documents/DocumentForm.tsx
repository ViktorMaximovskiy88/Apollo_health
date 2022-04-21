import { Button, Form, Select, Space } from "antd";
import { Input } from "antd";
import { useForm } from "antd/lib/form/Form";
import { format, parse, parseISO } from "date-fns";
import {useNavigate, useParams} from 'react-router-dom';
import { useGetDocumentQuery, useUpdateDocumentMutation } from "./documentsApi";
import { RetrievedDocument } from "./types";

export function DocumentForm() {
    const navigate = useNavigate();
    const params = useParams();
    const [updateDoc] = useUpdateDocumentMutation();
    const { data: doc } = useGetDocumentQuery(params.docId, { skip: !params.docId })
    const [form] = useForm();
    async function onFinish(doc: Partial<RetrievedDocument>) {
        await updateDoc({
            ...doc,
            effective_date: parse(doc.effective_date || '', 'yyyy-MM-dd', 0).toISOString(),
            _id: params.docId,
        });
        navigate(-1);
    } 

    if (!doc) return null;

    const initialValues = {
        name: doc.name,
        effective_date: doc.effective_date ? format(parseISO(doc.effective_date), 'yyyy-MM-dd') : null,
        document_type: doc.document_type,
        url: doc.url,
    }
    
    const documentTypes = [
        { value: 'PA', label: 'Prior Authorization' },
        { value: 'ST', label: 'Step Therapy' },
        { value: 'Formulary', label: 'Formulary' },
    ]

    const dateOptions = doc.identified_dates?.map((d) => {
        const date = format(parseISO(d), 'yyyy-MM-dd')
        return { value: date, label: date }
    }) || []

    return <Form
        layout="vertical"
        form={form}
        requiredMark={false}
        initialValues={initialValues}
        onFinish={onFinish}
    >
    <Form.Item name="name" label="Name">
        <Input />
    </Form.Item>
    <Form.Item name="document_type" label="Document Type">
        <Select options={documentTypes}/>
    </Form.Item>
    <Form.Item name="effective_date" label="Effective Date">
        <Select options={dateOptions}/>
    </Form.Item>
    <Form.Item name="url" label="URL">
        <Input disabled/>
    </Form.Item>
      <Form.Item>
        <Space>
          <Button type="primary" htmlType="submit">
            Submit
          </Button>
          <Button htmlType="submit" onClick={(e) => { navigate(-1); e.preventDefault()}}>Cancel</Button>
        </Space>
      </Form.Item>
    </Form>
}