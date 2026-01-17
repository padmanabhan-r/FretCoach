import Navbar from "@/components/landing/Navbar";
import HeroSection from "@/components/landing/HeroSection";
import FeaturesSection from "@/components/landing/FeaturesSection";
import HowItWorksSection from "@/components/landing/HowItWorksSection";
import ArchitectureSection from "@/components/landing/ArchitectureSection";
import OtherProductsSection from "@/components/landing/OtherProductsSection";
import Footer from "@/components/landing/Footer";

const Index = () => {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <main>
        <HeroSection />
        <FeaturesSection />
        <HowItWorksSection />
        <ArchitectureSection />
        <OtherProductsSection />
      </main>
      <Footer />
    </div>
  );
};

export default Index;
