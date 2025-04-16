import ModelForm, { FormField } from '../common/ModelForm';
import { HardwareItem } from '../../types/hardwareItems'
import { createPlaceholder } from '../../api/storageElement';

type Props = {
  item: HardwareItem | null;
  onSubmit: (data: HardwareItem) => Promise<void>;
  onSuccess: () => void;
};

const fetch_storage = async (): Promise<{ id: any; label: string }[]> => {
  const response = await fetch('http://localhost:8000/api/storage');
  const data = await response.json();
  return data.map((se: any) => ({
    id: se.id,
    label: se.name
  }));
};

const fields: FormField<Record<string, any>>[] = [
  { name: 'hwtype', label: 'Type', required: true },
  { name: 'main_metric', label: 'Main Metric', required: true },
  { name: 'secondary_metric', label: 'Secondary Metric' },
  { name: 'length', label: 'Length', type: 'number' },
  {
    name: 'storage_element_id',
    label: 'Stored in',
    type: 'select-create',
    loadOptions: fetch_storage,
    createNew: async () => {
      // Open your modal here or inline prompt
      const name = prompt("New storage name?");
      if (null !== name) {
        const newItem = await createPlaceholder(name);
        return { id: newItem.id, label: newItem.name };
      } else {
        return { id: 0, label: '' };
      }
    }
  },
  {
    name: 'reorder',
    label: 'Mark for Reordering',
    type: 'boolean',
  },
  {
    name: 'reorder_link',
    label: 'Reorder Link',
    type: 'text',
  },
];

export default function HardwareItemForm({ item, onSubmit, onSuccess }: Props) {
  return (
    <ModelForm
      fields={fields}
      initialValues={item ?? {}}
      onValidSubmit={onSubmit}
      onSuccess={onSuccess}
      submitLabel={item ? 'Update' : 'Add'}
    />
  );
}
