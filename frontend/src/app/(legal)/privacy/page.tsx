import type { Metadata } from 'next';
import Link from 'next/link';
import styles from '../legal.module.css';

export const metadata: Metadata = {
    title: 'Privacy Policy — Cura3.ai',
    description: 'How Cura3.ai collects, uses, and protects your personal and medical data.',
};

export default function PrivacyPage() {
    return (
        <div className={styles.legalPage}>
            <Link href="/" className={styles.backLink}>← Back to Home</Link>

            <div className={styles.legalHeader}>
                <h1>Privacy Policy</h1>
                <p>Last updated: February 25, 2026</p>
            </div>

            <div className={styles.section}>
                <h2>1. Information We Collect</h2>
                <ul>
                    <li><strong>Account Information:</strong> Name, email address, and profile picture via Google Sign-In.</li>
                    <li><strong>Medical Reports:</strong> Files or text content you upload for analysis.</li>
                    <li><strong>Diagnosis Results:</strong> AI-generated specialist and final diagnosis reports.</li>
                    <li><strong>Chat Messages:</strong> Follow-up questions and AI responses.</li>
                    <li><strong>Usage Data:</strong> Diagnosis count, specialist usage, and activity timestamps.</li>
                </ul>
            </div>

            <div className={styles.section}>
                <h2>2. How We Use Your Data</h2>
                <ul>
                    <li>To provide AI-powered medical report analysis.</li>
                    <li>To maintain your diagnosis history and enable follow-up conversations.</li>
                    <li>To generate anonymous aggregate statistics for platform improvement.</li>
                    <li>We do NOT sell your data to third parties.</li>
                </ul>
            </div>

            <div className={styles.section}>
                <h2>3. Data Storage & Security</h2>
                <p>
                    Your data is stored in MongoDB Atlas with encryption at rest. Data is transmitted
                    over HTTPS. We follow HIPAA-aware security principles, though we are not a HIPAA-covered entity.
                </p>
            </div>

            <div className={styles.section}>
                <h2>4. Third-Party Services</h2>
                <ul>
                    <li><strong>Google OAuth 2.0:</strong> For secure authentication.</li>
                    <li><strong>OpenAI GPT-4.1:</strong> For medical report analysis. Report content is sent to
                        OpenAI&apos;s API for processing but is not stored by OpenAI for training purposes.</li>
                    <li><strong>MongoDB Atlas:</strong> For secure cloud database hosting.</li>
                </ul>
            </div>

            <div className={styles.section}>
                <h2>5. Your Rights</h2>
                <ul>
                    <li>You can view all your stored data through the Dashboard and History pages.</li>
                    <li>You can delete individual diagnoses, reports, and chat sessions at any time.</li>
                    <li>You can request complete account deletion by contacting us.</li>
                    <li>You control whether reports are stored in your history (opt-out at upload time).</li>
                </ul>
            </div>

            <div className={styles.section}>
                <h2>6. Data Retention</h2>
                <p>
                    We retain your data for as long as your account is active. If you delete specific data
                    (reports, diagnoses), it is permanently removed from our database. Account deletion
                    removes all associated data.
                </p>
            </div>

            <div className={styles.section}>
                <h2>7. Contact</h2>
                <p>
                    For privacy questions or data deletion requests, contact us at <strong>privacy@cura3.ai</strong>.
                </p>
            </div>
        </div>
    );
}
