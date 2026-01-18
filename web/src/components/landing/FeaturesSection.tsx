import { Lightbulb, Cpu, Brain, Sparkles, Layers, Activity, Smartphone, BarChart3 } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const features = [
  {
    icon: Lightbulb,
    title: "Real-time Visual Feedback",
    description: "Instant ambient lighting cues guide your playing with physical, tangible feedback that your brain naturally responds to, translating performance quality into immediate visual signals.",
  },
  {
    icon: Cpu,
    title: "Edge-first Architecture",
    description: "All real-time audio analysis runs deterministically on a Raspberry Pi — no cloud latency, just pure speed.",
  },
  {
    icon: Brain,
    title: "Adaptive AI Learning",
    description: "LLM-powered coaching synthesizes your performance metrics and adapts future training strategies.",
  },
  {
    icon: Sparkles,
    title: "Intelligent Analysis",
    description: "Evaluates pitch accuracy, scale conformity, timing stability, and note transitions in real-time.",
  },
  {
    icon: Layers,
    title: "Extensible Design",
    description: "Architecture designed to generalize to other instruments and vocal training that benefit from adaptive feedback.",
  },
  {
    icon: Activity,
    title: "Digital Signal Processing",
    description: "Advanced DSP algorithms extract musical features and analyze acoustic characteristics with precision.",
  },
  {
    icon: Smartphone,
    title: "Cross-Platform Support",
    description: "Run on portable Edge devices like Raspberry Pi or use the Desktop app — choose your learning environment.",
  },
  {
    icon: BarChart3,
    title: "Cloud-Based Analytics",
    description: "Optional cloud sync collects performance statistics regularly for long-term progress tracking and insights.",
  },
];

const FeaturesSection = () => {
  return (
    <section className="py-24 bg-card/50" id="features">
      <div className="container px-4 md:px-6">
        {/* Section Header */}
        <div className="text-center space-y-4 mb-16">
          <h2 className="text-3xl md:text-4xl font-bold">
            Key <span className="text-primary">Features</span>
          </h2>
          <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
            FretCoach combines real-time audio processing with cutting-edge AI to create 
            a learning experience that adapts to you.
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <Card 
              key={index} 
              className="group hover:shadow-lg transition-all duration-300 hover:-translate-y-1 bg-card border-border/50"
            >
              <CardHeader>
                <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4 group-hover:bg-primary/20 transition-colors">
                  <feature.icon className="h-6 w-6 text-primary" />
                </div>
                <CardTitle className="text-xl">{feature.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-base">
                  {feature.description}
                </CardDescription>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
};

export default FeaturesSection;
