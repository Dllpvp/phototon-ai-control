import { JournalTable } from "../components/decision/JournalTable";
import { NotificationLog } from "../components/decision/NotificationLog";

export default function JournalPage() {
  return (
    <main className="flex flex-col gap-6">
      <section className="card p-4">
        <h1 className="display text-2xl" style={{ color: "var(--text)" }}>Журнал решений</h1>
        <div className="mt-4"><JournalTable /></div>
      </section>
      <section className="card p-4">
        <h2 className="display text-xl" style={{ color: "var(--text)" }}>Журнал отправок</h2>
        <div className="mt-4"><NotificationLog /></div>
      </section>
    </main>
  );
}
