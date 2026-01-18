import { Button } from "@/components/ui/button";
import { ArrowRight, Play } from "lucide-react";
import heroImage from "@/assets/hero-guitar.jpg";

const HeroSection = () => {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Background Image */}
      <div 
        className="absolute inset-0 bg-cover bg-center bg-no-repeat"
        style={{ backgroundImage: `url(${heroImage})` }}
      >
        <div className="absolute inset-0 bg-gradient-to-r from-background/95 via-background/80 to-background/40" />
        <div className="absolute inset-0 bg-gradient-to-t from-background via-transparent to-transparent" />
      </div>
      
      {/* Content */}
      <div className="container relative z-10 px-4 md:px-6 py-20">
        <div className="max-w-3xl space-y-8">
          {/* Badge */}
          <div className="inline-flex items-center gap-3 px-6 py-3 rounded-full bg-primary/10 border border-primary/20 text-primary">
            <span className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-primary"></span>
            </span>
            <span className="text-base sm:text-lg font-medium">AI-Powered Guitar Training</span>
          </div>

          {/* Main Heading */}
          <h1 className="text-4xl md:text-5xl lg:text-7xl font-bold tracking-tight">
            Train Your Brain,{" "}
            <span className="text-primary">Not Your Tone</span>
          </h1>
          
          {/* Description */}
          <p className="text-lg text-foreground/80 max-w-xl">
            Transform unstructured practice into a guided learning loop with real-time visual feedback, 
            adaptive AI coaching, and ambient lighting cues that help you self-correct as you play.
          </p>
          
          {/* Stats */}
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 sm:gap-8 pt-8 border-t border-border/50 max-w-lg">
            <div className="min-w-0">
              <div className="text-2xl sm:text-3xl font-bold text-primary truncate">Real-time</div>
              <div className="text-xs sm:text-sm text-muted-foreground">Visual Feedback</div>
            </div>
            <div className="min-w-0">
              <div className="text-2xl sm:text-3xl font-bold text-primary truncate">Edge-first</div>
              <div className="text-xs sm:text-sm text-muted-foreground">& Desktop</div>
            </div>
            <div className="min-w-0 col-span-2 sm:col-span-1">
              <div className="text-2xl sm:text-3xl font-bold text-primary truncate">Adaptive</div>
              <div className="text-xs sm:text-sm text-muted-foreground">AI Coaching</div>
            </div>
          </div>
        </div>
      </div>

      {/* Scroll indicator */}
      <div className="absolute bottom-8 left-1/2 -translate-x-1/2 animate-bounce">
        <div className="w-6 h-10 rounded-full border-2 border-primary/50 flex items-start justify-center p-2">
          <div className="w-1 h-2 bg-primary rounded-full animate-pulse" />
        </div>
      </div>
    </section>
  );
};

export default HeroSection;
