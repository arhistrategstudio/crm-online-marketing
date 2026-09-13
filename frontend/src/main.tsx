import { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";
import "./contact-toolbar.css";
import "./contact-modal.css";
import "./workflow-controls.css";
import "./auth.css";

import { AuthProvider, useAuth } from "./lib/auth";
import { Page } from "./types";
import { Shell } from "./components/Shell";
import { CommandPalette } from "./components/CommandPalette";
import { Login } from "./pages/Login";
import { Signup } from "./pages/Signup";
import { Dashboard } from "./pages/Dashboard";
import { Inbox } from "./pages/Inbox";
import { Contacts } from "./pages/Contacts";
import { Pipeline } from "./pages/Pipeline";
import { Campaigns } from "./pages/Campaigns";
import { Integrations } from "./pages/Integrations";
import { Settings } from "./pages/Settings";

function AuthGate() {
  const [showSignup, setShowSignup] = useState(false);
  return showSignup ? (
    <Signup onSwitchToLogin={() => setShowSignup(false)} />
  ) : (
    <Login onSwitchToSignup={() => setShowSignup(true)} />
  );
}

function AppShell() {
  const [page, setPage] = useState<Page>("Dashboard");
  const [dark, setDark] = useState(false);
  const [accent, setAccent] = useState("plava");
  const [command, setCommand] = useState(false);

  useEffect(() => {
    document.documentElement.dataset.theme = dark ? "dark" : "light";
    document.documentElement.dataset.accent = accent;
  }, [dark, accent]);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setCommand(true);
      }
    };
    addEventListener("keydown", handler);
    return () => removeEventListener("keydown", handler);
  }, []);

  let body;
  if (page === "Dashboard") body = <Dashboard />;
  else if (page === "Inbox") body = <Inbox />;
  else if (page === "Kontakti") body = <Contacts />;
  else if (page === "Prodajni levak") body = <Pipeline />;
  else if (page === "Kampanje") body = <Campaigns />;
  else if (page === "Integracije") body = <Integrations />;
  else body = <Settings />;

  return (
    <Shell page={page} setPage={setPage} dark={dark} setDark={setDark} accent={accent} setAccent={setAccent} onOpenCommand={() => setCommand(true)}>
      {body}
      {command && (
        <CommandPalette
          onSelect={(next) => { setPage(next); setCommand(false); }}
          onClose={() => setCommand(false)}
        />
      )}
    </Shell>
  );
}

function AppRoot() {
  const { user, loading } = useAuth();
  if (loading) return null;
  return user ? <AppShell /> : <AuthGate />;
}

createRoot(document.getElementById("root")!).render(
  <AuthProvider>
    <AppRoot />
  </AuthProvider>,
);
