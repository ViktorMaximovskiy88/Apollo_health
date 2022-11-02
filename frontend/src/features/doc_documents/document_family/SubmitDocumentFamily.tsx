import { Button } from 'antd';
import { FormInstance } from 'antd/lib/form/Form';
import { Link } from 'react-router-dom';

export function SubmitDocumentFamily({ form }: { form: FormInstance<any> }) {
  return (
    <div className="flex items-center space-x-4">
      <Link to="/document-family">
        <Button htmlType="submit">Cancel</Button>
      </Link>
      <Button
        type="primary"
        onClick={() => {
          form.submit();
        }}
      >
        Submit
      </Button>
    </div>
  );
}
