"use client";

import Link from "next/link";

export function StickyHeader() {
  return (
    <header className="sticky top-0 z-40 mx-auto flex max-w-[480px] items-center justify-center border-b border-zinc-200/80 bg-warm-gray/80 px-4 py-3 backdrop-blur-md">
      <Link href="/" className="font-display text-lg font-semibold tracking-tight text-zinc-900">
        AI Skin Health Monitor
      </Link>
    </header>
  );
}
