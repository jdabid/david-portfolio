import { useState } from "react";
import { sendContactMessage } from "../../services/api";

export default function Contact() {
  const [form, setForm] = useState({ name: "", email: "", subject: "", message: "" });
  const [status, setStatus] = useState<"idle" | "sending" | "sent" | "error">("idle");
  const [errorMsg, setErrorMsg] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus("sending");
    setErrorMsg("");

    try {
      await sendContactMessage(form);
      setStatus("sent");
      setForm({ name: "", email: "", subject: "", message: "" });
    } catch (err: any) {
      setStatus("error");
      setErrorMsg(err.message || "Failed to send message");
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  return (
    <section className="max-w-3xl mx-auto px-4 py-24">
      <h2 className="text-3xl font-bold text-white mb-4">Get In Touch</h2>
      <p className="text-gray-400 mb-8">
        Have a question or want to work together? Send me a message and I'll get back to you.
      </p>

      {status === "sent" ? (
        <div className="border border-green-500/30 bg-green-500/10 rounded-lg p-6 text-center">
          <p className="text-green-400 text-lg font-semibold">Message sent!</p>
          <p className="text-gray-400 text-sm mt-2">
            Thanks for reaching out. I'll reply as soon as possible.
          </p>
          <button
            onClick={() => setStatus("idle")}
            className="mt-4 text-primary-500 hover:text-primary-400 text-sm"
          >
            Send another message
          </button>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid md:grid-cols-2 gap-4">
            <input
              type="text"
              name="name"
              placeholder="Your Name"
              required
              value={form.name}
              onChange={handleChange}
              className="w-full px-4 py-3 bg-dark-800 border border-white/10 rounded text-white placeholder-gray-500 focus:border-primary-500 focus:outline-none transition-colors"
            />
            <input
              type="email"
              name="email"
              placeholder="Your Email"
              required
              value={form.email}
              onChange={handleChange}
              className="w-full px-4 py-3 bg-dark-800 border border-white/10 rounded text-white placeholder-gray-500 focus:border-primary-500 focus:outline-none transition-colors"
            />
          </div>
          <input
            type="text"
            name="subject"
            placeholder="Subject"
            required
            value={form.subject}
            onChange={handleChange}
            className="w-full px-4 py-3 bg-dark-800 border border-white/10 rounded text-white placeholder-gray-500 focus:border-primary-500 focus:outline-none transition-colors"
          />
          <textarea
            name="message"
            placeholder="Your Message"
            required
            rows={6}
            value={form.message}
            onChange={handleChange}
            className="w-full px-4 py-3 bg-dark-800 border border-white/10 rounded text-white placeholder-gray-500 focus:border-primary-500 focus:outline-none transition-colors resize-none"
          />

          {status === "error" && (
            <p className="text-red-400 text-sm">{errorMsg}</p>
          )}

          <button
            type="submit"
            disabled={status === "sending"}
            className="px-6 py-3 bg-primary-600 text-white rounded hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {status === "sending" ? "Sending..." : "Send Message"}
          </button>
        </form>
      )}
    </section>
  );
}
