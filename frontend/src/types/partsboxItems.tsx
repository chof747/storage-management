export interface PartsBoxItem {
  id?: string;
  name: string;
  label: string;
  description: string;
  storage_place: string;
  total_stock: number;
  material_part_number: string;
  queued_for_printing: boolean;
}