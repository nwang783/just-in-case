import { Button } from "./ui/button";
import { ArrowRight } from "lucide-react";

const companies = [
  { name: "PwC Strategy&", cases: 89 },
  { name: "EY-Parthenon", cases: 76 },
  { name: "KPMG Consulting", cases: 72 },
  { name: "Accenture Strategy", cases: 94 },
  { name: "Oliver Wyman", cases: 68 },
  { name: "A.T. Kearney", cases: 63 },
  { name: "Roland Berger", cases: 54 },
  { name: "L.E.K. Consulting", cases: 58 },
  { name: "Simon-Kucher", cases: 47 },
  { name: "Kearney", cases: 61 },
  { name: "Monitor Deloitte", cases: 52 },
  { name: "ZS Associates", cases: 43 },
];

export function AllCompanies() {
  return (
    <section className="py-12 bg-gray-50">
      <div className="container mx-auto px-4">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-8">
            <h2 className="text-3xl md:text-4xl mb-2">
              More Consulting Firms
            </h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {companies.map((company) => (
              <button
                key={company.name}
                className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:border-indigo-600 hover:bg-white transition-all group text-left bg-white"
              >
                <div>
                  <p className="text-gray-900 group-hover:text-indigo-600">
                    {company.name}
                  </p>
                  <p className="text-sm text-gray-500">{company.cases} cases</p>
                </div>
                <ArrowRight className="size-5 text-gray-400 group-hover:text-indigo-600 transition-colors" />
              </button>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}