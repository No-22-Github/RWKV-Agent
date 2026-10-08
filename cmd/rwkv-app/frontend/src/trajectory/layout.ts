/** Ledger section models the trajectory table, timeline and search consume (from DSH layout.ts, MIT). */
import type { TrajectoryCellProps } from './trajectory-record.ts'

/** One Message or Step group inside a turn. */
export interface TrajectoryGroupModel {
  title: string
  description?: string
  cells: readonly TrajectoryCellProps[]
}

/** One sticky turn, or a standalone compaction section between turns. */
export interface TrajectoryTurnModel {
  turn: number | null
  groups: readonly TrajectoryGroupModel[]
}

