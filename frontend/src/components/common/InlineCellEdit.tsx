// components/common/InlineEditCell.tsx
import React, { useState } from "react";
import { TextField, CircularProgress } from "@mui/material";

export type InlineEditCellProps<T> = {
  value: T;
  renderDisplay?: (value: T) => React.ReactNode;
  onCommit: (newValue: T) => Promise<void> | void;
  editable?: boolean;
  parse?: (raw: string) => T;
  format?: (value: T) => string;
  /** MUI TextField props passthrough (size, placeholder, etc.) */
  textFieldProps?: Omit<React.ComponentProps<typeof TextField>, "value" | "onChange" | "onKeyDown">;
  onCancel?: () => void;
  defaultEditing?: boolean;
};

export default function InlineCellEdit<T = unknown>({
  value,
  renderDisplay,
  onCommit,
  editable = true,
  parse,
  format,
  textFieldProps,
  onCancel,
  defaultEditing = false,
}: InlineEditCellProps<T>) {

  const [isEditing, setIsEditing] = useState<boolean>(defaultEditing);
  const [raw, setRaw] = useState<string>(() => (format ? format(value) : (value ?? "") + ""));
  const [busy, setBusy] = useState<boolean>(false);

  const displayNode = renderDisplay
    ? renderDisplay(value)
    : (value === undefined || value === null || value === "" ? <i>(none)</i> : String(value));

  const toValue = (txt: string) => (parse ? parse(txt) : (txt as unknown as T));

  const commit = async () => {
    const newVal = toValue(raw);
    try {
      setBusy(true);
      await Promise.resolve(onCommit(newVal));
      setIsEditing(false);
    } finally {
      setBusy(false);
    }
  };

  const cancel = () => {
    setRaw(format ? format(value) : (value ?? "") + "");
    setIsEditing(false);
    onCancel?.();
  };

  if (!editable) {
    return <>{displayNode}</>;
  }

  if (!isEditing) {
    return (
      <div
        style={{ cursor: "text", minHeight: 24, display: "flex", alignItems: "center" }}
        onClick={() => setIsEditing(true)}
      >
        {displayNode}
      </div>
    );
  }

  return (
    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
      <TextField
        autoFocus
        fullWidth
        size="small"
        variant="standard"
        value={raw}
        inputProps={{ style: { fontSize: '0.875rem', lineHeight: 1.43, padding: 0 } }}
        onChange={(e) => setRaw(e.target.value)}
        onBlur={() => cancel()}
        onKeyDown={(e) => {
          if (e.key === "Enter") commit();
          if (e.key === "Escape") cancel();
        }}
        disabled={busy}
        {...textFieldProps}
      />
      {busy && <CircularProgress size={18} />}
    </div>
  );
}
