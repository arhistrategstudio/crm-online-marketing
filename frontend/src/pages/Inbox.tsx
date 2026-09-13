import { FormEvent, useEffect, useState } from "react";
import { apiFetch } from "../lib/api";

export function Inbox() {
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [messages, setMessages] = useState(["Zdravo, interesuje me ponuda.", "Hvala na upitu, šaljemo ponudu danas."]);
  const [message, setMessage] = useState("");

  useEffect(() => {
    apiFetch("/conversations")
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((items) => { if (items.length) setConversationId(items[0].id); })
      .catch(() => undefined);
  }, []);

  useEffect(() => {
    if (!conversationId) return;
    apiFetch(`/conversations/${conversationId}/messages`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((items) => setMessages(items.map((item: { content: string }) => item.content)))
      .catch(() => undefined);
  }, [conversationId]);

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!message.trim() || !conversationId) return;
    const response = await apiFetch(`/conversations/${conversationId}/messages`, {
      method: "POST",
      body: JSON.stringify({ content: message.trim() }),
    });
    if (!response.ok) {
      alert("Poruka nije poslata.");
      return;
    }
    const saved = await response.json();
    setMessages([...messages, saved.content]);
    setMessage("");
  };

  return (
    <section className="card">
      <h2>Ana Jovanović · Instagram</h2>
      {messages.map((item, index) => (
        <p className={index % 2 ? "out" : "in"} key={`${item}-${index}`}>{item}</p>
      ))}
      <form className="inbox-form" onSubmit={submit}>
        <input value={message} onChange={(e) => setMessage(e.target.value)} placeholder="Napišite poruku..." />
        <button>Pošalji</button>
      </form>
    </section>
  );
}
