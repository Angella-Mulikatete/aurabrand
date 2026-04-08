import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  brand_guidelines: defineTable({
    content: v.string(),
    category: v.string(),
    embedding: v.array(v.float64()),
    id: v.string(), // Local ID/Reference
  }).vectorIndex("by_embedding", {
    vectorField: "embedding",
    dimensions: 384,
  }),
});
