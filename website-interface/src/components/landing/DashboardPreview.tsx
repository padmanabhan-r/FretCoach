import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowRight, TrendingUp, Clock, Music2, Target } from "lucide-react";
import { Link } from "react-router-dom";

const mockStats = [
  { label: "In-Scale Ratio", value: "87%", icon: Music2, trend: "+5%" },
  { label: "Timing Stability", value: "92%", icon: Clock, trend: "+3%" },
  { label: "Flow State", value: "78%", icon: Target, trend: "+12%" },
  { label: "Sessions This Week", value: "12", icon: TrendingUp, trend: "+4" },
];

const DashboardPreview = () => {
  return (
    <section className="py-24 bg-background" id="dashboard">
      <div className="container px-4 md:px-6">
        {/* Section Header */}
        <div className="text-center space-y-4 mb-16">
          <h2 className="text-3xl md:text-4xl font-bold">
            Track Your <span className="text-primary">Progress</span>
          </h2>
          <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
            Detailed analytics and AI-generated insights help you understand your growth and optimize practice.
          </p>
        </div>

        {/* Preview Cards */}
        <div className="max-w-5xl mx-auto">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            {mockStats.map((stat, index) => (
              <Card key={index} className="bg-card border-border/50">
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <stat.icon className="h-5 w-5 text-primary" />
                    <span className="text-xs text-primary font-medium">{stat.trend}</span>
                  </div>
                </CardHeader>
                <CardContent>
                  <CardTitle className="text-2xl md:text-3xl font-bold">{stat.value}</CardTitle>
                  <p className="text-sm text-muted-foreground">{stat.label}</p>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Chart placeholder */}
          <Card className="bg-card border-border/50 overflow-hidden">
            <CardHeader>
              <CardTitle>Performance Over Time</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-64 flex items-end gap-2 p-4">
                {[40, 55, 45, 60, 75, 65, 80, 70, 85, 78, 90, 87].map((height, index) => (
                  <div key={index} className="flex-1 flex flex-col items-center gap-1">
                    <div 
                      className="w-full rounded-t-sm bg-gradient-to-t from-primary/60 to-primary transition-all duration-300 hover:from-primary/80 hover:to-primary"
                      style={{ height: `${height}%` }}
                    />
                    <span className="text-xs text-muted-foreground">
                      {['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D'][index]}
                    </span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* CTA */}
          <div className="text-center mt-12">
            <Link to="/dashboard">
              <Button variant="hero" size="xl">
                View Full Dashboard
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
};

export default DashboardPreview;
