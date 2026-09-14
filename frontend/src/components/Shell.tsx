import { ReactNode, useEffect, useRef, useState } from "react";
import { BarChart3, Cable, Contact, Inbox, Kanban, LogOut, Megaphone, Settings, Search, Bell, ChevronDown, Phone } from "lucide-react";
import { Page } from "../types";
import { useAuth } from "../lib/auth";
import { apiFetch } from "../lib/api";

function initials(name: string) {
  const parts = name.trim().split(/\s+/);
  return (parts[0]?.[0] || "").concat(parts.length > 1 ? parts[parts.length - 1][0] : "").toUpperCase();
}

function useOutsideClick(ref: React.RefObject<HTMLElement | null>, onOutside: () => void) {
  useEffect(() => {
    function handler(event: MouseEvent) {
      if (ref.current && !ref.current.contains(event.target as Node)) onOutside();
    }
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [ref, onOutside]);
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

const pageSubtitles: Record<Page, string> = {
  Dashboard: "Pregled prodaje i aktivnosti",
  Inbox: "Razgovori sa klijentima",
  Kontakti: "Vaša baza kontakata",
  "Prodajni levak": "Prodaja kroz faze",
  Kampanje: "Oglasi i praćenje potrošnje",
  Integracije: "Povezani kanali i kanali za upite",
  Podešavanja: "Nalog i podešavanja aplikacije",
};

const pageEyebrows: Record<Page, string> = {
  Dashboard: "01 / Pregled",
  Inbox: "02 / Razgovori",
  Kontakti: "03 / Baza kontakata",
  "Prodajni levak": "04 / Prodaja",
  Kampanje: "05 / Kampanje",
  Integracije: "06 / Kanali",
  Podešavanja: "07 / Nalog",
};

type ContactSearchResult = { id: number; name: string; phone: string | null; email: string | null };
type NotificationItem = { type: "message" | "lead" | "reminder"; text: string; reference_id: number; created_at: string };

type ShellProps = {
  page: Page;
  setPage: (page: Page) => void;
  children: ReactNode;
  onOpenCommand: () => void;
};

export function Shell({ page, setPage, children, onOpenCommand }: ShellProps) {
  const { user, logout } = useAuth();

  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<ContactSearchResult[]>([]);
  const [searchOpen, setSearchOpen] = useState(false);
  const searchRef = useRef<HTMLDivElement>(null);
  useOutsideClick(searchRef, () => setSearchOpen(false));

  const [notifOpen, setNotifOpen] = useState(false);
  const [notifications, setNotifications] = useState<{ count: number; items: NotificationItem[] }>({ count: 0, items: [] });
  const notifRef = useRef<HTMLDivElement>(null);
  useOutsideClick(notifRef, () => setNotifOpen(false));

  const [avatarOpen, setAvatarOpen] = useState(false);
  const avatarRef = useRef<HTMLDivElement>(null);
  useOutsideClick(avatarRef, () => setAvatarOpen(false));

  useEffect(() => {
    if (searchQuery.trim().length < 2) {
      setSearchResults([]);
      return;
    }
    const timeout = setTimeout(() => {
      apiFetch(`/contacts?search=${encodeURIComponent(searchQuery.trim())}`)
        .then((r) => (r.ok ? r.json() : Promise.reject()))
        .then((items: ContactSearchResult[]) => {
          setSearchResults(items.slice(0, 6));
          setSearchOpen(true);
        })
        .catch(() => undefined);
    }, 300);
    return () => clearTimeout(timeout);
  }, [searchQuery]);

  const loadNotifications = () => {
    apiFetch("/dashboard/notifications")
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then(setNotifications)
      .catch(() => undefined);
  };

  useEffect(() => {
    loadNotifications();
    const interval = setInterval(loadNotifications, 30000);
    return () => clearInterval(interval);
  }, []);

  const goToContact = () => {
    setSearchOpen(false);
    setSearchQuery("");
    setPage("Kontakti");
  };

  const goToNotification = (item: NotificationItem) => {
    setNotifOpen(false);
    setPage(item.type === "message" ? "Inbox" : "Prodajni levak");
  };

  return (
    <div className="app-container">
      <div className="shell">
        <aside>
          <div className="brand">
            <div className="brand-icon"><Phone size={16} /></div>
            Called
          </div>
          <span className="version-badge">v1.0</span>
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
              <div className="search-bar" ref={searchRef}>
                <Search size={18} />
                <input
                  type="text"
                  placeholder="Pretraži kontakte"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onFocus={() => searchResults.length > 0 && setSearchOpen(true)}
                />
                <span className="shortcut-tag">⌘K</span>
                {searchOpen && searchResults.length > 0 && (
                  <div className="dropdown-panel search-results">
                    {searchResults.map((c) => (
                      <button className="dropdown-item" key={c.id} onClick={goToContact}>
                        <strong>{c.name}</strong>
                        <span>{c.phone || c.email || "Nema kontakt podataka"}</span>
                      </button>
                    ))}
                  </div>
                )}
              </div>
              <div className="header-actions">
                <button className="icon-btn" onClick={onOpenCommand}><Search size={18} /></button>
                <div className="online-pill"><span className="online-dot" />ONLINE</div>
                <div className="dropdown-wrap" ref={notifRef}>
                  <button className="icon-btn" onClick={() => setNotifOpen((v) => !v)}>
                    <Bell size={18} />
                    {notifications.count > 0 && <span className="notif-badge">{notifications.count}</span>}
                  </button>
                  {notifOpen && (
                    <div className="dropdown-panel notif-dropdown">
                      {notifications.items.length === 0 ? (
                        <p className="dropdown-empty">Nema novih obaveštenja.</p>
                      ) : (
                        notifications.items.map((item, i) => (
                          <button className="dropdown-item" key={i} onClick={() => goToNotification(item)}>
                            {item.text}
                          </button>
                        ))
                      )}
                    </div>
                  )}
                </div>
                {user && (
                  <div className="dropdown-wrap" ref={avatarRef}>
                    <div className="avatar-chip" onClick={() => setAvatarOpen((v) => !v)}>
                      <div className="avatar avatar-small">{initials(user.name)}</div>
                      <ChevronDown size={16} />
                    </div>
                    {avatarOpen && (
                      <div className="dropdown-panel avatar-dropdown">
                        <button className="dropdown-item" onClick={() => { setAvatarOpen(false); setPage("Podešavanja"); }}>
                          Podešavanja
                        </button>
                        <button className="dropdown-item" onClick={logout}>Odjava</button>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
            <div className="topbar-title">
              <span className="page-eyebrow">{pageEyebrows[page]}</span>
              <h1>{page}</h1>
              <p>{pageSubtitles[page]}</p>
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
