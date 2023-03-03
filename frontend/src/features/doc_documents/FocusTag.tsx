import { Switch, Tag } from 'antd';
import { DocumentTag } from './types';

export function ReadFocusTag({ tag }: { tag: DocumentTag }) {
  return (
    <>
      {tag.focus ? (
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
  return (
    <>
      <Switch
        defaultChecked={tag.focus}
        id="focus"
        onChange={(checked) => onEditTag(tag.id, 'focus', checked)}
        checkedChildren="Focus"
        unCheckedChildren="Focus"
      />
    </>
  );
}
