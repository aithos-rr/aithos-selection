import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  // Sync from Clerk via webhook (app/api/webhook/clerk/route.ts)
  users: defineTable({
    clerkId: v.string(),
    email: v.string(),
    name: v.optional(v.string()),
    imageUrl: v.optional(v.string()),
  }).index("byClerkId", ["clerkId"]),

  // Example domain entity — rinomina per il tuo use case
  items: defineTable({
    userId: v.id("users"),
    title: v.string(),
    description: v.optional(v.string()),
    completed: v.boolean(),
    dueAt: v.optional(v.number()),
  })
    .index("byUser", ["userId"])
    .index("byUserCompleted", ["userId", "completed"]),
});
