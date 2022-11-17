import { WarningFilled } from '@ant-design/icons';
import { Button } from 'antd';

import { FormInstance } from 'antd/lib/form/Form';
import { useCallback, useState } from 'react';

import { Link } from 'react-router-dom';

export function PayerEditSubmitComponent({ form }: { form: FormInstance<any> }) {
  const [payerInfoError, setPayerInfoError] = useState<boolean>(false);

  const onSubmit = useCallback(async () => {
    let { payer_ids, channels, benefits, plan_types, regions } = form.getFieldsValue(true);
    if (
      !payer_ids.length &&
      !channels.length &&
      !benefits.length &&
      !plan_types.length &&
      !regions.length
    ) {
      setPayerInfoError(true);
      return;
    }

    form.submit();
  }, [form]);

  return (
    <div className="flex items-center space-x-4">
      {payerInfoError ? (
        <>
          <WarningFilled className="text-red-600" />
          <span className="text-red-600">At least one payer value is required</span>
        </>
      ) : null}

      <Link to="/payer-family">
        <Button htmlType="submit">Cancel</Button>
      </Link>

      <Button type="primary" onClick={onSubmit}>
        Submit
      </Button>
    </div>
  );
}
