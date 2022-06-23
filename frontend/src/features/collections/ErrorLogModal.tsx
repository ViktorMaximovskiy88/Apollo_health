import { Button, Modal } from 'antd';

interface ErrorLogModalPropTypes {
  visible: boolean;
  setVisible: (visible: boolean) => void;
  errorTraceback: string;
}

export function ErrorLogModal({
  visible,
  setVisible,
  errorTraceback,
}: ErrorLogModalPropTypes) {
  return (
    <Modal
      visible={visible}
      title="Error Traceback"
      onCancel={() => setVisible(false)}
      width={1000}
      footer={[
        <Button
          className="px-10"
          type="primary"
          key="back"
          onClick={() => setVisible(false)}
        >
          Ok
        </Button>,
      ]}
    >
      <pre>{errorTraceback}</pre>
    </Modal>
  );
}
