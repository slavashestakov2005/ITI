import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import Index from './components/pages/Index.tsx'
import Navigation from './components/navigation.tsx';

export default function App() {
  return (
    <BrowserRouter>
      <Navigation />
      <Routes>
        <Route path="/" element={<Index />} />
      </Routes>
    </BrowserRouter>
  );
}