'use client';

import { useEffect } from 'react';

interface AdUnitProps {
  slot: string;
  format?: 'auto' | 'vertical' | 'horizontal' | 'rectangle';
  responsive?: boolean;
}

export default function AdUnit({ 
  slot, 
  format = 'auto', 
  responsive = true 
}: AdUnitProps) {
  useEffect(() => {
    // Load Google AdSense script
    if (typeof window !== 'undefined') {
      try {
        (window as any).adsbygoogle = (window as any).adsbygoogle || [];
        (window as any).adsbygoogle.push({});
      } catch (e) {
        console.error('AdSense error:', e);
      }
    }
  }, [slot]);

  const getSlotClass = () => {
    switch (slot) {
      case 'article-top':
        return 'min-h-[100px] mb-8';
      case 'article-mid':
        return 'min-h-[250px] my-8';
      case 'article-bottom':
        return 'min-h-[100px] mt-8';
      case 'sidebar':
        return 'min-h-[600px] my-4';
      default:
        return 'min-h-[90px] my-4';
    }
  };

  return (
    <div 
      className={`bg-gray-50 dark:bg-slate-800 rounded-lg p-4 flex items-center justify-center text-center ${getSlotClass()}`}
      data-ad-slot={slot}
    >
      {/* Google AdSense placeholder */}
      <ins
        className="adsbygoogle"
        style={{
          display: 'block',
          width: '100%',
          minHeight: '90px'
        }}
        data-ad-client="ca-pub-xxxxxxxxxxxxxxxx"
        data-ad-slot={slot}
        data-ad-format={format}
        data-full-width-responsive={responsive}
      />
      
      {/* Fallback for development without AdSense configured */}
      <div className="text-gray-400 dark:text-gray-500 text-sm">
        <div>Advertisement</div>
        <div className="text-xs mt-1">Slot: {slot}</div>
      </div>
    </div>
  );
}
