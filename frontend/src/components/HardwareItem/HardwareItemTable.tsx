import FilterableTable, { TableColumn } from '../common/FilterableTable';
import { HardwareItem } from '../../types/hardwareItems';
import { ShoppingCart as ReorderIcon } from '@mui/icons-material';

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
  {
    key: 'storage_element',
    label: 'Stored in',
    filterable: true,
    filterKey: 'storage_element.name',
    render: (val) => val?.name ?? '–',
  },
  {
    key: 'reorder', label: 'Reorder', filterable: true, render: (val, row) => {
      if (val) {
        return row.reorder_link
          ? <a href={row.reorder_link}><ReorderIcon color="warning" /></a>
          : <ReorderIcon />
      }
      else
        return null;
    }
  },
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
