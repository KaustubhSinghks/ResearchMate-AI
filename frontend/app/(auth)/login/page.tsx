"use client";

import { useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { Sparkles, Mail, Lock, ArrowRight, Loader2 } from "lucide-react";
import { useAuth } from "@/lib/auth";
import { ApiError } from "@/lib/api";

export default function LoginPage() {
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await login(email, password);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Login failed");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-base bg-mesh-light dark:bg-mesh-dark px-4">
      <div className="pointer-events-none absolute left-1/4 top-1/4 h-80 w-80 animate-blob rounded-full bg-brand-500/25 blur-3xl" />
      <div className="pointer-events-none absolute right-1/4 bottom-1/4 h-80 w-80 animate-blob rounded-full bg-cyan-400/15 blur-3xl [animation-delay:3s]" />

      <motion.form
        onSubmit={handleSubmit}
        initial={{ opacity: 0, y: 16, scale: 0.98 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.4, ease: "easeOut" }}
        className="card relative w-full max-w-sm p-8"
      >
        <div className="mb-6 flex flex-col items-center text-center">
          <div className="mb-3 flex h-11 w-11 items-center justify-center rounded-xl bg-brand-gradient shadow-lg shadow-brand-500/30">
            <Sparkles className="h-5 w-5 text-white" />
          </div>
          <h1 className="text-xl font-semibold text-ink">Welcome back</h1>
          <p className="mt-1 text-sm text-ink-muted">Log in to your research workspace</p>
        </div>

        {error && (
          <motion.p
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            className="mb-4 rounded-lg bg-red-500/10 px-3 py-2 text-sm text-red-500"
          >
            {error}
          </motion.p>
        )}

        <div className="relative mb-3">
          <Mail className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-faint" />
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="input-field pl-10"
          />
        </div>
        <div className="relative mb-5">
          <Lock className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-faint" />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="input-field pl-10"
          />
        </div>

        <button type="submit" disabled={submitting} className="btn-primary w-full">
          {submitting ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <>
              Log in <ArrowRight className="h-4 w-4" />
            </>
          )}
        </button>

        <p className="mt-5 text-center text-sm text-ink-muted">
          No account?{" "}
          <Link href="/signup" className="font-medium text-brand-500 hover:text-brand-400">
            Sign up
          </Link>
        </p>
      </motion.form>
    </div>
  );
}
