import React, { useState, useRef, useEffect } from 'react';

const UserSwitcher = ({ userId, onUserChange }) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  const users = [
    { id: 'default_user', name: 'Default User', badge: 'FretCoach Premium' },
    { id: 'test_user', name: 'Test User', badge: 'FretCoach Premium' },
  ];

  const currentUser = users.find((u) => u.id === userId) || users[0];

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  return (
    <div className="absolute top-4 right-4 z-50" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 rounded-lg bg-card/50 backdrop-blur-sm border border-border hover:bg-card/70 transition-all group"
      >
        <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center border-2 border-primary/20">
          <span className="text-xs font-semibold text-primary">
            {currentUser.name.split(' ').map(n => n[0]).join('')}
          </span>
        </div>
        <div className="text-left hidden sm:block">
          <p className="text-xs font-medium text-foreground leading-tight">{currentUser.name}</p>
          <p className="text-[10px] text-muted-foreground leading-tight">{currentUser.badge}</p>
        </div>
        <svg
          className={`w-4 h-4 text-muted-foreground transition-transform ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-64 rounded-lg bg-card border border-border shadow-xl overflow-hidden">
          <div className="px-3 py-2 bg-card/50 border-b border-border">
            <p className="text-xs font-medium text-muted-foreground">Switch User</p>
          </div>
          <div className="p-2 space-y-1">
            {users.map((user) => (
              <button
                key={user.id}
                onClick={() => {
                  onUserChange(user.id);
                  setIsOpen(false);
                }}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-md transition-all ${
                  userId === user.id
                    ? 'bg-primary/10 border border-primary/30'
                    : 'hover:bg-card/50 border border-transparent'
                }`}
              >
                <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center border-2 border-primary/20">
                  <span className="text-xs font-semibold text-primary">
                    {user.name.split(' ').map(n => n[0]).join('')}
                  </span>
                </div>
                <div className="flex-1 text-left">
                  <p className="text-sm font-medium text-foreground">{user.name}</p>
                  <p className="text-xs text-muted-foreground">{user.badge}</p>
                </div>
                {userId === user.id && (
                  <svg className="w-5 h-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                )}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default UserSwitcher;
