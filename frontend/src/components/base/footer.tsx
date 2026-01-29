import { Link } from "react-router-dom";

const NAV_ITEMS = [
    { label: "Главная", href: "/" },
    { label: "О нас", href: "/about" },
    { label: "Контакты", href: "/contacts" },
    { label: "Политика конфиденциальности", href: "/privacy" },
] as const;

export function Footer() {

    return (
        <footer className="bg-gray-100 dark:bg-gray-900 py-8">
            <div className="container mx-auto px-4 md:px-8 lg:px-16 flex flex-col items-start gap-2">
                {NAV_ITEMS.map((item) => {
                    return (
                        <Link to={item.href}>{item.label}</Link>
                    );
                })}
            </div>
        </footer>
    );
}