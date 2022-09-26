import { MainLayout } from '../../../components';
import { SiteMenu } from '../../sites/SiteMenu';

export function DocumentFamilyPage() {
  return <MainLayout sidebar={<SiteMenu />} pageTitle={'Document Family'}></MainLayout>;
}
