import { ReactNode } from "react";
import { BarChart3, Cable, Contact, Inbox, LogOut, Megaphone, Moon, Settings, Kanban, Sun } from "lucide-react";
import { Page } from "../types";
import { useAuth } from "../lib/auth";

export const nav: [Page, typeof BarChart3][] = [
  ["Dashboard", BarChart3],
  ["Inbox", Inbox],
  ["Kontakti", Contact],
  ["Prodajni levak", Kanban],
  ["Kampanje", Megaphone],
  ["Integracije", Cable],
  ["Podešavanja", Settings],
];

type ShellProps = {
  page: Page;
  setPage: (page: Page) => void;
  dark: boolean;
  setDark: (dark: boolean) => void;
  accent: string;
  setAccent: (accent: string) => void;
  onOpenCommand: () => void;
  children: ReactNode;
};

export function Shell({ page, setPage, dark, setDark, accent, setAccent, onOpenCommand, children }: ShellProps) {
  const { user, logout } = useAuth();

  return (
    <main className="shell">
      <aside>
        <div className="brand">CRM<span>+</span></div>
        <nav>
          {nav.map(([name, Icon]) => (
            <button className={page === name ? "active" : ""} onClick={() => setPage(name)} key={name}>
              <Icon size={18} />
              {name}
            </button>
          ))}
        </nav>
        {user && (
          <div className="user-chip">
            <div>
              <strong>{user.name}</strong>
              <span>{user.email}</span>
            </div>
            <button aria-label="Odjava" onClick={logout}><LogOut size={16} /></button>
          </div>
        )}
      </aside>
      <section className="content">
        <header>
          <div>
            <p>CRM Online Marketing</p>
            <h1>{page}</h1>
          </div>
          <div className="header-actions">
            <select aria-label="Akcentna boja" value={accent} onChange={(e) => setAccent(e.target.value)}>
              <option value="siva">Standardna siva</option>
              <option value="plava">Okean plava</option>
              <option value="narandzasta">Narandžasta</option>
              <option value="zelena">Šumsko zelena</option>
            </select>
            <button className="command" onClick={onOpenCommand}>⌘ K</button>
            <button className="command" onClick={() => setDark(!dark)}>{dark ? <Sun /> : <Moon />} Tema</button>
          </div>
        </header>
        <div className="demo">Razvojni režim: demo/test podaci.</div>
        {children}
      </section>
    </main>
  );
}
