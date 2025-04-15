import ModelForm, { FormField } from '../common/ModelForm';
import { HardwareItem } from '../../types/hardwareItems'

type Props = {
  item: HardwareItem | null;
  onSubmit: (data: HardwareItem) => Promise<void>;
  onSuccess: () => void;
};

const fetchLocations = async (): Promise<string[]> => {
  const response = await fetch('http://localhost:8000/api/locations');
  return response.json();
};

const fields: FormField<Record<string, any>>[] = [
  { name: 'hwtype', label: 'Type', required: true },
  { name: 'main_metric', label: 'Main Metric', required: true },
  { name: 'secondary_metric', label: 'Secondary Metric' },
  { name: 'length', label: 'Length', type: 'number' },
  {
    name: 'storage_element',
    label: 'Stored in',
    type: 'select',
    loadOptions: fetchLocations,
    required: true,
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
