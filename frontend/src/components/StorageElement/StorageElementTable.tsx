import FilterableTable, { TableColumn } from '../common/FilterableTable';
import { StorageElement } from '../../types/storageElements';

type Props = {
  items: StorageElement[];
  onEdit: (item: StorageElement) => void;
  onDelete: (id: number) => void;
};

const columns: TableColumn<StorageElement>[] = [
  { key: 'id', label: 'ID' },
  { key: 'name', label: 'Name', filterable: true },
  { key: 'location', label: 'Location', filterable: true },
  { key: 'position', label: 'Position' },
  { key: 'storage_type', label: 'Type', filterable: true },
  { key: 'description', label: 'Description' },
];

export default function StorageElementTable({ items, onEdit, onDelete }: Props) {
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
