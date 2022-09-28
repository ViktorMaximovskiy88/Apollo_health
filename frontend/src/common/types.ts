import { TypeFilterValue, TypeSortInfo } from '@inovua/reactdatagrid-community/types';
export interface BaseDocument {
  _id: string;
}

export type NestedPartial<T> = {
  [P in keyof T]?: NestedPartial<T[P]>;
};

export interface TableInfoType {
  limit: number;
  skip: number;
  sortInfo: TypeSortInfo;
  filterValue: TypeFilterValue;
  siteId: string;
  documentType: string;
}
