import { Mic, Piano, Drum, Sparkles } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const futureProducts = [
  {
    icon: Mic,
    name: "VocalCoach",
    description: "AI-powered vocal training with real-time pitch correction, breathing analysis, and adaptive ambient feedback for singers.",
    status: "Planned",
  },
  {
    icon: Piano,
    name: "KeysCoach",
    description: "Intelligent piano and keyboard trainer with chord recognition, timing analysis, and progressive learning paths.",
    status: "Planned",
  },
  {
    icon: Drum,
    name: "DrumCoach",
    description: "Rhythmic training assistant for drummers with tempo tracking, pattern recognition, and dynamic visual feedback.",
    status: "Planned",
  },
];

const OtherProductsSection = () => {
  return (
    <section className="py-24 bg-card/50" id="future-products">
      <div className="container px-4 md:px-6">
        {/* Section Header */}
        <div className="text-center space-y-4 mb-16">
          <h2 className="text-3xl md:text-4xl font-bold">
            Future <span className="text-primary">Products</span>
          </h2>
          <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
            The FretCoach architecture is designed to generalize to other instruments and vocal training. 
            Here's what's coming next in the Coach family.
          </p>
        </div>

        {/* Products Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto mb-12">
          {futureProducts.map((product, index) => (
            <Card 
              key={index} 
              className="group hover:shadow-lg transition-all duration-300 hover:-translate-y-1 bg-card border-border/50 relative overflow-hidden"
            >
              {/* Coming Soon Badge */}
              <div className="absolute top-4 right-4">
                <span className="text-xs px-3 py-1 rounded-full bg-accent/20 text-accent border border-accent/30">
                  {product.status}
                </span>
              </div>
              
              <CardHeader>
                <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4 group-hover:bg-primary/20 transition-colors">
                  <product.icon className="h-6 w-6 text-primary" />
                </div>
                <CardTitle className="text-xl">{product.name}</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-base">
                  {product.description}
                </CardDescription>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Expandable Architecture Note */}
        <div className="max-w-3xl mx-auto">
          <Card className="bg-gradient-to-br from-primary/5 to-accent/5 border-primary/20">
            <CardHeader>
              <div className="flex items-center gap-3">
                <Sparkles className="h-6 w-6 text-primary" />
                <CardTitle className="text-lg">Expandable by Design</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">
                FretCoach's core architecture—real-time audio analysis, adaptive AI coaching, and embodied 
                ambient feedback—can be adapted to any instrument or vocal training scenario. Each new product 
                in the Coach family shares the same powerful foundation while offering specialized features 
                tailored to its specific instrument.
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </section>
  );
};

export default OtherProductsSection;
