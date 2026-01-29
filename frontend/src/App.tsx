import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Index from './components/pages/Index.tsx'
import Navigation from './components/base/navigation.tsx';
import { ThemeProvider } from "@/components/theme-provider"
import { Footer } from './components/base/footer.tsx';


export default function App() {
  return (
    <BrowserRouter>
      <ThemeProvider defaultTheme="system" storageKey="vite-ui-theme">
      <Navigation />
      <Routes>
        <Route path="/" element={<Index />} />
      </Routes>
      </ThemeProvider>
      <Footer />
    </BrowserRouter>
  );
}