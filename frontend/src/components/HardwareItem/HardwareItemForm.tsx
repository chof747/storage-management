import ModelForm, { FormField } from '../common/ModelForm';
import { HardwareItem } from '../../types/hardwareItems'

type Props = {
  item: HardwareItem | null;
  onSubmit: (data: HardwareItem) => Promise<void>;
  onSuccess: () => void;
};

const fetchLocations = async (): Promise<string[]> => {
  const response = await fetch('http://localhost:8000/api/locations');
  return response.json(); // Assuming API returns: ["Box A", "Box B", "Drawer 2"]
};

const fields: FormField<Record<string, any>>[] = [
  { name: 'hwtype', label: 'Type', required: true },
  { name: 'main_metric', label: 'Main Metric', required: true },
  { name: 'secondary_metric', label: 'Secondary Metric' },
  { name: 'length', label: 'Length', type: 'number' },
  {
    name: 'location',
    label: 'Location',
    type: 'select',
    loadOptions: fetchLocations,
    required: true,
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
