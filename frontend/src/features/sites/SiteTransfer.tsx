import { Button } from 'antd';
import { Site } from '../../features/sites/types';
import { useCurrentUser } from '../../common/hooks';

export async function copySiteConfig(site: Site) {
  const { base_urls, collection_method, scrape_method, scrape_method_configuration, playbook } =
    site;

  const config = JSON.stringify(
    {
      base_urls,
      collection_method,
      scrape_method,
      scrape_method_configuration,
      playbook,
      __copyPasta: +new Date(),
    },
    null,
    2
  );
  await navigator.clipboard.writeText(config);
}

export async function pasteSiteConfig(onPaste: Function) {
  try {
    const site = await navigator.clipboard.readText();
    const config = JSON.parse(site);
    if (!config.__copyPasta) {
      return;
    }
    // eslint-disable-next-line no-restricted-globals
    const result = confirm('Are you sure you want to pasta?');
    result && onPaste(config);
  } catch (error) {}
}

export function SiteTransfer({ site, onPaste }: { site: Site; onPaste: Function }) {
  const user = useCurrentUser();
  return user?.is_admin ? (
    <div className="space-x-2">
      <Button onClick={() => copySiteConfig(site)}>Copy</Button>
      <Button onClick={() => pasteSiteConfig(onPaste)}>Pasta</Button>
    </div>
  ) : null;
}
