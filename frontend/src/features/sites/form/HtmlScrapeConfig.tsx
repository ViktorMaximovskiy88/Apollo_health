import { AttrSelectors } from './AttrSelectorField';

export function HtmlScrapeConfig() {
  return (
    <>
      <AttrSelectors
        parentName={['scrape_method_configuration', 'html_attr_selectors']}
        title={'HTML Target Selector'}
      />
      <AttrSelectors
        parentName={['scrape_method_configuration', 'html_exclusion_selectors']}
        title={'HTML Exclusion Selector'}
      />
    </>
  );
}
