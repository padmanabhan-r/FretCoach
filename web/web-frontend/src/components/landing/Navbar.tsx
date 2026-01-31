import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Menu, X, Guitar, BarChart3 } from "lucide-react";
import { Link } from "react-router-dom";
import UserSwitcher from "@/components/UserSwitcher";

const navLinks = [
  { href: "#features", label: "Features" },
  { href: "#how-it-works", label: "How It Works" },
  { href: "#ecosystem", label: "FretCoach Ecosystem" },
  { href: "#roadmap", label: "Roadmap" },
];

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [userId, setUserId] = useState<string>(() => {
    return localStorage.getItem('fretcoach-user-id') || 'default_user';
  });

  // Update localStorage when userId changes
  useEffect(() => {
    localStorage.setItem('fretcoach-user-id', userId);
  }, [userId]);

  const handleNavClick = (e: React.MouseEvent<HTMLAnchorElement>, href: string) => {
    e.preventDefault();
    const id = href.replace('#', '');
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    setIsOpen(false);
  };

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-background/80 backdrop-blur-md border-b border-border/50">
      <div className="container px-4 md:px-6">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 flex-shrink-0">
            <div className="p-2 rounded-lg bg-primary/10">
              <Guitar className="h-6 w-6 text-primary" />
            </div>
            <span className="text-xl font-bold">FretCoach</span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden lg:flex items-center gap-6 absolute left-1/2 -translate-x-1/2">
            {navLinks.map((link) => (
              <a
                key={link.href}
                href={link.href}
                onClick={(e) => handleNavClick(e, link.href)}
                className="text-muted-foreground hover:text-foreground transition-all duration-200 whitespace-nowrap text-xs lg:text-sm px-2 py-1 hover:scale-110"
              >
                {link.label}
              </a>
            ))}
          </div>

          {/* Desktop CTA */}
          <div className="hidden md:flex items-center gap-3 flex-shrink-0">
            <Link to="/dashboard">
              <Button variant="default" className="gap-2" size="sm">
                <BarChart3 className="h-4 w-4" />
                Dashboard
              </Button>
            </Link>
            <div className="pl-3 border-l border-border">
              <UserSwitcher userId={userId} onUserChange={setUserId} variant="navbar" />
            </div>
          </div>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden p-2"
            onClick={() => setIsOpen(!isOpen)}
            aria-label="Toggle menu"
          >
            {isOpen ? (
              <X className="h-6 w-6" />
            ) : (
              <Menu className="h-6 w-6" />
            )}
          </button>
        </div>

        {/* Mobile Navigation */}
        {isOpen && (
          <div className="md:hidden py-4 space-y-4">
            {navLinks.map((link) => (
              <a
                key={link.href}
                href={link.href}
                onClick={(e) => handleNavClick(e, link.href)}
                className="block text-muted-foreground hover:text-foreground transition-colors py-2"
              >
                {link.label}
              </a>
            ))}
            <div className="pt-4 space-y-3">
              <Link to="/dashboard" className="block">
                <Button variant="default" className="w-full gap-2">
                  <BarChart3 className="h-4 w-4" />
                  Dashboard
                </Button>
              </Link>
              <div className="flex justify-center p-2 rounded-lg bg-card/50 border border-border">
                <UserSwitcher userId={userId} onUserChange={setUserId} variant="header" />
              </div>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
