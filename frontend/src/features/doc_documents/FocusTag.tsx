import { Form, notification, Switch, Tag } from 'antd';
import { DocumentTag } from './types';
import { focusDocumentTypes } from './useOnFinish';

export function ReadFocusTag({ tag }: { tag: DocumentTag }) {
  const documentType = Form.useWatch('document_type');

  return (
    <>
      {focusDocumentTypes.includes(documentType) || tag.focus ? (
        <Tag color="gold" className="select-none cursor-default">
          Focus
        </Tag>
      ) : null}
    </>
  );
}

export function EditFocusTag({
  tag,
  onEditTag,
}: {
  tag: DocumentTag;
  onEditTag: (id: string, field: string, value: any) => void;
}) {
  const documentType = Form.useWatch('document_type');

  return (
    <>
      {focusDocumentTypes.includes(documentType) ? (
        <Switch
          checked={true}
          id="focus"
          checkedChildren="Focus"
          onClick={() =>
            notification.warning({
              message: 'Cannot Change Focus',
              description: `Cannot change focus while document type is ${documentType}`,
              placement: 'topRight',
            })
          }
        />
      ) : (
        <Switch
          defaultChecked={tag.focus}
          id="focus"
          onChange={(checked) => onEditTag(tag.id, 'focus', checked)}
          checkedChildren="Focus"
          unCheckedChildren="Focus"
        />
      )}
    </>
  );
}
