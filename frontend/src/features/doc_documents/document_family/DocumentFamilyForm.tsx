import { Form, FormInstance, Input, Spin } from 'antd';
import { useGetSiteQuery } from '../../sites/sitesApi';
import { useParams } from 'react-router-dom';
import { useGetDocDocumentQuery } from '..//docDocumentApi';
import { ReactNode } from 'react';
import { DocumentFamilyType } from '../types';
import { useLazyGetDocumentFamilyByNameQuery } from './documentFamilyApi';
import { Rule } from 'antd/lib/form';

// export const Name = () => {
//   const [getDocumentFamilyByName] = useLazyGetDocumentFamilyByNameQuery();
//   const { docDocumentId: docId } = useParams();
//   const { data: doc } = useGetDocDocumentQuery(docId);
//   const siteId = doc?.site_id;

//   const mustBeUniqueToSite = () => ({
//     async validator(_: Rule, name: string) {
//       if (!name) return;
//       if (!siteId) return Promise.reject(new Error(`Site ID not found. Please try again.`));
//       const { data: documentFamily } = await getDocumentFamilyByName({ name, siteId });
//       if (documentFamily) {
//         return Promise.reject(
//           new Error(`Document Family Name "${documentFamily.name}" already exists on this site!`)
//         );
//       }
//       return Promise.resolve();
//     },
//   });

//   return (
//     <div className="flex space-x-8">
//       <Form.Item
//         name="name"
//         label="Document Family Name"
//         className="flex-1"
//         rules={[
//           mustBeUniqueToSite,
//           { required: true, message: 'Please input a Document Family Name!' },
//         ]}
//         required
//       >
//         <Input />
//       </Form.Item>
//     </div>
//   );
// };

// const ReadonlyDocumentType = () => {
//   const form = Form.useFormInstance();
//   const documentType = form.getFieldValue('document_type');
//   return (
//     <Form.Item label="Document Type" className="flex-1">
//       <b>{documentType}</b>
//     </Form.Item>
//   );
// };
// const DocumentTypePicker = () => null; // TODO

// const ReadonlySite = () => {
//   const { docDocumentId: docId } = useParams();
//   const { data: doc } = useGetDocDocumentQuery(docId);
//   const { data: site } = useGetSiteQuery(doc?.site_id);

//   return (
//     <Form.Item label="Site Name" className="flex-1">
//       {site?.name ? <b>{site.name}</b> : <Spin size="small" />}
//     </Form.Item>
//   );
// };
// const SitePicker = () => null; // TODO

interface AddDocumentFamilyPropTypes {
  initialValues: Partial<DocumentFamilyType>;
  onFinish: (documentFamily: DocumentFamilyType) => Promise<void>;
  form: FormInstance;
  isSaving: boolean;
  lockSiteDocType: boolean;
  children: ReactNode;
}
export function AddDocumentFamily({
  initialValues,
  onFinish,
  form,
  isSaving,
  lockSiteDocType,
  children,
}: AddDocumentFamilyPropTypes) {
  return (
    <Form
      initialValues={initialValues}
      onFinish={onFinish}
      form={form}
      disabled={isSaving}
      name="add-document-family"
      layout="vertical"
      className="h-full"
      autoComplete="off"
      validateTrigger={['onBlur']}
    >
      {/* <Name />
      <div className="flex space-x-8">
        {lockSiteDocType ? <ReadonlyDocumentType /> : <DocumentTypePicker />}
        {lockSiteDocType ? <ReadonlySite /> : <SitePicker />}
      </div> */}
      {children}
    </Form>
  );
}
