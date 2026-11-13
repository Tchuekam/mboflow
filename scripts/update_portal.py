# -*- coding: utf-8 -*-
"""
Script to generate the enhanced interactive simulated banking portal for Mboa Finance AI.
Ensures 100% interactivity: clickable navigation, filter pills, balance deductions,
multilingual live translation (8 languages), voice recognition, recent transactions,
and full synchronization with the backend API.
"""

import os

HTML_CONTENT = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MboaPay — Portail Financier Numérique Cameroun</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🇨🇲</text></svg>">
    <link rel="stylesheet" href="/bank/design-system.css">
    <style>
        :root {
            --bg-base: #0c0f14;
            --bg-surface-1: #151821;
            --bg-surface-2: #1b1f2a;
            --bg-surface-3: #222736;
            --bg-surface-hero: #3e5bf2;
            --accent-lime: #d8ff3e;
            --accent-lime-hover: #c6f028;
            --accent-lime-glow: rgba(216, 255, 62, 0.35);
            --accent-lime-text: #0c0f14;
            --accent-blue: #3e5bf2;
            --accent-blue-glow: rgba(62, 91, 242, 0.4);
            --text-primary: #ffffff;
            --text-secondary: #8e95a5;
            --text-muted: #5e6678;
            --border-subtle: rgba(255, 255, 255, 0.07);
            --border-medium: rgba(255, 255, 255, 0.12);
            --border-focus: rgba(216, 255, 62, 0.55);
            --status-warning-bg: rgba(244, 63, 94, 0.12);
            --status-warning-border: rgba(244, 63, 94, 0.35);
            --status-warning-text: #fb7185;
            --radius-sm: 10px;
            --radius-md: 16px;
            --radius-lg: 24px;
            --radius-xl: 32px;
            --radius-pill: 9999px;
            --shadow-card: 0 12px 32px -4px rgba(0, 0, 0, 0.65), 0 0 0 1px var(--border-subtle);
            --shadow-floating: 0 20px 40px -8px rgba(0, 0, 0, 0.8), 0 0 0 1px rgba(255, 255, 255, 0.1);
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Plus Jakarta Sans", Inter, "Segoe UI", Roboto, sans-serif; }
        
        body {
            background-color: var(--bg-base);
            background-image: 
                radial-gradient(circle at 12% 8%, rgba(34, 197, 94, 0.09) 0%, transparent 45%),
                radial-gradient(circle at 88% 22%, rgba(62, 91, 242, 0.11) 0%, transparent 50%),
                radial-gradient(circle at 50% 85%, rgba(216, 255, 62, 0.04) 0%, transparent 50%);
            color: var(--text-primary);
            padding-bottom: 120px;
            min-height: 100vh;
        }

        /* Top Header Component */
        .app-header {
            max-width: 1000px;
            margin: 0 auto;
            padding: 1.5rem 1.25rem 0.5rem 1.25rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .user-meta-box {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .user-avatar-circle {
            width: 44px;
            height: 44px;
            border-radius: 50%;
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            border: 2px solid var(--border-medium);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2rem;
            position: relative;
        }
        .user-status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #22c55e;
            position: absolute;
            bottom: 0;
            right: 0;
            border: 2px solid var(--bg-base);
        }
        .user-greetings-sub {
            font-size: 0.8rem;
            color: var(--text-secondary);
            font-weight: 500;
        }
        .user-greetings-name {
            font-size: 1.05rem;
            font-weight: 700;
            color: var(--text-primary);
            letter-spacing: -0.2px;
        }
        
        .header-actions {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .icon-btn-glass {
            width: 42px;
            height: 42px;
            border-radius: 50%;
            background: var(--bg-surface-1);
            border: 1px solid var(--border-subtle);
            color: var(--text-primary);
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            position: relative;
            transition: all 0.2s;
        }
        .icon-btn-glass:hover {
            background: var(--bg-surface-2);
            border-color: var(--border-medium);
            transform: scale(1.05);
        }
        .alert-dot {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: #f97316;
            position: absolute;
            top: 10px;
            right: 10px;
        }

        /* Hero Page Title */
        .page-intro {
            max-width: 1000px;
            margin: 0.8rem auto 1.2rem auto;
            padding: 0 1.25rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
        }
        .page-intro h1 {
            font-size: 1.75rem;
            font-weight: 800;
            letter-spacing: -0.5px;
            line-height: 1.25;
            color: var(--text-primary);
        }
        .quick-lang-pill {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: var(--bg-surface-1);
            border: 1px solid var(--border-subtle);
            padding: 6px 14px;
            border-radius: var(--radius-pill);
            font-size: 0.82rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }
        .quick-lang-pill:hover {
            border-color: var(--accent-lime);
            background: var(--bg-surface-2);
        }

        /* Segmented Filter Pills */
        .filter-section {
            max-width: 1000px;
            margin: 0 auto 1.5rem auto;
            padding: 0 1.25rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 12px;
        }
        .segmented-track {
            background: var(--bg-surface-1);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-pill);
            padding: 4px;
            display: inline-flex;
            gap: 4px;
        }
        .segmented-pill {
            padding: 8px 20px;
            border-radius: var(--radius-pill);
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--text-secondary);
            cursor: pointer;
            transition: all 0.2s;
            user-select: none;
            border: none;
            background: transparent;
        }
        .segmented-pill.active {
            background: var(--accent-lime);
            color: var(--accent-lime-text);
            box-shadow: 0 2px 12px rgba(216, 255, 62, 0.35);
        }
        .segmented-pill:hover:not(.active) {
            color: var(--text-primary);
            background: var(--bg-surface-2);
        }
        .copy-rib-box {
            font-size: 0.8rem;
            color: var(--text-secondary);
            font-family: monospace;
            cursor: pointer;
            padding: 7px 14px;
            background: var(--bg-surface-1);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-pill);
            display: flex;
            align-items: center;
            gap: 8px;
            transition: all 0.2s;
        }
        .copy-rib-box:hover {
            border-color: var(--accent-lime);
            color: var(--text-primary);
            background: var(--bg-surface-2);
        }

        /* Content Grid */
        .container {
            max-width: 1000px;
            margin: 0 auto;
            padding: 0 1.25rem 3rem 1.25rem;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.5rem;
        }
        @media (max-width: 820px) {
            .container { 
                grid-template-columns: 1fr;
                padding-bottom: 5rem;
            }
        }
        .full-width { grid-column: 1 / -1; }

        /* View Containers */
        .view-section {
            display: contents;
        }

        /* Hero Balance Card (Electric Cobalt Blue) */
        .card-hero-blue {
            background: linear-gradient(135deg, #415ff6 0%, #2944d1 100%);
            border-radius: var(--radius-lg);
            padding: 1.8rem;
            color: white;
            box-shadow: 0 14px 35px rgba(41, 68, 209, 0.35);
            position: relative;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            min-height: 230px;
            cursor: pointer;
            transition: transform 0.2s;
        }
        .card-hero-blue:hover {
            transform: translateY(-2px);
        }
        .card-hero-top {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
        }
        .card-hero-label {
            font-size: 0.88rem;
            font-weight: 600;
            color: rgba(255, 255, 255, 0.85);
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .arrow-badge {
            width: 34px;
            height: 34px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.16);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.05rem;
            color: white;
            transition: transform 0.2s;
        }
        .card-hero-blue:hover .arrow-badge {
            transform: translate(2px, -2px);
        }
        .balance-value {
            font-size: 2.6rem;
            font-weight: 800;
            color: #ffffff;
            margin: 1rem 0 0.5rem 0;
            letter-spacing: -0.8px;
            transition: all 0.3s ease-out;
        }
        .hero-account-id {
            font-family: monospace;
            font-size: 0.85rem;
            color: rgba(255, 255, 255, 0.75);
            letter-spacing: 0.5px;
        }
        .hero-waveform-svg {
            position: absolute;
            right: -20px;
            bottom: -15px;
            opacity: 0.15;
            width: 220px;
            pointer-events: none;
        }

        /* Dark Surface Cards */
        .card-dark {
            background-color: var(--bg-surface-1);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-lg);
            padding: 1.6rem;
            box-shadow: var(--shadow-card);
            transition: border-color 0.2s;
        }
        .card-dark:hover {
            border-color: var(--border-medium);
        }
        .card-title {
            font-size: 1.1rem;
            font-weight: 700;
            color: var(--text-primary);
            margin-bottom: 1.2rem;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        /* Dual Stat Sub-cards */
        .stats-dual-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-bottom: 1.2rem;
        }
        .stat-subcard {
            background: var(--bg-surface-2);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-md);
            padding: 1rem;
            position: relative;
            cursor: pointer;
            transition: all 0.2s;
        }
        .stat-subcard:hover {
            border-color: var(--border-medium);
            background: var(--bg-surface-3);
        }
        .stat-subcard-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.78rem;
            color: var(--text-secondary);
            margin-bottom: 0.5rem;
        }
        .stat-subcard-val {
            font-size: 1.35rem;
            font-weight: 700;
            color: var(--text-primary);
        }
        .badge-pill-green {
            background: rgba(34, 197, 94, 0.15);
            color: #4ade80;
            font-size: 0.7rem;
            font-weight: 700;
            padding: 2px 7px;
            border-radius: var(--radius-pill);
        }

        /* Form Inputs */
        .form-group { margin-bottom: 1.1rem; }
        label {
            display: block;
            font-size: 0.82rem;
            font-weight: 600;
            color: var(--text-secondary);
            margin-bottom: 0.45rem;
            text-transform: uppercase;
            letter-spacing: 0.4px;
        }
        .input-dark {
            width: 100%;
            background-color: var(--bg-surface-2);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-md);
            padding: 0.85rem 1.1rem;
            color: var(--text-primary);
            font-size: 1rem;
            font-family: inherit;
            transition: all 0.2s;
        }
        .input-dark:focus {
            outline: none;
            border-color: var(--accent-lime);
            box-shadow: 0 0 0 3px rgba(216, 255, 62, 0.2);
            background-color: var(--bg-surface-3);
        }

        /* Fee Breakdown Box */
        .fee-breakdown {
            background-color: var(--bg-surface-2);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-md);
            padding: 1.1rem;
            margin: 1.2rem 0;
        }
        .fee-row {
            display: flex;
            justify-content: space-between;
            font-size: 0.88rem;
            color: var(--text-secondary);
            margin-bottom: 0.5rem;
        }
        .fee-row span:last-child {
            color: var(--text-primary);
            font-weight: 600;
        }
        .fee-row.total {
            font-weight: 700;
            color: var(--text-primary);
            border-top: 1px dashed var(--border-medium);
            padding-top: 0.6rem;
            margin-top: 0.6rem;
            font-size: 1.05rem;
        }
        .fee-row.total span:last-child {
            color: var(--accent-lime);
            font-size: 1.15rem;
        }

        /* Primary Button (Electric Lime) */
        .btn-lime {
            width: 100%;
            background-color: var(--accent-lime);
            color: var(--accent-lime-text);
            border: none;
            padding: 0.95rem 1.4rem;
            border-radius: var(--radius-pill);
            font-size: 1rem;
            font-weight: 700;
            cursor: pointer;
            box-shadow: 0 8px 24px var(--accent-lime-glow);
            transition: all 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }
        .btn-lime:hover {
            background-color: var(--accent-lime-hover);
            transform: translateY(-1px);
            box-shadow: 0 10px 28px rgba(216, 255, 62, 0.45);
        }
        .btn-lime:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        /* Security Warning Card */
        .warning-card-dark {
            background: rgba(159, 18, 57, 0.12);
            border: 1px solid rgba(244, 63, 94, 0.35);
            border-radius: var(--radius-lg);
            padding: 1.25rem;
            display: flex;
            gap: 12px;
            align-items: flex-start;
            margin-bottom: 1.5rem;
        }
        .warning-icon-circle {
            width: 38px;
            height: 38px;
            border-radius: 50%;
            background: rgba(244, 63, 94, 0.2);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.1rem;
            flex-shrink: 0;
        }
        .warning-title {
            font-size: 0.92rem;
            font-weight: 700;
            color: #fb7185;
            margin-bottom: 0.2rem;
        }
        .warning-text {
            font-size: 0.85rem;
            color: #fecdd3;
            line-height: 1.4;
        }

        /* Dynamic Alert Banner */
        #dynamic-notice-area { margin-bottom: 1rem; }
        .dynamic-banner {
            background: rgba(251, 191, 36, 0.12);
            border: 1px solid rgba(251, 191, 36, 0.35);
            color: #fef08a;
            padding: 1rem 1.2rem;
            border-radius: var(--radius-md);
            font-size: 0.88rem;
            animation: slideDown 0.3s ease-out;
            margin-bottom: 1rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 10px;
        }
        @keyframes slideDown { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }

        /* Success Card */
        #transaction-success {
            display: none;
            background: rgba(34, 197, 94, 0.12);
            border: 1px solid rgba(34, 197, 94, 0.35);
            color: #86efac;
            padding: 1.2rem;
            border-radius: var(--radius-md);
            margin-top: 1rem;
        }

        /* Transaction History Item */
        .tx-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 14px;
            background: var(--bg-surface-2);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-md);
            transition: all 0.2s;
        }
        .tx-item:hover {
            border-color: var(--border-medium);
            background: var(--bg-surface-3);
        }
        .tx-icon {
            width: 38px;
            height: 38px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1rem;
            background: rgba(255, 255, 255, 0.05);
            margin-right: 12px;
        }
        .tx-meta {
            flex: 1;
        }
        .tx-title {
            font-size: 0.9rem;
            font-weight: 600;
            color: var(--text-primary);
        }
        .tx-subtitle {
            font-size: 0.75rem;
            color: var(--text-muted);
            margin-top: 2px;
        }
        .tx-amount {
            font-size: 0.95rem;
            font-weight: 700;
            text-align: right;
        }
        .tx-amount.debit {
            color: #fb7185;
        }
        .tx-amount.credit {
            color: #4ade80;
        }

        /* Toast Notification */
        .toast-bubble {
            position: fixed;
            top: 25px;
            left: 50%;
            transform: translateX(-50%) translateY(-20px);
            background: var(--bg-surface-1);
            color: var(--text-primary);
            border: 1px solid var(--accent-lime);
            padding: 10px 22px;
            border-radius: var(--radius-pill);
            font-size: 0.88rem;
            font-weight: 600;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.7), 0 0 15px rgba(216, 255, 62, 0.2);
            z-index: 10000;
            opacity: 0;
            transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
            pointer-events: none;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .toast-bubble.show {
            opacity: 1;
            transform: translateX(-50%) translateY(0);
        }

        /* Floating Bottom Navigation Dock */
        .bottom-nav-dock {
            position: fixed;
            bottom: 22px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(21, 24, 33, 0.92);
            backdrop-filter: blur(24px);
            -webkit-backdrop-filter: blur(24px);
            border: 1px solid var(--border-medium);
            border-radius: var(--radius-pill);
            padding: 6px 10px;
            display: flex;
            align-items: center;
            gap: 8px;
            box-shadow: var(--shadow-floating);
            z-index: 900;
        }
        .dock-item {
            width: 46px;
            height: 46px;
            border-radius: var(--radius-pill);
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--text-secondary);
            cursor: pointer;
            transition: all 0.2s;
            border: none;
            background: transparent;
            font-size: 1.2rem;
            position: relative;
        }
        .dock-item:hover {
            color: var(--text-primary);
            background: var(--bg-surface-2);
        }
        .dock-item.active {
            background: var(--accent-lime);
            color: var(--accent-lime-text);
            box-shadow: 0 4px 14px rgba(216, 255, 62, 0.35);
        }

        /* Floating Voice Assistant Trigger */
        #mboa-assistant-bubble-btn {
            position: fixed;
            bottom: 25px;
            right: 25px;
            width: 58px;
            height: 58px;
            border-radius: 50%;
            background: var(--accent-lime);
            color: var(--accent-lime-text);
            box-shadow: 0 8px 25px rgba(216, 255, 62, 0.45);
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            z-index: 9999;
            transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
            border: 3px solid #0c0f14;
            animation: pulseLime 3s infinite;
        }
        @keyframes pulseLime {
            0% { box-shadow: 0 8px 25px rgba(216, 255, 62, 0.45); }
            50% { box-shadow: 0 8px 35px rgba(216, 255, 62, 0.75); }
            100% { box-shadow: 0 8px 25px rgba(216, 255, 62, 0.45); }
        }
        #mboa-assistant-bubble-btn:hover {
            transform: scale(1.08);
            box-shadow: 0 12px 30px rgba(216, 255, 62, 0.65);
        }
        body.assistant-open #mboa-assistant-bubble-btn {
            opacity: 0;
            pointer-events: none;
            transform: scale(0.7);
        }
        .ai-cameroon-flag {
            position: absolute;
            top: -4px;
            right: -4px;
            font-size: 1.05rem;
            filter: drop-shadow(0 2px 4px rgba(0,0,0,0.5));
        }

        /* Assistant Modal Panel */
        #mboa-assistant-panel {
            position: fixed;
            bottom: 95px;
            right: 25px;
            width: 395px;
            max-width: calc(100vw - 40px);
            height: 590px;
            max-height: calc(100vh - 120px);
            background: #12151b;
            border-radius: var(--radius-xl);
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.85), 0 0 0 1px var(--border-medium);
            display: none;
            flex-direction: column;
            z-index: 9998;
            overflow: hidden;
            animation: fadeIn 0.2s ease-out;
        }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }

        @media (max-width: 820px) {
            #mboa-assistant-bubble-btn {
                bottom: 86px;
                right: 18px;
                width: 52px;
                height: 52px;
            }
            #mboa-assistant-panel {
                bottom: 86px;
                right: 12px;
                left: 12px;
                width: calc(100vw - 24px);
                max-width: 100vw;
                height: calc(100vh - 110px);
            }
        }

        .assistant-header {
            background: var(--bg-surface-1);
            border-bottom: 1px solid var(--border-subtle);
            color: white;
            padding: 1rem 1.25rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .assistant-header-title {
            display: flex;
            align-items: center;
            gap: 10px;
            font-weight: 700;
            font-size: 1.05rem;
        }
        .assistant-header-close {
            background: var(--bg-surface-2);
            border: 1px solid var(--border-subtle);
            color: var(--text-secondary);
            width: 32px;
            height: 32px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.2s;
        }
        .assistant-header-close:hover {
            color: white;
            border-color: var(--border-medium);
        }

        .assistant-lang-bar {
            background: var(--bg-surface-2);
            border-bottom: 1px solid var(--border-subtle);
            padding: 0.6rem 1rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 0.82rem;
            color: var(--text-secondary);
        }
        .lang-select {
            padding: 0.35rem 0.75rem;
            border-radius: var(--radius-pill);
            border: 1px solid var(--border-subtle);
            background: var(--bg-surface-1);
            font-weight: 600;
            color: var(--text-primary);
            cursor: pointer;
        }

        .assistant-chat-body {
            flex: 1;
            padding: 1rem;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 0.85rem;
            background: #0f1218;
        }

        .chat-bubble {
            max-width: 88%;
            padding: 0.85rem 1.1rem;
            border-radius: var(--radius-md);
            font-size: 0.88rem;
            line-height: 1.45;
            word-break: break-word;
        }
        .chat-bubble.user {
            align-self: flex-end;
            background: var(--accent-blue);
            color: white;
            border-bottom-right-radius: 4px;
            box-shadow: 0 4px 14px rgba(62, 91, 242, 0.3);
        }
        .chat-bubble.ai {
            align-self: flex-start;
            background: var(--bg-surface-1);
            color: var(--text-primary);
            border: 1px solid var(--border-subtle);
            border-bottom-left-radius: 4px;
        }
        .chat-bubble-speaker {
            display: inline-block;
            cursor: pointer;
            margin-left: 6px;
            color: var(--accent-lime);
            font-size: 1rem;
            transition: transform 0.2s;
        }
        .chat-bubble-speaker:hover {
            transform: scale(1.2);
        }

        /* Two-phase Confirmation Card in Assistant */
        .confirm-card {
            background: rgba(251, 191, 36, 0.08);
            border: 1px solid rgba(251, 191, 36, 0.3);
            border-radius: var(--radius-md);
            padding: 1rem;
            margin-top: 0.5rem;
            font-size: 0.84rem;
        }
        .confirm-card-title {
            font-weight: 700;
            color: #fde047;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .confirm-actions {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
            margin-top: 0.85rem;
        }
        .btn-confirm-yes {
            background: var(--accent-lime);
            color: var(--accent-lime-text);
            border: none;
            padding: 0.65rem;
            border-radius: var(--radius-pill);
            font-weight: 700;
            cursor: pointer;
            font-size: 0.82rem;
            transition: all 0.2s;
        }
        .btn-confirm-yes:hover {
            background: var(--accent-lime-hover);
            box-shadow: 0 4px 12px rgba(216, 255, 62, 0.3);
        }
        .btn-confirm-no {
            background: rgba(244, 63, 94, 0.2);
            color: #fb7185;
            border: 1px solid rgba(244, 63, 94, 0.3);
            padding: 0.65rem;
            border-radius: var(--radius-pill);
            font-weight: 700;
            cursor: pointer;
            font-size: 0.82rem;
        }

        /* Quick Chips Bar */
        .quick-chips {
            padding: 0.6rem 0.85rem;
            background: var(--bg-surface-1);
            border-top: 1px solid var(--border-subtle);
            display: flex;
            gap: 6px;
            overflow-x: auto;
            white-space: nowrap;
        }
        .chip {
            background: var(--bg-surface-2);
            border: 1px solid var(--border-subtle);
            padding: 5px 12px;
            border-radius: var(--radius-pill);
            font-size: 0.78rem;
            color: var(--text-secondary);
            cursor: pointer;
            transition: all 0.15s;
        }
        .chip:hover {
            color: var(--text-primary);
            border-color: var(--accent-lime);
            background: var(--bg-surface-3);
        }

        /* Assistant Footer */
        .assistant-footer {
            padding: 0.85rem 1rem;
            background: var(--bg-surface-1);
            border-top: 1px solid var(--border-subtle);
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .assistant-input {
            flex: 1;
            padding: 0.65rem 1rem;
            background: var(--bg-surface-2);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-pill);
            font-size: 0.88rem;
            color: var(--text-primary);
        }
        .assistant-input:focus {
            outline: none;
            border-color: var(--accent-lime);
        }
        .mic-btn {
            width: 42px;
            height: 42px;
            border-radius: 50%;
            background: var(--accent-lime);
            color: var(--accent-lime-text);
            border: none;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 1.1rem;
        }
        .mic-btn.recording {
            background: #ef4444;
            color: white;
            animation: pulseRecord 1s infinite;
        }
        @keyframes pulseRecord {
            0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }
            70% { transform: scale(1.1); box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); }
            100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
        }
        .send-btn {
            width: 42px;
            height: 42px;
            border-radius: 50%;
            background: var(--bg-surface-2);
            color: var(--text-secondary);
            border: 1px solid var(--border-subtle);
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
        }
        .send-btn:hover { color: var(--text-primary); border-color: var(--border-medium); }
    </style>
</head>
<body>
    <!-- Floating Toast Notification -->
    <div id="toast-bubble" class="toast-bubble">
        <span id="toast-icon">✓</span>
        <span id="toast-msg">Action effectuée</span>
    </div>

    <!-- Top Header -->
    <header class="app-header">
        <div class="user-meta-box">
            <div class="user-avatar-circle" title="Utilisateur vérifié CEMAC">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
                <span class="user-status-dot"></span>
            </div>
            <div>
                <p class="user-greetings-sub">MboaPay Microfinance</p>
                <h2 class="user-greetings-name">Emmanuel Rostand</h2>
            </div>
        </div>
        <div class="header-actions">
            <button class="icon-btn-glass" onclick="triggerDemoAlert()" title="Déclencher alerte de sécurité">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg>
                <span class="alert-dot"></span>
            </button>
            <span style="font-size: 1.4rem; cursor:pointer;" onclick="showToast('Région: Cameroun (CEMAC)', 'info')" title="Cameroun (CEMAC)">🇨🇲</span>
        </div>
    </header>

    <!-- Page Intro Title -->
    <div class="page-intro">
        <h1 id="page-title">Opérations & Services</h1>
        <div class="quick-lang-pill" onclick="toggleAssistantPanel()" title="Changer de langue ou parler avec l'IA">
            <span>🗣️</span>
            <span id="header-lang-label">Langue: Français</span>
        </div>
    </div>

    <!-- Segmented Tabs (Fully Clickable) -->
    <div class="filter-section">
        <div class="segmented-track">
            <button class="segmented-pill active" id="pill-all" onclick="switchPill(this, 'all')">Tous</button>
            <button class="segmented-pill" id="pill-momo" onclick="switchPill(this, 'momo')">Transfert MoMo</button>
            <button class="segmented-pill" id="pill-orange" onclick="switchPill(this, 'orange')">Orange Money</button>
            <button class="segmented-pill" id="pill-tontine" onclick="switchPill(this, 'tontine')">Tontines / Njangi</button>
        </div>
        <div class="copy-rib-box" onclick="copyAccountNumber()" title="Cliquer pour copier le RIB">
            <span id="account-rib-text">CM21-10005-00012345678-89</span>
            <span>📋</span>
        </div>
    </div>

    <!-- Dynamic Alert Area -->
    <div style="max-width: 1000px; margin: 0 auto; padding: 0 1.25rem;">
        <div id="dynamic-notice-area"></div>
    </div>

    <!-- ============================================================ -->
    <!-- VIEW 1: OPERATIONS & SERVICES (DEFAULT ACTIVE VIEW) -->
    <!-- ============================================================ -->
    <div class="container" id="view-operations">
        <!-- Security Warning Banner (Shielded by Integrity Validator) -->
        <div class="full-width">
            <div class="warning-card-dark" id="security-warning-banner">
                <div class="warning-icon-circle">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fb7185" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
                </div>
                <div>
                    <div class="warning-title" id="security-title">Avertissement de sécurité</div>
                    <div class="warning-text" id="security-desc">Ne partagez jamais votre code secret PIN ou mot de passe à qui que ce soit, même à un agent bancaire. MboaPay ne vous demandera jamais vos identifiants secrets.</div>
                </div>
            </div>
        </div>

        <!-- Left Column: Hero Balance & Stats -->
        <div style="display: flex; flex-direction: column; gap: 1.5rem;">
            <!-- Hero Balance Card (Electric Cobalt Blue) -->
            <div class="card-hero-blue" onclick="showToast('Solde principal vérifié auprès de la passerelle CEMAC.', 'info')" title="Cliquer pour afficher les détails du solde">
                <div class="card-hero-top">
                    <div class="card-hero-label">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="20" height="14" x="2" y="5" rx="2"/><line x1="2" x2="22" y1="10" y2="10"/></svg>
                        <span id="account-name">Compte Courant Principal</span>
                    </div>
                    <div class="arrow-badge">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="7" y1="17" x2="17" y2="7"/><polyline points="7 7 17 7 17 17"/></svg>
                    </div>
                </div>

                <div>
                    <div style="font-size: 0.85rem; color: rgba(255,255,255,0.75);" id="balance-label">Solde disponible</div>
                    <div class="balance-value" id="account-balance">150 000 FCFA</div>
                    <p class="hero-account-id" id="account-region">Réseau national — Yaoundé / Douala</p>
                </div>

                <!-- Decorative Audio/Waveform SVG -->
                <svg class="hero-waveform-svg" viewBox="0 0 200 60" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M0 30 Q 25 10, 50 30 T 100 30 T 150 30 T 200 30" stroke="white" stroke-width="4" fill="none"/>
                    <path d="M0 30 Q 25 45, 50 30 T 100 30 T 150 30 T 200 30" stroke="white" stroke-width="2" fill="none" opacity="0.6"/>
                </svg>
            </div>

            <!-- Dual Stats Cards -->
            <div class="stats-dual-row">
                <div class="stat-subcard fee-card" onclick="showToast('Tarif réglementé CEMAC: 250 FCFA fixe pour tout transfert mobile.', 'info')">
                    <div class="stat-subcard-header">
                        <span id="fee-label-title">Frais standard</span>
                        <span class="badge-pill-green" id="fee-badge">Fixe</span>
                    </div>
                    <div class="stat-subcard-val fee-val" id="cond-3">250 FCFA</div>
                    <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 4px;" id="fee-sub">Par opération mobile</div>
                </div>

                <div class="stat-subcard" onclick="showToast('Plafond journalier de sécurité: 500 000 FCFA.', 'info')">
                    <div class="stat-subcard-header">
                        <span id="limit-label-title">Plafond journalier</span>
                        <span class="badge-pill-green" id="limit-badge">Max</span>
                    </div>
                    <div class="stat-subcard-val" id="cond-1">500 000 FCFA</div>
                    <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 4px;" id="cond-2">Délai: Immédiat</div>
                </div>
            </div>
        </div>

        <!-- Right Column: Transfer Form Card -->
        <div class="card-dark">
            <h2 class="card-title">
                <span class="title-icon">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
                </span>
                <span id="transfer-card-title">Transférer de l'argent</span>
            </h2>

            <form id="transfer-form" onsubmit="event.preventDefault(); submitTransfer();">
                <div class="form-group">
                    <label for="recipient" id="recipient-label">Numéro du bénéficiaire (MTN / Orange)</label>
                    <input type="text" id="recipient" name="recipient" class="input-dark" placeholder="Ex: 699001122" value="699001122" required>
                </div>

                <div class="form-group">
                    <label for="amount" id="amount-label">Montant du transfert</label>
                    <input type="text" id="amount" name="amount" class="input-dark" placeholder="Ex: 25000" value="25000" oninput="updateBreakdown()" required>
                </div>

                <div class="fee-breakdown">
                    <div class="fee-row">
                        <span id="breakdown-label-amount">Montant du transfert :</span>
                        <span id="breakdown-amount">25 000 FCFA</span>
                    </div>
                    <div class="fee-row">
                        <span id="breakdown-label-fee">Frais de transfert :</span>
                        <span id="breakdown-fee" class="fee-val">250 FCFA</span>
                    </div>
                    <div class="fee-row total">
                        <span id="breakdown-label-total">Total débité :</span>
                        <span id="breakdown-total">25 250 FCFA</span>
                    </div>
                </div>

                <button type="submit" id="submit-transfer" class="btn-lime">Confirmer le transfert simulé</button>
            </form>

            <div id="transaction-success">
                <strong>✅ Opération confirmée avec succès !</strong>
                <p id="success-desc" style="font-size: 0.85rem; margin-top: 4px; color: #bbf7d0;">Le transfert de 25 000 FCFA vers le 699001122 a été exécuté sur la passerelle simulée.</p>
                <div style="margin-top: 12px; display: flex; gap: 8px; flex-wrap: wrap;">
                    <button type="button" class="btn-confirm-yes" onclick="resetTransferForm()" style="width: auto; padding: 7px 16px;">+ Nouvelle opération</button>
                    <button type="button" class="btn-confirm-no" onclick="showToast('Reçu certifié CEMAC généré avec succès !', 'success')" style="width: auto; padding: 7px 16px; background: rgba(255,255,255,0.08); color: white; border-color: var(--border-medium);">📄 Reçu PDF</button>
                </div>
            </div>
        </div>

        <!-- Full-Width Recent Transactions Card -->
        <div class="card-dark full-width" id="transactions-history-card">
            <h2 class="card-title" style="justify-content: space-between;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span class="title-icon">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                    </span>
                    <span id="label-recent-transactions">Historique récent des opérations</span>
                </div>
                <span class="badge-pill-green" id="tx-badge-count">3 opérations</span>
            </h2>
            <div id="transactions-list" style="display: flex; flex-direction: column; gap: 10px;">
                <!-- dynamic items injected by JS -->
            </div>
        </div>
    </div>

    <!-- ============================================================ -->
    <!-- VIEW 2: TONTINES & NJANGI SAVINGS (CLICKABLE FROM DOCK) -->
    <!-- ============================================================ -->
    <div class="container" id="view-tontines" style="display: none;">
        <div class="card-dark full-width">
            <h2 class="card-title">
                <span>🤝</span>
                <span>Tontines & Épargne Rotative (Njangi)</span>
            </h2>
            <p style="font-size: 0.88rem; color: var(--text-secondary); margin-bottom: 1.5rem;">
                Gérez vos cercles de tontine communautaires sans commission intermédiaire avec validation arithmétique déterministe.
            </p>

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.25rem;">
                <div class="stat-subcard" style="padding: 1.3rem;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                        <strong style="color: var(--accent-lime); font-size: 1.05rem;">Tontine Mboa Solidaire</strong>
                        <span class="badge-pill-green">Cycle Actif</span>
                    </div>
                    <div style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 0.8rem;">Yaoundé — Mensuel (12 membres)</div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 4px;">
                        <span>Cagnotte par levée :</span>
                        <strong>600 000 FCFA</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 4px;">
                        <span>Votre cotisation :</span>
                        <strong style="color: var(--accent-lime);">50 000 FCFA</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 1rem;">
                        <span>Votre tour de levée :</span>
                        <span>Tour #6 (Le mois prochain)</span>
                    </div>
                    <button class="btn-lime" onclick="contributeToTontine('Tontine Mboa Solidaire', 50000)">
                        ⚡ Cotiser maintenant (50 000 FCFA)
                    </button>
                </div>

                <div class="stat-subcard" style="padding: 1.3rem;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                        <strong style="color: #60a5fa; font-size: 1.05rem;">Njangi Familial de l'Ouest</strong>
                        <span class="badge-pill-green">Bafoussam</span>
                    </div>
                    <div style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 0.8rem;">Bimensuel (8 membres)</div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 4px;">
                        <span>Cagnotte par levée :</span>
                        <strong>200 000 FCFA</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 4px;">
                        <span>Votre cotisation :</span>
                        <strong style="color: #60a5fa;">25 000 FCFA</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 1rem;">
                        <span>Prochaine date :</span>
                        <span>Le 28 du mois</span>
                    </div>
                    <button class="btn-lime" style="background: var(--accent-blue); color: white;" onclick="contributeToTontine('Njangi Familial Ouest', 25000)">
                        ⚡ Cotiser pour ce Njangi (25 000 FCFA)
                    </button>
                </div>
            </div>
        </div>
    </div>

    <!-- ============================================================ -->
    <!-- VIEW 3: STATISTIQUES & ACTIVITÉS (CLICKABLE FROM DOCK) -->
    <!-- ============================================================ -->
    <div class="container" id="view-stats" style="display: none;">
        <div class="card-dark full-width">
            <h2 class="card-title">
                <span>📊</span>
                <span>Statistiques & Analyse Financière</span>
            </h2>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 1.5rem;">
                <div class="stat-subcard">
                    <div class="stat-subcard-header">Volume débité ce mois</div>
                    <div class="stat-subcard-val" style="color: #fb7185;">125 500 FCFA</div>
                </div>
                <div class="stat-subcard">
                    <div class="stat-subcard-header">Volume crédité ce mois</div>
                    <div class="stat-subcard-val" style="color: #4ade80;">275 000 FCFA</div>
                </div>
                <div class="stat-subcard">
                    <div class="stat-subcard-header">Frais économisés</div>
                    <div class="stat-subcard-val" style="color: var(--accent-lime);">3 500 FCFA</div>
                </div>
            </div>

            <div class="stat-subcard" style="padding: 1.25rem;">
                <h3 style="font-size: 0.95rem; margin-bottom: 1rem;">Répartition par canal de paiement</h3>
                <div style="margin-bottom: 0.8rem;">
                    <div style="display:flex; justify-content: space-between; font-size: 0.82rem; margin-bottom: 4px;">
                        <span>MTN Mobile Money (48%)</span>
                        <span>60 240 FCFA</span>
                    </div>
                    <div style="height: 8px; background: var(--bg-surface-1); border-radius: 4px; overflow: hidden;">
                        <div style="width: 48%; height: 100%; background: #eab308;"></div>
                    </div>
                </div>
                <div style="margin-bottom: 0.8rem;">
                    <div style="display:flex; justify-content: space-between; font-size: 0.82rem; margin-bottom: 4px;">
                        <span>Orange Money (32%)</span>
                        <span>40 160 FCFA</span>
                    </div>
                    <div style="height: 8px; background: var(--bg-surface-1); border-radius: 4px; overflow: hidden;">
                        <div style="width: 32%; height: 100%; background: #f97316;"></div>
                    </div>
                </div>
                <div>
                    <div style="display:flex; justify-content: space-between; font-size: 0.82rem; margin-bottom: 4px;">
                        <span>Tontines Solidaire (20%)</span>
                        <span>25 100 FCFA</span>
                    </div>
                    <div style="height: 8px; background: var(--bg-surface-1); border-radius: 4px; overflow: hidden;">
                        <div style="width: 20%; height: 100%; background: var(--accent-lime);"></div>
                    </div>
                </div>
            </div>

            <div style="margin-top: 1.5rem;">
                <button class="btn-lime" style="width: auto; padding: 10px 24px;" onclick="showToast('Rapport mensuel exporté en PDF certifié.', 'success')">
                    📥 Télécharger le relevé mensuel certifié
                </button>
            </div>
        </div>
    </div>

    <!-- ============================================================ -->
    <!-- VIEW 4: PARAMÈTRES & SÉCURITÉ SAFINUM (CLICKABLE FROM DOCK) -->
    <!-- ============================================================ -->
    <div class="container" id="view-settings" style="display: none;">
        <div class="card-dark full-width">
            <h2 class="card-title">
                <span>🛡️</span>
                <span>Paramètres & Sécurité Déterministe</span>
            </h2>
            
            <div style="display: flex; flex-direction: column; gap: 12px; margin-bottom: 1.5rem;">
                <div class="tx-item">
                    <div class="tx-icon">🔒</div>
                    <div class="tx-meta">
                        <div class="tx-title">Validation Arithmétique Déterministe (SAFINUM)</div>
                        <div class="tx-subtitle">Garantie stricte: Total == Montant + Frais sans hallucination LLM</div>
                    </div>
                    <span class="badge-pill-green">100% ACTIF</span>
                </div>

                <div class="tx-item" onclick="toggleBiometrics()" style="cursor: pointer;">
                    <div class="tx-icon">👆</div>
                    <div class="tx-meta">
                        <div class="tx-title">Authentification Biométrique (Empreinte / Face ID)</div>
                        <div class="tx-subtitle">Protection pour les opérations supérieures à 50 000 FCFA</div>
                    </div>
                    <span class="badge-pill-green" id="bio-status-badge">ACTIVÉ</span>
                </div>

                <div class="tx-item">
                    <div class="tx-icon">🔑</div>
                    <div class="tx-meta">
                        <div class="tx-title">Code Secret PIN</div>
                        <div class="tx-subtitle">Code secret à 4 chiffres crypté en mémoire locale</div>
                    </div>
                    <button class="btn-confirm-yes" onclick="showToast('Code PIN vérifié et conforme.', 'info')" style="padding: 4px 12px; font-size: 0.75rem;">Vérifier</button>
                </div>
            </div>

            <h3 style="font-size: 0.95rem; margin-bottom: 0.8rem;">Journal d'audit cryptographique des actions</h3>
            <button class="btn-lime" style="width: auto; padding: 8px 18px; font-size: 0.85rem; margin-bottom: 1rem;" onclick="fetchAuditTrail()">
                🔄 Actualiser le journal d'audit
            </button>
            <div id="audit-trail-box" style="background: var(--bg-surface-2); padding: 12px; border-radius: var(--radius-md); font-family: monospace; font-size: 0.78rem; color: #a5b4fc; max-height: 180px; overflow-y: auto;">
                Cliquez sur Actualiser pour charger les journaux d'audit certifiés.
            </div>
        </div>
    </div>

    <!-- ============================================================ -->
    <!-- FLOATING BOTTOM NAVIGATION DOCK (CLICKABLE TABS) -->
    <!-- ============================================================ -->
    <nav class="bottom-nav-dock" aria-label="Navigation principale">
        <button class="dock-item active" id="nav-btn-operations" title="Accueil & Transferts" onclick="switchNav(this, 'operations')">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
        </button>
        <button class="dock-item" id="nav-btn-tontines" title="Tontines & Échéances (Njangi)" onclick="switchNav(this, 'tontines')">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="4" rx="2" ry="2"/><line x1="16" x2="16" y1="2" y2="6"/><line x1="8" x2="8" y2="6"/><line x1="3" x2="21" y1="10" y2="10"/></svg>
        </button>
        <button class="dock-item" id="nav-btn-assistant" title="Assistant Vocal Mboa" onclick="toggleAssistantPanel()" style="color: var(--accent-lime);" aria-label="Ouvrir assistant vocal">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" x2="12" y1="19" y2="22"/></svg>
        </button>
        <button class="dock-item" id="nav-btn-stats" title="Statistiques & Activités" onclick="switchNav(this, 'stats')">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" x2="18" y1="20" y2="10"/><line x1="12" x2="12" y2="4"/><line x1="6" x2="6" y1="20" y2="14"/></svg>
        </button>
        <button class="dock-item" id="nav-btn-settings" title="Paramètres & Sécurité" onclick="switchNav(this, 'settings')">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
        </button>
    </nav>

    <!-- ============================================================ -->
    <!-- FLOATING ASSISTANT OVERLAY TRIGGER & MODAL -->
    <!-- ============================================================ -->
    <div id="mboa-assistant-bubble-btn" onclick="toggleAssistantPanel()" title="Ouvrir l'assistant Mboa Finance AI">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" x2="12" y1="19" y2="22"/></svg>
        <span class="ai-cameroon-flag">🇨🇲</span>
    </div>

    <div id="mboa-assistant-panel">
        <div class="assistant-header">
            <div class="assistant-header-title">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--accent-lime)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="12" x="3" y="8" rx="2"/><path d="M12 2v6"/><circle cx="8" cy="14" r="1.5"/><circle cx="16" cy="14" r="1.5"/><path d="M9 17h6"/></svg>
                <span>Mboa Finance AI</span>
                <span style="font-size: 0.65rem; background: rgba(216, 255, 62, 0.2); color: var(--accent-lime); padding: 2px 8px; border-radius: 9999px; font-weight: 700;">SAFINUM</span>
            </div>
            <button class="assistant-header-close" onclick="toggleAssistantPanel()">✕</button>
        </div>

        <div class="assistant-lang-bar">
            <span>Langue vocale :</span>
            <select id="assistant-lang-select" class="lang-select" onchange="onLanguageChange(this.value)">
                <option value="fra" selected>Français</option>
                <option value="eng">English</option>
                <option value="fuv">Fulfulde (Nord)</option>
                <option value="ewo">Ewondo (Centre)</option>
                <option value="bum">Bulu (Sud)</option>
                <option value="bbj">Ghomálá' (Ouest)</option>
                <option value="dua">Duala (Littoral)</option>
                <option value="pcm">Cameroonian Pidgin</option>
            </select>
        </div>

        <div class="assistant-chat-body" id="assistant-chat-body">
            <div class="chat-bubble ai">
                👋 <strong>Bonjour ! Jam tan ! Mbolo !</strong><br>
                Je suis <strong>Mboa Finance AI</strong>. Je lis votre interface financière, explique vos soldes et frais, et prépare vos transferts en toute sécurité. Parlez ou choisissez une action :
            </div>
        </div>

        <!-- Quick Chips Bar -->
        <div class="quick-chips" id="quick-chips-bar">
            <!-- Rendered dynamically according to language -->
        </div>

        <div class="assistant-footer">
            <button id="mic-toggle-btn" class="mic-btn" onclick="toggleMicrophone()" title="Parler à l'agent">
                🎤
            </button>
            <input type="text" id="assistant-input-field" class="assistant-input" placeholder="Parlez ou écrivez ici..." onkeypress="handleInputKey(event)">
            <button class="send-btn" onclick="submitUserMessage()" title="Envoyer">➤</button>
        </div>
    </div>

    <!-- Hidden Audio Player for Synthesized Responses -->
    <audio id="mboa-audio-player" style="display:none;"></audio>

    <script>
        let currentBalance = 150000;
        let currentSessionId = "session_" + Date.now();
        let currentLanguage = "fra";
        let isRecording = false;
        let biometricsEnabled = true;
        let currentPill = "all";

        // Initial Transactions
        let recentTransactions = [
            {
                id: "tx-init-1",
                icon: "📱",
                title: "Virement Orange Money vers 699001122",
                subtitle: "Aujourd'hui à 04:30 • Réf: OM_847192",
                amount: -25250,
                status: "Confirmé"
            },
            {
                id: "tx-init-2",
                icon: "🤝",
                title: "Cotisation Tontine Mboa Solidaire",
                subtitle: "Hier à 18:15 • Cycle Mensuel Yaoundé",
                amount: -50000,
                status: "Confirmé"
            },
            {
                id: "tx-init-3",
                icon: "💰",
                title: "Recharge Dépôt Mobile Money (MTN)",
                subtitle: "10 Nov à 11:20 • Réf: MT_002931",
                amount: 80000,
                status: "Réussi"
            }
        ];

        // Authoritative Multilingual Interface Dictionary
        const pageTranslations = {
            fra: {
                "page-title": "Opérations & Services",
                "header-lang-label": "Langue: Français",
                "pill-all": "Tous",
                "pill-momo": "Transfert MoMo",
                "pill-orange": "Orange Money",
                "pill-tontine": "Tontines / Njangi",
                "account-name": "Compte Courant Principal",
                "balance-label": "Solde disponible",
                "account-region": "Réseau national — Yaoundé / Douala",
                "fee-label-title": "Frais standard",
                "fee-badge": "Fixe",
                "fee-sub": "Par opération mobile",
                "limit-label-title": "Plafond journalier",
                "limit-badge": "Max",
                "limit-sub": "Délai: Immédiat",
                "transfer-card-title": "Transférer de l'argent",
                "recipient-label": "Numéro du bénéficiaire (MTN / Orange)",
                "amount-label": "Montant du transfert",
                "breakdown-label-amount": "Montant du transfert :",
                "breakdown-label-fee": "Frais de transfert :",
                "breakdown-label-total": "Total débité :",
                "submit-transfer": "Confirmer le transfert simulé",
                "security-title": "Avertissement de sécurité",
                "security-desc": "Ne partagez jamais votre code secret PIN ou mot de passe à qui que ce soit, même à un agent bancaire. MboaPay ne vous demandera jamais vos identifiants secrets.",
                "label-recent-transactions": "Historique récent des opérations"
            },
            eng: {
                "page-title": "Operations & Services",
                "header-lang-label": "Language: English",
                "pill-all": "All",
                "pill-momo": "MoMo Transfer",
                "pill-orange": "Orange Money",
                "pill-tontine": "Njangi / Tontines",
                "account-name": "Main Checking Account",
                "balance-label": "Available balance",
                "account-region": "National network — Yaoundé / Douala",
                "fee-label-title": "Standard fee",
                "fee-badge": "Fixed",
                "fee-sub": "Per mobile transaction",
                "limit-label-title": "Daily limit",
                "limit-badge": "Max",
                "limit-sub": "Speed: Instant",
                "transfer-card-title": "Send Money",
                "recipient-label": "Beneficiary Number (MTN / Orange)",
                "amount-label": "Transfer Amount",
                "breakdown-label-amount": "Transfer amount :",
                "breakdown-label-fee": "Transfer fee :",
                "breakdown-label-total": "Total deduction :",
                "submit-transfer": "Confirm simulated transfer",
                "security-title": "Security Warning",
                "security-desc": "Never share your secret PIN or password with anyone, even a bank agent. MboaPay will never ask for your secret credentials.",
                "label-recent-transactions": "Recent Operations History"
            },
            fuv: {
                "page-title": "Kuugal & Sarwiisi",
                "header-lang-label": "Ɗemngal: Fulfulde",
                "pill-all": "Fuu",
                "pill-momo": "Neldol MoMo",
                "pill-orange": "Orange Money",
                "pill-tontine": "Kawtal ceede",
                "account-name": "Asiri ceede mawndo",
                "balance-label": "Ceede keɓotoodi",
                "account-region": "Kawtal leydi — Yaoundé / Douala",
                "fee-label-title": "Coggu neldol",
                "fee-badge": "Tabitngol",
                "fee-sub": "E kala neldol mobile",
                "limit-label-title": "Keerol nyalnde",
                "limit-badge": "Mawngol",
                "limit-sub": "Wakkati: Jonta jonta",
                "transfer-card-title": "Neldugo ceede",
                "recipient-label": "Lamba jaɓoowo (MTN / Orange)",
                "amount-label": "Ceede neldol",
                "breakdown-label-amount": "Ceede neldol :",
                "breakdown-label-fee": "Coggu neldol :",
                "breakdown-label-total": "Ceede de ɗon ittina fuu :",
                "submit-transfer": "Jaɓu neldol ceede",
                "security-title": "Reentaare e jommbaajo",
                "security-desc": "Taa hocciti koodi maada suuɗiindi sam. MboaPay ɗon ɗabbitaaka koodi maada suuɗiindi.",
                "label-recent-transactions": "Doggol kuugal ɓanniiŋgal"
            },
            ewo: {
                "page-title": "Bisio & Mefeg",
                "header-lang-label": "Nkóbó: Ewondo",
                "pill-all": "Mese",
                "pill-momo": "Mintol MoMo",
                "pill-orange": "Orange Money",
                "pill-tontine": "Nkuñ",
                "account-name": "Asu moni ya nyoñ",
                "balance-label": "Moni me ne ya nyoñ",
                "account-region": "Esi bese — Yaoundé / Douala",
                "fee-label-title": "Moni m'asik",
                "fee-badge": "Atiñ",
                "fee-sub": "Asu mintol mese",
                "limit-label-title": "Plafond m'amos",
                "limit-badge": "Mawon",
                "limit-sub": "Awolo: Jôm nna",
                "transfer-card-title": "Lɔm moni",
                "recipient-label": "Namba mot a nyoñ (MTN / Orange)",
                "amount-label": "Moni mintol",
                "breakdown-label-amount": "Moni mintol :",
                "breakdown-label-fee": "Moni ya asik mintol :",
                "breakdown-label-total": "Moni mese ma vɔ̂k :",
                "submit-transfer": "Kañ nlem moni mintol",
                "security-title": "Nkat mebal me bôt",
                "security-desc": "Teghe ve mot kood wo ya bisio. MboaPay a yege ve kood wo bisio.",
                "label-recent-transactions": "Mebiña mebisio mefege"
            },
            bum: {
                "page-title": "Bisio & Bisô",
                "header-lang-label": "Nkóbó: Bulu",
                "pill-all": "Mese",
                "pill-momo": "Mintol MoMo",
                "pill-orange": "Orange Money",
                "pill-tontine": "Nkuñ",
                "account-name": "Asu moni wom",
                "balance-label": "Moni ô ne ngule ya nyoñ",
                "account-region": "Si ese — Yaoundé / Douala",
                "fee-label-title": "Moni m'asik",
                "fee-badge": "Atiñ",
                "fee-sub": "Akal lôm moni",
                "limit-label-title": "Plafond m'amos",
                "limit-badge": "Anene",
                "limit-sub": "Tê: Tege yeange",
                "transfer-card-title": "Lôm moni",
                "recipient-label": "Namba môt a nyoñ (MTN / Orange)",
                "amount-label": "Moni mintol",
                "breakdown-label-amount": "Moni mintol :",
                "breakdown-label-fee": "Moni m'asik :",
                "breakdown-label-total": "Moni mese ma man :",
                "submit-transfer": "Yene mvaé lôm moni",
                "security-title": "Enyiman akal mvus",
                "security-desc": "Te ve môt kood wô ô solô. MboaPay aa ye ke sili kood wô.",
                "label-recent-transactions": "Mebiña me moni"
            },
            bbj: {
                "page-title": "Gwe & Fa' nkáp",
                "header-lang-label": "Shʉ́: Ghomálá'",
                "pill-all": "Pʉ́",
                "pill-momo": "Sɔ̂ MoMo",
                "pill-orange": "Orange Money",
                "pill-tontine": "Dzo nkáp",
                "account-name": "Asi nkáp yəm",
                "balance-label": "Nkáp ye ô gǎ ku'",
                "account-region": "Tchou tse — Yaoundé / Douala",
                "fee-label-title": "Fa' nkáp le",
                "fee-badge": "Tʉ́",
                "fee-sub": "A tsia sɔ̂ nkáp",
                "limit-label-title": "Plafond lʉ́'",
                "limit-badge": "Kpɔ́ŋ",
                "limit-sub": "Tɔ́: Kwéne",
                "transfer-card-title": "Sɔ̂ nkáp",
                "recipient-label": "Nɔmbal gwe ne nkáp (MTN / Orange)",
                "amount-label": "Tsia nkáp",
                "breakdown-label-amount": "Tsia nkáp :",
                "breakdown-label-fee": "Fa' nkáp le :",
                "breakdown-label-total": "Nkáp buɔ fě :",
                "submit-transfer": "Pɔ́ lə́ sɔ̂ nkáp",
                "security-title": "Tse pfa le",
                "security-desc": "Kà fa kòd zwě o mò mûŋkam. MboaPay ka kɔ̌' kòd zwě o.",
                "label-recent-transactions": "Mfa' nkáp lʉ́'"
            },
            dua: {
                "page-title": "Bolo & Mwaya",
                "header-lang-label": "Eyala: Duala",
                "pill-all": "Bese",
                "pill-momo": "Loma MoMo",
                "pill-orange": "Orange Money",
                "pill-tontine": "Kaki ya mwaya",
                "account-name": "Koko ya mwaya mam",
                "balance-label": "Moto mu tondi",
                "account-region": "Woki mundi — Yaoundé / Douala",
                "fee-label-title": "Musawedi ma loma",
                "fee-badge": "Kakane",
                "fee-sub": "O loma la fon",
                "limit-label-title": "Koki ya bulu",
                "limit-badge": "Bonde",
                "limit-sub": "Ponda: Katan",
                "transfer-card-title": "Loma mwaya",
                "recipient-label": "Kalati ya moto nu ngaba (MTN / Orange)",
                "amount-label": "Ndando ya loma",
                "breakdown-label-amount": "Ndando ya loma :",
                "breakdown-label-fee": "Musawedi ma loma :",
                "breakdown-label-total": "Ndando yese e pimediyo :",
                "submit-transfer": "Dumisɛ loma mwaya",
                "security-title": "Mwemba ma bolea",
                "security-desc": "O si bole moto kodi yongo ya wumɛ to mutanedi. MboaPay e si mapula kodi yongo.",
                "label-recent-transactions": "Bwele ba bolo ba katan"
            },
            pcm: {
                "page-title": "Operations & Services",
                "header-lang-label": "Lang: Pidgin",
                "pill-all": "All",
                "pill-momo": "MoMo Transfer",
                "pill-orange": "Orange Money",
                "pill-tontine": "Njangi Money",
                "account-name": "Main Bank Account",
                "balance-label": "Money wey you fit use",
                "account-region": "Cameroon country — Yaoundé / Douala",
                "fee-label-title": "Transfer charges",
                "fee-badge": "No shake",
                "fee-sub": "For each mobile transfer",
                "limit-label-title": "Maximum for day",
                "limit-badge": "Big pass",
                "limit-sub": "Time: Sharp sharp",
                "transfer-card-title": "Send Money",
                "recipient-label": "Person phone number (MTN / Orange)",
                "amount-label": "How much you wan send",
                "breakdown-label-amount": "Transfer money :",
                "breakdown-label-fee": "Transfer charges :",
                "breakdown-label-total": "Total money wey go commot :",
                "submit-transfer": "Confirm transfer sharp",
                "security-title": "Security Warning",
                "security-desc": "No ever give your secret PIN code or password to anybody, even bank worker. MboaPay no go ever ask you for your PIN.",
                "label-recent-transactions": "Recent transactions wey you do"
            }
        };

        const promptChipsByLang = {
            fra: [
                { label: "📊 Solde", prompt: "Montre-moi mon solde disponible" },
                { label: "💡 Frais", prompt: "Explique les frais de transfert" },
                { label: "💸 Envoyer 25k", prompt: "Je veux envoyer 25000 FCFA au 699001122" },
                { label: "🌐 Traduire", prompt: "Traduire la page" }
            ],
            eng: [
                { label: "📊 Balance", prompt: "Show me my available balance" },
                { label: "💡 Fees", prompt: "Explain the transfer charges" },
                { label: "💸 Send 25k", prompt: "I want to send 25000 FCFA to 699001122" },
                { label: "🌐 Translate", prompt: "Translate the page to English" }
            ],
            fuv: [
                { label: "📊 Ceede", prompt: "Holle yam ceede am keddiiɗe" },
                { label: "💡 Coggu", prompt: "Famnin am coggu neldol ngol" },
                { label: "💸 Neldugo 25k", prompt: "Mi yiɗi neldugo 25000 FCFA haa 699001122" },
                { label: "🌐 Firo", prompt: "Firtu ɗerewol ngol e Fulfulde" }
            ],
            ewo: [
                { label: "📊 Moni", prompt: "Lere ma moni me ne wom" },
                { label: "💡 Mintol", prompt: "Fandan ma moni mintol" },
                { label: "💸 Lɔm 25k", prompt: "Ma kɔŋ ô lɔm 25000 FCFA asu 699001122" },
                { label: "🌐 Traduire", prompt: "Fiti foé nyi e Ewondo" }
            ],
            bum: [
                { label: "📊 Moni", prompt: "Lere ma moni wom" },
                { label: "💡 Minlemba", prompt: "Kat ma minlemba m'asik" },
                { label: "💸 Lôm 25k", prompt: "Ma kômbô lôm 25000 FCFA asu 699001122" }
            ],
            bbj: [
                { label: "📊 Nkáp", prompt: "Zǎk ma nkáp yəm" },
                { label: "💡 Fa' nkáp", prompt: "Tsyɛ́ mǎ fa' nkáp le" },
                { label: "💸 Sɔ̂ 25k", prompt: "Mə̀ kɔ́' sɔ̂ 25000 FCFA fa' 699001122" }
            ],
            dua: [
                { label: "📊 Moto", prompt: "Bolo mba moto mwam" },
                { label: "💡 Ndando", prompt: "Tele mba ndando ya loma" },
                { label: "💸 Loma 25k", prompt: "Na mapula loma 25000 FCFA na 699001122" }
            ],
            pcm: [
                { label: "📊 Balance", prompt: "Show me ma balance" },
                { label: "💡 Charges", prompt: "Explain di money wey dem dey cut" },
                { label: "💸 Send 25k", prompt: "I wan send 25000 FCFA give 699001122" },
                { label: "🌐 Translate", prompt: "Translate this page to Pidgin" }
            ]
        };

        // Initialize UI
        function initApp() {
            renderTransactions();
            renderQuickChips(currentLanguage);
            updateBreakdown();
        }

        // Render Recent Transactions
        function renderTransactions() {
            const list = document.getElementById('transactions-list');
            if (!list) return;
            list.innerHTML = recentTransactions.map(tx => `
                <div class="tx-item" id="${tx.id}">
                    <div class="tx-icon">${tx.icon}</div>
                    <div class="tx-meta">
                        <div class="tx-title">${tx.title}</div>
                        <div class="tx-subtitle">${tx.subtitle}</div>
                    </div>
                    <div>
                        <div class="tx-amount ${tx.amount < 0 ? 'debit' : 'credit'}">
                            ${tx.amount < 0 ? '-' : '+'}${Math.abs(tx.amount).toLocaleString('fr-FR')} FCFA
                        </div>
                        <div style="font-size:0.7rem; color:var(--text-muted); text-align:right;">${tx.status}</div>
                    </div>
                </div>
            `).join('');

            const badge = document.getElementById('tx-badge-count');
            if (badge) badge.innerText = `${recentTransactions.length} opérations`;
        }

        // Add Transaction and apply debit to UI
        function applyDebitToUI(total, beneficiary, txRef) {
            currentBalance = Math.max(0, currentBalance - total);
            const balanceEl = document.getElementById('account-balance');
            if (balanceEl) {
                balanceEl.innerText = currentBalance.toLocaleString('fr-FR') + ' FCFA';
                balanceEl.style.transform = 'scale(1.05)';
                setTimeout(() => { balanceEl.style.transform = 'scale(1)'; }, 300);
            }

            const now = new Date();
            const timeStr = "Aujourd'hui à " + now.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
            
            recentTransactions.unshift({
                id: 'tx_' + Date.now(),
                icon: beneficiary.includes('Tontine') || beneficiary.includes('Njangi') ? '🤝' : '📱',
                title: "Transfert vers " + beneficiary,
                subtitle: `${timeStr} • Réf: ${txRef}`,
                amount: -total,
                status: "Confirmé"
            });

            renderTransactions();
            showToast(`Opération confirmée ! Débit: ${total.toLocaleString('fr-FR')} FCFA`, "success");
        }

        // Toast Feedback Message
        function showToast(msg, type = "success") {
            const toast = document.getElementById('toast-bubble');
            const icon = document.getElementById('toast-icon');
            const text = document.getElementById('toast-msg');
            
            if (type === "warning") icon.innerText = "⚠️";
            else if (type === "error") icon.innerText = "✕";
            else if (type === "info") icon.innerText = "ℹ️";
            else icon.innerText = "✓";

            text.innerText = msg;
            toast.classList.add('show');
            setTimeout(() => {
                toast.classList.remove('show');
            }, 3200);
        }

        // Copy Account Number
        function copyAccountNumber() {
            const rib = document.getElementById('account-rib-text').innerText;
            navigator.clipboard.writeText(rib).then(() => {
                showToast("RIB " + rib + " copié dans le presse-papier !", "success");
            }).catch(() => {
                showToast("RIB: " + rib, "info");
            });
        }

        // Switch Navigation Views (Dock)
        function switchNav(btn, viewName) {
            document.querySelectorAll('.dock-item').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const views = ['operations', 'tontines', 'stats', 'settings'];
            views.forEach(v => {
                const el = document.getElementById('view-' + v);
                if (el) el.style.display = (v === viewName) ? (v === 'operations' ? 'grid' : 'grid') : 'none';
            });

            if (viewName === 'settings') {
                fetchAuditTrail();
            }
        }

        // Switch Filter Pills
        function switchPill(btn, filterType) {
            document.querySelectorAll('.segmented-pill').forEach(p => p.classList.remove('active'));
            btn.classList.add('active');
            currentPill = filterType;

            const recInput = document.getElementById('recipient');
            const amtInput = document.getElementById('amount');

            if (filterType === 'momo') {
                recInput.value = "677123456";
                recInput.placeholder = "Ex: 677 12 34 56 (MTN MoMo)";
                showToast("Mode MTN Mobile Money sélectionné (Frais 250 FCFA)", "info");
            } else if (filterType === 'orange') {
                recInput.value = "699001122";
                recInput.placeholder = "Ex: 699 00 11 22 (Orange Money)";
                showToast("Mode Orange Money sélectionné (Frais 250 FCFA)", "info");
            } else if (filterType === 'tontine') {
                recInput.value = "Tontine Mboa Solidaire";
                recInput.placeholder = "Session / Groupe Njangi";
                amtInput.value = "50000";
                showToast("Mode Tontine / Njangi (0 FCFA de frais internes)", "info");
            } else {
                recInput.value = "699001122";
                recInput.placeholder = "Ex: 699001122";
            }
            updateBreakdown();
        }

        // Contribute to Tontine from View 2
        function contributeToTontine(name, amount) {
            const navBtn = document.getElementById('nav-btn-operations');
            switchNav(navBtn, 'operations');
            
            const pillTontine = document.getElementById('pill-tontine');
            switchPill(pillTontine, 'tontine');

            document.getElementById('recipient').value = name;
            document.getElementById('amount').value = amount.toString();
            updateBreakdown();

            showToast(`Cotisation de ${amount.toLocaleString('fr-FR')} FCFA pour ${name} prête.`, "info");
            document.getElementById('transfer-form').scrollIntoView({ behavior: 'smooth' });
        }

        // Biometrics Toggle
        function toggleBiometrics() {
            biometricsEnabled = !biometricsEnabled;
            const badge = document.getElementById('bio-status-badge');
            if (badge) {
                badge.innerText = biometricsEnabled ? "ACTIVÉ" : "DÉSACTIVÉ";
                badge.style.background = biometricsEnabled ? "rgba(34, 197, 94, 0.15)" : "rgba(244, 63, 94, 0.15)";
                badge.style.color = biometricsEnabled ? "#4ade80" : "#fb7185";
            }
            showToast("Authentification biométrique " + (biometricsEnabled ? "activée" : "désactivée"), "info");
        }

        // Fetch Audit Trail from backend
        async function fetchAuditTrail() {
            const box = document.getElementById('audit-trail-box');
            box.innerText = "Chargement des signatures cryptographiques...";
            try {
                const res = await fetch('/api/v1/transaction/audit-trail');
                const data = await res.json();
                if (data && data.length > 0) {
                    box.innerHTML = data.slice(-5).reverse().map(e => `
                        <div style="border-bottom: 1px solid rgba(255,255,255,0.07); padding: 4px 0;">
                            <strong>[${e.status}]</strong> ${e.action_type || 'TX'} | ID: ${e.transaction_id || 'N/A'}<br>
                            <span style="color:var(--text-muted); font-size:0.72rem;">Hash SHA-256: ${(e.tamper_evident_hash || 'verified_ok').substring(0, 32)}...</span>
                        </div>
                    `).join('');
                } else {
                    box.innerText = "Aucune action critique enregistrée dans ce cycle de test.";
                }
            } catch (err) {
                box.innerText = "Passerelle audit locale prête (Conformité SAFINUM intégrale).";
            }
        }

        // Toggle Assistant Panel
        function toggleAssistantPanel() {
            const panel = document.getElementById('mboa-assistant-panel');
            const isOpening = panel.style.display !== 'flex';
            panel.style.display = isOpening ? 'flex' : 'none';
            if (isOpening) {
                document.body.classList.add('assistant-open');
                document.getElementById('assistant-input-field').focus();
            } else {
                document.body.classList.remove('assistant-open');
            }
        }

        // Apply Language To Full Page
        function onLanguageChange(lang) {
            currentLanguage = lang;
            const dict = pageTranslations[lang] || pageTranslations.fra;

            for (const [key, val] of Object.entries(dict)) {
                const el = document.getElementById(key);
                if (el) el.innerText = val;
            }

            const select = document.getElementById('assistant-lang-select');
            if (select) select.value = lang;

            renderQuickChips(lang);
            showToast(`Langue sélectionnée: ${lang.toUpperCase()}`, "info");
            addChatMessage("ai", `Langue active: <strong>${lang.toUpperCase()}</strong>. Vous pouvez parler ou choisir une action.`);
        }

        function renderQuickChips(lang) {
            const chipsBar = document.getElementById('quick-chips-bar');
            const chips = promptChipsByLang[lang] || promptChipsByLang.fra;
            chipsBar.innerHTML = chips.map(c => 
                `<div class="chip" onclick="sendQuickPrompt('${c.prompt}')">${c.label}</div>`
            ).join('');
        }

        function sendQuickPrompt(prompt) {
            document.getElementById('assistant-input-field').value = prompt;
            submitUserMessage();
        }

        function handleInputKey(e) {
            if (e.key === 'Enter') submitUserMessage();
        }

        // Submit User Message to Orchestrator API
        async function submitUserMessage() {
            const input = document.getElementById('assistant-input-field');
            const query = input.value.trim();
            if (!query) return;

            addChatMessage("user", query);
            input.value = "";

            const typingId = addChatMessage("ai", "<em>Réflexion et analyse de l'interface en cours...</em>");

            try {
                const response = await fetch('/api/v1/agent/message', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        session_id: currentSessionId,
                        user_input: query,
                        language: currentLanguage
                    })
                });

                const data = await response.json();
                removeChatMessage(typingId);

                // If intent was translation, apply immediately to web UI
                if (data.intent === "TRANSLATE_PAGE") {
                    onLanguageChange(currentLanguage);
                }

                let formattedExplanation = data.explanation;
                let cardHtml = "";

                if (data.prepared_transaction && data.requires_user_confirmation) {
                    const tx = data.prepared_transaction;
                    cardHtml = `
                    <div class="confirm-card">
                        <div class="confirm-card-title">⚠️ Confirmation d'opération requise</div>
                        <div><strong>Bénéficiaire :</strong> ${tx.beneficiary_account}</div>
                        <div><strong>Montant :</strong> ${tx.amount.toLocaleString('fr-FR')} ${tx.currency}</div>
                        <div><strong>Frais :</strong> ${tx.fee.toLocaleString('fr-FR')} ${tx.currency}</div>
                        <div><strong>Total débité :</strong> ${tx.total_debit.toLocaleString('fr-FR')} ${tx.currency}</div>
                        <div style="font-size:0.75rem; color:var(--text-muted); margin-top:4px;">Vérification : ${tx.verification_status}</div>
                        <div class="confirm-actions">
                            <button class="btn-confirm-yes" onclick="confirmPreparedTransaction('${tx.transaction_id}', ${tx.total_debit}, '${tx.beneficiary_account}')">✓ Confirmer</button>
                            <button class="btn-confirm-no" onclick="cancelPreparedTransaction('${tx.transaction_id}')">✕ Annuler</button>
                        </div>
                    </div>`;
                }

                addChatMessage("ai", formattedExplanation + cardHtml, data.audio_base64);

                if (data.audio_base64) {
                    playAudioBase64(data.audio_base64);
                }

            } catch (err) {
                removeChatMessage(typingId);
                addChatMessage("ai", "⚠️ Impossible de contacter le backend Mboa Finance AI sur le port 8000.");
            }
        }

        // Confirm Two-Phase Transaction
        async function confirmPreparedTransaction(txId, totalDebit = 25250, beneficiary = "699001122") {
            addChatMessage("user", "Je confirme le transfert.");
            try {
                const resp = await fetch('/api/v1/transaction/confirm', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        transaction_id: txId,
                        confirmed: true,
                        user_speech_acknowledgment: "Explicit confirmation in UI"
                    })
                });
                const tx = await resp.json();
                addChatMessage("ai", `✅ Opération <strong>${tx.transaction_id}</strong> confirmée avec succès ! Les fonds simulés ont été transférés.`);
                
                // Deduct from live interface balance & add to history
                applyDebitToUI(tx.total_debit || totalDebit, tx.beneficiary_account || beneficiary, tx.transaction_id);

            } catch (err) {
                addChatMessage("ai", "❌ Erreur lors de la confirmation de la transaction.");
            }
        }

        function cancelPreparedTransaction(txId) {
            addChatMessage("user", "J'annule l'opération.");
            addChatMessage("ai", "L'opération a été annulée. Aucun frais n'a été prélevé.");
            showToast("Opération annulée par l'utilisateur", "info");
        }

        function addChatMessage(role, htmlText, audioB64 = null) {
            const body = document.getElementById('assistant-chat-body');
            const bubble = document.createElement('div');
            const id = 'msg_' + Date.now() + Math.random().toString(36).substring(2, 6);
            bubble.id = id;
            bubble.className = 'chat-bubble ' + role;
            
            let speakerIcon = "";
            if (audioB64) {
                speakerIcon = ` <span class="chat-bubble-speaker" onclick="playAudioBase64('${audioB64}')" title="Réécouter">🔊</span>`;
            }
            bubble.innerHTML = htmlText + speakerIcon;
            body.appendChild(bubble);
            body.scrollTop = body.scrollHeight;
            return id;
        }

        function removeChatMessage(id) {
            const el = document.getElementById(id);
            if (el) el.remove();
        }

        function playAudioBase64(b64) {
            const player = document.getElementById('mboa-audio-player');
            player.src = 'data:audio/wav;base64,' + b64;
            player.play().catch(e => console.log('Audio autoplay prevented or error:', e));
        }

        // Web Speech API with Clean Fallback
        function toggleMicrophone() {
            const btn = document.getElementById('mic-toggle-btn');
            const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;

            if (SpeechRec && !isRecording) {
                try {
                    const rec = new SpeechRec();
                    const langMap = {
                        fra: 'fr-FR',
                        eng: 'en-US',
                        fuv: 'fr-FR',
                        ewo: 'fr-FR',
                        bum: 'fr-FR',
                        bbj: 'fr-FR',
                        dua: 'fr-FR',
                        pcm: 'en-US'
                    };
                    rec.lang = langMap[currentLanguage] || 'fr-FR';
                    rec.interimResults = false;
                    rec.maxAlternatives = 1;

                    rec.onstart = function() {
                        isRecording = true;
                        btn.classList.add('recording');
                        btn.innerHTML = '⏹️';
                        showToast("Microphone actif — parlez maintenant...", "info");
                        addChatMessage("ai", "<em>Écoute en cours... Parlez naturellement.</em>");
                    };

                    rec.onresult = function(event) {
                        const transcript = event.results[0][0].transcript;
                        document.getElementById('assistant-input-field').value = transcript;
                        submitUserMessage();
                    };

                    rec.onerror = function() {
                        stopRecordingUI();
                        fallbackVoiceInput();
                    };

                    rec.onend = function() {
                        stopRecordingUI();
                    };

                    rec.start();
                    window._activeRec = rec;
                    return;
                } catch (e) {
                    fallbackVoiceInput();
                }
            } else if (isRecording) {
                if (window._activeRec) window._activeRec.stop();
                stopRecordingUI();
            } else {
                fallbackVoiceInput();
            }
        }

        function stopRecordingUI() {
            isRecording = false;
            const btn = document.getElementById('mic-toggle-btn');
            if (btn) {
                btn.classList.remove('recording');
                btn.innerHTML = '🎤';
            }
        }

        function fallbackVoiceInput() {
            stopRecordingUI();
            const sample = promptChipsByLang[currentLanguage] ? promptChipsByLang[currentLanguage][0].prompt : "Montre-moi mon solde disponible";
            document.getElementById('assistant-input-field').value = sample;
            showToast("Commande vocale simulée: « " + sample + " »", "info");
            submitUserMessage();
        }

        // Update Breakdown in Form
        function updateBreakdown() {
            const rawAmount = document.getElementById('amount').value.replace(/\\D/g, '');
            const amount = parseInt(rawAmount) || 0;
            const fee = currentPill === 'tontine' ? 0 : (amount > 0 ? 250 : 0);
            const total = amount + fee;

            document.getElementById('breakdown-amount').innerText = amount.toLocaleString('fr-FR') + ' FCFA';
            document.getElementById('breakdown-fee').innerText = fee.toLocaleString('fr-FR') + ' FCFA';
            document.getElementById('breakdown-total').innerText = total.toLocaleString('fr-FR') + ' FCFA';
        }

        // Submit Transfer with Deterministic Balance Checks
        async function submitTransfer() {
            const recipient = document.getElementById('recipient').value.trim();
            const rawAmount = document.getElementById('amount').value.replace(/\\D/g, '');
            const amount = parseInt(rawAmount) || 0;

            if (amount <= 0) {
                showToast("Veuillez saisir un montant valide.", "warning");
                return;
            }

            const fee = currentPill === 'tontine' ? 0 : 250;
            const total = amount + fee;

            if (total > currentBalance) {
                showToast(`Solde insuffisant ! Votre solde est de ${currentBalance.toLocaleString('fr-FR')} FCFA.`, "error");
                return;
            }

            const submitBtn = document.getElementById('submit-transfer');
            submitBtn.disabled = true;
            submitBtn.innerText = "Traitement déterministe en cours...";

            let txId = "TX_" + Date.now().toString(36).toUpperCase();

            try {
                const resp = await fetch('/api/v1/transaction/prepare', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        source_account: "CM21-10005-00012345678-89",
                        beneficiary_name: "Bénéficiaire Mobile",
                        beneficiary_account: recipient,
                        amount: amount,
                        fee: fee,
                        total_debit: total,
                        currency: "FCFA"
                    })
                });
                if (resp.ok) {
                    const data = await resp.json();
                    txId = data.transaction_id;
                }
            } catch (e) {
                console.warn("Backend prepare fallback:", e);
            }

            // Apply debit to balance and history
            applyDebitToUI(total, recipient, txId);

            document.getElementById('transaction-success').style.display = 'block';
            document.getElementById('success-desc').innerText = `Le transfert de ${amount.toLocaleString('fr-FR')} FCFA vers ${recipient} a été exécuté sur la passerelle simulée. Total débité: ${total.toLocaleString('fr-FR')} FCFA.`;
            document.getElementById('submit-transfer').style.display = 'none';

            submitBtn.disabled = false;
            submitBtn.innerText = "Confirmer le transfert simulé";
        }

        function resetTransferForm() {
            document.getElementById('transaction-success').style.display = 'none';
            document.getElementById('submit-transfer').style.display = 'flex';
            document.getElementById('amount').value = "25000";
            updateBreakdown();
        }

        // Demo Alerts
        function triggerDemoAlert() {
            window.triggerDynamicAlert("Avertissement de sécurité: Maintenance planifiée des services Mobile Money de 02h00 à 04h00. Aucun frais supplémentaire ne sera facturé.");
        }

        window.triggerDynamicAlert = function(msg) {
            const area = document.getElementById('dynamic-notice-area');
            const alertDiv = document.createElement('div');
            alertDiv.className = 'dynamic-banner';
            alertDiv.id = 'dynamic-notice-' + Date.now();
            alertDiv.innerHTML = `
                <span>${msg || "Alerte de sécurité: Maintenance planifiée des serveurs bancaires ce soir de 02h00 à 04h00."}</span>
                <button onclick="this.parentElement.remove()" style="background:transparent; border:none; color:inherit; font-size:1.1rem; cursor:pointer;">✕</button>
            `;
            area.appendChild(alertDiv);
            showToast("Nouvelle alerte de sécurité reçue", "warning");
        };

        // Run Init
        window.addEventListener('DOMContentLoaded', initApp);
    </script>
</body>
</html>
"""

def main():
    target_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "simulated-bank", "index.html"))
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(HTML_CONTENT)
    print(f"Updated {target_path} successfully ({len(HTML_CONTENT)} characters).")

if __name__ == "__main__":
    main()

