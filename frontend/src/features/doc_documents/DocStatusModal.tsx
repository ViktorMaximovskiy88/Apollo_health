import { Form, List, Modal, Select, Steps } from 'antd';
import { useState } from 'react';
import { prettyDateUTCFromISO } from '../../common';
import { ApprovalStatus, statusOptions } from '../../common/approvalStatus';
import { ButtonLink } from '../../components';
import { DocDocument } from './types';

function toStepStatus(status: ApprovalStatus) {
  if (status === ApprovalStatus.Approved) {
    return 'finish';
  }
  if (status === ApprovalStatus.Queued) {
    return 'process';
  }
  return 'wait';
}

function displayItem(item: string) {
  switch (item) {
    case 'IDENTIFIED_DATES':
      return 'Large Number of Dates Identified';
    case 'DOC_TYPE':
      return 'Low Document Type Confidence or Deviates from Previous Version';
    case 'EFFECTIVE_DATE':
      return 'Effective Date Far in the Future or Past';
    case 'TAGS':
      return 'Therapy/Indication Tags Deviate from Previous Version';
    case 'LINEAGE':
      return 'No Previous Version Specified';
    case 'DOC_FAMILY':
      return 'Document Family Not Set';
    case 'PAYER_FAMILY':
      return 'Not Every Location has a Payer Family';
    case 'NO_TRANSLATION':
      return 'Translation Configuration Not Set';
    case 'EXTRACT_DELTA':
      return 'Large Number of Extraction Changes Compared to Previous Version';
    default:
      return item;
  }
}

function renderHoldItem(item: string) {
  return <List.Item key={item}>{displayItem(item)}</List.Item>;
}

function holdInfo(holdInfo?: string[]) {
  if (holdInfo && holdInfo.length > 0) {
    return <List dataSource={holdInfo} renderItem={renderHoldItem} />;
  }
  return undefined;
}

function statusSelect(name: string) {
  return (
    <Form.Item name={name} noStyle>
      <Select className="w-36" options={statusOptions} />
    </Form.Item>
  );
}

export function DocStatusModal({ doc }: { doc: DocDocument }) {
  const [isOpen, setOpen] = useState(false);
  return (
    <>
      <ButtonLink onClick={() => setOpen(true)}>Status</ButtonLink>
      <Modal open={isOpen} onCancel={() => setOpen(false)} onOk={() => setOpen(false)}>
        <Steps direction="vertical" size="small">
          <Steps.Step
            title="Collection"
            subTitle={prettyDateUTCFromISO(doc.first_collected_date)}
            status="finish"
            description=""
          />
          <Steps.Step
            title={<span className="align-top">Classification</span>}
            subTitle={statusSelect('classification_status')}
            status={toStepStatus(doc.classification_status)}
            description={holdInfo(doc.classification_hold_info)}
          />
          <Steps.Step
            title={<span className="align-top">Doc & Payer Family</span>}
            subTitle={statusSelect('family_status')}
            status={toStepStatus(doc.family_status)}
            description={holdInfo(doc.family_hold_info)}
          />
          <Steps.Step
            title={<span className="align-top">Translation & Extraction</span>}
            subTitle={statusSelect('content_extraction_status')}
            status={toStepStatus(doc.content_extraction_status)}
            description={holdInfo(doc.extraction_hold_info)}
          />
          <Steps.Step title="Approval" status={toStepStatus(doc.status)} />
        </Steps>
      </Modal>
    </>
  );
}
