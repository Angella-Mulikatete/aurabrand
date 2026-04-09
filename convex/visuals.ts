import { v } from "convex/values";
import { mutation, query } from "./_generated/server";

export const update = mutation({
  args: {
    primary_color: v.string(),
    secondary_color: v.optional(v.string()),
    font_family: v.string(),
    logo_url: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const existing = await ctx.db.query("brand_visuals").unique();
    if (existing) {
      await ctx.db.patch(existing._id, {
        ...args,
        last_updated: Date.now(),
      });
    } else {
      await ctx.db.insert("brand_visuals", {
        ...args,
        last_updated: Date.now(),
      });
    }
  },
});

export const get = query({
  handler: async (ctx) => {
    return await ctx.db.query("brand_visuals").unique();
  },
});
