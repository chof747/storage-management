import React from 'react';
import { Checkbox, FormControlLabel } from '@mui/material';
import { FormField } from '../ModelForm';

export function renderCheckboxField<T>(
  field: FormField<T>,
  value: boolean,
  handleChange: React.ChangeEventHandler
) {
  const name = String(field.name);

  return (
    <FormControlLabel
      key={name}
      control={
        <Checkbox
          name={name}
          checked={!!value}
          onChange={handleChange}
        />
      }
      label={field.label}
    />
  );
}
