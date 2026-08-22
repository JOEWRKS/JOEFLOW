import type { Role } from '../domain/types';

const LABELS: Record<Role, string> = {
  EMPLOYEE: 'Employee',
  MANAGER: 'Manager',
  FINANCE: 'Finance',
  ADMIN: 'Admin',
};

interface Props {
  activeRole: Role;
  onChange: (role: Role) => void;
}

export function RoleSwitcher({ activeRole, onChange }: Props) {
  return (
    <nav className="role-switcher" aria-label="Role workspaces">
      {(Object.keys(LABELS) as Role[]).map((role) => (
        <button
          key={role}
          type="button"
          className={role === activeRole ? 'role-button active' : 'role-button'}
          aria-current={role === activeRole ? 'page' : undefined}
          onClick={() => onChange(role)}
        >
          <span className="role-dot" aria-hidden="true" />
          {LABELS[role]} workspace
        </button>
      ))}
    </nav>
  );
}
