"use client";

import { ChangeEvent, FormEvent, useEffect, useMemo, useRef, useState } from "react";
import styles from "./page.module.css";
import { analyzeText, analyzeMultipart } from "../lib/trustlens-api";
import type {
  RiskBand,
  EvidenceItem,
  ScamPattern,
  RiskSynthesis,
  UserCommunication,
  TrustLensResult,
  AnalyzeTextRequest,
} from "../lib/types";

const LANGUAGES = [
  { value: "en", label: "English" },
  { value: "hi", label: "हिन्दी" },
  { value: "id", label: "Bahasa Indonesia" },
  { value: "ms", label: "Bahasa Melayu" },
  { value: "bn", label: "বাংলা" },
];

const EXAMPLE_MESSAGE =
  "Your bank refund is pending. Share your OTP and click http://example.test to release the money.";

function RiskBadge({ band }: { band: RiskBand }) {
  const label = band === "high" ? "High risk" : band === "review" ? "Needs review" : "Low risk";
  return <span className={`${styles.riskBadge} ${styles[band]}`}>{label}</span>;
}

function ConfidenceMeter({ value }: { value: number }) {
  const percent = Math.round(Math.max(0, Math.min(1, value)) * 100);
  return (
    <div className={styles.meterGroup} aria-label={`${percent}% confidence`}>
      <div className={styles.meterTrack}>
        <div className={styles.meterFill} style={{ width: `${percent}%` }} />
      </div>
      <span>{percent}%</span>
    </div>
  );
}

export default function TrustLensDashboard() {
  const [message, setMessage] = useState("");
  const [language, setLanguage] = useState("en");
  const [screenshot, setScreenshot] = useState<File | null>(null);
  const [result, setResult] = useState<TrustLensResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [reviewState, setReviewState] = useState<"pending" | "approved" | "corrected">("pending");
  const [showRaw, setShowRaw] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => () => abortRef.current?.abort(), []);

  const canSubmit = message.trim().length >= 10 && !loading;
  const evidenceCount = result?.risk.evidence_ids.length ?? 0;
  const isEscalated = result?.risk.human_review_required || result?.risk.risk_band === "high";

  const statusText = useMemo(() => {
    if (loading) return "Analyzing evidence with TrustLens agents…";
    if (result) return `Case ${result.case_id} analyzed`;
    return "Ready for a new case";
  }, [loading, result]);

  function useExample() {
    setMessage(EXAMPLE_MESSAGE);
    setResult(null);
    setError(null);
    setReviewState("pending");
  }

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0] || null;
    if (!file) return;
    if (!/image\/(jpeg|png|webp)/.test(file.type)) {
      setError("Please upload a JPEG, PNG, or WebP screenshot.");
      return;
    }
    if (file.size > 8 * 1024 * 1024) {
      setError("Screenshots must be smaller than 8 MB.");
      return;
    }
    setScreenshot(file);
    setError(null);
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!canSubmit) return;

    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;
    setLoading(true);
    setError(null);
    setResult(null);
    setReviewState("pending");

    try {
      const next = screenshot
        ? await analyzeMultipart({ message, language, screenshot, signal: controller.signal })
        : await analyzeText({ message, language, signal: controller.signal });
      setResult(next);
    } catch (err) {
      if ((err as Error).name !== "AbortError") {
        setError((err as Error).message || "Unable to analyze this case.");
      }
    } finally {
      setLoading(false);
    }
  }

  function clearCase() {
    abortRef.current?.abort();
    setMessage("");
    setScreenshot(null);
    setResult(null);
    setError(null);
    setReviewState("pending");
  }

  return (
    <main className={styles.shell}>
      <header className={styles.topbar}>
        <div className={styles.brandBlock}>
          <div className={styles.brandMark}>TL</div>
          <div>
            <div className={styles.brand}>TrustLens <span>APAC</span></div>
            <div className={styles.brandSub}>Grounded scam prevention</div>
          </div>
        </div>
        <div className={styles.topActions}>
          <span className={styles.liveDot}><i /> Live prototype</span>
          <button className={styles.outlineButton} onClick={clearCase}>New case</button>
        </div>
      </header>

      <section className={styles.hero}>
        <div>
          <p className={styles.eyebrow}>BFSI / assisted prevention</p>
          <h1>Make the safe next step obvious.</h1>
          <p className={styles.heroCopy}>
            Analyze suspicious payment messages and screenshots with explainable Gemini-powered evidence, policy grounding, and human review.
          </p>
        </div>
        <div className={styles.heroStats}>
          <div><strong>5</strong><span>bounded agents</span></div>
          <div><strong>0</strong><span>unsafe actions</span></div>
          <div><strong>100%</strong><span>auditable output</span></div>
        </div>
      </section>

      <div className={styles.dashboardGrid}>
        <section className={styles.panel} aria-labelledby="check-heading">
          <div className={styles.panelHeader}>
            <div><p className={styles.sectionKicker}>01 / Intake</p><h2 id="check-heading">Check a message</h2></div>
            <button className={styles.textButton} onClick={useExample}>Use example</button>
          </div>
          <form onSubmit={handleSubmit}>
            <label className={styles.label} htmlFor="message">Message or transaction context</label>
            <textarea
              id="message"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Paste the suspicious message here…"
              rows={8}
              maxLength={20000}
            />
            <div className={styles.inputMeta}><span>Do not enter real OTPs or account numbers.</span><span>{message.length}/20,000</span></div>

            <div className={styles.formRow}>
              <div className={styles.fieldGroup}>
                <label className={styles.label} htmlFor="language">Explanation language</label>
                <select id="language" value={language} onChange={(e) => setLanguage(e.target.value)}>
                  {LANGUAGES.map((item) => <option key={item.value} value={item.value}>{item.label}</option>)}
                </select>
              </div>
              <div className={styles.fieldGroup}>
                <label className={styles.label} htmlFor="screenshot">Screenshot <span>(optional)</span></label>
                <label className={styles.fileInput} htmlFor="screenshot">
                  <span>{screenshot ? screenshot.name : "Upload image"}</span>
                  <input id="screenshot" type="file" accept="image/jpeg,image/png,image/webp" onChange={handleFileChange} />
                </label>
              </div>
            </div>

            {error && <div className={styles.errorBox} role="alert">{error}</div>}
            <button className={styles.primaryButton} disabled={!canSubmit} type="submit">
              {loading ? <><span className={styles.spinner} /> Running analysis</> : <>Analyze safely <span>↗</span></>}
            </button>
            <p className={styles.formHint}>TrustLens never sends a payment, freezes an account, or contacts a bank.</p>
          </form>
        </section>

        <section className={`${styles.panel} ${styles.resultPanel}`} aria-live="polite">
          <div className={styles.panelHeader}>
            <div><p className={styles.sectionKicker}>02 / Decision support</p><h2>Analysis result</h2></div>
            <span className={styles.status}>{statusText}</span>
          </div>

          {!result && !loading && (
            <div className={styles.emptyState}><div className={styles.emptyIcon}>◎</div><h3>Your evidence trail will appear here</h3><p>Paste a suspicious message or use the example to see risk factors, grounded policy actions, and escalation guidance.</p></div>
          )}
          {loading && <div className={styles.loadingState}><div className={styles.loadingOrb}><span /></div><h3>Building the evidence trail</h3><p>Extracting signals, checking grounded policies, and applying safety guards.</p><div className={styles.loadingSteps}><span className={styles.stepDone}>✓ Evidence extraction</span><span className={styles.stepActive}>◌ Risk synthesis</span><span>○ Communication</span></div></div>}
          {result && (
            <div className={styles.resultBody}>
              <div className={`${styles.riskCard} ${styles[result.risk.risk_band]}`}>
                <div><span className={styles.cardLabel}>TrustLens assessment</span><div className={styles.riskHeadline}><RiskBadge band={result.risk.risk_band} /><span>{result.communication.headline}</span></div></div>
                <div className={styles.confidence}><span>Confidence</span><ConfidenceMeter value={result.risk.confidence} /></div>
              </div>

              <div className={styles.summary}>{result.communication.explanation}</div>

              {isEscalated && <div className={styles.reviewBanner}><div className={styles.reviewIcon}>!</div><div><strong>Human review recommended</strong><span>Conflicting or high-risk signals require an analyst decision before closure.</span></div><button onClick={() => setReviewState("approved")}>Open review</button></div>}

              <div className={styles.twoCol}>
                <div className={styles.infoSection}><h3>Why this was flagged</h3><ul>{result.risk.rationale.map((item, index) => <li key={`${item}-${index}`}><span className={styles.bulletRed}>×</span>{item}</li>)}</ul>{result.risk.scam_patterns.length > 0 && <div className={styles.tags}>{result.risk.scam_patterns.map((pattern) => <span key={pattern}>{pattern.replaceAll("_", " ")}</span>)}</div>}</div>
                <div className={styles.infoSection}><h3>Recommended next step</h3><div className={styles.actionBox}><span className={styles.checkIcon}>✓</span><p>{result.risk.recommended_action}</p></div><h3 className={styles.subHeading}>Do not do</h3><ul>{result.risk.prohibited_actions.map((item, index) => <li key={`${item}-${index}`}><span className={styles.bulletRed}>×</span>{item}</li>)}</ul></div>
              </div>

              {result.risk.uncertainty.length > 0 && <div className={styles.uncertainty}><strong>Uncertainty to resolve</strong>{result.risk.uncertainty.map((item) => <span key={item}>{item}</span>)}</div>}

              <div className={styles.resultFooter}><span><strong>{evidenceCount}</strong> evidence references</span><span><strong>{result.audit.grounding_sources.length}</strong> grounded policies</span><span>Case <strong>{result.case_id}</strong></span></div>
              <div className={styles.reviewControls}><span>Analyst review: <strong className={reviewState === "approved" ? styles.approved : ""}>{reviewState === "approved" ? "Approved for handoff" : "Pending"}</strong></span><div><button className={styles.secondaryButton} onClick={() => setReviewState("corrected")}>Correct finding</button><button className={styles.secondaryButton} onClick={() => setReviewState("approved")}>Approve handoff</button></div></div>
              <button className={styles.rawToggle} onClick={() => setShowRaw(!showRaw)}>{showRaw ? "Hide" : "Show"} API response and audit trace <span>{showRaw ? "⌃" : "⌄"}</span></button>
              {showRaw && <pre className={styles.rawOutput}>{JSON.stringify(result, null, 2)}</pre>}
            </div>
          )}
        </section>
      </div>

      <footer className={styles.footer}><span>TRUSTLENS APAC / GOOGLE CLOUD AI BUILDER CUP PROTOTYPE</span><span>Educational prototype · Synthetic/demo workflow only</span></footer>
    </main>
  );
}
