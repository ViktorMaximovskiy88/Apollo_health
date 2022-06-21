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
  const handleOk = () => {
    setVisible(false);
  };

  return (
    <Modal
      visible={visible}
      title="Error Traceback"
      onOk={handleOk}
      onCancel={handleOk}
      footer={[
        <Button className="px-10" type="primary" key="back" onClick={handleOk}>
          Ok
        </Button>,
      ]}
    >
      <pre>{errorTraceback}</pre>
    </Modal>
  );
}
