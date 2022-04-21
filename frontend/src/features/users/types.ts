import { BaseDocument } from '../types';

export interface User extends BaseDocument {
  email: string;
  full_name: string;
  disabled: boolean;
  roles: string[];
}
