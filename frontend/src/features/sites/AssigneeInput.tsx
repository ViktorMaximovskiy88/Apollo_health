import { Form, Input, AutoComplete } from 'antd';
import { FormInstance } from 'antd/lib/form/Form';
import { useState } from 'react';
import { useGetUsersQuery } from '../users/usersApi';

interface OptionType {
  label: string;
  value: string | null;
}

export function Assignee({ form }: { form: FormInstance }) {
  const { data: users } = useGetUsersQuery();

  const options: OptionType[] =
    users?.map((user) => ({ label: user.full_name, value: user._id })) ?? [];
  options.unshift({ label: 'Unassigned', value: null });

  const currentAssigneeId = form.getFieldValue('assignee');

  const initialAssigneeName = options.find((option) => currentAssigneeId === option.value);
  const [name, setName] = useState<string | null>(
    initialAssigneeName?.label === 'Unassigned' ? null : initialAssigneeName?.label ?? null
  );

  const [filteredOptions, setFilteredOptions] = useState<OptionType[]>(options);

  const onSearch = (searchText: string): void => {
    setFilteredOptions(
      searchText
        ? options.filter((option) =>
            option.label.toLowerCase().includes(searchText.toLocaleLowerCase())
          )
        : options
    );
  };
  const onSelect = (assigneeId: string, option: OptionType): void => {
    form.setFieldsValue({ assignee: assigneeId });
    const newAssigneeName = option.label === 'Unassigned' ? null : option.label;
    setName(newAssigneeName);
  };
  const onChange = (name: string) => {
    setName(name);
  };

  const validateStatus = (): '' | 'error' => {
    if (name === '') {
      return '';
    }
    const currentAssignee = users?.find((user) => user._id === currentAssigneeId);
    if (name === currentAssignee?.full_name) {
      return '';
    }
    return 'error';
  };

  return (
    <>
      <Form.Item label="Assignee" validateStatus={validateStatus()}>
        <AutoComplete // element only displays fullname of selected assignee
          placeholder="Unassigned"
          value={name}
          options={filteredOptions}
          onSelect={onSelect}
          onSearch={onSearch}
          onChange={onChange}
        />
      </Form.Item>
      <Form.Item // the element that actually saves the assignee user id
        hidden
        label="assignee id - should be hidden"
        name="assignee"
      >
        <Input />
      </Form.Item>
    </>
  );
}
