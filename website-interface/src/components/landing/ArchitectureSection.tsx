import { Monitor, Cpu, Globe, Database, Lightbulb, Usb, ArrowDownUp } from "lucide-react";
import pedalImage from "@/assets/fretcoach-pedal.jpeg";
import ambientLightImage from "@/assets/ambient-light.jpg";
import desktopAppImage from "@/assets/desktop-app.jpg";
import webDashboardImage from "@/assets/web-dashboard.jpg";

const ArchitectureSection = () => {
  return (
    <section className="py-24 bg-background" id="architecture">
      <div className="container px-4 md:px-6">
        {/* Section Header */}
        <div className="text-center space-y-4 mb-16">
          <h2 className="text-3xl md:text-4xl font-bold">
            The FretCoach <span className="text-primary">Ecosystem</span>
          </h2>
          <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
            Three AI-powered components connected to a central database, creating a unified learning ecosystem.
          </p>
        </div>

        {/* Architecture Diagram */}
        <div className="max-w-6xl mx-auto">
          {/* Top: Desktop & Portable with Adaptive Ambient Light */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-stretch">
            {/* Desktop App */}
            <div className="rounded-xl border-2 border-border bg-card hover:border-primary/50 transition-all duration-300 flex flex-col">
              <div className="aspect-video overflow-hidden rounded-t-xl flex-shrink-0 max-h-48">
                <img 
                  src={desktopAppImage} 
                  alt="FretCoach Desktop App" 
                  className="w-full h-full object-cover"
                />
              </div>
              <div className="p-4 sm:p-6 flex-1 flex flex-col">
                <div className="flex items-center gap-3 mb-4">
                  <div className="p-2 sm:p-3 rounded-lg bg-primary/10 flex-shrink-0">
                    <Monitor className="h-5 w-5 sm:h-6 sm:w-6 text-primary" />
                  </div>
                  <div className="min-w-0">
                    <h3 className="text-base sm:text-lg font-bold">Desktop App</h3>
                    <span className="text-xs px-2 py-1 rounded-full bg-accent text-accent-foreground whitespace-nowrap">Beta</span>
                  </div>
                </div>
                <p className="text-xs sm:text-sm text-muted-foreground mb-4">
                  Your personal guitar trainer with advanced visualization, AI coaching, and ambient lighting control.
                </p>
                <div className="space-y-2 text-xs sm:text-sm text-muted-foreground mb-4 flex-1">
                  <p>• Real-time analysis & feedback</p>
                  <p>• Professional audio interface</p>
                  <p>• Rich UI for detailed metrics</p>
                  <p>• AI-powered adaptive learning</p>
                </div>
                <div className="flex items-center gap-2 text-xs text-muted-foreground pt-3 border-t border-border">
                  <Usb className="h-4 w-4 text-primary flex-shrink-0" />
                  <span className="truncate">🎸 → USB Audio Interface</span>
                </div>
              </div>
            </div>

            {/* Adaptive Ambient Light - Center */}
            <div className="flex flex-col items-center justify-center">
              <div className="rounded-2xl border-2 border-border bg-gradient-to-br from-primary/10 to-accent/10 overflow-hidden w-full max-w-sm mx-auto">
                <div className="aspect-square overflow-hidden">
                  <img 
                    src={ambientLightImage} 
                    alt="Adaptive Ambient Light" 
                    className="w-full h-full object-cover"
                  />
                </div>
                <div className="p-6 text-center">
                  <h3 className="text-lg font-bold mb-2">Adaptive Ambient Light</h3>
                  <p className="text-sm text-muted-foreground">
                    Visual feedback synchronized with performance for embodied, intelligent learning
                  </p>
                </div>
              </div>
            </div>

            {/* Portable Pedal */}
            <div className="rounded-xl border-2 border-border bg-card hover:border-primary/50 transition-all duration-300 flex flex-col">
              <div className="aspect-video overflow-hidden rounded-t-xl flex-shrink-0 max-h-48">
                <img 
                  src={pedalImage} 
                  alt="FretCoach Portable Pedal" 
                  className="w-full h-full object-cover"
                />
              </div>
              <div className="p-4 sm:p-6 flex-1 flex flex-col">
                <div className="flex items-center gap-3 mb-4">
                  <div className="p-2 sm:p-3 rounded-lg bg-primary/10 flex-shrink-0">
                    <Cpu className="h-5 w-5 sm:h-6 sm:w-6 text-primary" />
                  </div>
                  <div className="min-w-0">
                    <h3 className="text-base sm:text-lg font-bold">Portable Pedal</h3>
                    <span className="text-xs px-2 py-1 rounded-full bg-accent text-accent-foreground whitespace-nowrap">Prototyping</span>
                  </div>
                </div>
                <p className="text-xs sm:text-sm text-muted-foreground mb-4">
                  Standalone Raspberry Pi pedal with real-time processing and AI-powered feedback.
                </p>
                <div className="space-y-2 text-xs sm:text-sm text-muted-foreground mb-4 flex-1">
                  <p>• Portable & practice-ready</p>
                  <p>• Integrated ADC for direct input</p>
                  <p>• On-device AI analysis</p>
                  <p>• Cloud connectivity</p>
                </div>
                <div className="flex items-center gap-2 text-xs text-muted-foreground pt-3 border-t border-border">
                  <span className="truncate">🎸 → Direct Input</span>
                </div>
              </div>
            </div>
          </div>

          {/* Bottom: Web Interface */}
          <div className="flex justify-center mt-8">
            <div className="rounded-xl border-2 border-border bg-gradient-to-br from-primary/5 to-accent/5 overflow-hidden max-w-lg w-full">
              <div className="aspect-video overflow-hidden">
                <img 
                  src={webDashboardImage} 
                  alt="FretCoach Web Dashboard" 
                  className="w-full h-full object-cover"
                />
              </div>
              <div className="p-6">
                <div className="flex items-center gap-4 mb-3">
                  <div className="p-3 rounded-lg bg-primary/10 border border-primary/20">
                    <Globe className="h-6 w-6 text-primary" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-xl font-bold">Web Dashboard</h3>
                    <p className="text-sm text-muted-foreground">Analytics & Progress Tracking</p>
                  </div>
                </div>
                <div className="text-sm text-muted-foreground space-y-1">
                  <p>• Historical performance tracking</p>
                  <p>• AI-generated insights</p>
                  <p>• Cross-device synchronization</p>
                </div>
              </div>
            </div>
          </div>
          <div className="mt-12 text-center max-w-3xl mx-auto">
            <p className="text-muted-foreground italic">
              All three components leverage AI integration and communicate with a central database, 
              creating a unified learning ecosystem that adapts to your progress whether you're 
              practicing at home or on the go.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default ArchitectureSection;
