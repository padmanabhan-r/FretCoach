import { Mic, Piano, Drum, Guitar, Music, Cpu, Monitor, Zap, CheckCircle2, Circle, ArrowRight } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const roadmapItems = [
  {
    phase: "Current",
    title: "FretCoach MVP",
    subtitle: "Scales",
    description: "Master guitar scales with real-time audio analysis and ambient light feedback. Focus on building muscle memory through deliberate practice.",
    icon: Guitar,
    status: "active",
    features: ["Desktop and portable", "Adaptive AI coaching", "Real-time analysis", "Ambient light feedback", "Web support and performance analytics"],
    hardware: {
      title: "MVP Hardware",
      icon: Cpu,
      items: ["Raspberry Pi 5", "USB Audio Interface", "Tablet/Phone Screen"],
    },
  },
  {
    phase: "Next",
    title: "FretCoach Extended",
    subtitle: "Chords & Songs",
    description: "Expand beyond scales to chord progressions and full song practice with intelligent accompaniment and real-time guidance.",
    icon: Music,
    status: "planned",
    features: ["Chord recognition", "Song practice mode", "Backing track sync", "Progress through songs"],
    hardware: {
      title: "Standalone Pedal",
      icon: Monitor,
      items: ["IPS Display", "Physical Controls", "Built-in Unit"],
    },
  },
  {
    phase: "Future",
    title: "Coach Family",
    subtitle: "Multi-Instrument Platform",
    description: "Bringing the same powerful coaching experience to keyboards, vocals, and drums.",
    icon: Zap,
    status: "vision",
    products: [
      { name: "KeysCoach", icon: Piano, description: "Piano & keyboard training" },
      { name: "VocalCoach", icon: Mic, description: "Vocal pitch & breathing" },
      { name: "DrumCoach", icon: Drum, description: "Rhythm & pattern training" },
    ],
  },
];

const getStatusBadge = (status: string) => {
  switch (status) {
    case "active":
      return <Badge className="bg-green-500/20 text-green-400 border-green-500/30">Current Release (Feb 8th) - Commit To Change Hackathon</Badge>;
    case "planned":
      return <Badge className="bg-blue-500/20 text-blue-400 border-blue-500/30">Q3 2026</Badge>;
    case "vision":
      return <Badge className="bg-purple-500/20 text-purple-400 border-purple-500/30">Future Vision</Badge>;
    default:
      return null;
  }
};

const getStatusIcon = (status: string) => {
  switch (status) {
    case "active":
      return <CheckCircle2 className="h-6 w-6 text-green-500" />;
    default:
      return <Circle className="h-6 w-6 text-muted-foreground/50" />;
  }
};

const RoadmapSection = () => {
  return (
    <section className="py-24 bg-card/50" id="roadmap">
      <div className="container px-4 md:px-6">
        {/* Section Header */}
        <div className="text-center space-y-4 mb-16">
          <h2 className="text-3xl md:text-4xl font-bold">
            Product <span className="text-primary">Roadmap</span>
          </h2>
          <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
            FretCoach is part of the Coach family of products. Here's our vision for bringing
            AI-powered practice coaching to musicians everywhere.
          </p>
        </div>

        {/* Roadmap Timeline */}
        <div className="max-w-5xl mx-auto space-y-8">
          {roadmapItems.map((item, index) => (
            <div key={index} className="relative">
              {/* Timeline connector */}
              {index < roadmapItems.length - 1 && (
                <div className="absolute left-[23px] top-16 bottom-0 w-0.5 bg-gradient-to-b from-primary/50 to-transparent hidden md:block" />
              )}

              <Card className={`group hover:shadow-lg transition-all duration-300 bg-card border-border/50 ${
                item.status === "active" ? "border-primary/50 shadow-primary/10 shadow-lg" : ""
              }`}>
                <CardHeader>
                  <div className="flex items-start gap-4">
                    {/* Status indicator */}
                    <div className="hidden md:flex flex-col items-center">
                      {getStatusIcon(item.status)}
                    </div>

                    <div className="flex-1">
                      <div className="flex flex-wrap items-center gap-3 mb-2">
                        <span className="text-sm font-medium text-primary uppercase tracking-wider">
                          {item.phase}
                        </span>
                        {getStatusBadge(item.status)}
                      </div>

                      <div className="flex items-center gap-3 mb-2">
                        <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
                          <item.icon className="h-5 w-5 text-primary" />
                        </div>
                        <div>
                          <CardTitle className="text-xl">{item.title}</CardTitle>
                          <CardDescription className="text-sm">{item.subtitle}</CardDescription>
                        </div>
                      </div>

                      <p className="text-muted-foreground mt-3">{item.description}</p>
                    </div>
                  </div>
                </CardHeader>

                <CardContent>
                  {/* Offset to align with header content (accounting for status icon + gap on md) */}
                  <div className="md:ml-10">
                    {/* Features list for FretCoach phases */}
                    {item.features && (
                      <div className="grid md:grid-cols-2 gap-6">
                        {/* Software Features */}
                        <div>
                          <h4 className="text-sm font-medium mb-3 text-foreground">Features</h4>
                          <ul className="space-y-2">
                            {item.features.map((feature, i) => (
                              <li key={i} className="flex items-center gap-2 text-sm text-muted-foreground">
                                <ArrowRight className="h-3 w-3 text-primary flex-shrink-0" />
                                {feature}
                              </li>
                            ))}
                          </ul>
                        </div>

                        {/* Hardware */}
                        {item.hardware && (
                          <div className="md:border-l md:border-border/50 md:pl-6">
                            <div className="flex items-center gap-2 mb-3">
                              <item.hardware.icon className="h-4 w-4 text-primary" />
                              <h4 className="text-sm font-medium text-foreground">{item.hardware.title}</h4>
                            </div>
                            <ul className="space-y-2">
                              {item.hardware.items.map((hw, i) => (
                                <li key={i} className="flex items-center gap-2 text-sm text-muted-foreground">
                                  <ArrowRight className="h-3 w-3 text-primary flex-shrink-0" />
                                  {hw}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Future products grid */}
                    {item.products && (
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        {item.products.map((product, i) => (
                          <div
                            key={i}
                            className="p-4 rounded-lg bg-background/50 border border-border/50 hover:border-primary/30 transition-colors"
                          >
                            <div className="flex items-center gap-3 mb-2">
                              <div className="h-8 w-8 rounded-md bg-primary/10 flex items-center justify-center">
                                <product.icon className="h-4 w-4 text-primary" />
                              </div>
                              <span className="font-medium">{product.name}</span>
                            </div>
                            <p className="text-sm text-muted-foreground">{product.description}</p>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default RoadmapSection;
