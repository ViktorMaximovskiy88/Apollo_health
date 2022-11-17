import { Rule } from 'antd/lib/form';

export function playbookValidator() {
  return {
    async validator(_rule: Rule, playbook: string) {
      !playbook || playbook.includes('playwright')
        ? Promise.resolve()
        : Promise.reject('Playbook must be a playwright script');
    },
  };
}
