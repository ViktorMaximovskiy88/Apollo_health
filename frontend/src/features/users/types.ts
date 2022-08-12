import { BaseDocument } from '../../common/types';

export interface User extends BaseDocument {
  email: string;
  full_name: string;
  is_admin: boolean;
  disabled: boolean;
  roles: string[];
}
