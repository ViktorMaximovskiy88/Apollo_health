import { ModalProps, Modal } from 'antd';
import tw from 'twin.macro';

export function FullScreenModal({ children, ...props }: ModalProps) {
  return (
    <Modal
      width={'97vw'}
      className="p-0 ant-modal-full-screen"
      style={{ top: '3vh', height: '94vh' }}
      bodyStyle={tw`h-full overflow-auto`}
      {...props}
    >
      {children}
    </Modal>
  );
}
