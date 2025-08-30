import { ResultPage, QueryFilter } from "../types/page";
import { getApiBase } from "./endpoint";
import { PartsBoxItem } from "../types/partsboxItems";

const PATH = "electronic-parts";

export const getItems = async (offset: number, limit: number, filters: QueryFilter[] = []): Promise<ResultPage<PartsBoxItem>> => {
  const API_BASE = await getApiBase();

  var filterParams = filters.map(f => `${encodeURIComponent(f.key)}:${encodeURIComponent(f.value)}`).join('&filter=');
  if (filterParams) {
    filterParams = '&filter=' + filterParams;
  }
  const res = await fetch(`${API_BASE}/${PATH}/?offset=${offset}&limit=${limit}${filterParams}`);
  return await res.json();
};

export const togglePartforPrinting = async (item: PartsBoxItem): Promise<void> => {
  const API_BASE = await getApiBase();
  const un = item.queued_for_printing ? "un" : "";
  const res = await fetch(`${API_BASE}/${PATH}/${un}queueforprinting/${item.id}`);
  if (!res.ok) {
    const error = new Error('Could not toggle printing state');
    throw error;
  }
};

