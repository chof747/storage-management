import { getApiBase } from "./endpoint";
const PATH = "printing_strategies";

export const getPrintStrategies = async (): Promise<string[]> => {
  const API_BASE = await getApiBase();
  const res = await fetch(`${API_BASE}/${PATH}/`);
  return await res.json();
};
