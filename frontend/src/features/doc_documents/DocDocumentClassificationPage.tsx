import { Form, FormInstance } from 'antd';
import { useGetDocDocumentQuery } from './docDocumentApi';

export function DocDocumentClassificationPage(props: {
  docId: string;
  form: FormInstance;
  onSubmit: (u: any) => void;
}) {
  const { data: doc } = useGetDocDocumentQuery(props.docId);
  if (!doc) return null;

  return (
    <>
      <div> Document Classification - {doc.name} </div>
      <Form form={props.form} onFinish={props.onSubmit}></Form>
    </>
  );
}
