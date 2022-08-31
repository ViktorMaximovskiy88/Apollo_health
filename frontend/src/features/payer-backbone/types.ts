import { BaseDocument } from '../../common';

export interface PayerBackbone extends BaseDocument {
  l_id: number;
  name: string;
}

export interface Plan extends PayerBackbone {
  l_formulary_id: number;
  plan_type: string;
  channel: number;
}

export interface Formulary extends PayerBackbone {
  l_parent_id: number;
  l_bm_id: number;
  l_drug_list_id: number;
  l_ump_id: number;
}

export interface MCO extends PayerBackbone {}

export interface UMP extends PayerBackbone {}

export interface DrugList extends PayerBackbone {}

export interface PayerParent extends PayerBackbone {
  parent_type: string;
}

export interface BenefitManager extends PayerBackbone {}
