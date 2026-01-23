import { Guitar, Activity, Lightbulb, Brain } from "lucide-react";

const steps = [
  {
    icon: Guitar,
    title: "Connect & Play",
    description: "Plug your guitar into a USB audio interface (desktop) or the portable Raspberry Pi device. Choose a scale and start playing naturally.",
    color: "from-chart-1 to-chart-2",
  },
  {
    icon: Activity,
    title: "Real-time Analysis",
    description: "FretCoach's audio engine evaluates your playing across four metrics: pitch accuracy, scale conformity, timing stability, and noise control.",
    color: "from-chart-2 to-chart-3",
  },
  {
    icon: Lightbulb,
    title: "Multi-Sensory Feedback",
    description: "Get instant feedback through on-screen metrics, live AI coaching commentary, and ambient lighting that shifts from red to green based on performance.",
    color: "from-chart-3 to-chart-4",
  },
  {
    icon: Brain,
    title: "Track & Improve",
    description: "Every session is logged. The AI coach analyzes your progress over time, identifies patterns, and generates personalized practice plans.",
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
            A continuous learning loop that transforms unstructured practice into guided improvement.
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

        {/* Metrics callout */}
        <div className="mt-16 max-w-4xl mx-auto">
          <div className="p-6 rounded-xl bg-card/50 border border-border/50">
            <h4 className="text-sm font-medium text-primary uppercase tracking-wider mb-4 text-center">Performance Metrics Analyzed</h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
              <div className="p-3 rounded-lg bg-background/50">
                <p className="font-medium">Pitch Accuracy</p>
                <p className="text-xs text-muted-foreground">Note correctness</p>
              </div>
              <div className="p-3 rounded-lg bg-background/50">
                <p className="font-medium">Scale Conformity</p>
                <p className="text-xs text-muted-foreground">Scale adherence</p>
              </div>
              <div className="p-3 rounded-lg bg-background/50">
                <p className="font-medium">Timing Stability</p>
                <p className="text-xs text-muted-foreground">Rhythmic precision</p>
              </div>
              <div className="p-3 rounded-lg bg-background/50">
                <p className="font-medium">Noise Control</p>
                <p className="text-xs text-muted-foreground">Playing clarity</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default HowItWorksSection;
