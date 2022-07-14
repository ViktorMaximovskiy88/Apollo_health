import { Site } from './types';
import { DateTime } from 'luxon';
import reduce from 'lodash/reduce';
import { SiteStatus } from './siteStatus';

function isQualityHoldLastSevenDays(site: Site) {
  if (site.status !== SiteStatus.QualityHold) {
    return false;
  }
  if (!site.last_run_time) {
    return false;
  }
  const lastRunTime = DateTime.fromISO(site.last_run_time);
  const sevenDaysAgo = DateTime.now().minus({ days: 7 });
  if (lastRunTime < sevenDaysAgo) {
    return false;
  }
  return true;
}

interface QuickFilterType {
  assignedToMe: boolean;
  unassigned: boolean;
  onHoldLastSevenDays: boolean;
}

function filterQuickFilter(quickFilter: QuickFilterType, sites: Site[]): Site[] {
  sites = sites.filter((site) => {
    if (quickFilter.onHoldLastSevenDays && !isQualityHoldLastSevenDays(site)) {
      return false;
    }
    // TODO: add assignedToMe and unassigned logic after roles are added
    return true;
  });
  return sites;
}

/**
 * sorts sites in ascending order if any quick filter is active
 */
function sortQuickFilter(quickFilter: QuickFilterType, sites: Site[]): Site[] {
  if ((reduce(quickFilter, (acc, value) => acc || value), false)) {
    sites.sort((a: Site, b: Site) => {
      if (!a.last_run_time || !b.last_run_time) return 0;
      // @ts-ignore - ts doesn't like mathematical operations with strings
      return a.last_run_time - b.last_run_time;
    });
  }
  return sites;
}

interface TableStateType {
  quickFilter: QuickFilterType;
}
export function applyQuickFilter({ quickFilter }: TableStateType, sites: Site[]): Site[] {
  sites = filterQuickFilter(quickFilter, sites);
  sites = sortQuickFilter(quickFilter, sites);
  return sites;
}
