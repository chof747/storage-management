import ModelForm, { FormField } from '../common/ModelForm';
import { StorageElement } from '../../types/storageElements'

type Props = {
  item: StorageElement | null;
  onSubmit: (data: StorageElement) => Promise<void>;
  onSuccess: () => void;
};

const fetchLocations = async (): Promise<string[]> => {
  const response = await fetch('http://localhost:8000/api/locations');
  return response.json();
};

const fields: FormField<Record<string, any>>[] = [
  { name: 'name', label: 'Name', required: true },
  { name: 'location', label: 'Location', required: true },
  { name: 'position', label: 'Position', required: true },
  { name: 'storage_type', label: 'Type of Storage', required: true },
  { name: 'description', label: 'Description', required: true },

];

export default function StorageElementForm({ item, onSubmit, onSuccess }: Props) {
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
