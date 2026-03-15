"use client";

import { useRef, useCallback, type ButtonHTMLAttributes } from "react";

interface RippleButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
  className?: string;
}

export function RippleButton({ children, className = "", onClick, ...props }: RippleButtonProps) {
  const btnRef = useRef<HTMLButtonElement>(null);

  const handleClick = useCallback(
    (e: React.MouseEvent<HTMLButtonElement>) => {
      const button = btnRef.current;
      if (button) {
        const rect = button.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const ripple = document.createElement("span");
        ripple.className = "absolute rounded-full bg-white/40 animate-ripple pointer-events-none";
        ripple.style.left = `${x - 100}px`;
        ripple.style.top = `${y - 100}px`;
        ripple.style.width = "200px";
        ripple.style.height = "200px";
        button.style.position = "relative";
        button.style.overflow = "hidden";
        button.appendChild(ripple);
        setTimeout(() => ripple.remove(), 500);
      }
      onClick?.(e);
    },
    [onClick]
  );

  return (
    <button
      ref={btnRef}
      type="button"
      className={className}
      onClick={handleClick}
      {...props}
    >
      {children}
    </button>
  );
}
