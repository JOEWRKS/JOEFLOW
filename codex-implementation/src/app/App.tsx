export function App() {
  const roles = ['Employee', 'Manager', 'Finance', 'Admin'] as const

  return (
    <nav aria-label="Role workspaces">
      {roles.map((role) => (
        <button key={role} type="button">
          {role} workspace
        </button>
      ))}
    </nav>
  )
}
