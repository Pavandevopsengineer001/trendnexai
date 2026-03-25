import Link from 'next/link';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface ArticleCardProps {
  article: {
    _id: string;
    title: string;
    slug: string;
    summary: string;
    category: string;
    company?: string;
    source_url?: string;
    image_url?: string;
    tags: string[];
    createdAt: string;
  };
}

export default function ArticleCard({ article }: ArticleCardProps) {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  return (
    <Card className="h-full card-premium animate-fade-up hover:scale-[1.01] duration-300">
      {article.image_url && (
        <div className="h-40 overflow-hidden rounded-t-xl">
          <img src={article.image_url} alt={article.title} className="object-cover w-full h-full" />
        </div>
      )}
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between mb-2">
          <div className="flex gap-2 items-center">
            <Badge variant="secondary" className="text-xs">
              {article.category}
            </Badge>
            {article.company && (
              <span className="text-xs text-gray-500 dark:text-gray-300">{article.company}</span>
            )}
          </div>
          <span className="text-xs text-gray-500">
            {formatDate(article.createdAt)}
          </span>
        </div>
        <Link href={`/article/${article.slug}`}>
          <h3 className="text-lg font-semibold text-gray-900 hover:text-blue-600 transition-colors line-clamp-2">
            {article.title}
          </h3>
        </Link>
      </CardHeader>

      <CardContent>
        <p className="text-gray-600 text-sm mb-4 line-clamp-3">
          {article.summary}
        </p>

        <div className="flex flex-wrap gap-1 mb-4">
          {article.tags.slice(0, 3).map((tag) => (
            <Badge key={tag} variant="outline" className="text-xs">
              {tag}
            </Badge>
          ))}
        </div>

        <div className="flex items-center justify-between gap-2">
          <Link
            href={`/article/${article.slug}`}
            className="text-blue-600 hover:text-blue-800 text-sm font-medium"
          >
            Read More →
          </Link>
          {article.source_url && (
            <a
              href={article.source_url}
              target="_blank"
              rel="noreferrer"
              className="text-xs text-gray-500 hover:text-gray-700"
            >
              Original Source
            </a>
          )}
        </div>
      </CardContent>
    </Card>
  );
}