'use client';

import React, { useEffect, useRef } from 'react';

interface DataPoint {
    label: string;
    value: number;
}

interface TimeSeriesChartProps {
    data: DataPoint[];
    width?: number;
    height?: number;
    color?: string;
    gradientFrom?: string;
    gradientTo?: string;
    showArea?: boolean;
    emptyText?: string;
}

/**
 * Lightweight time-series line/area chart rendered on HTML5 Canvas.
 * Zero dependencies — no chart library needed.
 */
export default function TimeSeriesChart({
    data,
    width = 600,
    height = 220,
    color = '#0A6EBD',
    gradientFrom = 'rgba(10, 110, 189, 0.25)',
    gradientTo = 'rgba(10, 110, 189, 0.02)',
    showArea = true,
    emptyText = 'No data available',
}: TimeSeriesChartProps) {
    const canvasRef = useRef<HTMLCanvasElement>(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas || data.length === 0) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        const dpr = window.devicePixelRatio || 1;
        canvas.width = width * dpr;
        canvas.height = height * dpr;
        ctx.scale(dpr, dpr);
        ctx.clearRect(0, 0, width, height);

        const padding = { top: 24, right: 24, bottom: 36, left: 48 };
        const chartW = width - padding.left - padding.right;
        const chartH = height - padding.top - padding.bottom;

        const maxVal = Math.max(...data.map((d) => d.value), 1);

        // Grid lines + Y-axis labels
        ctx.strokeStyle = '#E2E8F0';
        ctx.lineWidth = 0.5;
        ctx.fillStyle = '#A0AEC0';
        ctx.font = '10px Inter, sans-serif';
        ctx.textAlign = 'right';

        for (let i = 0; i <= 4; i++) {
            const y = padding.top + (chartH / 4) * i;
            ctx.beginPath();
            ctx.setLineDash([4, 4]);
            ctx.moveTo(padding.left, y);
            ctx.lineTo(width - padding.right, y);
            ctx.stroke();
            ctx.setLineDash([]);

            const label = Math.round(maxVal * (1 - i / 4));
            ctx.fillText(String(label), padding.left - 8, y + 3);
        }

        // Compute points
        const points = data.map((d, i) => ({
            x: padding.left + (chartW / Math.max(data.length - 1, 1)) * i,
            y: padding.top + chartH - (d.value / maxVal) * chartH,
        }));

        // Area fill (gradient under the line)
        if (showArea && points.length >= 2) {
            const areaGrad = ctx.createLinearGradient(0, padding.top, 0, padding.top + chartH);
            areaGrad.addColorStop(0, gradientFrom);
            areaGrad.addColorStop(1, gradientTo);

            ctx.beginPath();
            ctx.moveTo(points[0].x, padding.top + chartH);
            points.forEach((p) => ctx.lineTo(p.x, p.y));
            ctx.lineTo(points[points.length - 1].x, padding.top + chartH);
            ctx.closePath();
            ctx.fillStyle = areaGrad;
            ctx.fill();
        }

        // Smooth line using quadratic curves
        if (points.length >= 2) {
            ctx.beginPath();
            ctx.strokeStyle = color;
            ctx.lineWidth = 2.5;
            ctx.lineJoin = 'round';
            ctx.lineCap = 'round';

            ctx.moveTo(points[0].x, points[0].y);
            for (let i = 1; i < points.length; i++) {
                const prev = points[i - 1];
                const curr = points[i];
                const midX = (prev.x + curr.x) / 2;
                const midY = (prev.y + curr.y) / 2;
                ctx.quadraticCurveTo(prev.x, prev.y, midX, midY);
            }
            ctx.lineTo(points[points.length - 1].x, points[points.length - 1].y);
            ctx.stroke();
        }

        // Data points (dots)
        const dotsToShow = data.length > 30 ? 0 : data.length;
        if (dotsToShow > 0) {
            points.forEach((p) => {
                ctx.beginPath();
                ctx.arc(p.x, p.y, 3, 0, Math.PI * 2);
                ctx.fillStyle = '#FFFFFF';
                ctx.fill();
                ctx.strokeStyle = color;
                ctx.lineWidth = 2;
                ctx.stroke();
            });
        }

        // X-axis labels
        const labelEvery = Math.max(1, Math.floor(data.length / 7));
        ctx.fillStyle = '#A0AEC0';
        ctx.font = '9px Inter, sans-serif';
        ctx.textAlign = 'center';
        data.forEach((d, i) => {
            if (i % labelEvery === 0 || i === data.length - 1) {
                const x = padding.left + (chartW / Math.max(data.length - 1, 1)) * i;
                ctx.fillText(d.label, x, height - padding.bottom + 16);
            }
        });
    }, [data, width, height, color, gradientFrom, gradientTo, showArea]);

    if (data.length === 0) {
        return (
            <div style={{
                width, height,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#A0AEC0',
                fontSize: '14px',
            }}>
                {emptyText}
            </div>
        );
    }

    return (
        <canvas
            ref={canvasRef}
            style={{ width, height, display: 'block', maxWidth: '100%' }}
        />
    );
}
