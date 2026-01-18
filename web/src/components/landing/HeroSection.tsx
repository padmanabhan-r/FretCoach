import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";
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
            Practice Until You{" "}
            <span className="text-primary">Can't Get It Wrong</span>
          </h1>

          {/* Description */}
          <p className="text-lg text-foreground/80 max-w-xl">
            FretCoach listens to every note, flags mistakes instantly, and delivers feedback through
            screen, voice, and ambient lighting. Stop reinforcing bad habits. Make every minute of practice count.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-wrap gap-4 pt-4">
            <Link to="/dashboard">
              <Button variant="hero" size="xl">
                View Dashboard
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
            <a href="#how-it-works">
              <Button variant="outline" size="xl">
                See How It Works
              </Button>
            </a>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 sm:gap-8 pt-8 border-t border-border/50 max-w-lg">
            <div className="min-w-0">
              <div className="text-2xl sm:text-3xl font-bold text-primary truncate">Real-time</div>
              <div className="text-xs sm:text-sm text-muted-foreground">Audio Analysis</div>
            </div>
            <div className="min-w-0">
              <div className="text-2xl sm:text-3xl font-bold text-primary truncate">Instant</div>
              <div className="text-xs sm:text-sm text-muted-foreground">Feedback</div>
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
