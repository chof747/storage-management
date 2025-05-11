
import React from 'react';
import {
  TextField,
  MenuItem,
  CircularProgress,
  IconButton,
  InputAdornment,
  Box,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import { FormField } from '../ModelForm';

export default function renderSelectWithCreate<T>(
  field: FormField<T>,
  value: any,
  error: string | undefined,
  handleChange: React.ChangeEventHandler,
  loading: boolean,
  options: { id: any; label: string }[],
  onNewItem?: (id: any, label: string) => void
) {
  const name = String(field.name);

  const handleCreate = async () => {
    if (field.createNew) {
      const result = await field.createNew();
      (onNewItem !== undefined) && onNewItem(result.id, result.label);
    }
  };

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
        startAdornment: field.createNew ? (
          <InputAdornment position="start">
            <IconButton size="small" onClick={handleCreate}>
              <AddIcon fontSize="small" />
            </IconButton>
          </InputAdornment>
        ) : undefined,
        endAdornment: loading ? <CircularProgress size={20} /> : undefined,
      }}
    >
      {options.map((opt) => (
        <MenuItem key={opt.id} value={opt.id}>
          {opt.label}
        </MenuItem>
      ))}
    </TextField>
  );
}
