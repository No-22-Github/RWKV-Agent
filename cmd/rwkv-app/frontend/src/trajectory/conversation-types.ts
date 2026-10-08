/*
 * The slice of DSH's conversation contracts the ported trajectory view reads,
 * restated locally (MIT, see ./LICENSE.deepseek-harness).
 */
import type { ReactNode } from 'react'

/** Request configuration recorded for one provider call. */
export interface AssistantRequestConfig {
  provider?: string
  model?: string
  purpose?: string
  thinking?: string
  reasoningEffort?: string
  temperature?: number
  maxTokens?: number
  stop?: readonly string[]
}

/** One model-visible tool definition. */
export interface ToolSchema {
  name: string
  description: string
  parameters: object
}

/** Complete model-visible request state in force for one generation. */
export interface ConversationPromptSnapshot {
  config: AssistantRequestConfig
  system: string
  tools: readonly ToolSchema[]
}

/** Attachment references; this app records none yet, the shapes keep the inspector code intact. */
export interface ImageAttachmentRef { name?: string; bytes: number; mediaType?: string; width: number; height: number }
export interface FileAttachmentRef { name?: string; bytes: number; mediaType?: string }

export type RenderMessageImages = (owner: { images: readonly unknown[]; align: 'start' | 'end'; compact?: boolean; thumbnail?: boolean }) => ReactNode
