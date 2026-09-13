import { ReactNode } from "react";
import { BarChart3, Cable, Contact, Inbox, Kanban, LogOut, Megaphone, Settings, Search, Bell, ChevronsLeft, ChevronsRight, MoreHorizontal } from "lucide-react";
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
  children: ReactNode;
  onOpenCommand: () => void;
};

export function Shell({ page, setPage, children, onOpenCommand }: ShellProps) {
  const { user, logout } = useAuth();

  return (
    <div className="app-container">
      <div className="shell">
        <aside>
          <div className="brand">
            <div className="brand-icon">📞</div>
            Called
          </div>
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
              <div className="user-chip-info">
                <strong>{user.name}</strong>
                <span>{user.email}</span>
              </div>
              <button aria-label="Odjava" onClick={logout}><LogOut size={16} /></button>
            </div>
          )}
        </aside>
        <section className="content">
          <div className="topbar">
            <div className="topbar-top">
              <div className="search-bar">
                <Search size={18} />
                <input type="text" placeholder="Search" />
                <span className="shortcut-tag">⌘K</span>
              </div>
              <div className="ticker">
                <div className="ticker-item">
                  <span className="ticker-label">Gold</span>
                  <span className="ticker-value">$4,114.44</span>
                </div>
                <div className="ticker-item">
                  <span className="ticker-label">Silver</span>
                  <span className="ticker-value">$48.42</span>
                </div>
              </div>
              <div className="header-actions">
                <button className="icon-btn" onClick={onOpenCommand}><Search size={18} /></button>
                <button className="icon-btn"><MoreHorizontal size={18} /></button>
                <button className="icon-btn"><Bell size={18} /></button>
                <div className="user-chip" style={{ marginTop: 0, padding: '6px 10px' }}>
                  <div className="user-chip-info">
                    <strong style={{ fontSize: '12px' }}>Mike Taylor</strong>
                    <span style={{ fontSize: '10px' }}>mike@example.com</span>
                  </div>
                </div>
              </div>
            </div>
            <div className="topbar-title">
              <h1>{page}</h1>
              <p>Welcome to your dashboard</p>
            </div>
          </div>
          <div className="main-content">
            {children}
          </div>
        </section>
      </div>
    </div>
  );
}
