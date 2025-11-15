import { Button } from "./ui/button";
import { ArrowRight } from "lucide-react";

export function Hero() {
  return (
    <section className="from-indigo-50 to-white py-8 md:py-12">
      <div className="container mx-auto px-4">
        <div className="max-w-3xl mx-auto text-center">
          <h1 className="text-4xl md:text-5xl mb-4">
            Ace Your <span className="text-indigo-600">Consulting Interview</span>
          </h1>
        </div>
      </div>
    </section>
  );
}