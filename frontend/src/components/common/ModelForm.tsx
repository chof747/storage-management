import React, { useEffect, useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Paper,
  MenuItem,
  CircularProgress,
} from '@mui/material';

export type FormField<T> = {
  name: keyof T;
  label: string;
  type?: 'text' | 'number' | 'select';
  required?: boolean;
  options?: string[];
  loadOptions?: () => Promise<string[]>;
};

type Props<T> = {
  fields: FormField<T>[];
  initialValues?: Partial<T>;
  onValidSubmit: (data: T) => Promise<void>;
  onSuccess: () => void;
  submitLabel?: string;
};

function ModelForm<T extends Record<string, any>>({
  fields,
  initialValues = {},
  onValidSubmit,
  onSuccess,
  submitLabel = 'Submit',
}: Props<T>) {
  const [form, setForm] = useState<Partial<T>>(initialValues);
  const [selectOptions, setSelectOptions] = useState<Record<string, string[]>>({});
  const [loadingSelects, setLoadingSelects] = useState<Record<string, boolean>>({});
  const [generalError, setGeneralError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    setForm(initialValues);
  }, [initialValues]);

  // Load async options if needed
  useEffect(() => {
    fields.forEach((field) => {
      if (field.type === 'select' && field.loadOptions && !selectOptions[field.name as string]) {
        setLoadingSelects((prev) => ({ ...prev, [field.name as string]: true }));
        field
          .loadOptions()
          .then((opts) => {
            setSelectOptions((prev) => ({ ...prev, [field.name as string]: opts }));
          })
          .finally(() => {
            setLoadingSelects((prev) => ({ ...prev, [field.name as string]: false }));
          });
      }
    });
  }, [fields]);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    const fieldDef = fields.find((f) => f.name === name);

    setForm((prev) => ({
      ...prev,
      [name]: fieldDef?.type === 'number' ? parseFloat(value) || '' : value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setGeneralError(null);
    setFieldErrors({});

    try {
      await onValidSubmit(form as T);
      console.log("success!")
      onSuccess();
    } catch (err: any) {
      console.log(err)
      if (err.name === 'ValidationError') {
        // custom error (e.g. from Zod or manual)
      } else if (err.response?.status === 422) {
        const data = await err.response.json();

        const errors: Record<string, string> = {};
        for (const detail of data.detail) {
          const loc = detail.loc[detail.loc.length - 1]; // e.g. "main_metric"
          errors[loc] = detail.msg;
        }

        setFieldErrors(errors);
        setGeneralError("Please correct the highlighted errors.");
      } else if (err.response?.status === 400 || err.response?.status === 500) {
        const data = await err.response.json();
        setGeneralError(data.detail || "Something went wrong.");
      } else {
        setGeneralError("Unknown error occurred.");
      }
    }
  };


  return (
    <Paper sx={{ p: 2 }}>
      {generalError && (
        <Box
          sx={{
            backgroundColor: '#fdecea',
            border: '1px solid #f5c2c0',
            color: '#a94442',
            fontSize: '0.875rem',
            p: 1,
            mb: 2,
            borderRadius: 1,
          }}
        >
          {generalError}
        </Box>
      )}
      <form onSubmit={handleSubmit}>
        <Box display="flex" flexDirection="column" gap={2}>
          {fields.map((field) => {
            const name = String(field.name);
            const value = form[field.name] ?? '';
            const loading = loadingSelects[name] || false;

            if (field.type === 'select') {
              const options = field.options ?? selectOptions[name] ?? [];

              return (
                <TextField
                  key={name}
                  name={name}
                  label={field.label}
                  value={value}
                  onChange={handleChange}
                  required={field.required}
                  size="small"
                  error={Boolean(fieldErrors[name])}
                  helperText={fieldErrors[name]}
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
                error={Boolean(fieldErrors[name])}
                helperText={fieldErrors[name]}
              />
            );
          })}
          <Box>
            <Button variant="contained" type="submit">
              {submitLabel}
            </Button>
          </Box>
        </Box>
      </form>
    </Paper>
  );
}

export default ModelForm;
