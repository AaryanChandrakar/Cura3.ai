'use client';

import React, { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import Sidebar from '@/components/Sidebar/Sidebar';
import {
    uploadReport,
    submitTextReport,
    autoSelectSpecialists,
    runDiagnosis,
    listSpecialists,
} from '@/lib/api';
import styles from './page.module.css';

type UploadMode = 'file' | 'text';
type Step = 'upload' | 'specialists' | 'running' | 'done';

interface SpecialistInfo {
    name: string;
    display_name: string;
    icon: string;
}

const SPECIALIST_ICONS: Record<string, string> = {
    Cardiologist: '❤️',
    Psychologist: '🧠',
    Pulmonologist: '🫁',
    Neurologist: '🧬',
    Endocrinologist: '⚗️',
    Oncologist: '🔬',
    Dermatologist: '🩺',
    Gastroenterologist: '🏥',
    Orthopedist: '🦴',
    'General Practitioner': '👨‍⚕️',
};

export default function AnalyzePage() {
    const { loading, isAuthenticated } = useAuth();
    const router = useRouter();
    const fileInputRef = useRef<HTMLInputElement>(null);

    // Step state
    const [step, setStep] = useState<Step>('upload');

    // Upload state
    const [mode, setMode] = useState<UploadMode>('file');
    const [file, setFile] = useState<File | null>(null);
    const [textContent, setTextContent] = useState('');
    const [patientName, setPatientName] = useState('');
    const [storeReport, setStoreReport] = useState(true);
    const [uploading, setUploading] = useState(false);
    const [reportId, setReportId] = useState<string | null>(null);

    // Specialist state
    const [allSpecialists, setAllSpecialists] = useState<SpecialistInfo[]>([]);
    const [recommended, setRecommended] = useState<string[]>([]);
    const [selected, setSelected] = useState<string[]>([]);
    const [selectingSpecialists, setSelectingSpecialists] = useState(false);

    // Diagnosis state
    const [_running, setRunning] = useState(false);
    const [diagnosisId, setDiagnosisId] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);

    // Progress tracking
    const [progress, setProgress] = useState(0);
    const [progressMessage, setProgressMessage] = useState('');

    useEffect(() => {
        if (!loading && !isAuthenticated) router.push('/');
    }, [loading, isAuthenticated, router]);

    useEffect(() => {
        listSpecialists()
            .then((res) => setAllSpecialists(res.specialists || []))
            .catch(() => { });
    }, []);

    // Handle file drop
    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        const dropped = e.dataTransfer.files[0];
        if (dropped) setFile(dropped);
    };

    // Handle upload
    const handleUpload = async () => {
        setError(null);
        setUploading(true);

        try {
            let result;
            if (mode === 'file' && file) {
                result = await uploadReport(file, patientName || 'Unknown Patient', storeReport);
            } else if (mode === 'text' && textContent.trim()) {
                result = await submitTextReport(textContent, patientName || 'Unknown Patient', storeReport);
            } else {
                setError('Please provide a file or text content.');
                setUploading(false);
                return;
            }

            setReportId(result.id);

            // Auto-select specialists
            setSelectingSpecialists(true);
            try {
                const autoResult = await autoSelectSpecialists(result.id);
                setRecommended(autoResult.recommended_specialists || []);
                setSelected(autoResult.recommended_specialists || []);
            } catch {
                // fallback to default selection
                setSelected(['Cardiologist', 'Neurologist', 'General Practitioner']);
            }
            setSelectingSpecialists(false);
            setStep('specialists');
        } catch (err: unknown) {
            setError(err instanceof Error ? err.message : 'Upload failed');
        } finally {
            setUploading(false);
        }
    };

    // Toggle specialist
    const toggleSpecialist = (name: string) => {
        setSelected((prev) =>
            prev.includes(name) ? prev.filter((s) => s !== name) : [...prev, name]
        );
    };

    // Run diagnosis
    const handleRunDiagnosis = async () => {
        if (!reportId || selected.length === 0) return;
        setError(null);
        setRunning(true);
        setStep('running');
        setProgress(0);
        setProgressMessage('Initializing AI agents...');

        // Simulate progress updates
        const progressInterval = setInterval(() => {
            setProgress((prev) => {
                if (prev >= 90) return 90;
                const increment = Math.random() * 15;
                const next = Math.min(prev + increment, 90);
                if (next < 20) setProgressMessage('Sending report to specialists...');
                else if (next < 40) setProgressMessage('Specialists are analyzing...');
                else if (next < 60) setProgressMessage('Cross-referencing findings...');
                else if (next < 80) setProgressMessage('Generating final diagnosis...');
                else setProgressMessage('Finalizing report...');
                return next;
            });
        }, 800);

        try {
            const result = await runDiagnosis(reportId, selected);
            clearInterval(progressInterval);
            setProgress(100);
            setProgressMessage('Diagnosis complete!');
            setDiagnosisId(result.id);
            setStep('done');
        } catch (err: unknown) {
            clearInterval(progressInterval);
            setError(err instanceof Error ? err.message : 'Diagnosis failed');
            setStep('specialists');
            setRunning(false);
        }
    };

    if (loading || !isAuthenticated) {
        return (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh' }}>
                <div className="spinner spinner-lg" />
            </div>
        );
    }

    return (
        <div className="page-layout">
            <Sidebar />
            <main className="page-content">
                <h1 className="page-title">New Diagnosis</h1>
                <p className="page-subtitle">Upload a medical report and let the AI team analyze it.</p>

                {error && (
                    <div className="alert alert-danger" style={{ marginBottom: 24 }}>
                        <span>⚠️</span> {error}
                    </div>
                )}

                {/* Step 1: Upload */}
                {step === 'upload' && (
                    <div className={`card ${styles.uploadCard}`}>
                        {/* Mode Toggle */}
                        <div className={styles.modeToggle}>
                            <button
                                className={`${styles.modeBtn} ${mode === 'file' ? styles.active : ''}`}
                                onClick={() => setMode('file')}
                            >
                                📁 Upload File
                            </button>
                            <button
                                className={`${styles.modeBtn} ${mode === 'text' ? styles.active : ''}`}
                                onClick={() => setMode('text')}
                            >
                                ✏️ Paste Text
                            </button>
                        </div>

                        {/* File Upload Zone */}
                        {mode === 'file' && (
                            <div
                                className={styles.dropZone}
                                onDragOver={(e) => e.preventDefault()}
                                onDrop={handleDrop}
                                onClick={() => fileInputRef.current?.click()}
                            >
                                <input
                                    ref={fileInputRef}
                                    type="file"
                                    accept=".txt,.pdf,.docx"
                                    onChange={(e) => setFile(e.target.files?.[0] || null)}
                                    style={{ display: 'none' }}
                                />
                                {file ? (
                                    <div className={styles.fileInfo}>
                                        <span className={styles.fileIcon}>📄</span>
                                        <span className={styles.fileName}>{file.name}</span>
                                        <span className={styles.fileSize}>
                                            ({(file.size / 1024).toFixed(1)} KB)
                                        </span>
                                        <button
                                            className="btn btn-ghost btn-sm"
                                            onClick={(e) => { e.stopPropagation(); setFile(null); }}
                                        >
                                            ✕
                                        </button>
                                    </div>
                                ) : (
                                    <div className={styles.dropContent}>
                                        <span className={styles.dropIcon}>📤</span>
                                        <p className={styles.dropTitle}>Drag & drop your medical report here</p>
                                        <p className={styles.dropHint}>
                                            or click to browse — Supports .txt, .pdf, .docx (max 10MB)
                                        </p>
                                    </div>
                                )}
                            </div>
                        )}

                        {/* Text Paste Area */}
                        {mode === 'text' && (
                            <textarea
                                className="textarea-field"
                                placeholder="Paste the full medical report text here..."
                                value={textContent}
                                onChange={(e) => setTextContent(e.target.value)}
                                style={{ minHeight: 220 }}
                            />
                        )}

                        {/* Patient Name & Options */}
                        <div className={styles.formRow}>
                            <div className="input-group" style={{ flex: 1 }}>
                                <label className="input-label">Patient Name</label>
                                <input
                                    type="text"
                                    className="input-field"
                                    placeholder="e.g. James Carter"
                                    value={patientName}
                                    onChange={(e) => setPatientName(e.target.value)}
                                />
                            </div>
                            <label className={styles.checkbox}>
                                <input
                                    type="checkbox"
                                    checked={storeReport}
                                    onChange={(e) => setStoreReport(e.target.checked)}
                                />
                                <span>Store report in my history</span>
                            </label>
                        </div>

                        <button
                            className="btn btn-primary btn-lg"
                            onClick={handleUpload}
                            disabled={uploading || (mode === 'file' ? !file : !textContent.trim())}
                            style={{ width: '100%', marginTop: 16 }}
                        >
                            {uploading ? (
                                <>
                                    <div className="spinner" style={{ width: 18, height: 18, borderWidth: 2 }} />
                                    Uploading...
                                </>
                            ) : (
                                'Upload & Continue →'
                            )}
                        </button>
                    </div>
                )}

                {/* Step 2: Select Specialists */}
                {step === 'specialists' && (
                    <div className={`card ${styles.specialistCard}`}>
                        <h2 className={styles.stepTitle}>
                            🩺 Select Specialists
                        </h2>
                        <p className={styles.stepDesc}>
                            AI has recommended the best specialists for this report.
                            You can add or remove any.
                        </p>

                        {selectingSpecialists ? (
                            <div style={{ display: 'flex', alignItems: 'center', gap: 12, padding: 24 }}>
                                <div className="spinner" />
                                <span>AI is analyzing the report to recommend specialists...</span>
                            </div>
                        ) : (
                            <>
                                <div className={styles.chipGrid}>
                                    {allSpecialists.map((s) => (
                                        <button
                                            key={s.name}
                                            className={`specialist-chip ${selected.includes(s.name) ? 'selected' : ''} ${recommended.includes(s.name) ? 'recommended' : ''}`}
                                            onClick={() => toggleSpecialist(s.name)}
                                        >
                                            <span>{SPECIALIST_ICONS[s.name] || '👨‍⚕️'}</span>
                                            {s.display_name}
                                        </button>
                                    ))}
                                </div>

                                <div className={styles.selectedCount}>
                                    {selected.length} specialist{selected.length !== 1 ? 's' : ''} selected
                                </div>

                                <div className={styles.actionRow}>
                                    <button
                                        className="btn btn-ghost"
                                        onClick={() => { setStep('upload'); setReportId(null); }}
                                    >
                                        ← Back
                                    </button>
                                    <button
                                        className="btn btn-primary btn-lg"
                                        onClick={handleRunDiagnosis}
                                        disabled={selected.length === 0}
                                    >
                                        Run Diagnosis ({selected.length} specialists) →
                                    </button>
                                </div>
                            </>
                        )}
                    </div>
                )}

                {/* Step 3: Running */}
                {step === 'running' && (
                    <div className={`card ${styles.runningCard}`}>
                        <div className={styles.runningContent}>
                            <div className={styles.runningIcon}>
                                <div className="spinner spinner-lg" />
                            </div>
                            <h2 className={styles.runningTitle}>AI Team at Work</h2>
                            <p className={styles.runningMessage}>{progressMessage}</p>
                            <div className={styles.progressBar}>
                                <div
                                    className={styles.progressFill}
                                    style={{ width: `${progress}%` }}
                                />
                            </div>
                            <span className={styles.progressPercent}>{Math.round(progress)}%</span>
                            <div className={styles.runningSpecialists}>
                                {selected.map((s) => (
                                    <span key={s} className="badge badge-primary">
                                        {SPECIALIST_ICONS[s] || '👨‍⚕️'} {s}
                                    </span>
                                ))}
                            </div>
                        </div>
                    </div>
                )}

                {/* Step 4: Done */}
                {step === 'done' && (
                    <div className={`card ${styles.doneCard}`}>
                        <div className={styles.doneContent}>
                            <span className={styles.doneIcon}>✅</span>
                            <h2 className={styles.doneTitle}>Diagnosis Complete!</h2>
                            <p className={styles.doneMessage}>
                                Your medical report has been analyzed by {selected.length} specialists.
                            </p>
                            <div className={styles.doneActions}>
                                <button
                                    className="btn btn-primary btn-lg"
                                    onClick={() => router.push(`/diagnosis/${diagnosisId}`)}
                                >
                                    View Full Diagnosis →
                                </button>
                                <button
                                    className="btn btn-outline"
                                    onClick={() => {
                                        setStep('upload');
                                        setFile(null);
                                        setTextContent('');
                                        setPatientName('');
                                        setReportId(null);
                                        setDiagnosisId(null);
                                        setProgress(0);
                                        setRunning(false);
                                    }}
                                >
                                    Run Another Diagnosis
                                </button>
                            </div>
                        </div>
                    </div>
                )}

                {/* Disclaimer */}
                <div className="alert alert-warning" style={{ marginTop: 24 }}>
                    <span>⚠️</span>
                    <span>
                        <strong>Medical Disclaimer:</strong> This AI tool is for research and educational
                        purposes only. It is NOT a substitute for professional medical advice,
                        diagnosis, or treatment. Always consult a qualified healthcare provider.
                    </span>
                </div>
            </main>
        </div>
    );
}
