import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogClose } from "@/components/ui/dialog";
import { ArrowRight, X } from "lucide-react";

const NEWS_ITEMS = [
  {
    title: "Lorem ipsum dolor sit amet",
    text: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.",
    date: "01.01.2026",
    image: "https://placehold.co/850x120",
  },
  {
    title: "Ut enim ad minim veniam",
    text: "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
    date: "05.01.2026",
    image: "https://placehold.co/900x140",
  },
  {
    title: "Duis aute irure dolor",
    text: "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
    date: "10.01.2026",
    image: "https://placehold.co/800x110",
  },
  {
    title: "Duis aute irure dolor",
    text: "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
    date: "10.01.2026",
    image: "https://placehold.co/400x300",
  },
] as const;

export default function InfoPage() {
  return (
    <div className="container mx-auto px-4 py-8 space-y-10 md:px-8 lg:px-16 max-w-6xl">
      {/* Header */}
      <section className="space-y-4 flex flex-col items-center my-30">
        <h1 className="text-3xl font-bold text-center">Что такое ИТИ</h1>
        <p className="max-w-2xl text-muted-foreground text-center">
          Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam.
        </p>
        <Button className="mt-5">
          Перейти к результатам
          <ArrowRight className="h-4 w-4" />
        </Button>
      </section>

      {/* News */}
      <section className="space-y-6">
        <h2 className="text-2xl font-semibold text-center md:text-left">Новости</h2>

        <div className="flex flex-col items-center md:grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {NEWS_ITEMS.map((news, index) => (
            <Dialog key={index}>
              <DialogTrigger asChild>
                <Card className="w-80 md:max-w-none h-95 hover:shadow-lg transition flex flex-col cursor-pointer p-5">
                  {news.image && <img src={news.image} alt={news.title} className="w-full h-40 object-contain" />}
                  <CardHeader className="p-1 pb-0">
                    <CardTitle className="text-base">{news.title}</CardTitle>
                    <span className="text-xs text-muted-foreground">{news.date}</span>
                  </CardHeader>
                  <CardContent className="text-sm text-muted-foreground flex-1 p-1 -mt-4">
                    {news.text.slice(0, 120)}...
                  </CardContent>
                </Card>
              </DialogTrigger>

              <DialogContent showCloseButton={false} className="sm:max-w-lg max-h-[80vh] overflow-y-auto top-1/2 -translate-y-1/2">
                {news.image && <img src={news.image} alt={news.title} className="w-full h-48 object-cover mb-2" />}
                <DialogClose asChild>
                  <Button className="absolute top-2 right-2 z-20" variant="ghost" size="icon">
                    <X className="h-5 w-5" />
                  </Button>
                </DialogClose>
                <DialogHeader className="mt-2 mx-2">
                  <DialogTitle>{news.title}</DialogTitle>
                </DialogHeader>
                <div className="p-2 text-sm text-muted-foreground">
                  {news.text}
                </div>
              </DialogContent>
            </Dialog>
          ))}
        </div>
      </section>
    </div>
  );
}