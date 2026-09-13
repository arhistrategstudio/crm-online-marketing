import { FormEvent, useEffect, useState } from "react";
import { apiFetch } from "../lib/api";
import { ConversationItem, channelLabels } from "../types";

type MessageItem = { id: number; sender: string; content: string };

export function Inbox() {
  const [conversations, setConversations] = useState<ConversationItem[]>([]);
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [messages, setMessages] = useState<MessageItem[]>([]);
  const [message, setMessage] = useState("");

  const loadConversations = () => {
    apiFetch("/conversations")
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((items: ConversationItem[]) => {
        setConversations(items);
        setConversationId((current) => current ?? (items.length ? items[0].id : null));
      })
      .catch(() => undefined);
  };

  useEffect(loadConversations, []);

  useEffect(() => {
    if (!conversationId) return;
    apiFetch(`/conversations/${conversationId}/messages`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((items: MessageItem[]) => {
        setMessages(items);
        setConversations((current) => current.map((c) => (c.id === conversationId ? { ...c, unread_count: 0 } : c)));
      })
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
    setMessages([...messages, saved]);
    setConversations((current) =>
      current.map((c) => (c.id === conversationId ? { ...c, last_message: saved.content } : c)),
    );
    setMessage("");
  };

  const selected = conversations.find((c) => c.id === conversationId) || null;

  return (
    <div className="inbox-layout">
      <section className="card inbox-list">
        <h2>Razgovori</h2>
        {!conversations.length && <p className="muted-line">Još uvek nema razgovora.</p>}
        {conversations.map((c) => (
          <button
            key={c.id}
            className={`inbox-list-item${c.id === conversationId ? " active" : ""}`}
            onClick={() => setConversationId(c.id)}
          >
            <div className="inbox-list-item-top">
              <strong>{c.contact_name}</strong>
              {c.unread_count > 0 && <span className="notif-badge">{c.unread_count}</span>}
            </div>
            <span className="muted-line">{channelLabels[c.channel] || c.channel}</span>
            {c.last_message && <p className="inbox-list-preview">{c.last_message}</p>}
          </button>
        ))}
      </section>
      <section className="card inbox-thread">
        {selected ? (
          <>
            <h2>{selected.contact_name} · {channelLabels[selected.channel] || selected.channel}</h2>
            <div className="inbox-thread-messages">
              {messages.map((item) => (
                <p className={item.sender === "agent" ? "out" : "in"} key={item.id}>{item.content}</p>
              ))}
            </div>
            <form className="inbox-form" onSubmit={submit}>
              <input value={message} onChange={(e) => setMessage(e.target.value)} placeholder="Napišite poruku..." />
              <button>Pošalji</button>
            </form>
          </>
        ) : (
          <p className="muted-line">Izaberite razgovor sa leve strane.</p>
        )}
      </section>
    </div>
  );
}
