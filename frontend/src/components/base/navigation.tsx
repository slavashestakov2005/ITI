import { Link, useLocation } from "react-router-dom";
import { useState } from "react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { Menu } from "lucide-react";
import { ModeToggle } from "@/components/base/mode-toggle";

/* ================== CONFIG ================== */

const APP_CONFIG = {
  siteName: "ИТИ-2027",
  mobileBreakpoint: "md",
};

const NAV_ITEMS = [
  { label: "Главная", href: "/" },
  { label: "Результаты", href: "/results" },
  { label: "Учительская", href: "/teacher-room" },
  { label: "О нас", href: "/news" },
] as const;

/* ============================================ */

export default function Layout() {
  const location = useLocation();
  const [open, setOpen] = useState(false);

  return (
    <div className="flex flex-col">
      <header className="border-b">
        <div
          className="container mx-auto flex items-center justify-between h-14 px-4 max-w-6xl"
        >
          <Link to="/" className="text-base font-semibold">
            {APP_CONFIG.siteName}
          </Link>

          {/* Mobile menu */}
          <div className="md:hidden">
            <Sheet open={open} onOpenChange={setOpen}>
              <SheetTrigger asChild>
                <Button size="icon" variant="ghost">
                  <Menu className="h-5 w-5" />
                </Button>
              </SheetTrigger>
              <SheetContent side="right" className="pt-10 max-w-xs">
                <nav className="flex flex-col gap-2 mx-2">
                  {NAV_ITEMS.map((item) => {
                    const isActive = location.pathname === item.href;

                    return (
                      <Link
                        key={item.href}
                        to={item.href}
                        onClick={() => setOpen(false)}
                        className={cn(
                          "rounded-md px-3 py-2 text-sm transition-colors",
                          isActive
                            ? "bg-primary text-primary-foreground"
                            : "hover:bg-muted"
                        )}
                      >
                        {item.label}
                      </Link>
                    );
                  })}
                  <ModeToggle />
                </nav>
              </SheetContent>
            </Sheet>
          </div>

          {/* Desktop menu */}
          <nav className="hidden md:flex gap-2">
            {NAV_ITEMS.map((item) => {
              const isActive = location.pathname === item.href;

              return (
                <Button
                  key={item.href}
                  asChild
                  variant={isActive ? "default" : "ghost"}
                  size="sm"
                >
                  <Link to={item.href}>{item.label}</Link>
                </Button>
              );
            })}
            <ModeToggle />
          </nav>
        </div>
      </header>
    </div>
  );
}
