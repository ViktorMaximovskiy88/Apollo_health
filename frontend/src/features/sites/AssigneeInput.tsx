import { Form, Input, AutoComplete } from 'antd';
import { FormInstance } from 'antd/lib/form/Form';
import { useEffect, useMemo, useState } from 'react';
import { User } from '../users/types';
import { useGetUsersQuery } from '../users/usersApi';

interface OptionType {
  label: string;
  value: string | null;
}
const useOptions = (users?: User[]): OptionType[] => {
  return useMemo(() => {
    const options: OptionType[] =
      users?.map((user: User) => ({ label: user.full_name, value: user._id })) ?? [];
    options.unshift({ label: 'Unassigned', value: null });
    return options;
  }, [users]);
};
const useNameState = (
  options: OptionType[],
  currentAssigneeId: string
): [string | null, (name: string | null) => void] => {
  const initialAssigneeName = options.find((option) => currentAssigneeId === option.value);
  const [name, setName] = useState<string | null>(
    initialAssigneeName?.label === 'Unassigned' ? null : initialAssigneeName?.label ?? null
  );
  return [name, setName];
};
interface KeepFieldsInSyncTypes {
  currentAssigneeId: string;
  options: OptionType[];
  setName: (name: string | null) => void;
}
const useKeepFieldsInSync = ({ options, currentAssigneeId, setName }: KeepFieldsInSyncTypes) => {
  useEffect(() => {
    const option = options.find((option: OptionType) => option.value === currentAssigneeId);
    const newAssigneeName = option?.label === 'Unassigned' ? null : option?.label;
    setName(newAssigneeName ?? null);
  }, [currentAssigneeId, options, setName]);
};
const filterOptions = (searchText: string, options: OptionType[]): OptionType[] => {
  let newFilteredOptions = options;
  if (searchText) {
    newFilteredOptions = options.filter((option) =>
      option.label.toLowerCase().includes(searchText.toLowerCase())
    );
  }
  return newFilteredOptions;
};

export function Assignee(props: { form: FormInstance }) {
  const { data: users } = useGetUsersQuery();

  const options: OptionType[] = useOptions(users);

  const currentAssigneeId = props.form.getFieldValue('assignee');

  const [name, setName] = useNameState(options, currentAssigneeId);
  const [filteredOptions, setFilteredOptions] = useState<OptionType[]>(options);

  useKeepFieldsInSync({ options, currentAssigneeId, setName });

  const onSearch = (searchText: string): void => {
    const newFilteredOptions = filterOptions(searchText, options);
    setFilteredOptions(newFilteredOptions);
  };
  const onSelect = (assigneeId: string, option: OptionType): void => {
    props.form.setFieldsValue({ assignee: assigneeId });
    const newAssigneeName = option.label === 'Unassigned' ? null : option.label;
    setName(newAssigneeName);
  };
  const onChange = (name: string) => {
    setName(name);
  };

  const validateStatus = (): '' | 'error' => {
    if (!name) {
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
        <AutoComplete // element only displays full_name of selected assignee
          placeholder="Unassigned"
          value={name}
          options={filteredOptions}
          onSelect={onSelect}
          onSearch={onSearch}
          onChange={onChange}
        />
      </Form.Item>
      <Form.Item // element that actually saves the assignee user id
        hidden
        label="assignee id - should be hidden"
        name="assignee"
      >
        <Input />
      </Form.Item>
    </>
  );
}
