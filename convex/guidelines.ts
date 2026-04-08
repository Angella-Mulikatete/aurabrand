import { v } from "convex/values";
import { mutation, query, action } from "./_generated/server";
import { api } from "./_generated/api";

export const add = mutation({
  args: {
    id: v.string(),
    content: v.string(),
    category: v.string(),
    embedding: v.array(v.number()),
  },
  handler: async (ctx, args) => {
    await ctx.db.insert("brand_guidelines", {
      id: args.id,
      content: args.content,
      category: args.category,
      embedding: args.embedding,
    });
  },
});

// Vector search must be performed via an Action using ctx.vectorSearch

// Since Convex Vector Search requires 'ctx.vectorSearch' which is only in Actions:

export const getById = query({
    args: { id: v.id("brand_guidelines") },
    handler: async (ctx, args) => {
        return await ctx.db.get(args.id);
    }
});

export const clearAll = mutation({
    handler: async (ctx) => {
        const docs = await ctx.db.query("brand_guidelines").collect();
        for (const doc of docs) {
            await ctx.db.delete(doc._id);
        }
    }
});

export const count = query({
    handler: async (ctx) => {
        const docs = await ctx.db.query("brand_guidelines").collect();
        return docs.length;
    }
});
