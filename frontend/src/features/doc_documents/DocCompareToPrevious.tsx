import { Button, Form, Modal, notification, Tooltip, Typography } from 'antd';
import { LinkOutlined } from '@ant-design/icons';
import { useCallback, useState } from 'react';
import { Link } from 'react-router-dom';
import { parseDiff, Diff, Hunk } from 'react-diff-view';
import 'react-diff-view/style/index.css';

import { isErrorWithData } from '../../common/helpers';
import { Hr } from '../../components';
import { useCreateDiffWithPreviousMutation, useGetDocDocumentQuery } from './docDocumentApi';

function CompareModal(props: {
  diff?: string;
  previousDocDocId: string;
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

  if (!props.diff || !props.previousDocDocId) return null;

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
        <Link
          className="text-lg font-semibold"
          to={`/documents/${props.previousDocDocId}`}
          target="_blank"
          rel="noopener"
        >
          Previous Document
          <LinkOutlined />
        </Link>
        <div className="text-lg font-semibold">Current Document</div>
      </div>
      <Hr />
      {files.map(renderFile)}
      {props.diff === '' && (
        <div className="text-center">The two files have identical text content.</div>
      )}
    </Modal>
  );
}

export function DocCompareToPrevious() {
  const form = Form.useFormInstance();
  const currentDocDocId = form.getFieldValue('docId');
  const { data: currentDocument } = useGetDocDocumentQuery(currentDocDocId);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [createDiffWithPrevious, { data: diffData, isLoading, isSuccess }] =
    useCreateDiffWithPreviousMutation();

  const { previous_doc_doc_id: previousDocDocId } = currentDocument ?? {};

  function handleCloseModal() {
    setIsModalVisible(false);
  }

  const handleCompare = useCallback(async () => {
    try {
      await createDiffWithPrevious(currentDocDocId).unwrap();
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
  }, [createDiffWithPrevious, currentDocDocId]);

  return (
    <div className="flex space-x-8 items-center">
      {previousDocDocId ? (
        <Button className="mt-1" loading={isLoading} onClick={handleCompare} type="primary">
          Compare To Previous
        </Button>
      ) : (
        <Tooltip title={'Previous document ID not found. Comparison is not possible'}>
          <Button className="mt-1" type="primary" disabled={true}>
            Compare To Previous
          </Button>
        </Tooltip>
      )}
      {isSuccess && (
        <CompareModal
          isModalVisible={isModalVisible}
          diff={diffData?.diff}
          previousDocDocId={previousDocDocId ?? ''}
          handleCloseModal={handleCloseModal}
        />
      )}
    </div>
  );
}
