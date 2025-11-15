import { Hero } from "../components/Hero";
import { AIFeatures } from "../components/AIFeatures";
import { FeaturedCompanies } from "../components/FeaturedCompanies";
import { AllCompanies } from "../components/AllCompanies";
import { Header } from "../components/Header";

export default function Home() {
  return (
    <div className="min-h-screen bg-white">
      <Header />
      <Hero />
      <AIFeatures />
      <FeaturedCompanies />
      <br />
      <br />
      <br />
      <AllCompanies />
    </div>
  );
}
