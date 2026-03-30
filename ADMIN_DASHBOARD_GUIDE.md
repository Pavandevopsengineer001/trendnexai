# 🎛️ Admin Dashboard - Complete Guide

**Status:** ✅ **FULLY IMPLEMENTED & READY TO USE**

---

## 📋 Overview

The admin dashboard is a production-ready content management system for TrendNexAI. It allows authorized users to:
- ✅ Create new articles
- ✅ Edit existing articles
- ✅ Publish, archive, and delete articles
- ✅ Filter articles by status (Draft, Published, Archived)
- ✅ Search articles by title
- ✅ Track article views
- ✅ Manage article categories

---

## 🚀 Quick Start

### 1. Access Admin Panel

```
URL: http://localhost:3000/admin/login
```

### 2. Login Credentials

Default credentials for testing:

| Field | Value |
|-------|-------|
| **Username** | `admin` |
| **Password** | `admin` |

⚠️ **Change these credentials immediately in production!**

### 3. After Login

You'll be redirected to:
```
http://localhost:3000/admin/articles
```

---

## 📍 Admin Routes

| Route | Purpose | Description |
|-------|---------|-------------|
| `/admin/login` | Authentication | Login to admin panel |
| `/admin` | Dashboard | Overview & statistics |
| `/admin/articles` | Articles List | View, search, filter articles |
| `/admin/articles/new` | Create | Create new article |
| `/admin/articles/:id` | Edit | Edit existing article |

---

## 🔑 Key Features

### 1. **Articles Management Page** (`/admin/articles`)

#### Features:
- 📋 **Table View**: Display all articles with key information
- 🔍 **Search**: Filter articles by title in real-time
- 🏷️ **Status Tabs**: Filter by Draft / Published / Archived
- 📊 **Columns**:
  - Title (clickable to edit)
  - Category
  - Status (with color badges)
  - Views count
  - Creation date
  - Action buttons

#### Action Buttons:
- **Edit**: Go to edit page
- **Publish**: Change status from Draft → Published (unavailable if already published)
- **Archive**: Move to archive (grayed out button)
- **Delete**: Permanently remove article (with confirmation)

#### Status Colors:
- 🟢 **Published**: Green badge
- 🟡 **Draft**: Yellow badge
- ⚫ **Archived**: Gray badge

---

### 2. **Create Article Page** (`/admin/articles/new`)

#### Form Fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| **Title** | Text | ✅ Yes | Article headline (max 200 chars) |
| **Category** | Dropdown | ✅ Yes | Choose from 8 categories |
| **Status** | Dropdown | ✅ Yes | Draft or Published |
| **Summary** | Textarea | ❌ No | Brief description (shown in lists) |
| **Content** | Textarea | ✅ Yes | Full article body (markdown supported) |
| **Tags** | Text | ❌ No | Comma-separated keywords |

#### Categories Available:
- General
- Technology
- Business
- Sports
- Health
- Science
- Entertainment
- World

#### Submission:
- **Save**: Creates article and returns to articles list
- **Cancel**: Discard changes and return to articles list

---

### 3. **Edit Article Page** (`/admin/articles/[id]`)

**Same form as Create, but:**
- Pre-populated with existing article data
- Can change all fields
- Can change status (Draft → Published → Archived)
- Updates existing article instead of creating new

---

### 4. **Admin Dashboard** (`/admin`)

Overview page showing:
- 📊 **Total Articles**: Overall count
- 🟢 **Published**: Live articles
- 🟡 **Draft**: In-progress articles
- 👁️ **Total Views**: Aggregate engagement metric

Quick action links:
- View All Articles
- Create New Article
- Back to Home

---

## 🔐 Authentication

### How it works:

1. **Login**: POST to `/api/admin/login`
   - Username + Password sent
   - Backend validates credentials
   - Returns JWT token + user info

2. **Token Storage**: 
   - Stored in localStorage as `admin_token`
   - Automatically included in API requests
   - Expires after 30 minutes (configurable)

3. **Protected Routes**:
   - All `/admin/*` pages check for valid token
   - Auto-redirect to login if token missing/expired
   - Token sent in `Authorization: Bearer <token>` header

### Backend Security:

```python
# Roles available:
- "admin"   → Full access to all features
- "editor"  → Can create/edit articles, publish
- "user"    → Read-only access

# Default admin account:
Username: admin
Password: admin  # ⚠️ Change immediately!
```

---

## 💾 Data Workflow

### Creating an Article

```
Create Page
    ↓
Fill Form (title, category, content, etc.)
    ↓
Click "Create Article"
    ↓
API: POST /api/admin/articles (with token)
    ↓
Backend: Validates, saves to MongoDB
    ↓
Response: 201 Created + article data
    ↓
Redirect to Articles List
    ↓
New article visible in table
```

### Publishing an Article

```
Draft Article in Table
    ↓
Click "Publish" button
    ↓
API: POST /api/admin/articles/:id/status
    ↓
Body: { "status_value": "published" }
    ↓
Backend: Updates status, invalidates cache
    ↓
Table refreshes automatically
    ↓
Status badge changes to green "Published"
```

### Deleting an Article

```
Article in Table
    ↓
Click "Delete" button
    ↓
Confirmation dialog appears
    ↓
If confirmed: API: DELETE /api/admin/articles/:id
    ↓
Backend: Removes from MongoDB
    ↓
Cache invalidated
    ↓
Article removed from table
```

---

## 🎯 Use Cases

### Use Case 1: Daily Content Publishing

1. Journalist writes article (could be in any text editor)
2. Go to `/admin/articles/new`
3. Fill in title, category, content
4. Save as **Draft**
5. Supervisor reviews
6. Editor publishes it manually via **Publish** button
7. Article goes live on homepage

### Use Case 2: Content Management

1. Editor opens `/admin/articles`
2. Uses search to find article: "Python Tips"
3. Clicks "Edit"
4. Updates content
5. Saves changes
6. Changes reflected immediately on public site

### Use Case 3: Archive Old Content

1. Find outdated article in articles list
2. Click "Archive" button
3. Article hidden from public but kept in database
4. Can be restored later if needed

### Use Case 4: Bulk Status Management

1. Admin filters to view all "Draft" articles
2. Reviews several drafts
3. Publishes approved ones individually
4. Deletes rejected ones
5. All changes reflected in search results

---

## 🔄 Real-Time Features

### Auto-Refresh:
- After creating/editing/deleting, article list updates automatically
- Status changes reflect immediately
- View counts update in real-time

### Search:
- Type to filter articles
- Search is instant (no button needed)
- Searches across article titles

### Error Handling:
- Failed operations show error messages
- Validation errors display in form
- Network errors caught gracefully
- Duplicate deletions prevented

---

## 📱 Responsive Design

- ✅ **Desktop**: Full-width table with all columns visible
- ✅ **Tablet**: Responsive grid layout
- ✅ **Mobile**: Sidebar collapses to icons, table becomes scrollable

---

## 🌓 Dark Mode

- Full dark mode support via Tailwind CSS
- Auto-detects system preference
- Toggle via theme button in header
- All colors optimized for readability

---

## 🔗 API Integration

### Backend Endpoints Used

```
POST   /api/admin/login
       → Authenticate with username/password
       ← Returns: { "access_token": "...", "user": {...} }

GET    /api/admin/articles?status=draft
       → Fetch articles with optional status filter
       ← Returns: { "items": [...] }

POST   /api/admin/articles
       → Create new article
       ← Returns: { "_id": "...", "title": "..." }

GET    /api/admin/articles/:id
       → Fetch single article for editing
       ← Returns: { "title": "...", "content": "..." }

PUT    /api/admin/articles/:id
       → Update article
       ← Returns: Updated article object

POST   /api/admin/articles/:id/status
       → Change article status
       ← Returns: Updated article with new status

DELETE /api/admin/articles/:id
       → Delete article permanently
       ← Returns: { "message": "Deleted" }
```

---

## 📊 Form Validation

### Client-Side:
- Required fields marked with red asterisk (*)
- Submit button disabled until required fields filled
- Console warnings for invalid input

### Server-Side:
- Title length validation (10-200 chars)
- Category whitelist validation
- Status enum validation
- Content length requirement (min 100 chars)
- Similar validations for all fields

---

## 🚨 Common Issues & Solutions

### Issue: Can't Login
**Solution**: 
- Check admin backend is running (`docker-compose up`)
- Verify credentials (default: admin/admin)
- Check console for error messages

### Issue: Changes Not Saving
**Solution**:
- Verify network connection
- Check browser console for errors
- Ensure backend API URL is correct in `.env`
- Check token hasn't expired

### Issue: Can't See Articles
**Solution**:
- Log in first
- Check articles list page loads (`/admin/articles`)
- If empty, create article via "New Article" button
- Use search/filters to find articles

### Issue: Can't Publish Article
**Solution**:
- Only draft articles can be published
- Check article status in table
- Ensure you have editor/admin role
- Try refreshing page and retry

---

## 🛠️ Customization Guide

### Change Default Login Credentials

Edit in `.env` file:
```bash
ADMIN_USERNAME=newadmin
ADMIN_PASSWORD=newpassword
```

Then restart backend.

### Add More Categories

Edit [AdminArticleEditPage]:
```typescript
const CATEGORIES = [
  'general',
  'technology',
  // Add here
];
```

Also update backend in `backend/app/schemas.py`

### Customize Form Fields

Edit `app/admin/articles/[id]/page.tsx`:
```typescript
// Add new field to form
<div>
  <label>Author Name</label>
  <input value={formData.author} onChange={...} />
</div>
```

---

## 📈 Monitoring

### View Admin Logs
```bash
docker-compose logs -f backend
```

### Check Login Attempts
Look for logs with "admin/login"

### Monitor Article Operations
Check database directly:
```bash
# Connect to MongoDB
mongodb://admin:password@localhost:27017/trendnexai
```

---

## 🔒 Security Checklist

- ✅ JWT tokens used (not storing passwords)
- ✅ HTTPS recommended for production
- ✅ CORS configured
- ✅ Rate limiting on login endpoint
- ✅ Admin credentials changeable
- ✅ Token expiration set (30 min)
- ✅ Protected routes require authentication

---

## 📖 File Structure

```
app/
├── admin/
│   ├── page.tsx                 ← Dashboard home
│   ├── login/
│   │   └── page.tsx             ← Login form
│   └── articles/
│       ├── page.tsx             ← Articles list
│       ├── new/
│       │   └── page.tsx         ← Create article
│       └── [id]/
│           └── page.tsx         ← Edit article

components/
└── AdminLayout.tsx              ← Layout wrapper with sidebar
```

---

## ✅ Testing the Admin Panel

### Test Flow:

```bash
# 1. Start backend
cd backend && python -m uvicorn app.main:app --reload

# 2. Start frontend
npm run dev

# 3. Navigate to admin login
http://localhost:3000/admin/login

# 4. Login with credentials
Username: admin
Password: admin

# 5. Test workflow
- Create article
- Publish article
- Edit article
- Search article
- Delete article

# 6. Verify in database
- Check MongoDB for created articles
- Check article shows on public homepage
```

---

## 🎉 Summary

The admin dashboard is **fully functional** and provides:
- ✅ Complete article CRUD operations
- ✅ Status workflow (Draft → Published → Archived)
- ✅ Real-time updates
- ✅ Authentication & authorization
- ✅ Responsive design
- ✅ Dark mode support
- ✅ Error handling
- ✅ Production-ready code

**You're ready to start managing content!** 🚀

---

**For questions or issues, check the backend logs:**
```bash
docker-compose logs backend
```
