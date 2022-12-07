import { WarningFilled } from '@ant-design/icons';
import { Button } from 'antd';

import { FormInstance } from 'antd/lib/form/Form';
import { useCallback, useState } from 'react';

import { Link } from 'react-router-dom';
import { useLazyConvertPayerFamilyDataQuery } from './payerFamilyApi';

export function PayerEditSubmitComponent({ form }: { form: FormInstance<any> }) {
  const [payerInfoError, setPayerInfoError] = useState<string>('');
  const [convertPayerFamily] = useLazyConvertPayerFamilyDataQuery();

  const onSubmit = useCallback(async () => {
    const { name, payer_type, payer_ids, channels, benefits, plan_types, regions } =
      form.getFieldsValue(true);
    if (
      !payer_ids.length &&
      !channels.length &&
      !benefits.length &&
      !plan_types.length &&
      !regions.length
    ) {
      setPayerInfoError(
        'You must specify at least one Backbone Value, Channel, Benefit, Plan Type or Region'
      );
      return;
    }
    try {
      await convertPayerFamily({
        payerType: 'plan',
        body: {
          name,
          payer_type,
          payer_ids,
          channels,
          benefits,
          plan_types,
          regions,
        },
      }).unwrap();
      setPayerInfoError('');
    } catch (err: any) {
      setPayerInfoError(err.data.detail);
      return;
    }

    form.submit();
  }, [form, setPayerInfoError, convertPayerFamily]);

  return (
    <div className="flex items-center space-x-4">
      {payerInfoError ? (
        <>
          <WarningFilled className="text-red-600" />
          <span className="text-red-600">{payerInfoError}</span>
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
