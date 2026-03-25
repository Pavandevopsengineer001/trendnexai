import mongoose, { Schema, Document } from 'mongoose';

export interface IArticle extends Document {
  title: string;
  slug: string;
  category: string;
  company?: string;
  summary: string;
  content: {
    en: string;
    te: string;
    ta: string;
    kn: string;
    ml: string;
  };
  tags: string[];
  seo_title: string;
  seo_description: string;
  createdAt: Date;
}

const ArticleSchema: Schema = new Schema({
  title: { type: String, required: true },
  slug: { type: String, required: true, unique: true },
  category: { type: String, required: true },
  company: { type: String, default: 'TrendNexAI' },
  summary: { type: String, required: true },
  content: {
    en: { type: String, required: true },
    te: { type: String, required: true },
    ta: { type: String, required: true },
    kn: { type: String, required: true },
    ml: { type: String, required: true },
  },
  tags: [{ type: String }],
  seo_title: { type: String, required: true },
  seo_description: { type: String, required: true },
  createdAt: { type: Date, default: Date.now },
});

export default mongoose.models.Article || mongoose.model<IArticle>('Article', ArticleSchema);