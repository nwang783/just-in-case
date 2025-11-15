import { Mic, BarChart3 } from "lucide-react";

const features = [
  {
    icon: Mic,
    title: "Voice-to-Voice AI Interviews",
    description: "Practice with realistic AI conducting full case and behavioral interviews",
  },
  {
    icon: BarChart3,
    title: "Detailed Performance Analysis",
    description: "Get feedback on structure, clarity, problem-solving, executive presence, and more",
  },
];

export function AIFeatures() {
  return (
    <section className="py-8 bg-white border-gray-200">
      <div className="container mx-auto px-4">
        <div className="max-w-4xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {features.map((feature) => {
              const Icon = feature.icon;
              return (
                <div key={feature.title} className="flex items-start gap-3">
                  <div className="size-10 bg-indigo-100 rounded-full flex items-center justify-center flex-shrink-0">
                    <Icon className="size-5 text-indigo-600" />
                  </div>
                  <div>
                    <h3 className="mb-1">{feature.title}</h3>
                    <p className="text-sm text-gray-600">{feature.description}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
      <br />
      <br />
    </section>
  );
}