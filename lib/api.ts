const BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8001";

export async function fetchArticles({ category, company, search, sort, page, pageSize }:{category?: string; company?: string; search?: string; sort?: string; page?: number; pageSize?: number;}) {
  const params = new URLSearchParams();
  if (category) params.set("category", category);
  if (company) params.set("company", company);
  if (search) params.set("search", search);
  if (sort) params.set("sort", sort);
  params.set("skip", String((page || 0) * (pageSize || 12)));
  params.set("limit", String(pageSize || 12));

  const res = await fetch(`${BASE}/api/articles?${params.toString()}`);
  if (!res.ok) throw new Error(`Failed to fetch articles ${res.status}`);
  return res.json();
}

export async function fetchArticleBySlug(slug: string) {
  const res = await fetch(`${BASE}/api/article/${encodeURIComponent(slug)}`);
  if (!res.ok) throw new Error(`Failed to fetch article ${res.status}`);
  return res.json();
}

export async function fetchCategories() {
  const res = await fetch(`${BASE}/api/categories`);
  if (!res.ok) throw new Error("Failed to fetch categories");
  const payload = await res.json();
  return payload.categories || [];
}

export async function fetchCompanies() {
  const res = await fetch(`${BASE}/api/companies`);
  if (!res.ok) throw new Error("Failed to fetch companies");
  const payload = await res.json();
  return payload.companies || [];
}
