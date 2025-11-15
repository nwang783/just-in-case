import { Button } from "./ui/button";

export function Header() {
  return (
    <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md">
      <div className="container mx-auto px-4 py-4">
        <div className="py-2 max-w-6xl mx-auto flex items-center justify-between border-gray-200 pb-4">
          <h1 className="text-indigo-600">ConsultPrep</h1>
          <div className="flex items-center gap-3">
            <Button variant="ghost" className="hidden sm:inline-flex">
              Sign In
            </Button>
            <Button>Get Started</Button>
          </div>
        </div>
      </div>
    </header>
  );
}