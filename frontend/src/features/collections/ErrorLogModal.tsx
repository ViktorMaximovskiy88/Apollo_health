import { Button, Modal } from 'antd';

interface ErrorLogModalPropTypes {
  open: boolean;
  setOpen: (open: boolean) => void;
  errorTraceback: string;
}

export function ErrorLogModal({ open, setOpen, errorTraceback }: ErrorLogModalPropTypes) {
  return (
    <Modal
      open={open}
      title="Error Traceback"
      onCancel={() => setOpen(false)}
      width={1000}
      footer={[
        <Button className="px-10" type="primary" key="back" onClick={() => setOpen(false)}>
          Ok
        </Button>,
      ]}
    >
      <pre>{errorTraceback}</pre>
    </Modal>
  );
}
