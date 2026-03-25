(()=>{var e={};e.id=530,e.ids=[530],e.modules={6037:e=>{"use strict";e.exports=require("mongoose")},846:e=>{"use strict";e.exports=require("next/dist/compiled/next-server/app-page.runtime.prod.js")},4870:e=>{"use strict";e.exports=require("next/dist/compiled/next-server/app-route.runtime.prod.js")},3295:e=>{"use strict";e.exports=require("next/dist/server/app-render/after-task-async-storage.external.js")},9294:e=>{"use strict";e.exports=require("next/dist/server/app-render/work-async-storage.external.js")},3033:e=>{"use strict";e.exports=require("next/dist/server/app-render/work-unit-async-storage.external.js")},9021:e=>{"use strict";e.exports=require("fs")},1630:e=>{"use strict";e.exports=require("http")},5591:e=>{"use strict";e.exports=require("https")},3873:e=>{"use strict";e.exports=require("path")},1997:e=>{"use strict";e.exports=require("punycode")},7910:e=>{"use strict";e.exports=require("stream")},9551:e=>{"use strict";e.exports=require("url")},8354:e=>{"use strict";e.exports=require("util")},3566:e=>{"use strict";e.exports=require("worker_threads")},4075:e=>{"use strict";e.exports=require("zlib")},3024:e=>{"use strict";e.exports=require("node:fs")},7075:e=>{"use strict";e.exports=require("node:stream")},7830:e=>{"use strict";e.exports=require("node:stream/web")},8715:(e,t,r)=>{"use strict";r.r(t),r.d(t,{patchFetch:()=>x,routeModule:()=>d,serverHooks:()=>y,workAsyncStorage:()=>g,workUnitAsyncStorage:()=>m});var s={};r.r(s),r.d(s,{POST:()=>l});var n=r(2706),i=r(8203),a=r(5994),o=r(9187),u=r(9081),c=r(1317),p=r(9620);async function l(e){try{await (0,c.A)();let{title:t,description:r,content:s,category:n,company:i}=await e.json();if(!t||!r||!s)return o.NextResponse.json({error:"Missing required fields: title, description, content"},{status:400});let a=await (0,u.X)({title:t,description:r,content:s,category:n||"General"});if(a.company=i||a.company||"TrendNexAI",await p.A.findOne({slug:a.slug}))return o.NextResponse.json({error:"Article with this slug already exists"},{status:409});let l=new p.A(a);return await l.save(),o.NextResponse.json({success:!0,article:l})}catch(e){return console.error("Error in generate-article:",e),o.NextResponse.json({error:"Failed to generate article"},{status:500})}}let d=new n.AppRouteRouteModule({definition:{kind:i.RouteKind.APP_ROUTE,page:"/api/generate-article/route",pathname:"/api/generate-article",filename:"route",bundlePath:"app/api/generate-article/route"},resolvedPagePath:"/home/pavan-kalyan-penchikalapati/Desktop/trendnexai/app/api/generate-article/route.ts",nextConfigOutput:"",userland:s}),{workAsyncStorage:g,workUnitAsyncStorage:m,serverHooks:y}=d;function x(){return(0,a.patchFetch)({workAsyncStorage:g,workUnitAsyncStorage:m})}},6487:()=>{},8335:()=>{},1317:(e,t,r)=>{"use strict";r.d(t,{A:()=>o});var s=r(6037),n=r.n(s);let i=process.env.MONGODB_URI,a=global.mongoose;a||(a=global.mongoose={conn:null,promise:null});let o=async function(){return i&&(i.startsWith("mongodb://")||i.startsWith("mongodb+srv://"))?(a.conn||(a.promise||(a.promise=n().connect(i,{bufferCommands:!1}).then(e=>e)),a.conn=await a.promise),a.conn):(console.warn("MONGODB_URI is not set or invalid. Skipping database connection. Please set a valid MongoDB URI in .env.local."),null)}},9081:(e,t,r)=>{"use strict";r.d(t,{X:()=>n});let s=new(r(7590)).Ay({apiKey:process.env.OPENAI_API_KEY});async function n(e){let t=`
You are an AI news processor. Take the following raw news data and convert it into a structured JSON format suitable for a multilingual news website.

Raw News:
Title: ${e.title}
Description: ${e.description}
Content: ${e.content}
Category: ${e.category||"General"}

Requirements:
- Create a compelling title
- Generate a unique slug (URL-friendly, lowercase, hyphens)
- Determine appropriate category
- Determine company/source name (e.g., Times of India, Economic Times, etc.)
- Write a concise summary (2-3 sentences)
- Translate the full content into English, Telugu (te), Tamil (ta), Kannada (kn), and Malayalam (ml)
- Generate relevant tags (3-5 keywords)
- Create SEO title and description

Return ONLY valid JSON with this exact structure:
{
  "title": "string",
  "slug": "string",
  "category": "string",
  "company": "string",
  "summary": "string",
  "content": {
    "en": "string",
    "te": "string",
    "ta": "string",
    "kn": "string",
    "ml": "string"
  },
  "tags": ["string"],
  "seo_title": "string",
  "seo_description": "string"
}
`,r=await s.chat.completions.create({model:"gpt-4",messages:[{role:"user",content:t}],temperature:.7}),n=r.choices[0]?.message?.content;if(!n)throw Error("Failed to process news with AI");try{return JSON.parse(n)}catch(e){throw Error("Invalid JSON response from AI")}}},9620:(e,t,r)=>{"use strict";r.d(t,{A:()=>a});var s=r(6037),n=r.n(s);let i=new s.Schema({title:{type:String,required:!0},slug:{type:String,required:!0,unique:!0},category:{type:String,required:!0},company:{type:String,default:"TrendNexAI"},summary:{type:String,required:!0},content:{en:{type:String,required:!0},te:{type:String,required:!0},ta:{type:String,required:!0},kn:{type:String,required:!0},ml:{type:String,required:!0}},tags:[{type:String}],seo_title:{type:String,required:!0},seo_description:{type:String,required:!0},createdAt:{type:Date,default:Date.now}}),a=n().models.Article||n().model("Article",i)}};var t=require("../../../webpack-runtime.js");t.C(e);var r=e=>t(t.s=e),s=t.X(0,[638,452,590],()=>r(8715));module.exports=s})();