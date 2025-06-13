// src/api/printLabels.tsx

import { LabelPrintRequest } from "../types/labelPrintRequest";
import { getApiBase } from "./endpoint";

const PATH = "/print/label";

export const printLabels = async (request: LabelPrintRequest): Promise<Blob> => {
  const API_BASE = await getApiBase();

  const response = await fetch(`${API_BASE}${PATH}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(request)
  });

  if (!response.ok) {
    const error = new Error("Failed to generate PDF") as Error & { response?: Response };
    error.response = response;
    throw error;
  }

  const pdfBlob = await response.blob();
  return pdfBlob;
};
