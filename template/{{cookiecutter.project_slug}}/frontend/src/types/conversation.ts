{%- if cookiecutter.use_database %}
/**
 * Conversation types for AI chat persistence.
 */
import { RatingValue, type UserRating } from "./chat";

export interface Conversation {
  id: string;
  user_id?: string;
  title?: string;
  created_at: string;
  updated_at: string;
  is_archived: boolean;
}

export interface ConversationMessage {
  id: string;
  conversation_id: string;
  role: "user" | "assistant" | "system";
  content: string;
  created_at: string;
  model_name?: string;
  tokens_used?: number;
  tool_calls?: ConversationToolCall[];
{%- if cookiecutter.use_jwt %}
  user_rating?: UserRating;
  rating_count?: { likes: number; dislikes: number } | null;
{%- endif %}
}

export interface ConversationToolCall {
  id: string;
  message_id: string;
  tool_call_id: string;
  tool_name: string;
  args: Record<string, unknown>;
  result?: string;
  status: "pending" | "running" | "completed" | "failed";
  started_at: string;
  completed_at?: string;
  duration_ms?: number;
}

export interface ConversationListResponse {
  items: Conversation[];
  total: number;
}

export interface ConversationWithMessages extends Conversation {
  messages: ConversationMessage[];
}

{%- if cookiecutter.use_jwt %}
/**
 * Message rating types.
 */

export interface MessageRating {
  id: string;
  message_id: string;
  user_id: string;
  rating: RatingValue;
  comment: string | null;
  created_at: string;
  updated_at: string;
}

export interface MessageRatingWithDetails extends MessageRating {
  message_content: string | null;
  message_role: string | null;
  conversation_id: string | null;
  user_email: string | null;
  user_name: string | null;
}

export interface MessageRatingListResponse {
  items: MessageRatingWithDetails[];
  total: number;
}

export interface RatingSummary {
  total_ratings: number;
  like_count: number;
  dislike_count: number;
  average_rating: number;
  with_comments: number;
  ratings_by_day: Array<{ date: string; likes: number; dislikes: number }>;
}
{%- endif %}
{%- endif %}
