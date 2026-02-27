import type { Metadata } from 'next';
import Link from 'next/link';
import styles from '../legal.module.css';

export const metadata: Metadata = {
    title: 'Medical Disclaimer — Cura3.ai',
    description: 'Important medical disclaimer for Cura3.ai AI-generated diagnosis reports.',
};

export default function DisclaimerPage() {
    return (
        <div className={styles.legalPage}>
            <Link href="/" className={styles.backLink}>← Back to Home</Link>

            <div className={styles.legalHeader}>
                <h1>Medical Disclaimer</h1>
                <p>Please read this carefully before using Cura3.ai</p>
            </div>

            <div className={styles.highlight}>
                <p>
                    <strong>IMPORTANT:</strong> Cura3.ai is an AI research and educational tool. It is NOT a
                    medical device, NOT a diagnostic tool, and NOT intended for clinical use. All AI-generated
                    outputs must NOT be used as a basis for medical decisions.
                </p>
            </div>

            <div className={styles.section}>
                <h2>Purpose of the Platform</h2>
                <p>
                    Cura3.ai uses OpenAI GPT-4.1 to simulate multi-specialist analysis of medical reports.
                    The platform is designed for:
                </p>
                <ul>
                    <li>Educational exploration of AI in healthcare.</li>
                    <li>Research into multi-agent diagnostic systems.</li>
                    <li>Demonstrating the potential and limitations of AI-assisted diagnostics.</li>
                </ul>
            </div>

            <div className={styles.section}>
                <h2>Limitations of AI Analysis</h2>
                <ul>
                    <li>AI models can produce inaccurate, incomplete, or misleading results.</li>
                    <li>The AI does not have access to the patient&apos;s full medical history or physical examination.</li>
                    <li>AI cannot replace the clinical judgment of trained medical professionals.</li>
                    <li>Results may contain biases present in AI training data.</li>
                    <li>The platform cannot handle medical emergencies.</li>
                </ul>
            </div>

            <div className={styles.section}>
                <h2>Your Responsibilities</h2>
                <ul>
                    <li>Always consult a qualified healthcare provider for medical advice.</li>
                    <li>Do not delay seeking medical attention based on AI outputs.</li>
                    <li>Do not self-diagnose or self-treat based on platform results.</li>
                    <li>Use platform outputs only as supplementary educational information.</li>
                </ul>
            </div>

            <div className={styles.section}>
                <h2>Liability</h2>
                <p>
                    Cura3.ai, its creators, contributors, and affiliates assume <strong>no liability</strong> for
                    any harm, injury, or adverse outcomes resulting from the use of or reliance on AI-generated
                    reports. By using this platform, you acknowledge and accept these limitations.
                </p>
            </div>

            <div className={styles.section}>
                <h2>If You&apos;re Experiencing a Medical Emergency</h2>
                <div className={styles.highlight}>
                    <p>
                        If you are experiencing a medical emergency, call your local emergency services immediately
                        (e.g., 911 in the US, 112 in the EU, 102/108 in India). Do NOT rely on this platform
                        for emergency medical guidance.
                    </p>
                </div>
            </div>
        </div>
    );
}
