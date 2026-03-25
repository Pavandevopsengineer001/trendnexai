'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

interface ArticleContentProps {
  article: {
    title: string;
    category: string;
    summary: string;
    content: {
      en: string;
      te: string;
      ta: string;
      kn: string;
      ml: string;
    };
    tags: string[];
    createdAt: string;
  };
}

const ArticleContent = ({ article }: ArticleContentProps) => {
  const [selectedLanguage, setSelectedLanguage] = useState('en');

  const languages = [
    { code: 'en', name: 'English', content: article.content.en },
    { code: 'te', name: 'Telugu', content: article.content.te },
    { code: 'ta', name: 'Tamil', content: article.content.ta },
    { code: 'kn', name: 'Kannada', content: article.content.kn },
    { code: 'ml', name: 'Malayalam', content: article.content.ml },
  ];

  const activeLanguage = languages.find((lang) => lang.code === selectedLanguage) || languages[0];

  return (
    <section className="glass-glow p-6 mb-8 animate-pop-in">
      <div className="mb-4 flex flex-wrap gap-2">
        {languages.map((lang) => (
          <Button
            key={lang.code}
            variant={selectedLanguage === lang.code ? 'default' : 'outline'}
            size="sm"
            onClick={() => setSelectedLanguage(lang.code)}
          >
            {lang.name}
          </Button>
        ))}
      </div>

      <div className="prose prose-lg max-w-none">
        {activeLanguage.content.split('\n').map((paragraph, index) => (
          <p key={index} className="mb-4 text-gray-700 dark:text-slate-100 leading-relaxed">
            {paragraph}
          </p>
        ))}
      </div>
    </section>
  );
};

export default ArticleContent;
