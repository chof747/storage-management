// src/types/labelPrintRequest.tsx

export interface StartPosition {
  row: number;
  col: number;
}

export interface LabelSheet {
  start_pos: StartPosition;
}

export interface LabelPrintRequest {
  sheets: LabelSheet[];
  strategy: string;
}
