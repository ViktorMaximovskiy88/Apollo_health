import { BaseDocument } from '../../common';

export interface PayerBackbone extends BaseDocument {
  l_id: number;
  name: string;
}

export interface Plan extends PayerBackbone {
  l_formulary_id: number;
  l_parent_id: number;
  l_mco_id: number;
  l_bm_id: number;
  plan_type: string;
  channel: string;
  type: string;
  is_national: boolean;
  pharmacy_states: string[];
  medical_states: string[];
  pharmacy_lives: string[];
  medical_lives: string[];
}

export interface Formulary extends PayerBackbone {
  l_parent_id: number;
  l_bm_id: number;
  l_drug_list_id: number;
  l_ump_id: number;
}

export interface MCO extends PayerBackbone {}

export interface UMP extends PayerBackbone {
  benefit: string;
}

export interface PayerParent extends PayerBackbone {
  type: string;
  control: string;
}

export interface BenefitManager extends PayerBackbone {}
