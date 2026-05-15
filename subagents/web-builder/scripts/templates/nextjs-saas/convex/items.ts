import { query, mutation } from "./_generated/server";
import { v } from "convex/values";

export const list = query({
  args: { userId: v.id("users") },
  handler: async (ctx, { userId }) => {
    return await ctx.db
      .query("items")
      .withIndex("byUser", (q) => q.eq("userId", userId))
      .collect();
  },
});

export const create = mutation({
  args: { userId: v.id("users"), title: v.string() },
  handler: async (ctx, { userId, title }) => {
    return await ctx.db.insert("items", {
      userId,
      title,
      completed: false,
    });
  },
});

export const toggleComplete = mutation({
  args: { itemId: v.id("items") },
  handler: async (ctx, { itemId }) => {
    const item = await ctx.db.get(itemId);
    if (!item) throw new Error("Item not found");
    await ctx.db.patch(itemId, { completed: !item.completed });
  },
});
