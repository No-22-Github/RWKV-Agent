import Md3Dialog from "./Md3Dialog";

interface Props {
  open: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  confirmLabel?: string;
}

export default function ConfirmDialog({ open, onClose, onConfirm, title, message, confirmLabel }: Props) {
  return (
    <Md3Dialog
      open={open}
      onClose={onClose}
      title={title}
      actions={[
        { label: "取消", onClick: onClose },
        { label: confirmLabel || "确认", onClick: onConfirm, variant: "filled" },
      ]}
    >
      <p style={{ margin: 0, color: "var(--md-sys-color-on-surface-variant)" }}>{message}</p>
    </Md3Dialog>
  );
}
