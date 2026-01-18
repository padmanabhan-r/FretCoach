import { Music, Zap, BarChart3, Target } from "lucide-react";

const steps = [
  {
    icon: Music,
    title: "Play Your Guitar",
    description: "Connect via USB audio interface (desktop) or directly to the portable pedal. Just play naturally.",
    color: "from-chart-1 to-chart-2",
  },
  {
    icon: Zap,
    title: "Real-time Analysis",
    description: "FretCoach evaluates pitch accuracy, scale conformity, timing stability, and note transitions instantly.",
    color: "from-chart-2 to-chart-3",
  },
  {
    icon: BarChart3,
    title: "Visual Feedback",
    description: "Ambient lighting cues act as subconscious training signals, helping your brain adapt and self-correct.",
    color: "from-chart-3 to-chart-4",
  },
  {
    icon: Target,
    title: "Adaptive Coaching",
    description: "AI synthesizes performance metrics over time, identifies bottlenecks, and adapts your training strategy.",
    color: "from-chart-4 to-chart-1",
  },
];

const HowItWorksSection = () => {
  return (
    <section className="py-24 bg-background" id="how-it-works">
      <div className="container px-4 md:px-6">
        {/* Section Header */}
        <div className="text-center space-y-4 mb-16">
          <h2 className="text-3xl md:text-4xl font-bold">
            How It <span className="text-primary">Works</span>
          </h2>
          <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
            A simple four-step loop that transforms your practice into guided learning.
          </p>
        </div>

        {/* Steps */}
        <div className="relative">
          {/* Connection line */}
          <div className="absolute top-1/2 left-0 right-0 h-0.5 bg-gradient-to-r from-chart-1 via-chart-3 to-chart-1 hidden lg:block" />
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {steps.map((step, index) => (
              <div key={index} className="relative group">
                {/* Step number */}
                <div className="absolute -top-3 -left-3 h-8 w-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-bold text-sm z-10">
                  {index + 1}
                </div>
                
                {/* Card */}
                <div className="p-6 rounded-xl bg-card border border-border hover:border-primary/50 transition-all duration-300 hover:shadow-lg h-full">
                  {/* Icon */}
                  <div className={`h-16 w-16 rounded-xl bg-gradient-to-br ${step.color} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300`}>
                    <step.icon className="h-8 w-8 text-foreground" />
                  </div>
                  
                  <h3 className="text-xl font-semibold mb-2">{step.title}</h3>
                  <p className="text-muted-foreground">{step.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

export default HowItWorksSection;
