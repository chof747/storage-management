import { ResultPage } from "../types/page";

const API_BASE = "http://localhost:8000/api";
const PATH = "printing_strategies";

export const getPrintStrategies = async (): Promise<string[]> => {
  const res = await fetch(`${API_BASE}/${PATH}/`);
  return await res.json();
};
