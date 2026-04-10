import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  brand_guidelines: defineTable({
    content: v.string(),
    category: v.string(),
    embedding: v.array(v.float64()),
    id: v.string(), 
  }).vectorIndex("by_embedding", {
    vectorField: "embedding",
    dimensions: 768,
  }),

  // Visual Identity Storage
  brand_visuals: defineTable({
    primary_color: v.string(), // HEX
    secondary_color: v.optional(v.string()),
    font_family: v.string(),
    logo_url: v.optional(v.string()),
    last_updated: v.number(),
  }),

  // Tracking improvement over time for judges
  learning_history: defineTable({
    timestamp: v.number(),
    topic: v.string(),
    previous_score: v.float64(),
    new_score: v.float64(),
    improvement_delta: v.float64(),
    lesson_learned: v.string(),
  }),
});
