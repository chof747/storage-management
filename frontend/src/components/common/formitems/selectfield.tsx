import React from 'react';
import {
  TextField,
  MenuItem,
  CircularProgress
} from '@mui/material';
import { FormField } from '../ModelForm';

export default function renderSelectField<T>(
  field: FormField<T>,
  value: any,
  error: string | undefined,
  handleChange: React.ChangeEventHandler,
  loading: boolean,
  options: string[]
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
      size="small"
      error={Boolean(error)}
      helperText={error}
      select
      disabled={loading}
      InputProps={{
        endAdornment: loading ? <CircularProgress size={20} /> : undefined,
      }}
    >
      {options.map((opt) => (
        <MenuItem key={opt} value={opt}>
          {opt}
        </MenuItem>
      ))}
    </TextField>
  );
}
