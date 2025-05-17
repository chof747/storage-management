import renderTextField from './textfield';
import { FormField } from '../ModelForm';

export default function renderNumberField<T>(
  field: FormField<T>,
  value: number,
  error: string | undefined,
  handleChange: React.ChangeEventHandler
) {
  return renderTextField({ ...field, type: 'number' }, value.toString(), error, handleChange);
}
