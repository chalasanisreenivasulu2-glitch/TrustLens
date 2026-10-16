export type RiskBand = "low" | "review" | "high";

export interface EvidenceItem {
  id: string;
  kind: "text" | "visual" | "transaction" | "url" | "rule";
  claim: string;
  quote: string;
  confidence: number;
}

export interface ScamPattern {
  name: string;
  evidence_ids: string[];
  rationale: string;
}

export interface RiskSynthesis {
  risk_band: RiskBand;
  confidence: number;
  scam_patterns: string[];
  evidence_ids: string[];
  rationale: string[];
  recommended_action: string;
  prohibited_actions: string[];
  human_review_required: boolean;
  uncertainty: string[];
}

export interface UserCommunication {
  language: string;
  headline: string;
  explanation: string;
  next_steps: string[];
  do_not_do: string[];
  disclaimer: string;
}

export interface TrustLensResult {
  case_id: string;
  risk: RiskSynthesis;
  communication: UserCommunication;
  audit: {
    model: string;
    agent_budget: number;
    grounding_sources: string[];
    image_analyzed: boolean;
    human_review_required: boolean;
    prototype_notice: string;
  };
}

export interface AnalyzeTextRequest {
  message: string;
  language: string;
}
