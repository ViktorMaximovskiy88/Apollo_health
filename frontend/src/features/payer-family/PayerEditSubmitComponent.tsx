import { WarningFilled } from '@ant-design/icons';
import { Button } from 'antd';

import { FormInstance } from 'antd/lib/form/Form';
import { useCallback, useState } from 'react';

import { Link } from 'react-router-dom';
import { useLazyGetPayerBackboneByLIdQuery } from '../payer-backbone/payerBackboneApi';

export function PayerEditSubmitComponent({ form }: { form: FormInstance<any> }) {
  const [getPayerName] = useLazyGetPayerBackboneByLIdQuery();
  const [payerInfoError, setPayerInfoError] = useState<boolean>(false);

  const onSubmit = useCallback(async () => {
    let { payer_type, payer_ids, channels, benefits, plan_types, regions } =
      form.getFieldsValue(true);
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

    if (form.getFieldValue('auto_generated')) {
      let getPayerNameVals = async () => {
        const payers: any = [];
        for (let i = 0; i < payer_ids.length; i++) {
          const { data } = await getPayerName({ payerType: payer_type, id: payer_ids[i] });
          payers.push(data?.name);
        }
        return payers;
      };
      let payerNames;
      if (payer_ids && payer_ids[0] !== '') {
        payerNames = await getPayerNameVals();
      }
      const newName = [regions, plan_types, benefits, channels, payerNames]
        .filter((vals: any) => (!vals || vals.length === 0 ? false : true))
        .join(' | ');
      form.setFieldsValue({ name: newName });
    }
    form.submit();
  }, [form, getPayerName]);

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
