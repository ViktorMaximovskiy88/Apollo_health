import { Button, Form, Input, Modal, notification, Typography } from 'antd';
import { LinkOutlined } from '@ant-design/icons';
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { parseDiff, Diff, Hunk } from 'react-diff-view';
import 'react-diff-view/style/index.css';

import { isErrorWithData } from '../../common/helpers';
import { Hr } from '../../components';
import { useCreateDiffMutation, useGetDocDocumentQuery } from './docDocumentApi';
import { RetrievedDocument } from '../retrieved_documents/types';

function CompareModal(props: {
  diff?: string;
  newDoc?: RetrievedDocument;
  isModalVisible: boolean;
  handleCloseModal: (e: React.MouseEvent<HTMLElement, MouseEvent>) => void;
}) {
  const { Title } = Typography;

  const files = props.diff ? parseDiff(props.diff) : [];
  const renderFile = ({ type, hunks }: any) => (
    <Diff viewType="split" diffType={type} hunks={hunks}>
      {(hunks: any) =>
        hunks.map((hunk: any) => <Hunk key={hunk.content} hunk={hunk} className="diff-unified" />)
      }
    </Diff>
  );

  return (
    <Modal
      footer={null}
      width={1200}
      visible={props.isModalVisible}
      onCancel={props.handleCloseModal}
      destroyOnClose={true}
    >
      <Title className="text-center" level={3}>
        Comparison File
      </Title>
      <div className="flex justify-around">
        <div className="text-lg font-semibold">Current File</div>
        <Link
          className="text-lg font-semibold"
          to={`/sites/${props.newDoc?.site_id}/documents/${props.newDoc?._id}/edit`}
          target="_blank"
          rel="noopener"
        >
          New File <LinkOutlined />
        </Link>
      </div>
      <Hr />
      {files.map(renderFile)}
      {props.diff === '' && (
        <div className="text-center">The two files have identical text content.</div>
      )}
    </Modal>
  );
}

export function DocCompare() {
  const form = Form.useFormInstance();
  const docId = form.getFieldValue('docId');
  const { data: orgDoc } = useGetDocDocumentQuery(docId);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [compareId, setCompareId] = useState('');
  const [createDiff, { data: diffData, isLoading, isSuccess }] = useCreateDiffMutation();

  function handleCloseModal() {
    setIsModalVisible(false);
  }

  function handleInput(e: React.ChangeEvent<HTMLInputElement>) {
    setCompareId(e.target.value);
  }

  async function handleCompare() {
    try {
      if (compareId === '') {
        notification.error({
          message: 'Document ID Required',
          description: 'You must provide a Retrieved Document ID to generate a compare file',
        });
        return;
      }
      const compareInfo = { _id: orgDoc?._id ?? '', compareId: compareId };
      await createDiff(compareInfo).unwrap();
      setIsModalVisible(true);
    } catch (err) {
      if (isErrorWithData(err)) {
        notification.error({
          message: 'Error Creating Compare File',
          description: `${err.data.detail}`,
        });
      } else {
        notification.error({
          message: 'Error Creating Compare File',
          description: JSON.stringify(err),
        });
      }
    }
  }

  return (
    <div className="flex space-x-8 items-center">
      <Form.Item
        className="flex-1"
        label={'Compare File ID'}
        tooltip="ID of Retrieved Document to Compare"
      >
        <Input onChange={handleInput} />
      </Form.Item>
      <Button className="mt-1" loading={isLoading} onClick={handleCompare} type="primary">
        Compare
      </Button>
      {isSuccess && (
        <CompareModal
          isModalVisible={isModalVisible}
          diff={diffData?.diff}
          newDoc={diffData?.new_doc}
          handleCloseModal={handleCloseModal}
        />
      )}
    </div>
  );
}
