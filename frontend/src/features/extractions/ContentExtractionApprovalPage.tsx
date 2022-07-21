import { Form, FormInstance } from 'antd';
import { useGetDocDocumentQuery } from '../doc_documents/docDocumentApi';

export function ContentExtractionApprovalPage(props: {
  docId: string;
  form: FormInstance;
  onSubmit: (u: any) => void;
}) {
  const { data: doc } = useGetDocDocumentQuery(props.docId);
  if (!doc) return null;

  return (
    <>
      <div>Content Extraction - {doc.name}</div>
      <Form form={props.form} onFinish={props.onSubmit}></Form>
    </>
  );
}
