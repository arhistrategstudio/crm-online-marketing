import { ReactNode } from "react";
import { BarChart3, Cable, Contact, Inbox, Kanban, LogOut, Megaphone, Settings, Search, Bell, ChevronDown, MoreHorizontal, Phone } from "lucide-react";
import { Page } from "../types";
import { useAuth } from "../lib/auth";

function initials(name: string) {
  const parts = name.trim().split(/\s+/);
  return (parts[0]?.[0] || "").concat(parts.length > 1 ? parts[parts.length - 1][0] : "").toUpperCase();
}

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
            <div className="brand-icon"><Phone size={16} fill="white" /></div>
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
              <div className="user-chip-main">
                <div className="avatar">{initials(user.name)}</div>
                <div className="user-chip-info">
                  <strong>{user.name}</strong>
                  <span>{user.email}</span>
                </div>
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
                {user && (
                  <div className="avatar-chip">
                    <div className="avatar avatar-small">{initials(user.name)}</div>
                    <ChevronDown size={16} />
                  </div>
                )}
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
