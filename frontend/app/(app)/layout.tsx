"use client";

import { useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import { motion } from "framer-motion";
import { Loader2 } from "lucide-react";
import { useAuth } from "@/lib/auth";
import Sidebar from "@/components/Sidebar";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (!loading && !user) router.replace("/login");
  }, [loading, user, router]);

  if (loading || !user) {
    return (
      <div className="flex h-screen items-center justify-center bg-base">
        <Loader2 className="h-6 w-6 animate-spin text-brand-500" />
      </div>
    );
  }

  return (
    <div className="relative flex min-h-screen bg-base bg-mesh-light dark:bg-mesh-dark">
      <div className="pointer-events-none fixed left-1/4 top-0 -z-10 h-96 w-96 animate-blob rounded-full bg-brand-500/20 blur-3xl" />
      <div className="pointer-events-none fixed right-1/4 top-1/3 -z-10 h-96 w-96 animate-blob rounded-full bg-fuchsia-500/10 blur-3xl [animation-delay:4s]" />

      <Sidebar />
      <main className="min-h-screen flex-1 overflow-y-auto">
        <motion.div
          key={pathname}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35, ease: "easeOut" }}
          className="mx-auto max-w-6xl p-8"
        >
          {children}
        </motion.div>
      </main>
    </div>
  );
}
