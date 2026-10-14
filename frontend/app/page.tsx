"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";
import { useAuth } from "@/lib/auth";

export default function RootPage() {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (loading) return;
    router.replace(user ? "/dashboard" : "/login");
  }, [loading, user, router]);

  return (
    <div className="flex h-screen items-center justify-center bg-base bg-mesh-light dark:bg-mesh-dark">
      <Loader2 className="h-6 w-6 animate-spin text-brand-500" />
    </div>
  );
}
