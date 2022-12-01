import React from 'react';
import { RemoteSelect } from './RemoteSelect';

type TypeFilterValue = {
  name: string;
  operator: string;
  type: string;
  value: string | null;
};

type FilterProps = {
  filterValue?: TypeFilterValue;
  filterEditorProps?: any;
  disabled?: boolean;
  onChange?: Function;
  render?: Function;
  placeholder?: string;
};

type FilterState = {
  value?: string | string[] | null;
};

export class RemoteColumnFilter extends React.Component<FilterProps, FilterState> {
  constructor(props: FilterProps) {
    super(props);
    const defaultValue = props.filterEditorProps.mode === 'multiple' ? [] : '';
    this.state = {
      value: props.filterValue ? props.filterValue.value : defaultValue,
    };
    this.onChange = this.onChange.bind(this);
    this.onValueChange = this.onValueChange.bind(this);
  }

  onChange(value: string) {
    this.onValueChange(value);
    this.setValue(value);
  }

  setValue(value: string) {
    this.setState({
      value,
    });
  }

  onValueChange(value: string) {
    if (this.props.onChange) {
      this.props.onChange({ ...this.props.filterValue, value });
    }
  }

  render() {
    const { filterEditorProps, render } = this.props;

    return (
      render &&
      render(
        <RemoteSelect
          {...filterEditorProps}
          onChange={this.onChange}
          value={this.state.value}
          allowClear
        />
      )
    );
  }
}
