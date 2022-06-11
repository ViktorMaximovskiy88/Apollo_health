import { DateTime, Duration } from 'luxon';

/**
 * Pretty date renders a date in the default format if a date is present.
 * If not render a default missing placeholder value.
 */
export function prettyDateFromISO(
  value?: string,
  dateFormat = DateTime.DATE_MED
): string {
  return value
    ? DateTime.fromISO(value, { zone: 'utc' }).toLocaleString(dateFormat)
    : '';
}

/**
 * Pretty date renders a date in the default format from a date obj
 */
export function prettyDate(
  value: Date,
  dateFormat = DateTime.DATE_MED
): string {
  return DateTime.fromJSDate(value, { zone: 'utc' }).toLocaleString(dateFormat);
}

/**
 * Pretty relative date renders a date distance from the start date until the end date.
 * If the end date is missing the start date is relative to now.
 */
export function prettyDateDistance(
  startDate: string,
  endDate?: string
): string {
  const startDateTime = DateTime.fromISO(startDate);
  const endDateTime = endDate ? DateTime.fromISO(endDate) : DateTime.now();
  const duration = endDateTime.diff(startDateTime, [
    'hours',
    'minutes',
    'seconds',
  ]);
  return stripZeroUnitsFromDuration(duration).toHuman();
}

// Helper func to strip zero value units
function stripZeroUnitsFromDuration(duration: Duration): Duration {
  const nonZeroUnits: any = {};
  for (const [unit, value] of Object.entries(duration.toObject())) {
    if (value > 0) {
      nonZeroUnits[unit] = value;
    }
  }
  return Duration.fromObject(nonZeroUnits);
}
