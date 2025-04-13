import FilterableTable, { TableColumn } from '../common/FilterableTable';
import { HardwareItem } from '../../types/hardwareItems';

type Props = {
  items: HardwareItem[];
  onEdit: (item: HardwareItem) => void;
  onDelete: (id: number) => void;
};

const columns: TableColumn<HardwareItem>[] = [
  { key: 'id', label: 'ID' },
  { key: 'hwtype', label: 'Type', filterable: true },
  { key: 'main_metric', label: 'Main Metric', filterable: true },
  { key: 'secondary_metric', label: 'Secondary' },
  { key: 'length', label: 'Length' },
  { key: 'location', label: 'Location', filterable: true },
];

export default function HardwareItemTable({ items, onEdit, onDelete }: Props) {
  return (
    <FilterableTable
      data={items}
      columns={columns}
      onEdit={onEdit}
      onDelete={(item) => onDelete(item.id!)}
      getRowId={(item) => item.id!}
    />
  );
}
