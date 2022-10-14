import { AttrSelectors } from './AttrSelectorField';
import { ScrapeMethod } from '../types';

interface PropTypes {
  scrapeMethod: string;
}

export function HtmlScrapeConfig({ scrapeMethod }: PropTypes) {
  return (
    <>
      {scrapeMethod === ScrapeMethod.Html && (
        <AttrSelectors
          parentName={['scrape_method_configuration', 'html_attr_selectors']}
          title={'HTML Target Selector'}
        />
      )}

      <AttrSelectors
        parentName={['scrape_method_configuration', 'html_exclusion_selectors']}
        title={'HTML Exclusion Selector'}
      />
    </>
  );
}
