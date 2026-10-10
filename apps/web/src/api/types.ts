/** Names for the simulator API's generated types (spec §11, §15.3: generated, never hand-written). */
import type { components } from './schema'

type Schemas = components['schemas']

export type TurnResult = Schemas['TurnResult']
export type Card = NonNullable<TurnResult['card']>
export type CardOf<T extends Card['tool']> = Extract<Card, { tool: T }>
export type PendingView = Schemas['PendingView']
export type HealthResponse = Schemas['HealthResponse']
export type VisitCard = Schemas['VisitCard']
export type ReminderCard = Schemas['ReminderCard']
export type SourceInfo = Schemas['SourceInfo']
export type ItemCard = Schemas['ItemCard']
export type ChangeCard = Schemas['ChangeCard']
export type SegmentCard = Schemas['SegmentCard']
export type PlanEntryCard = Schemas['PlanEntryCard']
export type QuestionCard = Schemas['QuestionCard']
