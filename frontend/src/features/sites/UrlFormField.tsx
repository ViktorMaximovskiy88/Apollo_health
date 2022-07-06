import { Button, Form, Input, Select } from 'antd';
import {
  LinkOutlined,
  MinusCircleOutlined,
  PlusOutlined,
} from '@ant-design/icons';
import { Site } from './types';
import { FormInstance } from 'antd/lib/form/Form';
import { FormListFieldData } from 'antd/lib/form/FormList';
import { UrlInput } from './UrlInput';

interface LabelInputPropTypes {
  name: number;
  field: { fieldKey?: number };
}
function LabelInput({ name, field }: LabelInputPropTypes) {
  return (
    <Form.Item {...field} name={[name, 'name']} label="Label" className="mb-0">
      <Input />
    </Form.Item>
  );
}

interface StatusSelectPropTypes {
  name: number;
  field: { fieldKey?: number };
}
function StatusSelect({ name, field }: StatusSelectPropTypes) {
  return (
    <Form.Item
      {...field}
      name={[name, 'status']}
      label="Status"
      className="mb-0"
    >
      <Select
        options={[
          { value: 'ACTIVE', label: 'Active' },
          { value: 'INACTIVE', label: 'Inactive' },
        ]}
      />
    </Form.Item>
  );
}

interface LinkButtonPropTypes {
  form: FormInstance;
  index: number;
}
function LinkButton({ form, index }: LinkButtonPropTypes) {
  const hasError = (fieldName: string, fieldIndex: number): boolean => {
    const errors = form.getFieldsError();
    const fieldErrors = errors.filter(({ errors, name }) => {
      const [currentFieldName, currentFieldIndex] = name;
      if (!currentFieldName) return false;
      if (currentFieldName !== fieldName) return false;
      if (currentFieldIndex !== fieldIndex) return false;
      return errors.length > 0;
    });
    return fieldErrors.length > 0;
  };

  return (
    <Form.Item label=" " shouldUpdate className="mb-0">
      {() => (
        <Button
          className="p-0 focus:border focus:border-offset-2 focus:border-blue-500"
          href={form.getFieldValue('base_urls')[index].url}
          disabled={hasError('base_urls', index)}
          type="link"
          target="_blank"
          rel="noreferrer noopener"
        >
          <LinkOutlined className="text-gray-500 hover:text-blue-500 focus:text-blue-500" />
        </Button>
      )}
    </Form.Item>
  );
}

interface RemoveButtonPropTypes {
  fields: FormListFieldData[];
  remove: (index: number | number[]) => void;
  name: number;
}
function RemoveButton({ fields, remove, name }: RemoveButtonPropTypes) {
  if (fields.length < 2) {
    return null;
  }
  return (
    <Form.Item label=" " className="mb-0">
      <MinusCircleOutlined
        className="text-gray-500"
        onClick={() => remove(name)}
      />
    </Form.Item>
  );
}

interface UrlFormFieldPropTypes {
  initialValues?: Site;
  form: FormInstance;
}
export function UrlFormFields({ initialValues, form }: UrlFormFieldPropTypes) {
  return (
    <Form.List name="base_urls">
      {(fields, { add, remove }, { errors }) => (
        <>
          {fields.map(({ key, name, ...field }, index) => (
            <Form.Item key={key} className="mb-2" {...field}>
              <Input.Group className="space-x-2 flex">
                <UrlInput
                  initialValues={initialValues}
                  key={key}
                  name={name}
                  field={field}
                  form={form}
                />
                <LabelInput name={name} field={field} />
                <StatusSelect name={name} field={field} />
                <LinkButton form={form} index={index} />
                <RemoveButton fields={fields} remove={remove} name={name} />
              </Input.Group>
            </Form.Item>
          ))}
          <Form.Item>
            <Button
              type="dashed"
              onClick={() => add({ url: '', name: '', status: 'ACTIVE' })}
              icon={<PlusOutlined />}
            >
              Add URL
            </Button>
            <Form.ErrorList errors={errors} />
          </Form.Item>
        </>
      )}
    </Form.List>
  );
}
