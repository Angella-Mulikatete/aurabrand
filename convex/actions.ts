import { v } from "convex/values";
import { action } from "./_generated/server";
import { api } from "./_generated/api";

export const vectorSearch = action({
  args: {
    embedding: v.array(v.number()),
    limit: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    const results = await ctx.vectorSearch("brand_guidelines", "by_embedding", {
      vector: args.embedding,
      limit: args.limit ?? 3,
    });
    
    // Fetch the actual documents
    const guidelines = await Promise.all(
        results.map(async (r) => {
            const doc = await ctx.runQuery(api.guidelines.getById, { id: r._id });
            return doc;
        })
    );
    return guidelines;
  },
});
