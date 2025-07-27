import { useState } from 'react';

// Animation utilities for consistent animations across the app

export const transitions = {
  // Standard transitions
  fast: 'transition-all duration-150 ease-out',
  normal: 'transition-all duration-300 ease-out',
  slow: 'transition-all duration-500 ease-out',
  
  // Specialized transitions
  bounce: 'transition-all duration-300 ease-bounce',
  spring: 'transition-all duration-400 ease-spring',
  
  // Colors and opacity
  colors: 'transition-colors duration-200 ease-out',
  opacity: 'transition-opacity duration-200 ease-out',
  transform: 'transition-transform duration-300 ease-out',
  
  // Interactive elements
  button: 'transition-all duration-200 ease-out hover:scale-105 active:scale-95',
  card: 'transition-all duration-300 ease-out hover:shadow-lg hover:-translate-y-1',
  input: 'transition-all duration-200 ease-out focus:scale-[1.02]',
};

export const animations = {
  // Fade animations
  fadeIn: 'animate-in fade-in duration-300',
  fadeOut: 'animate-out fade-out duration-200',
  
  // Slide animations
  slideInFromTop: 'animate-in slide-in-from-top-4 duration-300',
  slideInFromBottom: 'animate-in slide-in-from-bottom-4 duration-300',
  slideInFromLeft: 'animate-in slide-in-from-left-4 duration-300',
  slideInFromRight: 'animate-in slide-in-from-right-4 duration-300',
  
  // Scale animations
  scaleIn: 'animate-in zoom-in-95 duration-300',
  scaleOut: 'animate-out zoom-out-95 duration-200',
  
  // Bounce animation
  bounce: 'animate-bounce',
  pulse: 'animate-pulse',
  ping: 'animate-ping',
  spin: 'animate-spin',
  
  // Combined animations
  popIn: 'animate-in zoom-in-95 fade-in duration-200',
  slideUp: 'animate-in slide-in-from-bottom-4 fade-in duration-300',
  slideDown: 'animate-in slide-in-from-top-4 fade-in duration-300',
};

export const staggeredAnimations = {
  // Staggered children animations
  container: 'animate-in fade-in duration-300',
  item: (index: number) => 
    `animate-in slide-in-from-bottom-4 fade-in duration-300 delay-[${index * 50}ms]`,
};

// Framer Motion variants for more complex animations
export const motionVariants = {
  // Container variants
  container: {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        delayChildren: 0.1,
        staggerChildren: 0.1,
      },
    },
  },
  
  // Item variants
  item: {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        type: 'spring',
        stiffness: 100,
      },
    },
  },
  
  // Modal variants
  modal: {
    hidden: {
      opacity: 0,
      scale: 0.95,
      transition: {
        duration: 0.2,
      },
    },
    visible: {
      opacity: 1,
      scale: 1,
      transition: {
        type: 'spring',
        stiffness: 300,
        damping: 30,
      },
    },
  },
  
  // Overlay variants
  overlay: {
    hidden: { opacity: 0 },
    visible: { opacity: 1 },
    exit: { opacity: 0 },
  },
  
  // Slide variants
  slideLeft: {
    hidden: { x: '-100%' },
    visible: { x: 0 },
    exit: { x: '-100%' },
  },
  
  slideRight: {
    hidden: { x: '100%' },
    visible: { x: 0 },
    exit: { x: '100%' },
  },
  
  slideUp: {
    hidden: { y: '100%' },
    visible: { y: 0 },
    exit: { y: '100%' },
  },
  
  slideDown: {
    hidden: { y: '-100%' },
    visible: { y: 0 },
    exit: { y: '-100%' },
  },
};

// Hook for managing animation states
export const useAnimationState = (initialState = false) => {
  const [isAnimating, setIsAnimating] = useState(initialState);
  
  const startAnimation = () => setIsAnimating(true);
  const stopAnimation = () => setIsAnimating(false);
  const toggleAnimation = () => setIsAnimating(!isAnimating);
  
  return {
    isAnimating,
    startAnimation,
    stopAnimation,
    toggleAnimation,
  };
};

// Utility for creating responsive animations
export const responsiveAnimation = {
  mobile: 'duration-200',
  tablet: 'sm:duration-300',
  desktop: 'lg:duration-500',
  combined: 'duration-200 sm:duration-300 lg:duration-500',
};

// Performance-optimized animations for mobile
export const mobileOptimized = {
  transform: 'transform-gpu',
  willChange: 'will-change-transform',
  backfaceVisibility: 'backface-visibility-hidden',
}; 