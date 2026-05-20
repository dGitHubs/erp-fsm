const LABELS: Record<string, string> = {
  draft: 'Brouillon',
  confirmed: 'Confirmé',
  in_progress: 'En cours',
  done: 'Terminé',
  cancelled: 'Annulé',
};

const COLORS: Record<string, string> = {
  draft: 'badge--gray',
  confirmed: 'badge--blue',
  in_progress: 'badge--orange',
  done: 'badge--green',
  cancelled: 'badge--red',
};

export function StatusBadge({ status }: { status: string }) {
  return (
    <span className={`badge ${COLORS[status] ?? 'badge--gray'}`}>
      {LABELS[status] ?? status}
    </span>
  );
}