import { Moon, Sun } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { useTheme } from "@/components/theme-provider"
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"


export function ModeToggle() {
  const { setTheme, theme } = useTheme()

  return (
    <>
      <DropdownMenu>
        <DropdownMenuTrigger asChild className="hidden md:flex">
          <Button size="icon-sm" variant="ghost">
            <Sun className="h-[1.2rem] w-[1.2rem] scale-100 rotate-0 transition-all dark:scale-0 dark:-rotate-90" />
            <Moon className="absolute h-[1.2rem] w-[1.2rem] scale-0 rotate-90 transition-all dark:scale-100 dark:rotate-0" />
            <span className="sr-only">Toggle theme</span>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          <DropdownMenuItem onClick={() => setTheme("light")}>
            Светлая
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => setTheme("dark")}>
            Тёмная
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => setTheme("system")}>
            Системная
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>

      <Dialog>
        <DialogTrigger asChild className="md:hidden">
          <Button variant="outline">Сменить тему</Button>
        </DialogTrigger>
        <DialogContent className="max-w-sm" showCloseButton={false}>
          <DialogHeader>
            <DialogTitle>Выбор темы</DialogTitle>
          </DialogHeader>
          <div className="flex flex-col gap-2">
            <Button
              onClick={() => setTheme("light")}
              variant={
                theme == "light"
                  ? "default"
                  : "outline"}
            >Светлая</Button>
            <Button
              onClick={() => setTheme("dark")}
              variant={
                theme == "dark"
                  ? "default"
                  : "outline"}
            >Тёмная</Button>
            <Button
              onClick={() => setTheme("system")}
              variant={
                theme == "system"
                  ? "default"
                  : "outline"}
            >Системная</Button>
          </div>
          <DialogFooter>
            <DialogClose asChild>
              <Button type="button" variant="outline" className="mt-5">Готово</Button>
            </DialogClose>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}