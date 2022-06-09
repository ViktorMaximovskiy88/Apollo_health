import { Button, Form, Select, Space, Switch } from 'antd';
import { Input } from 'antd';
import { useForm } from 'antd/lib/form/Form';
import { format, parse, parseISO } from 'date-fns';
import React, { useEffect, useState }  from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useUpdateDocumentAssessmentMutation } from './assessmentsApi';
import { DocumentAssessment } from './types';
import { NestedPartial } from '../types';
import { RetrievedDocument } from '../documents/types';
import { SubmitAction, WorkQueue } from '../work_queue/types';

export function AssessmentForm(props: {readonly: boolean | undefined, assessment: DocumentAssessment, document: RetrievedDocument, workQueue: WorkQueue }) {
  const navigate = useNavigate();
  const params = useParams();
  const [updateDoc] = useUpdateDocumentAssessmentMutation();
  const [form] = useForm();
  const [action, setAction] = useState<SubmitAction | undefined>();
  const assessment = props.assessment;
  const triage = assessment.triage;

  function onCancel(e: React.SyntheticEvent) {
    e.preventDefault();
    navigate(-1);
  }
  
  useEffect(() => {
    if (action) form.submit();
  }, [action])

  async function onFinish(assessmentUpdate: NestedPartial<DocumentAssessment>) {
    assessmentUpdate.triage = {
      ...assessmentUpdate.triage,
      effective_date: parse(
        assessmentUpdate.triage?.effective_date || '',
        'yyyy-MM-dd',
        0
      ).toISOString(),
    }

    const submitAction = action?.submit_action
    const newAssessment = {
      ...assessment,
      ...assessmentUpdate,
      ...submitAction,
    }

    await updateDoc(newAssessment);
    navigate(-1);
  }

  const initialValues = {
    name: assessment.name,
    triage: {
      effective_date: triage.effective_date
        ? format(parseISO(triage.effective_date), 'yyyy-MM-dd')
        : null,
      document_type: triage.document_type,
    }
  };

  const documentTypes = [
    { value: 'Authorization Policy', label: 'Authorization Policy' },
    { value: 'Provider Guide', label: 'Provider Guide' },
    { value: 'Treatment Request Form', label: 'Treatment Request Form' },
    { value: 'Payer Unlisted Policy', label: 'Payer Unlisted Policy' },
    { value: 'Covered Treatment List', label: 'Covered Treatment List' },
    { value: 'Regulatory Document', label: 'Regulatory Document' },
    { value: 'Formulary', label: 'Formulary' },
    { value: 'Internal Reference', label: 'Internal Reference' },
  ]

  const extractionOptions = [
    { value: 'BasicTableExtraction', label: 'Basic Table Extraction' },
    { value: 'UHCFormularyExtraction', label: 'UHC Formulary Extraction' },
  ];

  const identified_dates: string[] = props.document.identified_dates || [];

  const dateOptions =
    identified_dates.map((d) => {
      const date = format(parseISO(d), 'yyyy-MM-dd');
      return { value: date, label: date };
    }) || [];
  const today = format(new Date(), 'yyyy-MM-dd');
  dateOptions.push({value: today, label: today });

  return (
    <Form
      layout="vertical"
      form={form}
      requiredMark={false}
      initialValues={initialValues}
      onFinish={onFinish}
    >
      <Form.Item name="name" label="Name">
        <Input />
      </Form.Item>
      <Form.Item name={['triage', "document_type"]} label="Document Type">
        <Select options={documentTypes} />
      </Form.Item>
      <Form.Item name={['triage', "effective_date"]} label="Effective Date">
        <Select options={dateOptions} />
      </Form.Item>
      <Form.Item>
        <Space>
          {!props.readonly && props.workQueue.submit_actions.map((action) => {
            return (
              <Button
                key={action.label}
                type={action.primary ? 'primary' : 'default'}
                onClick={() => setAction(action)}
              >
                {action.label}
              </Button>
            )
          })}
          <Button htmlType="submit" onClick={onCancel}>
            Cancel
          </Button>
        </Space>
      </Form.Item>
    </Form>
  );
}
