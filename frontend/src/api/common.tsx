import { QueryFilter } from "../types/page";

/**
 * Build filter query string for API calls.
 * Returns a string like '&filter=key:val&filter=key2:val2' or '' when no filters.
 */
export function buildFilterParams(filters: QueryFilter[] = []): string {
  const filterParams = filters
    .map((f) => `${encodeURIComponent(f.key)}:${encodeURIComponent(f.value)}`)
    .join("&filter=");

  return filterParams ? `&filter=${filterParams}` : "";
}
