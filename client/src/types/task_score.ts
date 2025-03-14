export interface TaskScore {
  score: number;
  created_at: Date;
  evaluator_id: string;
  evaluator_tags?: string[];
  score_tags?: string[];
}
