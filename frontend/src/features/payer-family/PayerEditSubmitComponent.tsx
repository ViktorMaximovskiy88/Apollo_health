import { Button } from 'antd';

import { FormInstance } from 'antd/lib/form/Form';

import { Link } from 'react-router-dom';
import { useLazyGetPayerBackboneByLIdQuery } from '../payer-backbone/payerBackboneApi';

export function PayerEditSubmitComponent({ form }: { form: FormInstance<any> }) {
  const [getPayerName] = useLazyGetPayerBackboneByLIdQuery();

  const handleSubmit = async () => {
    let { payer_type, payer_ids, channels, benefits, plan_types, regions } =
      form.getFieldsValue(true);
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
    form.submit();
  };

  return (
    <div className="flex items-center space-x-4">
      <Link to="/payer-family">
        <Button htmlType="submit">Cancel</Button>
      </Link>

      <Button type="primary" onClick={handleSubmit}>
        Submit
      </Button>
    </div>
  );
}
