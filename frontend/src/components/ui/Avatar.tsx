'use client';

import { cn, getInitials } from '@/lib/utils';

interface AvatarProps {
  name: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  variant?: 'circle' | 'square';
  className?: string;
}

export function Avatar({ name, size = 'md', variant = 'circle', className }: AvatarProps) {
  const sizes = {
    sm: 'h-8 w-8 text-xs',
    md: 'h-10 w-10 text-sm',
    lg: 'h-12 w-12 text-base',
    xl: 'h-16 w-16 text-lg',
  };

  const shapes = {
    circle: 'rounded-full',
    square: 'rounded-lg',
  };

  // Generate consistent color based on name
  const colors = [
    'bg-blue-500',
    'bg-green-500',
    'bg-purple-500',
    'bg-amber-500',
    'bg-rose-500',
    'bg-cyan-500',
    'bg-indigo-500',
    'bg-teal-500',
  ];

  const colorIndex = name.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0) % colors.length;

  return (
    <div
      className={cn(
        'flex items-center justify-center font-semibold text-white',
        sizes[size],
        shapes[variant],
        colors[colorIndex],
        className
      )}
    >
      {getInitials(name)}
    </div>
  );
}
