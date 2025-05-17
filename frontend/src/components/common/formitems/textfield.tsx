import React from 'react';
import { TextField } from '@mui/material';
import { FormField } from '../ModelForm';

export default function renderTextField<T>(
  field: FormField<T>,
  value: string,
  error: string | undefined,
  handleChange: React.ChangeEventHandler
) {
  const name = String(field.name);
  return (
    <TextField
      key={name}
      name={name}
      label={field.label}
      value={value}
      onChange={handleChange}
      required={field.required}
      type={field.type || 'text'}
      size="small"
      error={Boolean(error)}
      helperText={error}
    />
  );
}
