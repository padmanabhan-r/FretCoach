import { useState } from "react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Guitar, ChevronDown, Check } from "lucide-react";

interface UserSwitcherProps {
  userId: string;
  onUserChange: (userId: string) => void;
  variant?: "navbar" | "header";
}

const users = [
  { id: "default_user", name: "Default User", badge: "FretCoach Premium" },
  { id: "test_user", name: "Test User", badge: "FretCoach Premium" },
];

const UserSwitcher = ({ userId, onUserChange, variant = "navbar" }: UserSwitcherProps) => {
  const [open, setOpen] = useState(false);
  const currentUser = users.find((u) => u.id === userId) || users[0];

  const isNavbar = variant === "navbar";

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <button className="flex items-center gap-2 hover:opacity-80 transition-opacity group">
          {isNavbar && (
            <div className="text-right hidden lg:block">
              <p className="text-sm font-medium">{currentUser.name}</p>
              <p className="text-xs text-muted-foreground">{currentUser.badge}</p>
            </div>
          )}
          <Avatar className={`border-2 border-primary/20 ${isNavbar ? "h-9 w-9" : "h-10 w-10"}`}>
            <AvatarImage src="" alt="FretCoach User" />
            <AvatarFallback className="bg-primary/10 text-primary">
              <Guitar className="h-4 w-4" />
            </AvatarFallback>
          </Avatar>
          <ChevronDown className="h-3 w-3 text-muted-foreground group-hover:text-foreground transition-colors" />
        </button>
      </PopoverTrigger>
      <PopoverContent className="w-64 p-2" align="end">
        <div className="space-y-1">
          <div className="px-2 py-1.5">
            <p className="text-xs font-medium text-muted-foreground">Switch User</p>
          </div>
          {users.map((user) => (
            <button
              key={user.id}
              onClick={() => {
                onUserChange(user.id);
                setOpen(false);
              }}
              className={`w-full flex items-center gap-3 px-2 py-2 rounded-md transition-colors ${
                userId === user.id
                  ? "bg-primary/10 text-foreground"
                  : "hover:bg-accent text-muted-foreground hover:text-foreground"
              }`}
            >
              <Avatar className="h-8 w-8 border-2 border-primary/20">
                <AvatarImage src="" alt={user.name} />
                <AvatarFallback className="bg-primary/10 text-primary text-xs">
                  <Guitar className="h-3 w-3" />
                </AvatarFallback>
              </Avatar>
              <div className="flex-1 text-left">
                <p className="text-sm font-medium">{user.name}</p>
                <p className="text-xs text-muted-foreground">{user.badge}</p>
              </div>
              {userId === user.id && <Check className="h-4 w-4 text-primary" />}
            </button>
          ))}
        </div>
      </PopoverContent>
    </Popover>
  );
};

export default UserSwitcher;
