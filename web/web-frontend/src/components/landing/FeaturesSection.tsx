import { Activity, MessageSquare, Lightbulb, BarChart3, Brain, Globe, Monitor, Zap } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const features = [
  {
    icon: Activity,
    title: "Real-time Audio Analysis",
    description: "Every note is evaluated across four dimensions: pitch accuracy, scale conformity, timing stability, and noise control. Know instantly if you're playing the right notes, at the right time, cleanly.",
  },
  {
    icon: MessageSquare,
    title: "Live AI Coach",
    description: "Receive preventive guidance during practice like \"Your timing is drifting—lock in with the beat\" or \"Pitch is solid, watch the string noise.\" Correct technique as you play.",
  },
  {
    icon: Lightbulb,
    title: "Ambient Lighting Feedback",
    description: "Smart bulbs shift from red to green based on your performance. Color changes are processed faster than conscious thought, training your muscle memory subconsciously.",
  },
  {
    icon: BarChart3,
    title: "Session Logging",
    description: "Every session is recorded: notes played, accuracy, duration, and trends. See exactly how you're improving over time with real data, not guesswork.",
  },
  {
    icon: Brain,
    title: "AI Practice Planning",
    description: "The AI analyzes your history and recommends preventive practice routines. No more wondering what to work on—get personalized plans that prevent technique gaps from forming.",
  },
  {
    icon: Globe,
    title: "FretCoach Hub",
    description: "Review sessions from anywhere, chat with the AI coach about your progress, and generate practice plans that sync across all your devices.",
  },
  {
    icon: Monitor,
    title: "FretCoach Studio",
    description: "The primary training environment with on-screen metrics, live AI coaching, and ambient lighting control. Connect via USB audio interface and start practicing.",
  },
  {
    icon: Zap,
    title: "FretCoach Portable",
    description: "A Raspberry Pi-powered device running the same analysis engine. Practice anywhere without a laptop—your progress syncs automatically when online.",
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
            FretCoach does not correct—it prevents. Instant feedback during practice prevents bad habits
            from forming, guiding you toward correct technique from day one.
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
