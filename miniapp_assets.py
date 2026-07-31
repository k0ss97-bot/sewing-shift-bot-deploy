"""Shared HTML assets for Telegram Mini App and the standalone web app."""

MINIAPP_HTML = """<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover">
  <title>Шагаем вместе</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f3f5f8;
      --text: #101722;
      --muted: #5f6978;
      --soft: rgba(255, 255, 255, .72);
      --line: rgba(16, 23, 34, .10);
      --accent: #1959f3;
      --accent-dark: #0a3ab8;
      --sage: #31a86b;
      --sage-dark: #237e52;
      --cream: #f7f8fa;
      --danger: #dd4f5d;
      --good: #31a86b;
      --warning: #f2a23a;
      --border: rgba(16, 23, 34, .16);
      --shadow: 0 24px 58px rgba(16, 23, 34, .18);
      --shadow-soft: 0 12px 28px rgba(16, 23, 34, .10);
      --blue-shadow: 0 16px 32px rgba(25, 89, 243, .24);
      --inset-shadow: inset 0 1px 0 rgba(255,255,255,.82);
      --font: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
    }

    * { box-sizing: border-box; }

    [hidden] { display: none !important; }

    html, body {
      margin: 0;
      min-height: 100%;
      font-family: var(--font);
      color: var(--text);
      background:
        linear-gradient(135deg, #ffffff 0%, #f7f8fa 46%, #e8ecf3 100%),
        repeating-linear-gradient(90deg, rgba(25,89,243,.035) 0 1px, transparent 1px 86px),
        repeating-linear-gradient(0deg, rgba(25,89,243,.025) 0 1px, transparent 1px 86px);
      overflow-x: hidden;
      -webkit-text-size-adjust: 100%;
    }

    button, input, select, textarea {
      font: inherit;
    }

    input,
    select,
    textarea {
      font-size: 16px;
    }

    button {
      cursor: pointer;
      -webkit-tap-highlight-color: transparent;
    }

    .login-view {
      min-height: 100dvh;
      padding: calc(28px + env(safe-area-inset-top)) 18px calc(28px + env(safe-area-inset-bottom));
      display: grid;
      place-items: center;
      background:
        linear-gradient(135deg, #ffffff 0%, #f7f8fa 46%, #e8ecf3 100%),
        repeating-linear-gradient(90deg, rgba(25,89,243,.035) 0 1px, transparent 1px 86px),
        repeating-linear-gradient(0deg, rgba(25,89,243,.025) 0 1px, transparent 1px 86px);
    }

    .login-shell {
      width: min(100%, 430px);
      display: grid;
      gap: 22px;
    }

    .login-brand {
      display: grid;
      justify-items: center;
      text-align: center;
    }

    .login-brand img {
      width: 78px;
      height: 78px;
      margin-bottom: 14px;
      border-radius: 20px;
      box-shadow: 0 16px 32px rgba(16,23,34,.16);
    }

    .login-brand h1 {
      margin: 0;
      font-size: 32px;
      line-height: 1;
      letter-spacing: 0;
    }

    .login-brand p {
      margin: 8px 0 0;
      color: var(--muted);
      font-size: 14px;
      font-weight: 500;
    }

    .auth-tabs {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 4px;
      padding: 4px;
      border: 1px solid var(--line);
      border-radius: 16px;
      background: rgba(255,255,255,.72);
      box-shadow: var(--inset-shadow);
    }

    .auth-tab {
      min-height: 44px;
      border: 0;
      border-radius: 12px;
      background: transparent;
      color: var(--muted);
      font-weight: 700;
    }

    .auth-tab.active {
      background: var(--accent);
      color: #fff;
      box-shadow: 0 8px 18px rgba(10,58,184,.18);
    }

    .login-card {
      display: grid;
      gap: 14px;
      padding: 22px;
      border: 1px solid var(--line);
      border-radius: 22px;
      background: rgba(255,255,255,.92);
      box-shadow: var(--shadow), var(--inset-shadow);
    }

    .login-card label {
      display: grid;
      gap: 7px;
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
    }

    .login-card input {
      width: 100%;
      min-height: 50px;
      border: 1px solid rgba(109,124,158,.16);
      border-radius: 14px;
      padding: 12px 14px;
      background: #fff;
      color: var(--text);
      outline: none;
    }

    .login-card input:focus {
      border-color: var(--accent);
      box-shadow: 0 0 0 3px rgba(25,89,243,.13);
    }

    .login-submit {
      min-height: 52px;
      border: none;
      border-radius: 14px;
      background: var(--accent);
      color: white;
      font-weight: 700;
    }

    .login-submit:disabled {
      opacity: .58;
      cursor: wait;
    }

    .login-error {
      min-height: 18px;
      margin: 0;
      color: var(--danger);
      font-size: 12px;
      line-height: 1.35;
      text-align: center;
    }

    .login-error.success {
      color: var(--good);
    }

    .login-help {
      margin: -2px 0 0;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.4;
      text-align: center;
    }

    .connection-card {
      justify-items: center;
      text-align: center;
    }

    .connection-orbit {
      position: relative;
      width: 58px;
      height: 58px;
      border: 1px solid rgba(25,89,243,.18);
      border-radius: 50%;
      background: rgba(25,89,243,.08);
      box-shadow: 0 14px 30px rgba(25,89,243,.12), var(--inset-shadow);
    }

    .connection-orbit::before {
      content: "";
      position: absolute;
      inset: 9px;
      border: 3px solid rgba(25,89,243,.16);
      border-top-color: var(--accent);
      border-radius: 50%;
      animation: connection-spin 1s linear infinite;
    }

    .connection-card h2 {
      margin: 0;
      color: var(--text);
      font-size: 22px;
      line-height: 1.15;
    }

    .connection-message,
    .connection-retry-status {
      margin: 0;
      color: var(--muted);
      line-height: 1.45;
    }

    .connection-message {
      font-size: 14px;
    }

    .connection-retry-status {
      min-height: 18px;
      font-size: 12px;
      font-weight: 500;
    }

    .connection-card .login-submit {
      width: 100%;
    }

    @keyframes connection-spin {
      to { transform: rotate(360deg); }
    }

    @media (prefers-reduced-motion: reduce) {
      .connection-orbit::before { animation: none; }
    }

    /* Desktop web workspace: this is intentionally a different layout from
       the installable, phone-first application. */
    @media (min-width: 900px) {
      body.web-mode {
        min-width: 900px;
        background:
          radial-gradient(circle at 92% 8%, rgba(25,89,243,.12), transparent 26%),
          radial-gradient(circle at 8% 92%, rgba(79,178,142,.10), transparent 28%),
          linear-gradient(135deg, #f8fafc 0%, #eef2f7 100%);
      }

      body.web-mode .app {
        width: min(1440px, calc(100% - 48px));
        min-height: calc(100vh - 48px);
        margin: 24px auto;
        padding-bottom: 0;
        border-radius: 20px;
        overflow: visible;
        box-shadow: 0 26px 70px rgba(16,23,34,.14), 0 2px 8px rgba(16,23,34,.06);
      }

      body.web-mode .appbar {
        min-height: 92px;
        padding: 18px 36px 18px 286px;
        border-bottom: 1px solid rgba(109,124,158,.15);
        background: rgba(255,255,255,.74);
        backdrop-filter: blur(22px);
      }

      body.web-mode .app-title {
        justify-items: start;
      }

      body.web-mode .app-brand-lockup {
        justify-content: flex-start;
      }

      body.web-mode .body {
        min-height: calc(100vh - 188px);
        padding: 32px 36px 48px 286px;
      }

      body.web-mode .bottom-nav {
        top: 128px;
        bottom: auto;
        left: max(36px, calc(50% - 696px));
        width: 224px;
        padding: 12px;
        transform: none;
        grid-template-columns: 1fr;
        gap: 6px;
        border: 1px solid rgba(109,124,158,.16);
        border-radius: 16px;
        box-shadow: 0 18px 44px rgba(16,23,34,.12);
      }

      body.web-mode .nav-btn {
        grid-template-columns: 40px minmax(0, 1fr);
        grid-template-rows: 1fr;
        justify-items: start;
        gap: 10px;
        padding: 10px 12px;
        font-size: 13px;
        line-height: 1.2;
      }

      body.web-mode .nav-btn span:last-child {
        text-align: left;
      }

      body.web-mode .nav-ico {
        width: 36px;
        height: 36px;
      }

      body.web-mode .screen-head {
        align-items: center;
        margin: 0 0 20px;
      }

      body.web-mode .screen-head h2 {
        font-size: 31px;
        line-height: 1.05;
      }

      body.web-mode .screen-head p {
        max-width: 680px;
        font-size: 14px;
      }

      body.web-mode .tabs {
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 6px;
        margin-bottom: 20px;
      }

      body.web-mode .tab {
        min-height: 46px;
        font-size: 13px;
      }

      body.web-mode .kpi-grid {
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 14px;
        margin: 18px 0 24px;
      }

      body.web-mode .kpi {
        min-height: 150px;
        padding: 18px;
      }

      body.web-mode .form-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 14px;
      }

      body.web-mode .field-card,
      body.web-mode .card {
        border-radius: 14px;
      }

      body.web-mode .op-list {
        gap: 12px;
      }

      body.web-mode .report-row {
        padding: 15px 18px;
      }

      body.web-mode #webActionSlot {
        position: sticky;
        bottom: 20px;
        z-index: 4;
        display: flex;
        justify-content: flex-end;
        margin-top: 24px;
      }

      body.web-mode #webActionSlot .main-button {
        width: min(360px, 100%);
        min-height: 52px;
      }
    }

    @media (max-height: 760px) {
      .login-view {
        place-items: start center;
        padding-top: calc(18px + env(safe-area-inset-top));
      }

      .login-shell {
        gap: 14px;
      }

      .login-brand img {
        width: 58px;
        height: 58px;
        margin-bottom: 9px;
      }

      .login-brand h1 {
        font-size: 27px;
      }
    }

    .app {
      min-height: 100vh;
      padding: calc(12px + env(safe-area-inset-top)) 12px calc(150px + env(safe-area-inset-bottom));
      background: transparent;
      position: relative;
      overflow: hidden;
    }

    .app::after {
      content: "";
      position: fixed;
      inset: 0;
      background-image:
        repeating-linear-gradient(90deg, rgba(25,89,243,.035) 0 1px, transparent 1px 86px),
        repeating-linear-gradient(0deg, rgba(25,89,243,.028) 0 1px, transparent 1px 86px);
      opacity: .42;
      pointer-events: none;
    }

    .appbar {
      position: relative;
      z-index: 2;
      display: grid;
      grid-template-columns: 42px 1fr 42px;
      gap: 8px;
      align-items: center;
      padding: 4px 4px 12px;
    }

    .icon-btn {
      width: 40px;
      height: 40px;
      border: none;
      border-radius: 16px;
      background: rgba(255,255,255,.58);
      box-shadow: var(--inset-shadow);
      color: var(--muted);
      display: grid;
      place-items: center;
      font-size: 22px;
    }

    .icon-btn:hover {
      background: rgba(255,255,255,.78);
      color: var(--accent-dark);
    }

    .app-title {
      text-align: center;
      font-size: 16px;
      font-weight: 700;
      line-height: 1.05;
      letter-spacing: 0;
    }

    .app-title small {
      display: block;
      margin-top: 3px;
      color: var(--muted);
      font-size: 10px;
      font-weight: 600;
    }

    .body {
      position: relative;
      z-index: 2;
    }

    .tabs {
      display: grid;
      grid-template-columns: repeat(var(--tab-count, 3), minmax(0, 1fr));
      gap: 5px;
      padding: 5px;
      margin: 3px 0 16px;
      background: rgba(255,255,255,.52);
      border: 1px solid rgba(109,124,158,.11);
      border-radius: 17px;
    }

    .order-mode-tabs { --tab-count: 2; }
    .admin-task-status-tabs { --tab-count: 4; }

    .tabs[hidden] {
      display: none;
    }

    .tab {
      min-width: 0;
      min-height: 36px;
      border: none;
      background: transparent;
      color: var(--muted);
      border-radius: 13px;
      padding: 8px 4px;
      font-size: 10.5px;
      line-height: 1.05;
      font-weight: 700;
      overflow-wrap: anywhere;
      word-break: break-word;
    }

    .tab.active {
      color: white;
      background: var(--accent);
      box-shadow: 0 9px 18px rgba(25,89,243,.20);
    }

    .tab:hover:not(.active) {
      color: var(--accent-dark);
      background: rgba(25,89,243,.10);
    }

    .screen-head {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: flex-end;
      margin: 4px 0 14px;
    }

    .screen-head h2 {
      margin: 0;
      font-size: 25px;
      letter-spacing: 0;
      line-height: 1;
    }

    .screen-head p {
      margin: 6px 0 0;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.35;
    }

    .date {
      color: var(--muted);
      font-size: 11px;
      font-weight: 700;
      padding: 8px 10px;
      border-radius: 99px;
      background: rgba(255,255,255,.54);
      white-space: nowrap;
    }

    .card {
      border: 1px solid rgba(109,124,158,.11);
      background: rgba(255,255,255,.76);
      border-radius: 22px;
      box-shadow: 0 10px 24px rgba(16,23,34,.055), var(--inset-shadow);
    }

    .shift-card {
      padding: 14px;
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 12px;
    }

    .shift-card b {
      display: block;
      font-size: 15px;
      margin-bottom: 5px;
    }

    .shift-card span {
      color: var(--muted);
      font-size: 12px;
      line-height: 1.35;
    }

    .status-chip {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      color: var(--sage-dark);
      background: rgba(49,168,107,.16);
      border: 1px solid rgba(49,168,107,.18);
      border-radius: 99px;
      padding: 7px 9px;
      font-size: 10.5px;
      font-weight: 700;
      white-space: nowrap;
    }

    .status-chip.warn {
      color: var(--accent-dark);
      background: rgba(25,89,243,.12);
      border-color: rgba(25,89,243,.18);
    }

    .status-chip.gray {
      color: var(--muted);
      background: rgba(109,124,158,.10);
      border-color: rgba(109,124,158,.10);
    }

    .kpi-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
      margin: 12px 0;
    }

    .kpi {
      padding: 13px;
      min-height: 104px;
    }

    .home-kpi {
      width: 100%;
      min-width: 0;
      text-align: left;
      color: inherit;
      border-color: rgba(25,89,243,.24);
      cursor: pointer;
      transition: transform .16s ease, border-color .16s ease, box-shadow .16s ease, background .16s ease;
    }

    .home-kpi:hover {
      transform: translateY(-1px);
      border-color: rgba(25,89,243,.52);
      background: rgba(255,255,255,.74);
      box-shadow: 0 14px 28px rgba(25,89,243,.16);
    }

    .home-kpi:active {
      transform: translateY(0);
    }

    .home-kpi > span:last-child {
      color: var(--accent-dark);
      font-weight: 600;
    }

    .summary-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
      margin: 12px 0 18px;
    }

    .summary-card {
      width: 100%;
      min-width: 0;
      min-height: 112px;
      padding: 14px;
      color: inherit;
      text-align: left;
      display: grid;
      grid-template-rows: auto 1fr auto;
      gap: 8px;
      overflow: hidden;
    }

    .summary-card > span {
      display: block;
      min-width: 0;
      color: var(--muted);
      font-size: 11px;
      line-height: 1.2;
      font-weight: 700;
      overflow-wrap: anywhere;
    }

    .summary-card > strong {
      display: block;
      align-self: end;
      min-width: 0;
      font-size: 28px;
      line-height: 1;
      letter-spacing: 0;
    }

    .summary-card > small {
      display: block;
      min-width: 0;
      color: var(--muted);
      font-size: 10.5px;
      line-height: 1.3;
      font-weight: 700;
      overflow-wrap: anywhere;
    }

    .employee-detail-head {
      align-items: center;
    }

    .employee-detail-title {
      min-width: 0;
      flex: 1;
    }

    .employee-detail-back {
      width: 40px;
      height: 40px;
      flex: 0 0 40px;
      border: 1px solid rgba(25,89,243,.22);
      border-radius: 15px;
      color: var(--accent-dark);
      background: rgba(255,255,255,.64);
      font-size: 25px;
      line-height: 1;
      box-shadow: var(--inset-shadow);
    }

    .employee-detail-back:hover {
      border-color: rgba(25,89,243,.5);
      background: rgba(255,255,255,.84);
    }

    .employee-detail-row {
      width: 100%;
      color: inherit;
      text-align: left;
    }

    .warehouse-category {
      width: 100%;
      text-align: left;
      color: inherit;
      font: inherit;
      cursor: pointer;
      border-color: rgba(25,89,243,.24);
      transition: transform .16s ease, border-color .16s ease, box-shadow .16s ease, background .16s ease;
    }

    .warehouse-category:hover {
      transform: translateY(-1px);
      border-color: rgba(25,89,243,.52);
      background: rgba(255,255,255,.72);
      box-shadow: 0 14px 28px rgba(25,89,243,.16);
    }

    .warehouse-category:active {
      transform: translateY(0);
    }

    .kpi > .kpi-top {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      margin: 0;
      color: var(--muted);
      font-size: 11px;
      font-weight: 700;
    }

    .kpi > .kpi-top > span:first-child {
      display: block;
      min-width: 0;
      margin: 0;
      color: inherit;
      font: inherit;
      line-height: 1.2;
    }

    .kpi .kpi-ico {
      width: 40px;
      height: 40px;
      flex: 0 0 40px;
      margin: 0;
      border-radius: 13px;
      border: 1px solid rgba(25,89,243,.16);
      background: linear-gradient(145deg, rgba(25,89,243,.22), rgba(25,89,243,.08));
      color: var(--accent-dark);
      display: grid;
      place-items: center;
      box-shadow: var(--inset-shadow);
    }

    .kpi .kpi-ico svg {
      display: block;
      width: 22px;
      height: 22px;
      fill: none;
      stroke: currentColor;
      stroke-width: 1.8;
      stroke-linecap: round;
      stroke-linejoin: round;
    }

    .ui-icon {
      display: block;
      width: 22px;
      height: 22px;
      fill: none;
      stroke: currentColor;
      stroke-width: 1.8;
      stroke-linecap: round;
      stroke-linejoin: round;
    }

    .kpi.good .kpi-ico {
      border-color: rgba(49,168,107,.18);
      background: linear-gradient(145deg, rgba(49,168,107,.20), rgba(49,168,107,.07));
      color: var(--sage-dark);
    }

    .kpi.danger .kpi-ico {
      border-color: rgba(221,79,93,.18);
      background: linear-gradient(145deg, rgba(221,79,93,.18), rgba(221,79,93,.06));
      color: var(--danger);
    }

    .kpi strong {
      display: block;
      margin-top: 12px;
      font-size: 26px;
      letter-spacing: 0;
    }

    .kpi strong small {
      font-size: 12px;
      letter-spacing: 0;
      color: var(--muted);
    }

    .kpi > span:not(.kpi-top) {
      display: block;
      margin-top: 4px;
      color: var(--muted);
      font-size: 11px;
      line-height: 1.3;
    }

    .warehouse-category .kpi-top {
      display: flex;
      margin-top: 0;
    }

    .warehouse-category .kpi-ico {
      display: grid;
      margin-top: 0;
      color: var(--accent-dark);
    }

    .warehouse-category.good .kpi-ico {
      color: var(--sage-dark);
    }

    .analytics-card {
      width: 100%;
      text-align: left;
      color: inherit;
      font: inherit;
      cursor: pointer;
      border-color: rgba(25,89,243,.28);
      transition: transform .16s ease, border-color .16s ease, box-shadow .16s ease, background .16s ease;
    }

    .analytics-card:hover,
    .analytics-row:hover {
      transform: translateY(-1px);
      border-color: rgba(25,89,243,.54);
      background: rgba(255,255,255,.74);
      box-shadow: 0 14px 28px rgba(25,89,243,.15);
    }

    .analytics-card:active,
    .analytics-row:active {
      transform: translateY(0);
    }

    .analytics-card > span:last-child {
      color: var(--accent-dark);
      font-weight: 600;
    }

    .analytics-row {
      cursor: pointer;
      transition: transform .16s ease, border-color .16s ease, box-shadow .16s ease, background .16s ease;
    }

    .analytics-formula {
      padding: 14px;
      margin-bottom: 12px;
    }

    .analytics-formula strong {
      display: block;
      font-size: 22px;
      margin-bottom: 5px;
    }

    .analytics-formula span {
      color: var(--muted);
      font-size: 11px;
      line-height: 1.4;
    }

    .progress {
      height: 7px;
      border-radius: 99px;
      background: rgba(109,124,158,.12);
      overflow: hidden;
      margin-top: 10px;
    }

    .progress i {
      display: block;
      height: 100%;
      width: var(--w, 70%);
      border-radius: 99px;
      background: var(--accent);
    }

    .progress.sage i {
      background: var(--sage);
    }

    .section-title {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin: 17px 0 10px;
    }

    .section-title b {
      font-size: 15px;
      letter-spacing: 0;
    }

    .section-title button, .section-title span {
      border: none;
      background: transparent;
      color: var(--accent-dark);
      font-weight: 700;
      font-size: 11px;
    }

    .wms-map-shell {
      display: grid;
      gap: 14px;
    }

    /* Warehouse UI v2: presentation only. It never writes, sorts or recreates
       physical locations; every action continues to use the existing cell id. */
    .warehouse-v2-layout {
      display: grid;
      grid-template-columns: 226px minmax(0, 1fr);
      align-items: start;
      gap: 24px;
    }

    .warehouse-v2-sidebar {
      position: sticky;
      top: 16px;
      display: grid;
      gap: 4px;
      padding: 18px 12px;
      border: 1px solid rgba(25,89,243,.14);
      border-radius: 18px;
      background: rgba(255,255,255,.82);
      box-shadow: var(--shadow-soft);
    }

    .warehouse-v2-sidebar h3 {
      margin: 0 0 10px 8px;
      color: var(--muted);
      font-size: 11px;
      letter-spacing: .11em;
      text-transform: uppercase;
    }

    .warehouse-v2-nav {
      min-height: 44px;
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 10px 11px;
      border: 1px solid transparent;
      border-radius: 12px;
      color: var(--muted);
      background: transparent;
      text-align: left;
      font: inherit;
      font-size: 13px;
      font-weight: 700;
    }

    .warehouse-v2-nav:hover { background: rgba(37,99,235,.07); color: var(--accent-dark); }
    .warehouse-v2-nav.active { color: white; background: var(--accent); box-shadow: 0 8px 18px rgba(25,89,243,.22); }
    .warehouse-v2-nav .warehouse-v2-icon { width: 18px; text-align: center; font-size: 16px; }
    .warehouse-v2-content { min-width: 0; }
    .warehouse-v2-actions { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px; }
    .warehouse-v2-actions .summary-card { min-height: 116px; }
    .warehouse-v2-alert { border-left: 4px solid var(--warning); }
    .warehouse-v2-alert.critical { border-left-color: var(--danger); }
    .warehouse-v2-filter-row { display: grid; grid-template-columns: minmax(180px, 1fr) minmax(160px, .55fr) auto; gap: 10px; align-items: end; }
    .warehouse-v2-filter-row .field { margin: 0; }
    .warehouse-v2-status { display: inline-flex; align-items: center; gap: 6px; min-width: 0; }
    .warehouse-v2-status i { width: 9px; height: 9px; display: inline-block; border-radius: 99px; background: var(--sage); }
    .warehouse-v2-status.occupied i { background: var(--accent); }
    .warehouse-v2-status.reserved i { background: var(--warning); }
    .warehouse-v2-status.blocked i { background: var(--danger); }

    @media (max-width: 1023px) {
      .warehouse-v2-layout { grid-template-columns: 1fr; }
      .warehouse-v2-sidebar { position: static; grid-template-columns: repeat(5, minmax(0, 1fr)); overflow-x: auto; padding: 8px; }
      .warehouse-v2-sidebar h3 { display: none; }
      .warehouse-v2-nav { justify-content: center; min-width: 104px; }
      .warehouse-v2-nav span:last-child { white-space: nowrap; }
    }

    @media (max-width: 767px) {
      .warehouse-v2-layout { gap: 12px; }
      .warehouse-v2-sidebar { display: none; }
      .warehouse-v2-actions { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .warehouse-v2-filter-row { grid-template-columns: 1fr; }
      .warehouse-v2-filter-row .small-button { min-height: 44px; }
    }

    .wms-stock-filter-tabs {
      --tab-count: 3;
      margin: 0 0 12px;
    }

    .wms-stock-filter-tabs .tab {
      min-height: 44px;
      font-size: 11px;
    }

    .wms-stock-filter-card {
      margin-bottom: 14px;
    }

    .wms-map-scroll {
      overflow-x: auto;
      padding: 2px 2px 10px;
      -webkit-overflow-scrolling: touch;
    }

    .wms-zone-map {
      min-width: 700px;
      display: grid;
      gap: 10px;
    }

    .wms-zone-map-head {
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      gap: 12px;
      padding: 0 4px;
    }

    .wms-zone-map-head b {
      font-size: 18px;
    }

    .wms-zone-map-head span {
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
    }

    .wms-map-grid {
      display: grid;
      gap: 4px;
      padding: 8px;
      border: 1px solid rgba(25, 89, 243, .18);
      border-radius: 18px;
      background: linear-gradient(145deg, rgba(255,255,255,.94), rgba(235,241,255,.84));
      box-shadow: var(--shadow-soft);
    }

    .wms-cell {
      min-height: 64px;
      padding: 7px 5px;
      display: grid;
      align-content: center;
      gap: 3px;
      border: 1px solid rgba(25, 89, 243, .20);
      border-radius: 10px;
      color: var(--text);
      background: rgba(255,255,255,.82);
      text-align: left;
      transition: transform .16s ease, box-shadow .16s ease, border-color .16s ease;
    }

    .wms-cell:hover,
    .wms-cell:focus-visible {
      border-color: var(--accent);
      box-shadow: 0 8px 18px rgba(25,89,243,.18);
      transform: translateY(-1px);
      outline: none;
    }

    .wms-cell strong {
      font-size: 11px;
      line-height: 1.1;
      overflow-wrap: anywhere;
      white-space: normal;
    }

    .wms-cell small {
      color: var(--muted);
      font-size: 10px;
      font-weight: 700;
    }

    .wms-cell-empty {
      border-color: rgba(49,168,107,.30);
      background: linear-gradient(145deg, rgba(238,251,245,.96), rgba(255,255,255,.90));
    }

    .wms-cell-occupied {
      border-color: rgba(25,89,243,.44);
      background: linear-gradient(145deg, rgba(225,235,255,.98), rgba(255,255,255,.92));
    }

    .wms-cell-reserved {
      border-color: rgba(242,162,58,.62);
      background: linear-gradient(145deg, rgba(255,244,220,.98), rgba(255,255,255,.92));
    }

    .wms-cell-blocked {
      border-color: rgba(221,79,93,.50);
      background: rgba(255,238,240,.94);
    }

    .wms-cell-filtered { opacity: .30; filter: grayscale(.45); }

    .wms-cell-section-start {
      margin-left: 8px;
    }

    .wms-map-legend {
      display: flex;
      flex-wrap: wrap;
      gap: 8px 14px;
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
    }

    .wms-map-legend span {
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }

    .wms-map-legend i {
      width: 12px;
      height: 12px;
      display: inline-block;
      border: 1px solid rgba(25,89,243,.24);
      border-radius: 4px;
      background: rgba(255,255,255,.9);
    }

    .wms-map-legend .occupied i { background: #dfe9ff; }
    .wms-map-legend .reserved i { background: #fff0cc; border-color: #f2a23a; }
    .wms-map-legend .blocked i { background: #ffe6e9; border-color: #dd4f5d; }

    .wms-location-detail {
      display: grid;
      gap: 14px;
    }

    .wms-location-detail .detail-grid {
      margin-top: 0;
    }

    .wms-location-products {
      display: grid;
      gap: 8px;
    }

    /* ТСД работает как клавиатура: код не показываем в поле и очищаем после считывания. */
    .wms-hardware-scanner-input { color: transparent; caret-color: transparent; }
    .wms-hardware-scanner-input::placeholder { color: var(--muted); opacity: 1; }

    @media (max-width: 600px) {
      /* На телефоне карта не должна разъезжаться в горизонтальный скролл.
         Две колонки дают ячейке достаточно места для полного имени. */
      .wms-map-scroll {
        overflow-x: visible;
        padding-right: 0;
      }

      .wms-zone-map {
        min-width: 0;
        width: 100%;
      }

      .wms-map-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
        gap: 8px;
        padding: 8px;
      }

      .wms-cell {
        min-width: 0;
        min-height: 72px;
        padding: 8px 9px;
      }

      .wms-cell strong {
        overflow: visible;
        font-size: 12px;
        line-height: 1.18;
        text-overflow: clip;
        white-space: normal;
        overflow-wrap: anywhere;
      }

      .wms-cell small {
        font-size: 11px;
      }

      .wms-cell-section-start {
        margin-left: 0;
      }
    }

    .op-icon {
      width: 44px;
      height: 44px;
      border-radius: 16px;
      background: rgba(25,89,243,.13);
      display: grid;
      place-items: center;
      color: var(--accent-dark);
      flex: 0 0 auto;
    }

    .active-operation,
    .op-row,
    .order-head {
      display: grid;
      grid-template-columns: 44px minmax(0, 1fr) auto;
      gap: 10px;
      align-items: center;
      padding: 11px;
    }

    .active-operation b,
    .op-meta b,
    .order-head b {
      display: block;
      font-size: 13px;
      line-height: 1.18;
    }

    .active-operation span,
    .op-meta span,
    .order-head span,
    .item-meta {
      display: block;
      margin-top: 4px;
      color: var(--muted);
      font-size: 11px;
      line-height: 1.35;
    }

    .op-list {
      display: grid;
      gap: 10px;
    }

    .op-row.selected {
      border-color: rgba(25,89,243,.44);
      box-shadow: 0 12px 28px rgba(25,89,243,.12), var(--inset-shadow);
    }

    .op-num {
      text-align: right;
      font-size: 12px;
      color: var(--muted);
      font-weight: 700;
    }

    .op-num strong {
      display: block;
      color: var(--text);
      font-size: 15px;
      letter-spacing: 0;
    }

    .field-card {
      padding: 13px;
      margin-bottom: 10px;
    }

    .field-card label {
      display: block;
      color: var(--muted);
      font-size: 11px;
      font-weight: 700;
      margin-bottom: 9px;
    }

    .form-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 9px;
    }

    .field {
      min-width: 0;
    }

    .field.full {
      grid-column: 1 / -1;
    }

    .field input,
    .field select,
    .field textarea {
      width: 100%;
      min-height: 42px;
      border: 1px solid rgba(109,124,158,.13);
      border-radius: 15px;
      background: rgba(255,255,255,.56);
      color: var(--text);
      padding: 9px 10px;
      outline: none;
      font-size: 16px;
      font-weight: 500;
    }

    .field textarea {
      min-height: 108px;
      resize: vertical;
      line-height: 1.35;
    }

    .segment-row {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 6px;
      margin-bottom: 12px;
    }

    .segment-button {
      min-width: 0;
      min-height: 34px;
      border: none;
      border-radius: 13px;
      padding: 8px 5px;
      background: rgba(255,255,255,.56);
      color: var(--muted);
      font-size: 12px;
      line-height: 1.05;
      font-weight: 600;
      overflow-wrap: anywhere;
    }

    .segment-button.active {
      background: var(--accent);
      color: white;
    }

    .segment-button:hover:not(.active) {
      color: var(--accent-dark);
      background: rgba(25,89,243,.10);
    }

    .button-row {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 9px;
      margin-top: 11px;
    }

    .button-row > .status-chip:only-child {
      grid-column: 1 / -1;
      min-height: 34px;
      justify-content: center;
    }

    .small-button {
      display: flex;
      align-items: center;
      justify-content: center;
      min-width: 0;
      border: none;
      border-radius: 15px;
      padding: 11px 10px;
      color: white;
      background: var(--accent);
      font-size: 12px;
      font-weight: 700;
      overflow-wrap: anywhere;
      text-decoration: none;
    }

    .small-button.secondary {
      color: var(--accent-dark);
      background: rgba(25,89,243,.12);
    }

    .small-button.danger {
      background: var(--danger);
    }

    .small-button:hover {
      filter: brightness(1.03);
      box-shadow: 0 10px 18px rgba(25,89,243,.15);
    }

    button,
    [data-go],
    [data-admin-home-period],
    [data-order-category],
    [data-report-section],
    [data-admin-home-view],
    [data-admin-home-employee],
    [data-employee-home-detail],
    [data-employee-home-back],
    [data-admin-section],
    [data-admin-action],
    [data-order-action],
    [data-order-size],
    [data-order-color],
    [data-history-action],
    [data-feedback-action],
    [data-profile-action],
    [data-select-operation],
    [data-select-order],
    [data-select-report-task],
    [data-select-cutting-report-task] {
      cursor: pointer;
      user-select: none;
      -webkit-user-select: none;
      -webkit-tap-highlight-color: transparent;
    }

    .card[data-go],
    .card[data-order-action],
    .card[data-admin-home-view],
    .card[data-admin-home-employee],
    .card[data-select-operation],
    .card[data-select-order],
    .card[data-select-report-task],
    .card[data-select-cutting-report-task] {
      border-color: rgba(25,89,243,.24);
      box-shadow: 0 9px 22px rgba(16,23,34,.07);
      transition: transform .16s ease, border-color .16s ease, box-shadow .16s ease, background .16s ease;
    }

    .marketplace-clickable {
      width: 100%;
      padding: 0;
      color: inherit;
      font: inherit;
      text-align: left;
      cursor: pointer;
      border-color: rgba(25,89,243,.24);
      transition: transform .16s ease, border-color .16s ease, box-shadow .16s ease, background .16s ease;
    }

    .marketplace-clickable.kpi {
      padding: 13px;
    }

    .marketplace-clickable.field-card {
      padding: 13px;
    }

    .marketplace-clickable:hover,
    .marketplace-clickable:focus-visible {
      transform: translateY(-1px);
      border-color: rgba(25,89,243,.52);
      background: rgba(255,255,255,.82);
      box-shadow: 0 14px 28px rgba(25,89,243,.16);
      outline: none;
    }

    .marketplace-clickable:active {
      transform: translateY(0);
      box-shadow: 0 7px 16px rgba(25,89,243,.12);
    }

    .marketplace-provider-panel {
      display: grid;
      gap: 12px;
      margin-bottom: 20px;
      padding: 12px;
      border: 1px solid rgba(111,128,159,.14);
      border-radius: 16px;
      background: rgba(255,255,255,.74);
      box-shadow: var(--inset-shadow);
    }

    .marketplace-provider-switch {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 8px;
    }

    .marketplace-provider-button {
      min-width: 0;
      padding: 12px 14px;
      border: 1px solid rgba(111,128,159,.14);
      border-radius: 12px;
      color: var(--muted);
      background: rgba(255,255,255,.66);
      font: inherit;
      text-align: left;
      cursor: pointer;
      transition: border-color .16s ease, color .16s ease, background .16s ease, box-shadow .16s ease;
    }

    .marketplace-provider-button b,
    .marketplace-provider-button span {
      display: block;
    }

    .marketplace-provider-button b {
      color: var(--text);
      font-size: 14px;
    }

    .marketplace-provider-button span {
      margin-top: 4px;
      overflow-wrap: anywhere;
      font-size: 11px;
    }

    .marketplace-provider-button.active {
      border-color: rgba(25,89,243,.48);
      color: var(--accent-dark);
      background: rgba(220,230,255,.75);
      box-shadow: 0 8px 18px rgba(25,89,243,.12);
    }

    .marketplace-provider-inline {
      width: min(480px, 100%);
      display: grid;
      gap: 6px;
      flex: 0 1 480px;
    }

    .marketplace-provider-inline .marketplace-provider-switch {
      grid-template-columns: repeat(3, minmax(0, 1fr));
    }

    .marketplace-provider-inline .marketplace-provider-button {
      padding: 9px 10px;
      text-align: center;
    }

    .marketplace-provider-inline .marketplace-provider-button b {
      font-size: 12px;
    }

    .marketplace-provider-inline .marketplace-provider-button span {
      margin-top: 2px;
      font-size: 9px;
      white-space: nowrap;
    }

    .marketplace-provider-inline .marketplace-provider-button.active b,
    .marketplace-provider-inline .marketplace-provider-button.active span {
      color: #fff;
    }

    .marketplace-provider-inline .marketplace-provider-all.active {
      border-color: #14233b;
      background: #14233b;
      box-shadow: 0 8px 18px rgba(20,35,59,.18);
    }

    .marketplace-provider-inline .marketplace-provider-ozon.active {
      border-color: #005bff;
      background: linear-gradient(135deg, #005bff, #0046c7);
      box-shadow: 0 8px 18px rgba(0,91,255,.24);
    }

    .marketplace-provider-inline .marketplace-provider-wb.active {
      border-color: #cb11ab;
      background: linear-gradient(135deg, #cb11ab, #8d0b99);
      box-shadow: 0 8px 18px rgba(203,17,171,.24);
    }

    .marketplace-provider-inline .marketplace-provider-status {
      justify-content: flex-end;
      gap: 8px;
      padding: 0 2px;
      font-size: 10px;
    }

    .marketplace-provider-inline .marketplace-provider-status b {
      color: var(--text);
    }

    .marketplace-provider-status {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      padding: 4px 2px 0;
      color: var(--muted);
      font-size: 12px;
    }

    .marketplace-provider-status b {
      color: var(--text);
    }

    @media (max-width: 520px) {
      .marketplace-provider-switch {
        grid-template-columns: 1fr;
      }
    }

    .marketplace-group-card {
      padding: 16px;
      display: grid;
      gap: 12px;
    }

    .marketplace-group-card .group-title,
    .marketplace-product-card .product-title {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 12px;
    }

    .marketplace-group-card .group-title b,
    .marketplace-product-card .product-title b {
      font-size: 15px;
      line-height: 1.2;
    }

    .marketplace-group-meta,
    .marketplace-product-meta {
      display: flex;
      flex-wrap: wrap;
      gap: 7px;
      color: var(--muted);
      font-size: 11px;
      line-height: 1.35;
    }

    .marketplace-detail-head {
      display: flex;
      align-items: flex-start;
      gap: 10px;
      margin: 8px 0 12px;
    }

    .marketplace-detail-head .small-button {
      flex: 0 0 auto;
      min-width: 94px;
      padding: 9px 12px;
    }

    .marketplace-detail-head > div {
      min-width: 0;
      flex: 1;
    }

    .marketplace-detail-head h3 {
      margin: 0;
      font-size: 18px;
      line-height: 1.15;
    }

    .marketplace-detail-head p {
      margin: 5px 0 0;
      color: var(--muted);
      font-size: 12px;
    }

    .marketplace-detail-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 8px;
      margin: 12px 0;
    }

    .marketplace-detail-field {
      min-width: 0;
      padding: 11px 12px;
      border: 1px solid rgba(109,124,158,.12);
      border-radius: 14px;
      background: rgba(255,255,255,.58);
    }

    .marketplace-detail-field span {
      display: block;
      margin-bottom: 4px;
      color: var(--muted);
      font-size: 10px;
    }

    .marketplace-detail-field b {
      display: block;
      overflow-wrap: anywhere;
      font-size: 13px;
    }

    @media (min-width: 900px) {
      body.web-mode .marketplace-group-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 12px;
      }
    }

    .card[data-go]:hover,
    .card[data-order-action]:hover,
    .card[data-admin-home-view]:hover,
    .card[data-admin-home-employee]:hover,
    .card[data-select-operation]:hover,
    .card[data-select-order]:hover,
    .card[data-select-report-task]:hover,
    .card[data-select-cutting-report-task]:hover {
      transform: translateY(-1px);
      border-color: rgba(25,89,243,.52);
      background: rgba(255,255,255,.72);
      box-shadow: 0 14px 28px rgba(25,89,243,.16);
    }

    .card[data-go]:active,
    .card[data-order-action]:active,
    .card[data-admin-home-view]:active,
    .card[data-admin-home-employee]:active,
    .card[data-select-operation]:active,
    .card[data-select-order]:active,
    .card[data-select-report-task]:active,
    .card[data-select-cutting-report-task]:active {
      transform: translateY(0);
      box-shadow: 0 7px 16px rgba(25,89,243,.12);
    }

    .card[data-go] .status-chip.gray,
    .card[data-order-action] .status-chip.gray,
    .card[data-admin-home-view] .status-chip.gray,
    .card[data-admin-home-employee] .status-chip.gray,
    .card[data-select-operation] .status-chip.gray,
    .card[data-select-order] .status-chip.gray,
    .card[data-select-report-task] .status-chip.gray,
    .card[data-select-cutting-report-task] .status-chip.gray {
      color: var(--accent-dark);
      background: rgba(25,89,243,.13);
      border-color: rgba(25,89,243,.18);
    }

    .choice-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 8px;
    }

    .choice-chip {
      min-width: 0;
      min-height: 38px;
      border: 1px solid rgba(109,124,158,.13);
      border-radius: 14px;
      background: rgba(255,255,255,.54);
      color: var(--muted);
      padding: 9px 10px;
      font-size: 11px;
      font-weight: 700;
      line-height: 1.12;
      overflow-wrap: anywhere;
      transition: .16s ease;
    }

    .choice-chip.active,
    .choice-chip:hover {
      color: var(--accent-dark);
      border-color: rgba(25,89,243,.44);
      background: rgba(25,89,243,.12);
      box-shadow: 0 8px 18px rgba(25,89,243,.10);
    }

    .stock-picker {
      display: grid;
      gap: 9px;
      margin-top: 10px;
    }

    .stock-picker-head {
      display: flex;
      justify-content: space-between;
      gap: 10px;
      align-items: center;
      color: var(--muted);
      font-size: 12px;
      font-weight: 600;
      line-height: 1.25;
    }

    .stock-picker-actions {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
    }

    .stock-component-group {
      display: grid;
      gap: 7px;
      padding-top: 8px;
      border-top: 1px solid rgba(109,124,158,.10);
    }

    .stock-component-title {
      display: flex;
      justify-content: space-between;
      gap: 10px;
      align-items: center;
      color: var(--text);
      font-size: 12px;
      font-weight: 700;
    }

    .stock-component-title span {
      color: var(--accent-dark);
      font-size: 10px;
    }

    .stock-component-title b,
    .route-input-row span:first-child {
      min-width: 0;
      overflow-wrap: anywhere;
    }

    .stock-pick-row {
      display: grid;
      grid-template-columns: 24px minmax(0, 1fr) 92px;
      gap: 10px;
      align-items: center;
      padding: 11px;
      border: 1px solid rgba(109,124,158,.10);
      border-radius: 18px;
      background: rgba(255,255,255,.58);
      transition: .16s ease;
    }

    .stock-pick-row.active,
    .stock-pick-row:hover {
      border-color: rgba(25,89,243,.42);
      background: rgba(25,89,243,.10);
      box-shadow: 0 8px 18px rgba(25,89,243,.10);
    }

    .stock-pick-row input[type="checkbox"] {
      width: 20px;
      height: 20px;
      accent-color: var(--accent);
    }

    .stock-pick-main b {
      display: block;
      font-size: 13px;
      line-height: 1.2;
      overflow-wrap: anywhere;
    }

    .stock-pick-main span {
      display: block;
      margin-top: 4px;
      color: var(--muted);
      font-size: 11px;
      font-weight: 600;
      line-height: 1.32;
    }

    .stock-pick-qty input {
      width: 100%;
      min-height: 42px;
      border: 1px solid rgba(109,124,158,.12);
      border-radius: 14px;
      background: rgba(255,255,255,.78);
      padding: 0 10px;
      color: var(--text);
      font-size: 16px;
      font-weight: 700;
      outline: none;
    }

    .route-inputs {
      display: grid;
      gap: 6px;
      margin-top: 10px;
      padding-top: 9px;
      border-top: 1px solid rgba(109,124,158,.10);
    }

    .route-inputs > b {
      font-size: 11px;
      color: var(--muted);
    }

    .route-input-row {
      display: flex;
      justify-content: space-between;
      gap: 10px;
      font-size: 11px;
      font-weight: 600;
      line-height: 1.3;
    }

    .route-input-row span:last-child {
      flex: 0 0 auto;
      color: var(--accent-dark);
      font-weight: 700;
    }

    .report-row input,
    .report-row select,
    .report-row textarea {
      width: 100%;
      min-height: 42px;
      border: 1px solid rgba(109,124,158,.12);
      border-radius: 14px;
      background: rgba(255,255,255,.78);
      padding: 0 10px;
      color: var(--text);
      font-size: 16px;
      font-weight: 700;
      outline: none;
    }

    .cutting-input-row {
      display: grid;
      grid-template-columns: minmax(0, 1fr);
      gap: 11px;
      align-items: stretch;
      padding: 13px;
    }

    .cutting-input-row b {
      display: block;
      font-size: 15px;
      line-height: 1.22;
      overflow-wrap: anywhere;
    }

    .cutting-input-row span {
      display: block;
      margin-top: 4px;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.3;
    }

    .cutting-input-row input {
      width: 100%;
      min-height: 44px;
      border: 1px solid rgba(109,124,158,.12);
      border-radius: 14px;
      background: rgba(255,255,255,.78);
      padding: 0 12px;
      color: var(--text);
      font-size: 16px;
      font-weight: 700;
      outline: none;
    }

    .cutting-input-row input:focus {
      border-color: rgba(25,89,243,.48);
      box-shadow: 0 0 0 3px rgba(25,89,243,.12);
    }

    .arbitrary-operation-card {
      display: grid;
      gap: 12px;
      padding: 14px;
      border: 1px solid rgba(25,89,243,.16);
      border-radius: 18px;
      background: rgba(244,248,255,.78);
    }

    .arbitrary-operation-head {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 12px;
    }

    .arbitrary-operation-head b {
      display: block;
      font-size: 15px;
      line-height: 1.25;
    }

    .arbitrary-operation-head span,
    .arbitrary-operation-help {
      color: var(--muted);
      font-size: 12px;
      line-height: 1.35;
    }

    .arbitrary-operation-grid {
      display: grid;
      grid-template-columns: minmax(0, 1.2fr) minmax(0, 1fr) minmax(0, .8fr) minmax(0, .8fr) auto;
      gap: 8px;
      align-items: end;
    }

    .arbitrary-operation-grid label {
      display: grid;
      gap: 5px;
      color: var(--muted);
      font-size: 11px;
      font-weight: 700;
    }

    .arbitrary-operation-grid select,
    .arbitrary-operation-grid input {
      width: 100%;
      min-height: 42px;
      border: 1px solid rgba(109,124,158,.16);
      border-radius: 12px;
      background: rgba(255,255,255,.9);
      padding: 0 9px;
      color: var(--text);
      font-size: 14px;
      font-weight: 700;
      outline: none;
    }

    .arbitrary-operation-grid select:focus,
    .arbitrary-operation-grid input:focus {
      border-color: rgba(25,89,243,.48);
      box-shadow: 0 0 0 3px rgba(25,89,243,.12);
    }

    .arbitrary-operation-remove {
      min-height: 42px;
      padding: 0 11px;
      white-space: nowrap;
    }

    @media (max-width: 680px) {
      .arbitrary-operation-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }

      .arbitrary-operation-grid .arbitrary-operation-remove {
        width: 100%;
      }
    }

    .stock-pick-qty input:focus {
      border-color: rgba(25,89,243,.48);
      box-shadow: 0 0 0 3px rgba(25,89,243,.12);
    }

    .report-row {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 10px;
      align-items: center;
      padding: 12px 13px;
    }

    .report-row b {
      display: block;
      font-size: 13px;
      line-height: 1.22;
    }

    .report-row span {
      display: block;
      margin-top: 4px;
      color: var(--muted);
      font-size: 11px;
      line-height: 1.35;
    }

    .report-row-actions {
      display: flex;
      align-items: center;
      justify-content: flex-end;
      flex-wrap: wrap;
      gap: 7px;
      min-width: 130px;
    }

    .report-row-actions .small-button {
      margin-top: 0;
      padding: 8px 10px;
      border-radius: 11px;
      font-size: 11px;
    }

    .report-row-actions .status-chip,
    .report-row-actions .muted {
      margin-top: 0;
    }

    .select-row {
      display: grid;
      grid-template-columns: 42px minmax(0, 1fr) auto;
      gap: 10px;
      align-items: center;
    }

    .select-row b {
      display: block;
      font-size: 13px;
    }

    .select-row span {
      display: block;
      margin-top: 4px;
      color: var(--muted);
      font-size: 11px;
    }

    .detail-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 8px;
      margin-top: 11px;
    }

    .detail-box {
      border-radius: 15px;
      background: rgba(255,255,255,.48);
      padding: 10px;
    }

    .detail-box span {
      display: block;
      color: var(--muted);
      font-size: 10px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0;
    }

    .detail-box strong {
      display: block;
      margin-top: 5px;
      font-size: 13px;
    }

    .order-card {
      padding: 9px 10px;
    }

    .order-card.selected {
      border-color: rgba(25,89,243,.44);
      box-shadow: 0 12px 28px rgba(25,89,243,.12), var(--inset-shadow);
    }

    .order-card .order-head {
      padding: 4px 2px;
    }

    .route-order-head {
      grid-template-columns: 44px minmax(0, 1fr);
      align-items: start;
    }

    .route-order-head > .status-chip {
      grid-column: 2;
      justify-self: start;
      margin-top: 0;
    }

    .route-assignee {
      display: inline-block;
      margin-top: 5px;
      color: var(--accent-dark);
      font-size: 11px;
      font-weight: 700;
    }

    .order-foot {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 10px;
      margin-top: 8px;
      color: var(--muted);
      font-size: 12px;
      font-weight: 600;
    }

    .order-foot strong {
      color: var(--text);
      font-size: 14px;
      line-height: 1.2;
    }

    .order-card-actions {
      display: flex;
      justify-content: flex-end;
      margin-top: 7px;
    }

    .order-delete-button {
      min-height: 30px;
      border: 1px solid rgba(221,79,93,.28);
      border-radius: 11px;
      padding: 6px 11px;
      color: var(--danger);
      background: rgba(221,79,93,.10);
      font-size: 11px;
      font-weight: 700;
    }

    .order-delete-button:hover {
      color: white;
      background: var(--danger);
    }

    .order-detail {
      padding: 14px;
      background: linear-gradient(135deg, rgba(25,89,243,.12), rgba(49,168,107,.10));
    }

    .task-completion-card {
      padding: 13px;
      margin-top: 10px;
    }

    .task-completion-head {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 10px;
      margin-bottom: 11px;
    }

    .task-completion-head b {
      min-width: 0;
      font-size: 14px;
      line-height: 1.25;
      overflow-wrap: anywhere;
    }

    .task-action-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 8px;
      margin-top: 10px;
    }

    .task-action-grid .small-button {
      min-height: 40px;
    }

    .task-note {
      margin-top: 9px;
      padding: 9px 10px;
      border-left: 3px solid var(--accent);
      background: rgba(25,89,243,.08);
      color: var(--muted);
      font-size: 11px;
      font-weight: 600;
      line-height: 1.35;
    }

    .trace-code {
      display: inline-flex;
      margin-top: 7px;
      color: var(--accent-dark);
      font-size: 10.5px;
      font-weight: 700;
    }

    .passport-timeline {
      display: grid;
      gap: 0;
    }

    .passport-event {
      position: relative;
      display: grid;
      grid-template-columns: 18px minmax(0, 1fr);
      gap: 9px;
      padding: 0 0 14px;
    }

    .passport-event::before {
      content: "";
      position: absolute;
      left: 7px;
      top: 14px;
      bottom: 0;
      width: 2px;
      background: rgba(25,89,243,.18);
    }

    .passport-event:last-child::before {
      display: none;
    }

    .passport-dot {
      position: relative;
      z-index: 1;
      width: 16px;
      height: 16px;
      border: 4px solid rgba(25,89,243,.18);
      border-radius: 50%;
      background: var(--accent);
    }

    .passport-event b,
    .passport-event span {
      display: block;
      overflow-wrap: anywhere;
    }

    .passport-event b {
      font-size: 12px;
      line-height: 1.25;
    }

    .passport-event span {
      margin-top: 3px;
      color: var(--muted);
      font-size: 10.5px;
      line-height: 1.35;
    }

    .party-qr {
      display: block;
      width: min(190px, 70vw);
      aspect-ratio: 1;
      margin: 10px auto;
      border: 8px solid white;
      background: white;
    }

    .scan-row {
      display: flex;
      justify-content: flex-end;
      margin: -4px 0 10px;
    }

    .scan-row .small-button {
      width: auto;
      padding-inline: 14px;
    }

    .chart-card {
      padding: 14px;
    }

    .chart-top {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 8px;
    }

    .chart-top b {
      display: block;
      font-size: 14px;
    }

    .chart-top strong {
      display: block;
      font-size: 27px;
      letter-spacing: 0;
      margin-top: 6px;
    }

    .chart-top small {
      color: var(--muted);
      font-size: 11px;
    }

    .ring {
      --p: 72;
      width: 68px;
      height: 68px;
      border-radius: 50%;
      background: conic-gradient(var(--accent) calc(var(--p)*1%), rgba(25,89,243,.13) 0);
      display: grid;
      place-items: center;
      position: relative;
      flex: 0 0 auto;
    }

    .ring::before {
      content: "";
      position: absolute;
      inset: 8px;
      border-radius: 50%;
      background: var(--cream);
      box-shadow: inset 0 1px 2px rgba(16,23,34,.08);
    }

    .ring strong {
      position: relative;
      z-index: 1;
      font-size: 15px;
      letter-spacing: 0;
    }

    .chart {
      width: 100%;
      height: 150px;
    }

    .mini-metrics {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 8px;
      margin-top: 10px;
    }

    .mini-metric {
      padding: 10px 8px;
      text-align: center;
    }

    .mini-metric .ring {
      width: 52px;
      height: 52px;
      margin: 0 auto 8px;
    }

    .mini-metric .ring::before {
      inset: 7px;
    }

    .mini-metric .ring strong {
      font-size: 12px;
    }

    .mini-metric b {
      display: block;
      font-size: 11px;
    }

    .mini-metric span {
      display: block;
      margin-top: 3px;
      color: var(--muted);
      font-size: 9.5px;
    }

    .empty {
      margin: 0;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.4;
      padding: 13px;
    }

    .toast {
      position: fixed;
      z-index: 50;
      left: 50%;
      bottom: calc(142px + env(safe-area-inset-bottom));
      transform: translate(-50%, 26px);
      opacity: 0;
      min-width: min(360px, calc(100% - 32px));
      border: 1px solid rgba(255,255,255,.42);
      border-radius: 20px;
      background: rgba(18,24,43,.88);
      color: white;
      padding: 14px 16px;
      box-shadow: 0 20px 60px rgba(0,0,0,.24);
      backdrop-filter: blur(20px);
      transition: .24s ease;
      pointer-events: none;
    }

    .toast.show {
      transform: translate(-50%, 0);
      opacity: 1;
    }

    .toast b {
      display: block;
      font-size: 13px;
      margin-bottom: 3px;
    }

    .toast span {
      color: rgba(255,255,255,.72);
      font-size: 12px;
    }

    .shift-reminder {
      position: fixed;
      z-index: 140;
      inset: 0;
      display: grid;
      place-items: center;
      padding: 22px;
      background: rgba(14, 20, 37, .58);
      backdrop-filter: blur(12px);
    }

    .shift-reminder[hidden] {
      display: none;
    }

    .shift-reminder-card {
      width: min(430px, 100%);
      display: grid;
      gap: 15px;
      padding: 24px;
      border: 1px solid rgba(25,89,243,.2);
      border-radius: 24px;
      background: #fff;
      box-shadow: 0 24px 70px rgba(11, 29, 71, .28);
      text-align: center;
    }

    .shift-reminder-icon {
      width: 58px;
      height: 58px;
      display: grid;
      place-items: center;
      margin: 0 auto;
      border-radius: 18px;
      background: rgba(25,89,243,.11);
      color: var(--accent);
      font-size: 28px;
    }

    .shift-reminder-card h2 { margin: 0; font-size: 23px; }
    .shift-reminder-card p { margin: 0; color: var(--muted); line-height: 1.55; }

    .qr-scanner {
      position: fixed;
      z-index: 100;
      inset: 0;
      display: grid;
      place-items: center;
      padding: max(18px, env(safe-area-inset-top)) 18px max(18px, env(safe-area-inset-bottom));
      background: #181513;
      color: white;
    }

    .qr-scanner-shell {
      position: relative;
      width: min(560px, 100%);
      height: min(760px, 100%);
      overflow: hidden;
      border-radius: 18px;
      background: #090807;
    }

    .qr-scanner video {
      display: block;
      width: 100%;
      height: 100%;
      min-width: 100%;
      min-height: 100%;
      object-fit: cover;
      background: #090807;
    }

    .qr-scanner-head,
    .qr-scanner-actions {
      position: absolute;
      z-index: 2;
      left: 14px;
      right: 14px;
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .qr-scanner-head {
      top: 14px;
      justify-content: space-between;
      font-size: 15px;
      font-weight: 700;
    }

    .qr-scanner-actions {
      bottom: 14px;
      justify-content: center;
    }

    .qr-scanner-status {
      position: absolute;
      z-index: 2;
      left: 18px;
      right: 18px;
      bottom: 72px;
      padding: 9px 12px;
      border-radius: 12px;
      background: rgba(0,0,0,.58);
      color: rgba(255,255,255,.92);
      font-size: 12px;
      font-weight: 700;
      text-align: center;
    }

    .qr-scanner .small-button {
      min-height: 44px;
      background: rgba(255,255,255,.92);
      color: #101722;
    }

    .qr-scanner-close {
      width: 44px;
      height: 44px;
      border: none;
      border-radius: 50%;
      background: rgba(255,255,255,.92);
      color: #101722;
      font-size: 26px;
      line-height: 1;
    }

    .qr-scanner-frame {
      position: absolute;
      z-index: 1;
      width: min(64vw, 280px);
      aspect-ratio: 1;
      left: 50%;
      top: 50%;
      transform: translate(-50%, -50%);
      border: 3px solid rgba(255,255,255,.9);
      border-radius: 16px;
      box-shadow: 0 0 0 999px rgba(0,0,0,.28);
      pointer-events: none;
    }

    .main-button {
      position: fixed;
      z-index: 6;
      left: 16px;
      right: 16px;
      bottom: calc(88px + env(safe-area-inset-bottom));
      border: none;
      border-radius: 18px;
      padding: 15px 16px;
      color: white;
      background: linear-gradient(135deg, var(--accent), #1959f3);
      font-size: 15px;
      font-weight: 700;
      box-shadow: 0 18px 36px rgba(25,89,243,.30);
    }

    .main-button:disabled {
      opacity: .48;
      box-shadow: none;
    }

    .bottom-nav {
      position: fixed;
      z-index: 5;
      left: 0;
      right: 0;
      bottom: 0;
      padding: 9px 12px calc(12px + env(safe-area-inset-bottom));
      background: rgba(255,255,255,.88);
      border-top: 1px solid rgba(109,124,158,.11);
      backdrop-filter: blur(18px);
      display: grid;
      grid-template-columns: repeat(var(--nav-count, 5), minmax(0, 1fr));
      gap: 2px;
    }

    body.keyboard-open .main-button,
    body.keyboard-open .bottom-nav {
      display: none;
    }

    body.keyboard-open .app {
      padding-bottom: calc(24px + env(safe-area-inset-bottom));
    }

    .nav-btn {
      min-width: 0;
      border: none;
      background: transparent;
      color: var(--muted);
      border-radius: 16px;
      padding: 8px 3px 6px;
      display: grid;
      gap: 4px;
      place-items: center;
      font-size: 10px;
      line-height: 1.05;
      font-weight: 600;
    }

    .nav-btn span:last-child {
      max-width: 100%;
      overflow-wrap: anywhere;
      word-break: break-word;
      text-align: center;
    }

    .nav-ico {
      width: 24px;
      height: 24px;
      border-radius: 10px;
      display: grid;
      place-items: center;
      font-size: 14px;
    }

    .nav-btn.active {
      color: var(--accent-dark);
    }

    .nav-btn.active .nav-ico {
      background: rgba(25,89,243,.12);
    }

    .nav-btn:hover {
      color: var(--accent-dark);
    }

    .nav-btn:hover .nav-ico {
      background: rgba(25,89,243,.10);
    }

    @media (min-width: 680px) {
      .app {
        width: min(430px, 100%);
        min-height: 880px;
        margin: 22px auto;
        border-radius: 38px;
        box-shadow: var(--shadow);
      }

      .main-button,
      .bottom-nav {
        left: 50%;
        width: min(430px, 100%);
        transform: translateX(-50%);
      }

      .stock-pick-row {
        grid-template-columns: 24px minmax(0, 1fr);
      }

      .stock-pick-qty {
        grid-column: 2;
      }

      .toast {
        bottom: 104px;
      }

      body.web-mode .app {
        width: min(760px, calc(100% - 32px));
      }

      body.web-mode .main-button,
      body.web-mode .bottom-nav {
        width: min(760px, calc(100% - 32px));
      }

      body.web-mode .login-shell {
        width: min(100%, 460px);
      }
    }

    body.web-mode .app {
      padding-bottom: calc(92px + env(safe-area-inset-bottom));
    }

    body.web-mode .main-button {
      position: static;
      inset: auto;
      width: 100%;
      transform: none;
      margin: 18px 0 4px;
    }

    /* Restored legacy blue-glass visual system. Structure and behavior stay current. */
    .login-brand img {
      border: 1px solid rgba(255,255,255,.78);
      border-radius: 8px;
      box-shadow: var(--blue-shadow), var(--inset-shadow);
    }

    .login-brand h1,
    .app-title,
    .screen-head h2,
    .section-title b {
      color: #101722;
    }

    .auth-tabs,
    .tabs {
      border-color: rgba(255,255,255,.82);
      border-radius: 8px;
      background: rgba(255,255,255,.72);
      box-shadow: var(--shadow-soft), var(--inset-shadow);
      backdrop-filter: blur(24px);
    }

    .auth-tab,
    .tab,
    .segment-button {
      border-radius: 8px;
    }

    .auth-tab.active,
    .tab.active,
    .segment-button.active {
      background: linear-gradient(135deg, #1959f3, var(--accent-dark));
      box-shadow: var(--blue-shadow);
    }

    .login-card,
    .card {
      border-color: rgba(255,255,255,.78);
      border-radius: 8px;
      background:
        linear-gradient(145deg, rgba(255,255,255,.88), rgba(234,239,255,.62)),
        rgba(255,255,255,.74);
      box-shadow: var(--shadow-soft), var(--inset-shadow);
      backdrop-filter: blur(24px);
    }

    .login-card input,
    .field input,
    .field select,
    .field textarea,
    .report-row input,
    .report-row select,
    .report-row textarea,
    .cutting-input-row input,
    .stock-pick-qty input {
      border-color: rgba(129,143,178,.24);
      border-radius: 8px;
      background: rgba(255,255,255,.72);
      box-shadow: var(--inset-shadow);
    }

    .login-submit,
    .small-button,
    .main-button {
      border-radius: 8px;
      background: linear-gradient(135deg, #1959f3, var(--accent-dark));
      box-shadow: var(--blue-shadow);
    }

    .small-button.secondary {
      color: #101722;
      border: 1px solid rgba(255,255,255,.76);
      background: rgba(255,255,255,.64);
      box-shadow: var(--inset-shadow);
    }

    .small-button.danger,
    .order-delete-button:hover {
      background: linear-gradient(135deg, #f16f78, var(--danger));
      box-shadow: 0 12px 24px rgba(221,79,93,.22);
    }

    .status-chip.warn {
      color: #925800;
      border-color: rgba(242,162,58,.28);
      background: rgba(242,162,58,.14);
    }

    .appbar {
      margin-bottom: 8px;
      padding: 4px 2px 12px;
    }

    .icon-btn,
    .employee-detail-back {
      border: 1px solid rgba(255,255,255,.78);
      border-radius: 8px;
      color: #101722;
      background: rgba(255,255,255,.66);
      box-shadow: var(--shadow-soft), var(--inset-shadow);
      backdrop-filter: blur(18px);
    }

    .app-title {
      font-size: 22px;
      font-weight: 700;
    }

    .app-title small {
      font-size: 11px;
    }

    .screen-head h2 {
      font-size: 24px;
    }

    .date,
    .kpi-ico,
    .op-icon,
    .detail-box,
    .choice-chip,
    .stock-pick-row,
    .order-delete-button,
    .task-note,
    .toast,
    .qr-scanner-shell,
    .qr-scanner-frame {
      border-radius: 8px;
    }

    .kpi-ico,
    .op-icon {
      color: var(--accent-dark);
      background: rgba(25,89,243,.13);
    }

    .kpi.good .kpi-ico {
      color: var(--sage-dark);
      background: rgba(49,168,107,.14);
    }

    .progress {
      background: rgba(109,124,158,.16);
    }

    .progress i {
      background: linear-gradient(90deg, #1959f3, var(--accent-dark));
    }

    .detail-box,
    .stock-pick-row,
    .choice-chip {
      border-color: rgba(255,255,255,.78);
      background: rgba(255,255,255,.62);
      box-shadow: var(--inset-shadow);
    }

    .order-detail {
      background: linear-gradient(135deg, rgba(25,89,243,.12), rgba(49,168,107,.10));
    }

    .ring {
      background: conic-gradient(var(--accent) calc(var(--p)*1%), rgba(25,89,243,.13) 0);
    }

    .ring::before {
      background: rgba(247,248,250,.96);
    }

    .main-button {
      box-shadow: 0 18px 36px rgba(25,89,243,.30);
    }

    .bottom-nav {
      border-color: rgba(109,124,158,.18);
      background: rgba(255,255,255,.82);
      box-shadow: 0 -10px 28px rgba(16,23,34,.10);
      backdrop-filter: blur(24px);
    }

    .nav-btn {
      border-radius: 8px;
    }

    .nav-btn.active {
      color: var(--accent-dark);
    }

    .nav-btn.active .nav-ico {
      color: #fff;
      border-radius: 8px;
      background: linear-gradient(135deg, #1959f3, var(--accent-dark));
      box-shadow: 0 8px 18px rgba(25,89,243,.22);
    }

    @media (min-width: 680px) {
      .app {
        border: 1px solid rgba(255,255,255,.78);
        border-radius: 8px;
        background: rgba(247,248,250,.58);
        box-shadow: var(--shadow);
        backdrop-filter: blur(24px);
      }
    }

    @media (min-width: 1024px) {
      body.web-mode .app {
        width: min(1280px, calc(100% - 40px));
        min-height: calc(100vh - 44px);
        margin: 22px auto;
        padding-bottom: 28px;
      }

      body.web-mode .body {
        min-height: calc(100vh - 150px);
        padding-right: 30px;
        padding-left: 252px;
      }

      body.web-mode .bottom-nav {
        top: 112px;
        bottom: auto;
        left: max(34px, calc(50% - 616px));
        right: auto;
        width: 210px;
        padding: 10px;
        transform: none;
        grid-template-columns: 1fr;
        gap: 5px;
        border: 1px solid rgba(109,124,158,.16);
        border-radius: 14px;
        box-shadow: 0 18px 44px rgba(16,23,34,.12);
      }

      body.web-mode .nav-btn {
        grid-template-columns: 38px minmax(0,1fr);
        grid-template-rows: 1fr;
        justify-items: start;
        gap: 8px;
        padding: 9px 10px;
        font-size: 13px;
        line-height: 1.2;
      }

      body.web-mode .nav-btn span:last-child {
        text-align: left;
      }

      body.web-mode .nav-ico {
        width: 34px;
        height: 34px;
      }

      body.web-mode .toast {
        right: 28px;
        bottom: 28px;
        left: auto;
        width: min(430px, calc(100% - 56px));
        transform: none;
      }
    }

    /* Final brand overrides: the lockup stays visible above every app screen. */
    .brand-lockup {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 12px;
      min-width: 0;
    }

    .brand-lockup .brand-mark {
      display: block;
      flex: 0 0 auto;
      margin: 0;
      border: 0;
      border-radius: 0;
      object-fit: contain;
      box-shadow: none;
    }

    .brand-wordmark {
      display: grid;
      min-width: 0;
      margin: 0;
      color: var(--text);
      font-weight: 700;
      line-height: .84;
      letter-spacing: -.035em;
      text-align: left;
    }

    .brand-wordmark-primary {
      color: var(--accent);
    }

    .brand-wordmark-secondary {
      color: var(--text);
    }

    .login-brand-lockup .brand-mark {
      width: 88px;
      height: 88px;
    }

    .login-brand-lockup .brand-wordmark {
      font-size: 35px;
    }

    .login-brand p {
      margin-top: 15px;
      color: var(--muted);
    }

    .app-title {
      display: grid;
      justify-items: center;
      min-width: 0;
    }

    .app-brand-lockup {
      gap: 7px;
      max-width: 100%;
    }

    .app-brand-lockup .brand-mark {
      width: 34px;
      height: 34px;
    }

    .app-brand-lockup .brand-wordmark {
      font-size: 15px;
      line-height: .82;
      letter-spacing: -.025em;
    }

    .app-title small {
      margin-top: 5px;
      color: var(--muted);
    }

    .login-brand h1,
    .app-title,
    .screen-head h2,
    .section-title b {
      color: var(--text);
    }

    .auth-tab.active,
    .tab.active,
    .segment-button.active,
    .login-submit,
    .small-button,
    .main-button,
    .nav-btn.active .nav-ico {
      background: linear-gradient(135deg, var(--accent), var(--accent-dark));
    }

    .kpi-ico,
    .op-icon {
      color: var(--accent-dark);
      background: rgba(25,89,243,.12);
    }

    .progress i {
      background: linear-gradient(90deg, var(--accent), var(--accent-dark));
    }

    .ring {
      background: conic-gradient(var(--accent) calc(var(--p)*1%), rgba(25,89,243,.12) 0);
    }

    .ring::before {
      background: rgba(247,248,250,.96);
    }

    @media (max-height: 760px) {
      .login-brand-lockup .brand-mark {
        width: 68px;
        height: 68px;
      }

      .login-brand-lockup .brand-wordmark {
        font-size: 29px;
      }

      .login-brand p {
        margin-top: 10px;
      }
    }
    /* Full desktop application workspace.  The mobile-first shell remains
       untouched below 900px; desktop uses the entire browser canvas. */
    @media (min-width: 900px) {
      html, body { min-height: 100%; }

      body.web-mode {
        min-width: 0;
        background:
          radial-gradient(circle at 88% 6%, rgba(23,81,226,.14), transparent 28%),
          radial-gradient(circle at 8% 96%, rgba(62,165,128,.12), transparent 30%),
          #edf2f8;
      }

      body.web-mode .app {
        width: calc(100vw - 32px) !important;
        max-width: none !important;
        min-height: calc(100vh - 32px);
        margin: 16px !important;
        border-radius: 18px;
        overflow: visible;
        box-shadow: 0 18px 56px rgba(26,40,68,.14);
      }

      body.web-mode .appbar {
        min-height: 88px;
        padding: 16px 38px 16px 286px !important;
        display: grid;
        grid-template-columns: minmax(0, 1fr) auto;
        align-items: center;
        background: rgba(255,255,255,.82);
        border-bottom: 1px solid rgba(110,126,158,.16);
        backdrop-filter: blur(20px);
      }

      body.web-mode .body {
        box-sizing: border-box;
        width: 100% !important;
        max-width: none !important;
        min-height: calc(100vh - 120px);
        padding: 34px 40px 64px 286px !important;
      }

      body.web-mode .body > * {
        width: 100%;
        max-width: none !important;
      }

      body.web-mode .bottom-nav {
        position: fixed;
        inset: 116px auto 40px 32px;
        width: 220px;
        height: auto;
        padding: 14px;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        gap: 8px;
        border: 1px solid rgba(120,137,169,.16);
        border-radius: 16px;
        background: rgba(255,255,255,.88);
        box-shadow: 0 14px 36px rgba(38,56,85,.12);
        backdrop-filter: blur(18px);
      }

      body.web-mode .nav-item,
      body.web-mode .bottom-nav button {
        width: 100%;
        min-height: 48px;
        padding: 0 14px;
        display: flex;
        justify-content: flex-start;
        gap: 12px;
        border-radius: 11px;
        text-align: left;
      }

      body.web-mode .screen-head {
        min-height: 74px;
        margin-bottom: 22px;
        display: grid;
        grid-template-columns: minmax(0, 1fr) auto;
        align-items: end;
        column-gap: 28px;
      }

      body.web-mode .screen-head h1,
      body.web-mode .screen-head h2 {
        font-size: clamp(28px, 2vw, 38px);
        letter-spacing: -.035em;
      }

      body.web-mode .tabs {
        display: grid;
        grid-template-columns: repeat(var(--tab-count, 3), minmax(160px, 1fr));
        width: min(760px, 100%);
        margin: 0 0 24px;
        padding: 5px;
        gap: 6px;
        border-radius: 14px;
      }

      body.web-mode .kpi-grid {
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 18px;
        margin-bottom: 22px;
      }

      body.web-mode .form-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 18px 22px;
      }

      body.web-mode .card,
      body.web-mode .report-row,
      body.web-mode .op-list > *,
      body.web-mode .list-item {
        max-width: none !important;
        border-radius: 14px;
      }

      body.web-mode .op-list {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 14px;
      }

      body.web-mode .main-button,
      body.web-mode #webActionSlot .main-button {
        width: auto;
        min-width: 280px;
        min-height: 52px;
      }

      body.web-mode #webActionSlot {
        position: sticky;
        bottom: 20px;
        display: flex;
        justify-content: flex-end;
        margin-top: 28px;
        z-index: 5;
      }
    }
    /* Desktop composition pass: establish hierarchy and comfortable reading
       widths instead of stretching mobile forms across the entire monitor. */
    @media (min-width: 900px) {
      body.web-mode .app {
        width: calc(100vw - 48px) !important;
        min-height: calc(100vh - 48px);
        margin: 24px !important;
        border-radius: 20px;
      }

      body.web-mode .appbar {
        min-height: 84px;
        padding: 0 42px 0 300px !important;
        display: flex !important;
        align-items: center;
        justify-content: space-between;
        gap: 18px;
      }

      body.web-mode .appbar > button {
        position: static !important;
        flex: 0 0 auto;
      }

      body.web-mode .app-title,
      body.web-mode .app-brand-lockup {
        position: static !important;
        margin: 0 !important;
        display: flex !important;
        align-items: center;
        justify-content: flex-start !important;
        text-align: left !important;
      }

      body.web-mode .app-title {
        flex: 1 1 auto;
        order: -1;
      }

      body.web-mode .body {
        min-height: 0;
        padding: 38px 54px 72px 300px !important;
      }

      body.web-mode .body > * {
        max-width: 1480px !important;
        margin-left: auto;
        margin-right: auto;
      }

      body.web-mode .bottom-nav {
        inset: 126px auto 48px 48px;
        width: 224px;
        padding: 12px;
      }

      body.web-mode .bottom-nav::before {
        content: "РАБОЧЕЕ ПРОСТРАНСТВО";
        display: block;
        padding: 10px 12px 8px;
        color: #71809a;
        font-size: 10px;
        font-weight: 600;
        letter-spacing: .11em;
      }

      body.web-mode .nav-item,
      body.web-mode .bottom-nav button {
        min-height: 46px;
        padding: 0 13px;
        font-size: 14px;
      }

      body.web-mode .screen-head {
        max-width: 1480px !important;
        min-height: auto;
        margin: 4px auto 24px;
        padding-bottom: 18px;
        border-bottom: 1px solid rgba(111,128,159,.16);
      }

      body.web-mode .screen-head h1,
      body.web-mode .screen-head h2 {
        margin: 0;
        font-size: clamp(30px, 2.1vw, 38px);
      }

      body.web-mode .card,
      body.web-mode .report-row {
        box-shadow: 0 9px 26px rgba(33,52,84,.07);
      }

      body.web-mode .body form {
        max-width: 1080px;
        margin-left: 0;
      }

      body.web-mode .body input,
      body.web-mode .body select,
      body.web-mode .body textarea {
        max-width: 760px;
      }

      body.web-mode .form-grid input,
      body.web-mode .form-grid select,
      body.web-mode .form-grid textarea {
        max-width: none;
      }

      body.web-mode .main-button,
      body.web-mode #webActionSlot .main-button {
        min-width: 240px;
      }

      body.web-mode #webActionSlot {
        max-width: 1480px !important;
        margin: 26px auto 0;
      }
    }
    /* Desktop header: compact, legible, and visually connected to the
       workspace rather than a large empty banner. */
    @media (min-width: 900px) {
      body.web-mode .appbar {
        min-height: 74px;
        padding: 0 34px 0 292px !important;
        display: grid !important;
        grid-template-columns: minmax(280px, 1fr) auto;
        align-items: center;
        gap: 22px;
        background: rgba(255,255,255,.94);
        box-shadow: 0 1px 0 rgba(111,128,159,.15);
      }

      body.web-mode .app-title {
        min-width: 0;
        display: flex !important;
        align-items: center;
        justify-content: flex-start !important;
        gap: 18px;
      }

      body.web-mode .app-brand-lockup {
        min-height: 44px;
        display: flex !important;
        align-items: center;
        justify-content: flex-start !important;
        gap: 10px;
      }

      body.web-mode .app-brand-lockup img,
      body.web-mode .app-title img {
        max-height: 34px;
        width: auto;
      }

      body.web-mode .app-title::after {
        content: "ОПЕРАЦИОННЫЙ ЦЕНТР";
        padding-left: 18px;
        border-left: 1px solid rgba(111,128,159,.2);
        color: #74829a;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: .1em;
        white-space: nowrap;
      }

      body.web-mode .appbar > button {
        width: 38px;
        height: 38px;
        min-height: 38px;
        padding: 0;
        border: 1px solid rgba(111,128,159,.15);
        border-radius: 10px;
        box-shadow: 0 5px 14px rgba(27,47,78,.08);
      }

      body.web-mode .appbar > button + button {
        margin-left: 10px;
      }

      body.web-mode .bottom-nav {
        inset: 94px auto 32px 24px;
        width: 238px;
        padding: 14px 12px;
        border-radius: 14px;
        box-shadow: 0 12px 30px rgba(34,53,85,.1);
      }

      body.web-mode .bottom-nav::before {
        padding: 8px 12px 12px;
        color: #687995;
        font-size: 10px;
        letter-spacing: .12em;
      }

      body.web-mode .nav-item,
      body.web-mode .bottom-nav button {
        min-height: 44px;
        padding: 0 12px;
        border-radius: 10px;
      }

      body.web-mode .body {
        padding-top: 32px !important;
      }
    }

    /* Desktop product shell: global directions live in the header, while the
       side navigation stays focused on the production workspace. */
    .workspace-nav,
    .mobile-workspace-nav,
    .appbar-profile,
    .appbar-actions {
      display: none;
    }

    .mobile-workspace-nav {
      position: relative;
      z-index: 2;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 4px;
      margin: 0 2px 14px;
      padding: 4px;
      border: 1px solid rgba(111,128,159,.13);
      border-radius: 14px;
      background: rgba(255,255,255,.74);
      box-shadow: var(--inset-shadow);
    }

    .mobile-workspace-nav button {
      min-width: 0;
      min-height: 44px;
      padding: 8px 6px;
      border: 0;
      border-radius: 10px;
      color: #65748d;
      background: transparent;
      font: inherit;
      font-size: 11px;
      font-weight: 700;
      line-height: 1.15;
    }

    .mobile-workspace-nav button.active {
      color: #fff;
      background: linear-gradient(135deg, #2160f3, #1647c9);
      box-shadow: 0 8px 18px rgba(25,89,243,.22);
    }

    @media (min-width: 900px) {
      body.web-mode .appbar {
        min-height: 96px;
        padding: 0 34px !important;
        display: grid !important;
        grid-template-columns: 250px minmax(420px, 1fr) 164px auto;
        gap: 22px;
        background: rgba(255,255,255,.96);
        box-shadow: 0 1px 0 rgba(111,128,159,.16);
      }

      body.web-mode .app-title {
        display: block !important;
        min-width: 0;
      }

      body.web-mode .app-title::after {
        display: none;
      }

      body.web-mode .app-brand-lockup {
        min-height: 58px;
        gap: 13px;
      }

      body.web-mode .app-brand-lockup img,
      body.web-mode .app-title img {
        width: 46px;
        height: 46px;
        max-height: none;
      }

      body.web-mode .app-brand-lockup .brand-wordmark {
        font-size: 22px;
        line-height: .78;
        letter-spacing: -.04em;
      }

      body.web-mode .workspace-nav {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        align-items: center;
        gap: 4px;
        padding: 5px;
        border: 1px solid rgba(111,128,159,.13);
        border-radius: 12px;
        background: #f5f7fb;
      }

      body.web-mode .workspace-nav button {
        min-height: 46px;
        padding: 7px 10px;
        border: 0;
        border-radius: 8px;
        color: #65748d;
        background: transparent;
        font: inherit;
        font-size: 11px;
        font-weight: 600;
        line-height: 1.15;
        text-align: center;
        white-space: normal;
      }

      body.web-mode .workspace-nav button.active {
        color: #fff;
        background: linear-gradient(135deg, #2160f3, #1647c9);
        box-shadow: 0 8px 18px rgba(25,89,243,.22);
      }

      body.web-mode .workspace-nav button:disabled {
        cursor: not-allowed;
        opacity: .46;
      }

      body.web-mode.has-wms-access .workspace-nav {
        grid-template-columns: repeat(4, minmax(0, 1fr));
      }

      body.web-mode .appbar-profile {
        display: grid;
        justify-items: end;
        gap: 3px;
        min-width: 0;
        padding-right: 4px;
        text-align: right;
      }

      body.web-mode .appbar-profile span {
        color: #7a899f;
        font-size: 10px;
        font-weight: 600;
        letter-spacing: .07em;
        text-transform: uppercase;
        white-space: nowrap;
      }

      body.web-mode .appbar-profile small {
        margin: 0 !important;
        color: #17243a;
        font-size: 14px;
        font-weight: 700;
        white-space: nowrap;
      }

      body.web-mode .appbar-actions {
        display: flex;
        align-items: center;
        gap: 8px;
      }

      body.web-mode .appbar-actions .icon-btn {
        width: 40px;
        height: 40px;
        min-height: 40px;
        padding: 0;
        border: 1px solid rgba(111,128,159,.15);
        border-radius: 10px;
        box-shadow: 0 5px 14px rgba(27,47,78,.08);
      }

      body.web-mode .bottom-nav {
        inset: 136px auto 32px 24px !important;
        width: 244px;
        padding: 16px 12px;
      }

      body.web-mode .bottom-nav::before {
        content: "УПРАВЛЕНИЕ ПРОИЗВОДСТВОМ";
        padding: 9px 12px 14px;
      }

      body.web-mode .body {
        min-height: calc(100vh - 170px);
        padding: 38px 52px 70px 312px !important;
      }
    }

    @media (min-width: 900px) and (max-width: 1260px) {
      body.web-mode .appbar {
        grid-template-columns: 205px minmax(340px, 1fr) 126px auto;
        gap: 14px;
        padding: 0 22px !important;
      }

      body.web-mode .app-brand-lockup .brand-wordmark {
        font-size: 18px;
      }

      body.web-mode .workspace-nav button {
        padding: 6px 5px;
        font-size: 9px;
      }
    }

    @media (max-width: 899px) {
      .appbar {
        grid-template-columns: minmax(0, 1fr) auto;
        gap: 10px;
      }

      .workspace-nav,
      .appbar-profile {
        display: none !important;
      }

      body.has-wms-access .mobile-workspace-nav {
        display: grid;
      }

      .appbar-actions {
        display: flex;
        gap: 8px;
      }

      .app-title {
        text-align: left;
      }
    }

    @media (min-width: 900px) {
      body.web-mode .bottom-nav .desktop-redundant {
        display: none;
      }

      body.web-mode.warehouse-workspace .bottom-nav::before {
        content: "УПРАВЛЕНИЕ СКЛАДОМ";
      }

      body.web-mode.warehouse-workspace .bottom-nav {
        border-color: rgba(25,89,243,.16);
      }

      /* UI v2 owns the desktop warehouse navigation. The old app sidebar is
         kept for the reversible flag and for the mobile bottom navigation. */
      body.web-mode.warehouse-workspace.warehouse-v2-enabled .bottom-nav {
        display: none !important;
      }

      body.web-mode.warehouse-workspace.warehouse-v2-enabled .body {
        padding-left: 52px !important;
      }

      body.web-mode.marketplace-workspace .bottom-nav::before {
        content: "УПРАВЛЕНИЕ МАРКЕТПЛЕЙСАМИ";
      }

      body.web-mode.marketplace-workspace .bottom-nav {
        border-color: rgba(25,89,243,.16);
      }
    }

    /* ── Searchable select ── */
    .searchable-select {
      position: relative;
      display: inline-block;
      width: 100%;
    }
    .searchable-select .ss-input {
      width: 100%;
      box-sizing: border-box;
      padding: 8px 28px 8px 8px;
      font: inherit;
      border: 1px solid var(--border);
      border-radius: var(--radius, 6px);
      background: var(--card);
      color: var(--text);
      cursor: pointer;
    }
    .searchable-select .ss-input:focus {
      outline: none;
      border-color: var(--accent, #4a90d9);
    }
    .searchable-select .ss-arrow {
      position: absolute;
      top: 50%;
      right: 8px;
      transform: translateY(-50%);
      pointer-events: none;
      color: var(--muted);
      font-size: 12px;
    }
    .ss-dropdown {
      position: fixed;
      max-height: 240px;
      overflow-y: auto;
      background: var(--card, #fff);
      border: 1px solid var(--border, #ccc);
      border-radius: var(--radius, 6px);
      z-index: 9999;
      display: none;
      box-shadow: 0 4px 16px rgba(0,0,0,0.3);
    }
    .ss-dropdown.open {
      display: block;
    }
    .ss-dropdown .ss-option {
      padding: 8px 10px;
      cursor: pointer;
      font: inherit;
      color: var(--text, #111);
    }
    .ss-dropdown .ss-option:hover,
    .ss-dropdown .ss-option.active {
      background: var(--accent-bg, rgba(74,144,217,0.12));
    }
    .ss-dropdown .ss-no-match {
      padding: 8px 10px;
      color: var(--muted, #888);
      font-style: italic;
    }
  </style>
  <script src="/assets/jsqr.js"></script>
</head>
<body>
  <section class="login-view" id="connectionView" hidden aria-labelledby="connectionTitle">
    <div class="login-shell">
      <div class="login-brand">
        <div class="brand-lockup login-brand-lockup">
          <img class="brand-mark" src="/brand/mark.svg" alt="" aria-hidden="true">
          <h1 class="brand-wordmark"><span class="brand-wordmark-primary">Шагаем</span><span class="brand-wordmark-secondary">вместе</span></h1>
        </div>
        <p>Управление производством</p>
      </div>
      <div class="login-card connection-card">
        <div class="connection-orbit" aria-hidden="true"></div>
        <div role="status" aria-live="polite" aria-atomic="true">
          <h2 id="connectionTitle">Подключаемся</h2>
          <p class="connection-message" id="connectionMessage">Проверяем защищённую сессию.</p>
        </div>
        <p class="connection-retry-status" id="connectionRetryStatus"></p>
        <button class="login-submit" id="webConnectionRetry" type="button">Попробовать снова</button>
      </div>
    </div>
  </section>

  <section class="login-view" id="loginView" hidden>
    <div class="login-shell">
      <div class="login-brand">
        <div class="brand-lockup login-brand-lockup">
          <img class="brand-mark" src="/brand/mark.svg" alt="" aria-hidden="true">
          <h1 class="brand-wordmark"><span class="brand-wordmark-primary">Шагаем</span><span class="brand-wordmark-secondary">вместе</span></h1>
        </div>
        <p>Управление производством</p>
      </div>
      <div class="auth-tabs" role="tablist" aria-label="Доступ к приложению">
        <button class="auth-tab active" id="webLoginTab" type="button" role="tab" aria-selected="true" aria-controls="webLoginForm">Вход</button>
        <button class="auth-tab" id="webRegisterTab" type="button" role="tab" aria-selected="false" aria-controls="webRegisterForm">Регистрация</button>
      </div>
      <form class="login-card" id="webLoginForm">
        <label>Почта, телефон или логин<input id="webUsername" name="username" autocomplete="username" autocapitalize="none" spellcheck="false" required></label>
        <label>Пароль<input id="webPassword" name="password" type="password" autocomplete="current-password" maxlength="128" required></label>
        <p class="login-error" id="webLoginError" role="alert" aria-live="polite"></p>
        <button class="login-submit" id="webLoginButton" type="submit">Войти</button>
      </form>
      <form class="login-card" id="webRegisterForm" hidden>
        <label>Фамилия, имя и отчество<input id="webFullName" name="full_name" autocomplete="name" minlength="5" maxlength="120" required></label>
        <label>Электронная почта<input id="webEmail" name="email" type="email" inputmode="email" autocomplete="email" autocapitalize="none" spellcheck="false" maxlength="254" required></label>
        <label>Номер телефона<input id="webPhone" name="phone" type="tel" inputmode="tel" autocomplete="tel" placeholder="+7 999 123-45-67" maxlength="24" required></label>
        <label>Пароль<input id="webRegisterPassword" name="password" type="password" autocomplete="new-password" minlength="10" maxlength="128" required></label>
        <label>Повторите пароль<input id="webPasswordConfirm" name="password_confirm" type="password" autocomplete="new-password" minlength="10" maxlength="128" required></label>
        <p class="login-help">После регистрации администратор назначит должность и откроет доступ.</p>
        <p class="login-error" id="webRegisterError" role="alert" aria-live="polite"></p>
        <button class="login-submit" id="webRegisterButton" type="submit">Зарегистрироваться</button>
      </form>
    </div>
  </section>

  <main class="app" id="appRoot" hidden>
    <div class="appbar">
      <div class="app-title">
        <div class="brand-lockup app-brand-lockup">
          <img class="brand-mark" src="/brand/mark.svg" alt="" aria-hidden="true">
          <span class="brand-wordmark"><span class="brand-wordmark-primary">Шагаем</span><span class="brand-wordmark-secondary">вместе</span></span>
        </div>
      </div>
      <nav class="workspace-nav" aria-label="Разделы системы">
        <button class="active" type="button" data-workspace="production" aria-current="page">Управление производством</button>
        <button type="button" data-workspace="warehouse">Управление складом</button>
        <button type="button" data-workspace="marketplaces" hidden>Управление маркетплейсами</button>
        <button type="button" disabled title="Раздел готовится">Отчёт</button>
      </nav>
      <div class="appbar-profile"><span>Должность на проекте</span><small id="roleLabel">Загрузка</small></div>
      <div class="appbar-actions">
        <button class="icon-btn" id="backBtn" aria-label="Назад">‹</button>
        <button class="icon-btn" id="menuBtn" aria-label="Меню">⋯</button>
      </div>
    </div>

    <nav class="mobile-workspace-nav" id="mobileWorkspaceNav" aria-label="Рабочая среда" hidden>
      <button class="active" type="button" data-workspace="production" aria-current="page">Производство</button>
      <button type="button" data-workspace="warehouse">Склад</button>
      <button type="button" data-workspace="marketplaces" hidden>Маркетплейсы</button>
    </nav>

    <div class="body">
      <div class="tabs" id="topTabs" hidden></div>
      <div id="mount"></div>
      <div id="webActionSlot"></div>
    </div>
  </main>

  <button class="main-button" id="mainButton" hidden>Загрузка</button>
  <nav class="bottom-nav" id="bottomNav" aria-label="Навигация приложения" hidden></nav>
  <div class="toast" id="toast"><b></b><span></span></div>
  <section class="shift-reminder" id="shiftReminder" aria-modal="true" role="dialog" hidden>
    <div class="shift-reminder-card">
      <div class="shift-reminder-icon">✓</div>
      <h2>Смена открыта</h2>
      <p id="shiftReminderText"></p>
      <button class="small-button" id="shiftReminderClose" type="button">Понятно</button>
    </div>
  </section>
  <section class="qr-scanner" id="qrScanner" aria-label="Сканер QR-кода" hidden>
    <div class="qr-scanner-shell">
      <video id="qrScannerVideo" autoplay playsinline webkit-playsinline muted></video>
      <div class="qr-scanner-frame"></div>
      <div class="qr-scanner-head"><span id="qrScannerTitle">QR-код партии</span><button class="qr-scanner-close" id="qrScannerClose" type="button" aria-label="Закрыть">×</button></div>
      <div class="qr-scanner-status" id="qrScannerStatus" role="status" aria-live="polite">Запускаем камеру…</div>
      <div class="qr-scanner-actions"><button class="small-button" id="qrScannerManual" type="button">Ввести код</button></div>
    </div>
  </section>

  <script>
    const tg = null;

    /* ── Searchable select ── */
    function makeSearchable(select) {
      if (!select || select.dataset.ssApplied) return;
      select.dataset.ssApplied = "1";
      select.style.display = "none";

      const wrapper = document.createElement("div");
      wrapper.className = "searchable-select";

      const input = document.createElement("input");
      input.type = "text";
      input.className = "ss-input";
      input.autocomplete = "off";
      input.spellcheck = false;

      const arrow = document.createElement("span");
      arrow.className = "ss-arrow";
      arrow.textContent = "▼";

      const dropdown = document.createElement("div");
      dropdown.className = "ss-dropdown";

      wrapper.appendChild(input);
      wrapper.appendChild(arrow);
      select.parentNode.insertBefore(wrapper, select);
      document.body.appendChild(dropdown);
      wrapper._sourceSelect = select;
      dropdown._sourceSelect = select;
      wrapper._dropdown = dropdown;

      let options = [];
      let selectedIndex = -1;
      let activeIndex = -1;

      function rebuildOptionList() {
        options = Array.from(select.options);
        if (select.selectedIndex >= 0) {
          selectedIndex = options.indexOf(select.options[select.selectedIndex]);
        }
        if (selectedIndex < 0 && options.length > 0) selectedIndex = 0;
        syncInput();
      }

      function syncInput() {
        var opt = options[selectedIndex];
        input.value = opt ? opt.textContent : "";
      }

      function positionDropdown() {
        var inputRect = input.getBoundingClientRect();
        var viewportHeight = window.innerHeight;
        var maxHeight = 240;
        var spaceBelow = viewportHeight - inputRect.bottom;
        var openUpward = spaceBelow < maxHeight && inputRect.top > spaceBelow;

        dropdown.style.left = inputRect.left + "px";
        dropdown.style.width = inputRect.width + "px";
        if (openUpward) {
          dropdown.style.maxHeight = Math.min(maxHeight, inputRect.top - 8) + "px";
          dropdown.style.bottom = (viewportHeight - inputRect.top + 1) + "px";
          dropdown.style.top = "auto";
        } else {
          dropdown.style.maxHeight = Math.min(maxHeight, spaceBelow - 8) + "px";
          dropdown.style.top = (inputRect.bottom + 1) + "px";
          dropdown.style.bottom = "auto";
        }
      }

      function filterOptions(query) {
        var q = query.toLowerCase();
        dropdown.innerHTML = "";
        var matches = options.filter(function(opt) {
          return opt.textContent.toLowerCase().indexOf(q) >= 0;
        });
        if (matches.length === 0) {
          dropdown.innerHTML = '<div class="ss-no-match">Ничего не найдено</div>';
        } else {
          matches.forEach(function(opt, idx) {
            var div = document.createElement("div");
            div.className = "ss-option" + (opt === options[selectedIndex] ? " active" : "");
            div.textContent = opt.textContent;
            div.addEventListener("mousedown", function(e) {
              e.preventDefault();
              selectOption(opt);
            });
            dropdown.appendChild(div);
          });
        }

        positionDropdown();
        dropdown.classList.add("open");
      }

      function selectOption(opt) {
        var idx = options.indexOf(opt);
        if (idx < 0) return;
        selectedIndex = idx;
        select.selectedIndex = Array.from(select.options).indexOf(opt);
        syncInput();
        dropdown.classList.remove("open");
        select.dispatchEvent(new Event("change", {bubbles: true}));
      }

      function closeDropdown() {
        dropdown.classList.remove("open");
      }

      /* Keep dropdown pinned to input on scroll/resize while open */
      var repositionHandler = function() {
        if (dropdown.classList.contains("open")) positionDropdown();
      };
      window.addEventListener("scroll", repositionHandler, true);
      window.addEventListener("resize", repositionHandler);

      rebuildOptionList();

      input.addEventListener("focus", function() {
        activeIndex = -1;
        input.select();
        filterOptions("");
      });

      input.addEventListener("click", function() {
        if (!dropdown.classList.contains("open")) {
          input.select();
          filterOptions("");
        }
      });

      input.addEventListener("input", function() {
        filterOptions(input.value);
      });

      input.addEventListener("keydown", function(e) {
        if (e.key === "ArrowDown") {
          e.preventDefault();
          var items = dropdown.querySelectorAll(".ss-option");
          if (items.length) {
            activeIndex = Math.min((activeIndex >= 0 ? activeIndex : -1) + 1, items.length - 1);
            items.forEach(function(item, i) {
              item.classList.toggle("active", i === activeIndex);
              if (i === activeIndex) item.scrollIntoView({block: "nearest"});
            });
          }
        } else if (e.key === "ArrowUp") {
          e.preventDefault();
          var items = dropdown.querySelectorAll(".ss-option");
          if (items.length) {
            activeIndex = Math.max((activeIndex >= 0 ? activeIndex : 1) - 1, 0);
            items.forEach(function(item, i) {
              item.classList.toggle("active", i === activeIndex);
              if (i === activeIndex) item.scrollIntoView({block: "nearest"});
            });
          }
        } else if (e.key === "Enter") {
          e.preventDefault();
          var items = dropdown.querySelectorAll(".ss-option");
          if (items.length && activeIndex >= 0 && activeIndex < items.length) {
            var optText = items[activeIndex].textContent;
            var found = options.find(function(o) { return o.textContent === optText; });
            if (found) selectOption(found);
          } else if (options[selectedIndex]) {
            selectOption(options[selectedIndex]);
          }
          closeDropdown();
        } else if (e.key === "Escape") {
          closeDropdown();
          input.blur();
        }
      });

      input.addEventListener("blur", function() {
        setTimeout(function() {
          if (document.activeElement !== input) {
            closeDropdown();
            syncInput();
          }
        }, 150);
      });

      document.addEventListener("click", function(e) {
        if (!wrapper.contains(e.target) && e.target !== input) closeDropdown();
      });
    }

    function initSearchableSelects(root) {
      root = root || document;

      /* Clean up only orphaned wrappers/dropdowns.  Working searchable
         selects must survive MutationObserver callbacks. */
      document.querySelectorAll(".searchable-select").forEach(function(w) {
        var source = w._sourceSelect;
        if (source && source.isConnected) return;
        if (w._dropdown) w._dropdown.remove();
        w.remove();
      });
      document.querySelectorAll(".ss-dropdown").forEach(function(d) {
        if (d._sourceSelect && d._sourceSelect.isConnected) return;
        d.remove();
      });

      root.querySelectorAll("select:not([data-ss-applied]):not([disabled])").forEach(function(select) {
        makeSearchable(select);
      });
    }
    const urlParams = new URLSearchParams(window.location.search);
    const debugTelegramId = urlParams.get("debug_tg_id");
    try {
      window.localStorage.removeItem("miniapp_auth");
    } catch (error) {
      // Storage may be unavailable in private browsing mode.
    }
    const isStandaloneWeb = !debugTelegramId;
    let webCsrfToken = "";
    let webSessionProfile = {};
    const webIdentityStorageKey = "webapp_identity";
    let storedWebIdentity = "";
    try {
      storedWebIdentity = window.localStorage.getItem(webIdentityStorageKey) || "";
    } catch (error) {
      storedWebIdentity = "";
    }
    const authIdentity = debugTelegramId || storedWebIdentity || "web_anonymous";
    const uiStateStorageKey = `miniapp_ui_state_${authIdentity}`;
    const completionQueueKey = `miniapp_completion_queue_${authIdentity}`;
    const persistedUiStateKeys = [
      "workspace",
      "marketplaceView",
      "marketplaceProvider",
      "screen",
      "productionScreen",
      "selectedOrder",
      "selectedOrderKey",
      "selectedReportTask",
      "selectedReportTaskKey",
      "selectedCuttingReportTask",
      "selectedCuttingReportTaskKey",
      "orderCategory",
      "adminTaskStatus",
      "orderMode",
      "orderProductFilter",
      "orderSizeFilter",
      "orderColorFilter",
      "orderProduct",
      "orderProducts",
      "orderTaskType",
      "orderRouteStep",
      "orderMaterial",
      "orderSizes",
      "orderColors",
      "orderQuantity",
      "orderPriority",
      "orderDueDate",
      "orderStockQuantities",
      "orderFabricRolls",
      "reportSection",
      "fabricReceiptMaterial",
      "fabricReceiptColor",
      "fabricReceiptQuantity",
      "warehouseView",
      "warehouseProductFilter",
      "warehouseSizeFilter",
      "warehouseColorFilter",
      "wmsView",
      "wmsStockFilter",
      "wmsStockProductFilter",
      "wmsStockSizeFilter",
      "wmsStockColorFilter",
      "wmsSelectedLocationId",
      "wmsMapSearch",
      "wmsMapStatusFilter",
      "wmsCatalogSearch",
      "wmsCatalogGroup",
      "adminSection",
      "employeePositionFilter",
      "employeeStatusFilter",
      "employeeShiftFilter",
      "adminReportType",
      "adminStartDate",
      "adminEndDate",
      "adminEmployeeId",
      "adminShiftEndTime",
      "adminHomePeriod",
      "adminHomeView",
      "adminHomeEmployee",
      "analyticsView",
      "analyticsStage",
      "analyticsTaskId",
      "analyticsReturnView",
      "employeeHomeView",
      "userStartDate",
      "userEndDate",
      "taskCompletionDrafts",
      "cuttingStageDrafts",
      "feedbackDraft",
      "passportBatchId",
      "passportReturnScreen",
      "wmsMaterialReceipt",
    ];
    let persistedUiState = {};

    try {
      const parsedUiState = JSON.parse(window.localStorage.getItem(uiStateStorageKey) || "{}");
      persistedUiStateKeys.forEach((key) => {
        if (Object.prototype.hasOwnProperty.call(parsedUiState, key)) persistedUiState[key] = parsedUiState[key];
      });
    } catch (error) {
      persistedUiState = {};
    }

    const state = {
      workspace: "production",
      marketplaceView: "overview",
      marketplaceProvider: "all",
      screen: "shift",
      productionScreen: "shift",
      selectedOperation: 0,
      selectedOrder: 0,
      selectedOrderKey: "",
      selectedReportTask: 0,
      selectedReportTaskKey: "",
      selectedCuttingReportTask: 0,
      selectedCuttingReportTaskKey: "",
      orderCategory: "",
      adminTaskStatus: "all",
      reportSection: "work",
      orderMode: "list",
      orderProductFilter: "",
      orderSizeFilter: "",
      orderColorFilter: "",
      orderProduct: "",
      orderProducts: [],
      orderTaskType: "cutting",
      orderRouteStep: "",
      orderMaterial: "Ткань",
      orderSizes: [],
      orderColors: [],
      orderQuantity: "1",
      orderPriority: "normal",
      orderDueDate: "",
      orderStockQuantities: {},
      orderFabricRolls: {},
      orderAttachment: null,
      fabricReceiptMaterial: "Ткань",
      fabricReceiptColor: "",
      fabricReceiptQuantity: "",
      warehouseView: "overview",
      warehouseProductFilter: "",
      warehouseSizeFilter: "",
      warehouseColorFilter: "",
      adminSection: "reports",
      employeePositionFilter: "",
      employeeStatusFilter: "",
      employeeShiftFilter: "",
      adminReportType: "period",
      adminStartDate: "",
      adminEndDate: "",
      adminEmployeeId: "",
      adminAppliedReportPayload: null,
      adminShiftEndTime: "",
      adminHomePeriod: "today",
      adminHomeView: "overview",
      adminHomeEmployee: "",
      analyticsView: "overview",
      analyticsStage: "",
      analyticsTaskId: "",
      analyticsReturnView: "overview",
      employeeHomeView: "overview",
      userStartDate: "",
      userEndDate: "",
      taskCompletionDrafts: {},
      cuttingStageDrafts: {},
      feedbackDraft: {category: "Производство", message: ""},
      passportBatchId: "",
      passportData: null,
      passportReturnScreen: "orders",
      profileReturnScreen: "shift",
      taskDefectPhotos: {},
      wmsView: "overview",
      wmsStockFilter: "finished",
      wmsStockProductFilter: "",
      wmsStockSizeFilter: "",
      wmsStockColorFilter: "",
      wmsMapSearch: "",
      wmsMapStatusFilter: "all",
      wmsSelectedLocationId: "",
      wmsData: {loading: false, loaded: false, error: "", locations: [], stock: [], movements: []},
      wmsCatalogSearch: "",
      wmsCatalogGroup: "",
      wmsCatalog: {loading: false, loaded: false, error: "", products: [], lastSyncAt: ""},
      wmsLookup: {barcode: "", productKey: null, error: ""},
      pushDeviceActive: null,
      pushDeviceSyncing: false,
      wmsDraft: {itemType: "finished", productName: "", productSize: "", productColor: "", productScanned: false, fromLocationScanned: false, toLocationScanned: false, stageName: "Готово", readyForPosition: "Склад", quantity: "", unit: "шт", materialUnit: "рул", fromLocation: "", toLocation: "", reason: "", targetState: "SCRAPPED", barcode: "", locationZone: "STORAGE", locationName: ""},
      wmsMaterialReceipt: {name: "Ткань", color: "", unit: "рул", quantity: "", comment: ""},
      marketplaceData: {loading: false, loaded: false, error: "", payload: null},
      marketplaceDetail: null,
      ...persistedUiState,
      data: null,
    };

    if (!state.taskCompletionDrafts || typeof state.taskCompletionDrafts !== "object") state.taskCompletionDrafts = {};
    if (!state.cuttingStageDrafts || typeof state.cuttingStageDrafts !== "object") state.cuttingStageDrafts = {};
    if (!state.feedbackDraft || typeof state.feedbackDraft !== "object") state.feedbackDraft = {category: "Производство", message: ""};
    if (!Array.isArray(state.orderSizes)) state.orderSizes = [];
    if (!Array.isArray(state.orderColors)) state.orderColors = [];
    // Values restored from older browser sessions may be numeric.  Keep the
    // draft representation identical to the string values coming from the
    // HTML data attributes and the API catalog.
    state.orderSizes = state.orderSizes.map((value) => String(value));
    state.orderColors = state.orderColors.map((value) => String(value));
    if (!state.orderStockQuantities || typeof state.orderStockQuantities !== "object") state.orderStockQuantities = {};
    if (!state.orderFabricRolls || typeof state.orderFabricRolls !== "object") state.orderFabricRolls = {};
    if (!Array.isArray(state.orderProducts)) state.orderProducts = state.orderProduct ? [state.orderProduct] : [];
    if (!state.taskDefectPhotos || typeof state.taskDefectPhotos !== "object") state.taskDefectPhotos = {};
    if (!["all", "free", "in_work", "done"].includes(state.adminTaskStatus)) state.adminTaskStatus = "all";
    if (!state.wmsMaterialReceipt || typeof state.wmsMaterialReceipt !== "object") state.wmsMaterialReceipt = {name: "Ткань", color: "", unit: "рул", quantity: "", comment: ""};

    const mount = document.getElementById("mount");
    const appRoot = document.getElementById("appRoot");
    const loginView = document.getElementById("loginView");
    const connectionView = document.getElementById("connectionView");
    const connectionTitle = document.getElementById("connectionTitle");
    const connectionMessage = document.getElementById("connectionMessage");
    const connectionRetryStatus = document.getElementById("connectionRetryStatus");
    const webConnectionRetry = document.getElementById("webConnectionRetry");
    const webLoginForm = document.getElementById("webLoginForm");
    const webRegisterForm = document.getElementById("webRegisterForm");
    const webActionSlot = document.getElementById("webActionSlot");
    const mainButton = document.getElementById("mainButton");
    const topTabs = document.getElementById("topTabs");
    const bottomNav = document.getElementById("bottomNav");
    const toast = document.getElementById("toast");
    const shiftReminder = document.getElementById("shiftReminder");
    const shiftReminderText = document.getElementById("shiftReminderText");
    const shiftReminderClose = document.getElementById("shiftReminderClose");
    const qrScanner = document.getElementById("qrScanner");
    const qrScannerVideo = document.getElementById("qrScannerVideo");
    const qrScannerTitle = document.getElementById("qrScannerTitle");
    const qrScannerStatus = document.getElementById("qrScannerStatus");
    const pendingActions = new Set();
    const webSessionRetryDelaysMs = [2_000, 5_000, 10_000, 20_000, 30_000];
    const webSessionRequestTimeoutMs = 8_000;
    let webSessionRetryAttempt = 0;
    let webSessionRetryTimer = null;
    let webSessionRestorePromise = null;
    let qrScannerStream = null;
    let qrScannerFrame = 0;

    function beginAction(key) {
      if (pendingActions.has(key)) return false;
      pendingActions.add(key);
      return true;
    }

    function endAction(key) {
      pendingActions.delete(key);
    }

    const baseNav = [
      { id: "shift", label: "Главная", icon: "⌂" },
      { id: "report", label: "Отчёт", icon: "＋" },
      { id: "analytics", label: "Аналитика", icon: "▥" },
      { id: "orders", label: "Задания", icon: "▣" },
    ];
    const productionScreens = new Set(["shift", "report", "analytics", "orders", "admin", "passport", "profile"]);
    const warehouseMoreViews = new Set(["more", "lookup", "products", "transfer", "stock", "movements", "inventory", "scrap", "reports", "map"]);

    if (tg) {
      tg.ready();
      tg.expand();
    }

    function updateKeyboardState(forceOpen = null) {
      const viewport = window.visualViewport;
      const activeElement = document.activeElement;
      const editing = Boolean(activeElement && activeElement.matches("input, textarea"));
      const viewportReduced = Boolean(viewport && window.innerHeight - viewport.height > 140);
      document.body.classList.toggle("keyboard-open", forceOpen === null ? editing || viewportReduced : forceOpen);
    }

    if (window.visualViewport) {
      window.visualViewport.addEventListener("resize", () => updateKeyboardState());
      window.visualViewport.addEventListener("scroll", () => updateKeyboardState());
    }

    document.addEventListener("focusin", (event) => {
      if (event.target.matches("input, textarea")) updateKeyboardState(true);
    });
    document.addEventListener("focusout", () => window.setTimeout(() => updateKeyboardState(), 80));

    function escapeHtml(value) {
      return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }

    async function api(path, payload = {}) {
      const headers = {"Content-Type": "application/json"};
      if (isStandaloneWeb && webCsrfToken) headers["X-CSRF-Token"] = webCsrfToken;
      const response = await fetch(path, {
        method: "POST",
        headers,
        credentials: "same-origin",
        body: JSON.stringify({
          ...payload,
          telegram_id: debugTelegramId,
        }),
      });
      const data = await response.json();

      if (!response.ok) {
        const error = new Error(data.message || `HTTP ${response.status}`);
        error.apiMessage = data.message || "";
        error.status = response.status;
        if (response.status === 401 && isStandaloneWeb) showWebLogin(data.message || "Войдите в приложение.");
        throw error;
      }

      return data;
    }

    function createRequestId() {
      if (window.crypto && typeof window.crypto.randomUUID === "function") return window.crypto.randomUUID();
      return `${Date.now()}-${Math.random().toString(16).slice(2)}-${Math.random().toString(16).slice(2)}`;
    }

    function getCompletionQueue() {
      try {
        const rows = JSON.parse(window.localStorage.getItem(completionQueueKey) || "[]");
        return Array.isArray(rows) ? rows : [];
      } catch (error) {
        return [];
      }
    }

    function saveCompletionQueue(rows) {
      try {
        window.localStorage.setItem(completionQueueKey, JSON.stringify(rows.slice(-20)));
        return true;
      } catch (error) {
        return false;
      }
    }

    function queueCompletion(payload) {
      const rows = getCompletionQueue().filter((row) => row.request_id !== payload.request_id);
      rows.push(payload);
      return saveCompletionQueue(rows);
    }

    async function flushCompletionQueue(showResult = false) {
      const rows = getCompletionQueue();
      if (!rows.length || !navigator.onLine) return;
      const remaining = [];
      let synced = 0;

      for (const payload of rows) {
        try {
          const result = await api("/api/routes/complete", payload);
          if (result.ok) synced += 1;
          else remaining.push(payload);
        } catch (error) {
          remaining.push(payload);
        }
      }

      saveCompletionQueue(remaining);
      if (synced) {
        if (showResult) showToast("Синхронизация", `Отправлено заданий: ${synced}`);
        window.setTimeout(() => refreshState(), 0);
      }
    }

    window.addEventListener("online", () => flushCompletionQueue(true));

    function showToast(title, text) {
      toast.querySelector("b").textContent = title;
      toast.querySelector("span").textContent = text;
      toast.classList.add("show");
      clearTimeout(window.toastTimer);
      window.toastTimer = setTimeout(() => toast.classList.remove("show"), 2600);
    }

    function showShiftCloseReminder(text) {
      shiftReminderText.textContent = text || "В конце рабочего дня обязательно закройте смену в приложении.";
      shiftReminder.hidden = false;
      shiftReminderClose.focus();
    }

    shiftReminderClose.addEventListener("click", () => {
      shiftReminder.hidden = true;
    });

    function persistUiState() {
      const payload = {};
      persistedUiStateKeys.forEach((key) => {
        payload[key] = state[key];
      });

      try {
        window.localStorage.setItem(uiStateStorageKey, JSON.stringify(payload));
      } catch (error) {
        // Telegram may restrict storage in private mode; the in-memory state still works.
      }
    }

    function sewingIcon() {
      return `<svg viewBox="0 0 32 32" aria-hidden="true" width="25" height="25"><path d="M7 22h18v4H7z" fill="none" stroke="currentColor" stroke-width="2"/><path d="M10 22V8h9a5 5 0 0 1 5 5v2" fill="none" stroke="currentColor" stroke-width="2"/><path d="M6 14h5M19 15h8v7M13 8V5M22 15v-3M15 22v-5M13 17h4" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>`;
    }

    function uiIcon(name) {
      const icons = {
        target: `<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3"/>`,
        quality: `<path d="M12 3 19 6v5c0 4.6-2.8 8-7 10-4.2-2-7-5.4-7-10V6l7-3Z"/><path d="m8.8 12 2.1 2.1 4.6-5"/>`,
        work: `<rect x="4" y="7" width="16" height="12" rx="2"/><path d="M9 7V5h6v2M4 12h16M10 12v2h4v-2"/>`,
        layers: `<path d="m12 3 9 5-9 5-9-5 9-5Z"/><path d="m3 12 9 5 9-5M3 16l9 5 9-5"/>`,
        cycle: `<circle cx="12" cy="12" r="8"/><path d="M12 7v5l3 2M7 3.8 4.5 4.4l.6 2.5"/>`,
        lead: `<circle cx="5" cy="17" r="2"/><circle cx="19" cy="7" r="2"/><path d="M7 17h3c5 0 3-10 7-10M14 4l3 3-3 3"/>`,
        schedule: `<rect x="4" y="5" width="16" height="15" rx="2"/><path d="M8 3v4M16 3v4M4 9h16m-11 5 2 2 4-4"/>`,
        defect: `<path d="M12 3 2.8 20h18.4L12 3Z"/><path d="M12 9v5M12 17.5h.01"/>`,
        clipboard: `<rect x="5" y="4" width="14" height="17" rx="2"/><path d="M9 4.5V3h6v1.5M8.5 12l2 2 4.5-5"/>`,
        contour: `<path d="M4 8V4h4M16 4h4v4M20 16v4h-4M8 20H4v-4"/><path d="m8 16 8-8M9 8h7v7"/>`,
        fabric: `<path d="M6 5h10a3 3 0 0 1 3 3v9H9a4 4 0 0 1-4-4V6a1 1 0 0 1 1-1Z"/><circle cx="9" cy="13" r="2.5"/><path d="M19 8h2v9h-2"/>`,
        clock: `<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.5 2"/>`,
        users: `<path d="M16 20v-2a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4v2M9.5 10a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7Z"/><path d="M17 11a3 3 0 0 0 0-6M21 20v-2.2a3.6 3.6 0 0 0-2.5-3.4"/>`,
        inbox: `<path d="M4 5h16v14H4zM4 14h4l2 2h4l2-2h4"/>`,
      };
      return `<svg class="ui-icon" viewBox="0 0 24 24" aria-hidden="true">${icons[name] || icons.target}</svg>`;
    }

    function itemEmpty(text) {
      return `<p class="empty">${escapeHtml(text)}</p>`;
    }

    function attachmentFileUrl(taskId, action) {
      if (!taskId) return "";

      const url = new URL("/api/production/task-attachment", window.location.href);
      url.searchParams.set("task_id", taskId);
      url.searchParams.set("mode", action === "download" ? "download" : "open");

      if (debugTelegramId) url.searchParams.set("telegram_id", debugTelegramId);

      return url.toString();
    }

    async function openTaskAttachment(taskId, action) {
      const url = attachmentFileUrl(taskId, action);

      if (!url) {
        showToast("Файл", "Файл не найден. Обновите задание.");
        return;
      }

      try {
        if (action === "download") {
          const actionKey = `download-attachment:${taskId}`;
          if (!beginAction(actionKey)) return;
          try {
            const response = await fetch(url);
            if (!response.ok) throw new Error("download failed");
            const disposition = response.headers.get("Content-Disposition") || "";
            const utfName = disposition.match(/filename\\*=UTF-8''([^;]+)/i);
            const plainName = disposition.match(/filename="?([^";]+)"?/i);
            const fileName = decodeURIComponent((utfName && utfName[1]) || (plainName && plainName[1]) || `attachment-${taskId}`);
            const blobUrl = URL.createObjectURL(await response.blob());
            const link = document.createElement("a");
            link.href = blobUrl;
            link.download = fileName;
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.setTimeout(() => URL.revokeObjectURL(blobUrl), 1000);
          } finally {
            endAction(actionKey);
          }
          showToast("Файл", "Скачивание запущено.");
          return;
        }

        if (tg && typeof tg.openLink === "function") {
          tg.openLink(url);
        } else {
          const opened = window.open(url, "_blank", "noopener");
          if (!opened) window.location.href = url;
        }

        showToast("Файл", "Открываю файл.");
      } catch (error) {
        showToast("Файл", "Не удалось открыть файл.");
      }
    }

    function renderTaskAttachment(attachment) {
      if (!attachment || !attachment.task_id) return "";

      return `
        <div class="card field-card">
          <label>Файл задания</label>
          <div class="report-row"><div><b>${escapeHtml(attachment.file_name || "Файл")}</b><span>Word, Excel или PDF</span></div><span class="status-chip gray">файл</span></div>
          <div class="button-row"><button class="small-button secondary" data-attachment-action="open" data-attachment-task-id="${escapeHtml(attachment.task_id)}">Открыть файл</button><button class="small-button" data-attachment-action="download" data-attachment-task-id="${escapeHtml(attachment.task_id)}">Скачать</button></div>
        </div>
      `;
    }

    function renderTaskFabricRolls(task) {
      const rows = task && task.fabric_rolls ? task.fabric_rolls : [];
      if (!rows.length) return "";
      const productionTaskId = task.production_task_id || task.source_id || task.id;
      const canReject = Boolean(task.is_assigned_to_me && !(state.data && state.data.is_admin));

      return `
        <div class="card field-card">
          <label>Выданные рулоны</label>
          <div class="op-list">
            ${rows.map((row) => `
              <div class="report-row"><div><b>${escapeHtml(row.product_color_label || row.product_color)}</b><span>${escapeHtml(row.material_name || "Ткань")}${Number(row.rejected_rolls || 0) ? `<br>Брак: ${escapeHtml(row.rejected_rolls)} рул. · доступно ${escapeHtml(row.available_rolls)} рул.` : ""}</span></div><span class="status-chip ${Number(row.rejected_rolls || 0) ? "warn" : ""}">${escapeHtml(row.rolls)} рул.</span></div>
              ${(row.defects || []).map((defect) => `<div class="task-note"><b>Брак ${escapeHtml(defect.quantity)} рул.</b> · ${escapeHtml(defect.comment)}<br><span>${escapeHtml((defect.created_at || "").replace("T", " ").slice(0, 16))}</span></div>`).join("")}
              ${canReject && Number(row.available_rolls || 0) > 0 ? `<div class="button-row"><button type="button" class="small-button danger" data-fabric-defect-task-id="${escapeHtml(productionTaskId)}" data-fabric-defect-color="${escapeHtml(row.product_color)}" data-fabric-defect-available="${escapeHtml(row.available_rolls)}">Отправить рулоны в брак</button></div>` : ""}
            `).join("")}
          </div>
        </div>
      `;
    }

    function progressForTask(task) {
      if (!task) return 0;
      if (task.task_kind === "cutting_stage" || task.stage) {
        if (task.stage === "contours") return 18;
        if (task.stage === "layout") return 42;
        if (task.stage === "cutting") return Math.max(60, Number(task.progress || 0));
        if (task.stage === "formation") return 92;
      }
      if (task.status === "formed") return 100;
      if (task.status === "in_cutting") return 70;
      if (task.status === "contours_done") return 40;
      return 12;
    }

    function confirmTaskTake(task) {
      if (!task) return false;
      const product = task.product_name || task.product || "Изделие не указано";
      const stage = task.stage_title || task.operation || task.stage || "Производственная операция";
      const sizes = (task.sizes || task.product_size || task.size || "-");
      const colors = (task.color_labels || task.colors || task.product_color || task.color || "-");
      const quantity = task.quantity ? `${task.quantity} шт` : "по размерам и цветам";
      const details = [
        `Изделие: ${product}`,
        `Этап: ${stage}`,
        `Размеры: ${Array.isArray(sizes) ? sizes.join(", ") : sizes}`,
        `Цвета: ${Array.isArray(colors) ? colors.join(", ") : colors}`,
        `Количество: ${quantity}`,
        "\\nПосле подтверждения задание закрепится за вами.",
      ].join("\\n");
      return window.confirm(`Взять это задание?\\n\\n${details}`);
    }

    function getReportOperations() {
      return state.data && state.data.report && state.data.report.operations ? state.data.report.operations : [];
    }

    function getFeedbackRows() {
      return state.data && state.data.report && state.data.report.feedback ? state.data.report.feedback : [];
    }

    function getProduction() {
      return state.data && state.data.production ? state.data.production : {};
    }

    function getTasks() {
      return getProduction().tasks || [];
    }

    function getContourTasks() {
      return getProduction().contour_tasks || [];
    }

    function getCuttingTasks() {
      return getProduction().cutting_tasks || [];
    }

    function getWarehouseStock() {
      return getProduction().warehouse_stock || [];
    }

    function getRouteCatalog() {
      return state.data && state.data.routes && state.data.routes.catalog ? state.data.routes.catalog : [];
    }

    function getRouteTasks() {
      return state.data && state.data.routes && state.data.routes.tasks ? state.data.routes.tasks : [];
    }

    function getCompletedProductionTasks() {
      return state.data && state.data.production && state.data.production.completed_tasks
        ? state.data.production.completed_tasks
        : [];
    }

    function getCompletedOrderRows() {
      const productionTasks = state.data && state.data.is_admin ? getCompletedProductionTasks() : [];
      const routeTasks = getCompletedRouteTasks();
      const tasks = productionTasks.map((task) => ({...task, task_kind: "production"}));
      const routeRows = routeTasks.map((task) => ({...task, task_kind: "route"}));
      return [...tasks, ...routeRows];
    }

    function taskIdentity(task) {
      if (!task) return "";
      const kind = task.task_kind || (task.stage ? "cutting_stage" : "route");
      const sourceId = kind === "cutting_stage" ? (task.production_task_id || task.source_id || task.id) : task.id;
      return `${kind}:${sourceId}:${task.stage || ""}`;
    }

    function selectedTaskIndex(tasks, selectedKey, fallbackIndex = 0) {
      if (selectedKey) {
        const matchedIndex = tasks.findIndex((task) => taskIdentity(task) === selectedKey);
        if (matchedIndex >= 0) return matchedIndex;
      }
      return fallbackIndex >= 0 && fallbackIndex < tasks.length ? fallbackIndex : 0;
    }

    function getCompletedRouteTasks() {
      return state.data && state.data.routes && state.data.routes.completed_tasks ? state.data.routes.completed_tasks : [];
    }

    function getMyRouteTasks() {
      return getRouteTasks()
        .filter((task) => task.is_assigned_to_me)
        .map((task) => ({...task, task_kind: "route"}));
    }

    function getDisplayedRouteTask() {
      if (state.screen === "orders") {
        const rows = visibleOrderRows();
        const task = rows[state.selectedOrder] || rows[0];
        return task && task.task_kind === "route" && task.is_assigned_to_me ? task : null;
      }
      const tasks = getMyRouteTasks();
      return tasks[state.selectedReportTask] || tasks[0] || null;
    }

    function getMyCuttingTasks() {
      return getCuttingTasks()
        .filter((task) => task.is_assigned_to_me)
        .map((task) => ({...task, task_kind: "cutting_stage"}));
    }

    function getEmployeeContourTasks() {
      const cuttingContours = getCuttingTasks().filter((task) => task.stage === "contours");
      return cuttingContours.length ? cuttingContours : getContourTasks();
    }

    function getEmployeeFabricRows() {
      const rows = [];
      const seen = new Set();

      getCuttingTasks().forEach((task) => {
        (task.fabric_rolls || []).forEach((roll) => {
          const taskId = task.production_task_id || task.source_id || task.id;
          const key = `${taskId}|${roll.material_name || "Ткань"}|${roll.product_color || roll.product_color_label || ""}|${roll.rolls || 0}`;
          if (seen.has(key)) return;
          seen.add(key);
          rows.push({
            ...roll,
            task_id: taskId,
            product_name: task.product_name || "Изделие",
            stage_title: task.stage_title || "Раскрой",
          });
        });
      });

      return rows;
    }

    function getOrderColors() {
      const colors = getProduction().order_colors || [];
      if (colors.length) return colors;

      const fallbackColors = [];
      getRouteCatalog().forEach((product) => {
        (product.raw_colors || []).forEach((color) => {
          if (!fallbackColors.includes(color)) fallbackColors.push(color);
        });
      });
      return fallbackColors;
    }

    function routeProduct(productName) {
      return getRouteCatalog().find((item) => item.product_name === productName) || getRouteCatalog()[0] || null;
    }

    function routeOperations(product) {
      if (!product || !product.steps) return [];
      return product.steps
        .map((step, index) => ({...step, index}))
        .filter((step) => step.position !== "Раскройщик");
    }

    function currentOrderRows() {
      const productionTasks = state.data && state.data.is_admin ? getTasks() : getCuttingTasks();
      const routeTasks = getRouteTasks();
      const tasks = productionTasks.map((task) => ({...task, task_kind: state.data && state.data.is_admin ? "production" : "cutting_stage"}));
      const routeRows = routeTasks.map((task) => ({...task, task_kind: "route"}));
      return [...tasks, ...routeRows];
    }

    function employeeOrderCategories() {
      const employee = state.data && state.data.employee;
      const position = employee ? employee.position : "";

      if (position === "Упаковщик") return ["Подготовка", "ВТО", "Упаковка"];
      if (position === "Швея") return ["Подготовка", "Прямострочка", "Оверлок"];
      if (position === "Раскройщик") return ["Раскрой"];

      return [];
    }

    function adminOrderCategories() {
      return [
        {id: "cutting", label: "Раскрой"},
        {id: "sewing", label: "Швея"},
        {id: "packing", label: "Упаковка"},
      ];
    }

    function orderCategoryIds() {
      if (state.data && state.data.is_admin) {
        return adminOrderCategories().map((category) => category.id);
      }

      return employeeOrderCategories();
    }

    function ensureOrderCategory() {
      const categories = orderCategoryIds();

      if (!categories.length) {
        state.orderCategory = "";
        return;
      }

      if (!state.orderCategory || !categories.includes(state.orderCategory)) {
        state.orderCategory = categories[0];
      }
    }

    function adminOrderCategoryForTask(task) {
      if (task.task_kind === "production" || task.position === "Раскройщик" || task.category === "Раскрой") {
        return "cutting";
      }

      if (task.position === "Швея") {
        return "sewing";
      }

      if (task.position === "Упаковщик") {
        return "packing";
      }

      return "";
    }

    function adminTaskStatusForRow(task) {
      if (!task) return "unknown";
      if (task.task_kind === "route") return task.work_state || (task.assigned_employee_id ? "in_work" : "free");
      if (task.assigned_employee_id) return "in_work";
      return task.status === "active" ? "free" : (task.status || "unknown");
    }

    function orderTaskStatusBucket(task) {
      const status = adminTaskStatusForRow(task);
      if (status === "done" || ["formed", "cancelled", "cutting_done"].includes(task && task.status)) return "done";
      if (status === "free") return "free";
      return "in_work";
    }

    function adminTaskStatusLabel(status) {
      return {
        all: "Все",
        free: "Свободные",
        in_work: "В работе",
        done: "Завершённые",
      }[status] || status;
    }

    function orderTaskFilterValues(task) {
      if (!task) return {product: "", sizes: [], colors: []};
      const sizes = task.task_kind === "route"
        ? [task.product_size || task.size || ""]
        : (task.sizes || task.size || []);
      const colors = task.task_kind === "route"
        ? [task.product_color || task.color || ""]
        : (task.color_labels || task.colors || task.color || []);
      const asList = (value) => (Array.isArray(value) ? value : [value]).map((item) => String(item || "").trim()).filter(Boolean);
      return {
        product: String(task.product_name || task.product || "").trim(),
        sizes: asList(sizes),
        colors: asList(colors),
      };
    }

    function orderTaskMatchesFilters(task) {
      const values = orderTaskFilterValues(task);
      return (!state.orderProductFilter || values.product === state.orderProductFilter)
        && (!state.orderSizeFilter || values.sizes.includes(state.orderSizeFilter))
        && (!state.orderColorFilter || values.colors.includes(state.orderColorFilter));
    }

    function orderFilterOptions(rows, field) {
      const values = new Set();
      rows.forEach((task) => {
        const taskValues = orderTaskFilterValues(task);
        if (field === "product") {
          if (taskValues.product) values.add(taskValues.product);
        } else {
          (taskValues[field === "size" ? "sizes" : "colors"] || []).forEach((value) => values.add(value));
        }
      });
      return [...values].sort((left, right) => String(left).localeCompare(String(right), "ru", {numeric: true}));
    }

    function visibleOrderRows() {
      const rows = state.adminTaskStatus === "done" ? getCompletedOrderRows() : currentOrderRows();

      if (state.data && state.data.is_admin) {
        ensureOrderCategory();
        return rows.filter((task) => {
          if (adminOrderCategoryForTask(task) !== state.orderCategory) return false;
          if (state.adminTaskStatus !== "all" && orderTaskStatusBucket(task) !== state.adminTaskStatus) return false;
          return orderTaskMatchesFilters(task);
        });
      }

      const categories = employeeOrderCategories();
      const filtered = categories.length
        ? (() => {
          ensureOrderCategory();
          return rows.filter((task) => (task.category || "") === state.orderCategory);
        })()
        : rows;
      return filtered.filter((task) => {
        if (state.adminTaskStatus !== "all" && orderTaskStatusBucket(task) !== state.adminTaskStatus) return false;
        return orderTaskMatchesFilters(task);
      });
    }

    async function selectCuttingTaskForReport(task) {
      if (!task || state.data.is_admin) return;

      if (task.is_assigned_to_me) {
        const tasks = getMyCuttingTasks();
        const index = tasks.findIndex((row) => row.id === task.id && row.stage === task.stage);
        state.selectedCuttingReportTask = index >= 0 ? index : 0;
        state.selectedCuttingReportTaskKey = taskIdentity(tasks[state.selectedCuttingReportTask] || task);
        state.reportSection = "work";
        setScreen("report");
        return;
      }

      if (!task.can_take) {
        showToast("Задание", task.assigned_employee_name ? `Задание в работе у ${task.assigned_employee_name}.` : "Задание уже в работе.");
        return;
      }

      if (!confirmTaskTake(task)) return;

      const productionTaskId = task.production_task_id || task.source_id || task.id;
      const actionKey = `start-cutting-task:${productionTaskId}`;
      if (!beginAction(actionKey)) return;
      mainButton.disabled = true;

      try {
        const data = await api("/api/production/start-cutting-task", {task_id: productionTaskId});

        if (!data.ok) {
          showToast("Задание", data.message || "Не удалось взять задание.");
          mainButton.disabled = false;
          return;
        }

        state.data.production = data.production || state.data.production;
        const tasks = getMyCuttingTasks();
        const index = tasks.findIndex((row) => (row.production_task_id || row.source_id || row.id) === productionTaskId && row.stage === task.stage);
        state.selectedCuttingReportTask = index >= 0 ? index : 0;
        state.selectedCuttingReportTaskKey = taskIdentity(tasks[state.selectedCuttingReportTask] || task);
        state.reportSection = "work";
        setScreen("report");
        showToast("Задание", data.message || "Задание взято в работу.");
      } catch (error) {
        showToast("Ошибка", "Не удалось взять задание.");
        mainButton.disabled = false;
      } finally {
        endAction(actionKey);
      }
    }

    async function releaseCuttingTask(task) {
      const adminRelease = Boolean(state.data && state.data.is_admin);
      if (!task || (!task.is_assigned_to_me && !adminRelease)) return;
      const reason = window.prompt(
        adminRelease ? "Почему освобождаете задание?" : "Почему возвращаете задание?",
        adminRelease ? "Передать другому сотруднику" : "Нужно передать другому сотруднику",
      ) || "";
      if (!reason.trim()) return;
      const productionTaskId = task.production_task_id || task.source_id || task.id;
      const actionKey = `release-cutting-task:${productionTaskId}`;
      if (!beginAction(actionKey)) return;
      mainButton.disabled = true;
      try {
        const data = await api("/api/production/release-cutting-task", {
          task_id: productionTaskId,
          reason: reason.trim(),
        });
        if (!data.ok) {
          showToast("Задание", data.message || "Не удалось вернуть задание.");
          mainButton.disabled = false;
          return;
        }
        state.data.production = data.production || state.data.production;
        if (data.routes) state.data.routes = data.routes;
        state.selectedCuttingReportTask = 0;
        state.selectedCuttingReportTaskKey = "";
        state.reportSection = "work";
        render();
        showToast("Задание", data.message || "Задание возвращено в свободные.");
      } catch (error) {
        showToast("Ошибка", "Не удалось вернуть задание.");
        mainButton.disabled = false;
      } finally {
        endAction(actionKey);
      }
    }

    function shiftText() {
      const shift = state.data && state.data.shift;
      if (!shift) return "Смена не открыта";
      return shift.status === "open" ? "Смена открыта" : "Смена закрыта";
    }

    function navItems() {
      if (state.data && state.data.is_admin) {
        return [
          { id: "shift", label: "Главная", icon: "⌂" },
          { id: "analytics", label: "Аналитика", icon: "▥" },
          { id: "orders", label: "Заказы", icon: "▣" },
          { id: "admin", label: "Админ", icon: "◎" },
        ];
      }
      return baseNav;
    }

    function canAccessWms() {
      if (!state.data) return false;
      return Boolean(state.data.features && state.data.features.can_wms);
    }

    function canAccessMarketplaces() {
      return Boolean(state.data && state.data.is_admin);
    }

    function renderBottomNav() {
      if (state.workspace === "warehouse") {
        const wmsItems = [
          {id: "overview", label: "Главная", icon: "⌂"},
          {id: "receive", label: "Приёмка", icon: "↓"},
          {id: "putaway", label: "Размещение", icon: "→"},
          {id: "pick", label: "Выдача", icon: "↑"},
          {id: "more", label: "Ещё", icon: "•••"},
        ];
        bottomNav.style.setProperty("--nav-count", wmsItems.length);
        bottomNav.innerHTML = wmsItems.map((item) => `
          <button class="nav-btn ${(item.id === "more" ? warehouseMoreViews.has(state.wmsView) : state.wmsView === item.id) ? "active" : ""}" data-wms-view="${item.id}">
            <span class="nav-ico">${item.icon}</span><span>${item.label}</span>
          </button>
        `).join("");
        return;
      }

      if (state.workspace === "marketplaces") {
        const marketplaceItems = [
          {id: "overview", label: "Маркетплейсы", icon: "◎"},
          {id: "products", label: "Товары", icon: "▤"},
          {id: "stocks", label: "Остатки", icon: "▦"},
          {id: "analytics", label: "Аналитика", icon: "▥"},
          {id: "orders", label: "Отгрузки", icon: "↑"},
          {id: "sync", label: "Синхронизация", icon: "↻"},
        ];
        bottomNav.style.setProperty("--nav-count", marketplaceItems.length);
        bottomNav.innerHTML = marketplaceItems.map((item) => `
          <button class="nav-btn ${state.marketplaceView === item.id ? "active" : ""}" data-marketplace-view="${item.id}">
            <span class="nav-ico">${item.icon}</span><span>${item.label}</span>
          </button>
        `).join("");
        return;
      }

      const items = navItems();
      bottomNav.style.setProperty("--nav-count", items.length);
      bottomNav.innerHTML = items.map((item) => `
        <button class="nav-btn ${state.screen === item.id ? "active" : ""} ${item.desktop_redundant ? "desktop-redundant" : ""}" data-go="${item.id}">
          <span class="nav-ico">${item.icon}</span><span>${item.label}</span>
        </button>
      `).join("");
    }

    function renderTopTabs() {
      let tabs = [];

      if (state.screen === "shift" && state.data && state.data.is_admin) {
        tabs = [
          ["today", "Сегодня"],
          ["month", "Месяц"],
          ["quarter", "Квартал"],
        ].map(([id, label]) => ({
          id,
          label,
          attr: "data-admin-home-period",
          active: state.adminHomePeriod === id,
        }));
      }

      if (state.screen === "orders" && state.data && !state.data.is_admin) {
        ensureOrderCategory();
        tabs = employeeOrderCategories().map((category) => ({
          id: category,
          label: category,
          attr: "data-order-category",
          active: state.orderCategory === category,
        }));
      }

      if (state.screen === "orders" && state.data && state.data.is_admin && state.orderMode !== "create") {
        ensureOrderCategory();
        tabs = adminOrderCategories().map((category) => ({
          id: category.id,
          label: category.label,
          attr: "data-order-category",
          active: state.orderCategory === category.id,
        }));
      }

      if (state.screen === "report" && state.data && !state.data.is_admin) {
        tabs = [
          ["work", "В работе"],
          ["done", "Завершено"],
          ["feedback", "Обратная связь"],
        ].map(([id, label]) => ({
          id,
          label,
          attr: "data-report-section",
          active: state.reportSection === id,
        }));
      }

      topTabs.hidden = tabs.length === 0;
      topTabs.style.setProperty("--tab-count", tabs.length || 1);
      topTabs.innerHTML = tabs.map((tab) => `
        <button class="tab ${tab.active ? "active" : ""}" ${tab.attr}="${tab.id}">${tab.label}</button>
      `).join("");
    }

    function roleLabel() {
      if (state.data && state.data.is_admin) return "Администратор";
      const employee = state.data && state.data.employee;
      if (!employee) return "Нет доступа";
      const position = employee.position || "Сотрудник";
      return canAccessWms() ? `${position} + Кладовщик` : position;
    }

    function getAdmin() {
      return state.data && state.data.admin ? state.data.admin : null;
    }

    function getAdminReport() {
      const admin = getAdmin();
      return admin && admin.reports ? admin.reports : null;
    }

    function getHistory() {
      return state.data && state.data.history ? state.data.history : null;
    }

    function ensureUserDefaults() {
      const admin = getAdmin();
      const defaults = admin && admin.period_defaults ? admin.period_defaults : {};
      const history = getHistory();

      if (!state.userStartDate) {
        state.userStartDate = (history && history.start_date) || defaults.start_date || "";
      }
      if (!state.userEndDate) {
        state.userEndDate = (history && history.end_date) || defaults.end_date || "";
      }
    }

    function getHistoryPayload() {
      ensureUserDefaults();
      return {
        start_date: state.userStartDate,
        end_date: state.userEndDate,
      };
    }

    function ensureAdminDefaults() {
      const admin = getAdmin();
      const report = getAdminReport();
      const defaults = admin && admin.period_defaults ? admin.period_defaults : {};

      if (!state.adminStartDate) {
        state.adminStartDate = (report && report.start_date) || defaults.start_date || "";
      }
      if (!state.adminEndDate) {
        state.adminEndDate = (report && report.end_date) || defaults.end_date || "";
      }
      if (!state.adminEmployeeId && admin && admin.employees && admin.employees[0]) {
        state.adminEmployeeId = String(admin.employees[0].id);
      }
    }

    function syncHistoryForm() {
      const start = document.getElementById("userStartDate");
      const end = document.getElementById("userEndDate");

      if (start) state.userStartDate = start.value;
      if (end) state.userEndDate = end.value;
    }

    function getAdminReportPayload() {
      ensureAdminDefaults();
      return {
        report_type: state.adminReportType,
        start_date: state.adminStartDate,
        end_date: state.adminEndDate,
        employee_id: state.adminEmployeeId,
      };
    }

    function adminReportTotals(report) {
      if (!report) return { shifts: 0, minutes: 0, operations: 0, employees: 0 };

      if (report.type === "employee") {
        const summary = report.employee_summary || {};
        return {
          shifts: summary.shift_count || 0,
          minutes: summary.total_minutes || 0,
          operations: (report.employee_operations || []).length,
          employees: summary.full_name ? 1 : 0,
        };
      }

      const summaryRows = report.summary || [];
      return {
        shifts: summaryRows.reduce((sum, row) => sum + Number(row.shift_count || 0), 0),
        minutes: summaryRows.reduce((sum, row) => sum + Number(row.total_minutes || 0), 0),
        operations: (report.operations || []).length,
        employees: summaryRows.length,
      };
    }

    function minutesLabel(minutes) {
      const total = Number(minutes || 0);
      const hours = Math.floor(total / 60);
      const rest = total % 60;
      return `${hours}:${String(rest).padStart(2, "0")}`;
    }

    function syncAdminForm() {
      const type = document.getElementById("adminReportType");
      const start = document.getElementById("adminStartDate");
      const end = document.getElementById("adminEndDate");
      const employee = document.getElementById("adminEmployeeId");

      if (type) state.adminReportType = type.value;
      if (start) state.adminStartDate = start.value;
      if (end) state.adminEndDate = end.value;
      if (employee) state.adminEmployeeId = employee.value;
    }

    function replaceAdminDashboard(data, fallbackMessage) {
      if (!data.ok) {
        showToast("Админ", data.message || fallbackMessage || "Действие не выполнено.");
        mainButton.disabled = false;
        return;
      }

      state.data.admin = data;
      notifyCriticalNotifications(data.critical_notifications || []);
      render();
      showToast("Админ", data.message || fallbackMessage || "Данные обновлены.");
    }

    function notifyCriticalNotifications(notifications) {
      if (!("Notification" in window) || !notifications.length) return;
      state.notifiedCriticalIds = state.notifiedCriticalIds || {};
      const fresh = notifications.filter((item) => !state.notifiedCriticalIds[item.id]);
      if (!fresh.length) return;
      if (Notification.permission !== "granted") return;
      fresh.slice(0, 3).forEach((item) => {
        state.notifiedCriticalIds[item.id] = true;
        new Notification(item.title || "Критичное уведомление", {body: item.message || "Проверьте входящую продукцию."});
      });
    }

    function webPushSupported() {
      return window.isSecureContext && "serviceWorker" in navigator && "PushManager" in window && "Notification" in window;
    }

    function webPushApplicationKey(value) {
      const normalized = String(value || "").replace(/-/g, "+").replace(/_/g, "/");
      const padded = normalized + "=".repeat((4 - normalized.length % 4) % 4);
      const decoded = atob(padded);
      return Uint8Array.from(decoded, (character) => character.charCodeAt(0));
    }

    async function syncWebPushDeviceState() {
      if (!webPushSupported() || state.pushDeviceSyncing) return;
      state.pushDeviceSyncing = true;
      try {
        const registration = await navigator.serviceWorker.ready;
        const subscription = await registration.pushManager.getSubscription();
        const active = Boolean(subscription);
        if (state.pushDeviceActive !== active) {
          state.pushDeviceActive = active;
          if (state.data && state.data.is_admin && state.screen === "shift") render();
        }
      } catch (error) {
        state.pushDeviceActive = false;
      } finally {
        state.pushDeviceSyncing = false;
      }
    }

    async function enableAdminWebPush() {
      const actionKey = "web-push-enable";
      if (!beginAction(actionKey)) return;
      try {
        if (!webPushSupported()) throw new Error("unsupported");
        const config = await api("/api/admin/web-push/config");
        if (!config.ok || !config.configured || !config.public_key) {
          showToast("Уведомления", config.message || "Сервер уведомлений пока не настроен.");
          return;
        }
        const permission = await Notification.requestPermission();
        if (permission !== "granted") {
          showToast("Уведомления", "Разрешите уведомления в настройках телефона и попробуйте снова.");
          return;
        }
        const registration = await navigator.serviceWorker.ready;
        let subscription = await registration.pushManager.getSubscription();
        if (!subscription) {
          subscription = await registration.pushManager.subscribe({
            userVisibleOnly: true,
            applicationServerKey: webPushApplicationKey(config.public_key),
          });
        }
        const data = await api("/api/admin/web-push/subscribe", {subscription: subscription.toJSON()});
        if (!data.ok) {
          showToast("Уведомления", data.message || "Не удалось включить уведомления.");
          return;
        }
        state.pushDeviceActive = true;
        if (state.data && state.data.admin) state.data.admin.web_push_subscription = data.subscription;
        render();
        showToast("Уведомления", data.message || "Уведомления включены.");
      } catch (error) {
        showToast("Уведомления", error.message === "unsupported" ? "Откройте установленное приложение с экрана «Домой»." : "Не удалось включить уведомления на этом телефоне.");
      } finally {
        endAction(actionKey);
      }
    }

    async function disableAdminWebPush() {
      const actionKey = "web-push-disable";
      if (!beginAction(actionKey)) return;
      try {
        const registration = await navigator.serviceWorker.ready;
        const subscription = await registration.pushManager.getSubscription();
        if (!subscription) {
          state.pushDeviceActive = false;
          render();
          showToast("Уведомления", "На этом телефоне уведомления уже отключены.");
          return;
        }
        const data = await api("/api/admin/web-push/unsubscribe", {subscription: subscription.toJSON()});
        await subscription.unsubscribe();
        state.pushDeviceActive = false;
        if (state.data && state.data.admin && data.subscription) state.data.admin.web_push_subscription = data.subscription;
        render();
        showToast("Уведомления", data.message || "Уведомления отключены.");
      } catch (error) {
        showToast("Уведомления", "Не удалось отключить уведомления на этом телефоне.");
      } finally {
        endAction(actionKey);
      }
    }

    async function testAdminWebPush() {
      const actionKey = "web-push-test";
      if (!beginAction(actionKey)) return;
      try {
        const data = await api("/api/admin/web-push/test");
        showToast("Уведомления", data.message || (data.ok ? "Тест отправлен." : "Тест не отправлен."));
      } catch (error) {
        showToast("Уведомления", error.apiMessage || "Не удалось отправить тестовое уведомление.");
      } finally {
        endAction(actionKey);
      }
    }

    function getAdminHomePeriod() {
      const admin = getAdmin() || {};
      const periods = admin.home && admin.home.periods ? admin.home.periods : {};
      return periods[state.adminHomePeriod] || periods.today || {
        id: state.adminHomePeriod,
        title: "Главная",
        start_date: "",
        end_date: "",
        plan_text: "0",
        fact_text: "0",
        defect_count: 0,
        employees: [],
        defects: [],
      };
    }

    function periodDateLabel(period) {
      if (!period) return "";
      if (!period.start_date || period.start_date === period.end_date) return period.start_date || "";
      return `${period.start_date} — ${period.end_date}`;
    }

    function homeEmployeeTitle(period) {
      if (period && period.id === "today") return "Сотрудники на смене";
      if (period && period.id === "quarter") return "Сотрудники за квартал";
      return "Сотрудники за месяц";
    }

    function renderPlanFactCards(entity) {
      const plan = Number(entity.plan || 0);
      const fact = Number(entity.fact || 0);
      const factPercent = plan > 0 ? Math.min(100, Math.round(fact * 100 / plan)) : 0;
      return `
        <div class="kpi-grid">
          <div class="card kpi"><div class="kpi-top"><span>План</span><div class="kpi-ico">${uiIcon("target")}</div></div><strong>${escapeHtml(entity.plan_text || "0")}</strong><span>Плановое количество</span><div class="progress"><i style="--w:0%"></i></div></div>
          <div class="card kpi good"><div class="kpi-top"><span>Факт</span><div class="kpi-ico">${uiIcon("quality")}</div></div><strong>${escapeHtml(entity.fact_text || "0")}</strong><span>Сделано по заданиям</span><div class="progress sage"><i style="--w:${factPercent}%"></i></div></div>
        </div>
      `;
    }

    function renderCriticalNotifications() {
      const admin = getAdmin() || {};
      const notifications = admin.critical_notifications || [];
      if (!notifications.length) return "";
      return `
        <div class="section-title"><b>Критичные уведомления</b><span>${notifications.length}</span></div>
        <div class="op-list">
          ${notifications.map((item) => `
            <div class="card report-row">
              <div><b>Критично · ${escapeHtml(item.product_name || "Входящая продукция")}</b><span>${escapeHtml(item.operation_name || "Операция")} · ${escapeHtml(item.product_size || "-")} · ${escapeHtml(item.product_color || "-")}<br>Нужно ${escapeHtml(item.needed_quantity || 0)} шт. · доступно ${escapeHtml(item.available_quantity || 0)} шт. · не хватает ${escapeHtml(item.missing_quantity || 0)} шт.<br>${escapeHtml(item.message || "Проверьте остатки и маршрут.")}</span></div>
              <button class="small-button secondary" data-critical-notification="${escapeHtml(item.id)}">Просмотрено</button>
            </div>
          `).join("")}
        </div>
      `;
    }

    function renderWebPushCard() {
      const admin = getAdmin() || {};
      const subscription = admin.web_push_subscription || {};
      const active = state.pushDeviceActive === null ? Boolean(subscription.active) : state.pushDeviceActive;
      const configured = Boolean(admin.web_push_configured);
      const supported = webPushSupported();
      let description = "Получайте критические уведомления, даже когда приложение закрыто.";
      if (!supported) description = "Этот браузер не поддерживает push-уведомления. На iPhone откройте приложение с экрана «Домой».";
      else if (!configured) description = "Сервер уведомлений пока не настроен.";
      else if (active) description = `Уведомления включены на ${Number(subscription.active_count || 1)} устройстве(ах).`;
      return `
        <div class="section-title"><b>Уведомления на телефон</b><span>${active ? "включены" : "выключены"}</span></div>
        <div class="card field-card">
          <div class="report-row"><div><b>${active ? "Критические push включены" : "Включить критические push"}</b><span>${escapeHtml(description)}</span></div><span class="status-chip ${active ? "" : "gray"}">${active ? "активно" : "не активно"}</span></div>
          <div class="button-row">${active ? `<button class="small-button secondary" data-push-action="test">Отправить тест</button>` : ""}<button class="small-button ${active ? "danger" : ""}" data-push-action="${active ? "disable" : "enable"}" ${!supported || !configured ? "disabled" : ""}>${active ? "Отключить на этом телефоне" : "Включить на этом телефоне"}</button></div>
        </div>
      `;
    }

    function renderAdminHomeOverview(period) {
      const employees = period.employees || [];
      const title = period.id === "today" ? "Текущая смена" : period.title;

      return `
        <div class="screen-head"><div><h2>${escapeHtml(title)}</h2><p>${escapeHtml(period.title)} · план/факт.</p></div><div class="date">${escapeHtml(periodDateLabel(period))}</div></div>
        <div class="card shift-card" data-admin-home-view="planfact">
          <div><b>План / факт</b><span>План ${escapeHtml(period.plan_text || "0")} · факт ${escapeHtml(period.fact_text || "0")}</span></div>
          <span class="status-chip">открыть</span>
        </div>
        <div class="op-list">
          <div class="card report-row" data-admin-home-view="employees"><div><b>${escapeHtml(homeEmployeeTitle(period))}</b><span>${escapeHtml(employees.length)} сотрудников · план/факт по каждому</span></div><span class="status-chip gray">›</span></div>
          <div class="card report-row" data-admin-home-view="defects"><div><b>Брак</b><span>${escapeHtml(period.defect_count || 0)} записей · изделие, этап, причина</span></div><span class="status-chip gray">›</span></div>
        </div>
        ${renderWebPushCard()}
        ${renderCriticalNotifications()}
      `;
    }

    function renderAdminHomePlanFact(period) {
      return `
        <div class="screen-head"><div><h2>План / факт</h2><p>${escapeHtml(period.title)}</p></div><div class="date">${escapeHtml(periodDateLabel(period))}</div></div>
        ${renderPlanFactCards(period)}
      `;
    }

    function renderAdminHomeEmployees(period) {
      const employees = period.employees || [];

      return `
        <div class="screen-head"><div><h2>${escapeHtml(homeEmployeeTitle(period))}</h2><p>${escapeHtml(period.title)} · сотрудник, должность, план/факт.</p></div><div class="date">${escapeHtml(employees.length)} чел</div></div>
        <div class="op-list">
          ${employees.length ? employees.map((employee, index) => `
            <div class="card report-row" data-admin-home-employee="${index}">
              <div><b>${escapeHtml(employee.name)}</b><span>${escapeHtml(employee.position)}${employee.on_shift ? ` · на смене${employee.start_time ? ` с ${escapeHtml(employee.start_time)}` : ""}` : (employee.start_time && employee.end_time ? ` · смена ${escapeHtml(employee.start_time)} — ${escapeHtml(employee.end_time)}` : "")}<br>План ${escapeHtml(employee.plan_text || "0")} · факт ${escapeHtml(employee.fact_text || "0")}</span></div>
              <span class="status-chip gray">›</span>
            </div>
          `).join("") : itemEmpty(period.id === "today" ? "Сотрудников на смене пока нет." : "За период сотрудников с отчётами пока нет.")}
        </div>
      `;
    }

    function renderAdminHomeEmployee(period) {
      const employees = period.employees || [];
      const employee = employees[Number(state.adminHomeEmployee)] || employees[0];

      if (!employee) {
        state.adminHomeView = "employees";
        return renderAdminHomeEmployees(period);
      }

      return `
        <div class="screen-head"><div><h2>${escapeHtml(employee.name)}</h2><p>${escapeHtml(employee.position)} · ${escapeHtml(period.title)}</p></div><div class="date">${escapeHtml(periodDateLabel(period))}</div></div>
        ${renderPlanFactCards(employee)}
        <div class="section-title"><b>Задания / факт</b><span>${(employee.operations || []).length}</span></div>
        <div class="op-list">
          ${(employee.operations || []).length ? employee.operations.map((operation) => `
            <div class="card report-row"><div><b>${escapeHtml(operation.operation)}</b><span>${escapeHtml(operation.stage)} · ${escapeHtml(operation.date || "")}<br>${escapeHtml(operation.size)} · ${escapeHtml(operation.color)}</span></div><span class="status-chip">${escapeHtml(operation.quantity_text)} ${escapeHtml(operation.unit)}</span></div>
          `).join("") : itemEmpty("Фактических операций за период пока нет.")}
        </div>
      `;
    }

    function renderAdminHomeDefects(period) {
      const defects = period.defects || [];

      mainButton.textContent = "Обновить главную";
      mainButton.disabled = false;

      return `
        <div class="screen-head"><div><h2>Брак</h2><p>${escapeHtml(period.title)} · изделие, этап, причина.</p></div><div class="date">${escapeHtml(defects.length)} записей</div></div>
        <div class="op-list">
          ${defects.length ? defects.map((defect) => `
            <div class="card report-row"><div><b>${escapeHtml(defect.product || "-")} · ${escapeHtml(defect.quantity || 0)} шт</b><span>${escapeHtml(defect.stage || "-")} · ${escapeHtml(defect.size || "-")} · ${escapeHtml(defect.color || "-")}<br>${escapeHtml(defect.reason || "Причина не указана")} · ${escapeHtml(defect.disposition || "Решение не указано")}${defect.rework_batch_id ? ` · переделка #${escapeHtml(defect.rework_batch_id)}` : ""}</span></div><span class="status-chip gray">${escapeHtml(defect.date || "")}</span></div>
          `).join("") : `
            <div class="card field-card">
              <div class="report-row"><div><b>Изделие</b><span>Этап<br>Причина</span></div><span class="status-chip gray">0</span></div>
            </div>
          `}
        </div>
      `;
    }

    function renderAdminHome() {
      const period = getAdminHomePeriod();

      mainButton.textContent = "Обновить главную";
      mainButton.disabled = false;

      if (state.adminHomeView === "planfact") {
        mount.innerHTML = renderAdminHomePlanFact(period);
        return;
      }
      if (state.adminHomeView === "employees") {
        mount.innerHTML = renderAdminHomeEmployees(period);
        return;
      }
      if (state.adminHomeView === "employee") {
        mount.innerHTML = renderAdminHomeEmployee(period);
        return;
      }
      if (state.adminHomeView === "defects") {
        mount.innerHTML = renderAdminHomeDefects(period);
        return;
      }

      mount.innerHTML = renderAdminHomeOverview(period);
    }

    async function loadHistory() {
      const actionKey = "load-history";
      if (!beginAction(actionKey)) return;
      syncHistoryForm();
      mainButton.disabled = true;

      try {
        const data = await api("/api/report/history", getHistoryPayload());
        if (!data.ok) {
          showToast("История", data.message || "Не удалось загрузить историю.");
          mainButton.disabled = false;
          return;
        }
        state.data.history = data;
        render();
        showToast("История", "Данные обновлены.");
      } catch (error) {
        showToast("Ошибка", "Не удалось загрузить историю.");
        mainButton.disabled = false;
      } finally {
        endAction(actionKey);
      }
    }

    async function sendFeedback() {
      const actionKey = "send-feedback";
      if (!beginAction(actionKey)) return;
      const category = document.getElementById("feedbackCategory");
      const message = document.getElementById("feedbackMessage");
      mainButton.disabled = true;

      try {
        const data = await api("/api/feedback/send", {
          category: category ? category.value : "",
          message: message ? message.value : "",
        });
        if (!data.ok) {
          showToast("Связь", data.message || "Не удалось отправить сообщение.");
          mainButton.disabled = false;
          return;
        }
        state.data.report = data.report || state.data.report;
        state.feedbackDraft = {
          category: category ? category.value : "Производство",
          message: "",
        };
        render();
        showToast("Связь", data.message || "Сообщение отправлено.");
      } catch (error) {
        showToast("Ошибка", "Не удалось отправить сообщение.");
        mainButton.disabled = false;
      } finally {
        endAction(actionKey);
      }
    }

    async function refreshAdminDashboard(message = "Данные обновлены.") {
      if (!state.data || !state.data.is_admin) return;
      mainButton.disabled = true;

      try {
        const data = await api("/api/admin/dashboard");
        replaceAdminDashboard(data, message);
      } catch (error) {
        showToast("Ошибка", "Не удалось обновить админ-раздел.");
        mainButton.disabled = false;
      }
    }

    async function refreshMarketplaces({silent = false} = {}) {
      if (!canAccessMarketplaces() || state.marketplaceData.loading) return;
      state.marketplaceDetail = null;
      state.marketplaceData.loading = true;
      state.marketplaceData.error = "";
      if (!silent) render();
      try {
        const data = await api("/api/marketplaces/dashboard");
        if (!data.ok) throw new Error(data.message || "Не удалось загрузить маркетплейсы.");
        state.marketplaceData.payload = data;
        state.marketplaceData.loaded = true;
      } catch (error) {
        state.marketplaceData.error = error.apiMessage || error.message || "Не удалось загрузить маркетплейсы.";
      } finally {
        state.marketplaceData.loading = false;
        if (state.workspace === "marketplaces") render();
      }
    }

    async function syncMarketplaces() {
      if (!canAccessMarketplaces() || state.marketplaceData.loading) return;
      state.marketplaceDetail = null;
      state.marketplaceData.loading = true;
      state.marketplaceData.error = "";
      render();
      try {
        const result = await api("/api/marketplaces/sync");
        if (!result.ok) {
          showToast("Маркетплейсы", result.message || "Синхронизация не выполнена.");
        } else {
          showToast("Маркетплейсы", result.message || "Данные синхронизированы.");
        }
        const data = await api("/api/marketplaces/dashboard");
        state.marketplaceData.payload = data;
        state.marketplaceData.loaded = true;
      } catch (error) {
        state.marketplaceData.error = error.apiMessage || error.message || "Не удалось синхронизировать маркетплейс.";
        showToast("Ошибка", state.marketplaceData.error);
      } finally {
        state.marketplaceData.loading = false;
        render();
      }
    }

    async function adminEmployeeStatus(employeeId, status) {
      mainButton.disabled = true;

      try {
        const data = await api("/api/admin/employee/status", {
          employee_id: employeeId,
          status,
        });
        if (!data.ok) throw new Error(data.message || "Не удалось изменить статус.");
        replaceAdminDashboard(data, "Статус сотрудника изменён.");
      } catch (error) {
        showToast("Ошибка", error.message || "Не удалось изменить статус.");
        mainButton.disabled = false;
      }
    }

    async function adminSizeMarkerStatus(taskId, status) {
      mainButton.disabled = true;
      try {
        const data = await api("/api/admin/size-markers/status", {
          task_id: taskId,
          status,
        });
        if (!data.ok) throw new Error(data.message || "Не удалось изменить задание размерников.");
        replaceAdminDashboard(data, data.message || "Задание размерников обновлено.");
      } catch (error) {
        showToast("Размерники", error.message || "Не удалось изменить задание.");
        mainButton.disabled = false;
      }
    }

    async function adminCompleteRouteOperation(batchId) {
      const performer = document.getElementById(`adminPerformer${batchId}`);
      const quantity = document.getElementById(`adminGoodQuantity${batchId}`);
      if (!performer || !performer.value) {
        showToast("Операции", "Выберите исполнителя.");
        performer?.focus();
        return;
      }
      mainButton.disabled = true;
      try {
        const data = await api("/api/admin/route/complete", {
          batch_id: batchId,
          performer_id: performer.value,
          good_quantity: quantity ? quantity.value : "",
        });
        if (!data.ok) throw new Error(data.message || "Не удалось закрыть операцию.");
        replaceAdminDashboard(data, "Операция закрыта.");
      } catch (error) {
        showToast("Операции", error.message || "Не удалось закрыть операцию.");
        mainButton.disabled = false;
      }
    }

    async function adminEmployeePosition(employeeId) {
      const select = document.getElementById(`employeePosition${employeeId}`);
      mainButton.disabled = true;

      try {
        const data = await api("/api/admin/employee/position", {
          employee_id: employeeId,
          position: select ? select.value : "",
        });
        if (!data.ok) throw new Error(data.message || "Не удалось изменить должность.");
        replaceAdminDashboard(data, "Должность изменена.");
      } catch (error) {
        showToast("Ошибка", error.message || "Не удалось изменить должность.");
        mainButton.disabled = false;
      }
    }

    async function adminEmployeeWmsAccess(employeeId, enabled) {
      mainButton.disabled = true;

      try {
        const data = await api("/api/admin/employee/wms-access", {
          employee_id: employeeId,
          enabled,
        });
        if (!data.ok) throw new Error(data.message || "Не удалось изменить доступ к складу.");
        replaceAdminDashboard(data, data.message || "Доступ к складу изменён.");
      } catch (error) {
        showToast("Склад", error.message || "Не удалось изменить доступ к складу.");
        mainButton.disabled = false;
      }
    }

    async function adminEmployeeRole(employeeId, role) {
      const select = document.getElementById(`employeePosition${employeeId}`);
      const position = select ? select.value : "";
      if (role === "employee" && !position) {
        showToast("Должность", "Выберите должность, с которой пользователь продолжит работу.");
        select?.focus();
        return;
      }
      const confirmation = role === "admin"
        ? "Назначить этому пользователю права администратора?"
        : "Снять права администратора и перевести пользователя в сотрудники?";
      if (!window.confirm(confirmation)) return;

      mainButton.disabled = true;
      try {
        const data = await api("/api/admin/employee/role", {
          employee_id: employeeId,
          role,
          position,
        });
        if (!data.ok) throw new Error(data.message || "Не удалось изменить роль.");
        replaceAdminDashboard(data, data.message || "Роль пользователя изменена.");
      } catch (error) {
        showToast("Ошибка", error.message || "Не удалось изменить роль.");
        mainButton.disabled = false;
      }
    }

    async function adminApproveEmployee(employeeId) {
      const actionKey = `approve-employee-${employeeId}`;
      if (!beginAction(actionKey)) return;
      const select = document.getElementById(`employeePosition${employeeId}`);
      const position = select ? select.value : "";
      if (!position) {
        showToast("Должность", "Сначала выберите должность сотрудника.");
        select?.focus();
        endAction(actionKey);
        return;
      }
      mainButton.disabled = true;

      try {
        const positionResult = await api("/api/admin/employee/position", {
          employee_id: employeeId,
          position,
        });
        if (!positionResult.ok) throw new Error(positionResult.message || "Не удалось назначить должность.");
        const statusResult = await api("/api/admin/employee/status", {
          employee_id: employeeId,
          status: "active",
        });
        if (!statusResult.ok) throw new Error(statusResult.message || "Не удалось активировать сотрудника.");
        replaceAdminDashboard(statusResult, "Сотрудник активирован.");
      } catch (error) {
        showToast("Ошибка", error.message || "Не удалось активировать сотрудника.");
        mainButton.disabled = false;
      } finally {
        endAction(actionKey);
      }
    }

    async function adminCloseShift(shiftId) {
      const endTime = document.getElementById("adminShiftEndTime");
      state.adminShiftEndTime = endTime ? endTime.value : state.adminShiftEndTime;
      mainButton.disabled = true;

      try {
        const data = await api("/api/admin/shift/close", {
          shift_id: shiftId,
          end_time: state.adminShiftEndTime,
        });
        replaceAdminDashboard(data, "Смена закрыта.");
      } catch (error) {
        showToast("Ошибка", "Не удалось закрыть смену.");
        mainButton.disabled = false;
      }
    }

    async function adminDeleteShift(shiftId) {
      if (!window.confirm("Удалить смену?")) return;
      mainButton.disabled = true;

      try {
        const data = await api("/api/admin/shift/delete", { shift_id: shiftId });
        replaceAdminDashboard(data, "Смена удалена.");
      } catch (error) {
        showToast("Ошибка", "Не удалось удалить смену.");
        mainButton.disabled = false;
      }
    }

    async function adminDeleteEmployee(employeeId, employeeName) {
      const name = String(employeeName || "этого сотрудника").trim();
      const message = `Удалить ${name} из базы и закрыть ему доступ к приложению?\n\nУдаление доступно только если у сотрудника нет смен, операций и производственных записей. Для сохранения истории такого сотрудника нужно отключить.`;
      if (!window.confirm(message)) return;
      mainButton.disabled = true;

      try {
        const data = await api("/api/admin/employee/delete", { employee_id: employeeId });
        if (!data.ok) throw new Error(data.message || "Не удалось удалить сотрудника.");
        replaceAdminDashboard(data, "Сотрудник удалён.");
      } catch (error) {
        showToast("Удаление", error.message || "Не удалось удалить сотрудника.");
        mainButton.disabled = false;
      }
    }

    async function loadAdminFeedback() {
      ensureAdminDefaults();
      syncAdminForm();
      mainButton.disabled = true;

      try {
        const data = await api("/api/admin/feedback", {
          start_date: state.adminStartDate,
          end_date: state.adminEndDate,
        });
        if (!data.ok) {
          showToast("Связь", data.message || "Не удалось загрузить сообщения.");
          mainButton.disabled = false;
          return;
        }
        state.data.admin = {
          ...state.data.admin,
          feedback: data.feedback || [],
        };
        render();
        showToast("Связь", "Сообщения обновлены.");
      } catch (error) {
        showToast("Ошибка", "Не удалось загрузить сообщения.");
        mainButton.disabled = false;
      }
    }

    async function loadAdminReport() {
      if (!state.data || !state.data.is_admin) return;
      syncAdminForm();
      mainButton.disabled = true;

      try {
        const data = await api("/api/admin/report", getAdminReportPayload());
        if (!data.ok) {
          showToast("Отчёт", data.message || "Не удалось загрузить отчёт.");
          mainButton.disabled = false;
          return;
        }
        state.data.admin = {
          ...state.data.admin,
          reports: data.report,
        };
        state.adminAppliedReportPayload = {...getAdminReportPayload()};
        render();
        showToast("Отчёт", "Данные обновлены.");
      } catch (error) {
        showToast("Ошибка", "Не удалось загрузить отчёт.");
        mainButton.disabled = false;
      }
    }

    async function exportAdminReport() {
      if (!state.data || !state.data.is_admin) return;
      const actionKey = "export-admin-report";
      if (!beginAction(actionKey)) return;
      mainButton.disabled = true;

      try {
        const exportHeaders = {"Content-Type": "application/json"};
        if (isStandaloneWeb && webCsrfToken) exportHeaders["X-CSRF-Token"] = webCsrfToken;
        const response = await fetch("/api/admin/report/export", {
          method: "POST",
          headers: exportHeaders,
          credentials: "same-origin",
          body: JSON.stringify({
            ...(state.adminAppliedReportPayload || getAdminReportPayload()),
            telegram_id: debugTelegramId,
          }),
        });

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          showToast("Выгрузка", errorData.message || "Не удалось выгрузить отчёт.");
          mainButton.disabled = false;
          return;
        }

        const blob = await response.blob();
        const disposition = response.headers.get("Content-Disposition") || "";
        const match = disposition.match(/filename\\*=UTF-8''([^;]+)/);
        const filename = match ? decodeURIComponent(match[1]) : "report.xlsx";
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.setTimeout(() => URL.revokeObjectURL(url), 60000);
        showToast("Выгрузка", "Файл отчёта сформирован.");
      } catch (error) {
        showToast("Ошибка", "Не удалось выгрузить отчёт.");
      } finally {
        endAction(actionKey);
        mainButton.disabled = false;
      }
    }

    function renderEmployeeHomeDetail(view, context) {
      const titles = {
        report: ["Отчёт смены", "Операции, внесённые в текущую смену."],
        tasks: ["Мои задания", "Производственные задания, которые сейчас в работе."],
        contours: ["Задания раскроя", "Доступные и взятые этапы нанесения контуров."],
        fabric: ["Ткань в заданиях", "Рулоны ткани, закреплённые за доступными заданиями."],
      };
      const [title, description] = titles[view] || titles.report;
      let rows = "";
      let count = 0;

      if (view === "report") {
        count = context.operations.length;
        rows = context.operations.length ? context.operations.map((operation) => `
          <button type="button" class="card report-row employee-detail-row" data-go="report" data-report-target="work">
            <div><b>${escapeHtml(operation.operation_name)}</b><span>${escapeHtml(operation.product_size || "-")} · ${escapeHtml(operation.product_color || "-")}</span></div>
            <span class="status-chip">${escapeHtml(operation.quantity || 0)} ${escapeHtml(operation.unit || "шт")}</span>
          </button>
        `).join("") : itemEmpty("В текущей смене пока нет операций.");
      } else if (view === "tasks") {
        const taskRows = [
          ...context.cuttingTasks.map((task) => ({
            title: task.stage_title || "Этап раскроя",
            detail: `${task.product_name || "Изделие"} · ${(task.sizes || []).join(", ") || task.sizes_text || "размер не указан"}`,
            status: task.status_text || task.status || "В работе",
          })),
          ...context.routeTasks.map((task) => ({
            title: task.operation || "Производственное задание",
            detail: `${task.product_name || "Изделие"} · ${task.product_size || "-"} · ${task.product_color || "-"}`,
            status: task.status_text || "В работе",
          })),
        ];
        count = taskRows.length;
        rows = taskRows.length ? taskRows.map((task) => `
          <button type="button" class="card report-row employee-detail-row" data-go="report" data-report-target="work">
            <div><b>${escapeHtml(task.title)}</b><span>${escapeHtml(task.detail)}</span></div>
            <span class="status-chip warn">${escapeHtml(task.status)} ›</span>
          </button>
        `).join("") : itemEmpty("У вас пока нет заданий в работе.");
      } else if (view === "contours") {
        count = context.contourTasks.length;
        rows = context.contourTasks.length ? context.contourTasks.map((task) => `
          <button type="button" class="card report-row employee-detail-row" data-go="orders">
            <div><b>${escapeHtml(task.product_name || task.stage_title || "Нанесение контуров")}</b><span>${escapeHtml((task.sizes || []).join(", ") || task.sizes_text || "Размеры не указаны")} · ${escapeHtml((task.color_labels || task.colors || []).join(", ") || task.colors_text || "цвета не указаны")}</span></div>
            <span class="status-chip ${task.is_assigned_to_me ? "warn" : "gray"}">${escapeHtml(task.status_text || (task.is_assigned_to_me ? "В работе" : "Свободно"))} ›</span>
          </button>
        `).join("") : itemEmpty("Заданий на нанесение контуров сейчас нет.");
      } else {
        count = context.fabricRows.length;
        rows = context.fabricRows.length ? context.fabricRows.map((row) => `
          <div class="card report-row">
            <div><b>${escapeHtml(row.product_name)}</b><span>${escapeHtml(row.material_name || "Ткань")} · ${escapeHtml(row.product_color_label || row.product_color || "Цвет не указан")}</span></div>
            <span class="status-chip gray">${escapeHtml(row.rolls || 0)} рул.</span>
          </div>
        `).join("") : itemEmpty("В доступных заданиях ткань пока не закреплена.");
      }

      mainButton.textContent = "Обновить данные";
      mainButton.disabled = false;
      mount.innerHTML = `
        <div class="screen-head employee-detail-head">
          <button type="button" class="employee-detail-back" data-employee-home-back aria-label="Вернуться на главную">‹</button>
          <div class="employee-detail-title"><h2>${escapeHtml(title)}</h2><p>${escapeHtml(description)}</p></div>
          <div class="date">${count}</div>
        </div>
        <div class="op-list">${rows}</div>
      `;
    }

    function renderShift() {
      if (state.data && state.data.is_admin) {
        renderAdminHome();
        return;
      }

      const employee = state.data && state.data.employee;
      const shift = state.data && state.data.shift;
      const operations = getReportOperations();
      const routeTasks = getMyRouteTasks();
      const cuttingTasks = getMyCuttingTasks();
      const contourTasks = getEmployeeContourTasks();
      const fabricRows = getEmployeeFabricRows();
      const activeTasks = routeTasks.length + cuttingTasks.length;
      const hasOpen = state.data && state.data.has_open_shift;

      if (state.employeeHomeView && state.employeeHomeView !== "overview") {
        renderEmployeeHomeDetail(state.employeeHomeView, {operations, routeTasks, cuttingTasks, contourTasks, fabricRows});
        return;
      }

      mainButton.textContent = hasOpen ? "Закрыть смену" : "Открыть смену";
      mainButton.disabled = Boolean(shift && shift.status === "closed");

      mount.innerHTML = `
        <div class="screen-head"><div><h2>Сегодня</h2><p>${escapeHtml(employee ? employee.full_name : "Пользователь не определён")}</p></div><div class="date">${escapeHtml(shift ? shift.date : "сегодня")}</div></div>
        <div class="card shift-card"><div><b>${escapeHtml(shiftText())}</b><span>${escapeHtml(employee ? employee.position : "-")} · профиль ${escapeHtml(employee ? employee.status : "-")}<br>${escapeHtml(shift ? `${shift.start_time || "-"}-${shift.end_time || ""}` : "Начните смену, чтобы вести отчёт")}</span></div><span class="status-chip ${hasOpen ? "" : "gray"}">● ${hasOpen ? "в процессе" : "ожидает"}</span></div>
        <div class="kpi-grid">
          <button type="button" class="card kpi home-kpi" data-employee-home-detail="report"><div class="kpi-top"><span>Отчёт</span><div class="kpi-ico">${sewingIcon()}</div></div><strong>${operations.length}<small> строк</small></strong><span>Открыть операции ›</span><div class="progress"><i style="--w:${Math.min(100, operations.length * 12)}%"></i></div></button>
          <button type="button" class="card kpi good home-kpi" data-employee-home-detail="tasks"><div class="kpi-top"><span>Задания</span><div class="kpi-ico">${uiIcon("clipboard")}</div></div><strong>${activeTasks}<small> акт.</small></strong><span>Открыть задания ›</span><div class="progress sage"><i style="--w:${Math.min(100, activeTasks * 18)}%"></i></div></button>
          <button type="button" class="card kpi home-kpi" data-employee-home-detail="contours"><div class="kpi-top"><span>Контуры</span><div class="kpi-ico">${uiIcon("contour")}</div></div><strong>${contourTasks.length}<small> шт</small></strong><span>Посмотреть список ›</span></button>
          <button type="button" class="card kpi home-kpi" data-employee-home-detail="fabric"><div class="kpi-top"><span>Ткань</span><div class="kpi-ico">${uiIcon("fabric")}</div></div><strong>${fabricRows.length}<small> поз.</small></strong><span>Ткань в заданиях ›</span></button>
        </div>
        <div class="section-title"><b>Активная операция</b><button data-go="report">отчёт</button></div>
        ${operations.length ? `
          <div class="card active-operation" data-go="report"><div class="op-icon">${sewingIcon()}</div><div><b>${escapeHtml(operations[0].operation_name)}</b><span>${escapeHtml(operations[0].product_size || "-")} · ${escapeHtml(operations[0].product_color || "-")}<br>${escapeHtml(operations[0].quantity)} ${escapeHtml(operations[0].unit)}</span></div><span class="status-chip">отчёт</span></div>
        ` : `<div class="card shift-card"><div><b>Операций пока нет</b><span>Когда появятся строки отчёта, они будут здесь.</span></div><span class="status-chip gray">пусто</span></div>`}
      `;
    }

    function renderOperations() {
      const operations = getReportOperations();
      const selected = operations[state.selectedOperation] || operations[0];
      mainButton.textContent = selected ? "Открыть отчёт" : "Обновить";
      mainButton.disabled = false;

      mount.innerHTML = `
        <div class="screen-head"><div><h2>Операции смены</h2><p>Строки текущего отчёта сотрудника.</p></div><div class="date">${operations.length} строк</div></div>
        <div class="op-list">
          ${operations.length ? operations.map((op, index) => `
            <div class="card op-row ${index === state.selectedOperation ? "selected" : ""}" data-select-operation="${index}">
              <div class="op-icon">${sewingIcon()}</div>
              <div class="op-meta"><b>${escapeHtml(op.operation_name)}</b><span>${escapeHtml(op.product_size || "-")} · ${escapeHtml(op.product_color || "-")}<br>${escapeHtml(op.quantity)} ${escapeHtml(op.unit)}</span><div class="progress ${Number(op.quantity || 0) > 0 ? "sage" : ""}"><i style="--w:${Math.min(100, Number(op.quantity || 0))}%"></i></div></div>
              <div class="op-num"><strong>${escapeHtml(op.quantity)}</strong>${escapeHtml(op.unit)}</div>
            </div>
          `).join("") : itemEmpty("Операций за текущую смену пока нет.")}
        </div>
      `;
    }

    function renderTaskCompletionForm(task) {
      if (!task) return "";
      const draft = state.taskCompletionDrafts[task.id] || {};
      if (!draft.request_id) draft.request_id = createRequestId();
      state.taskCompletionDrafts[task.id] = draft;
      const quality = state.data && state.data.quality ? state.data.quality : {defect_reasons: [], defect_dispositions: []};
      const defectVisible = Number(draft.defect || 0) > 0;
      const photo = state.taskDefectPhotos[task.id];
      const paused = task.work_state === "paused";
      const blocked = task.work_state === "blocked";
      const packingOptions = task.packing_options || [];
      if (packingOptions.length && !draft.packaging_option) draft.packaging_option = "individual";

      return `
        <div class="card task-completion-card">
          <div class="task-completion-head"><b>${escapeHtml(task.operation)}</b><span class="status-chip ${task.work_state === "in_work" ? "" : "warn"}">${escapeHtml(task.status_text || "В работе")}</span></div>
          ${renderRouteTaskInputs(task)}
          ${(paused || blocked) ? `<div class="task-note">${escapeHtml(task.blocked_reason || (paused ? "Работа приостановлена" : "Задание заблокировано"))}</div>` : ""}
          <div class="form-grid" style="margin-top:11px">
            ${packingOptions.length ? `<div class="field full"><label>Вариант упаковки</label><select id="taskPackagingOption">${packingOptions.map((option) => `<option value="${escapeHtml(option.id)}" ${draft.packaging_option === option.id ? "selected" : ""}>${escapeHtml(option.label)}</option>`).join("")}</select><div class="task-note">Для наборов приложение пересчитает готовые комплекты и спишет второй товар со склада, если он входит в комплект.</div></div>` : ""}
            <div class="field"><label>Годная продукция</label><input id="taskGoodQuantity" inputmode="numeric" type="number" min="0" max="${escapeHtml(task.quantity)}" step="1" value="${escapeHtml(draft.good ?? task.quantity)}"></div>
            <div class="field"><label>Брак</label><input id="taskDefectQuantity" inputmode="numeric" type="number" min="0" max="${escapeHtml(task.quantity)}" step="1" value="${escapeHtml(draft.defect ?? 0)}"></div>
            <div class="field full"><button type="button" class="small-button secondary" data-task-action="all-good" data-task-id="${escapeHtml(task.id)}">Всё годное: ${escapeHtml(task.quantity)} шт</button></div>
            <div class="field full" id="taskDefectDetails" style="display:${defectVisible ? "block" : "none"}">
              <div class="form-grid">
                <div class="field full"><label>Причина брака</label><select id="taskDefectReason"><option value="">Выберите причину</option>${(quality.defect_reasons || []).map((reason) => `<option value="${escapeHtml(reason)}" ${draft.defect_reason === reason ? "selected" : ""}>${escapeHtml(reason)}</option>`).join("")}</select></div>
                <div class="field full"><label>Решение</label><select id="taskDefectDisposition"><option value="">Выберите решение</option>${(quality.defect_dispositions || []).map((disposition) => `<option value="${escapeHtml(disposition)}" ${draft.defect_disposition === disposition ? "selected" : ""}>${escapeHtml(disposition)}</option>`).join("")}</select></div>
                <div class="field full"><label>Комментарий</label><textarea id="taskDefectComment" placeholder="Что произошло">${escapeHtml(draft.defect_comment || "")}</textarea></div>
                <div class="field full"><label>Фото брака</label><input id="taskDefectPhoto" type="file" accept="image/jpeg,image/png,image/webp"><div class="task-note">${escapeHtml(photo ? photo.file_name : "Фото не выбрано")}</div></div>
              </div>
            </div>
          </div>
          <div class="task-action-grid">
            ${(paused || blocked) ? `<button type="button" class="small-button" data-task-action="resume" data-task-id="${escapeHtml(task.id)}">Продолжить</button>` : `<button type="button" class="small-button secondary" data-task-action="pause" data-task-id="${escapeHtml(task.id)}">Пауза</button>`}
            ${!blocked ? `<button type="button" class="small-button secondary" data-task-action="block" data-task-id="${escapeHtml(task.id)}">Есть проблема</button>` : ""}
            <button type="button" class="small-button secondary" data-task-action="release" data-task-id="${escapeHtml(task.id)}">Передать</button>
            <button type="button" class="small-button secondary" data-task-action="passport" data-task-id="${escapeHtml(task.id)}">Паспорт / QR</button>
          </div>
          <div class="button-row"><button type="button" class="small-button" data-report-action="complete-task" ${task.can_complete ? "" : "disabled"}>Выполнить задание</button></div>
        </div>
      `;
    }

    function renderReport() {
      const feedback = getFeedbackRows();
      const history = getHistory();
      const workTasks = getMyRouteTasks();
      const cuttingWorkTasks = getMyCuttingTasks();
      const doneTasks = getCompletedRouteTasks();
      ensureUserDefaults();
      if (!["work", "done", "feedback"].includes(state.reportSection)) state.reportSection = "work";

      state.selectedReportTask = selectedTaskIndex(workTasks, state.selectedReportTaskKey, state.selectedReportTask);
      state.selectedCuttingReportTask = selectedTaskIndex(cuttingWorkTasks, state.selectedCuttingReportTaskKey, state.selectedCuttingReportTask);

      const selectedTask = workTasks[state.selectedReportTask] || workTasks[0];
      const selectedCuttingTask = cuttingWorkTasks[state.selectedCuttingReportTask] || cuttingWorkTasks[0];
      state.selectedReportTaskKey = taskIdentity(selectedTask);
      state.selectedCuttingReportTaskKey = taskIdentity(selectedCuttingTask);
      mainButton.textContent = state.reportSection === "work" && (selectedCuttingTask || selectedTask)
        ? (selectedCuttingTask ? "Выполнить этап" : (selectedTask.can_complete ? "Выполнить задание" : "Продолжить задание"))
        : "Обновить отчёт";
      mainButton.disabled = false;

      const historySummary = history && history.summary ? history.summary : null;
      const historyShifts = history && history.shifts ? history.shifts : [];
      const historyOperations = history && history.operations ? history.operations : [];

      if (state.reportSection === "work") {
        if (cuttingWorkTasks.length) {
          mount.innerHTML = `
            <div class="screen-head"><div><h2>В работе</h2><p>Этапы раскроя по выбранным заданиям.</p></div><div class="date">${cuttingWorkTasks.length} акт.</div></div>
            <div class="op-list">
              ${cuttingWorkTasks.map((task, index) => `
                <div class="card order-card ${index === state.selectedCuttingReportTask ? "selected" : ""}" data-select-cutting-report-task="${index}">
                  <div class="order-head"><div class="op-icon">${uiIcon("work")}</div><div><b>${escapeHtml(task.stage_title)}</b><span>${escapeHtml(task.product_name)}</span></div><span class="status-chip">${escapeHtml(task.status_text || task.status)}</span></div>
                  <div class="progress"><i style="--w:${progressForTask(task)}%"></i></div>
                  <div class="order-foot"><span>${escapeHtml((task.sizes || []).join(", ") || task.colors_text || task.sizes_text || "-")}</span><span>${escapeHtml(task.next_action || "этап")}</span></div>
                </div>
              `).join("")}
            </div>
            ${selectedCuttingTask ? `
              <div class="section-title"><b>Выполнение этапа</b><span>${escapeHtml(selectedCuttingTask.next_action || "")}</span></div>
              ${renderCuttingStageDetail(selectedCuttingTask)}
              <div class="button-row"><button class="small-button" data-report-action="complete-cutting-stage">Выполнить этап</button></div>
            ` : ""}
          `;
          return;
        }

        mount.innerHTML = `
          <div class="screen-head"><div><h2>В работе</h2><p>Задания, которые вы взяли в работу.</p></div><div class="date">${workTasks.length} акт.</div></div>
          <div class="op-list">
            ${workTasks.length ? workTasks.map((task, index) => routeTaskCard(task, index, {selectedIndex: state.selectedReportTask, selectAttr: "data-select-report-task"})).join("") : itemEmpty("В работе пока нет заданий. Возьмите свободное задание во вкладке «Задания».")}
          </div>
          ${selectedTask ? `
            <div class="section-title"><b>Сдача задания</b><span>${escapeHtml(selectedTask.quantity)} шт</span></div>
            ${renderTaskCompletionForm(selectedTask)}
          ` : ""}
        `;
        return;
      }

      if (state.reportSection === "done") {
        mainButton.textContent = "Обновить завершённые";
        mount.innerHTML = `
          <div class="screen-head"><div><h2>Завершено</h2><p>Ваши выполненные задания.</p></div><div class="date">${doneTasks.length} шт</div></div>
          <div class="op-list">
            ${doneTasks.length ? doneTasks.map((task, index) => `
              <div class="card order-card">
                <div class="order-head route-order-head"><div class="op-icon">${uiIcon("quality")}</div><div><b>${escapeHtml(task.operation)}</b><span>${escapeHtml(task.product_name)}</span></div><span class="status-chip">Завершено</span></div>
                <div class="order-foot"><strong>${escapeHtml(task.product_size)} · ${escapeHtml(task.product_color)}</strong><strong>${escapeHtml(task.good_quantity || 0)} годн. · ${escapeHtml(task.defect_quantity || 0)} брак</strong></div>
                ${(task.defects || []).length ? `<div class="route-inputs">${task.defects.map((defect) => `<div class="route-input-row"><span>${escapeHtml(defect.reason)} · ${escapeHtml(defect.disposition)}${defect.has_photo ? `<br><a href="${escapeHtml(defectPhotoUrl(defect.id))}" target="_blank" rel="noopener">Открыть фото</a>` : ""}</span><span>${defect.rework_batch_id ? `переделка #${escapeHtml(defect.rework_batch_id)}` : `${escapeHtml(defect.quantity)} шт`}</span></div>`).join("")}</div>` : ""}
                <div class="button-row"><button type="button" class="small-button secondary" data-task-action="passport" data-task-id="${escapeHtml(task.id)}">Паспорт / QR</button></div>
              </div>
            `).join("") : itemEmpty("Завершённых заданий пока нет.")}
          </div>
        `;
        return;
      }

      mainButton.textContent = "Обновить связь";
      mount.innerHTML = `
        <div class="screen-head"><div><h2>Обратная связь</h2><p>Сообщение администратору и история смен.</p></div><div class="date">${feedback.length} сообщ.</div></div>
        <div class="section-title"><b>Обратная связь</b><span>${feedback.length}</span></div>
        <div class="op-list">
          ${feedback.length ? feedback.map((row) => `
            <div class="card field-card"><label>${escapeHtml(row.category)} · ${escapeHtml(row.date)}</label><div class="textarea">${escapeHtml(row.message)}</div></div>
          `).join("") : `<div class="card field-card">${itemEmpty("Сообщений за смену нет.")}</div>`}
        </div>
        <div class="card field-card">
          <label>Написать администратору</label>
          <div class="form-grid">
            <div class="field full"><label>Раздел</label><select id="feedbackCategory"><option value="Производство" ${state.feedbackDraft.category === "Производство" ? "selected" : ""}>Производство</option><option value="Бытовое" ${state.feedbackDraft.category === "Бытовое" ? "selected" : ""}>Бытовое</option></select></div>
            <div class="field full"><label>Сообщение</label><textarea id="feedbackMessage" placeholder="Напишите сообщение">${escapeHtml(state.feedbackDraft.message || "")}</textarea></div>
          </div>
          <div class="button-row"><button class="small-button secondary" data-history-action="load">Обновить историю</button><button class="small-button" data-feedback-action="send">Отправить</button></div>
        </div>
        <div class="section-title"><b>Моя история</b><button data-history-action="load">показать</button></div>
        <div class="card field-card">
          <div class="form-grid">
            <div class="field"><label>Начало</label><input id="userStartDate" type="date" value="${escapeHtml(state.userStartDate)}"></div>
            <div class="field"><label>Окончание</label><input id="userEndDate" type="date" value="${escapeHtml(state.userEndDate)}"></div>
          </div>
          <div class="button-row"><button class="small-button secondary" data-history-action="load">Показать</button></div>
        </div>
        <div class="kpi-grid">
          <div class="card kpi"><div class="kpi-top"><span>Смены</span><div class="kpi-ico">${uiIcon("clock")}</div></div><strong>${historySummary ? historySummary.shift_count : 0}<small> шт</small></strong><span>За выбранный период</span></div>
          <div class="card kpi good"><div class="kpi-top"><span>Часы</span><div class="kpi-ico">${uiIcon("schedule")}</div></div><strong>${escapeHtml(historySummary ? historySummary.total_time : "0:00")}</strong><span>Отработано суммарно</span></div>
        </div>
        <div class="section-title"><b>Смены за период</b><span>${historyShifts.length}</span></div>
        <div class="op-list">
          ${historyShifts.length ? historyShifts.slice(0, 8).map((shift) => `
            <div class="card report-row"><div><b>${escapeHtml(shift.date)}</b><span>${escapeHtml(shift.start_time || "-")} — ${escapeHtml(shift.end_time || "-")} · ${escapeHtml(shift.status)}</span></div><span class="status-chip gray">${escapeHtml(shift.total_time || "-")}</span></div>
          `).join("") : itemEmpty("За выбранный период смен пока нет.")}
        </div>
        <div class="section-title"><b>Операции за период</b><span>${historyOperations.length}</span></div>
        <div class="op-list">
          ${historyOperations.length ? historyOperations.slice(0, 10).map((operation) => `
            <div class="card report-row"><div><b>${escapeHtml(operation.operation)}</b><span>Итого по операции</span></div><span class="status-chip">${escapeHtml(operation.quantity)} ${escapeHtml(operation.unit)}</span></div>
          `).join("") : itemEmpty("Операций за выбранный период пока нет.")}
        </div>
      `;
    }

    function resetOrderDraft() {
      const firstProduct = getRouteCatalog()[0];
      state.orderMode = "create";
      state.orderProduct = firstProduct ? firstProduct.product_name : "";
      state.orderProducts = firstProduct ? [firstProduct.product_name] : [];
      state.orderTaskType = "cutting";
      state.orderMaterial = "Ткань";
      state.orderSizes = [];
      state.orderColors = [];
      state.orderQuantity = "1";
      state.orderPriority = "normal";
      state.orderDueDate = "";
      state.orderFabricRolls = {};
      state.orderAttachment = null;
    }

    function ensureOrderDraftDefaults() {
      const catalog = getRouteCatalog();
      if (!catalog.length) return null;

      state.orderProducts = state.orderProducts.filter((name) => catalog.some((item) => item.product_name === name));
      if (!state.orderProducts.length) state.orderProducts = [state.orderProduct || catalog[0].product_name];
      state.orderProducts = state.orderProducts.filter((name) => catalog.some((item) => item.product_name === name));
      if (!state.orderProducts.length) state.orderProducts = [catalog[0].product_name];
      state.orderProduct = state.orderProducts[0];
      const selectedProducts = state.orderProducts.map((name) => routeProduct(name)).filter(Boolean);
      const product = selectedProducts[0] || catalog[0];

      const availableSizes = selectedProducts.slice(1).reduce(
        (common, selected) => common.filter((size) => (selected.sizes || []).includes(size)),
        [...(selectedProducts[0] ? selectedProducts[0].sizes || [] : product.sizes || [])],
      );
      const availableColors = selectedProducts.length > 1 ? selectedProducts.slice(1).reduce(
        (common, selected) => common.filter((color) => (selected.raw_colors || []).includes(color)),
        [...(selectedProducts[0] && selectedProducts[0].raw_colors && selectedProducts[0].raw_colors.length ? selectedProducts[0].raw_colors : getOrderColors())],
      ) : getOrderColors();
      state.orderAvailableSizes = availableSizes.map((size) => String(size));
      state.orderSizes = state.orderSizes.filter((size) => availableSizes.includes(size));
      state.orderColors = state.orderColors.filter((color) => availableColors.includes(color));
      Object.keys(state.orderFabricRolls).forEach((color) => {
        if (!state.orderColors.includes(color)) delete state.orderFabricRolls[color];
      });

      return product;
    }

    function syncOrderDraft() {
      const product = document.getElementById("orderProduct");
      const material = document.getElementById("orderMaterial");
      const quantity = document.getElementById("orderQuantity");
      const priority = document.getElementById("orderPriority");
      const dueDate = document.getElementById("orderDueDate");
      const fabricRollInputs = document.querySelectorAll("[data-fabric-rolls]");
      const previousProduct = state.orderProduct;

      if (product) state.orderProduct = product.value;
      if (material) state.orderMaterial = material.value;
      if (quantity) state.orderQuantity = quantity.value;
      if (priority) state.orderPriority = priority.value;
      if (dueDate) state.orderDueDate = dueDate.value;
      fabricRollInputs.forEach((input) => {
        state.orderFabricRolls[input.dataset.fabricRolls] = input.value;
      });

      if (previousProduct && previousProduct !== state.orderProduct) {
        state.orderSizes = [];
        state.orderColors = [];
        state.orderFabricRolls = {};
      }

      ensureOrderDraftDefaults();
    }

    function toggleOrderValue(kind, value) {
      const key = kind === "size" ? "orderSizes" : (kind === "color" ? "orderColors" : "orderProducts");
      const values = state[key];
      const isSelected = values.includes(value);
      if (kind === "product" && isSelected && values.length === 1) {
        showToast("Изделия", "Оставьте хотя бы одно изделие в настиле.");
        return;
      }
      const normalizedValue = String(value);
      state[key] = isSelected
        ? values.filter((item) => String(item) !== normalizedValue)
        : [...values, normalizedValue];

      if (kind === "product") {
        state.orderProduct = state.orderProducts[0] || "";
        state.orderSizes = [];
        state.orderColors = [];
        state.orderFabricRolls = {};
        ensureOrderDraftDefaults();
      }

      if (kind === "color") {
        if (isSelected) {
          delete state.orderFabricRolls[value];
        } else if (!state.orderFabricRolls[value]) {
          state.orderFabricRolls[value] = "1";
        }
      }

      render();
    }

    function renderChoiceChips(kind, values, selectedValues) {
      return `<div class="choice-grid">${values.map((value) => `
        <button type="button" class="choice-chip ${selectedValues.includes(value) ? "active" : ""}" data-order-${kind}="${escapeHtml(value)}">${escapeHtml(value)}</button>
      `).join("")}</div>`;
    }

    function stockQuantity(row) {
      const current = Number(state.orderStockQuantities[row.id] || 0);
      const max = Number(row.quantity || 0);
      if (!Number.isFinite(current) || current <= 0) return 0;
      if (!Number.isFinite(max) || max <= 0) return current;
      return Math.min(current, max);
    }

    function renderStockPicker(stockRows, selectedOperation) {
      const selectedRows = stockRows.filter((row) => stockQuantity(row) > 0);
      const selectedTotal = selectedRows.reduce((total, row) => total + stockQuantity(row), 0);
      const acceptedStages = selectedOperation ? selectedOperation.accepted_stock_stages || [] : [];
      const renderStockRow = (row) => {
        const quantity = stockQuantity(row);
        const isSelected = quantity > 0;

        return `
          <div class="stock-pick-row ${isSelected ? "active" : ""}">
            <input data-stock-toggle="${escapeHtml(row.id)}" type="checkbox" ${isSelected ? "checked" : ""} aria-label="Выбрать полуфабрикат">
            <div class="stock-pick-main">
              <b>${escapeHtml(row.product_name)} — ${escapeHtml(row.stage_name || "После раскроя")}</b>
              <span>${escapeHtml(row.product_size)} · ${escapeHtml(row.product_color_label || row.product_color)}<br>Для: ${escapeHtml(row.ready_for_position)} · доступно ${escapeHtml(row.quantity_text || row.quantity)} ${escapeHtml(row.unit || "шт")}</span>
            </div>
            <div class="stock-pick-qty">
              <input data-stock-quantity="${escapeHtml(row.id)}" type="number" min="0" max="${escapeHtml(row.quantity)}" step="1" value="${escapeHtml(quantity || "")}" placeholder="0">
            </div>
          </div>
        `;
      };
      const stockHtml = acceptedStages.length ? acceptedStages.map((stage) => {
        const stageRows = stockRows.filter((row) => row.stage_name === stage);
        const selectedStageRows = stageRows.filter((row) => stockQuantity(row) > 0);

        return `
          <div class="stock-component-group">
            <div class="stock-component-title"><b>${escapeHtml(stage)}</b><span>${selectedStageRows.length ? `выбрано ${selectedStageRows.length}` : "обязательно"}</span></div>
            ${stageRows.length ? stageRows.map(renderStockRow).join("") : itemEmpty(`Нет доступного компонента: ${stage}.`)}
          </div>
        `;
      }).join("") : itemEmpty(`На складе нет подходящих полуфабрикатов${selectedOperation ? ` для ${selectedOperation.position}` : ""}.`);

      return `
        <div class="card field-card">
          <label>Вход</label>
          <div class="stock-picker">
            <div class="stock-picker-head"><span>Компоненты операции</span><span>${selectedRows.length} поз. · ${selectedTotal} шт</span></div>
            ${stockRows.length ? `<div class="stock-picker-actions"><button class="small-button secondary" data-stock-action="clear">Очистить</button><button class="small-button" data-stock-action="all">Взять всё</button></div>` : ""}
            ${stockHtml}
          </div>
        </div>
      `;
    }

    async function createOrderTask() {
      if (!state.data || !state.data.is_admin) return;
      const actionKey = "create-order-task";
      if (!beginAction(actionKey)) return;
      syncOrderDraft();
      mainButton.disabled = true;
      try {
        const data = await api("/api/production/create-order-task", {
          product_name: state.orderProduct,
          product_names: state.orderProducts,
          task_type: "cutting",
          material_name: state.orderMaterial,
          sizes: state.orderSizes,
          colors: state.orderColors,
          quantity: state.orderQuantity,
          priority: state.orderPriority,
          due_date: state.orderDueDate,
          fabric_rolls: state.orderFabricRolls,
          attachment: state.orderAttachment,
        });

        if (!data.ok) {
          showToast("Задание", data.message || "Не удалось создать задание.");
          mainButton.disabled = false;
          return;
        }

        state.data.production = data.production || state.data.production;
        if (data.routes) state.data.routes = data.routes;
        state.orderMode = "list";
        state.selectedOrderKey = "";
        render();
        showToast("Задание", data.message || "Задание создано.");
      } catch (error) {
        showToast("Ошибка", "Не удалось создать задание.");
        mainButton.disabled = false;
      } finally {
        endAction(actionKey);
      }
    }

    function readOrderAttachment(file) {
      if (!file) {
        state.orderAttachment = null;
        render();
        return;
      }

      const allowed = [".pdf", ".doc", ".docx", ".xls", ".xlsx"];
      const lowerName = file.name.toLowerCase();

      if (!allowed.some((extension) => lowerName.endsWith(extension))) {
        state.orderAttachment = null;
        showToast("Файл", "Можно прикрепить только Word, Excel или PDF.");
        render();
        return;
      }

      const reader = new FileReader();
      reader.onload = () => {
        const dataUrl = String(reader.result || "");
        state.orderAttachment = {
          file_name: file.name,
          mime_type: file.type || "application/octet-stream",
          content_base64: dataUrl.includes(",") ? dataUrl.split(",").pop() : dataUrl,
        };
        render();
        showToast("Файл", "Файл прикреплён к заданию.");
      };
      reader.onerror = () => showToast("Файл", "Не удалось прочитать файл.");
      reader.readAsDataURL(file);
    }

    function syncWarehouseReceiptForm() {
      const material = document.getElementById("fabricReceiptMaterial");
      const color = document.getElementById("fabricReceiptColor");
      const quantity = document.getElementById("fabricReceiptQuantity");

      if (material) state.fabricReceiptMaterial = material.value;
      if (color) state.fabricReceiptColor = color.value;
      if (quantity) state.fabricReceiptQuantity = quantity.value;
    }

    function syncWmsMaterialReceiptForm() {
      const draft = state.wmsMaterialReceipt;
      const name = document.getElementById("wmsMaterialName");
      const color = document.getElementById("wmsMaterialColor");
      const unit = document.getElementById("wmsMaterialUnit");
      const quantity = document.getElementById("wmsMaterialQuantity");
      const comment = document.getElementById("wmsMaterialComment");
      if (name) draft.name = name.value;
      if (color) draft.color = color.value;
      if (unit) draft.unit = unit.value;
      if (quantity) draft.quantity = quantity.value;
      if (comment) draft.comment = comment.value;
    }

    function syncWarehouseFilters() {
      const product = document.getElementById("warehouseProductFilter");
      const size = document.getElementById("warehouseSizeFilter");
      const color = document.getElementById("warehouseColorFilter");

      if (product) state.warehouseProductFilter = product.value;
      if (size) state.warehouseSizeFilter = size.value;
      if (color) state.warehouseColorFilter = color.value;
    }

    function syncEmployeeFilters() {
      const position = document.getElementById("employeePositionFilter");
      const status = document.getElementById("employeeStatusFilter");
      const shift = document.getElementById("employeeShiftFilter");

      if (position) state.employeePositionFilter = position.value;
      if (status) state.employeeStatusFilter = status.value;
      if (shift) state.employeeShiftFilter = shift.value;
    }

    function resetEmployeeFilters() {
      state.employeePositionFilter = "";
      state.employeeStatusFilter = "";
      state.employeeShiftFilter = "";
    }

    function resetWarehouseFilters() {
      state.warehouseProductFilter = "";
      state.warehouseSizeFilter = "";
      state.warehouseColorFilter = "";
    }

    function cuttingDraftKey(task) {
      return task ? `${task.stage}:${task.id}` : "";
    }

    function cuttingDraft(task) {
      const key = cuttingDraftKey(task);
      return key ? (state.cuttingStageDrafts[key] || {}) : {};
    }

    function formatCuttingSizeQuantities(value) {
      return String(value || "").split(",").map((item) => {
        const parts = item.split(" - ");
        if (parts.length < 2) return item.trim();
        return `${parts[0].trim()} — ${parts.slice(1).join(" - ").trim()} шт`;
      }).filter(Boolean).join(" · ");
    }

    function formatCuttingContourMatrix(matrix, color, fallback) {
      const rows = Array.isArray(matrix)
        ? matrix.filter((row) => !color || String(row.color || "") === String(color))
        : [];
      if (rows.length) {
        return rows.map((row) => `${String(row.size || "").trim()} — ${Number(row.quantity || 0)} шт`).filter(Boolean).join(" · ");
      }
      return formatCuttingSizeQuantities(fallback || "Размеры задания");
    }

    function formatCuttingContourSummary(matrix, fallback) {
      const rows = Array.isArray(matrix) ? matrix : [];
      if (rows.length) {
        return rows.map((row) => `${String(row.size || "").trim()} · ${String(row.color || "без цвета").trim()} — ${Number(row.quantity || 0)} шт`).filter(Boolean).join(" · ");
      }
      return formatCuttingSizeQuantities(fallback || "Размеры задания");
    }

    function cuttingArbitrarySizes(current) {
      const sizes = Array.isArray(current && current.sizes) ? current.sizes : [];
      if (sizes.length) return sizes;
      const matrix = Array.isArray(current && current.contour_matrix) ? current.contour_matrix : [];
      return [...new Set(matrix.map((row) => String(row.size || "").trim()).filter(Boolean))];
    }

    function readCuttingArbitraryRowsFromDom() {
      return [...document.querySelectorAll("[data-arbitrary-row]")].map((row) => ({
        product_size: row.querySelector("[data-arbitrary-size]")?.value || "",
        product_color: row.querySelector("[data-arbitrary-color]")?.value || "",
        parts_count: row.querySelector("[data-arbitrary-parts]")?.value || "2",
        layers: row.querySelector("[data-arbitrary-layers]")?.value || "",
      }));
    }

    function syncCuttingArbitraryDraftFromDom(current) {
      const key = cuttingDraftKey(current);
      if (!key || !current || current.stage !== "layout") return;
      const draft = state.cuttingStageDrafts[key] || {};
      draft.arbitrary_operations = readCuttingArbitraryRowsFromDom();
      state.cuttingStageDrafts[key] = draft;
    }

    async function addFabricReceipt() {
      if (!state.data || !state.data.is_admin) return;
      const actionKey = "add-fabric-receipt";
      if (!beginAction(actionKey)) return;
      syncWarehouseReceiptForm();
      mainButton.disabled = true;

      try {
        const data = await api("/api/production/fabric-receipt", {
          material_name: state.fabricReceiptMaterial || "Ткань",
          product_color: state.fabricReceiptColor,
          quantity: state.fabricReceiptQuantity,
        });

        if (!data.ok) {
          showToast("Склад", data.message || "Не удалось сохранить приход.");
          mainButton.disabled = false;
          return;
        }

        state.data.production = data.production || state.data.production;
        state.fabricReceiptQuantity = "";
        render();
        showToast("Склад", data.message || "Приход сохранён.");
      } catch (error) {
        showToast("Ошибка", "Не удалось сохранить приход.");
        mainButton.disabled = false;
      } finally {
        endAction(actionKey);
      }
    }

    async function deleteOrderTask(taskKind = "", taskId = 0) {
      if (!state.data || !state.data.is_admin) return;
      const rows = taskKind && taskId ? currentOrderRows() : visibleOrderRows();
      const current = taskKind && taskId
        ? rows.find((task) => task.task_kind === taskKind && String(task.id) === String(taskId))
        : (rows[state.selectedOrder] || rows[0]);

      if (!current) {
        showToast("Задание", "Задание не найдено. Обновите список.");
        return;
      }

      const confirmed = window.confirm(`Удалить задание #${current.id}?`);
      if (!confirmed) return;

      const actionKey = `delete-order-task:${current.task_kind}:${current.id}`;
      if (!beginAction(actionKey)) return;

      mainButton.disabled = true;

      try {
        const data = await api("/api/production/delete-order-task", {
          task_kind: current.task_kind,
          task_id: current.id,
        });

        if (!data.ok) {
          showToast("Задание", data.message || "Не удалось удалить задание.");
          mainButton.disabled = false;
          return;
        }

        state.data.production = data.production || state.data.production;
        if (data.routes) state.data.routes = data.routes;
        state.selectedOrder = 0;
        state.selectedOrderKey = "";
        if (state.screen === "analytics") {
          state.analyticsView = state.analyticsReturnView && state.analyticsReturnView !== "task" ? state.analyticsReturnView : "overview";
          state.analyticsTaskId = "";
          await refreshAdminDashboard(data.message || "Задание удалено.");
          return;
        }
        render();
        showToast("Задание", data.message || "Задание удалено.");
      } catch (error) {
        showToast("Ошибка", "Не удалось удалить задание.");
        mainButton.disabled = false;
      } finally {
        endAction(actionKey);
      }
    }

    async function adjustWarehouseStock(stockKind, stockId, currentQuantity, label) {
      if (!state.data || !state.data.is_admin) return;
      const rawQuantity = window.prompt(`Новый остаток: ${label}`, String(currentQuantity));
      if (rawQuantity === null) return;
      const normalized = String(rawQuantity).trim();
      if (!/^[0-9]+$/.test(normalized)) {
        showToast("Склад", "Введите целое количество от 0.");
        return;
      }
      const reason = window.prompt("Причина корректировки", "Инвентаризация") || "";
      if (!reason.trim()) {
        showToast("Склад", "Причина корректировки обязательна.");
        return;
      }

      const actionKey = `adjust-stock:${stockKind}:${stockId}`;
      if (!beginAction(actionKey)) return;
      mainButton.disabled = true;
      try {
        const data = await api("/api/production/adjust-stock", {
          stock_kind: stockKind,
          stock_id: stockId,
          quantity: normalized,
          reason: reason.trim(),
        });
        if (!data.ok) {
          showToast("Склад", data.message || "Не удалось скорректировать остаток.");
          mainButton.disabled = false;
          return;
        }
        state.data.production = data.production || state.data.production;
        render();
        showToast("Склад", data.message || "Остаток скорректирован.");
      } catch (error) {
        showToast("Ошибка", "Не удалось скорректировать остаток.");
        mainButton.disabled = false;
      } finally {
        endAction(actionKey);
      }
    }

    function readWmsDraftFromForm() {
      const d = state.wmsDraft;
      const valueOrDraft = (id, key, fallback = "") => {
        const element = document.getElementById(id);
        return element ? element.value : (d[key] ?? fallback);
      };
      const productName = valueOrDraft("wmsProductName", "productName");
      const productSize = valueOrDraft("wmsProductSize", "productSize");
      const productColor = valueOrDraft("wmsProductColor", "productColor");
      const itemType = valueOrDraft("wmsItemType", "itemType", "finished");
      const quantity = valueOrDraft("wmsQuantity", "quantity");
      const fromLocation = valueOrDraft("wmsFromLocation", "fromLocation");
      const toLocation = valueOrDraft("wmsToLocation", "toLocation");
      const reason = valueOrDraft("wmsReason", "reason");
      const targetState = valueOrDraft("wmsTargetState", "targetState", "SCRAPPED");
      const barcode = valueOrDraft("wmsBarcode", "barcode");
      const locationZone = valueOrDraft("wmsLocationZone", "locationZone", "STORAGE");
      const locationName = valueOrDraft("wmsLocationName", "locationName");
      d.productName = productName; d.productSize = productSize; d.productColor = productColor;
      d.itemType = itemType; d.quantity = quantity;
      d.fromLocation = fromLocation; d.toLocation = toLocation;
      d.reason = reason; d.targetState = targetState;
      d.barcode = barcode;
      d.locationZone = locationZone; d.locationName = locationName;
      return d;
    }

    function wmsProductKey(d) {
      return {
        item_type: d.itemType || "finished",
        product_name: d.productName,
        product_size: d.productSize,
        product_color: d.productColor,
        stage_name: d.stageName || "Готово",
        ready_for_position: d.readyForPosition || "Склад",
      };
    }

    async function wmsReceive() {
      const d = readWmsDraftFromForm();
      const qty = parseInt(d.quantity, 10);
      if (!d.productName || !qty || qty < 1) {
        showToast("ТСД", "Укажите изделие и количество (≥ 1).");
        return;
      }
      const actionKey = `wms:receive:${d.productName}:${d.productSize}:${d.productColor}:${qty}`;
      if (!beginAction(actionKey)) return;
      mainButton.disabled = true;
      const requestKey = `wms:receive:${createRequestId()}`;
      try {
        const data = await api("/api/wms/receive", {
          product_key: wmsProductKey(d),
          quantity: qty,
          request_key: requestKey,
          reason: "Приёмка от производства (ТСД)",
          tsd_device_id: navigator.userAgent.slice(0, 40),
        });
        const ok = data.status === "ok" || data.status === "duplicate";
        showToast("ТСД", ok ? `Принято: ${qty} шт.` : (data.reason || "Ошибка приёмки."));
        if (ok) { state.wmsDraft.quantity = ""; render(); refreshWmsWorkspace({silent: true}); }
        else mainButton.disabled = false;
      } catch (error) {
        showToast("Ошибка", error.apiMessage || "Не удалось принять товар.");
        mainButton.disabled = false;
      } finally {
        endAction(actionKey);
      }
    }

    async function wmsMaterialReceive() {
      const draft = state.wmsMaterialReceipt;
      syncWmsMaterialReceiptForm();
      const quantity = parseInt(draft.quantity, 10);
      if (!String(draft.name || "").trim() || !String(draft.color || "").trim() || !quantity || quantity < 1) {
        showToast("Материалы", "Введите материал, цвет и количество больше нуля.");
        return;
      }
      const actionKey = `wms:material-receive:${draft.name}:${draft.color}:${draft.unit}:${quantity}`;
      if (!beginAction(actionKey)) return;
      mainButton.disabled = true;
      try {
        const data = await api("/api/wms/material-receive", {
          material_name: String(draft.name).trim(),
          product_color: String(draft.color).trim(),
          quantity,
          unit: draft.unit || "рул",
          comment: String(draft.comment || "").trim(),
          request_key: `wms:material-receive:${createRequestId()}`,
          reason: "Ручная приёмка материала",
          tsd_device_id: navigator.userAgent.slice(0, 40),
        });
        const ok = data.status === "ok" || data.status === "duplicate";
        showToast("Материалы", ok ? (data.message || `Принято: ${quantity} ${draft.unit}.`) : (data.reason || data.message || "Ошибка приёмки."));
        if (ok) {
          draft.quantity = "";
          draft.comment = "";
          render();
          refreshWmsWorkspace({silent: true});
        } else {
          mainButton.disabled = false;
        }
      } catch (error) {
        showToast("Ошибка", error.apiMessage || "Не удалось принять материал.");
        mainButton.disabled = false;
      } finally {
        endAction(actionKey);
      }
    }

    async function wmsPutaway() {
      const d = readWmsDraftFromForm();
      const qty = parseInt(d.quantity, 10);
      const materialMode = d.itemType === "material";
      if (materialMode && d.toLocation) d.toLocationScanned = true;
      if (!d.toLocationScanned) {
        showToast("Склад", "Сначала отсканируйте ячейку размещения.");
        return;
      }
      if (!materialMode && !d.productScanned) {
        showToast("Склад", "Отсканируйте штрихкод товара.");
        return;
      }
      if (!d.productName || !qty || qty < 1) {
        showToast("ТСД", "Укажите изделие и количество (≥ 1).");
        return;
      }
      const toLoc = (d.toLocation || "").replace(/^LOC:/i, "").trim();
      if (!toLoc) {
        showToast("ТСД", "Отсканируйте или введите целевую ячейку.");
        return;
      }
      const actionKey = `wms:putaway:${d.productName}:${d.productSize}:${d.productColor}:${toLoc}:${qty}`;
      if (!beginAction(actionKey)) return;
      mainButton.disabled = true;
      const requestKey = `wms:putaway:${createRequestId()}`;
      try {
        const data = await api("/api/wms/putaway", {
          product_key: wmsProductKey(d),
          quantity: qty,
          unit: materialMode ? (d.materialUnit || "рул") : "шт",
          request_key: requestKey,
          to_location_code: toLoc,
          reason: materialMode ? "Размещение материала (вручную)" : "Размещение (ТСД)",
          tsd_device_id: navigator.userAgent.slice(0, 40),
        });
        const ok = data.status === "ok" || data.status === "duplicate";
        showToast("Склад", ok ? `Размещено: ${qty} ${materialMode ? (d.materialUnit || "рул") : "шт"} → ${toLoc}` : (data.reason || "Ошибка размещения."));
        if (ok) {
          state.wmsDraft.quantity = "";
          state.wmsDraft.toLocation = "";
          state.wmsDraft.productName = "";
          state.wmsDraft.productSize = "";
          state.wmsDraft.productColor = "";
          state.wmsDraft.itemType = "finished";
          state.wmsDraft.materialUnit = "рул";
          state.wmsDraft.productScanned = false;
          state.wmsDraft.toLocationScanned = false;
          render();
          refreshWmsWorkspace({silent: true});
        }
        else mainButton.disabled = false;
      } catch (error) {
        showToast("Ошибка", error.apiMessage || "Не удалось разместить товар.");
        mainButton.disabled = false;
      } finally {
        endAction(actionKey);
      }
    }

    async function wmsTransfer() {
      const d = readWmsDraftFromForm();
      const qty = parseInt(d.quantity, 10);
      if (!d.productName || !qty || qty < 1) {
        showToast("ТСД", "Укажите изделие и количество (≥ 1).");
        return;
      }
      const fromLoc = (d.fromLocation || "").replace(/^LOC:/i, "").trim();
      const toLoc = (d.toLocation || "").replace(/^LOC:/i, "").trim();
      if (!fromLoc || !toLoc) {
        showToast("ТСД", "Отсканируйте обе ячейки (из/в).");
        return;
      }
      if (fromLoc === toLoc) {
        showToast("ТСД", "Ячейки откуда и куда совпадают.");
        return;
      }
      const actionKey = `wms:transfer:${d.productName}:${d.productSize}:${d.productColor}:${fromLoc}:${toLoc}:${qty}`;
      if (!beginAction(actionKey)) return;
      mainButton.disabled = true;
      const requestKey = `wms:transfer:${createRequestId()}`;
      try {
        const data = await api("/api/wms/transfer", {
          product_key: wmsProductKey(d),
          quantity: qty,
          request_key: requestKey,
          from_location_code: fromLoc,
          to_location_code: toLoc,
          reason: "Перемещение (ТСД)",
          tsd_device_id: navigator.userAgent.slice(0, 40),
        });
        const ok = data.status === "ok" || data.status === "duplicate";
        showToast("ТСД", ok ? `Перемещено: ${qty} шт. ${fromLoc} → ${toLoc}` : (data.reason || "Ошибка перемещения."));
        if (ok) { state.wmsDraft.quantity = ""; state.wmsDraft.fromLocation = ""; state.wmsDraft.toLocation = ""; render(); refreshWmsWorkspace({silent: true}); }
        else mainButton.disabled = false;
      } catch (error) {
        showToast("Ошибка", error.apiMessage || "Не удалось переместить товар.");
        mainButton.disabled = false;
      } finally {
        endAction(actionKey);
      }
    }

    async function wmsPick() {
      const d = readWmsDraftFromForm();
      const qty = parseInt(d.quantity, 10);
      const fromLoc = (d.fromLocation || "").replace(/^LOC:/i, "").trim();
      if (!fromLoc || !d.fromLocationScanned) {
        showToast("Склад", "Сначала отсканируйте ячейку.");
        return;
      }
      if (!d.productName || !d.productScanned) {
        showToast("Склад", "Отсканируйте товар из выбранной ячейки.");
        return;
      }
      if (!qty || qty < 1) {
        showToast("Склад", "Введите количество (1 или больше).");
        return;
      }
      const stockRow = wmsFindScannedStock(fromLoc, wmsProductKey(d));
      const available = stockRow ? Math.max(0, Number(stockRow.quantity || 0) - Number(stockRow.reserved_quantity || 0)) : 0;
      if (!stockRow || qty > available) {
        showToast("Склад", `В ячейке доступно ${available} шт.`);
        return;
      }
      const actionKey = `wms:pick:${fromLoc}:${d.productName}:${d.productSize}:${d.productColor}:${qty}`;
      if (!beginAction(actionKey)) return;
      mainButton.disabled = true;
      try {
        const data = await api("/api/wms/pick", {
          product_key: wmsProductKey(d),
          quantity: qty,
          from_location_code: fromLoc,
          request_key: `wms:pick:${createRequestId()}`,
          reason: "Подбор из ячейки (ТСД)",
          tsd_device_id: navigator.userAgent.slice(0, 40),
        });
        const ok = data.status === "ok" || data.status === "duplicate";
        showToast("Склад", ok ? `Выдано: ${qty} шт. из ${fromLoc}` : (data.reason || "Ошибка выдачи."));
        if (ok) {
          state.wmsDraft.quantity = "";
          state.wmsDraft.productName = "";
          state.wmsDraft.productSize = "";
          state.wmsDraft.productColor = "";
          state.wmsDraft.productScanned = false;
          render();
          refreshWmsWorkspace({silent: true});
        } else {
          mainButton.disabled = false;
        }
      } catch (error) {
        showToast("Ошибка", error.apiMessage || "Не удалось выдать товар из ячейки.");
        mainButton.disabled = false;
      } finally {
        endAction(actionKey);
      }
    }

    async function wmsInventory() {
      const d = readWmsDraftFromForm();
      const countedQty = parseInt(d.quantity, 10);
      const locationCode = (d.fromLocation || "").replace(/^LOC:/i, "").trim();
      if (!d.productName || Number.isNaN(countedQty) || countedQty < 0) {
        showToast("ТСД", "Укажите изделие и фактическое количество (0 или больше).");
        return;
      }
      if (!locationCode) {
        showToast("ТСД", "Отсканируйте или введите ячейку пересчёта.");
        return;
      }
      const actionKey = `wms:inventory:${locationCode}:${d.productName}`;
      if (!beginAction(actionKey)) return;
      mainButton.disabled = true;
      try {
        const data = await api("/api/wms/inventory", {
          location_code: locationCode,
          counted: [{product_key: wmsProductKey(d), counted_quantity: countedQty}],
          request_key: `wms:inventory:${createRequestId()}`,
        });
        const ok = data.status === "ok" || data.status === "duplicate";
        showToast("ТСД", ok ? `Пересчёт сохранён: ${countedQty} шт.` : (data.reason || "Ошибка пересчёта."));
        if (ok) { state.wmsDraft.quantity = ""; render(); refreshWmsWorkspace({silent: true}); }
        else mainButton.disabled = false;
      } catch (error) {
        showToast("Ошибка", error.apiMessage || "Не удалось сохранить пересчёт.");
        mainButton.disabled = false;
      } finally {
        endAction(actionKey);
      }
    }

    async function wmsScrap() {
      const d = readWmsDraftFromForm();
      const qty = parseInt(d.quantity, 10);
      const fromLoc = (d.fromLocation || "").replace(/^LOC:/i, "").trim();
      if (!d.productName || !qty || qty < 1) {
        showToast("ТСД", "Укажите изделие и количество (≥ 1).");
        return;
      }
      if (!fromLoc || !d.reason.trim()) {
        showToast("ТСД", "Укажите ячейку и причину списания.");
        return;
      }
      const actionKey = `wms:scrap:${fromLoc}:${d.productName}:${qty}`;
      if (!beginAction(actionKey)) return;
      mainButton.disabled = true;
      try {
        const data = await api("/api/wms/scrap", {
          product_key: wmsProductKey(d),
          quantity: qty,
          from_location_code: fromLoc,
          target_state: d.targetState || "SCRAPPED",
          reason: d.reason.trim(),
          request_key: `wms:scrap:${createRequestId()}`,
          tsd_device_id: navigator.userAgent.slice(0, 40),
        });
        const ok = data.status === "ok" || data.status === "duplicate";
        showToast("ТСД", ok ? `Списано: ${qty} шт.` : (data.reason || "Ошибка списания."));
        if (ok) { state.wmsDraft.quantity = ""; state.wmsDraft.reason = ""; render(); refreshWmsWorkspace({silent: true}); }
        else mainButton.disabled = false;
      } catch (error) {
        showToast("Ошибка", error.apiMessage || "Не удалось списать товар.");
        mainButton.disabled = false;
      } finally {
        endAction(actionKey);
      }
    }

    async function wmsRegisterBarcode() {
      const d = readWmsDraftFromForm();
      const barcode = (d.barcode || "").trim();
      if (!barcode || !d.productName) {
        showToast("ТСД", "Укажите товар и отсканируйте его штрихкод.");
        return;
      }
      const actionKey = `wms:barcode:${barcode}`;
      if (!beginAction(actionKey)) return;
      try {
        const data = await api("/api/wms/barcode/register", {
          barcode,
          product_key: wmsProductKey(d),
        });
        state.wmsDraft.barcode = "";
        render();
        showToast("ТСД", data.message || "Штрихкод привязан.");
      } catch (error) {
        showToast("Ошибка", error.apiMessage || "Не удалось привязать штрихкод.");
      } finally {
        endAction(actionKey);
      }
    }

    async function wmsCreateLocation() {
      const d = readWmsDraftFromForm();
      const newLocationInput = document.getElementById("wmsNewLocation");
      const code = ((newLocationInput ? newLocationInput.value : "") || d.toLocation || "").replace(/^LOC:/i, "").trim().toUpperCase();
      if (!code) {
        showToast("ТСД", "Введите код новой ячейки.");
        return;
      }
      const actionKey = `wms:create-location:${code}`;
      if (!beginAction(actionKey)) return;
      try {
        const data = await api("/api/wms/locations/create", {
          code,
          zone_code: d.locationZone || "STORAGE",
          name_ru: (d.locationName || "").trim(),
        });
        state.wmsDraft.toLocation = code;
        render();
        refreshWmsWorkspace({silent: true});
        showToast("ТСД", data.message || `Ячейка ${code} создана.`);
      } catch (error) {
        showToast("Ошибка", error.apiMessage || "Не удалось создать ячейку.");
      } finally {
        endAction(actionKey);
      }
    }

    async function rejectFabricRolls(taskId, productColor, availableRolls) {
      const rawQuantity = window.prompt(`Сколько рулонов отправить в брак? Доступно: ${availableRolls}`, "1");
      if (rawQuantity === null) return;
      const normalized = String(rawQuantity).trim();
      if (!/^[0-9]+$/.test(normalized) || Number(normalized) <= 0 || Number(normalized) > Number(availableRolls)) {
        showToast("Брак рулонов", `Введите количество от 1 до ${availableRolls}.`);
        return;
      }
      const comment = window.prompt("Комментарий к браку рулонов", "") || "";
      if (!comment.trim()) {
        showToast("Брак рулонов", "Комментарий обязателен.");
        return;
      }

      const actionKey = `reject-fabric-rolls:${taskId}:${productColor}`;
      if (!beginAction(actionKey)) return;
      mainButton.disabled = true;
      try {
        const data = await api("/api/production/reject-fabric-rolls", {
          task_id: taskId,
          product_color: productColor,
          quantity: normalized,
          comment: comment.trim(),
        });
        if (!data.ok) {
          showToast("Брак рулонов", data.message || "Не удалось списать рулоны.");
          mainButton.disabled = false;
          return;
        }
        state.data.production = data.production || state.data.production;
        render();
        showToast("Брак рулонов", data.message || "Рулоны списаны в брак.");
      } catch (error) {
        showToast("Ошибка", "Не удалось списать рулоны в брак.");
        mainButton.disabled = false;
      } finally {
        endAction(actionKey);
      }
    }

    function renderCuttingStageDetail(current) {
      const draft = cuttingDraft(current);

      if (current.stage === "contours") {
        const rows = (current.colors || []).map((color) => (current.sizes || []).map((size) => `
          <div class="card cutting-input-row">
            <div><b>${escapeHtml(current.product_name || "Изделие")} · ${escapeHtml(size)} · ${escapeHtml(color)}</b><span>Количество деталей именно этого изделия</span></div>
            <input data-contour-key="${escapeHtml(`${current.product_name || "Изделие"}|${size}|${color}`)}" type="number" inputmode="numeric" min="0" step="1" placeholder="шт для этого изделия" value="${escapeHtml((draft.quantities || {})[`${current.product_name || "Изделие"}|${size}|${color}`] ?? (draft.quantities || {})[`${size}|${color}`] ?? "")}" aria-label="Количество ${escapeHtml(current.product_name || "изделия")} размер ${escapeHtml(size)} цвет ${escapeHtml(color)}">
          </div>
        `).join("")).join("");

        return `
          <div class="card order-detail">
            <div class="order-head"><div class="op-icon">${sewingIcon()}</div><div><b>${escapeHtml(current.stage_title)}</b><span>${escapeHtml(current.product_name)}</span></div><span class="status-chip">1 этап</span></div>
            <div class="op-list">${rows || itemEmpty("Нет размеров или цветов.")}</div>
            ${current.is_assigned_to_me ? `<div class="button-row"><button type="button" class="small-button secondary" data-cutting-action="release" data-cutting-task-id="${escapeHtml(current.id)}">Отменить и вернуть задание</button></div>` : ""}
          </div>
          ${renderTaskFabricRolls(current)}
          ${renderTaskAttachment(current.attachment)}
        `;
      }

      if (current.stage === "layout") {
        const rows = (current.colors || []).map((color) => `
          <div class="card cutting-input-row">
            <div><b>${escapeHtml(color)}</b><span>Нанесено контуров: ${escapeHtml(formatCuttingContourMatrix(current.contour_matrix, color, current.sizes_text || "Размеры задания"))}</span></div>
            <input data-layer-color="${escapeHtml(color)}" type="number" inputmode="numeric" min="0" step="1" placeholder="слои" value="${escapeHtml((draft.color_layers || {})[color] || "")}">
          </div>
        `).join("");
        const arbitrarySizes = cuttingArbitrarySizes(current);
        const arbitraryRows = Array.isArray(draft.arbitrary_operations) ? draft.arbitrary_operations : [];
        const arbitraryMarkup = arbitraryRows.map((item, index) => `
          <div class="arbitrary-operation-grid" data-arbitrary-row="${index}">
            <label>Размер
              <select data-arbitrary-size>
                ${arbitrarySizes.map((size) => `<option value="${escapeHtml(size)}" ${String(item.product_size || arbitrarySizes[0] || "") === String(size) ? "selected" : ""}>${escapeHtml(size)}</option>`).join("")}
              </select>
            </label>
            <label>Цвет настила
              <select data-arbitrary-color>
                ${(current.colors || []).map((color) => `<option value="${escapeHtml(color)}" ${String(item.product_color || current.colors[0] || "") === String(color) ? "selected" : ""}>${escapeHtml(color)}</option>`).join("")}
              </select>
            </label>
            <label>Частей
              <select data-arbitrary-parts>
                ${[2, 3, 4].map((parts) => `<option value="${parts}" ${Number(item.parts_count || 2) === parts ? "selected" : ""}>${parts}</option>`).join("")}
              </select>
            </label>
            <label>Слоёв
              <input data-arbitrary-layers type="number" inputmode="numeric" min="1" step="1" placeholder="например, 5" value="${escapeHtml(item.layers || "")}">
            </label>
            <button type="button" class="small-button secondary arbitrary-operation-remove" data-arbitrary-remove="${index}">Удалить</button>
          </div>
        `).join("");

        return `
          <div class="card order-detail">
            <div class="order-head"><div class="op-icon">${sewingIcon()}</div><div><b>${escapeHtml(current.stage_title)}</b><span>${escapeHtml(current.product_name)}</span></div><span class="status-chip">2 этап</span></div>
            <div class="op-list">${rows || itemEmpty("Нет цветов для настила.")}</div>
            <div class="arbitrary-operation-card">
              <div class="arbitrary-operation-head"><div><b>Произвольная операция</b><span>Отдельно в отчёте, но количество добавится к общему выпуску.</span></div><button type="button" class="small-button secondary" data-arbitrary-add>Добавить строку</button></div>
              <div class="arbitrary-operation-help">Выберите размер и цвет этого настила, укажите деление настила на 2, 3 или 4 части и фактическое число слоёв. Количество изделий система посчитает как число слоёв.</div>
              ${arbitraryMarkup || `<div class="empty">Если остатка настила нет, оставьте раздел пустым.</div>`}
            </div>
            ${current.is_assigned_to_me ? `<div class="button-row"><button type="button" class="small-button secondary" data-cutting-action="release" data-cutting-task-id="${escapeHtml(current.id)}">Отменить и вернуть задание</button></div>` : ""}
          </div>
          ${renderTaskFabricRolls(current)}
          ${renderTaskAttachment(current.attachment)}
        `;
      }

      if (current.stage === "cutting") {
        return `
          <div class="card order-detail">
            <div class="order-head"><div class="op-icon">${sewingIcon()}</div><div><b>${escapeHtml(current.stage_title)}</b><span>${escapeHtml(current.product_name)}</span></div><span class="status-chip">3 этап</span></div>
            <div class="form-grid"><div class="field full"><label>Готовность</label><select id="cuttingProgress">${[25, 50, 75, 100].map((value) => `<option value="${value}" ${String(draft.progress || 100) === String(value) ? "selected" : ""}>${value}%</option>`).join("")}</select></div></div>
            ${current.is_assigned_to_me ? `<div class="button-row"><button type="button" class="small-button secondary" data-cutting-action="release" data-cutting-task-id="${escapeHtml(current.id)}">Отменить и вернуть задание</button></div>` : ""}
          </div>
          ${renderTaskFabricRolls(current)}
          ${renderTaskAttachment(current.attachment)}
        `;
      }

      return `
        <div class="card order-detail">
          <div class="order-head"><div class="op-icon">${sewingIcon()}</div><div><b>${escapeHtml(current.stage_title)}</b><span>${escapeHtml(current.product_name)}</span></div><span class="status-chip">4 этап</span></div>
          <p class="empty">После выполнения готовый крой попадёт на склад полуфабрикатов.</p>
        </div>
        ${renderTaskFabricRolls(current)}
        ${renderTaskAttachment(current.attachment)}
      `;
    }

    function renderCuttingStageSummary(current) {
      return `
        <div class="card order-detail">
          <div class="order-head">
            <div class="op-icon">${sewingIcon()}</div>
            <div><b>${escapeHtml(current.stage_title)}</b><span>${escapeHtml(current.product_name)}</span></div>
            <span class="status-chip">${escapeHtml(current.status_text || current.status)}</span>
          </div>
          <div class="detail-grid">
            <div class="detail-box"><span>Этап</span><strong>${escapeHtml(current.next_action || "-")}</strong></div>
            <div class="detail-box"><span>Готовность</span><strong>${progressForTask(current)}%</strong></div>
            <div class="detail-box"><span>Размеры</span><strong>${escapeHtml((current.sizes || []).join(", ") || current.sizes_text || "-")}</strong></div>
            <div class="detail-box"><span>Цвета</span><strong>${escapeHtml((current.color_labels || current.colors || []).join(", ") || current.colors_text || "-")}</strong></div>
          </div>
        </div>
        ${renderTaskFabricRolls(current)}
        ${renderTaskAttachment(current.attachment)}
      `;
    }

    async function submitCuttingStage(current) {
      if (!current) return;
      const actionKey = `submit-cutting-stage:${current.stage}:${current.id}`;
      if (!beginAction(actionKey)) return;
      const payload = {stage: current.stage};

      if (current.stage === "contours") {
        payload.task_id = current.id;
        payload.quantities = {};
        document.querySelectorAll("[data-contour-key]").forEach((input) => {
          payload.quantities[input.dataset.contourKey] = input.value;
        });
      } else {
        payload.batch_id = current.id;
      }

      if (current.stage === "layout") {
        payload.color_layers = {};
        document.querySelectorAll("[data-layer-color]").forEach((input) => {
          payload.color_layers[input.dataset.layerColor] = input.value;
        });
        payload.arbitrary_operations = readCuttingArbitraryRowsFromDom();
      }

      if (current.stage === "cutting") {
        const progress = document.getElementById("cuttingProgress");
        payload.progress = progress ? progress.value : "100";
      }

      mainButton.disabled = true;

      try {
        const data = await api("/api/production/submit-cutting-stage", payload);

        if (!data.ok) {
          showToast("Задание", data.message || "Не удалось выполнить этап.");
          mainButton.disabled = false;
          return;
        }

        state.data.production = data.production || state.data.production;
        delete state.cuttingStageDrafts[cuttingDraftKey(current)];
        state.selectedOrder = 0;
        state.selectedOrderKey = "";
        state.selectedCuttingReportTask = 0;
        state.selectedCuttingReportTaskKey = "";
        render();
        showToast("Задание", data.message || "Этап выполнен.");
      } catch (error) {
        showToast("Ошибка", "Не удалось выполнить этап.");
        mainButton.disabled = false;
      } finally {
        endAction(actionKey);
      }
    }

    async function readDefectPhoto(file, task) {
      if (!file || !task) return;
      if (!["image/jpeg", "image/png", "image/webp"].includes(file.type) || file.size > 2 * 1024 * 1024) {
        showToast("Фото брака", "Выберите JPG, PNG или WebP размером не больше 2 МБ.");
        return;
      }
      const contentBase64 = await new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(String(reader.result || "").split(",", 2)[1] || "");
        reader.onerror = reject;
        reader.readAsDataURL(file);
      });
      state.taskDefectPhotos[task.id] = {
        file_name: file.name || `defect-${task.id}.jpg`,
        mime_type: file.type,
        content_base64: contentBase64,
      };
      render();
      showToast("Фото брака", "Фотография прикреплена.");
    }

    async function completeOperationTask(current) {
      if (!current) return;
      const actionKey = `complete-operation-task:${current.id}`;
      if (!beginAction(actionKey)) return;
      const goodInput = document.getElementById("taskGoodQuantity");
      const defectInput = document.getElementById("taskDefectQuantity");
      const draft = state.taskCompletionDrafts[current.id] || {};
      if (!draft.request_id) draft.request_id = createRequestId();
      state.taskCompletionDrafts[current.id] = draft;
      const completionPayload = {
        batch_id: current.id,
        request_id: draft.request_id,
        good_quantity: goodInput ? goodInput.value : (draft.good ?? current.quantity),
        defect_quantity: defectInput ? defectInput.value : (draft.defect ?? 0),
        defect_reason: document.getElementById("taskDefectReason") ? document.getElementById("taskDefectReason").value : (draft.defect_reason || ""),
        defect_disposition: document.getElementById("taskDefectDisposition") ? document.getElementById("taskDefectDisposition").value : (draft.defect_disposition || ""),
        defect_comment: document.getElementById("taskDefectComment") ? document.getElementById("taskDefectComment").value : (draft.defect_comment || ""),
        defect_photo: state.taskDefectPhotos[current.id] || null,
        packaging_option: document.getElementById("taskPackagingOption") ? document.getElementById("taskPackagingOption").value : (draft.packaging_option || ""),
      };
      mainButton.disabled = true;

      try {
        const data = await api("/api/routes/complete", completionPayload);

        if (!data.ok) {
          showToast("Задание", data.message || "Не удалось завершить операцию.");
          mainButton.disabled = false;
          return;
        }

        if (state.data.routes) state.data.routes.tasks = data.tasks || [];
        if (state.data.routes) state.data.routes.completed_tasks = data.completed_tasks || [];
        state.data.production = data.production || state.data.production;
        delete state.taskCompletionDrafts[current.id];
        delete state.taskDefectPhotos[current.id];
        state.selectedOrder = 0;
        state.selectedOrderKey = "";
        state.selectedReportTask = 0;
        state.selectedReportTaskKey = "";
        render();
        showToast("Задание", data.message || "Операция завершена.");
      } catch (error) {
        if (!navigator.onLine || error instanceof TypeError) {
          const saved = queueCompletion(completionPayload);
          showToast(saved ? "Сохранено" : "Ошибка", saved ? "Отчёт отправится автоматически после появления связи." : "Не удалось сохранить отчёт на устройстве.");
          mainButton.disabled = false;
        } else {
          showToast("Ошибка", "Не удалось завершить операцию.");
          mainButton.disabled = false;
        }
      } finally {
        endAction(actionKey);
      }
    }

    async function startOperationTask(current) {
      if (!current || current.task_kind !== "route" || state.data.is_admin) return;

      if (current.is_assigned_to_me) {
        state.selectedOrderKey = taskIdentity(current);
        render();
        return;
      }

      if (!current.can_take) {
        showToast("Задание", current.assigned_employee_name ? `Задание в работе у ${current.assigned_employee_name}.` : "Задание уже в работе.");
        return;
      }

      if (!confirmTaskTake(current)) return;

      const actionKey = `start-operation-task:${current.id}`;
      if (!beginAction(actionKey)) return;

      mainButton.disabled = true;

      try {
        const data = await api("/api/routes/start", {batch_id: current.id});

        if (!data.ok) {
          showToast("Задание", data.message || "Не удалось взять задание.");
          mainButton.disabled = false;
          return;
        }

        if (state.data.routes) {
          state.data.routes.tasks = data.tasks || [];
          state.data.routes.completed_tasks = data.completed_tasks || state.data.routes.completed_tasks || [];
        }
        state.selectedOrderKey = taskIdentity(current);
        state.screen = "orders";
        render();
        showToast("Задание", data.message || "Задание взято в работу.");
      } catch (error) {
        showToast("Ошибка", "Не удалось взять задание.");
        mainButton.disabled = false;
      } finally {
        endAction(actionKey);
      }
    }

    function authenticatedFileUrl(path, params = {}) {
      const url = new URL(path, window.location.href);
      Object.entries(params).forEach(([key, value]) => url.searchParams.set(key, value));
      if (debugTelegramId) url.searchParams.set("telegram_id", debugTelegramId);
      return url.toString();
    }

    function routeQrUrl(batchId) {
      return authenticatedFileUrl("/api/routes/qr", {batch_id: batchId});
    }

    function defectPhotoUrl(defectId) {
      return authenticatedFileUrl("/api/routes/defect-photo", {defect_id: defectId});
    }

    async function updateRouteTaskState(task, action) {
      if (!task) return;
      let reason = "";
      if (action === "pause") reason = "Перерыв";
      if (action === "block") {
        reason = window.prompt("Что мешает продолжить работу?", task.blocked_reason || "") || "";
        if (!reason.trim()) return;
      }
      if (action === "release") {
        reason = window.prompt("Почему передаёте задание?", "Передача следующей смене") || "";
        if (!reason.trim()) return;
      }

      const actionKey = `route-work-action:${task.id}:${action}`;
      if (!beginAction(actionKey)) return;
      mainButton.disabled = true;
      try {
        const data = await api("/api/routes/work-action", {batch_id: task.id, action, reason});
        if (!data.ok) {
          showToast("Задание", data.message || "Не удалось изменить состояние.");
          mainButton.disabled = false;
          return;
        }
        if (state.data.routes) {
          state.data.routes.tasks = data.tasks || [];
          state.data.routes.completed_tasks = data.completed_tasks || state.data.routes.completed_tasks || [];
        }
        state.selectedOrderKey = taskIdentity(data.batch || task);
        render();
        showToast("Задание", data.message || "Состояние обновлено.");
      } catch (error) {
        showToast("Ошибка", "Не удалось изменить состояние задания.");
        mainButton.disabled = false;
      } finally {
        endAction(actionKey);
      }
    }

    async function openRoutePassport(batchId) {
      if (!batchId) return;
      const actionKey = `route-passport:${batchId}`;
      if (!beginAction(actionKey)) return;
      try {
        const data = await api("/api/routes/passport", {batch_id: batchId});
        if (!data.ok) {
          showToast("Паспорт партии", data.message || "Паспорт не найден.");
          return;
        }
        state.passportReturnScreen = state.screen === "passport" ? (state.passportReturnScreen || "orders") : state.screen;
        state.passportBatchId = String(batchId);
        state.passportData = data.passport;
        state.screen = "passport";
        render();
      } catch (error) {
        showToast("Ошибка", "Не удалось открыть паспорт партии.");
      } finally {
        endAction(actionKey);
      }
    }

    async function openTraceCode(rawValue) {
      const traceCode = String(rawValue || "").trim().replace(/^TRACE:/i, "").toUpperCase();
      if (!traceCode) return;
      try {
        const data = await api("/api/routes/lookup", {trace_code: traceCode});
        if (!data.ok || !data.batch) {
          showToast("QR партии", data.message || "Партия не найдена.");
          return;
        }
        const task = {...data.batch, task_kind: "route"};
        if (task.work_status === "done") {
          openRoutePassport(task.id);
          return;
        }
        state.screen = "orders";
        state.orderCategory = state.data.is_admin ? adminOrderCategoryForTask(task) : (task.category || state.orderCategory);
        state.selectedOrderKey = taskIdentity(task);
        render();
        showToast("QR партии", `Открыто задание ${task.trace_code || task.id}.`);
      } catch (error) {
        showToast("Ошибка", "Не удалось найти партию.");
      }
    }

    function promptRouteCode() {
      const value = window.prompt("Введите код партии", "RB-");
      if (value) openTraceCode(value);
    }

    function stopWebQrScanner() {
      if (qrScannerFrame) window.cancelAnimationFrame(qrScannerFrame);
      qrScannerFrame = 0;
      if (qrScannerStream) {
        qrScannerStream.getTracks().forEach((track) => track.stop());
      }
      qrScannerStream = null;
      qrScannerVideo.srcObject = null;
      qrScanner.hidden = true;
      qrScannerStatus.textContent = "Запускаем камеру…";
    }

    async function getWmsCameraStream() {
      const constraints = [
        {audio: false, video: {facingMode: {exact: "environment"}, width: {ideal: 1280}, height: {ideal: 720}}},
        {audio: false, video: {facingMode: {ideal: "environment"}, width: {ideal: 1280}, height: {ideal: 720}}},
        {audio: false, video: true},
      ];
      let lastError = null;
      for (const constraint of constraints) {
        try {
          return await navigator.mediaDevices.getUserMedia(constraint);
        } catch (error) {
          lastError = error;
        }
      }
      throw lastError || new Error("Camera unavailable");
    }

    async function attachScannerStream(stream) {
      qrScannerStream = stream;
      qrScannerVideo.autoplay = true;
      qrScannerVideo.muted = true;
      qrScannerVideo.playsInline = true;
      qrScanner.hidden = false;
      qrScannerVideo.srcObject = stream;
      qrScannerStatus.textContent = "Камера включена. Наведите её на код.";
      try {
        await qrScannerVideo.play();
      } catch (_error) {
        qrScannerStatus.textContent = "Нажмите по экрану, чтобы запустить камеру.";
      }
    }

    async function openWebQrScanner() {
      qrScannerTitle.textContent = "QR-код партии";
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia || typeof window.BarcodeDetector !== "function") {
        promptRouteCode();
        return;
      }

      try {
        await attachScannerStream(await getWmsCameraStream());
        const detector = new window.BarcodeDetector({formats: ["qr_code"]});
        let detecting = false;
        const detectFrame = async () => {
          if (!qrScannerStream || qrScanner.hidden) return;
          if (!detecting && qrScannerVideo.readyState >= HTMLMediaElement.HAVE_CURRENT_DATA) {
            detecting = true;
            try {
              const codes = await detector.detect(qrScannerVideo);
              const value = codes && codes[0] ? codes[0].rawValue : "";
              if (value) {
                stopWebQrScanner();
                openTraceCode(value);
                return;
              }
            } catch (error) {
              // A transient unreadable frame is expected while the camera is moving.
            } finally {
              detecting = false;
            }
          }
          qrScannerFrame = window.requestAnimationFrame(detectFrame);
        };
        qrScannerFrame = window.requestAnimationFrame(detectFrame);
      } catch (error) {
        stopWebQrScanner();
        showToast("QR-код", "Камера недоступна. Введите код партии.");
        promptRouteCode();
      }
    }

    function scanRouteQr() {
      if (tg && typeof tg.showScanQrPopup === "function") {
        tg.showScanQrPopup({text: "Наведите камеру на QR-код партии"}, (value) => {
          openTraceCode(value);
          return true;
        });
        return;
      }
      openWebQrScanner();
    }

    function scanWms(field) {
      const prompts = {
        product: "Наведите камеру на штрихкод товара",
        bind_product: "Наведите камеру на новый штрихкод товара",
        from_location: "Наведите камеру на штрихкод ячейки",
        to_location: "Наведите камеру на штрихкод ячейки",
      };
      state.wmsScanField = field;
      qrScannerTitle.textContent = prompts[field] || "Сканирование";
      openWmsScanner();
    }

    function promptCurrentScannerCode() {
      if (state.workspace === "warehouse" && state.wmsScanField) {
        const code = window.prompt("Введите код ячейки или штрихкод товара:", "");
        if (code) handleWmsScan(code);
        return;
      }
      promptRouteCode();
    }

    async function handleWmsScan(rawValue) {
      const v = String(rawValue || "").trim();
      if (!v) return;
      clearWmsHardwareScannerInput();
      const field = state.wmsScanField || "product";
      if (field === "bind_product") {
        const el = document.getElementById("wmsBarcode");
        if (el) el.value = v;
        state.wmsDraft.barcode = v;
        showToast("ТСД", `Штрихкод считан: ${v}`);
        return;
      }
      const expectsLocation = field === "from_location" || field === "to_location";
      const location = wmsLocationByScan(v);
      const looksLikeLocation = /^LOC:/i.test(v) || /^Z\\d+-S\\d+-P\\d+-\\d+$/i.test(v);
      const scannedLocation = Boolean(location) || looksLikeLocation;
      if (expectsLocation && !scannedLocation) {
        showToast("Склад", "Сначала отсканируйте штрихкод ячейки.");
        return;
      }
      if (!expectsLocation && scannedLocation) {
        showToast("Склад", field === "lookup_product" ? "Для проверки отсканируйте товар, а не ячейку." : "Сейчас нужно отсканировать товар, а не ячейку.");
        return;
      }
      if (scannedLocation) {
        const code = location ? String(location.code) : v.replace(/^LOC:/i, "").trim().toUpperCase();
        if (state.wmsData.loaded && !location) {
          showToast("Склад", `Ячейка ${code} не найдена.`);
          return;
        }
        const target = field === "from_location" ? "wmsFromLocation" : "wmsToLocation";
        const el = document.getElementById(target);
        if (el) el.value = code;
        state.wmsDraft[field === "from_location" ? "fromLocation" : "toLocation"] = code;
        state.wmsDraft[field === "from_location" ? "fromLocationScanned" : "toLocationScanned"] = true;
        render();
        showToast("ТСД", `Ячейка: ${code}`);
      } else if (/^LPN:/i.test(v)) {
        showToast("ТСД", `Контейнер: ${v} (поддержка LPN — в разработке)`);
      } else {
        try {
          const data = await api("/api/wms/barcode/resolve", {barcode: v});
          const pk = data.product_key || {};
          if (field === "lookup_product") {
            state.wmsLookup = {barcode: v, productKey: pk, error: ""};
            render();
            focusWmsHardwareScanner();
            showToast("ТСД", `Товар найден: ${wmsProductLabel(pk)}.`);
            return;
          }
          state.wmsDraft.itemType = pk.item_type || "finished";
          state.wmsDraft.productName = pk.product_name || "";
          state.wmsDraft.productSize = pk.product_size || "";
          state.wmsDraft.productColor = pk.product_color || "";
          state.wmsDraft.stageName = pk.stage_name || "Готово";
          state.wmsDraft.readyForPosition = pk.ready_for_position || "Склад";
          state.wmsDraft.productScanned = true;
          const locationCode = state.wmsView === "putaway" ? state.wmsDraft.toLocation : state.wmsDraft.fromLocation;
          const stockRow = state.wmsView === "pick" && locationCode ? wmsFindScannedStock(locationCode, pk) : null;
          if (state.wmsView === "pick" && locationCode && !stockRow) {
            state.wmsDraft.productName = "";
            state.wmsDraft.productSize = "";
            state.wmsDraft.productColor = "";
            state.wmsDraft.productScanned = false;
            render();
            showToast("Склад", "Этого товара нет в отсканированной ячейке.");
          } else {
            render();
            showToast("ТСД", `Товар: ${state.wmsDraft.productName}`);
          }
        } catch (error) {
          if (field === "lookup_product") {
            state.wmsLookup = {barcode: v, productKey: null, error: error.apiMessage || "Штрихкод товара не зарегистрирован."};
            render();
            focusWmsHardwareScanner();
          }
          showToast("ТСД", error.apiMessage || "Штрихкод товара не зарегистрирован.");
        }
      }
    }

    function clearWmsHardwareScannerInput() {
      const input = document.getElementById("wmsHardwareScannerInput");
      if (input) input.value = "";
    }

    function focusWmsHardwareScanner() {
      window.setTimeout(() => {
        const input = document.getElementById("wmsHardwareScannerInput");
        if (!input) return;
        input.value = "";
        input.focus({preventScroll: true});
      }, 0);
    }

    // Code 128 fallback for Safari/iPhone, where BarcodeDetector is often
    // unavailable. It keeps the existing MoySklad labels (Z1-S1-P1-1) usable
    // without reprinting them as QR codes or adding a LOC: prefix.
    const code128Patterns = [
      "212222","222122","222221","121223","121322","131222","122213","122312","132212","221213","221312","231212","112232","122132","122231","113222","123122","123221","223211","221132","221231","213212","223112","312131","311222","321122","321221","312212","322112","322211","212123","212321","232121","111323","131123","131321","112313","132113","132311","211313","231113","231311","112133","112331","132131","113123","113321","133121","313121","211331","231131","213113","213311","213131","311123","311321","331121","312113","312311","332111","314111","221411","431111","111224","111422","121124","121421","141122","141221","112214","112412","122114","122411","142112","142211","241211","221114","413111","241112","134111","111242","121142","121241","114212","124112","124211","411212","421112","421211","212141","214121","412121","111143","111341","131141","114113","114311","411113","411311","113141","114131","311141","411131","211412","211214","211232","2331112",
    ];

    function code128PatternError(widths, pattern) {
      if (!pattern || widths.length !== pattern.length) return Number.POSITIVE_INFINITY;
      const modules = Array.from(pattern, Number);
      const scale = widths.reduce((sum, value) => sum + value, 0) / modules.reduce((sum, value) => sum + value, 0);
      if (scale < 0.65) return Number.POSITIVE_INFINITY;
      return widths.reduce((sum, value, index) => {
        const delta = (value / scale) - modules[index];
        return sum + (delta * delta);
      }, 0) / widths.length;
    }

    function nearestCode128Pattern(widths, allowedCodes = null) {
      let best = null;
      const codes = allowedCodes || code128Patterns.map((_pattern, index) => index);
      codes.forEach((code) => {
        const error = code128PatternError(widths, code128Patterns[code]);
        if (!best || error < best.error) best = {code, error};
      });
      return best;
    }

    function decodeCode128Values(values) {
      if (values.length < 3) return "";
      const start = values[0];
      const checksum = values[values.length - 1];
      const expected = values.slice(1, -1).reduce((sum, value, index) => sum + ((index + 1) * value), start) % 103;
      if (checksum !== expected) return "";
      let codeSet = start === 103 ? "A" : (start === 104 ? "B" : (start === 105 ? "C" : ""));
      if (!codeSet) return "";
      let result = "";
      for (const value of values.slice(1, -1)) {
        if (value === 102) continue; // FNC1
        if (codeSet === "C") {
          if (value === 100) { codeSet = "B"; continue; }
          if (value === 101) { codeSet = "A"; continue; }
          if (value > 99) return "";
          result += String(value).padStart(2, "0");
          continue;
        }
        if (value === 99) { codeSet = "C"; continue; }
        if (codeSet === "A" && value === 100) { codeSet = "B"; continue; }
        if (codeSet === "B" && value === 101) { codeSet = "A"; continue; }
        if (value > 95) return "";
        const charCode = codeSet === "A" && value >= 64 ? value - 64 : value + 32;
        if (charCode < 32 || charCode > 126) return "";
        result += String.fromCharCode(charCode);
      }
      return result;
    }

    function decodeCode128Runs(runs) {
      for (let startRun = 0; startRun + 19 <= runs.length; startRun += 1) {
        if (!runs[startRun].dark) continue;
        const startMatch = nearestCode128Pattern(
          runs.slice(startRun, startRun + 6).map((run) => run.width),
          [103, 104, 105],
        );
        if (!startMatch || startMatch.error > 1.8) continue;
        const values = [startMatch.code];
        const errors = [startMatch.error];
        let cursor = startRun + 6;
        while (cursor + 7 <= runs.length && values.length < 80) {
          const stopError = code128PatternError(
            runs.slice(cursor, cursor + 7).map((run) => run.width),
            code128Patterns[106],
          );
          if (values.length >= 3 && stopError <= 2.2) {
            const decoded = decodeCode128Values(values);
            const averageError = errors.reduce((sum, value) => sum + value, 0) / errors.length;
            if (decoded && averageError <= 2.0) return decoded;
          }
          if (cursor + 6 > runs.length) break;
          const match = nearestCode128Pattern(runs.slice(cursor, cursor + 6).map((run) => run.width));
          if (!match || match.code === 106 || match.error > 2.4) break;
          values.push(match.code);
          errors.push(match.error);
          cursor += 6;
        }
      }
      return "";
    }

    function decodeCode128Image(image) {
      const {data, width, height} = image;
      if (!data || width < 40 || height < 20) return "";
      const rows = [];
      for (let index = 0; index < 17; index += 1) {
        rows.push(Math.max(0, Math.min(height - 1, Math.round(height * (0.16 + (index * 0.0425))))));
      }
      for (const y of rows) {
        const luminance = [];
        let minimum = 255;
        let maximum = 0;
        for (let x = 0; x < width; x += 1) {
          const offset = ((y * width) + x) * 4;
          const value = (data[offset] * 0.299) + (data[offset + 1] * 0.587) + (data[offset + 2] * 0.114);
          luminance.push(value);
          minimum = Math.min(minimum, value);
          maximum = Math.max(maximum, value);
        }
        if (maximum - minimum < 70) continue;
        const threshold = minimum + ((maximum - minimum) * 0.48);
        const runs = [];
        let dark = luminance[0] < threshold;
        let runWidth = 0;
        luminance.forEach((value) => {
          const nextDark = value < threshold;
          if (nextDark === dark) {
            runWidth += 1;
          } else {
            runs.push({dark, width: runWidth});
            dark = nextDark;
            runWidth = 1;
          }
        });
        runs.push({dark, width: runWidth});
        const decoded = decodeCode128Runs(runs);
        if (decoded) return decoded;
      }
      return "";
    }

    async function openWmsScanner() {
      const hasNativeDetector = typeof window.BarcodeDetector === "function";
      const hasQrFallback = typeof window.jsQR === "function";
      const hasCanvasFallback = typeof document.createElement === "function";
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia || (!hasNativeDetector && !hasQrFallback && !hasCanvasFallback)) {
        if (tg && typeof tg.showScanQrPopup === "function") {
          tg.showScanQrPopup({text: qrScannerTitle.textContent || "Сканирование"}, (value) => {
            handleWmsScan(value);
            return true;
          });
          return;
        }
        const code = window.prompt("Введите код ячейки или штрихкод товара вручную:", "");
        if (code) handleWmsScan(code);
        return;
      }
      try {
        await attachScannerStream(await getWmsCameraStream());
        let detector = null;
        if (hasNativeDetector) {
          try {
            detector = new window.BarcodeDetector({formats: ["qr_code", "code_128", "ean_13", "code_39"]});
          } catch (_error) {
            try {
              detector = new window.BarcodeDetector({formats: ["qr_code"]});
            } catch (_fallbackError) {
              detector = null;
            }
          }
        }
        if (!detector && !hasQrFallback && !hasCanvasFallback) {
          stopWebQrScanner();
          const code = window.prompt("Введите код ячейки или штрихкод товара вручную:", "");
          if (code) handleWmsScan(code);
          return;
        }
        const canvas = hasCanvasFallback ? document.createElement("canvas") : null;
        const canvasContext = canvas ? canvas.getContext("2d", {willReadFrequently: true}) : null;
        let detecting = false;
        let lastFallbackScanAt = 0;
        const detectFrame = async (frameTime = 0) => {
          if (!qrScannerStream || qrScanner.hidden) return;
          const fallbackDue = frameTime - lastFallbackScanAt >= 140;
          if (!detecting && (detector || fallbackDue) && qrScannerVideo.readyState >= HTMLMediaElement.HAVE_CURRENT_DATA) {
            detecting = true;
            try {
              let value = "";
              if (detector) {
                const codes = await detector.detect(qrScannerVideo);
                value = codes && codes[0] ? codes[0].rawValue : "";
              }
              if (!value && fallbackDue && canvasContext && qrScannerVideo.videoWidth && qrScannerVideo.videoHeight) {
                lastFallbackScanAt = frameTime;
                const scale = Math.min(1, 960 / qrScannerVideo.videoWidth);
                canvas.width = Math.max(1, Math.round(qrScannerVideo.videoWidth * scale));
                canvas.height = Math.max(1, Math.round(qrScannerVideo.videoHeight * scale));
                canvasContext.drawImage(qrScannerVideo, 0, 0, canvas.width, canvas.height);
                const image = canvasContext.getImageData(0, 0, canvas.width, canvas.height);
                const qrCode = hasQrFallback ? window.jsQR(image.data, image.width, image.height) : null;
                value = qrCode ? qrCode.data : decodeCode128Image(image);
              }
              if (value) {
                stopWebQrScanner();
                handleWmsScan(value);
                return;
              }
            } catch (error) {
              // transient unreadable frame
            } finally {
              detecting = false;
            }
          }
          qrScannerFrame = window.requestAnimationFrame(detectFrame);
        };
        qrScannerFrame = window.requestAnimationFrame(detectFrame);
      } catch (error) {
        stopWebQrScanner();
        showToast("ТСД", "Камера недоступна. Введите код вручную.");
        const code = window.prompt("Введите код ячейки или штрихкод товара:", "");
        if (code) handleWmsScan(code);
      }
    }

    function renderPassport() {
      const passport = state.passportData;
      mainButton.textContent = "Назад к заданиям";
      mainButton.disabled = false;
      if (!passport) {
        mount.innerHTML = `<div class="screen-head"><div><h2>Паспорт партии</h2><p>Данные не загружены.</p></div></div>`;
        return;
      }
      const events = passport.events || [];
      const batches = passport.batches || [];
      const fabricLots = passport.fabric_lots || [];
      const workStateText = {
        free: "Свободно",
        in_work: "В работе",
        paused: "Пауза",
        blocked: "Заблокировано",
        done: "Готово",
      };
      const focusBatch = batches.find((batch) => String(batch.id) === String(passport.focus_batch_id)) || batches[0];
      mount.innerHTML = `
        <div class="screen-head"><div><h2>Паспорт партии</h2><p>${escapeHtml(focusBatch ? focusBatch.product_name : "Производственная партия")}</p></div><div class="date">${escapeHtml(passport.trace_code || "-")}</div></div>
        <div class="card field-card">
          <label>QR-код партии</label>
          <img class="party-qr" src="${escapeHtml(routeQrUrl(passport.focus_batch_id))}" alt="QR-код ${escapeHtml(passport.trace_code || "партии")}">
          <div class="detail-grid"><div class="detail-box"><span>Код</span><strong>${escapeHtml(passport.trace_code || "-")}</strong></div><div class="detail-box"><span>Версия маршрута</span><strong>${escapeHtml(passport.route_version || "-")}</strong></div></div>
        </div>
        <div class="section-title"><b>Материал и партии</b><span>${fabricLots.length}</span></div>
        <div class="op-list">${fabricLots.length ? fabricLots.map((lot) => `<div class="card report-row"><div><b>${escapeHtml(lot.lot_code)}</b><span>${escapeHtml(lot.material_name)} · ${escapeHtml(lot.product_color)}</span></div><span class="status-chip gray">${escapeHtml(lot.rolls)} рул.</span></div>`).join("") : itemEmpty("Для этой части маршрута партии ткани пока не связаны.")}</div>
        <div class="section-title"><b>Операции партии</b><span>${batches.length}</span></div>
        <div class="op-list">${batches.map((batch) => `<div class="card report-row"><div><b>${escapeHtml((batch.step || {}).operation || "Производственный этап")}</b><span>${escapeHtml(batch.product_size)} · ${escapeHtml(batch.product_color_label || batch.product_color)}${batch.assignee ? `<br>${escapeHtml(batch.assignee.full_name)}` : ""}</span></div><span class="status-chip ${batch.status === "done" ? "" : "warn"}">${escapeHtml(workStateText[batch.status === "done" ? "done" : batch.work_state] || "Открыто")}</span></div>`).join("")}</div>
        <div class="section-title"><b>Хронология</b><span>${events.length}</span></div>
        <div class="card field-card"><div class="passport-timeline">${events.length ? events.map((event) => `<div class="passport-event"><i class="passport-dot"></i><div><b>${escapeHtml(event.event_text || event.event_type)}</b><span>${escapeHtml((event.created_at || "").replace("T", " ").slice(0, 16))}${event.employee_name ? ` · ${escapeHtml(event.employee_name)}` : ""}${event.operation_name ? `<br>${escapeHtml(event.operation_name)}` : ""}${event.reason ? `<br>${escapeHtml(event.reason)}` : ""}${Number(event.good_quantity || 0) || Number(event.defect_quantity || 0) ? `<br>Годно ${escapeHtml(event.good_quantity || 0)} · брак ${escapeHtml(event.defect_quantity || 0)}` : ""}</span></div></div>`).join("") : itemEmpty("Событий пока нет.")}</div></div>
      `;
    }

    function renderOrderCreate() {
      const product = ensureOrderDraftDefaults();
      const catalog = getRouteCatalog();
      // For a shared lay, only sizes present in every selected product are
      // valid.  Rendering the first product's full list made unavailable
      // sizes (notably 86 and 128) look clickable before being discarded by
      // the draft validation.
      const sizes = state.orderAvailableSizes || (product ? product.sizes || [] : []);
      const selectedProducts = state.orderProducts.map((name) => routeProduct(name)).filter(Boolean);
      const colors = selectedProducts.length > 1
        ? selectedProducts.slice(1).reduce(
          (common, selected) => common.filter((color) => (selected.raw_colors || []).includes(color)),
          [...(selectedProducts[0].raw_colors && selectedProducts[0].raw_colors.length ? selectedProducts[0].raw_colors : getOrderColors())],
        )
        : getOrderColors();
      const rollInputs = state.orderColors.length ? `
        <div class="card field-card">
          <label>Рулоны по цветам</label>
          <div class="form-grid">
            ${state.orderColors.map((color) => `
              <div class="field"><label>${escapeHtml(color)}</label><input data-fabric-rolls="${escapeHtml(color)}" type="number" min="1" step="1" value="${escapeHtml(state.orderFabricRolls[color] || "1")}"></div>
            `).join("")}
          </div>
        </div>
      ` : `<div class="card field-card">${itemEmpty("Выберите цвета, чтобы указать рулоны.")}</div>`;
      const attachmentText = state.orderAttachment ? state.orderAttachment.file_name : "Word, Excel или PDF";

      mainButton.textContent = "Создать задание";
      mainButton.disabled = false;

      mount.innerHTML = `
        <div class="screen-head"><div><h2>Создать задание на раскрой</h2><p>Дальнейшие операции система создаст по маршруту автоматически.</p></div><div class="date">админ</div></div>
        <div class="tabs order-mode-tabs" role="tablist" aria-label="Раздел заказов"><button type="button" class="tab" data-order-mode="list" role="tab" aria-selected="false">Текущие задания</button><button type="button" class="tab active" data-order-mode="create" role="tab" aria-selected="true">Создать задание</button></div>
        <div class="card field-card">
          <div class="form-grid">
            <div class="field full"><label>Изделия в одном настиле</label>${renderChoiceChips("product", catalog.map((item) => item.product_name), state.orderProducts)}<p class="empty">Выберите одно или несколько изделий. Для выбранных изделий применяются общие размеры, цвета и настил.</p></div>
            <div class="field full"><label>Материал</label><select id="orderMaterial"><option value="Ткань" selected>Ткань</option></select></div>
          </div>
        </div>
        <div class="card field-card">
          <label>Планирование</label>
          <div class="form-grid">
            <div class="field"><label>Приоритет</label><select id="orderPriority"><option value="low" ${state.orderPriority === "low" ? "selected" : ""}>Низкий</option><option value="normal" ${state.orderPriority === "normal" ? "selected" : ""}>Обычный</option><option value="high" ${state.orderPriority === "high" ? "selected" : ""}>Высокий</option><option value="urgent" ${state.orderPriority === "urgent" ? "selected" : ""}>Срочный</option></select></div>
            <div class="field"><label>Срок</label><input id="orderDueDate" type="date" value="${escapeHtml(state.orderDueDate || "")}"></div>
          </div>
        </div>
        <div class="card field-card"><label>Размеры</label>${sizes.length ? renderChoiceChips("size", sizes, state.orderSizes) : itemEmpty("У изделия нет размеров.")}</div>
        <div class="card field-card"><label>Цвета ткани</label>${colors.length ? renderChoiceChips("color", colors, state.orderColors) : itemEmpty("У изделия нет цветов.")}</div>
        ${rollInputs}
        <div class="card field-card"><label>Файл задания</label><div class="form-grid"><div class="field full"><input id="orderAttachment" type="file" accept=".doc,.docx,.xls,.xlsx,.pdf,application/pdf,application/msword,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"></div></div><p class="empty">${escapeHtml(attachmentText)}</p></div>
        <div class="button-row"><button class="small-button secondary" data-order-action="cancel">К списку</button><button class="small-button" data-order-action="create">Создать</button></div>
      `;
    }

    function priorityLabel(priority) {
      return {low: "Низкий", normal: "Обычный", high: "Высокий", urgent: "Срочный"}[priority] || "Обычный";
    }

    function routeTaskCard(task, index, options = {}) {
      const isSelected = index === options.selectedIndex;
      const selectAttr = options.selectAttr || "data-select-order";
      const assignee = task.assigned_employee_name ? `<span class="route-assignee">В работе: ${escapeHtml(task.assigned_employee_name)}</span>` : "";
      const statusClass = task.work_status === "free" ? "gray" : (task.work_status === "done" ? "" : "warn");
      const deleteButton = state.data && state.data.is_admin ? `
        <div class="order-card-actions">
          ${task.work_state === "in_work" ? `<button type="button" class="small-button secondary" data-task-action="pause" data-task-id="${escapeHtml(task.id)}">Пауза</button><button type="button" class="small-button danger" data-task-action="block" data-task-id="${escapeHtml(task.id)}">Блокировать</button>` : ""}
          ${["paused", "blocked"].includes(task.work_state) ? `<button type="button" class="small-button" data-task-action="resume" data-task-id="${escapeHtml(task.id)}">Продолжить</button>` : ""}
          ${task.work_state && task.work_state !== "free" ? `<button type="button" class="small-button secondary" data-task-action="release" data-task-id="${escapeHtml(task.id)}">Освободить</button>` : ""}
          <button type="button" class="order-delete-button" data-order-action="delete" data-task-kind="${escapeHtml(task.task_kind || "route")}" data-task-id="${escapeHtml(task.id)}">Удалить</button>
        </div>
      ` : "";

      return `
        <div class="card order-card ${isSelected ? "selected" : ""}" ${selectAttr}="${index}">
          <div class="order-head route-order-head">
            <div class="op-icon">${uiIcon("work")}</div>
            <div><b>${escapeHtml(task.operation)}</b><span>${escapeHtml(task.product_name)}</span>${assignee}<span class="trace-code">${escapeHtml(task.trace_code || `RB-${task.id}`)}</span></div>
            <span class="status-chip ${statusClass}">${escapeHtml(task.status_text || "Свободно")}</span>
          </div>
          <div class="order-foot"><strong>${escapeHtml(task.product_size)} · ${escapeHtml(task.product_color)}</strong><strong>${escapeHtml(task.quantity)} шт</strong></div>
          ${task.blocked_reason ? `<div class="task-note">${escapeHtml(task.blocked_reason)}</div>` : ""}
          ${(task.due_date || task.priority === "urgent" || task.parent_batch_id) ? `<div class="route-inputs"><div class="route-input-row"><span>${task.parent_batch_id ? (task.parallel_group ? `Параллельная ветка · ${escapeHtml(task.parallel_branch || "операция")}` : `Связано с заданием #${escapeHtml(task.parent_batch_id)}`) : `Приоритет: ${escapeHtml(priorityLabel(task.priority))}`}</span><span>${task.due_date ? `до ${escapeHtml(task.due_date)}` : ""}</span></div></div>` : ""}
          ${renderRouteTaskInputs(task)}
          ${deleteButton}
        </div>
      `;
    }

    function renderRouteTaskInputs(task) {
      const inputs = task && task.inputs ? task.inputs : [];

      if (!inputs.length) return "";

      return `
        <div class="route-inputs">
          <b>Состав задания · ${inputs.length} ${inputs.length === 1 ? "вход" : "входа"}</b>
          ${inputs.map((input) => `
            <div class="route-input-row">
              <span>${escapeHtml(input.stage_name)} · ${escapeHtml(input.product_size)} · ${escapeHtml(input.product_color_label || input.product_color)}</span>
              <span>${escapeHtml(input.quantity_text || input.quantity)} ${escapeHtml(input.unit || "шт")}</span>
            </div>
          `).join("")}
        </div>
      `;
    }

    function orderTaskStatusText(task) {
      const bucket = orderTaskStatusBucket(task);
      if (bucket === "done") return task && task.status === "cancelled" ? "Отменено" : "Завершено";
      if (bucket === "free") return "Свободно";
      return task && task.status_text ? task.status_text : "В работе";
    }

    function renderOrderFilters(filterRows) {
      const products = orderFilterOptions(filterRows, "product");
      const sizes = orderFilterOptions(filterRows, "size");
      const colors = orderFilterOptions(filterRows, "color");
      const optionList = (values, selected, emptyLabel) => `<option value="">${emptyLabel}</option>${values.map((value) => `<option value="${escapeHtml(value)}" ${selected === value ? "selected" : ""}>${escapeHtml(value)}</option>`).join("")}`;

      return `
        <div class="card field-card order-filters">
          <div class="section-title"><b>Фильтры заданий</b><span>Изделие · размер · цвет</span></div>
          <div class="form-grid">
            <div class="field"><label>Наименование изделия</label><select data-order-filter="product">${optionList(products, state.orderProductFilter, "Все изделия")}</select></div>
            <div class="field"><label>Размер</label><select data-order-filter="size">${optionList(sizes, state.orderSizeFilter, "Все размеры")}</select></div>
            <div class="field"><label>Цвет</label><select data-order-filter="color">${optionList(colors, state.orderColorFilter, "Все цвета")}</select></div>
          </div>
          <div class="button-row"><button type="button" class="small-button secondary" data-order-action="clear-filters">Сбросить фильтры</button></div>
        </div>
      `;
    }

    function renderOrders() {
      if (state.data && state.data.is_admin && state.orderMode === "create") {
        renderOrderCreate();
        return;
      }

      const allTasks = visibleOrderRows();
      const filterRows = [...currentOrderRows(), ...getCompletedOrderRows()];
      state.selectedOrder = selectedTaskIndex(allTasks, state.selectedOrderKey, state.selectedOrder);
      const tasks = allTasks.filter((task) => task.task_kind !== "route");
      const routeRows = allTasks.filter((task) => task.task_kind === "route");
      const current = allTasks[state.selectedOrder] || allTasks[0];
      state.selectedOrderKey = taskIdentity(current);
      mainButton.textContent = state.data && state.data.is_admin
        ? "Обновить список"
        : (current && current.task_kind === "route" && current.is_assigned_to_me
          ? (current.can_complete ? "Выполнить задание" : "Продолжить задание")
          : (current && current.is_assigned_to_me ? "Открыть отчёт" : (current ? "Выбрать задание" : "Обновить статус")));
      mainButton.disabled = false;

      mount.innerHTML = `
        <div class="screen-head"><div><h2>${state.data && state.data.is_admin ? "Заказы" : "Задания"}</h2><p>${state.data && state.data.is_admin ? "Создавайте задания на раскрой и контролируйте маршрут производства." : "Выберите свободное задание, чтобы взять его в работу."}</p></div><div class="date">${allTasks.length} заданий</div></div>
        <div class="scan-row"><button type="button" class="small-button secondary" data-task-action="scan">Сканировать QR</button></div>
        ${state.data && state.data.is_admin ? `<div class="tabs order-mode-tabs" role="tablist" aria-label="Раздел заказов"><button type="button" class="tab ${state.orderMode === "list" ? "active" : ""}" data-order-mode="list" role="tab" aria-selected="${state.orderMode === "list" ? "true" : "false"}">Текущие задания</button><button type="button" class="tab ${state.orderMode === "create" ? "active" : ""}" data-order-mode="create" role="tab" aria-selected="${state.orderMode === "create" ? "true" : "false"}">Создать задание</button></div>` : ""}
        <div class="tabs admin-task-status-tabs" role="tablist" aria-label="Статус заданий">${["all", "free", "in_work", "done"].map((status) => `<button type="button" class="tab ${state.adminTaskStatus === status ? "active" : ""}" data-admin-task-status="${status}" role="tab" aria-selected="${state.adminTaskStatus === status ? "true" : "false"}">${adminTaskStatusLabel(status)}</button>`).join("")}</div>
        ${renderOrderFilters(filterRows)}
        <div class="op-list">
          ${allTasks.length ? `
          ${tasks.map((task, index) => {
            const filterValues = orderTaskFilterValues(task);
            const statusBucket = orderTaskStatusBucket(task);
            return `
            <div class="card order-card ${index === state.selectedOrder ? "selected" : ""}" data-select-order="${index}">
              <div class="order-head"><div class="op-icon">${uiIcon("work")}</div><div><b>${task.task_kind === "cutting_stage" ? escapeHtml(task.stage_title) : `Задание #${escapeHtml(task.id)}`}</b><span>${escapeHtml(filterValues.product || "Изделие не указано")}${task.assigned_employee_name ? `<br>В работе: ${escapeHtml(task.assigned_employee_name)}` : ""}</span></div><span class="status-chip ${statusBucket === "free" ? "gray" : (statusBucket === "done" ? "" : "warn")}">${escapeHtml(orderTaskStatusText(task))}</span></div>
              <div class="progress"><i style="--w:${progressForTask(task)}%"></i></div>
              <div class="order-foot"><span>Размер: ${escapeHtml(filterValues.sizes.join(", ") || "-")} · Цвет: ${escapeHtml(filterValues.colors.join(", ") || "-")}</span><span>${task.task_kind === "cutting_stage" ? escapeHtml(task.next_action) : `${progressForTask(task)}%`}</span></div>
              ${state.data && state.data.is_admin ? `<div class="order-card-actions">${task.task_kind === "production" && task.assigned_employee_id && statusBucket !== "done" ? `<button type="button" class="small-button secondary" data-order-action="release-cutting" data-task-kind="${escapeHtml(task.task_kind)}" data-task-id="${escapeHtml(task.id)}">Освободить</button>` : ""}${statusBucket !== "done" ? `<button type="button" class="order-delete-button" data-order-action="delete" data-task-kind="${escapeHtml(task.task_kind)}" data-task-id="${escapeHtml(task.id)}">Удалить</button>` : ""}</div>` : ""}
            </div>
          `;
          }).join("")}
          ${routeRows.map((task, routeIndex) => {
            const index = tasks.length + routeIndex;
            return routeTaskCard(task, index, {selectedIndex: state.selectedOrder});
          }).join("")}
          ` : itemEmpty("Активных заданий пока нет.")}
        </div>
        <div class="section-title"><b>Детали выбранного</b><span>${current ? progressForTask(current) : 0}%</span></div>
        ${current && current.task_kind === "cutting_stage" ? renderCuttingStageSummary(current) : current && current.task_kind === "production" ? `
          <div class="card order-detail"><div class="order-head"><div class="op-icon">${sewingIcon()}</div><div><b>Задание #${escapeHtml(current.id)}</b><span>${escapeHtml(current.product_name)}</span></div><span class="status-chip">${escapeHtml(orderTaskStatusText(current))}</span></div><div class="detail-grid"><div class="detail-box"><span>Размеры</span><strong>${escapeHtml((current.sizes || []).join(", ") || "-")}</strong></div><div class="detail-box"><span>Цвета</span><strong>${escapeHtml((current.color_labels || current.colors || []).join(", ") || "-")}</strong></div><div class="detail-box"><span>Приоритет</span><strong>${escapeHtml(priorityLabel(current.priority))}</strong></div><div class="detail-box"><span>Срок</span><strong>${escapeHtml(current.due_date || "Не задан")}</strong></div><div class="detail-box"><span>Статус</span><strong>${escapeHtml(orderTaskStatusText(current))}</strong></div><div class="detail-box"><span>Создано</span><strong>${escapeHtml((current.created_at || "").slice(0, 10) || "-")}</strong></div></div></div>
          ${renderTaskFabricRolls(current)}
          ${renderTaskAttachment(current.attachment)}
        ` : current ? `
          <div class="card order-detail"><div class="order-head route-order-head"><div class="op-icon">${sewingIcon()}</div><div><b>${escapeHtml(current.operation)}</b><span>${escapeHtml(current.product_name)}</span>${current.assigned_employee_name ? `<span class="route-assignee">В работе: ${escapeHtml(current.assigned_employee_name)}</span>` : ""}<span class="trace-code">${escapeHtml(current.trace_code || `RB-${current.id}`)}</span></div><span class="status-chip ${current.work_state === "free" ? "gray" : "warn"}">${escapeHtml(current.status_text || "Свободно")}</span></div><div class="detail-grid"><div class="detail-box"><span>Размер</span><strong>${escapeHtml(current.product_size || "-")}</strong></div><div class="detail-box"><span>Цвет</span><strong>${escapeHtml(current.product_color || "-")}</strong></div><div class="detail-box"><span>Количество</span><strong>${escapeHtml(current.quantity || 0)} шт</strong></div><div class="detail-box"><span>Статус</span><strong>${escapeHtml(current.status_text || "-")}</strong></div></div>${renderRouteTaskInputs(current)}${current.blocked_reason ? `<div class="task-note">${escapeHtml(current.blocked_reason)}</div>` : ""}<div class="button-row"><button type="button" class="small-button secondary" data-task-action="passport" data-task-id="${escapeHtml(current.id)}">Паспорт / QR</button></div></div>
          ${!state.data.is_admin && current.is_assigned_to_me ? renderTaskCompletionForm(current) : ""}
        ` : `<div class="card order-detail">${itemEmpty("Детали появятся после создания задания.")}</div>`}
        ${state.data && state.data.is_admin && current ? `<div class="button-row">${current.task_kind === "production" && current.assigned_employee_id ? `<button class="small-button secondary" data-order-action="release-cutting" data-task-kind="${escapeHtml(current.task_kind)}" data-task-id="${escapeHtml(current.id)}">Освободить задание</button>` : ""}<button class="small-button danger" data-order-action="delete" data-task-kind="${escapeHtml(current.task_kind)}" data-task-id="${escapeHtml(current.id)}">Удалить задание</button></div>` : ""}
      `;
    }

    function analyticsDuration(minutes) {
      const value = Number(minutes || 0);
      if (value < 60) return `${Math.round(value)} мин`;
      return `${Math.floor(value / 60)} ч ${Math.round(value % 60)} мин`;
    }

    function analyticsTaskMetric(task, metric) {
      if (metric === "cycle") return analyticsDuration(task.cycle_minutes);
      if (metric === "lead") return analyticsDuration(task.lead_minutes);
      if (metric === "quality") return `${Number(task.good_quantity || 0)} / ${Number(task.defect_quantity || 0)}`;
      if (metric === "schedule") return task.on_time === true ? "в срок" : task.on_time === false ? "просрочено" : "без срока";
      if (metric === "quantity") return `${Number(task.quantity || 0)} шт`;
      return task.status_text || task.status || "открыть";
    }

    function analyticsTaskRows(tasks, metric = "status") {
      return tasks.length ? tasks.map((task) => `
        <div class="card report-row analytics-row" data-analytics-task-id="${escapeHtml(task.id)}">
          <div><b>${escapeHtml(task.operation || "Задание")}</b><span>#${escapeHtml(task.id)} · ${escapeHtml(task.product || "-")}<br>${escapeHtml(task.size || "-")} · ${escapeHtml(task.color || "-")}${task.employee ? ` · ${escapeHtml(task.employee)}` : ""}</span></div>
          <span class="status-chip ${metric === "schedule" && task.on_time === false ? "warn" : "gray"}">${escapeHtml(analyticsTaskMetric(task, metric))}</span>
        </div>
      `).join("") : itemEmpty("Данных за выбранный период нет.");
    }

    function analyticsDefectRows(defects) {
      return defects.length ? defects.map((defect) => `
        <div class="card report-row analytics-row" data-analytics-task-id="${escapeHtml(defect.batch_id)}">
          <div><b>${escapeHtml(defect.product)} · ${escapeHtml(defect.stage)}</b><span>${escapeHtml(defect.size)} · ${escapeHtml(defect.color)} · ${escapeHtml(defect.reason)}<br>${escapeHtml(defect.disposition)}${defect.employee ? ` · ${escapeHtml(defect.employee)}` : ""}</span></div>
          <span class="status-chip warn">${escapeHtml(defect.quantity)} шт</span>
        </div>
      `).join("") : itemEmpty("Брак за выбранный период не зарегистрирован.");
    }

    function analyticsAllTasks(control) {
      const details = control.details || {};
      const unique = new Map();
      [details.active_tasks || [], details.completed_tasks || [], details.planned_tasks || []]
        .flat()
        .forEach((task) => unique.set(String(task.id), task));
      return [...unique.values()];
    }

    function renderAdminAnalyticsDetail(control) {
      const details = control.details || {};
      const view = state.analyticsView || "overview";
      const period = control.start_date === control.end_date
        ? control.start_date || ""
        : `${control.start_date || ""} — ${control.end_date || ""}`;
      const titles = {
        planfact: ["План / факт", "Задания, вошедшие в расчёт плана и выпуска."],
        fpy: ["Качество FPY", "Годная продукция и брак с первого прохождения."],
        active: ["В работе", "Все активные производственные задания."],
        semifinished: ["Полуфабрикаты", "Текущие остатки незавершённого производства."],
        cycle: ["Cycle time", "Время от взятия задания до завершения."],
        lead: ["Lead time", "Время от создания задания до завершения."],
        schedule: ["Соблюдение сроков", "Задания со сроком выполнения."],
        defects: ["Брак", "Изделие, этап, причина и принятое решение."],
        wip: ["WIP по этапам", "Незавершённое производство по участкам."],
        stage: [state.analyticsStage || "Этап", "Активные задания выбранного этапа."],
        alerts: ["Требует внимания", "Свободные, просроченные задания и брак."],
        task: ["Карточка задания", "Подробные данные производственного задания."],
      };
      const heading = titles[view] || titles.planfact;
      const head = `
        <div class="screen-head"><div><h2>${escapeHtml(heading[0])}</h2><p>${escapeHtml(heading[1])}</p></div><div class="date">${escapeHtml(period)}</div></div>
        <div class="section-title"><b>Аналитика</b><button type="button" data-analytics-back>К обзору</button></div>
      `;

      if (view === "task") {
        const task = analyticsAllTasks(control).find((row) => String(row.id) === String(state.analyticsTaskId));
        if (!task) return `${head}${itemEmpty("Задание не найдено в текущем периоде.")}`;
        const taskDefects = (details.defects || control.defects || []).filter((row) => String(row.batch_id) === String(task.id));
        return `${head}
          <div class="card order-detail">
            <div class="order-head"><div class="op-icon">${uiIcon("work")}</div><div><b>${escapeHtml(task.operation)}</b><span>#${escapeHtml(task.id)} · ${escapeHtml(task.product)}</span></div><span class="status-chip ${task.on_time === false ? "warn" : "gray"}">${escapeHtml(task.status_text)}</span></div>
            <div class="detail-grid">
              <div class="detail-box"><span>Размер</span><strong>${escapeHtml(task.size || "-")}</strong></div>
              <div class="detail-box"><span>Цвет</span><strong>${escapeHtml(task.color || "-")}</strong></div>
              <div class="detail-box"><span>План</span><strong>${escapeHtml(task.quantity || 0)} шт</strong></div>
              <div class="detail-box"><span>Годно / брак</span><strong>${escapeHtml(task.good_quantity || 0)} / ${escapeHtml(task.defect_quantity || 0)}</strong></div>
              <div class="detail-box"><span>Сотрудник</span><strong>${escapeHtml(task.employee || "Не назначен")}</strong></div>
              <div class="detail-box"><span>Приоритет</span><strong>${escapeHtml(priorityLabel(task.priority))}</strong></div>
              <div class="detail-box"><span>Срок</span><strong>${escapeHtml(task.due_date || "Не задан")}</strong></div>
              <div class="detail-box"><span>Этап</span><strong>${escapeHtml(task.stage || "-")}</strong></div>
              <div class="detail-box"><span>Cycle time</span><strong>${escapeHtml(task.cycle_minutes == null ? "-" : analyticsDuration(task.cycle_minutes))}</strong></div>
              <div class="detail-box"><span>Lead time</span><strong>${escapeHtml(task.lead_minutes == null ? "-" : analyticsDuration(task.lead_minutes))}</strong></div>
              <div class="detail-box"><span>Код партии</span><strong>${escapeHtml(task.trace_code || `RB-${task.id}`)}</strong></div>
              <div class="detail-box"><span>Версия маршрута</span><strong>${escapeHtml(task.route_version || "-")}</strong></div>
            </div>
            ${task.blocked_reason ? `<div class="task-note">${escapeHtml(task.blocked_reason)}</div>` : ""}
            <div class="button-row"><button type="button" class="small-button secondary" data-task-action="passport" data-task-id="${escapeHtml(task.id)}">Паспорт / QR</button>${task.status === "active" ? `<button type="button" class="small-button danger" data-analytics-delete-task-kind="${escapeHtml(task.task_kind || "route")}" data-analytics-delete-task-id="${escapeHtml(task.id)}">Удалить задание</button>` : ""}</div>
          </div>
          <div class="section-title"><b>Брак задания</b><span>${taskDefects.length}</span></div>
          <div class="op-list">${analyticsDefectRows(taskDefects)}</div>
        `;
      }

      if (view === "planfact") return `${head}
        <div class="card analytics-formula"><strong>${escapeHtml(control.fact || 0)} / ${escapeHtml(control.plan || 0)} шт</strong><span>Факт годной продукции относительно количества во всех созданных заданиях периода.</span></div>
        <div class="section-title"><b>Созданные задания</b><span>${(details.planned_tasks || []).length}</span></div><div class="op-list">${analyticsTaskRows(details.planned_tasks || [], "quantity")}</div>
        <div class="section-title"><b>Завершённые задания</b><span>${(details.completed_tasks || []).length}</span></div><div class="op-list">${analyticsTaskRows(details.completed_tasks || [], "quality")}</div>`;

      if (view === "fpy") return `${head}
        <div class="card analytics-formula"><strong>${escapeHtml(control.fpy || 0)}%</strong><span>FPY = годное количество / (годное количество + брак). Переделка отображается в карточке исходного задания.</span></div>
        <div class="op-list">${analyticsTaskRows((details.completed_tasks || []).slice().sort((a, b) => Number(b.defect_quantity || 0) - Number(a.defect_quantity || 0)), "quality")}</div>`;

      if (view === "active") return `${head}<div class="op-list">${analyticsTaskRows(details.active_tasks || [], "quantity")}</div>`;

      if (view === "semifinished") return `${head}<div class="op-list">${(details.semifinished || []).length ? (details.semifinished || []).map((row) => `
        <div class="card report-row"><div><b>${escapeHtml(row.product)} · ${escapeHtml(row.stage)}</b><span>${escapeHtml(row.size)} · ${escapeHtml(row.color)}<br>Для: ${escapeHtml(row.ready_for || "-")}</span></div><span class="status-chip gray">${escapeHtml(row.quantity)} ${escapeHtml(row.unit)}</span></div>
      `).join("") : itemEmpty("На складе нет полуфабрикатов.")}</div>`;

      if (view === "cycle") return `${head}<div class="op-list">${analyticsTaskRows((details.cycle_tasks || []).slice().sort((a, b) => Number(b.cycle_minutes || 0) - Number(a.cycle_minutes || 0)), "cycle")}</div>`;
      if (view === "lead") return `${head}<div class="op-list">${analyticsTaskRows((details.lead_tasks || []).slice().sort((a, b) => Number(b.lead_minutes || 0) - Number(a.lead_minutes || 0)), "lead")}</div>`;
      if (view === "schedule") return `${head}<div class="op-list">${analyticsTaskRows((details.schedule_tasks || []).slice().sort((a, b) => String(a.due_date).localeCompare(String(b.due_date))), "schedule")}</div>`;
      if (view === "defects") return `${head}<div class="op-list">${analyticsDefectRows(details.defects || control.defects || [])}</div>`;

      if (view === "wip") return `${head}<div class="op-list">${(control.stages || []).length ? (control.stages || []).map((stage) => `
        <div class="card report-row analytics-row" data-analytics-stage="${escapeHtml(stage.stage)}"><div><b>${escapeHtml(stage.stage)}</b><span>${escapeHtml(stage.tasks)} заданий · свободно ${escapeHtml(stage.free)} · просрочено ${escapeHtml(stage.overdue)}</span></div><span class="status-chip ${stage.overdue ? "warn" : "gray"}">${escapeHtml(stage.quantity)} шт ›</span></div>
      `).join("") : itemEmpty("Активных производственных этапов сейчас нет.")}</div>`;

      if (view === "stage") {
        const stageTasks = (details.active_tasks || []).filter((task) => task.stage === state.analyticsStage);
        return `${head}<div class="op-list">${analyticsTaskRows(stageTasks, "quantity")}</div>`;
      }

      return `${head}<div class="op-list">${(control.alerts || []).length ? (control.alerts || []).map((alert) => `
        <div class="card report-row analytics-row" ${alert.batch_id ? `data-analytics-task-id="${escapeHtml(alert.batch_id)}"` : ""}><div><b>${escapeHtml(alert.title)}</b><span>${escapeHtml(alert.detail)}</span></div><span class="status-chip ${alert.type === "overdue" || alert.type === "defect" ? "warn" : "gray"}">${alert.type === "defect" ? "брак" : alert.type === "overdue" ? "срок" : "свободно"} ›</span></div>
      `).join("") : itemEmpty("Отклонений не найдено.")}</div>`;
    }

    function renderAnalytics() {
      const operations = getReportOperations();
      const feedback = getFeedbackRows();
      const tasks = getTasks();
      const fabricRows = getProduction().fabric_stock || [];
      const formed = tasks.filter((task) => task.status === "formed").length;
      const inCutting = tasks.filter((task) => task.status === "in_cutting" || task.status === "contours_done").length;
      const active = tasks.filter((task) => task.status === "active").length;
      const total = Math.max(tasks.length, 1);
      const donePercent = Math.round(formed / total * 100);

      mainButton.textContent = state.data && state.data.is_admin ? "Обновить контроль" : "Открыть задания";
      mainButton.disabled = false;

      if (!state.data || !state.data.is_admin) {
        const myRouteTasks = getMyRouteTasks();
        const myCuttingTasks = getMyCuttingTasks();
        const freeTasks = getRouteTasks().filter((task) => task.can_take).length;
        const completedTasks = getCompletedRouteTasks();

        mount.innerHTML = `
          <div class="screen-head"><div><h2>Моя работа</h2><p>Текущие и завершённые задания.</p></div><div class="date">сейчас</div></div>
          <div class="summary-grid">
            <button class="card summary-card clickable" data-go="report" data-report-target="work"><span>В работе</span><strong>${myRouteTasks.length + myCuttingTasks.length}</strong><small>активных заданий</small></button>
            <button class="card summary-card clickable" data-go="orders"><span>Свободно</span><strong>${freeTasks}</strong><small>можно взять</small></button>
            <button class="card summary-card clickable" data-go="report" data-report-target="done"><span>Завершено</span><strong>${completedTasks.length}</strong><small>в истории заданий</small></button>
            <button class="card summary-card clickable" data-go="report" data-report-target="work"><span>В отчёте</span><strong>${operations.length}</strong><small>операций смены</small></button>
          </div>
          <div class="section-title"><b>Последние завершённые</b><button data-go="report">открыть</button></div>
          <div class="op-list">
            ${completedTasks.length ? completedTasks.slice(0, 6).map((task) => `
              <div class="card shift-card clickable" data-go="report"><div><b>${escapeHtml(task.operation || task.product_name)}</b><span>${escapeHtml(task.product_size || "-")} · ${escapeHtml(task.product_color || "-")}</span></div><span class="status-chip">${escapeHtml(task.good_quantity || 0)} шт</span></div>
            `).join("") : itemEmpty("Завершённых заданий пока нет.")}
          </div>
        `;
        return;
      }

      const control = state.data.admin && state.data.admin.production_control ? state.data.admin.production_control : {};
      const stages = control.stages || [];
      const alerts = control.alerts || [];

      if (state.analyticsView && state.analyticsView !== "overview") {
        mount.innerHTML = renderAdminAnalyticsDetail(control);
        return;
      }

      mount.innerHTML = `
        <div class="screen-head"><div><h2>Контроль производства</h2><p>План, качество, незавершёнка и отклонения.</p></div><div class="date">${escapeHtml(control.start_date === control.end_date ? control.start_date || "" : `${control.start_date || ""} — ${control.end_date || ""}`)}</div></div>
        <div class="kpi-grid">
          <button type="button" class="card kpi analytics-card" data-analytics-view="planfact"><span class="kpi-top"><span>План / факт</span><span class="kpi-ico">${uiIcon("target")}</span></span><strong>${escapeHtml(control.fact || 0)}<small> / ${escapeHtml(control.plan || 0)}</small></strong><span>Подробнее ›</span></button>
          <button type="button" class="card kpi good analytics-card" data-analytics-view="fpy"><span class="kpi-top"><span>FPY</span><span class="kpi-ico">${uiIcon("quality")}</span></span><strong>${escapeHtml(control.fpy || 0)}<small>%</small></strong><span>Подробнее ›</span></button>
          <button type="button" class="card kpi analytics-card" data-analytics-view="active"><span class="kpi-top"><span>В работе</span><span class="kpi-ico">${uiIcon("work")}</span></span><strong>${escapeHtml(control.active_quantity || 0)}<small> шт</small></strong><span>${escapeHtml(control.active_tasks || 0)} заданий · подробнее ›</span></button>
          <button type="button" class="card kpi analytics-card" data-analytics-view="semifinished"><span class="kpi-top"><span>Полуфабрикаты</span><span class="kpi-ico">${uiIcon("layers")}</span></span><strong>${escapeHtml(control.semifinished_quantity || 0)}<small> шт</small></strong><span>Подробнее ›</span></button>
        </div>
        <div class="kpi-grid">
          <button type="button" class="card kpi analytics-card" data-analytics-view="cycle"><span class="kpi-top"><span>Cycle time</span><span class="kpi-ico">${uiIcon("cycle")}</span></span><strong>${escapeHtml(analyticsDuration(control.average_cycle_minutes))}</strong><span>Подробнее ›</span></button>
          <button type="button" class="card kpi analytics-card" data-analytics-view="lead"><span class="kpi-top"><span>Lead time</span><span class="kpi-ico">${uiIcon("lead")}</span></span><strong>${escapeHtml(analyticsDuration(control.average_lead_minutes))}</strong><span>Подробнее ›</span></button>
          <button type="button" class="card kpi good analytics-card" data-analytics-view="schedule"><span class="kpi-top"><span>В срок</span><span class="kpi-ico">${uiIcon("schedule")}</span></span><strong>${escapeHtml(control.schedule_adherence || 0)}<small>%</small></strong><span>Подробнее ›</span></button>
          <button type="button" class="card kpi danger analytics-card" data-analytics-view="defects"><span class="kpi-top"><span>Брак</span><span class="kpi-ico">${uiIcon("defect")}</span></span><strong>${escapeHtml(control.defect_quantity || 0)}<small> шт</small></strong><span>Подробнее ›</span></button>
        </div>
        <div class="section-title"><b>WIP по этапам</b><button type="button" data-analytics-view="wip">все этапы</button></div>
        <div class="op-list">
          ${stages.length ? stages.map((stage) => `<div class="card report-row analytics-row" data-analytics-stage="${escapeHtml(stage.stage)}"><div><b>${escapeHtml(stage.stage)}</b><span>${escapeHtml(stage.tasks)} заданий · свободно ${escapeHtml(stage.free)} · просрочено ${escapeHtml(stage.overdue)}</span></div><span class="status-chip ${stage.overdue ? "warn" : "gray"}">${escapeHtml(stage.quantity)} шт ›</span></div>`).join("") : itemEmpty("Активных производственных этапов сейчас нет.")}
        </div>
        <div class="section-title"><b>Требует внимания</b><button type="button" data-analytics-view="alerts">все ${alerts.length}</button></div>
        <div class="op-list">
          ${alerts.length ? alerts.slice(0, 5).map((alert) => `<div class="card report-row analytics-row" ${alert.batch_id ? `data-analytics-task-id="${escapeHtml(alert.batch_id)}"` : `data-analytics-view="alerts"`}><div><b>${escapeHtml(alert.title)}</b><span>${escapeHtml(alert.detail)}</span></div><span class="status-chip ${alert.type === "overdue" || alert.type === "defect" ? "warn" : "gray"}">${alert.type === "defect" ? "брак" : alert.type === "overdue" ? "срок" : "свободно"} ›</span></div>`).join("") : itemEmpty("Отклонений не найдено.")}
        </div>
      `;
    }

    function renderAdminTabs() {
      const sections = [
        ["reports", "Отчёты"],
        ["size_markers", "Размерники"],
        ["operations", "Операции"],
        ["employees", "Сотрудники"],
        ["shifts", "Смены"],
        ["feedback", "Связь"],
      ];

      return `<div class="segment-row">${sections.map(([id, label]) => `
        <button class="segment-button ${state.adminSection === id ? "active" : ""}" data-admin-section="${id}">${label}</button>
      `).join("")}</div>`;
    }

    function renderAdminSizeMarkers(admin) {
      const rows = admin && Array.isArray(admin.size_markers) ? admin.size_markers : [];
      const openRows = rows.filter((row) => row.status === "open");
      const totalRequired = rows.reduce((sum, row) => sum + Number(row.planned_quantity || 0), 0);
      const totalRemaining = rows.reduce((sum, row) => sum + Number(row.remaining_quantity || 0), 0);
      mainButton.textContent = "Обновить размерники";
      mainButton.disabled = false;

      const rowsHtml = rows.length ? rows.map((row) => {
        const done = Number(row.completed_quantity || 0);
        const planned = Number(row.planned_quantity || 0);
        const remaining = Number(row.remaining_quantity || 0);
        const isDone = row.status === "done";
        return `
          <div class="card report-row">
            <div>
              <b>${escapeHtml(row.product_name)}</b>
              <span>Цвет: ${escapeHtml(row.product_color)}<br>Норма: 1 размерник на 1 изделие</span>
            </div>
            <div class="report-row-actions">
              <span class="status-chip ${isDone ? "" : "warn"}">${isDone ? "готово" : `${remaining} шт.`}</span>
              <span class="muted">${done} / ${planned}</span>
              <button type="button" class="small-button ${isDone ? "secondary" : ""}" data-admin-action="${isDone ? "reopen-size-marker" : "complete-size-marker"}" data-size-marker-id="${escapeHtml(row.id)}">${isDone ? "Вернуть" : "Выполнено"}</button>
            </div>
          </div>
        `;
      }).join("") : itemEmpty("Готовой продукции пока нет — задания на размерники появятся автоматически.");

      return `
        <div class="screen-head"><div><h2>Размерники</h2><p>Административное задание: 1 размерник на 1 готовое изделие. Сейчас группировка по изделию и цвету; размеры добавим следующим этапом.</p></div><div class="date">${openRows.length} открыто</div></div>
        ${renderAdminTabs()}
        <div class="kpi-grid">
          <div class="card kpi"><div class="kpi-top"><span>Группы</span><div class="kpi-ico">▦</div></div><strong>${rows.length}<small> шт</small></strong><span>Изделие + цвет</span></div>
          <div class="card kpi"><div class="kpi-top"><span>Всего размерников</span><div class="kpi-ico">✓</div></div><strong>${totalRequired}<small> шт</small></strong><span>По готовой продукции</span></div>
          <div class="card kpi warn"><div class="kpi-top"><span>Осталось сделать</span><div class="kpi-ico">!</div></div><strong>${totalRemaining}<small> шт</small></strong><span>Открытые задания</span></div>
        </div>
        <div class="section-title"><b>Задания</b><button type="button" data-admin-action="refresh">обновить</button></div>
        <div class="op-list">${rowsHtml}</div>
      `;
    }

    function renderAdminOperations(admin) {
      const control = admin && admin.production_control ? admin.production_control : {};
      const details = control.details || {};
      const tasks = Array.isArray(details.active_tasks) ? details.active_tasks : [];
      const employees = (admin && admin.employees ? admin.employees : [])
        .filter((employee) => employee.status === "active" && employee.position && employee.position !== "-");
      mainButton.textContent = "Обновить операции";
      mainButton.disabled = false;

      const rowsHtml = tasks.length ? tasks.map((task) => {
        const candidates = employees.filter((employee) => employee.position === task.position);
        const selectedId = task.assigned_employee_id && candidates.some((employee) => Number(employee.id) === Number(task.assigned_employee_id))
          ? String(task.assigned_employee_id)
          : (candidates[0] ? String(candidates[0].id) : "");
        const performerOptions = candidates.length
          ? candidates.map((employee) => `<option value="${escapeHtml(employee.id)}" ${String(employee.id) === selectedId ? "selected" : ""}>${escapeHtml(employee.full_name)}</option>`).join("")
          : `<option value="">Нет активных ${escapeHtml(task.position)}</option>`;
        return `
          <div class="card field-card">
            <div class="order-head"><div class="op-icon">${uiIcon("work")}</div><div><b>${escapeHtml(task.operation)}</b><span>#${escapeHtml(task.id)} · ${escapeHtml(task.product)} · ${escapeHtml(task.size)} · ${escapeHtml(task.color)}</span></div><span class="status-chip ${task.work_state === "blocked" ? "warn" : "gray"}">${escapeHtml(task.status_text || task.work_state || "В работе")}</span></div>
            <div class="detail-grid">
              <div class="detail-box"><span>Количество</span><strong>${escapeHtml(task.quantity)} шт</strong></div>
              <div class="detail-box"><span>Текущий исполнитель</span><strong>${escapeHtml(task.employee || "Не назначен")}</strong></div>
            </div>
            <div class="form-grid">
              <div class="field"><label>Исполнитель (${escapeHtml(task.position)})</label><select id="adminPerformer${escapeHtml(task.id)}">${performerOptions}</select></div>
              <div class="field"><label>Годное количество</label><input id="adminGoodQuantity${escapeHtml(task.id)}" type="number" min="0" max="${escapeHtml(task.quantity)}" value="${escapeHtml(task.quantity)}"></div>
            </div>
            <div class="button-row"><button type="button" class="small-button" data-admin-action="complete-route-operation" data-route-batch-id="${escapeHtml(task.id)}">Закрыть операцию</button><button type="button" class="small-button secondary" data-admin-action="refresh">Обновить</button></div>
          </div>
        `;
      }).join("") : itemEmpty("Активных операций сейчас нет.");

      return `
        <div class="screen-head"><div><h2>Операции</h2><p>Администратор может закрыть активную операцию и указать фактического исполнителя. Следующий этап создастся автоматически по маршруту.</p></div><div class="date">${tasks.length} активных</div></div>
        ${renderAdminTabs()}
        <div class="card field-card"><b>Важно</b><span class="muted">Для выбранного исполнителя должна быть открыта смена сегодня. Закрытие проведёт полное количество или введённое годное количество.</span></div>
        <div class="op-list">${rowsHtml}</div>
      `;
    }

    function renderAdminWarehouse(includeTabs = false) {
      const fabricRows = (getProduction().fabric_stock || []).filter((row) => Number(row.quantity || 0) > 0);
      const warehouseRows = getWarehouseStock().filter((row) => Number(row.quantity || 0) > 0);
      const receiptColors = getOrderColors();
      const semifinished = warehouseRows.filter((row) => row.item_type === "semifinished");
      const finished = warehouseRows.filter((row) => row.item_type === "finished");
      const totalQuantity = (rows) => rows.reduce((total, row) => total + Number(row.quantity || 0), 0);
      const finishedQuantity = totalQuantity(finished);
      const semifinishedQuantity = totalQuantity(semifinished);
      const materialsQuantity = totalQuantity(fabricRows);
      mainButton.textContent = "Обновить склад";
      mainButton.disabled = false;

      if ((!state.fabricReceiptColor || !receiptColors.includes(state.fabricReceiptColor)) && receiptColors.length) {
        state.fabricReceiptColor = receiptColors[0];
      }

      const receiptColorOptions = receiptColors.map((color) => `
        <option value="${escapeHtml(color)}" ${color === state.fabricReceiptColor ? "selected" : ""}>${escapeHtml(color)}</option>
      `).join("");
      const viewDefinitions = {
        finished: {label: "Склад готовой продукции", rows: finished, icon: "✓"},
        semifinished: {label: "Склад полуфабрикатов", rows: semifinished, icon: "▣"},
        materials: {label: "Склад материалов", rows: fabricRows, icon: "▦"},
      };

      if (state.warehouseView === "overview" || !viewDefinitions[state.warehouseView]) {
        state.warehouseView = "overview";
        return `
          <div class="screen-head"><div><h2>Управление складом</h2><p>Три самостоятельных склада: готовая продукция, полуфабрикаты и материалы.</p></div><div class="date">${warehouseRows.length + fabricRows.length} поз.</div></div>
          ${includeTabs ? renderAdminTabs() : ""}
          <div class="kpi-grid">
            <button type="button" class="card kpi good warehouse-category" data-warehouse-view="finished"><span class="kpi-top"><span>Склад готовой продукции</span><span class="kpi-ico">${uiIcon("quality")}</span></span><strong>${finished.length}<small> поз.</small></strong><span>${escapeHtml(String(finishedQuantity))} шт. в наличии</span></button>
            <button type="button" class="card kpi warehouse-category" data-warehouse-view="semifinished"><span class="kpi-top"><span>Склад полуфабрикатов</span><span class="kpi-ico">${uiIcon("layers")}</span></span><strong>${semifinished.length}<small> поз.</small></strong><span>${escapeHtml(String(semifinishedQuantity))} шт. в наличии</span></button>
            <button type="button" class="card kpi warehouse-category" data-warehouse-view="materials"><span class="kpi-top"><span>Склад материалов</span><span class="kpi-ico">${uiIcon("fabric")}</span></span><strong>${fabricRows.length}<small> поз.</small></strong><span>${escapeHtml(String(materialsQuantity))} рул. в наличии</span></button>
          </div>
          <div class="section-title"><b>Приход материалов</b><span>рулоны</span></div>
          <div class="card field-card">
            <div class="form-grid">
              <div class="field"><label>Материал</label><select id="fabricReceiptMaterial"><option value="Ткань" ${state.fabricReceiptMaterial === "Ткань" ? "selected" : ""}>Ткань</option></select></div>
              <div class="field"><label>Цвет</label><select id="fabricReceiptColor">${receiptColorOptions || `<option value="">Нет цветов</option>`}</select></div>
              <div class="field full"><label>Количество рулонов</label><input id="fabricReceiptQuantity" type="number" min="1" step="1" value="${escapeHtml(state.fabricReceiptQuantity)}" placeholder="0"></div>
            </div>
            <div class="button-row"><button class="small-button secondary" data-warehouse-action="refresh">Обновить</button><button class="small-button" data-warehouse-action="receipt">Добавить приход</button></div>
          </div>
        `;
      }

      const definition = viewDefinitions[state.warehouseView];
      const isMaterials = state.warehouseView === "materials";
      const productField = isMaterials ? "material_name" : "product_name";
      const uniqueValues = (rows, field) => [...new Set(rows.map((row) => String(row[field] || "")).filter(Boolean))]
        .sort((first, second) => first.localeCompare(second, "ru"));
      const optionHtml = (values, selected, allLabel, labelForValue = (value) => value) => `
        <option value="">${escapeHtml(allLabel)}</option>
        ${values.map((value) => `<option value="${escapeHtml(value)}" ${value === selected ? "selected" : ""}>${escapeHtml(labelForValue(value))}</option>`).join("")}
      `;
      const productValues = uniqueValues(definition.rows, productField);

      if (state.warehouseProductFilter && !productValues.includes(state.warehouseProductFilter)) {
        state.warehouseProductFilter = "";
      }

      const productRows = definition.rows.filter((row) => !state.warehouseProductFilter || row[productField] === state.warehouseProductFilter);
      const sizeValues = isMaterials ? [] : uniqueValues(productRows, "product_size");

      if (state.warehouseSizeFilter && !sizeValues.includes(state.warehouseSizeFilter)) {
        state.warehouseSizeFilter = "";
      }

      const sizeRows = productRows.filter((row) => isMaterials || !state.warehouseSizeFilter || row.product_size === state.warehouseSizeFilter);
      const colorValues = uniqueValues(sizeRows, "product_color");

      if (state.warehouseColorFilter && !colorValues.includes(state.warehouseColorFilter)) {
        state.warehouseColorFilter = "";
      }

      const filteredRows = sizeRows.filter((row) => !state.warehouseColorFilter || row.product_color === state.warehouseColorFilter);
      const colorLabel = (value) => {
        const row = definition.rows.find((item) => item.product_color === value);
        return row ? row.product_color_label || row.product_color : value;
      };
      const rowsHtml = filteredRows.length ? filteredRows.map((row) => isMaterials ? `
        <div class="card report-row"><div><b>${escapeHtml(row.material_name)}</b><span>${escapeHtml(row.product_color_label || row.product_color)}</span></div><div><span class="status-chip">${escapeHtml(row.quantity_text)} ${escapeHtml(row.unit === "рул" ? "рул." : row.unit)}</span><button type="button" class="small-button secondary" data-stock-adjust-kind="fabric" data-stock-adjust-id="${escapeHtml(row.id)}" data-stock-adjust-quantity="${escapeHtml(row.quantity)}" data-stock-adjust-label="${escapeHtml(`${row.material_name} · ${row.product_color_label || row.product_color}`)}">Изменить</button></div></div>
      ` : `
        <div class="card report-row"><div><b>${escapeHtml(row.product_name)}</b><span>${escapeHtml(row.stage_name)}<br>${escapeHtml(row.product_size)} · ${escapeHtml(row.product_color_label || row.product_color)}${state.warehouseView === "semifinished" ? `<br>Для: ${escapeHtml(row.ready_for_position)}` : ""}</span></div><div><span class="status-chip">${escapeHtml(row.quantity_text)} ${escapeHtml(row.unit)}</span><button type="button" class="small-button secondary" data-stock-adjust-kind="warehouse" data-stock-adjust-id="${escapeHtml(row.id)}" data-stock-adjust-quantity="${escapeHtml(row.quantity)}" data-stock-adjust-label="${escapeHtml(`${row.product_name} · ${row.product_size} · ${row.product_color_label || row.product_color}`)}">Изменить</button></div></div>
      `).join("") : itemEmpty("По выбранным фильтрам остатков нет.");

      return `
        <div class="screen-head"><div><h2>${escapeHtml(definition.label)}</h2><p>Остатки на складе.</p></div><div class="date">${filteredRows.length} из ${definition.rows.length}</div></div>
        <div class="card field-card">
          <div class="form-grid">
            <div class="field ${isMaterials ? "" : "full"}"><label>${isMaterials ? "Материал" : "Номенклатура изделия"}</label><select id="warehouseProductFilter">${optionHtml(productValues, state.warehouseProductFilter, isMaterials ? "Все материалы" : "Все изделия")}</select></div>
            ${isMaterials ? "" : `<div class="field"><label>Размер</label><select id="warehouseSizeFilter">${optionHtml(sizeValues, state.warehouseSizeFilter, "Все размеры")}</select></div>`}
            <div class="field"><label>Цвет</label><select id="warehouseColorFilter">${optionHtml(colorValues, state.warehouseColorFilter, "Все цвета", colorLabel)}</select></div>
          </div>
          <div class="button-row"><button class="small-button secondary" data-warehouse-action="overview">К разделам</button><button class="small-button" data-warehouse-action="clear-filters">Сбросить фильтры</button></div>
        </div>
        <div class="section-title"><b>Остатки</b><span>${filteredRows.length}</span></div>
        <div class="op-list">${rowsHtml}</div>
      `;
    }

    function wmsLocationMap() {
      return new Map((state.wmsData.locations || []).map((location) => [Number(location.id), location]));
    }

    function wmsLocationByCode(code) {
      const normalized = String(code || "").replace(/^LOC:/i, "").trim().toUpperCase();
      return (state.wmsData.locations || []).find((location) => String(location.code || "").toUpperCase() === normalized) || null;
    }

    function wmsLocationByScan(value) {
      const scanned = String(value || "").trim().toUpperCase();
      const normalizedCode = scanned.replace(/^LOC:/i, "").trim();
      return (state.wmsData.locations || []).find((location) =>
        String(location.code || "").trim().toUpperCase() === normalizedCode
        || String(location.barcode || "").trim().toUpperCase() === scanned
      ) || null;
    }

    function wmsStockAtLocation(code) {
      const location = wmsLocationByCode(code);
      if (!location) return [];
      return (state.wmsData.stock || []).filter((row) =>
        Number(row.location_id) === Number(location.id)
        && row.item_state === "SELLABLE"
        && Number(row.quantity || 0) > 0
      );
    }

    function wmsStockFilterDefinitions() {
      return [
        {id: "finished", label: "Готовая продукция", shortLabel: "Готовая продукция", itemType: "finished", unit: "шт."},
        {id: "semifinished", label: "Полуфабрикаты", shortLabel: "Полуфабрикаты", itemType: "semifinished", unit: "шт."},
        {id: "material", label: "Материалы", shortLabel: "Материалы", itemType: "material", unit: "рул."},
      ];
    }

    function wmsCurrentStockFilter() {
      const definitions = wmsStockFilterDefinitions();
      return definitions.find((definition) => definition.id === state.wmsStockFilter) || definitions[0];
    }

    /* The imported 102 physical cells are the finished-goods warehouse.
       Semi-finished goods and materials have their own stock categories, but
       their address cells have not been created yet.  Do not show the finished
       goods layout there as if those were their empty cells. */
    function wmsHasAddressMapForCurrentStock() {
      return wmsCurrentStockFilter().id === "finished";
    }

    function wmsFilteredStockByType() {
      const definition = wmsCurrentStockFilter();
      return (state.wmsData.stock || []).filter((row) => row.product_key && row.product_key.item_type === definition.itemType);
    }

    function wmsStockFilterOptions(rows, field) {
      return [...new Set(rows.map((row) => String((row.product_key || {})[field] || "")).filter(Boolean))]
        .sort((first, second) => first.localeCompare(second, "ru"));
    }

    function wmsFilteredStock() {
      const typeRows = wmsFilteredStockByType();
      const productValues = wmsStockFilterOptions(typeRows, "product_name");
      if (state.wmsStockProductFilter && !productValues.includes(state.wmsStockProductFilter)) state.wmsStockProductFilter = "";
      const productRows = typeRows.filter((row) => !state.wmsStockProductFilter || row.product_key.product_name === state.wmsStockProductFilter);
      const sizeValues = wmsCurrentStockFilter().itemType === "material" ? [] : wmsStockFilterOptions(productRows, "product_size");
      if (state.wmsStockSizeFilter && !sizeValues.includes(state.wmsStockSizeFilter)) state.wmsStockSizeFilter = "";
      const sizeRows = productRows.filter((row) => wmsCurrentStockFilter().itemType === "material" || !state.wmsStockSizeFilter || row.product_key.product_size === state.wmsStockSizeFilter);
      const colorValues = wmsStockFilterOptions(sizeRows, "product_color");
      if (state.wmsStockColorFilter && !colorValues.includes(state.wmsStockColorFilter)) state.wmsStockColorFilter = "";
      return sizeRows.filter((row) => !state.wmsStockColorFilter || row.product_key.product_color === state.wmsStockColorFilter);
    }

    function wmsFilteredStockAtLocation(code, stockRows = wmsFilteredStock()) {
      const location = wmsLocationByCode(code);
      if (!location) return [];
      return stockRows.filter((row) =>
        Number(row.location_id) === Number(location.id)
        && row.item_state === "SELLABLE"
        && Number(row.quantity || 0) > 0
      );
    }

    function wmsStockFilterValues() {
      const typeRows = wmsFilteredStockByType();
      const productRows = typeRows.filter((row) => !state.wmsStockProductFilter || row.product_key.product_name === state.wmsStockProductFilter);
      const sizeValues = wmsCurrentStockFilter().itemType === "material" ? [] : wmsStockFilterOptions(productRows, "product_size");
      const sizeRows = productRows.filter((row) => wmsCurrentStockFilter().itemType === "material" || !state.wmsStockSizeFilter || row.product_key.product_size === state.wmsStockSizeFilter);
      return {
        productValues: wmsStockFilterOptions(typeRows, "product_name"),
        sizeValues,
        colorValues: wmsStockFilterOptions(sizeRows, "product_color"),
      };
    }

    function wmsFilterOptionHtml(values, selected, allLabel, labelForValue = (value) => value) {
      return `<option value="">${escapeHtml(allLabel)}</option>${values.map((value) => `<option value="${escapeHtml(value)}" ${value === selected ? "selected" : ""}>${escapeHtml(labelForValue(value))}</option>`).join("")}`;
    }

    function syncWmsStockFilters() {
      const filter = document.getElementById("wmsStockFilter");
      const product = document.getElementById("wmsStockProductFilter");
      const size = document.getElementById("wmsStockSizeFilter");
      const color = document.getElementById("wmsStockColorFilter");
      if (filter) state.wmsStockFilter = filter.value;
      if (product) state.wmsStockProductFilter = product.value;
      if (size) state.wmsStockSizeFilter = size.value;
      if (color) state.wmsStockColorFilter = color.value;
    }

    function resetWmsStockFilters() {
      state.wmsStockProductFilter = "";
      state.wmsStockSizeFilter = "";
      state.wmsStockColorFilter = "";
      state.wmsSelectedLocationId = "";
    }

    function wmsReceivingStock() {
      return wmsStockAtLocation("RECEIVE-01");
    }

    function wmsReceivingMaterials() {
      return wmsReceivingStock().filter((row) => row.product_key && row.product_key.item_type === "material");
    }

    function wmsProductKeysEqual(first, second) {
      const keys = ["item_type", "product_name", "product_size", "product_color", "stage_name", "ready_for_position"];
      return keys.every((key) => String((first || {})[key] || "") === String((second || {})[key] || ""));
    }

    function wmsFindScannedStock(locationCode, productKey) {
      return wmsStockAtLocation(locationCode).find((row) => wmsProductKeysEqual(row.product_key, productKey)) || null;
    }

    function renderWmsGuidedScanner(locationField, locationCode, productDetected, locationLabel) {
      const locationWasScanned = locationField === "from_location" ? state.wmsDraft.fromLocationScanned : state.wmsDraft.toLocationScanned;
      const locationReady = Boolean(locationWasScanned && locationCode && wmsLocationByCode(locationCode));
      const expectedField = locationReady ? "product" : locationField;
      const expectedText = locationReady ? "Отсканируйте товар" : `Отсканируйте ${locationLabel.toLowerCase()}`;
      return `
        <div class="card field-card">
          <label>Порядок сканирования</label>
          <div class="op-list">
            <div class="report-row"><div><b>1. ${escapeHtml(locationLabel)}</b><span>${locationReady ? escapeHtml(locationCode) : "Наведите сканер на штрихкод ячейки"}</span></div><span class="status-chip ${locationReady ? "" : "gray"}">${locationReady ? "✓" : "1"}</span></div>
            <div class="report-row"><div><b>2. Товар</b><span>${productDetected ? escapeHtml(wmsProductLabel(wmsProductKey(state.wmsDraft))) : "Отсканируйте штрихкод изделия"}</span></div><span class="status-chip ${productDetected ? "" : "gray"}">${productDetected ? "✓" : "2"}</span></div>
            <div class="report-row"><div><b>3. Количество</b><span>Введите количество и подтвердите операцию</span></div><span class="status-chip gray">3</span></div>
          </div>
          <div class="field full"><label>Сканер ТСД</label><input id="wmsHardwareScannerInput" class="wms-hardware-scanner-input" data-wms-hardware-field="${expectedField}" inputmode="none" autocomplete="off" placeholder="${escapeHtml(expectedText)}" autofocus></div>
          <div class="button-row"><button class="small-button" data-wms-scan="${expectedField}">📷 ${escapeHtml(expectedText)}</button></div>
        </div>
      `;
    }

    function renderWmsLocationContents(code) {
      if (!code) return "";
      const location = wmsLocationByCode(code);
      if (!location) return `<div class="card field-card">${itemEmpty(`Ячейка ${code} не найдена.`)}</div>`;
      const rows = wmsStockAtLocation(code);
      return `
        <div class="section-title"><b>Содержимое ${escapeHtml(location.code)}</b><span>${rows.length} поз.</span></div>
        <div class="op-list">${rows.length ? rows.map((row) => {
          const available = Math.max(0, Number(row.quantity || 0) - Number(row.reserved_quantity || 0));
          return `<div class="card report-row"><div><b>${escapeHtml(wmsProductLabel(row.product_key))}</b><span>Доступно ${escapeHtml(available)} · резерв ${escapeHtml(row.reserved_quantity || 0)}</span></div><span class="status-chip">${escapeHtml(row.quantity)} ${escapeHtml(row.unit || "шт")}</span></div>`;
        }).join("") : itemEmpty("Ячейка пустая.")}</div>
      `;
    }

    function wmsLocationLabel(locationId) {
      if (!locationId) return "—";
      const location = wmsLocationMap().get(Number(locationId));
      return location ? location.code : `Ячейка #${locationId}`;
    }

    function wmsProductLabel(productKey) {
      const product = productKey || {};
      if (product.item_type === "material") {
        return [product.product_name, product.product_color].filter(Boolean).join(" · ") || "Материал";
      }
      return [product.product_name, product.product_size, product.product_color].filter(Boolean).join(" · ") || "Товар";
    }

    function wmsMovementLabel(type) {
      return ({
        receive: "Приёмка",
        production_receipt: "Приёмка",
        material_receipt: "Приёмка материалов",
        putaway: "Размещение",
        transfer: "Перемещение",
        pick: "Выдача из ячейки",
        inventory: "Инвентаризация",
        count: "Инвентаризация",
        inventory_adjustment: "Корректировка",
        scrap: "Списание",
      })[type] || type || "Операция";
    }

    function wmsMovementTime(value) {
      if (!value) return "";
      const date = new Date(value);
      if (Number.isNaN(date.getTime())) return String(value);
      return date.toLocaleString("ru-RU", {day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit"});
    }

    function renderWmsDataNotice() {
      if (state.wmsData.loading && !state.wmsData.loaded) {
        return `<div class="card field-card">${itemEmpty("Загружаем остатки и движения…")}</div>`;
      }
      if (state.wmsData.error) {
        return `<div class="card field-card"><div class="task-note"><b>Не удалось обновить склад</b><br>${escapeHtml(state.wmsData.error)}</div><div class="button-row"><button class="small-button" data-wms-action="refresh">Повторить</button></div></div>`;
      }
      return "";
    }

    function renderWmsOverview() {
      const stock = state.wmsData.stock || [];
      const locations = state.wmsData.locations || [];
      const movements = state.wmsData.movements || [];
      const total = stock.reduce((sum, row) => sum + Number(row.quantity || 0), 0);
      const reserved = stock.reduce((sum, row) => sum + Number(row.reserved_quantity || 0), 0);
      const activeLocations = locations.filter((row) => row.status === "active").length;
      const occupiedLocations = locations.filter((row) => wmsLocationSummary(row).quantity > 0).length;
      const receiving = wmsReceivingStock().concat(wmsReceivingMaterials());
      const unplaced = stock.filter((row) => !row.location_id && Number(row.quantity || 0) > 0);
      const alerts = [
        ...(unplaced.length ? [{level: "critical", title: "Товар без ячейки", text: `${unplaced.length} поз. ожидают размещения`, view: "putaway"}] : []),
        ...(receiving.length ? [{level: "warning", title: "Ожидает приёмки", text: `${receiving.length} поз. находятся в зоне приёмки`, view: "receive"}] : []),
        ...(reserved > 0 ? [{level: "info", title: "Есть резерв", text: `${reserved} ед. защищены от выдачи`, view: "stock"}] : []),
      ];
      mainButton.textContent = state.wmsData.loading ? "Обновляем…" : "Обновить склад";
      mainButton.disabled = state.wmsData.loading;
      mount.innerHTML = `
        <div class="screen-head"><div><h2>Обзор склада</h2><p>Ключевые показатели и текущее состояние склада.</p></div><div class="date">${state.wmsData.loaded ? "данные загружены" : "загрузка"}</div></div>
        ${renderWmsDataNotice()}
        <div class="kpi-grid">
          <button type="button" class="card kpi warehouse-category" data-wms-view="stock"><span class="kpi-top"><span>Остатки SKU</span><span class="kpi-ico">▤</span></span><strong>${stock.length}<small> поз.</small></strong><span>${escapeHtml(total)} ед. на складе</span></button>
          <button type="button" class="card kpi warehouse-category" data-wms-view="stock"><span class="kpi-top"><span>Товары на складе</span><span class="kpi-ico">□</span></span><strong>${escapeHtml(total)}<small> ед.</small></strong><span>Резерв: ${escapeHtml(reserved)} ед.</span></button>
          <button type="button" class="card kpi warehouse-category" data-wms-view="map"><span class="kpi-top"><span>Занято ячеек</span><span class="kpi-ico">▦</span></span><strong>${occupiedLocations}<small> / ${activeLocations}</small></strong><span>${activeLocations ? Math.round((occupiedLocations / activeLocations) * 100) : 0}% действующих ячеек</span></button>
          <button type="button" class="card kpi warehouse-category" data-wms-view="receive"><span class="kpi-top"><span>Ожидает приёмки</span><span class="kpi-ico">↓</span></span><strong>${receiving.length}<small> поз.</small></strong><span>Требуют проверки и размещения</span></button>
          <button type="button" class="card kpi warehouse-category" data-wms-view="movements"><span class="kpi-top"><span>Движения</span><span class="kpi-ico">⇄</span></span><strong>${movements.length}<small> зап.</small></strong><span>Последние операции</span></button>
        </div>
        ${alerts.length ? `<div class="section-title"><b>Требуют внимания</b><span>${alerts.length}</span></div><div class="op-list">${alerts.map((alert) => `<button type="button" class="card report-row warehouse-v2-alert ${alert.level === "critical" ? "critical" : ""}" data-wms-view="${alert.view}"><div><b>${escapeHtml(alert.title)}</b><span>${escapeHtml(alert.text)}</span></div><span class="status-chip ${alert.level === "warning" ? "warn" : ""}">${alert.level === "critical" ? "критично" : alert.level === "warning" ? "внимание" : "инфо"}</span></button>`).join("")}</div>` : ""}
        <div class="section-title"><b>Быстрые действия</b><span>сканер</span></div>
        <div class="warehouse-v2-actions">
          <button type="button" class="card summary-card clickable" data-wms-view="products"><span>Товары Ozon</span><strong>▤</strong><small>Артикулы и штрихкоды</small></button>
          <button type="button" class="card summary-card clickable" data-wms-view="receive"><span>Приёмка</span><strong>↓</strong><small>Проверить поступление</small></button>
          <button type="button" class="card summary-card clickable" data-wms-view="map"><span>Карта склада</span><strong>▦</strong><small>Открыть ячейку</small></button>
          <button type="button" class="card summary-card clickable" data-wms-view="putaway"><span>Размещение</span><strong>→</strong><small>Положить в ячейку</small></button>
          <button type="button" class="card summary-card clickable" data-wms-view="pick"><span>Выдача</span><strong>↑</strong><small>Забрать из ячейки</small></button>
          <button type="button" class="card summary-card clickable" data-wms-view="transfer"><span>Перемещение</span><strong>⇄</strong><small>Между ячейками</small></button>
          <button type="button" class="card summary-card clickable" data-wms-view="inventory"><span>Инвентаризация</span><strong>≡</strong><small>Пересчитать ячейку</small></button>
          <button type="button" class="card summary-card clickable" data-wms-view="reports"><span>Отчёты</span><strong>↧</strong><small>Остатки и движения</small></button>
        </div>
        <div class="section-title"><b>Последние движения</b><button type="button" data-wms-view="movements">показать все</button></div>
        <div class="op-list">${movements.length ? movements.slice(0, 4).map((movement) => `
          <div class="card report-row"><div><b>${escapeHtml(wmsMovementLabel(movement.movement_type))}</b><span>${escapeHtml(wmsProductLabel(movement.product_key))}<br>${escapeHtml(wmsLocationLabel(movement.from_location_id))} → ${escapeHtml(wmsLocationLabel(movement.to_location_id))}</span></div><div><span class="status-chip">${escapeHtml(movement.quantity)} шт.</span><small>${escapeHtml(wmsMovementTime(movement.occurred_at))}</small></div></div>
        `).join("") : itemEmpty("Складских движений пока нет.")}</div>
      `;
    }

    function renderWmsMore() {
      mainButton.textContent = "Обновить склад";
      mainButton.disabled = state.wmsData.loading;
      mount.innerHTML = `
        <div class="screen-head"><div><h2>Складские операции</h2><p>Контроль остатков, пересчёт и специальные операции.</p></div></div>
        ${renderWmsDataNotice()}
        <div class="kpi-grid">
          <button type="button" class="card summary-card clickable" data-wms-view="lookup"><span>Проверка товара</span><strong>⌕</strong><small>Штрихкод · ячейки · остаток</small></button>
          <button type="button" class="card summary-card clickable" data-wms-view="products"><span>Товары Ozon</span><strong>▤</strong><small>Артикулы и штрихкоды</small></button>
          <button type="button" class="card summary-card clickable" data-wms-view="transfer"><span>Перемещение</span><strong>⇄</strong><small>Между ячейками</small></button>
          <button type="button" class="card summary-card clickable" data-wms-view="stock"><span>Остатки</span><strong>▤</strong><small>По адресным ячейкам</small></button>
          <button type="button" class="card summary-card clickable" data-wms-view="movements"><span>История</span><strong>⇄</strong><small>Все движения</small></button>
          <button type="button" class="card summary-card clickable" data-wms-view="inventory"><span>Инвентаризация</span><strong>≡</strong><small>Фактический пересчёт</small></button>
          <button type="button" class="card summary-card clickable" data-wms-view="scrap"><span>Списание</span><strong>×</strong><small>Брак и карантин</small></button>
        </div>
      `;
    }

    function renderWmsLookup() {
      const lookup = state.wmsLookup || {barcode: "", productKey: null, error: ""};
      const productKey = lookup.productKey;
      const rows = productKey ? (state.wmsData.stock || []).filter((row) =>
        row.product_key && wmsProductKeysEqual(row.product_key, productKey) && Number(row.quantity || 0) > 0
      ) : [];
      const total = rows.reduce((sum, row) => sum + Number(row.quantity || 0), 0);
      const reserved = rows.reduce((sum, row) => sum + Number(row.reserved_quantity || 0), 0);
      mainButton.textContent = "Обновить склад";
      mainButton.disabled = state.wmsData.loading;
      mount.innerHTML = `
        <div class="screen-head"><div><h2>Проверка товара</h2><p>Сканируйте штрихкод: покажем товар, все ячейки и фактический остаток.</p></div><div class="date">ТСД</div></div>
        ${renderWmsDataNotice()}
        <div class="card field-card">
          <div class="field full"><label>Сканер ТСД</label><input id="wmsHardwareScannerInput" class="wms-hardware-scanner-input" data-wms-hardware-field="lookup_product" inputmode="none" autocomplete="off" placeholder="Отсканируйте товар" autofocus></div>
          <div class="button-row"><button type="button" class="small-button" data-wms-scan="lookup_product">📷 Сканировать товар</button></div>
          <div class="task-note">После каждого считывания поле очищается и снова готово к следующему товару.</div>
        </div>
        ${lookup.error ? `<div class="card field-card"><div class="task-note"><b>Товар не найден</b><br>${escapeHtml(lookup.error)}<br>Если это новый товар, сначала один раз привяжите его штрихкод в приёмке.</div></div>` : ""}
        ${productKey ? `<div class="card field-card"><div class="section-title"><b>${escapeHtml(wmsProductLabel(productKey))}</b><span class="status-chip">найден</span></div><div class="detail-grid"><div class="detail-box"><span>Штрихкод</span><strong>${escapeHtml(lookup.barcode || "—")}</strong></div><div class="detail-box"><span>Всего на складе</span><strong>${escapeHtml(total)} шт.</strong></div><div class="detail-box"><span>В резерве</span><strong>${escapeHtml(reserved)} шт.</strong></div><div class="detail-box"><span>Доступно</span><strong>${escapeHtml(Math.max(0, total - reserved))} шт.</strong></div></div></div><div class="section-title"><b>Ячейки хранения</b><span>${rows.length}</span></div><div class="op-list">${rows.length ? rows.map((row) => { const available = Math.max(0, Number(row.quantity || 0) - Number(row.reserved_quantity || 0)); return `<button type="button" class="card report-row marketplace-clickable" data-wms-cell-id="${escapeHtml(row.location_id)}"><div><b>${escapeHtml(wmsLocationLabel(row.location_id))}</b><span>Доступно ${escapeHtml(available)} · резерв ${escapeHtml(row.reserved_quantity || 0)}</span></div><span class="status-chip">${escapeHtml(row.quantity)} ${escapeHtml(row.unit || "шт")}</span></button>`; }).join("") : itemEmpty("Товар распознан, но адресных остатков в ячейках пока нет.")}</div>` : itemEmpty("Наведите ТСД на штрихкод товара.")}
      `;
      focusWmsHardwareScanner();
    }

    function wmsPhysicalLocationParts(location) {
      const match = String((location || {}).code || "").toUpperCase().match(/^Z(\\d+)-S(\\d+)-P(\\d+)-(\\d+)$/);
      if (!match) return null;
      return {zone: Number(match[1]), section: Number(match[2]), level: Number(match[3]), position: Number(match[4])};
    }

    function wmsLocationDisplayName(location) {
      if (!location) return "Ячейка";
      return String(location.name_ru || "").trim() || `Ячейка ${location.code || ""}`.trim();
    }

    function wmsLocationSummary(location, stockRows = wmsFilteredStock()) {
      const rows = location ? wmsFilteredStockAtLocation(location.code, stockRows) : [];
      const quantity = rows.reduce((sum, row) => sum + Number(row.quantity || 0), 0);
      const reserved = rows.reduce((sum, row) => sum + Number(row.reserved_quantity || 0), 0);
      const status = location && location.status !== "active" ? "blocked" : (reserved > 0 ? "reserved" : (quantity > 0 ? "occupied" : "empty"));
      return {rows, quantity, reserved, available: Math.max(0, quantity - reserved), status};
    }

    function renderWmsMapCell(location, parts, sectionStart, stockRows, gridStyle = "") {
      const summary = wmsLocationSummary(location, stockRows);
      const selected = Number(state.wmsSelectedLocationId || 0) === Number(location.id);
      const search = String(state.wmsMapSearch || "").trim().toLocaleLowerCase("ru");
      const productText = summary.rows.map((row) => wmsProductLabel(row.product_key)).join(" ").toLocaleLowerCase("ru");
      const searchable = `${location.code || ""} ${location.name_ru || ""} ${location.barcode || ""} ${productText}`.toLocaleLowerCase("ru");
      const statusMatches = state.wmsMapStatusFilter === "all" || state.wmsMapStatusFilter === summary.status;
      const searchMatches = !search || searchable.includes(search);
      const statusText = summary.status === "blocked" ? "Заблокирована" : (summary.quantity ? `${summary.quantity} ${wmsCurrentStockFilter().unit}` : "Свободна");
      const fullName = wmsLocationDisplayName(location);
      return `<button type="button" class="wms-cell wms-cell-${summary.status} ${(!statusMatches || !searchMatches) ? "wms-cell-filtered" : ""} ${sectionStart ? "wms-cell-section-start" : ""}" ${gridStyle} data-wms-cell-id="${escapeHtml(location.id)}" title="${escapeHtml(fullName)}" aria-label="${escapeHtml(fullName)}${selected ? ", выбрана" : ""}"><strong>${escapeHtml(location.code)}</strong><small>${escapeHtml(statusText)}</small></button>`;
    }

    function renderWmsLocationDetail(stockRows = wmsFilteredStock()) {
      const location = (state.wmsData.locations || []).find((row) => Number(row.id) === Number(state.wmsSelectedLocationId || 0));
      if (!location) return `<div class="card field-card">${itemEmpty("Нажмите на ячейку, чтобы увидеть её содержимое и операции.")}</div>`;
      const parts = wmsPhysicalLocationParts(location);
      const summary = wmsLocationSummary(location, stockRows);
      const movements = (state.wmsData.movements || []).filter((movement) => Number(movement.from_location_id) === Number(location.id) || Number(movement.to_location_id) === Number(location.id)).slice(0, 6);
      const statusLabel = summary.status === "blocked" ? "Заблокирована" : (summary.status === "empty" ? "Свободна" : "Занята");
      return `<div class="card field-card wms-location-detail">
        <div class="section-title"><b>${escapeHtml(wmsLocationDisplayName(location))}</b><span>${escapeHtml(statusLabel)}</span></div>
        <div class="detail-grid">
          <div class="detail-box"><span>Код ячейки</span><strong>${escapeHtml(location.code || "—")}</strong></div>
          <div class="detail-box"><span>Зона</span><strong>${escapeHtml(parts ? `Зона №${parts.zone}` : (location.name_ru || "-"))}</strong></div>
          <div class="detail-box"><span>Штрихкод</span><strong>${escapeHtml(location.barcode || location.code)}</strong></div>
          <div class="detail-box"><span>Всего</span><strong>${escapeHtml(summary.quantity)} ${escapeHtml(wmsCurrentStockFilter().unit)}</strong></div>
          <div class="detail-box"><span>Доступно / резерв</span><strong>${escapeHtml(summary.available)} / ${escapeHtml(summary.reserved)}</strong></div>
        </div>
        <div class="button-row"><button type="button" class="small-button" data-wms-cell-action="putaway" data-wms-cell-code="${escapeHtml(location.code)}">Разместить сюда</button><button type="button" class="small-button secondary" data-wms-cell-action="pick" data-wms-cell-code="${escapeHtml(location.code)}">Выдать из ячейки</button></div>
        <div class="section-title"><b>Содержимое</b><span>${summary.rows.length} поз.</span></div>
        <div class="wms-location-products">${summary.rows.length ? summary.rows.map((row) => `<div class="report-row"><div><b>${escapeHtml(wmsProductLabel(row.product_key))}</b><span>Доступно ${escapeHtml(Math.max(0, Number(row.quantity || 0) - Number(row.reserved_quantity || 0)))} · резерв ${escapeHtml(row.reserved_quantity || 0)}</span></div><span class="status-chip">${escapeHtml(row.quantity)} ${escapeHtml(row.unit || "шт")}</span></div>`).join("") : itemEmpty("Ячейка свободна.")}</div>
        <div class="section-title"><b>История ячейки</b><span>${movements.length}</span></div>
        <div class="wms-location-products">${movements.length ? movements.map((movement) => `<div class="report-row"><div><b>${escapeHtml(wmsMovementLabel(movement.movement_type))}</b><span>${escapeHtml(wmsProductLabel(movement.product_key))}<br>${escapeHtml(wmsMovementTime(movement.occurred_at))}</span></div><span class="status-chip gray">${escapeHtml(movement.quantity)} шт.</span></div>`).join("") : itemEmpty("Движений по ячейке пока нет.")}</div>
      </div>`;
    }

    function renderWmsWarehouseMap() {
      const stockRows = arguments.length ? arguments[0] : wmsFilteredStock();
      if (!wmsHasAddressMapForCurrentStock()) {
        state.wmsSelectedLocationId = "";
        const definition = wmsCurrentStockFilter();
        return `<div class="card field-card"><div class="task-note"><b>Адресные ячейки ещё не заведены</b><br>Созданная карта из 102 ячеек относится к складу готовой продукции. Для раздела «${escapeHtml(definition.label)}» карта не показывается, чтобы не создавать ложных пустых ячеек.</div></div>`;
      }
      const locations = (state.wmsData.locations || []).map((location) => ({location, parts: wmsPhysicalLocationParts(location)})).filter((row) => row.parts);
      if (!locations.length) return `<div class="card field-card">${itemEmpty("Физические ячейки ещё не загружены.")}</div>`;
      const zones = [...new Set(locations.map((row) => row.parts.zone))].sort((a, b) => a - b);
      return `<div class="wms-map-shell">
        <div class="section-title"><b>Карта адресного хранения</b><span>${locations.length} яч.</span></div>
        <div class="wms-map-legend"><span><i></i> свободна</span><span class="occupied"><i></i> занята</span><span class="reserved"><i></i> есть резерв</span><span class="blocked"><i></i> заблокирована</span></div>
        <div class="wms-map-scroll">${zones.map((zone) => {
          const zoneRows = locations.filter((row) => row.parts.zone === zone);
          const maxSection = Math.max(...zoneRows.map((row) => row.parts.section));
          const maxLevel = Math.max(...zoneRows.map((row) => row.parts.level));
          const maxPosition = Math.max(...zoneRows.map((row) => row.parts.position));
          const zoneQuantity = zoneRows.reduce((sum, row) => sum + wmsLocationSummary(row.location, stockRows).quantity, 0);
          /* Only existing locations are rendered. Their coordinates are read
             from the already established Z/S/P code; no UI location is made. */
          const cells = zoneRows.slice().sort((a, b) => (b.parts.level - a.parts.level) || (a.parts.section - b.parts.section) || (a.parts.position - b.parts.position)).map((row) => {
            const column = ((row.parts.section - 1) * maxPosition) + row.parts.position;
            const visualRow = maxLevel - row.parts.level + 1;
            return renderWmsMapCell(row.location, row.parts, row.parts.section > 1 && row.parts.position === 1, stockRows, `style="grid-column:${column};grid-row:${visualRow}"`);
          });
          return `<section class="wms-zone-map"><div class="wms-zone-map-head"><b>Зона №${zone}</b><span>${zoneRows.length} ячеек · ${zoneQuantity} ${escapeHtml(wmsCurrentStockFilter().unit)}</span></div><div class="wms-map-grid" style="grid-template-columns:repeat(${maxSection * maxPosition},minmax(62px,1fr));grid-template-rows:repeat(${maxLevel},minmax(64px,auto))">${cells.join("")}</div></section>`;
        }).join("")}</div>
        ${renderWmsLocationDetail(stockRows)}
      </div>`;
    }

    function renderWmsMapView() {
      /* The map screen always opens the existing finished-goods layout. */
      state.wmsStockFilter = "finished";
      const locations = state.wmsData.locations || [];
      const stock = wmsFilteredStock();
      const byStatus = locations.reduce((result, location) => {
        const status = wmsLocationSummary(location, stock).status;
        result[status] = (result[status] || 0) + 1;
        return result;
      }, {});
      mainButton.textContent = "Обновить карту";
      mainButton.disabled = state.wmsData.loading;
      mount.innerHTML = `
        <div class="screen-head"><div><h2>Размещение · карта готовой продукции</h2><p>Фактические ячейки, коды и штрихкоды сохранены без изменений. Нажмите на ячейку, чтобы открыть её содержимое.</p></div><div class="date">${locations.length} яч.</div></div>
        ${renderWmsDataNotice()}
        <div class="card field-card wms-stock-filter-card"><div class="warehouse-v2-filter-row">
          <div class="field"><label>Найти ячейку, товар или штрихкод</label><input id="wmsMapSearch" value="${escapeHtml(state.wmsMapSearch || "")}" placeholder="Например Z1-S1-P1-1"></div>
          <div class="field"><label>Статус ячейки</label><select id="wmsMapStatusFilter"><option value="all" ${state.wmsMapStatusFilter === "all" ? "selected" : ""}>Все статусы</option><option value="empty" ${state.wmsMapStatusFilter === "empty" ? "selected" : ""}>Свободна (${byStatus.empty || 0})</option><option value="occupied" ${state.wmsMapStatusFilter === "occupied" ? "selected" : ""}>Занята (${byStatus.occupied || 0})</option><option value="reserved" ${state.wmsMapStatusFilter === "reserved" ? "selected" : ""}>Есть резерв (${byStatus.reserved || 0})</option><option value="blocked" ${state.wmsMapStatusFilter === "blocked" ? "selected" : ""}>Заблокирована (${byStatus.blocked || 0})</option></select></div>
          <button type="button" class="small-button" data-wms-map-action="apply">Показать</button>
        </div></div>
        ${renderWmsWarehouseMap(stock)}
      `;
    }

    function renderWmsReports() {
      const stock = state.wmsData.stock || [];
      const movements = state.wmsData.movements || [];
      mainButton.textContent = "Обновить отчёты";
      mainButton.disabled = state.wmsData.loading;
      mount.innerHTML = `
        <div class="screen-head"><div><h2>Складские отчёты</h2><p>Остатки и журнал движений по действующим ячейкам.</p></div><div class="date">${stock.length + movements.length} строк</div></div>
        ${renderWmsDataNotice()}
        <div class="op-list">
          <div class="card report-row"><div><b>Остатки по ячейкам</b><span>Товар, ячейка, количество, резерв и доступно</span></div><button type="button" class="small-button" data-wms-report="stock">Скачать CSV</button></div>
          <div class="card report-row"><div><b>История движений</b><span>Дата, операция, товар, количество, исходная и целевая ячейки</span></div><button type="button" class="small-button" data-wms-report="movements">Скачать CSV</button></div>
        </div>
        <div class="card field-card"><div class="task-note"><b>Важно</b><br>Выгрузки формируются из текущих складских данных и не меняют остатки, ячейки или историю операций.</div></div>
      `;
    }

    function renderWmsProducts() {
      const catalog = state.wmsCatalog || {loading: false, loaded: false, error: "", products: [], lastSyncAt: ""};
      const search = String(state.wmsCatalogSearch || "").trim().toLocaleLowerCase("ru");
      const searchedProducts = (catalog.products || []).filter((product) => {
        if (!search) return true;
        return [product.offer_id, product.name, product.color, product.size, product.barcode, product.sku]
          .some((value) => String(value || "").toLocaleLowerCase("ru").includes(search));
      });
      const groupMap = new Map();
      searchedProducts.forEach((product) => {
        const key = String(product.group_key || "other");
        const group = groupMap.get(key) || {key, name: product.group_name || "Прочие товары", products: []};
        group.products.push(product);
        groupMap.set(key, group);
      });
      const groups = [...groupMap.values()].sort((first, second) => first.name.localeCompare(second.name, "ru"));
      if (state.wmsCatalogGroup && !groupMap.has(state.wmsCatalogGroup)) state.wmsCatalogGroup = "";
      const selectedGroup = state.wmsCatalogGroup ? groupMap.get(state.wmsCatalogGroup) : null;
      const products = selectedGroup ? selectedGroup.products : searchedProducts;
      mainButton.textContent = catalog.loading ? "Обновляем…" : "Обновить товары";
      mainButton.disabled = catalog.loading;
      const notice = catalog.loading && !catalog.loaded
        ? `<div class="card field-card">${itemEmpty("Загружаем каталог Ozon…")}</div>`
        : (catalog.error ? `<div class="card field-card"><div class="task-note"><b>Не удалось загрузить товары Ozon</b><br>${escapeHtml(catalog.error)}</div><div class="button-row"><button type="button" class="small-button" data-wms-catalog-action="refresh">Повторить</button></div></div>` : "");
      const productRows = products.length ? products.map((product) => `
        <div class="card report-row wms-catalog-product">
          <div><b>${escapeHtml(product.name || "Без названия")}</b><span>Артикул: ${escapeHtml(product.offer_id || "—")}<br>Цвет: ${escapeHtml(product.color || "—")} · Размер: ${escapeHtml(product.size || "—")}</span></div>
          <div><span class="status-chip gray">Штрихкод: ${escapeHtml(product.barcode || "—")}</span><small>SKU: ${escapeHtml(product.sku || "—")}</small></div>
        </div>`).join("") : itemEmpty(catalog.loaded ? "По этому запросу товаров не найдено." : "Товары ещё не загружены.");
      const groupsBlock = groups.length ? `<div class="op-list marketplace-group-grid">${groups.map((group) => {
        const colors = new Set(group.products.map((product) => String(product.color || "Не указан")).filter(Boolean));
        const sizes = new Set(group.products.map((product) => String(product.size || "Не указан")).filter(Boolean));
        return `<button type="button" class="card marketplace-clickable marketplace-group-card" data-wms-catalog-group="${escapeHtml(group.key)}"><div class="group-title"><b>${escapeHtml(group.name)}</b><span class="status-chip">›</span></div><div class="marketplace-group-meta"><span>${group.products.length} вариантов</span><span>${colors.size} цветов</span><span>${sizes.size} размеров</span></div><div class="marketplace-group-meta"><span>Открыть цвета и размеры ›</span></div></button>`;
      }).join("")}</div>` : itemEmpty(catalog.loaded ? "По этому запросу групп не найдено." : "Товары ещё не загружены.");
      const colorsBlock = selectedGroup ? [...new Set(products.map((product) => String(product.color || "Не указан")))].sort((a, b) => a.localeCompare(b, "ru")).map((color) => {
        const colorProducts = products.filter((product) => String(product.color || "Не указан") === color).sort((a, b) => String(a.size || "").localeCompare(String(b.size || ""), "ru", {numeric: true}));
        return `<section class="wms-catalog-color-group"><div class="section-title"><b>${escapeHtml(color)}</b><span>${colorProducts.length} вариантов</span></div><div class="op-list">${colorProducts.map((product) => `
          <div class="card report-row wms-catalog-product"><div><b>${escapeHtml(selectedGroup.name)}</b><span>Размер: ${escapeHtml(product.size || "—")}<br>Артикул: ${escapeHtml(product.offer_id || "—")}<br>${product.production_status === "linked" ? `Производство: ${escapeHtml(product.production_product_name)} · ${escapeHtml(product.production_size)} · ${escapeHtml(product.production_color)}` : "Маршрут производства пока не настроен"}</span></div><div><span class="status-chip ${product.production_status === "linked" ? "" : "gray"}">${product.production_status === "linked" ? "связано" : "без маршрута"}</span><span class="status-chip gray">Штрихкод: ${escapeHtml(product.barcode || "—")}</span><small>SKU: ${escapeHtml(product.sku || "—")}</small></div></div>`).join("")}</div></section>`;
      }).join("") : "";
      mount.innerHTML = `
        <div class="screen-head"><div><h2>${selectedGroup ? escapeHtml(selectedGroup.name) : "Товары Ozon"}</h2><p>${selectedGroup ? "Варианты сгруппированы по цвету, затем по размеру." : "Выберите изделие, затем увидите его цвета и размеры."}</p></div><div class="date">${catalog.loaded ? `${products.length} из ${(catalog.products || []).length}` : "загрузка"}</div></div>
        <div class="card field-card"><div class="warehouse-v2-filter-row"><div class="field"><label>Поиск по артикулу, названию, цвету, размеру или штрихкоду</label><input id="wmsCatalogSearch" value="${escapeHtml(state.wmsCatalogSearch || "")}" placeholder="Например 1073896068 или Чёрный"></div><button type="button" class="small-button" data-wms-catalog-action="apply">Показать</button></div><div class="task-note">Последняя синхронизация Ozon: ${escapeHtml(catalog.lastSyncAt || "нет данных")}. В каталоге: артикул, название, цвет, размер и штрихкод.</div></div>
        ${notice}
        ${selectedGroup ? `<div class="button-row"><button type="button" class="small-button secondary" data-wms-catalog-action="groups">‹ Все группы</button></div><div class="section-title"><b>Цвета и размеры</b><span>${products.length}</span></div>${colorsBlock}` : `<div class="section-title"><b>Группы изделий</b><span>${catalog.loaded ? groups.length : ""}</span></div>${groupsBlock}`}
      `;
    }

    function downloadWmsReport(kind) {
      const quote = (value) => `"${String(value == null ? "" : value).replace(/"/g, '""')}"`;
      let rows = [];
      let name = "warehouse-report";
      if (kind === "stock") {
        name = "warehouse-stock";
        rows = [["Товар", "Размер", "Цвет", "Ячейка", "Количество", "Резерв", "Доступно", "Ед."]].concat((state.wmsData.stock || []).map((row) => {
          const product = row.product_key || {};
          const quantity = Number(row.quantity || 0);
          const reserved = Number(row.reserved_quantity || 0);
          return [product.product_name, product.product_size, product.product_color, wmsLocationLabel(row.location_id), quantity, reserved, Math.max(0, quantity - reserved), row.unit || "шт"];
        }));
      } else {
        name = "warehouse-movements";
        rows = [["Дата", "Операция", "Товар", "Количество", "Из ячейки", "В ячейку"]].concat((state.wmsData.movements || []).map((row) => [
          row.occurred_at, wmsMovementLabel(row.movement_type), wmsProductLabel(row.product_key), row.quantity,
          wmsLocationLabel(row.from_location_id), wmsLocationLabel(row.to_location_id),
        ]));
      }
      const blob = new Blob(["\\ufeff" + rows.map((row) => row.map(quote).join(";")).join("\\n")], {type: "text/csv;charset=utf-8"});
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = `${name}-${new Date().toISOString().slice(0, 10)}.csv`;
      link.click();
      URL.revokeObjectURL(link.href);
      showToast("Отчёт", "CSV сформирован из текущих складских данных.");
    }

    function renderWmsStock() {
      const definition = wmsCurrentStockFilter();
      const stock = wmsFilteredStock();
      const filterValues = wmsStockFilterValues();
      const colorLabel = (value) => {
        const row = (state.wmsData.stock || []).find((item) => item.product_key && item.product_key.product_color === value);
        return row && row.product_key.product_color_label ? row.product_key.product_color_label : value;
      };
      mainButton.textContent = "Обновить остатки";
      mainButton.disabled = state.wmsData.loading;
      mount.innerHTML = `
        <div class="screen-head"><div><h2>Адресные остатки</h2><p>Отдельное хранение по категориям склада.</p></div><div class="date">${stock.length} поз.</div></div>
        ${renderWmsDataNotice()}
        <div class="tabs wms-stock-filter-tabs" role="tablist" aria-label="Раздел склада">
          ${wmsStockFilterDefinitions().map((item) => `<button type="button" class="tab ${item.id === definition.id ? "active" : ""}" role="tab" aria-selected="${item.id === definition.id ? "true" : "false"}" data-wms-stock-filter="${item.id}">${escapeHtml(item.label)}</button>`).join("")}
        </div>
        <div class="card field-card wms-stock-filter-card">
          <div class="form-grid">
            <div class="field ${definition.itemType === "material" ? "" : "full"}"><label>${definition.itemType === "material" ? "Материал" : "Номенклатура изделия"}</label><select id="wmsStockProductFilter">${wmsFilterOptionHtml(filterValues.productValues, state.wmsStockProductFilter, definition.itemType === "material" ? "Все материалы" : "Все изделия")}</select></div>
            ${definition.itemType === "material" ? "" : `<div class="field"><label>Размер</label><select id="wmsStockSizeFilter">${wmsFilterOptionHtml(filterValues.sizeValues, state.wmsStockSizeFilter, "Все размеры")}</select></div>`}
            <div class="field"><label>Цвет</label><select id="wmsStockColorFilter">${wmsFilterOptionHtml(filterValues.colorValues, state.wmsStockColorFilter, "Все цвета", colorLabel)}</select></div>
          </div>
          <div class="button-row"><button type="button" class="small-button secondary" data-wms-stock-action="reset-filters">Сбросить фильтры</button><span class="status-chip">${escapeHtml(definition.label)}</span></div>
        </div>
        ${renderWmsWarehouseMap(stock)}
        <div class="op-list">${stock.length ? stock.map((row) => {
          const available = Math.max(0, Number(row.quantity || 0) - Number(row.reserved_quantity || 0));
          const itemLabel = definition.itemType === "material" ? "Материал" : (definition.itemType === "semifinished" ? "Полуфабрикат" : "Готовая продукция");
          return `<div class="card report-row"><div><b>${escapeHtml(wmsProductLabel(row.product_key))}</b><span>${escapeHtml(wmsLocationLabel(row.location_id))} · ${itemLabel}<br>Доступно ${escapeHtml(available)}, резерв ${escapeHtml(row.reserved_quantity || 0)}</span></div><span class="status-chip">${escapeHtml(row.quantity)} ${escapeHtml(row.unit || definition.unit)}</span></div>`;
        }).join("") : itemEmpty("В выбранном разделе нет остатков.")}</div>
      `;
    }

    function renderWmsMovements() {
      const movements = state.wmsData.movements || [];
      mainButton.textContent = "Обновить историю";
      mainButton.disabled = state.wmsData.loading;
      mount.innerHTML = `
        <div class="screen-head"><div><h2>История движений</h2><p>Последние складские операции сверху.</p></div><div class="date">${movements.length} зап.</div></div>
        ${renderWmsDataNotice()}
        <div class="op-list">${movements.length ? movements.map((movement) => `
          <div class="card report-row"><div><b>${escapeHtml(wmsMovementLabel(movement.movement_type))}</b><span>${escapeHtml(wmsProductLabel(movement.product_key))}<br>${escapeHtml(wmsLocationLabel(movement.from_location_id))} → ${escapeHtml(wmsLocationLabel(movement.to_location_id))}${movement.reason ? `<br>${escapeHtml(movement.reason)}` : ""}</span></div><div><span class="status-chip">${escapeHtml(movement.quantity)} шт.</span><small>${escapeHtml(wmsMovementTime(movement.occurred_at))}</small></div></div>
        `).join("") : itemEmpty("Складских движений пока нет.")}</div>
      `;
    }

    async function refreshWmsWorkspace({silent = false} = {}) {
      if (!canAccessWms() || state.wmsData.loading) return;
      state.wmsData.loading = true;
      state.wmsData.error = "";
      if (!silent) render();
      try {
        const [locations, stock, movements] = await Promise.all([
          api("/api/wms/locations"),
          api("/api/wms/stock"),
          api("/api/wms/movements", {limit: 100}),
        ]);
        state.wmsData.locations = locations.locations || [];
        state.wmsData.stock = stock.stock || [];
        state.wmsData.movements = movements.movements || [];
        state.wmsData.loaded = true;
      } catch (error) {
        state.wmsData.error = error.apiMessage || "Проверьте соединение и повторите попытку.";
      } finally {
        state.wmsData.loading = false;
        if (state.workspace === "warehouse") render();
      }
    }

    async function refreshWmsCatalog({silent = false} = {}) {
      if (!canAccessWms() || state.wmsCatalog.loading) return;
      state.wmsCatalog.loading = true;
      state.wmsCatalog.error = "";
      if (!silent) render();
      try {
        const data = await api("/api/wms/catalog/products");
        if (!data.ok) throw new Error(data.message || "Не удалось загрузить каталог Ozon.");
        state.wmsCatalog.products = Array.isArray(data.products) ? data.products : [];
        state.wmsCatalog.lastSyncAt = data.last_sync_at || "";
        state.wmsCatalog.loaded = true;
      } catch (error) {
        state.wmsCatalog.error = error.apiMessage || error.message || "Проверьте соединение и повторите попытку.";
      } finally {
        state.wmsCatalog.loading = false;
        if (state.workspace === "warehouse" && state.wmsView === "products") render();
      }
    }

    function marketplaceMoney(value) {
      if (value === null || value === undefined || value === "") return "—";
      return `${Number(value).toLocaleString("ru-RU", {maximumFractionDigits: 2})} ₽`;
    }

    function marketplaceGroups(payload, products) {
      const groups = Array.isArray(payload.product_groups) ? payload.product_groups : [];
      if (groups.length) return groups;
      const fallback = new Map();
      products.forEach((row) => {
        const key = row.group_key || "other";
        const group = fallback.get(key) || {key, name: row.group_name || "Прочие товары", products: 0, articles: 0, available: 0, price_min: null, price_max: null};
        group.products += 1;
        group.available += Number(row.available || 0);
        const price = row.current_price == null ? null : Number(row.current_price);
        if (price != null && !Number.isNaN(price)) {
          group.price_min = group.price_min == null ? price : Math.min(group.price_min, price);
          group.price_max = group.price_max == null ? price : Math.max(group.price_max, price);
        }
        fallback.set(key, group);
      });
      return [...fallback.values()].sort((a, b) => String(a.name).localeCompare(String(b.name), "ru"));
    }

    function marketplaceDetailField(label, value) {
      return `<div class="marketplace-detail-field"><span>${escapeHtml(label)}</span><b>${escapeHtml(value == null || value === "" ? "—" : value)}</b></div>`;
    }

    function marketplaceBackButton(label = "Назад") {
      return `<button type="button" class="small-button secondary" data-marketplace-action="back">‹ ${escapeHtml(label)}</button>`;
    }

    function renderMarketplaceDetail(products, orders, runs) {
      const detail = state.marketplaceDetail || {};
      if (detail.kind === "group") {
        const groupRows = products.filter((row) => String(row.group_key || "other") === String(detail.key));
        const group = marketplaceGroups(state.marketplaceData.payload || {}, products).find((row) => String(row.key) === String(detail.key));
        if (!group) return "";
        return `
          <div class="marketplace-detail-head"><div>${marketplaceBackButton("К группам")}</div><div><h3>${escapeHtml(group.name)}</h3><p>${groupRows.length} позиций · ${group.articles || groupRows.length} артикулов · остаток ${escapeHtml(group.available || 0)} шт.</p></div></div>
          <div class="marketplace-detail-grid">
            ${marketplaceDetailField("Товаров в группе", group.products || groupRows.length)}
            ${marketplaceDetailField("Артикулов", group.articles || groupRows.length)}
            ${marketplaceDetailField("Цена от", marketplaceMoney(group.price_min))}
            ${marketplaceDetailField("Цена до", marketplaceMoney(group.price_max))}
          </div>
          <div class="section-title"><b>Товары группы</b><span>${groupRows.length}</span></div>
          <div class="op-list">${groupRows.length ? groupRows.map((row) => `
            <button type="button" class="card report-row marketplace-clickable marketplace-product-card" data-marketplace-product-id="${escapeHtml(row.id)}">
              <div class="product-title"><b>${escapeHtml(row.name || "Товар Ozon")}</b><span class="status-chip">›</span></div>
              <div class="marketplace-product-meta"><span>Название: ${escapeHtml(row.name || "—")}</span><span>Артикул: ${escapeHtml(row.offer_id || "—")}</span><span>SKU: ${escapeHtml(row.sku || "—")}</span></div>
              <div class="marketplace-product-meta"><span>${escapeHtml(row.size || "Размер не указан")} · ${escapeHtml(row.color || "Цвет не указан")}</span></div>
              <div class="marketplace-product-meta"><span>Остаток: ${escapeHtml(row.available == null ? "—" : row.available)} шт.</span><span>Цена: ${marketplaceMoney(row.current_price)}</span></div>
            </button>`).join("") : itemEmpty("В этой группе пока нет товаров.")}</div>
        `;
      }
      if (detail.kind === "product") {
        const product = products.find((row) => String(row.id) === String(detail.id));
        if (!product) return "";
        return `
          <div class="marketplace-detail-head"><div>${marketplaceBackButton("К группе")}</div><div><h3>${escapeHtml(product.name || product.offer_id || product.sku || "Товар")}</h3><p>${escapeHtml(product.group_name || "Товар маркетплейса")}</p></div></div>
          <div class="marketplace-detail-grid">
            ${marketplaceDetailField("Артикул", product.offer_id)}
            ${marketplaceDetailField("SKU", product.sku)}
            ${marketplaceDetailField("Штрихкод", product.barcode)}
            ${marketplaceDetailField("Размер", product.size)}
            ${marketplaceDetailField("Цвет", product.color)}
            ${marketplaceDetailField("Остаток", `${product.available == null ? "—" : product.available} шт.`)}
            ${marketplaceDetailField("Текущая цена", marketplaceMoney(product.current_price))}
            ${marketplaceDetailField("Старая цена", marketplaceMoney(product.old_price))}
            ${marketplaceDetailField("Обновлено", product.updated_at)}
          </div>
        `;
      }
      if (detail.kind === "order") {
        const order = orders.find((row) => String(row.id) === String(detail.id));
        if (!order) return "";
        return `
          <div class="marketplace-detail-head"><div>${marketplaceBackButton("К отгрузкам")}</div><div><h3>${escapeHtml(order.posting_number || order.external_order_id || "Отгрузка")}</h3><p>Отгрузка Ozon · подробности доступны только для чтения</p></div></div>
          <div class="marketplace-detail-grid">
            ${marketplaceDetailField("Номер заказа", order.external_order_id)}
            ${marketplaceDetailField("Статус", order.status)}
            ${marketplaceDetailField("Срок отгрузки", order.shipment_date)}
            ${marketplaceDetailField("Обновлено", order.updated_at)}
          </div>
        `;
      }
      if (detail.kind === "sync") {
        const run = runs.find((row) => String(row.id) === String(detail.id));
        if (!run) return "";
        return `
          <div class="marketplace-detail-head"><div>${marketplaceBackButton("К синхронизации")}</div><div><h3>Синхронизация ${escapeHtml(run.started_at || "")}</h3><p>Результат обращения к Ozon Seller API</p></div></div>
          <div class="marketplace-detail-grid">
            ${marketplaceDetailField("Статус", run.status)}
            ${marketplaceDetailField("Товары", run.products_count)}
            ${marketplaceDetailField("Цены", run.prices_count)}
            ${marketplaceDetailField("Остатки", run.stocks_count)}
            ${marketplaceDetailField("Отгрузки", run.orders_count)}
            ${marketplaceDetailField("Ошибка", run.error_message)}
          </div>
        `;
      }
      return "";
    }

    function renderMarketplaces() {
      if (!canAccessMarketplaces()) {
        mainButton.textContent = "Обновить";
        mainButton.disabled = false;
        mount.innerHTML = `<div class="screen-head"><div><h2>Маркетплейсы</h2><p>Раздел доступен администратору.</p></div></div><div class="card field-card">${itemEmpty("Нет прав администратора.")}</div>`;
        return;
      }
      const payload = state.marketplaceData.payload || {};
      const selectedProvider = ["all", "ozon", "wildberries"].includes(state.marketplaceProvider) ? state.marketplaceProvider : "all";
      const isOzon = selectedProvider === "ozon";
      const isWildberries = selectedProvider === "wildberries";
      const isAll = selectedProvider === "all";
      const summary = isWildberries ? {} : (payload.summary || {});
      const products = isWildberries ? [] : (payload.products_rows || []);
      const orders = isWildberries ? [] : (payload.orders_rows || []);
      const runs = isWildberries ? [] : (payload.sync_runs || []);
      const accounts = payload.accounts || [];
      const account = accounts[0] || {};
      const wildberries = (payload.connectors || []).find((item) => item.marketplace === "wildberries") || {};
      const providerName = isAll ? "маркетплейсов" : (isOzon ? "Ozon" : "Wildberries");
      const providerConfigured = isAll
        ? Boolean(payload.configured || wildberries.configured)
        : (isOzon ? Boolean(payload.configured) : Boolean(wildberries.configured));
      const providerStatus = isAll
        ? `Ozon: ${payload.configured ? "подключён" : "не подключён"} · Wildberries: ${wildberries.configured ? "подключён" : "не подключён"}`
        : (isOzon
          ? (providerConfigured ? `Подключён · ${account.account_name || "Основной аккаунт"}` : "Не настроен · добавьте ключи")
          : (providerConfigured ? "Токен задан · синхронизатор готовится" : "Токен пока не задан"));
      const providerTitle = isAll ? "маркетплейсами" : providerName;
      const groups = marketplaceGroups(payload, products);
      mainButton.hidden = isWildberries;
      mainButton.textContent = state.marketplaceData.loading ? "Синхронизация…" : "Синхронизировать Ozon";
      mainButton.disabled = isWildberries || state.marketplaceData.loading;
      const errorNotice = !isWildberries && state.marketplaceData.error ? `<div class="card field-card"><div class="task-note"><b>Ошибка маркетплейса</b><br>${escapeHtml(state.marketplaceData.error)}</div><div class="button-row"><button type="button" class="small-button" data-marketplace-action="refresh">Повторить</button></div></div>` : "";
      const notConfigured = !providerConfigured ? `<div class="card field-card"><div class="task-note"><b>${isAll ? "Маркетплейсы пока не подключены" : `${providerName} пока не подключён`}</b><br>${isAll ? "Подключите хотя бы одну площадку, чтобы загрузить товары и остатки." : (isOzon ? "Добавьте на сервере OZON_CLIENT_ID и OZON_API_KEY в /etc/sewing-web/sewing-web.env, затем перезапустите сервис." : "Добавьте токен Wildberries, чтобы загрузить товары, остатки и отгрузки.")}</div></div>` : "";
      const productsBlock = groups.length ? `<div class="op-list marketplace-group-grid">${groups.map((group) => `<button type="button" class="card marketplace-clickable marketplace-group-card" data-marketplace-group="${escapeHtml(group.key)}"><div class="group-title"><b>${escapeHtml(group.name)}</b><span class="status-chip">›</span></div><div class="marketplace-group-meta"><span>${escapeHtml(group.products || 0)} поз.</span><span>${escapeHtml(group.articles || group.products || 0)} артикулов</span><span>Остаток: ${escapeHtml(group.available || 0)} шт.</span></div><div class="marketplace-group-meta"><span>Цена: ${marketplaceMoney(group.price_min)}${group.price_max != null && group.price_max !== group.price_min ? ` — ${marketplaceMoney(group.price_max)}` : ""}</span><span>Открыть группу ›</span></div></button>`).join("")}</div>` : itemEmpty("Товары ещё не загружены.");
      const stocksBlock = products.length ? `<div class="op-list">${products.map((row) => `<button type="button" class="card report-row marketplace-clickable" data-marketplace-product-id="${escapeHtml(row.id)}"><div><b>${escapeHtml(row.name || "Товар Ozon")}</b><span>${escapeHtml(row.group_name || "Прочие товары")} · Артикул: ${escapeHtml(row.offer_id || "—")}</span></div><span class="status-chip ${Number(row.available || 0) > 0 ? "" : "gray"}">${escapeHtml(row.available == null ? "—" : row.available)} шт. ›</span></button>`).join("")}</div>` : itemEmpty("Остатки ещё не загружены.");
      const analyticsBlock = `
        <div class="kpi-grid">
          <div class="card kpi"><div class="kpi-top"><span>Карточки товаров</span><span class="kpi-ico">▤</span></div><strong>${escapeHtml(summary.products || 0)}</strong><span>Загружено из ${providerName}</span></div>
          <div class="card kpi"><div class="kpi-top"><span>Строк остатков</span><span class="kpi-ico">▦</span></div><strong>${escapeHtml(summary.stock_rows || 0)}</strong><span>FBO и FBS</span></div>
          <div class="card kpi"><div class="kpi-top"><span>Открытые отгрузки</span><span class="kpi-ico">↑</span></div><strong>${escapeHtml(summary.open_orders || 0)}</strong><span>Требуют контроля</span></div>
        </div>
        <div class="card field-card"><div class="section-title"><b>Состояние синхронизации</b><span>${escapeHtml(account.last_sync_at || "нет данных")}</span></div><div class="task-note">Раздел аналитики показывает только данные, полученные из маркетплейса. Изменения на Ozon и Wildberries из приложения не отправляются.</div></div>
      `;
      const ordersBlock = orders.length ? `<div class="op-list">${orders.map((row) => `<button type="button" class="card report-row marketplace-clickable" data-marketplace-order-id="${escapeHtml(row.id)}"><div><b>${escapeHtml(row.posting_number || row.external_order_id)}</b><span>Заказ: ${escapeHtml(row.external_order_id)}<br>${escapeHtml(row.shipment_date || "Срок не указан")}</span></div><span class="status-chip ${row.status && !["delivering", "awaiting_packaging"].includes(row.status) ? "warn" : "gray"}">${escapeHtml(row.status || "Без статуса")} ›</span></button>`).join("")}</div>` : itemEmpty("Отгрузки ещё не загружены.");
      const runsBlock = runs.length ? `<div class="op-list">${runs.map((row) => `<button type="button" class="card report-row marketplace-clickable" data-marketplace-sync-id="${escapeHtml(row.id)}"><div><b>${escapeHtml(row.started_at || "Синхронизация")}</b><span>Товары ${escapeHtml(row.products_count)} · цены ${escapeHtml(row.prices_count)} · остатки ${escapeHtml(row.stocks_count)} · отгрузки ${escapeHtml(row.orders_count)}${row.error_message ? `<br>${escapeHtml(row.error_message)}` : ""}</span></div><span class="status-chip ${row.status === "success" ? "" : "warn"}">${escapeHtml(row.status)} ›</span></button>`).join("")}</div>` : itemEmpty("Синхронизаций ещё не было.");
      const overviewBlock = `
        <div class="kpi-grid">
          <button type="button" class="card kpi marketplace-clickable" data-marketplace-view="products"><div class="kpi-top"><span>Товары</span><span class="kpi-ico">▤</span></div><strong>${escapeHtml(summary.products || 0)}<small> поз.</small></strong><span>Каталог ${providerName} · открыть товары ›</span></button>
          <button type="button" class="card kpi marketplace-clickable" data-marketplace-view="stocks"><div class="kpi-top"><span>Остатки</span><span class="kpi-ico">▦</span></div><strong>${escapeHtml(summary.stock_rows || 0)}<small> строк</small></strong><span>FBO и FBS · открыть остатки ›</span></button>
          <button type="button" class="card kpi marketplace-clickable" data-marketplace-view="orders"><div class="kpi-top"><span>Отгрузки</span><span class="kpi-ico">↑</span></div><strong>${escapeHtml(summary.open_orders || 0)}<small> открыто</small></strong><span>Данные ${providerName} · открыть список ›</span></button>
        </div>
      `;
      const content = state.marketplaceView === "overview" ? overviewBlock : state.marketplaceView === "orders" ? ordersBlock : state.marketplaceView === "sync" ? runsBlock : state.marketplaceView === "stocks" ? stocksBlock : state.marketplaceView === "analytics" ? analyticsBlock : productsBlock;
      const title = state.marketplaceView === "overview" ? "Обзор" : state.marketplaceView === "orders" ? "Отгрузки" : state.marketplaceView === "sync" ? "Журнал синхронизации" : state.marketplaceView === "stocks" ? "Остатки" : state.marketplaceView === "analytics" ? "Аналитика" : "Товары";
      const detail = renderMarketplaceDetail(products, orders, runs);
      mount.innerHTML = `
        <div class="screen-head"><div><h2>Управление ${providerTitle}</h2><p>Выберите площадку — содержимое разделов изменится под выбранный маркетплейс.</p></div><div class="marketplace-provider-inline"><div class="marketplace-provider-switch" role="tablist" aria-label="Выбор маркетплейса"><button type="button" class="marketplace-provider-button marketplace-provider-all ${isAll ? "active" : ""}" data-marketplace-provider="all" role="tab" aria-selected="${isAll}"><b>Общая</b><span>Все площадки</span></button><button type="button" class="marketplace-provider-button marketplace-provider-ozon ${isOzon ? "active" : ""}" data-marketplace-provider="ozon" role="tab" aria-selected="${isOzon}"><b>Ozon</b><span>${escapeHtml(payload.configured ? (account.account_name || "Подключён") : "Не подключён")}</span></button><button type="button" class="marketplace-provider-button marketplace-provider-wb ${isWildberries ? "active" : ""}" data-marketplace-provider="wildberries" role="tab" aria-selected="${isWildberries}"><b>Wildberries</b><span>${escapeHtml(wildberries.configured ? "Подключён" : "Не подключён")}</span></button></div><div class="marketplace-provider-status"><b>${isAll ? "Общий обзор" : providerName}</b><span>${escapeHtml(providerStatus)}</span></div></div></div>
        ${errorNotice}${notConfigured}
        ${state.marketplaceDetail ? detail : `<div class="section-title"><b>${title}</b><span>${state.marketplaceView === "orders" ? orders.length : state.marketplaceView === "sync" ? runs.length : state.marketplaceView === "stocks" ? products.length : state.marketplaceView === "analytics" ? "" : groups.length}</span></div>${content}`}
      `;
    }

    function renderWarehouse() {
      if (!canAccessWms()) {
        switchWorkspace("production");
        return;
      }
      renderWms();
    }

    function renderWarehouseSidebar() {
      const items = [
        ["overview", "⌂", "Обзор"],
        ["receive", "↓", "Приёмка"],
        ["map", "▦", "Карта склада"],
        ["putaway", "→", "Размещение"],
        ["transfer", "⇄", "Перемещение"],
        ["pick", "↑", "Выдача"],
        ["stock", "▤", "Остатки"],
        ["lookup", "⌕", "Проверка товара"],
        ["products", "▤", "Товары"],
        ["inventory", "≡", "Инвентаризация"],
        ["reports", "↧", "Отчёты"],
        ["more", "•••", "Ещё"],
      ];
      return `<aside class="warehouse-v2-sidebar" aria-label="Разделы склада"><h3>Управление складом</h3>${items.map(([id, icon, label]) => `
        <button type="button" class="warehouse-v2-nav ${state.wmsView === id || (id === "more" && warehouseMoreViews.has(state.wmsView) && !["map", "reports", "products", "lookup"].includes(state.wmsView)) ? "active" : ""}" data-wms-view="${id}"><span class="warehouse-v2-icon">${icon}</span><span>${label}</span></button>
      `).join("")}</aside>`;
    }

    function renderWms() {
      if (!canAccessWms()) {
        mainButton.textContent = "Обновить";
        mainButton.disabled = false;
        mount.innerHTML = `
          <div class="screen-head"><div><h2>ТСД</h2><p>Раздел доступен кладовщикам и администраторам.</p></div></div>
          <div class="card field-card">${itemEmpty("Нет доступа к складским операциям.")}</div>
        `;
        return;
      }
      if (state.wmsView === "overview") renderWmsOverview();
      else if (state.wmsView === "more") renderWmsMore();
      else if (state.wmsView === "map") renderWmsMapView();
      else if (state.wmsView === "stock") renderWmsStock();
      else if (state.wmsView === "lookup") renderWmsLookup();
      else if (state.wmsView === "products") renderWmsProducts();
      else if (state.wmsView === "movements") renderWmsMovements();
      else if (state.wmsView === "inventory") renderWmsInventory();
      else if (state.wmsView === "reports") renderWmsReports();
      else if (state.wmsView === "scrap") renderWmsScrap();
      else if (state.wmsView === "pick") renderWmsPick();
      else if (state.wmsView === "putaway") renderWmsPutaway();
      else if (state.wmsView === "transfer") renderWmsTransfer();
      else renderWmsReceive();
      if (!(state.data && state.data.features && state.data.features.warehouse_ui_v2)) return;
      const content = mount.innerHTML;
      mount.innerHTML = `<div class="warehouse-v2-layout">${renderWarehouseSidebar()}<div class="warehouse-v2-content">${content}</div></div>`;
    }

    function wmsProductOptions(selected) {
      const catalog = getRouteCatalog();
      const names = catalog.length ? catalog.map((c) => c.product_name) : ["Готовое изделие"];
      const unique = [...new Set(names)];
      if (selected && !unique.includes(selected)) unique.unshift(selected);
      return unique.map((name) => `<option value="${escapeHtml(name)}" ${name === selected ? "selected" : ""}>${escapeHtml(name)}</option>`).join("");
    }

    function wmsSizeOptions(productName, selected) {
      const catalog = getRouteCatalog();
      const item = catalog.find((c) => c.product_name === productName);
      const sizes = (item && item.sizes) || ["42", "44", "46", "48", "50", "52", "86", "92", "98", "104", "110", "116", "122", "128", "134", "140", "146", "152", "158", "164"];
      return sizes.map((s) => `<option value="${escapeHtml(s)}" ${s === selected ? "selected" : ""}>${escapeHtml(s)}</option>`).join("");
    }

    function wmsColorOptions(productName, selected) {
      const catalog = getRouteCatalog();
      const item = catalog.find((c) => c.product_name === productName);
      const colors = (item && item.colors) || ["Черный", "Белый", "Серый", "Бежевый", "Синий"];
      return colors.map((c) => `<option value="${escapeHtml(c)}" ${c === selected ? "selected" : ""}>${escapeHtml(c)}</option>`).join("");
    }

    function renderWmsReceive() {
      const d = state.wmsDraft;
      const receiving = wmsReceivingStock();
      const materials = wmsReceivingMaterials();
      const materialDraft = state.wmsMaterialReceipt;
      const total = receiving.reduce((sum, row) => sum + Number(row.quantity || 0), 0);
      const selectedProduct = receiving.find((row) => wmsProductKeysEqual(row.product_key, wmsProductKey(d)));
      mainButton.textContent = state.wmsData.loading ? "Обновляем…" : "Обновить приёмку";
      mainButton.disabled = state.wmsData.loading;
      mount.innerHTML = `
        <div class="screen-head"><div><h2>Зона приёмки</h2><p>Товар появляется здесь автоматически после завершения упаковки. Материалы принимаются вручную.</p></div><div class="date">${escapeHtml(total)} ед.</div></div>
        ${renderWmsDataNotice()}
        <div class="card field-card"><div class="task-note"><b>Как работать</b><br>Проверьте поступление, откройте «Размещение», отсканируйте ячейку, затем штрихкод товара и укажите количество.</div></div>
        <div class="section-title"><b>Ожидает размещения</b><span>${receiving.length} поз.</span></div>
        <div class="op-list">${receiving.length ? receiving.map((row, index) => {
          const available = Math.max(0, Number(row.quantity || 0) - Number(row.reserved_quantity || 0));
          const isMaterial = row.product_key && row.product_key.item_type === "material";
          return `<div class="card report-row"><div><b>${escapeHtml(wmsProductLabel(row.product_key))}</b><span>${isMaterial ? "Материал" : (row.product_key && row.product_key.item_type === "semifinished" ? "Полуфабрикат" : "Готовая продукция")} · доступно ${escapeHtml(available)}</span></div><div><span class="status-chip">${escapeHtml(row.quantity)} ${escapeHtml(row.unit || "шт")}</span>${isMaterial ? `<button type="button" class="link-button" data-wms-material-putaway="${materials.indexOf(row)}">Разместить</button>` : (state.data && state.data.is_admin ? `<button type="button" class="link-button" data-wms-receipt-product="${index}">штрихкод</button>` : "")}</div></div>`;
        }).join("") : itemEmpty("После завершения упаковки товар появится здесь автоматически.")}</div>
        <div class="section-title"><b>Ручная приёмка материалов</b><span>без штрихкода</span></div>
        <div class="card field-card">
          <div class="task-note"><b>Материал принимается в зону приёмки.</b><br>После сохранения выберите его в списке и вручную укажите ячейку размещения.</div>
          <div class="form-grid">
            <div class="field"><label>Материал</label><input id="wmsMaterialName" value="${escapeHtml(materialDraft.name || "")}" placeholder="Ткань, дублерин…"></div>
            <div class="field"><label>Цвет</label><input id="wmsMaterialColor" value="${escapeHtml(materialDraft.color || "")}" placeholder="Черный, бежевый…"></div>
            <div class="field"><label>Единица</label><select id="wmsMaterialUnit"><option value="рул" selected>рулонов</option></select></div>
            <div class="field"><label>Количество</label><input id="wmsMaterialQuantity" type="number" inputmode="numeric" min="1" step="1" value="${escapeHtml(materialDraft.quantity || "")}" placeholder="0"></div>
            <div class="field full"><label>Комментарий</label><input id="wmsMaterialComment" value="${escapeHtml(materialDraft.comment || "")}" placeholder="Партия или примечание (необязательно)"></div>
          </div>
          <div class="button-row"><button class="small-button" data-wms-action="material_receive">Принять материал</button></div>
        </div>
        ${state.data && state.data.is_admin && selectedProduct ? `
          <div class="card field-card">
            <label>Штрихкод выбранного товара</label>
            <div class="report-row"><div><b>${escapeHtml(wmsProductLabel(selectedProduct.product_key))}</b><span>Привяжите нанесённый на товар код один раз</span></div><span class="status-chip">выбран</span></div>
            <div class="field full"><label>Новый штрихкод</label><input id="wmsBarcode" value="${escapeHtml(d.barcode || "")}" placeholder="EAN-13 / Code 128"></div>
            <div class="button-row"><button class="small-button" data-wms-scan="bind_product">📷 Сканировать код</button><button class="small-button secondary" data-wms-action="register_barcode">Привязать код</button></div>
          </div>
        ` : ""}
      `;
    }

    function renderWmsPutaway() {
      const d = state.wmsDraft;
      const locationCode = (d.toLocation || "").replace(/^LOC:/i, "").trim();
      const materialMode = d.itemType === "material";
      const materialRow = materialMode ? wmsReceivingMaterials().find((row) => wmsProductKeysEqual(row.product_key, wmsProductKey(d))) : null;
      const materialAvailable = materialRow ? Math.max(0, Number(materialRow.quantity || 0) - Number(materialRow.reserved_quantity || 0)) : 0;
      const productDetected = !materialMode && Boolean(d.productScanned && d.productName && d.productSize && d.productColor);
      mainButton.textContent = "Разместить";
      mainButton.disabled = false;
      mount.innerHTML = `
        <div class="screen-head"><div><h2>Размещение</h2><p>${materialMode ? "Материал выбран из приёмки. Ячейку и количество введите вручную." : "Сначала ячейка, затем товар и количество."}</p></div></div>
        ${materialMode ? `<div class="card field-card"><div class="task-note"><b>Материал</b><br>${escapeHtml(wmsProductLabel(wmsProductKey(d)))} · доступно в приёмке: ${escapeHtml(materialAvailable)} ${escapeHtml(d.materialUnit || "рул")}</div></div>` : renderWmsGuidedScanner("to_location", locationCode, productDetected, "Ячейка размещения")}
        <div class="card field-card">
          <label>Данные размещения</label>
          <div class="form-grid">
            <div class="field full"><label>Ячейка</label><input id="wmsToLocation" value="${escapeHtml(d.toLocation || "")}" placeholder="${materialMode ? "Например Z1-S1-P1-1" : "Сначала отсканируйте ячейку"}" ${materialMode ? "" : "readonly"}></div>
            ${productDetected ? `<div class="field full"><label>Товар</label><div class="report-row"><div><b>${escapeHtml(wmsProductLabel(wmsProductKey(d)))}</b><span>Штрихкод распознан</span></div><span class="status-chip">✓</span></div></div>` : ""}
            ${materialMode || productDetected ? `<div class="field full"><label>Количество</label><input id="wmsQuantity" type="number" inputmode="numeric" min="1" ${materialMode ? `max="${escapeHtml(materialAvailable)}"` : ""} step="1" value="${escapeHtml(d.quantity || "")}" placeholder="0"></div>` : ""}
          </div>
        </div>
        ${renderWmsLocationContents(locationCode)}
        <div class="button-row">
          <button class="small-button secondary" data-wms-action="putaway">Разместить</button>
        </div>
      `;
    }

    function renderWmsPick() {
      const d = state.wmsDraft;
      const locationCode = (d.fromLocation || "").replace(/^LOC:/i, "").trim();
      const productDetected = Boolean(d.productScanned && d.productName && d.productSize && d.productColor);
      const stockRow = productDetected ? wmsFindScannedStock(locationCode, wmsProductKey(d)) : null;
      const available = stockRow ? Math.max(0, Number(stockRow.quantity || 0) - Number(stockRow.reserved_quantity || 0)) : 0;
      mainButton.textContent = "Подтвердить выдачу";
      mainButton.disabled = !locationCode || !stockRow;
      mount.innerHTML = `
        <div class="screen-head"><div><h2>Выдача из ячейки</h2><p>Отсканируйте ячейку, проверьте содержимое, затем отсканируйте товар.</p></div></div>
        ${renderWmsGuidedScanner("from_location", locationCode, productDetected, "Исходная ячейка")}
        ${renderWmsLocationContents(locationCode)}
        ${productDetected ? `
          <div class="card field-card">
            <label>Выбранный товар</label>
            <div class="report-row"><div><b>${escapeHtml(wmsProductLabel(wmsProductKey(d)))}</b><span>${stockRow ? `Доступно в ячейке: ${escapeHtml(available)} шт.` : "Товар отсутствует в этой ячейке"}</span></div><span class="status-chip ${stockRow ? "" : "warn"}">${stockRow ? "✓" : "!"}</span></div>
            <div class="field full"><label>Количество к выдаче</label><input id="wmsQuantity" type="number" inputmode="numeric" min="1" max="${escapeHtml(available)}" step="1" value="${escapeHtml(d.quantity || "")}" placeholder="0"></div>
          </div>
        ` : ""}
        <div class="button-row"><button class="small-button secondary" data-wms-action="pick" ${stockRow ? "" : "disabled"}>Подтвердить выдачу</button></div>
      `;
    }

    function renderWmsTransfer() {
      const d = state.wmsDraft;
      mainButton.textContent = "Переместить";
      mainButton.disabled = false;
      mount.innerHTML = `
        <div class="screen-head"><div><h2>Перемещение</h2><p>Переместить товар между ячейками. Отсканируйте исходную и целевую ячейки.</p></div></div>
        <div class="card field-card">
          <div class="form-grid">
            <div class="field full"><label>Изделие</label><select id="wmsProductName">${wmsProductOptions(d.productName)}</select></div>
            <div class="field"><label>Размер</label><select id="wmsProductSize">${wmsSizeOptions(d.productName, d.productSize)}</select></div>
            <div class="field"><label>Цвет</label><select id="wmsProductColor">${wmsColorOptions(d.productName, d.productColor)}</select></div>
            <div class="field full"><label>Из ячейки</label><input id="wmsFromLocation" value="${escapeHtml(d.fromLocation || "")}" placeholder="Z1-S1-P1-1"></div>
            <div class="field full"><label>В ячейку</label><input id="wmsToLocation" value="${escapeHtml(d.toLocation || "")}" placeholder="Z2-S1-P1-1"></div>
            <div class="field full"><label>Количество</label><input id="wmsQuantity" type="number" min="1" step="1" value="${escapeHtml(d.quantity || "")}" placeholder="0"></div>
          </div>
        </div>
        <div class="button-row">
          <button class="small-button" data-wms-scan="from_location">📷 Из ячейки</button>
          <button class="small-button" data-wms-scan="to_location">📷 В ячейку</button>
          <button class="small-button secondary" data-wms-action="transfer">Переместить</button>
        </div>
      `;
    }

    function renderWmsInventory() {
      const d = state.wmsDraft;
      mainButton.textContent = "Сохранить пересчёт";
      mainButton.disabled = false;
      mount.innerHTML = `
        <div class="screen-head"><div><h2>Инвентаризация</h2><p>Сначала отсканируйте ячейку, затем товар и введите фактическое количество.</p></div></div>
        <div class="card field-card">
          <div class="form-grid">
            <div class="field full"><label>Ячейка</label><input id="wmsFromLocation" value="${escapeHtml(d.fromLocation || "")}" placeholder="Z1-S1-P1-1"></div>
            <div class="field full"><label>Изделие</label><select id="wmsProductName">${wmsProductOptions(d.productName)}</select></div>
            <div class="field"><label>Размер</label><select id="wmsProductSize">${wmsSizeOptions(d.productName, d.productSize)}</select></div>
            <div class="field"><label>Цвет</label><select id="wmsProductColor">${wmsColorOptions(d.productName, d.productColor)}</select></div>
            <div class="field full"><label>Фактическое количество</label><input id="wmsQuantity" type="number" min="0" step="1" value="${escapeHtml(d.quantity || "")}" placeholder="0"></div>
          </div>
        </div>
        <div class="button-row">
          <button class="small-button" data-wms-scan="from_location">📷 Ячейка</button>
          <button class="small-button" data-wms-scan="product">📷 Товар</button>
          <button class="small-button secondary" data-wms-action="inventory">Сохранить</button>
        </div>
      `;
    }

    function renderWmsScrap() {
      const d = state.wmsDraft;
      mainButton.textContent = "Списать товар";
      mainButton.disabled = false;
      mount.innerHTML = `
        <div class="screen-head"><div><h2>Списание</h2><p>Списание брака, повреждённого товара или отправка в карантин.</p></div></div>
        <div class="card field-card">
          <div class="form-grid">
            <div class="field full"><label>Ячейка</label><input id="wmsFromLocation" value="${escapeHtml(d.fromLocation || "")}" placeholder="Z1-S1-P1-1"></div>
            <div class="field full"><label>Изделие</label><select id="wmsProductName">${wmsProductOptions(d.productName)}</select></div>
            <div class="field"><label>Размер</label><select id="wmsProductSize">${wmsSizeOptions(d.productName, d.productSize)}</select></div>
            <div class="field"><label>Цвет</label><select id="wmsProductColor">${wmsColorOptions(d.productName, d.productColor)}</select></div>
            <div class="field"><label>Количество</label><input id="wmsQuantity" type="number" min="1" step="1" value="${escapeHtml(d.quantity || "")}" placeholder="0"></div>
            <div class="field"><label>Результат</label><select id="wmsTargetState">
              <option value="SCRAPPED" ${d.targetState === "SCRAPPED" ? "selected" : ""}>Списано</option>
              <option value="DAMAGED" ${d.targetState === "DAMAGED" ? "selected" : ""}>Брак</option>
              <option value="QUARANTINE" ${d.targetState === "QUARANTINE" ? "selected" : ""}>Карантин</option>
            </select></div>
            <div class="field full"><label>Причина</label><textarea id="wmsReason" rows="3" placeholder="Что произошло">${escapeHtml(d.reason || "")}</textarea></div>
          </div>
        </div>
        <div class="button-row">
          <button class="small-button" data-wms-scan="from_location">📷 Ячейка</button>
          <button class="small-button" data-wms-scan="product">📷 Товар</button>
          <button class="small-button secondary" data-wms-action="scrap">Списать</button>
        </div>
      `;
    }

    function renderAdminReports(admin) {
      ensureAdminDefaults();
      const report = getAdminReport();
      const totals = adminReportTotals(report);
      const employees = admin && admin.employees ? admin.employees : [];
      const employeeOptions = employees.map((employee) => `
        <option value="${escapeHtml(employee.id)}" ${String(employee.id) === String(state.adminEmployeeId) ? "selected" : ""}>${escapeHtml(employee.full_name)} · ${escapeHtml(employee.position)}</option>
      `).join("");
      const isEmployeeReport = state.adminReportType === "employee";
      const summaryHtml = report && report.type === "employee" ? `
        ${report.employee_summary ? `
          <div class="card report-row"><div><b>${escapeHtml(report.employee_summary.full_name)}</b><span>${escapeHtml(report.employee_summary.position)} · ${escapeHtml(report.employee_summary.shift_count)} смен · ${escapeHtml(report.employee_summary.total_time)}</span></div><span class="status-chip">сотрудник</span></div>
        ` : itemEmpty("По выбранному сотруднику нет данных.")}
      ` : `
        ${(report && report.summary && report.summary.length) ? report.summary.slice(0, 8).map((row) => `
          <div class="card report-row"><div><b>${escapeHtml(row.full_name)}</b><span>${escapeHtml(row.shift_count)} смен · ${escapeHtml(row.total_time)}</span></div><span class="status-chip gray">ID ${escapeHtml(row.employee_id)}</span></div>
        `).join("") : itemEmpty("За выбранный период закрытых смен пока нет.")}
      `;
      const shifts = report && report.type === "employee" ? (report.employee_shifts || []) : (report ? report.shifts || [] : []);
      const operations = report && report.type === "employee" ? (report.employee_operations || []) : (report ? report.operations || [] : []);
      const operationsHtml = operations.length ? operations.slice(0, 10).map((operation) => `
        <div class="card report-row"><div><b>${escapeHtml(operation.operation)}</b><span>${escapeHtml(operation.employee || "")}${operation.employee ? " · " : ""}${escapeHtml(operation.date || "")}${operation.group ? `<br>${escapeHtml(operation.group)} · ${escapeHtml(operation.size || "-")} · ${escapeHtml(operation.color || "-")}` : ""}</span></div><span class="status-chip">${escapeHtml(operation.quantity)} ${escapeHtml(operation.unit)}</span></div>
      `).join("") : itemEmpty("Операций за выбранный период пока нет.");

      mainButton.textContent = "Выгрузить отчёт";

      return `
        <div class="screen-head"><div><h2>Админ отчёты</h2><p>Сегодня, период или конкретный сотрудник.</p></div><div class="date">${escapeHtml(report ? `${report.start_date} — ${report.end_date}` : "период")}</div></div>
        ${renderAdminTabs()}
        <div class="card field-card">
          <div class="form-grid">
            <div class="field full"><label>Тип отчёта</label><select id="adminReportType"><option value="today" ${state.adminReportType === "today" ? "selected" : ""}>Сегодня</option><option value="period" ${state.adminReportType === "period" ? "selected" : ""}>Период</option><option value="employee" ${isEmployeeReport ? "selected" : ""}>Сотрудник</option></select></div>
            <div class="field"><label>Начало</label><input id="adminStartDate" type="date" value="${escapeHtml(state.adminStartDate)}"></div>
            <div class="field"><label>Окончание</label><input id="adminEndDate" type="date" value="${escapeHtml(state.adminEndDate)}"></div>
            <div class="field full"><label>Сотрудник</label><select id="adminEmployeeId">${employeeOptions || `<option value="">Нет сотрудников</option>`}</select></div>
          </div>
          <div class="button-row"><button class="small-button secondary" data-admin-action="load-report">Показать</button><button class="small-button" data-admin-action="export-report">Выгрузить</button></div>
        </div>
        <div class="kpi-grid">
          <div class="card kpi"><div class="kpi-top"><span>Смены</span><div class="kpi-ico">${uiIcon("clock")}</div></div><strong>${totals.shifts}<small> шт</small></strong><span>Закрытые смены</span></div>
          <div class="card kpi good"><div class="kpi-top"><span>Часы</span><div class="kpi-ico">${uiIcon("schedule")}</div></div><strong>${escapeHtml(minutesLabel(totals.minutes))}</strong><span>Суммарно отработано</span></div>
          <div class="card kpi"><div class="kpi-top"><span>Операции</span><div class="kpi-ico">${sewingIcon()}</div></div><strong>${totals.operations}<small> строк</small></strong><span>Строки отчёта</span></div>
          <div class="card kpi"><div class="kpi-top"><span>Сотрудники</span><div class="kpi-ico">${uiIcon("users")}</div></div><strong>${totals.employees}<small> чел</small></strong><span>В выборке</span></div>
        </div>
        <div class="section-title"><b>${escapeHtml(report ? report.title : "Отчёт")}</b><button data-admin-action="export-report">выгрузить</button></div>
        <div class="op-list">${summaryHtml}</div>
        <div class="section-title"><b>Смены</b><span>${shifts.length}</span></div>
        <div class="op-list">
          ${shifts.length ? shifts.slice(0, 8).map((shift) => `
            <div class="card report-row"><div><b>${escapeHtml(shift.employee || "Сотрудник")}</b><span>${escapeHtml(shift.date)} · ${escapeHtml(shift.start_time || "-")} — ${escapeHtml(shift.end_time || "-")}</span></div><span class="status-chip gray">${escapeHtml(shift.total_time || "-")}</span></div>
          `).join("") : itemEmpty("Смен за выбранный период нет.")}
        </div>
        <div class="section-title"><b>Операции</b><span>${operations.length}</span></div>
        <div class="op-list">${operationsHtml}</div>
      `;
    }

    function renderAdminEmployees(admin) {
      const employees = admin && admin.user_accounts ? admin.user_accounts : (admin && admin.employees ? admin.employees : []);
      const pending = admin && admin.pending_employees ? admin.pending_employees : [];
      const positions = admin && admin.positions ? admin.positions : [];
      const listedEmployees = employees.filter((employee) => employee.status !== "pending");
      const openShiftNames = new Set((admin && admin.open_shifts ? admin.open_shifts : []).map((shift) => String(shift.employee || "").trim().toLocaleLowerCase("ru")));
      const positionFilters = [...new Set(listedEmployees.map((employee) => employee.position).filter((position) => position && position !== "-"))].sort((a, b) => a.localeCompare(b, "ru"));
      const currentTelegramId = Number(state.data && state.data.employee ? state.data.employee.telegram_id : 0);
      mainButton.textContent = "Обновить сотрудников";

      if (state.employeePositionFilter && !positionFilters.includes(state.employeePositionFilter)) state.employeePositionFilter = "";
      if (!["", "active", "inactive"].includes(state.employeeStatusFilter)) state.employeeStatusFilter = "";
      if (!["", "on_shift", "off_shift"].includes(state.employeeShiftFilter)) state.employeeShiftFilter = "";

      const employeeIsOnShift = (employee) => openShiftNames.has(String(employee.full_name || "").trim().toLocaleLowerCase("ru"));
      const filteredEmployees = listedEmployees.filter((employee) => {
        const onShift = employeeIsOnShift(employee);
        if (state.employeePositionFilter && employee.position !== state.employeePositionFilter) return false;
        if (state.employeeStatusFilter === "active" && employee.status !== "active") return false;
        if (state.employeeStatusFilter === "inactive" && employee.status === "active") return false;
        if (state.employeeShiftFilter === "on_shift" && !onShift) return false;
        if (state.employeeShiftFilter === "off_shift" && onShift) return false;
        return true;
      });

      const positionOptions = (employee) => {
        const hasPosition = positions.includes(employee.position);
        return `
          <option value="" disabled ${hasPosition ? "" : "selected"}>Выберите должность</option>
          ${positions.map((position) => `
            <option value="${escapeHtml(position)}" ${employee.position === position ? "selected" : ""}>${escapeHtml(position)}</option>
          `).join("")}
        `;
      };
      const employeeContact = (employee) => {
        const contact = [employee.email, employee.phone].filter(Boolean).map(escapeHtml).join(" · ");
        if (contact) return contact;
        const telegramId = Number(employee.telegram_id || 0);
        return telegramId > 0 ? `Telegram ID ${escapeHtml(telegramId)}` : "Контакты не указаны";
      };
      const employeeStatusLabel = (status) => ({
        active: "активен",
        inactive: "отключён",
        pending: "ожидает",
        rejected: "отклонён",
      }[status] || status || "-");
      const employeeCards = filteredEmployees.length ? filteredEmployees.map((employee) => `
        <div class="card field-card">
          <label>ID ${escapeHtml(employee.id)} · ${employee.role === "admin" ? "администратор" : "сотрудник"}</label>
          <div class="report-row"><div><b>${escapeHtml(employee.full_name)}</b><span>${escapeHtml(employee.position)} · ${employeeContact(employee)}</span></div><div class="employee-statuses"><span class="status-chip ${employee.status === "active" ? "" : "gray"}">${escapeHtml(employeeStatusLabel(employee.status))}</span><span class="status-chip ${employeeIsOnShift(employee) ? "on-shift" : "gray"}">${employeeIsOnShift(employee) ? "на смене" : "не на смене"}</span>${employee.can_access_wms ? `<span class="status-chip">Кладовщик</span>` : ""}</div></div>
          ${employee.role === "admin" && Number(employee.telegram_id) === currentTelegramId ? "" : `<div class="form-grid"><div class="field full"><label>${employee.role === "admin" ? "Должность после снятия прав" : "Должность"}</label><select id="employeePosition${escapeHtml(employee.id)}">${positionOptions(employee)}</select></div></div>`}
          ${employee.role === "admin" ? `
            <div class="button-row">
              ${Number(employee.telegram_id) === currentTelegramId ? `<span class="status-chip gray">Это ваш аккаунт</span>` : `<button class="small-button secondary" data-admin-action="role-employee" data-employee-id="${escapeHtml(employee.id)}">Снять права</button><button class="small-button ${employee.status === "active" ? "danger" : ""}" data-admin-action="${employee.status === "active" ? "inactive" : "active"}" data-employee-id="${escapeHtml(employee.id)}">${employee.status === "active" ? "Отключить" : "Активировать"}</button>`}
            </div>
          ` : `
            <div class="button-row"><button class="small-button secondary" data-admin-action="position" data-employee-id="${escapeHtml(employee.id)}">Сохранить должность</button><button class="small-button ${employee.status === "active" ? "danger" : ""}" data-admin-action="${employee.status === "active" ? "inactive" : "active"}" data-employee-id="${escapeHtml(employee.id)}">${employee.status === "active" ? "Отключить" : "Активировать"}</button></div>
            <div class="button-row"><button class="small-button ${employee.can_access_wms ? "danger" : "secondary"}" data-admin-action="${employee.can_access_wms ? "wms-revoke" : "wms-grant"}" data-employee-id="${escapeHtml(employee.id)}">${employee.can_access_wms ? "Снять права кладовщика" : "Назначить кладовщиком"}</button></div>
            <div class="button-row"><button class="small-button" data-admin-action="role-admin" data-employee-id="${escapeHtml(employee.id)}">Назначить администратором</button><button class="small-button danger" data-admin-action="delete-employee" data-employee-id="${escapeHtml(employee.id)}" data-employee-name="${escapeHtml(employee.full_name)}">Удалить</button></div>
          `}
        </div>
      `).join("") : itemEmpty("По выбранным фильтрам сотрудников нет.");
      const pendingCards = pending.length ? pending.map((employee) => `
        <div class="card field-card">
          <label>Заявка · ${escapeHtml(employee.registered_at || "")}</label>
          <div class="report-row"><div><b>${escapeHtml(employee.full_name)}</b><span>${employeeContact(employee)}</span></div><span class="status-chip warn">ожидает</span></div>
          <div class="form-grid"><div class="field full"><label>Должность</label><select id="employeePosition${escapeHtml(employee.id)}">${positionOptions(employee)}</select></div></div>
          <div class="button-row"><button class="small-button secondary" data-admin-action="inactive" data-employee-id="${escapeHtml(employee.id)}">Отклонить</button><button class="small-button" data-admin-action="approve" data-employee-id="${escapeHtml(employee.id)}">Назначить и активировать</button><button class="small-button danger" data-admin-action="delete-employee" data-employee-id="${escapeHtml(employee.id)}" data-employee-name="${escapeHtml(employee.full_name)}">Удалить</button></div>
        </div>
      `).join("") : itemEmpty("Новых заявок нет.");

      return `
        <div class="screen-head"><div><h2>Пользователи</h2><p>Заявки, роли, статусы и должности.</p></div><div class="date">${employees.length} всего</div></div>
        ${renderAdminTabs()}
        <div class="kpi-grid">
          <div class="card kpi"><div class="kpi-top"><span>Заявки</span><div class="kpi-ico">${uiIcon("inbox")}</div></div><strong>${pending.length}<small> шт</small></strong><span>Ожидают решения</span></div>
          <div class="card kpi good"><div class="kpi-top"><span>Активные</span><div class="kpi-ico">${uiIcon("quality")}</div></div><strong>${(admin.active_employees || []).length}<small> чел</small></strong><span>Могут работать</span></div>
        </div>
        <div class="section-title"><b>Заявки</b><span>${pending.length}</span></div>
        <div class="op-list">${pendingCards}</div>
        <div class="card field-card employee-filter-panel">
          <div class="form-grid employee-filter-grid">
            <div class="field"><label>Должность</label><select id="employeePositionFilter"><option value="">Все должности</option>${positionFilters.map((position) => `<option value="${escapeHtml(position)}" ${state.employeePositionFilter === position ? "selected" : ""}>${escapeHtml(position)}</option>`).join("")}</select></div>
            <div class="field"><label>Статус</label><select id="employeeStatusFilter"><option value="">Все статусы</option><option value="active" ${state.employeeStatusFilter === "active" ? "selected" : ""}>Активные</option><option value="inactive" ${state.employeeStatusFilter === "inactive" ? "selected" : ""}>Неактивные</option></select></div>
            <div class="field"><label>Текущая смена</label><select id="employeeShiftFilter"><option value="">Все сотрудники</option><option value="on_shift" ${state.employeeShiftFilter === "on_shift" ? "selected" : ""}>Сейчас на смене</option><option value="off_shift" ${state.employeeShiftFilter === "off_shift" ? "selected" : ""}>Сейчас не на смене</option></select></div>
          </div>
          <div class="button-row employee-filter-actions"><span class="status-chip gray">Найдено: ${filteredEmployees.length} из ${listedEmployees.length}</span><button class="small-button secondary" data-admin-action="clear-employee-filters">Сбросить фильтры</button></div>
        </div>
        <div class="section-title"><b>Все пользователи</b><button data-admin-action="refresh">обновить</button></div>
        <div class="op-list">${employeeCards}</div>
      `;
    }

    function renderAdminShifts(admin) {
      const openShifts = admin && admin.open_shifts ? admin.open_shifts : [];
      const recentShifts = admin && admin.recent_shifts ? admin.recent_shifts : [];
      mainButton.textContent = "Обновить смены";

      return `
        <div class="screen-head"><div><h2>Смены</h2><p>Открытые и последние смены сотрудников.</p></div><div class="date">${openShifts.length} открыто</div></div>
        ${renderAdminTabs()}
        <div class="card field-card">
          <div class="form-grid"><div class="field full"><label>Время закрытия</label><input id="adminShiftEndTime" type="time" value="${escapeHtml(state.adminShiftEndTime)}"></div></div>
        </div>
        <div class="section-title"><b>Открытые смены</b><span>${openShifts.length}</span></div>
        <div class="op-list">
          ${openShifts.length ? openShifts.map((shift) => `
            <div class="card field-card"><label>ID ${escapeHtml(shift.id)}</label><div class="report-row"><div><b>${escapeHtml(shift.employee)}</b><span>${escapeHtml(shift.date)} · начало ${escapeHtml(shift.start_time)}</span></div><span class="status-chip">open</span></div><div class="button-row"><button class="small-button secondary" data-admin-action="refresh">Обновить</button><button class="small-button" data-admin-action="close-shift" data-shift-id="${escapeHtml(shift.id)}">Закрыть</button></div></div>
          `).join("") : itemEmpty("Открытых смен сейчас нет.")}
        </div>
        <div class="section-title"><b>Последние смены</b><button data-admin-action="refresh">обновить</button></div>
        <div class="op-list">
          ${recentShifts.length ? recentShifts.map((shift) => `
            <div class="card field-card"><label>ID ${escapeHtml(shift.id)} · ${escapeHtml(shift.status)}</label><div class="report-row"><div><b>${escapeHtml(shift.employee)}</b><span>${escapeHtml(shift.date)} · ${escapeHtml(shift.start_time || "-")} — ${escapeHtml(shift.end_time || "-")}<br>Операций: ${escapeHtml(shift.operation_count || 0)}</span></div><span class="status-chip gray">${escapeHtml(shift.status)}</span></div><div class="button-row"><button class="small-button secondary" data-admin-action="refresh">Обновить</button><button class="small-button danger" data-admin-action="delete-shift" data-shift-id="${escapeHtml(shift.id)}">Удалить</button></div></div>
          `).join("") : itemEmpty("Последних смен пока нет.")}
        </div>
      `;
    }

    function renderAdminFeedback(admin) {
      ensureAdminDefaults();
      const feedback = admin && admin.feedback ? admin.feedback : [];
      mainButton.textContent = "Обновить связь";

      return `
        <div class="screen-head"><div><h2>Связь</h2><p>Сообщения сотрудников за выбранный период.</p></div><div class="date">${feedback.length} сообщений</div></div>
        ${renderAdminTabs()}
        <div class="card field-card">
          <div class="form-grid">
            <div class="field"><label>Начало</label><input id="adminStartDate" type="date" value="${escapeHtml(state.adminStartDate)}"></div>
            <div class="field"><label>Окончание</label><input id="adminEndDate" type="date" value="${escapeHtml(state.adminEndDate)}"></div>
          </div>
          <div class="button-row"><button class="small-button secondary" data-admin-action="refresh">Обновить всё</button><button class="small-button" data-admin-action="load-feedback">Показать связь</button></div>
        </div>
        <div class="op-list">
          ${feedback.length ? feedback.map((row) => `
            <div class="card report-row"><div><b>${escapeHtml(row.employee)} · ${escapeHtml(row.category)}</b><span>${escapeHtml(row.date)} ${escapeHtml(row.time || "")} · ${escapeHtml(row.position)}<br>${escapeHtml(row.message)}</span></div><span class="status-chip gray">${row.shift_id ? `#${escapeHtml(row.shift_id)}` : "-"}</span></div>
          `).join("") : itemEmpty("Сообщений за выбранный период нет.")}
        </div>
      `;
    }

    function renderAdmin() {
      if (!state.data || !state.data.is_admin) {
        mainButton.textContent = "Обновить";
        mainButton.disabled = false;
        mount.innerHTML = `
          <div class="screen-head"><div><h2>Админ</h2><p>Раздел доступен только администратору.</p></div></div>
          <div class="card field-card">${itemEmpty("Нет прав администратора.")}</div>
        `;
        return;
      }

      ensureAdminDefaults();
      const admin = getAdmin();
      mainButton.disabled = false;

      if (state.adminSection === "employees") {
        mount.innerHTML = renderAdminEmployees(admin);
        return;
      }
      if (state.adminSection === "size_markers") {
        mount.innerHTML = renderAdminSizeMarkers(admin);
        return;
      }
      if (state.adminSection === "operations") {
        mount.innerHTML = renderAdminOperations(admin);
        return;
      }
      if (state.adminSection === "shifts") {
        mount.innerHTML = renderAdminShifts(admin);
        return;
      }
      if (state.adminSection === "feedback") {
        mount.innerHTML = renderAdminFeedback(admin);
        return;
      }

      mount.innerHTML = renderAdminReports(admin);
    }

    function renderProfile() {
      const employee = state.data && state.data.employee ? state.data.employee : {};
      const fullName = webSessionProfile.full_name || employee.full_name || "Пользователь";
      const position = webSessionProfile.position || employee.position || "Сотрудник";
      const role = webSessionProfile.role === "admin" || state.data.is_admin ? "Администратор" : "Сотрудник";
      mainButton.textContent = "Вернуться";
      mainButton.disabled = false;
      mount.innerHTML = `
        <div class="screen-head"><div><h2>Профиль</h2><p>Учётная запись и безопасность.</p></div><div class="date">${escapeHtml(role)}</div></div>
        <div class="card field-card">
          <label>Пользователь</label>
          <div class="report-row"><div><b>${escapeHtml(fullName)}</b><span>${escapeHtml(position)}</span></div><span class="status-chip">активен</span></div>
          <div class="op-list">
            <div class="report-row"><div><b>Электронная почта</b><span>${escapeHtml(webSessionProfile.email || webSessionProfile.username || "Не указана")}</span></div></div>
            <div class="report-row"><div><b>Телефон</b><span>${escapeHtml(webSessionProfile.phone || "Не указан")}</span></div></div>
          </div>
        </div>
        <div class="card field-card">
          <label>Сменить пароль</label>
          <div class="form-grid">
            <div class="field full"><label>Текущий пароль</label><input id="profileCurrentPassword" type="password" autocomplete="current-password" maxlength="128"></div>
            <div class="field full"><label>Новый пароль</label><input id="profileNewPassword" type="password" autocomplete="new-password" minlength="10" maxlength="128"></div>
            <div class="field full"><label>Повторите новый пароль</label><input id="profileNewPasswordConfirm" type="password" autocomplete="new-password" minlength="10" maxlength="128"></div>
          </div>
          <div class="button-row"><button class="small-button secondary" data-profile-action="logout">Выйти</button><button class="small-button" data-profile-action="password">Сменить пароль</button></div>
        </div>
      `;
    }

    function render() {
      if (!state.data) return;
      if (state.screen === "wms") {
        state.workspace = "warehouse";
        state.screen = "warehouse";
      }
      if (!canAccessWms() && state.workspace === "warehouse") {
        state.workspace = "production";
        state.screen = "shift";
      }
      if (!canAccessMarketplaces() && state.workspace === "marketplaces") {
        state.workspace = "production";
        state.screen = "shift";
      }
      if (!['production', 'warehouse', 'marketplaces'].includes(state.workspace)) {
        state.workspace = state.screen === "warehouse" ? "warehouse" : "production";
      }
      if (state.workspace === "warehouse" && !["warehouse", "profile"].includes(state.screen)) {
        state.screen = "warehouse";
      }
      if (state.workspace === "marketplaces") state.screen = "marketplaces";

      const allowedProductionScreens = state.data.is_admin
        ? ["shift", "analytics", "orders", "admin", "passport", "profile"]
        : ["shift", "report", "analytics", "orders", "admin", "passport", "profile"];
      if (state.workspace === "production" && !allowedProductionScreens.includes(state.screen)) {
        state.screen = "shift";
      }
      document.getElementById("roleLabel").textContent = roleLabel();
      const isWarehouseWorkspace = state.workspace === "warehouse";
      const isMarketplaceWorkspace = state.workspace === "marketplaces";
      if (!isMarketplaceWorkspace) mainButton.hidden = false;
      document.body.classList.toggle("warehouse-workspace", isWarehouseWorkspace);
      document.body.classList.toggle("warehouse-v2-enabled", Boolean(isWarehouseWorkspace && state.data.features && state.data.features.warehouse_ui_v2));
      document.body.classList.toggle("marketplace-workspace", isMarketplaceWorkspace);
      document.body.classList.toggle("has-wms-access", canAccessWms());
      const mobileWorkspaceNav = document.getElementById("mobileWorkspaceNav");
      mobileWorkspaceNav.hidden = !canAccessWms();
      document.querySelectorAll("[data-workspace]").forEach((button) => {
        if (button.dataset.workspace === "warehouse") button.hidden = !canAccessWms();
        if (button.dataset.workspace === "marketplaces") button.hidden = !canAccessMarketplaces();
        const isActive = button.dataset.workspace === "warehouse" ? isWarehouseWorkspace : button.dataset.workspace === "marketplaces" ? isMarketplaceWorkspace : !isWarehouseWorkspace && !isMarketplaceWorkspace;
        button.classList.toggle("active", isActive);
        if (isActive) button.setAttribute("aria-current", "page");
        else button.removeAttribute("aria-current");
      });
      if (state.screen === "shift") renderShift();
      if (state.screen === "operations") renderOperations();
      if (state.screen === "report") renderReport();
      if (state.screen === "warehouse") renderWarehouse();
      if (state.screen === "marketplaces") renderMarketplaces();
      if (state.screen === "wms") renderWms();
      if (state.screen === "analytics") renderAnalytics();
      if (state.screen === "orders") renderOrders();
      if (state.screen === "admin") renderAdmin();
      if (state.screen === "passport") renderPassport();
      if (state.screen === "profile") renderProfile();
      renderBottomNav();
      renderTopTabs();
      persistUiState();
      if (isWarehouseWorkspace && !state.wmsData.loaded && !state.wmsData.loading && !state.wmsData.error) {
        window.setTimeout(() => refreshWmsWorkspace({silent: true}), 0);
      }
      if (isWarehouseWorkspace && state.wmsView === "products" && !state.wmsCatalog.loaded && !state.wmsCatalog.loading && !state.wmsCatalog.error) {
        window.setTimeout(() => refreshWmsCatalog({silent: true}), 0);
      }
      if (isMarketplaceWorkspace && !state.marketplaceData.loaded && !state.marketplaceData.loading && !state.marketplaceData.error) {
        window.setTimeout(() => refreshMarketplaces({silent: true}), 0);
      }
      if (state.data.is_admin && state.workspace === "production" && state.screen === "shift") window.setTimeout(syncWebPushDeviceState, 0);
    }

    function setScreen(screen) {
      if (screen === "warehouse" || screen === "wms") {
        switchWorkspace("warehouse");
        return;
      }
      if (screen === "marketplaces") {
        switchWorkspace("marketplaces");
        return;
      }
      if (state.workspace === "warehouse" && screen !== "profile") state.workspace = "production";
      state.screen = screen;
      if (state.workspace === "production" && !["profile", "passport"].includes(screen) && productionScreens.has(screen)) {
        state.productionScreen = screen;
      }
      render();
    }

    function switchWorkspace(workspace) {
      if (workspace === "warehouse") {
        if (!canAccessWms()) {
          showToast("Склад", "Нет доступа к складским операциям.");
          return;
        }
        if (state.workspace === "production" && !["profile", "passport"].includes(state.screen) && productionScreens.has(state.screen)) {
          state.productionScreen = state.screen;
        }
        state.workspace = "warehouse";
        state.screen = "warehouse";
      } else if (workspace === "marketplaces") {
        if (!canAccessMarketplaces()) {
          showToast("Маркетплейсы", "Раздел доступен только администратору.");
          return;
        }
        if (state.workspace === "production" && !["profile", "passport"].includes(state.screen) && productionScreens.has(state.screen)) {
          state.productionScreen = state.screen;
        }
        state.workspace = "marketplaces";
        state.screen = "marketplaces";
      } else {
        state.workspace = "production";
        const allowed = state.data && state.data.is_admin
          ? new Set(["shift", "analytics", "orders", "admin"])
          : new Set(["shift", "report", "analytics", "orders", "admin"]);
        state.screen = allowed.has(state.productionScreen) ? state.productionScreen : "shift";
      }
      render();
    }

    async function refreshState(message = "") {
      const actionKey = "refresh-state";
      if (!beginAction(actionKey)) return;
      mainButton.disabled = true;
      try {
        const data = await api("/api/app/state", {message});

        if (state.screen === "report" && state.reportSection === "done" && state.userStartDate && state.userEndDate && !data.is_admin) {
          try {
            const history = await api("/api/report/history", getHistoryPayload());
            if (history.ok) data.history = history;
          } catch (error) {
            // The current app state is still usable when only the saved period fails to refresh.
          }
        }

        if (state.screen === "admin" && state.adminSection === "reports" && data.is_admin && data.admin && state.adminStartDate && state.adminEndDate) {
          try {
            const report = await api("/api/admin/report", getAdminReportPayload());
            if (report.ok) {
              data.admin.reports = report.report;
              state.adminAppliedReportPayload = {...getAdminReportPayload()};
            }
          } catch (error) {
            // Keep the dashboard response and let the administrator retry the report separately.
          }
        }

        state.data = data;
        if (message) showToast("Готово", message);
        render();
        if (getCompletionQueue().length && navigator.onLine) window.setTimeout(() => flushCompletionQueue(true), 0);
      } catch (error) {
        state.data = null;
        document.getElementById("roleLabel").textContent = "Нет соединения";
        mount.innerHTML = `<div class="screen-head"><div><h2>Не удалось загрузить приложение</h2><p>${escapeHtml(error.apiMessage || "Проверьте соединение и повторите попытку.")}</p></div></div>`;
        topTabs.hidden = true;
        bottomNav.innerHTML = "";
        mainButton.textContent = "Повторить";
        mainButton.disabled = false;
        showToast("Ошибка", error.apiMessage || "Не удалось связаться с сервером.");
      } finally {
        endAction(actionKey);
      }
    }

    async function shiftAction(action) {
      const actionKey = `shift-action:${action}`;
      if (!beginAction(actionKey)) return;
      mainButton.disabled = true;
      try {
        const shiftData = await api(`/api/shift/${action}`);
        state.data = shiftData;
        render();
        showToast("Смена", shiftData.message || "Данные обновлены.");
        if (action === "open" && shiftData.shift_close_reminder) {
          window.setTimeout(() => showShiftCloseReminder(shiftData.shift_close_reminder), 120);
        }
      } catch (error) {
        showToast("Ошибка", "Не удалось обновить смену.");
        mainButton.disabled = false;
      } finally {
        endAction(actionKey);
      }
    }

    document.addEventListener("click", (event) => {
      const pushAction = event.target.closest("[data-push-action]");
      if (pushAction) {
        if (pushAction.dataset.pushAction === "enable") enableAdminWebPush();
        if (pushAction.dataset.pushAction === "disable") disableAdminWebPush();
        if (pushAction.dataset.pushAction === "test") testAdminWebPush();
        return;
      }

      const criticalNotification = event.target.closest("[data-critical-notification]");
      if (criticalNotification) {
        const notificationId = Number(criticalNotification.dataset.criticalNotification || 0);
        api("/api/admin/critical-notification/acknowledge", {notification_id: notificationId})
          .then((data) => replaceAdminDashboard(data, data.message || "Уведомление обработано."))
          .catch(() => showToast("Критично", "Не удалось обновить уведомление."));
        return;
      }

      const cuttingAction = event.target.closest("[data-cutting-action]");
      if (cuttingAction) {
        if (cuttingAction.dataset.cuttingAction === "release") {
          const taskId = Number(cuttingAction.dataset.cuttingTaskId || 0);
          const task = getMyCuttingTasks().find((row) => Number(row.id) === taskId);
          releaseCuttingTask(task);
        }
        return;
      }

      const cuttingTaskForArbitrary = getMyCuttingTasks()[state.selectedCuttingReportTask] || getMyCuttingTasks()[0];
      const arbitraryAdd = event.target.closest("[data-arbitrary-add]");
      if (arbitraryAdd && cuttingTaskForArbitrary && cuttingTaskForArbitrary.stage === "layout") {
        syncCuttingArbitraryDraftFromDom(cuttingTaskForArbitrary);
        const key = cuttingDraftKey(cuttingTaskForArbitrary);
        const draft = state.cuttingStageDrafts[key] || {};
        const sizes = cuttingArbitrarySizes(cuttingTaskForArbitrary);
        draft.arbitrary_operations = Array.isArray(draft.arbitrary_operations) ? draft.arbitrary_operations : [];
        draft.arbitrary_operations.push({
          product_size: sizes[0] || "",
          product_color: (cuttingTaskForArbitrary.colors || [])[0] || "",
          parts_count: 2,
          layers: "",
        });
        state.cuttingStageDrafts[key] = draft;
        persistUiState();
        render();
        return;
      }

      const arbitraryRemove = event.target.closest("[data-arbitrary-remove]");
      if (arbitraryRemove && cuttingTaskForArbitrary && cuttingTaskForArbitrary.stage === "layout") {
        syncCuttingArbitraryDraftFromDom(cuttingTaskForArbitrary);
        const key = cuttingDraftKey(cuttingTaskForArbitrary);
        const draft = state.cuttingStageDrafts[key] || {};
        const index = Number(arbitraryRemove.dataset.arbitraryRemove || -1);
        if (Array.isArray(draft.arbitrary_operations) && index >= 0) draft.arbitrary_operations.splice(index, 1);
        state.cuttingStageDrafts[key] = draft;
        persistUiState();
        render();
        return;
      }

      const taskAction = event.target.closest("[data-task-action]");
      if (taskAction) {
        const action = taskAction.dataset.taskAction;
        if (action === "scan") {
          scanRouteQr();
          return;
        }
        const taskId = Number(taskAction.dataset.taskId || 0);
        const task = getRouteTasks().find((row) => Number(row.id) === taskId) || getCompletedRouteTasks().find((row) => Number(row.id) === taskId);
        if (action === "passport") {
          openRoutePassport(taskId);
          return;
        }
        if (action === "all-good" && task) {
          const goodInput = document.getElementById("taskGoodQuantity");
          const defectInput = document.getElementById("taskDefectQuantity");
          if (goodInput) goodInput.value = task.quantity;
          if (defectInput) defectInput.value = "0";
          const details = document.getElementById("taskDefectDetails");
          if (details) details.style.display = "none";
          const draft = state.taskCompletionDrafts[task.id] || {request_id: createRequestId()};
          draft.good = String(task.quantity);
          draft.defect = "0";
          state.taskCompletionDrafts[task.id] = draft;
          persistUiState();
          return;
        }
        if (["pause", "block", "resume", "release"].includes(action)) {
          updateRouteTaskState(task, action);
          return;
        }
      }

      const orderMode = event.target.closest("[data-order-mode]");
      if (orderMode && state.data && state.data.is_admin) {
        if (orderMode.dataset.orderMode === "create") {
          resetOrderDraft();
        } else {
          state.orderMode = "list";
        }
        render();
        return;
      }

      const adminTaskStatus = event.target.closest("[data-admin-task-status]");
      if (adminTaskStatus && state.data) {
        state.adminTaskStatus = adminTaskStatus.dataset.adminTaskStatus || "all";
        state.selectedOrder = 0;
        state.selectedOrderKey = "";
        persistUiState();
        render();
        return;
      }

      const orderAction = event.target.closest("[data-order-action]");
      if (orderAction) {
        if (orderAction.dataset.orderAction === "clear-filters") {
          state.orderProductFilter = "";
          state.orderSizeFilter = "";
          state.orderColorFilter = "";
          state.selectedOrder = 0;
          state.selectedOrderKey = "";
          persistUiState();
          render();
          return;
        }
        syncOrderDraft();
        if (orderAction.dataset.orderAction === "new") {
          resetOrderDraft();
          render();
        }
        if (orderAction.dataset.orderAction === "cancel") {
          state.orderMode = "list";
          render();
        }
        if (orderAction.dataset.orderAction === "create") {
          createOrderTask();
        }
        if (orderAction.dataset.orderAction === "release-cutting") {
          const rows = currentOrderRows();
          const current = rows.find((task) => task.task_kind === orderAction.dataset.taskKind && String(task.id) === String(orderAction.dataset.taskId));
          releaseCuttingTask(current);
        }
        if (orderAction.dataset.orderAction === "delete") {
          deleteOrderTask(orderAction.dataset.taskKind, orderAction.dataset.taskId);
        }
        return;
      }

      const orderSize = event.target.closest("[data-order-size]");
      if (orderSize) {
        syncOrderDraft();
        toggleOrderValue("size", orderSize.dataset.orderSize);
        return;
      }

      const orderProduct = event.target.closest("[data-order-product]");
      if (orderProduct) {
        syncOrderDraft();
        toggleOrderValue("product", orderProduct.dataset.orderProduct);
        return;
      }

      const orderColor = event.target.closest("[data-order-color]");
      if (orderColor) {
        syncOrderDraft();
        toggleOrderValue("color", orderColor.dataset.orderColor);
        return;
      }

      const stockAction = event.target.closest("[data-stock-action]");
      if (stockAction) {
        syncOrderDraft();
        document.querySelectorAll("[data-stock-quantity]").forEach((input) => {
          input.value = stockAction.dataset.stockAction === "all" ? input.max || "1" : "";
          state.orderStockQuantities[input.dataset.stockQuantity] = input.value;
        });
        render();
        return;
      }

      const stockAdjustment = event.target.closest("[data-stock-adjust-id]");
      if (stockAdjustment) {
        adjustWarehouseStock(
          stockAdjustment.dataset.stockAdjustKind,
          Number(stockAdjustment.dataset.stockAdjustId || 0),
          Number(stockAdjustment.dataset.stockAdjustQuantity || 0),
          stockAdjustment.dataset.stockAdjustLabel || "остаток",
        );
        return;
      }

      const fabricDefect = event.target.closest("[data-fabric-defect-task-id]");
      if (fabricDefect) {
        rejectFabricRolls(
          Number(fabricDefect.dataset.fabricDefectTaskId || 0),
          fabricDefect.dataset.fabricDefectColor || "",
          Number(fabricDefect.dataset.fabricDefectAvailable || 0),
        );
        return;
      }

      const warehouseAction = event.target.closest("[data-warehouse-action]");
      if (warehouseAction) {
        syncWarehouseReceiptForm();
        if (warehouseAction.dataset.warehouseAction === "receipt") {
          addFabricReceipt();
        }
        if (warehouseAction.dataset.warehouseAction === "refresh") {
          refreshState("Склад обновлён.");
        }
        if (warehouseAction.dataset.warehouseAction === "overview") {
          state.warehouseView = "overview";
          resetWarehouseFilters();
          render();
        }
        if (warehouseAction.dataset.warehouseAction === "clear-filters") {
          resetWarehouseFilters();
          render();
        }
        return;
      }

      const warehouseView = event.target.closest("[data-warehouse-view]");
      if (warehouseView) {
        state.warehouseView = warehouseView.dataset.warehouseView;
        resetWarehouseFilters();
        render();
        return;
      }

      const wmsStockFilter = event.target.closest("[data-wms-stock-filter]");
      if (wmsStockFilter) {
        state.wmsStockFilter = wmsStockFilter.dataset.wmsStockFilter || "finished";
        resetWmsStockFilters();
        render();
        return;
      }

      const wmsStockAction = event.target.closest("[data-wms-stock-action]");
      if (wmsStockAction && wmsStockAction.dataset.wmsStockAction === "reset-filters") {
        resetWmsStockFilters();
        render();
        return;
      }

      const wmsMapAction = event.target.closest("[data-wms-map-action]");
      if (wmsMapAction && wmsMapAction.dataset.wmsMapAction === "apply") {
        const search = document.getElementById("wmsMapSearch");
        const status = document.getElementById("wmsMapStatusFilter");
        state.wmsMapSearch = search ? search.value.trim() : "";
        state.wmsMapStatusFilter = status ? status.value : "all";
        const matched = wmsLocationByScan(state.wmsMapSearch) || (state.wmsData.locations || []).find((location) =>
          String(location.code || "").toLocaleLowerCase("ru").includes(state.wmsMapSearch.toLocaleLowerCase("ru"))
        );
        if (matched) state.wmsSelectedLocationId = matched.id;
        render();
        return;
      }

      const wmsCatalogAction = event.target.closest("[data-wms-catalog-action]");
      if (wmsCatalogAction) {
        const search = document.getElementById("wmsCatalogSearch");
        if (search) state.wmsCatalogSearch = search.value.trim();
        if (wmsCatalogAction.dataset.wmsCatalogAction === "groups") {
          state.wmsCatalogGroup = "";
          render();
        } else if (wmsCatalogAction.dataset.wmsCatalogAction === "refresh") {
          state.wmsCatalog.loaded = false;
          refreshWmsCatalog();
        } else {
          render();
        }
        return;
      }

      const wmsCatalogGroup = event.target.closest("[data-wms-catalog-group]");
      if (wmsCatalogGroup) {
        state.wmsCatalogGroup = wmsCatalogGroup.dataset.wmsCatalogGroup || "";
        render();
        return;
      }

      const wmsReport = event.target.closest("[data-wms-report]");
      if (wmsReport) {
        downloadWmsReport(wmsReport.dataset.wmsReport);
        return;
      }

      const wmsCell = event.target.closest("[data-wms-cell-id]");
      if (wmsCell) {
        state.wmsSelectedLocationId = wmsCell.dataset.wmsCellId || "";
        state.workspace = "warehouse";
        state.screen = "warehouse";
        state.wmsView = state.wmsView === "map" ? "map" : "stock";
        render();
        return;
      }

      const wmsMaterialPutaway = event.target.closest("[data-wms-material-putaway]");
      if (wmsMaterialPutaway) {
        const materialRows = wmsReceivingMaterials();
        const row = materialRows[Number(wmsMaterialPutaway.dataset.wmsMaterialPutaway || -1)];
        if (row && row.product_key) {
          const product = row.product_key;
          state.wmsDraft.itemType = "material";
          state.wmsDraft.productName = product.product_name || "";
          state.wmsDraft.productSize = product.product_size || "—";
          state.wmsDraft.productColor = product.product_color || "";
          state.wmsDraft.stageName = product.stage_name || "Материал";
          state.wmsDraft.readyForPosition = product.ready_for_position || "Склад";
          state.wmsDraft.materialUnit = row.unit || "рул";
          state.wmsDraft.quantity = "";
          state.wmsDraft.toLocation = "";
          state.wmsDraft.toLocationScanned = false;
          state.wmsDraft.productScanned = true;
          state.workspace = "warehouse";
          state.screen = "warehouse";
          state.wmsView = "putaway";
          render();
        }
        return;
      }

      const wmsCellAction = event.target.closest("[data-wms-cell-action]");
      if (wmsCellAction) {
        const code = String(wmsCellAction.dataset.wmsCellCode || "").trim();
        const action = wmsCellAction.dataset.wmsCellAction;
        state.wmsView = action === "pick" ? "pick" : "putaway";
        state.wmsDraft.fromLocation = action === "pick" ? code : "";
        state.wmsDraft.toLocation = action === "putaway" ? code : "";
        state.wmsDraft.fromLocationScanned = action === "pick";
        state.wmsDraft.toLocationScanned = action === "putaway";
        state.wmsDraft.productScanned = false;
        state.wmsDraft.quantity = "";
        state.workspace = "warehouse";
        state.screen = "warehouse";
        render();
        return;
      }

      const wmsView = event.target.closest("[data-wms-view]");
      if (wmsView) {
        const nextView = wmsView.dataset.wmsView;
        if (nextView !== state.wmsView && ["putaway", "pick"].includes(nextView)) {
          state.wmsDraft.quantity = "";
          state.wmsDraft.productName = "";
          state.wmsDraft.productSize = "";
          state.wmsDraft.productColor = "";
          state.wmsDraft.productScanned = false;
          if (nextView === "putaway") {
            state.wmsDraft.toLocation = "";
            state.wmsDraft.toLocationScanned = false;
          }
          if (nextView === "pick") {
            state.wmsDraft.fromLocation = "";
            state.wmsDraft.fromLocationScanned = false;
          }
        }
        state.workspace = "warehouse";
        state.screen = "warehouse";
        state.wmsView = nextView;
        render();
        return;
      }

      const wmsScan = event.target.closest("[data-wms-scan]");
      const wmsReceiptProduct = event.target.closest("[data-wms-receipt-product]");
      if (wmsReceiptProduct) {
        const row = wmsReceivingStock()[Number(wmsReceiptProduct.dataset.wmsReceiptProduct || 0)];
        const pk = row && row.product_key;
        if (pk) {
          state.wmsDraft.itemType = pk.item_type || "finished";
          state.wmsDraft.productName = pk.product_name || "";
          state.wmsDraft.productSize = pk.product_size || "";
          state.wmsDraft.productColor = pk.product_color || "";
          state.wmsDraft.stageName = pk.stage_name || "Упаковано";
          state.wmsDraft.readyForPosition = pk.ready_for_position || "Склад";
          state.wmsDraft.barcode = "";
          render();
        }
        return;
      }

      if (wmsScan) {
        scanWms(wmsScan.dataset.wmsScan);
        return;
      }

      const wmsAction = event.target.closest("[data-wms-action]");
      if (wmsAction) {
        const action = wmsAction.dataset.wmsAction;
        if (action === "refresh") refreshWmsWorkspace();
        else if (action === "receive") wmsReceive();
        else if (action === "material_receive") wmsMaterialReceive();
        else if (action === "putaway") wmsPutaway();
        else if (action === "transfer") wmsTransfer();
        else if (action === "pick") wmsPick();
        else if (action === "inventory") wmsInventory();
        else if (action === "scrap") wmsScrap();
        else if (action === "register_barcode") wmsRegisterBarcode();
        else if (action === "create_location") wmsCreateLocation();
        return;
      }

      const marketplaceView = event.target.closest("[data-marketplace-view]");
      if (marketplaceView) {
        state.marketplaceView = marketplaceView.dataset.marketplaceView || "overview";
        state.marketplaceDetail = null;
        render();
        return;
      }

      const marketplaceProvider = event.target.closest("[data-marketplace-provider]");
      if (marketplaceProvider) {
        state.marketplaceProvider = ["all", "ozon", "wildberries"].includes(marketplaceProvider.dataset.marketplaceProvider)
          ? marketplaceProvider.dataset.marketplaceProvider
          : "all";
        state.marketplaceView = "overview";
        state.marketplaceDetail = null;
        render();
        return;
      }

      const marketplaceGroup = event.target.closest("[data-marketplace-group]");
      if (marketplaceGroup) {
        state.marketplaceView = "overview";
        state.marketplaceDetail = {kind: "group", key: marketplaceGroup.dataset.marketplaceGroup || ""};
        render();
        return;
      }

      const marketplaceProduct = event.target.closest("[data-marketplace-product-id]");
      if (marketplaceProduct) {
        state.marketplaceDetail = {kind: "product", id: marketplaceProduct.dataset.marketplaceProductId || ""};
        render();
        return;
      }

      const marketplaceOrder = event.target.closest("[data-marketplace-order-id]");
      if (marketplaceOrder) {
        state.marketplaceView = "orders";
        state.marketplaceDetail = {kind: "order", id: marketplaceOrder.dataset.marketplaceOrderId || ""};
        render();
        return;
      }

      const marketplaceSync = event.target.closest("[data-marketplace-sync-id]");
      if (marketplaceSync) {
        state.marketplaceView = "sync";
        state.marketplaceDetail = {kind: "sync", id: marketplaceSync.dataset.marketplaceSyncId || ""};
        render();
        return;
      }

      const marketplaceAction = event.target.closest("[data-marketplace-action]");
      if (marketplaceAction) {
        if (marketplaceAction.dataset.marketplaceAction === "back") {
          state.marketplaceDetail = null;
          render();
          return;
        }
        if (marketplaceAction.dataset.marketplaceAction === "refresh") refreshMarketplaces();
        if (marketplaceAction.dataset.marketplaceAction === "sync") syncMarketplaces();
        return;
      }

      const adminHomePeriod = event.target.closest("[data-admin-home-period]");
      if (adminHomePeriod) {
        state.adminHomePeriod = adminHomePeriod.dataset.adminHomePeriod;
        state.adminHomeView = "overview";
        state.adminHomeEmployee = "";
        render();
        return;
      }

      const orderCategory = event.target.closest("[data-order-category]");
      if (orderCategory) {
        state.orderCategory = orderCategory.dataset.orderCategory;
        state.selectedOrder = 0;
        state.selectedOrderKey = "";
        render();
        return;
      }

      const reportSection = event.target.closest("[data-report-section]");
      if (reportSection) {
        state.reportSection = reportSection.dataset.reportSection;
        state.selectedReportTask = 0;
        state.selectedReportTaskKey = "";
        state.selectedCuttingReportTask = 0;
        state.selectedCuttingReportTaskKey = "";
        render();
        return;
      }

      const adminHomeView = event.target.closest("[data-admin-home-view]");
      if (adminHomeView) {
        state.adminHomeView = adminHomeView.dataset.adminHomeView;
        state.adminHomeEmployee = "";
        render();
        return;
      }

      const adminHomeEmployee = event.target.closest("[data-admin-home-employee]");
      if (adminHomeEmployee) {
        state.adminHomeEmployee = adminHomeEmployee.dataset.adminHomeEmployee;
        state.adminHomeView = "employee";
        render();
        return;
      }

      const analyticsBack = event.target.closest("[data-analytics-back]");
      if (analyticsBack) {
        state.analyticsView = "overview";
        state.analyticsStage = "";
        state.analyticsTaskId = "";
        state.analyticsReturnView = "overview";
        render();
        return;
      }

      const analyticsDelete = event.target.closest("[data-analytics-delete-task-id]");
      if (analyticsDelete) {
        deleteOrderTask(
          analyticsDelete.dataset.analyticsDeleteTaskKind || "route",
          Number(analyticsDelete.dataset.analyticsDeleteTaskId || 0),
        );
        return;
      }

      const analyticsTask = event.target.closest("[data-analytics-task-id]");
      if (analyticsTask) {
        state.analyticsReturnView = state.analyticsView === "task" ? "overview" : state.analyticsView || "overview";
        state.analyticsTaskId = analyticsTask.dataset.analyticsTaskId;
        state.analyticsView = "task";
        render();
        return;
      }

      const analyticsStage = event.target.closest("[data-analytics-stage]");
      if (analyticsStage) {
        state.analyticsStage = analyticsStage.dataset.analyticsStage;
        state.analyticsView = "stage";
        state.analyticsTaskId = "";
        render();
        return;
      }

      const analyticsView = event.target.closest("[data-analytics-view]");
      if (analyticsView) {
        state.analyticsView = analyticsView.dataset.analyticsView;
        state.analyticsStage = "";
        state.analyticsTaskId = "";
        render();
        return;
      }

      const employeeHomeDetail = event.target.closest("[data-employee-home-detail]");
      if (employeeHomeDetail) {
        state.employeeHomeView = employeeHomeDetail.dataset.employeeHomeDetail;
        render();
        return;
      }

      const employeeHomeBack = event.target.closest("[data-employee-home-back]");
      if (employeeHomeBack) {
        state.employeeHomeView = "overview";
        render();
        return;
      }

      const workspace = event.target.closest("[data-workspace]");
      if (workspace && !workspace.disabled) {
        switchWorkspace(workspace.dataset.workspace);
        return;
      }

      const go = event.target.closest("[data-go]");
      if (go) {
        if (go.dataset.reportTarget) {
          state.reportSection = go.dataset.reportTarget;
          state.selectedReportTask = 0;
          state.selectedReportTaskKey = "";
          state.selectedCuttingReportTask = 0;
          state.selectedCuttingReportTaskKey = "";
        }
        if (go.dataset.go === "shift") state.employeeHomeView = "overview";
        setScreen(go.dataset.go);
        return;
      }

      const adminSection = event.target.closest("[data-admin-section]");
      if (adminSection) {
        state.adminSection = adminSection.dataset.adminSection;
        render();
        return;
      }

      const adminAction = event.target.closest("[data-admin-action]");
      if (adminAction) {
        syncAdminForm();
        if (adminAction.dataset.adminAction === "clear-employee-filters") {
          resetEmployeeFilters();
          render();
          return;
        }
        if (adminAction.dataset.adminAction === "refresh") refreshAdminDashboard();
        if (adminAction.dataset.adminAction === "load-report") loadAdminReport();
        if (adminAction.dataset.adminAction === "export-report") exportAdminReport();
        if (adminAction.dataset.adminAction === "load-feedback") loadAdminFeedback();
        if (adminAction.dataset.adminAction === "active") adminEmployeeStatus(adminAction.dataset.employeeId, "active");
        if (adminAction.dataset.adminAction === "inactive") adminEmployeeStatus(adminAction.dataset.employeeId, "inactive");
        if (adminAction.dataset.adminAction === "approve") adminApproveEmployee(adminAction.dataset.employeeId);
        if (adminAction.dataset.adminAction === "position") adminEmployeePosition(adminAction.dataset.employeeId);
        if (adminAction.dataset.adminAction === "wms-grant") adminEmployeeWmsAccess(adminAction.dataset.employeeId, true);
        if (adminAction.dataset.adminAction === "wms-revoke") adminEmployeeWmsAccess(adminAction.dataset.employeeId, false);
        if (adminAction.dataset.adminAction === "role-admin") adminEmployeeRole(adminAction.dataset.employeeId, "admin");
        if (adminAction.dataset.adminAction === "role-employee") adminEmployeeRole(adminAction.dataset.employeeId, "employee");
        if (adminAction.dataset.adminAction === "delete-employee") adminDeleteEmployee(adminAction.dataset.employeeId, adminAction.dataset.employeeName);
        if (adminAction.dataset.adminAction === "complete-size-marker") adminSizeMarkerStatus(adminAction.dataset.sizeMarkerId, "done");
        if (adminAction.dataset.adminAction === "reopen-size-marker") adminSizeMarkerStatus(adminAction.dataset.sizeMarkerId, "open");
        if (adminAction.dataset.adminAction === "complete-route-operation") adminCompleteRouteOperation(adminAction.dataset.routeBatchId);
        if (adminAction.dataset.adminAction === "close-shift") adminCloseShift(adminAction.dataset.shiftId);
        if (adminAction.dataset.adminAction === "delete-shift") adminDeleteShift(adminAction.dataset.shiftId);
        return;
      }

      const historyAction = event.target.closest("[data-history-action]");
      if (historyAction) {
        loadHistory();
        return;
      }

      const feedbackAction = event.target.closest("[data-feedback-action]");
      if (feedbackAction) {
        sendFeedback();
        return;
      }

      const attachmentAction = event.target.closest("[data-attachment-action]");
      if (attachmentAction) {
        openTaskAttachment(attachmentAction.dataset.attachmentTaskId, attachmentAction.dataset.attachmentAction);
        return;
      }

      const profileAction = event.target.closest("[data-profile-action]");
      if (profileAction) {
        if (profileAction.dataset.profileAction === "logout") logoutWebApp();
        if (profileAction.dataset.profileAction === "password") changeWebPassword();
        return;
      }

      const reportAction = event.target.closest("[data-report-action]");
      if (reportAction) {
        if (reportAction.dataset.reportAction === "complete-task") {
          completeOperationTask(getDisplayedRouteTask());
        }
        if (reportAction.dataset.reportAction === "complete-cutting-stage") {
          const tasks = getMyCuttingTasks();
          submitCuttingStage(tasks[state.selectedCuttingReportTask] || tasks[0]);
        }
        return;
      }

      const op = event.target.closest("[data-select-operation]");
      if (op) {
        state.selectedOperation = Number(op.dataset.selectOperation);
        setScreen("operations");
        return;
      }

      const order = event.target.closest("[data-select-order]");
      if (order) {
        state.selectedOrder = Number(order.dataset.selectOrder);
        const rows = visibleOrderRows();
        const current = rows[state.selectedOrder] || rows[0];
        state.selectedOrderKey = taskIdentity(current);
        if (current && orderTaskStatusBucket(current) === "done") {
          setScreen("orders");
          return;
        }
        if (current && current.task_kind === "route" && !state.data.is_admin) {
          startOperationTask(current);
          return;
        }
        if (current && current.task_kind === "cutting_stage" && !state.data.is_admin) {
          selectCuttingTaskForReport(current);
          return;
        }
        setScreen("orders");
        return;
      }

      const reportTask = event.target.closest("[data-select-report-task]");
      if (reportTask) {
        state.selectedReportTask = Number(reportTask.dataset.selectReportTask);
        const tasks = getMyRouteTasks();
        state.selectedReportTaskKey = taskIdentity(tasks[state.selectedReportTask] || tasks[0]);
        render();
      }

      const cuttingReportTask = event.target.closest("[data-select-cutting-report-task]");
      if (cuttingReportTask) {
        state.selectedCuttingReportTask = Number(cuttingReportTask.dataset.selectCuttingReportTask);
        const tasks = getMyCuttingTasks();
        state.selectedCuttingReportTaskKey = taskIdentity(tasks[state.selectedCuttingReportTask] || tasks[0]);
        render();
      }
    });

    mainButton.addEventListener("click", () => {
      if (!state.data) { refreshState(); return; }
      if (state.screen === "profile") {
        state.screen = state.profileReturnScreen || "shift";
        render();
        return;
      }
      if (state.screen === "shift") {
        if (state.data.is_admin) {
          refreshAdminDashboard("Главная обновлена.");
          return;
        }
        if (state.employeeHomeView && state.employeeHomeView !== "overview") {
          refreshState("Данные обновлены.");
          return;
        }
        if (state.data.shift && state.data.shift.status === "closed") return;
        shiftAction(state.data.has_open_shift ? "close" : "open");
        return;
      }
      if (state.screen === "operations") { setScreen("report"); return; }
      if (state.screen === "report") {
        if (state.reportSection === "work") {
          const cuttingTasks = getMyCuttingTasks();
          const cuttingCurrent = cuttingTasks[state.selectedCuttingReportTask] || cuttingTasks[0];
          if (cuttingCurrent) { submitCuttingStage(cuttingCurrent); return; }
          const tasks = getMyRouteTasks();
          const current = tasks[state.selectedReportTask] || tasks[0];
          if (current && current.can_resume) { updateRouteTaskState(current, "resume"); return; }
          if (current) { completeOperationTask(current); return; }
        }
        refreshState("Отчёт обновлён.");
        return;
      }
      if (state.screen === "warehouse" || state.screen === "wms") {
        if (state.wmsView === "products") refreshWmsCatalog();
        else if (state.wmsView === "receive") refreshWmsWorkspace();
        else if (state.wmsView === "putaway") wmsPutaway();
        else if (state.wmsView === "transfer") wmsTransfer();
        else if (state.wmsView === "pick") wmsPick();
        else if (state.wmsView === "inventory") wmsInventory();
        else if (state.wmsView === "scrap") wmsScrap();
        else refreshWmsWorkspace();
        return;
      }
      if (state.screen === "marketplaces") {
        syncMarketplaces();
        return;
      }
      if (state.screen === "analytics") {
        if (state.data && state.data.is_admin) { refreshAdminDashboard("Контроль производства обновлён."); return; }
        setScreen("orders");
        return;
      }
      if (state.screen === "orders" && state.data && state.data.is_admin) {
        if (state.orderMode === "create") { createOrderTask(); return; }
        refreshState("Список заданий обновлён.");
        return;
      }
      if (state.screen === "orders") {
        const rows = visibleOrderRows();
        const current = rows[state.selectedOrder] || rows[0];
        if (current && current.task_kind === "cutting_stage") { selectCuttingTaskForReport(current); return; }
        if (current && current.task_kind === "route") {
          if (current.is_assigned_to_me && current.can_complete) { completeOperationTask(current); return; }
          if (current.is_assigned_to_me && current.can_resume) { updateRouteTaskState(current, "resume"); return; }
          startOperationTask(current);
          return;
        }
        refreshState("Статус обновлён.");
        return;
      }
      if (state.screen === "passport") {
        state.screen = state.passportReturnScreen || "orders";
        state.passportData = null;
        render();
        return;
      }
      if (state.screen === "admin") {
        if (state.adminSection === "reports") { exportAdminReport(); return; }
        if (state.adminSection === "feedback") { loadAdminFeedback(); return; }
        refreshAdminDashboard();
      }
    });

    document.addEventListener("keydown", (event) => {
      const scannerInput = event.target.closest("#wmsHardwareScannerInput");
      if (!scannerInput || event.key !== "Enter") return;
      event.preventDefault();
      const value = scannerInput.value.trim();
      if (!value) return;
      state.wmsScanField = scannerInput.dataset.wmsHardwareField || "product";
      scannerInput.value = "";
      handleWmsScan(value);
    });

    document.addEventListener("input", (event) => {
      if (event.target.closest("#wmsQuantity, #wmsFromLocation, #wmsToLocation, #wmsReason")) {
        readWmsDraftFromForm();
      }
      if (event.target.closest("#orderProduct, #orderTaskType, #orderRouteStep, #orderMaterial, #orderQuantity, #orderPriority, #orderDueDate, [data-stock-quantity], [data-fabric-rolls]")) {
        syncOrderDraft();
      }
      if (event.target.closest("#fabricReceiptMaterial, #fabricReceiptColor, #fabricReceiptQuantity")) {
        syncWarehouseReceiptForm();
      }
      if (event.target.closest("#wmsMaterialName, #wmsMaterialColor, #wmsMaterialUnit, #wmsMaterialQuantity, #wmsMaterialComment")) {
        syncWmsMaterialReceiptForm();
      }

      const routeTask = getDisplayedRouteTask();

      if (routeTask && event.target.closest("#taskGoodQuantity, #taskDefectQuantity, #taskDefectReason, #taskDefectDisposition, #taskDefectComment, #taskPackagingOption")) {
        const draft = state.taskCompletionDrafts[routeTask.id] || {};
        if (event.target.id === "taskGoodQuantity") draft.good = event.target.value;
        if (event.target.id === "taskDefectQuantity") {
          draft.defect = event.target.value;
          const defectDetails = document.getElementById("taskDefectDetails");
          if (defectDetails) defectDetails.style.display = Number(event.target.value || 0) > 0 ? "block" : "none";
        }
        if (event.target.id === "taskDefectReason") draft.defect_reason = event.target.value;
        if (event.target.id === "taskDefectDisposition") draft.defect_disposition = event.target.value;
        if (event.target.id === "taskDefectComment") draft.defect_comment = event.target.value;
        if (event.target.id === "taskPackagingOption") draft.packaging_option = event.target.value;
        state.taskCompletionDrafts[routeTask.id] = draft;
      }

      const cuttingTasks = getMyCuttingTasks();
      const cuttingTask = cuttingTasks[state.selectedCuttingReportTask] || cuttingTasks[0];

      if (cuttingTask && (event.target.matches("[data-contour-key]") || event.target.matches("[data-layer-color]") || event.target.matches("[data-arbitrary-size], [data-arbitrary-color], [data-arbitrary-parts], [data-arbitrary-layers]") || event.target.id === "cuttingProgress")) {
        const key = cuttingDraftKey(cuttingTask);
        const draft = state.cuttingStageDrafts[key] || {};
        if (event.target.dataset.contourKey) {
          draft.quantities = draft.quantities || {};
          draft.quantities[event.target.dataset.contourKey] = event.target.value;
        }
        if (event.target.dataset.layerColor) {
          draft.color_layers = draft.color_layers || {};
          draft.color_layers[event.target.dataset.layerColor] = event.target.value;
        }
        if (event.target.closest("[data-arbitrary-row]")) {
          draft.arbitrary_operations = readCuttingArbitraryRowsFromDom();
        }
        if (event.target.id === "cuttingProgress") draft.progress = event.target.value;
        state.cuttingStageDrafts[key] = draft;
      }

      if (event.target.id === "feedbackCategory") state.feedbackDraft.category = event.target.value;
      if (event.target.id === "feedbackMessage") state.feedbackDraft.message = event.target.value;

      if (event.target.closest("#adminStartDate, #adminEndDate, #adminEmployeeId, #adminShiftEndTime")) {
        syncAdminForm();
        if (event.target.id === "adminShiftEndTime") state.adminShiftEndTime = event.target.value;
      }
      if (event.target.closest("#userStartDate, #userEndDate")) syncHistoryForm();
      persistUiState();
    });

    document.addEventListener("change", (event) => {
      if (event.target.closest("#wmsProductName")) {
        readWmsDraftFromForm();
        state.wmsDraft.productScanned = false;
        state.wmsDraft.productSize = "";
        state.wmsDraft.productColor = "";
        render();
        return;
      }

      if (event.target.closest("#wmsProductSize, #wmsProductColor, #wmsItemType, #wmsTargetState, #wmsLocationZone")) {
        readWmsDraftFromForm();
        return;
      }

      const defectPhotoInput = event.target.closest("#taskDefectPhoto");
      if (defectPhotoInput) {
        const task = getDisplayedRouteTask();
        readDefectPhoto(defectPhotoInput.files && defectPhotoInput.files[0], task).catch(() => {
          showToast("Фото брака", "Не удалось прочитать фотографию.");
        });
        return;
      }

      const orderFilter = event.target.closest("[data-order-filter]");
      if (orderFilter) {
        const filterName = orderFilter.dataset.orderFilter;
        if (filterName === "product") state.orderProductFilter = orderFilter.value;
        if (filterName === "size") state.orderSizeFilter = orderFilter.value;
        if (filterName === "color") state.orderColorFilter = orderFilter.value;
        state.selectedOrder = 0;
        state.selectedOrderKey = "";
        persistUiState();
        render();
        return;
      }

      const attachmentInput = event.target.closest("#orderAttachment");
      if (attachmentInput) {
        readOrderAttachment(attachmentInput.files && attachmentInput.files[0]);
        return;
      }

      if (event.target.closest("#fabricReceiptMaterial") || event.target.closest("#fabricReceiptColor") || event.target.closest("#fabricReceiptQuantity")) {
        syncWarehouseReceiptForm();
        return;
      }
      if (event.target.closest("#wmsMaterialName, #wmsMaterialColor, #wmsMaterialUnit, #wmsMaterialQuantity, #wmsMaterialComment")) {
        syncWmsMaterialReceiptForm();
        return;
      }

      if (event.target.closest("#wmsStockFilter, #wmsStockProductFilter, #wmsStockSizeFilter, #wmsStockColorFilter")) {
        syncWmsStockFilters();
        if (event.target.id === "wmsStockFilter") resetWmsStockFilters();
        render();
        return;
      }

      if (event.target.closest("#warehouseProductFilter") || event.target.closest("#warehouseSizeFilter") || event.target.closest("#warehouseColorFilter")) {
        syncWarehouseFilters();
        render();
        return;
      }

      if (event.target.closest("#employeePositionFilter") || event.target.closest("#employeeStatusFilter") || event.target.closest("#employeeShiftFilter")) {
        syncEmployeeFilters();
        render();
        return;
      }

      const stockToggle = event.target.closest("[data-stock-toggle]");
      if (stockToggle) {
        const input = document.querySelector(`[data-stock-quantity="${stockToggle.dataset.stockToggle}"]`);
        if (input) {
          input.value = stockToggle.checked ? (Number(input.value || 0) > 0 ? input.value : input.max || "1") : "";
          state.orderStockQuantities[input.dataset.stockQuantity] = input.value;
        }
        syncOrderDraft();
        render();
        return;
      }

      if (event.target.closest("#orderProduct") || event.target.closest("#orderTaskType") || event.target.closest("#orderRouteStep") || event.target.closest("#orderMaterial") || event.target.closest("#orderQuantity") || event.target.closest("#orderPriority") || event.target.closest("#orderDueDate") || event.target.closest("[data-stock-quantity]") || event.target.closest("[data-fabric-rolls]")) {
        syncOrderDraft();
        const stockQuantity = event.target.closest("[data-stock-quantity]");
        const fabricRolls = event.target.closest("[data-fabric-rolls]");
        if (stockQuantity) {
          const row = stockQuantity.closest(".stock-pick-row");
          const toggle = document.querySelector(`[data-stock-toggle="${stockQuantity.dataset.stockQuantity}"]`);
          const hasQuantity = Number(stockQuantity.value || 0) > 0;
          if (toggle) toggle.checked = hasQuantity;
          if (row) row.classList.toggle("active", hasQuantity);
        }
        if (!stockQuantity && !fabricRolls) render();
        return;
      }

      if (event.target.closest("#feedbackCategory") || event.target.closest("#cuttingProgress") || event.target.closest("#taskDefectReason") || event.target.closest("#taskDefectDisposition")) {
        event.target.dispatchEvent(new Event("input", {bubbles: true}));
        return;
      }

      if (event.target.closest("#adminStartDate, #adminEndDate, #adminEmployeeId, #userStartDate, #userEndDate")) {
        syncAdminForm();
        syncHistoryForm();
        persistUiState();
        return;
      }

      if (event.target.closest("#adminReportType")) {
        syncAdminForm();
        render();
      }
    });

    document.getElementById("backBtn").addEventListener("click", () => {
      if (state.screen === "profile") {
        state.screen = state.profileReturnScreen || "shift";
        render();
        return;
      }

      if (state.screen === "passport") {
        state.screen = state.passportReturnScreen || "orders";
        state.passportData = null;
        render();
        return;
      }

      if (state.screen === "analytics" && state.data && state.data.is_admin && state.analyticsView !== "overview") {
        if (state.analyticsView === "task" && state.analyticsReturnView && state.analyticsReturnView !== "task") {
          state.analyticsView = state.analyticsReturnView;
        } else {
          state.analyticsView = "overview";
          state.analyticsStage = "";
        }
        state.analyticsTaskId = "";
        render();
        return;
      }

      if (state.workspace === "warehouse" && state.screen === "warehouse" && state.wmsView !== "overview") {
        state.wmsView = warehouseMoreViews.has(state.wmsView) && state.wmsView !== "more" ? "more" : "overview";
        render();
        return;
      }

      if (state.workspace === "warehouse" && state.screen === "warehouse") {
        switchWorkspace("production");
        return;
      }

      if (state.workspace === "marketplaces" && state.screen === "marketplaces") {
        switchWorkspace("production");
        return;
      }

      if (state.screen === "shift" && state.data && state.data.is_admin && state.adminHomeView !== "overview") {
        state.adminHomeView = state.adminHomeView === "employee" ? "employees" : "overview";
        state.adminHomeEmployee = "";
        render();
        return;
      }

      if (state.screen === "shift" && state.data && !state.data.is_admin && state.employeeHomeView !== "overview") {
        state.employeeHomeView = "overview";
        render();
        return;
      }

      if (state.screen === "orders" && state.orderMode === "create") {
        state.orderMode = "list";
        render();
        return;
      }

      const flow = state.data && state.data.is_admin
        ? ["shift", "warehouse", "marketplaces", "analytics", "orders", "admin"]
        : ["shift", "report", "analytics", "orders", "admin"];
      const index = flow.indexOf(state.screen);
      setScreen(flow[Math.max(0, index - 1)]);
    });

    document.getElementById("menuBtn").addEventListener("click", () => {
      if (isStandaloneWeb) {
        state.profileReturnScreen = state.screen === "profile" ? (state.profileReturnScreen || "shift") : state.screen;
        setScreen("profile");
        return;
      }
      if (state.data && state.data.is_admin) {
        setScreen("admin");
        return;
      }
      showToast("Меню", "Настройки профиля и уведомления подключим позже.");
    });

    function requestedWebAuthMode() {
      if (!isStandaloneWeb) return "login";
      return new URLSearchParams(window.location.search).get("auth") === "register"
        ? "register"
        : "login";
    }

    function syncWebAuthModeUrl(mode) {
      if (!isStandaloneWeb || !window.history || typeof window.history.replaceState !== "function") return;
      const url = new URL(window.location.href);
      if (mode === "register") url.searchParams.set("auth", "register");
      else url.searchParams.delete("auth");
      const nextUrl = `${url.pathname}${url.search}${url.hash}`;
      if (nextUrl !== `${window.location.pathname}${window.location.search}${window.location.hash}`) {
        window.history.replaceState(null, "", nextUrl);
      }
    }

    function setWebAuthMode(mode, message = "", success = false) {
      const isRegistration = mode === "register";
      const loginTab = document.getElementById("webLoginTab");
      const registerTab = document.getElementById("webRegisterTab");
      const loginError = document.getElementById("webLoginError");
      const registerError = document.getElementById("webRegisterError");
      webLoginForm.hidden = isRegistration;
      webRegisterForm.hidden = !isRegistration;
      loginTab.classList.toggle("active", !isRegistration);
      registerTab.classList.toggle("active", isRegistration);
      loginTab.setAttribute("aria-selected", String(!isRegistration));
      registerTab.setAttribute("aria-selected", String(isRegistration));
      loginError.textContent = "";
      registerError.textContent = "";
      loginError.classList.remove("success");
      registerError.classList.remove("success");
      const messageNode = isRegistration ? registerError : loginError;
      messageNode.textContent = message;
      messageNode.classList.toggle("success", Boolean(message && success));
      syncWebAuthModeUrl(isRegistration ? "register" : "login");
      const focusTarget = isRegistration ? "webFullName" : "webUsername";
      window.setTimeout(() => document.getElementById(focusTarget)?.focus(), 60);
    }

    function showWebLogin(message = "") {
      clearWebSessionRetryTimer();
      webSessionRetryAttempt = 0;
      state.data = null;
      appRoot.hidden = true;
      mainButton.hidden = true;
      bottomNav.hidden = true;
      connectionView.hidden = true;
      loginView.hidden = false;
      setWebAuthMode(requestedWebAuthMode(), message);
    }

    function showWebApp() {
      clearWebSessionRetryTimer();
      webSessionRetryAttempt = 0;
      connectionView.hidden = true;
      loginView.hidden = true;
      appRoot.hidden = false;
      mainButton.hidden = false;
      bottomNav.hidden = false;
    }

    function clearWebSessionRetryTimer() {
      if (webSessionRetryTimer !== null) {
        window.clearTimeout(webSessionRetryTimer);
        webSessionRetryTimer = null;
      }
    }

    function storeWebIdentity(identity) {
      storedWebIdentity = String(identity || "");
      try {
        window.localStorage.setItem(webIdentityStorageKey, storedWebIdentity);
        return true;
      } catch (error) {
        return false;
      }
    }

    function clearWebIdentity() {
      storedWebIdentity = "";
      try { window.localStorage.removeItem(webIdentityStorageKey); } catch (error) {}
    }

    function showWebConnection(message, {checking = false, retryDelayMs = 0} = {}) {
      state.data = null;
      appRoot.hidden = true;
      mainButton.hidden = true;
      bottomNav.hidden = true;
      loginView.hidden = true;
      connectionView.hidden = false;
      connectionTitle.textContent = checking ? "Подключаемся" : "Нет связи с сервером";
      connectionMessage.textContent = message || (checking
        ? "Проверяем защищённую сессию."
        : "Не удалось проверить сессию. Ваш вход не сброшен.");
      connectionRetryStatus.textContent = retryDelayMs > 0
        ? `Повторим автоматически через ${Math.ceil(retryDelayMs / 1000)} сек.`
        : "";
      webConnectionRetry.disabled = checking;
      webConnectionRetry.textContent = checking ? "Проверяем…" : "Попробовать снова";
    }

    async function restoreWebSession() {
      const controller = typeof AbortController === "function" ? new AbortController() : null;
      const requestOptions = {credentials: "same-origin", cache: "no-store"};
      if (controller) requestOptions.signal = controller.signal;
      const timeoutId = controller
        ? window.setTimeout(() => controller.abort(), webSessionRequestTimeoutMs)
        : null;
      try {
        const response = await fetch("/api/web/session", requestOptions);
        const data = await response.json().catch(() => null);
        if (response.status === 401) {
          return {
            status: "unauthorized",
            message: data && data.message ? data.message : "Войдите в приложение.",
          };
        }
        if (!response.ok || !data || !data.ok) {
          return {
            status: "network_error",
            message: data && data.message
              ? data.message
              : "Сервер временно недоступен. Ваш вход сохранён, повторяем подключение.",
          };
        }
        webCsrfToken = data.csrf_token || "";
        webSessionProfile = data;
        const identity = String(data.telegram_id || data.username || "web");
        if (identity !== storedWebIdentity) {
          const identityPersisted = storeWebIdentity(identity);
          if (identityPersisted) {
            window.location.reload();
            return {status: "reloading"};
          }
        }
        return {status: "authenticated"};
      } catch (error) {
        return {
          status: "network_error",
          message: error && error.name === "AbortError"
            ? "Сервер отвечает слишком долго. Ваш вход сохранён, пробуем снова."
            : "Не удалось связаться с сервером. Ваш вход сохранён, пробуем снова.",
        };
      } finally {
        if (timeoutId !== null) window.clearTimeout(timeoutId);
      }
    }

    async function runWebSessionRestore({manual = false} = {}) {
      if (webSessionRestorePromise) return webSessionRestorePromise;
      clearWebSessionRetryTimer();
      showWebConnection(
        manual ? "Повторно проверяем соединение с сервером." : "Проверяем защищённую сессию.",
        {checking: true},
      );

      webSessionRestorePromise = (async () => {
        const result = await restoreWebSession();
        if (result.status === "reloading") return;
        if (result.status === "authenticated") {
          showWebApp();
          await refreshState();
          return;
        }
        if (result.status === "unauthorized") {
          showWebLogin(result.message);
          return;
        }

        const retryDelayMs = webSessionRetryDelaysMs[
          Math.min(webSessionRetryAttempt, webSessionRetryDelaysMs.length - 1)
        ];
        webSessionRetryAttempt += 1;
        showWebConnection(result.message, {retryDelayMs});
        webSessionRetryTimer = window.setTimeout(() => {
          webSessionRetryTimer = null;
          runWebSessionRestore();
        }, retryDelayMs);
      })();

      try {
        await webSessionRestorePromise;
      } finally {
        webSessionRestorePromise = null;
      }
    }

    async function loginWebApp(event) {
      event.preventDefault();
      const username = document.getElementById("webUsername");
      const password = document.getElementById("webPassword");
      const button = document.getElementById("webLoginButton");
      const errorNode = document.getElementById("webLoginError");
      button.disabled = true;
      errorNode.textContent = "";
      errorNode.classList.remove("success");
      try {
        const response = await fetch("/api/web/login", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          credentials: "same-origin",
          body: JSON.stringify({username: username.value, password: password.value}),
        });
        const data = await response.json().catch(() => ({}));
        if (!response.ok || !data.ok) throw new Error(data.message || "Не удалось войти.");
        storeWebIdentity(String(data.telegram_id || data.username || "web"));
        window.location.reload();
      } catch (error) {
        errorNode.textContent = error.message || "Не удалось войти.";
        password.value = "";
        password.focus();
        button.disabled = false;
      }
    }

    async function registerWebApp(event) {
      event.preventDefault();
      const fullName = document.getElementById("webFullName");
      const email = document.getElementById("webEmail");
      const phone = document.getElementById("webPhone");
      const password = document.getElementById("webRegisterPassword");
      const passwordConfirm = document.getElementById("webPasswordConfirm");
      const button = document.getElementById("webRegisterButton");
      const errorNode = document.getElementById("webRegisterError");
      errorNode.textContent = "";
      errorNode.classList.remove("success");

      if (password.value !== passwordConfirm.value) {
        errorNode.textContent = "Пароли не совпадают.";
        passwordConfirm.focus();
        return;
      }

      button.disabled = true;
      const loginValue = email.value.trim();
      try {
        const response = await fetch("/api/web/register", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          credentials: "same-origin",
          body: JSON.stringify({
            full_name: fullName.value,
            email: email.value,
            phone: phone.value,
            password: password.value,
          }),
        });
        const data = await response.json().catch(() => ({}));
        if (!response.ok || !data.ok) throw new Error(data.message || "Не удалось зарегистрироваться.");
        webRegisterForm.reset();
        document.getElementById("webUsername").value = loginValue;
        setWebAuthMode("login", data.message || "Регистрация завершена.", true);
      } catch (error) {
        errorNode.textContent = error.message || "Не удалось зарегистрироваться.";
      } finally {
        button.disabled = false;
      }
    }

    async function logoutWebApp() {
      if (!window.confirm("Выйти из приложения?")) return;
      const actionKey = "web-logout";
      if (!beginAction(actionKey)) return;
      const controller = typeof AbortController === "function" ? new AbortController() : null;
      const timeoutId = controller
        ? window.setTimeout(() => controller.abort(), webSessionRequestTimeoutMs)
        : null;
      try {
        const requestOptions = {
          method: "POST",
          headers: {"Content-Type": "application/json", "X-CSRF-Token": webCsrfToken},
          credentials: "same-origin",
          body: "{}",
        };
        if (controller) requestOptions.signal = controller.signal;
        const response = await fetch("/api/web/logout", requestOptions);
        const data = await response.json().catch(() => ({}));
        if (!response.ok || !data.ok) {
          throw new Error(data.message || "Не удалось завершить сессию.");
        }
        clearWebIdentity();
        webCsrfToken = "";
        window.location.reload();
      } catch (error) {
        showToast(
          "Выход не выполнен",
          error && error.name === "AbortError"
            ? "Сервер отвечает слишком долго. Проверьте подключение и повторите."
            : error.message || "Нет связи с сервером. Проверьте подключение и повторите.",
        );
      } finally {
        if (timeoutId !== null) window.clearTimeout(timeoutId);
        endAction(actionKey);
      }
    }

    async function changeWebPassword() {
      const currentPassword = document.getElementById("profileCurrentPassword");
      const newPassword = document.getElementById("profileNewPassword");
      const confirmation = document.getElementById("profileNewPasswordConfirm");
      if (!currentPassword || !newPassword || !confirmation) return;
      if (!currentPassword.value || !newPassword.value) {
        showToast("Пароль", "Заполните текущий и новый пароль.");
        return;
      }
      if (newPassword.value !== confirmation.value) {
        showToast("Пароль", "Новые пароли не совпадают.");
        confirmation.focus();
        return;
      }

      const actionKey = "change-web-password";
      if (!beginAction(actionKey)) return;
      try {
        const response = await fetch("/api/web/password", {
          method: "POST",
          headers: {"Content-Type": "application/json", "X-CSRF-Token": webCsrfToken},
          credentials: "same-origin",
          body: JSON.stringify({
            current_password: currentPassword.value,
            new_password: newPassword.value,
          }),
        });
        const data = await response.json().catch(() => ({}));
        if (!response.ok || !data.ok) throw new Error(data.message || "Не удалось изменить пароль.");
        clearWebIdentity();
        webCsrfToken = "";
        webSessionProfile = {};
        showWebLogin(data.message || "Пароль изменён. Войдите заново.");
      } catch (error) {
        currentPassword.value = "";
        currentPassword.focus();
        showToast("Пароль", error.message || "Не удалось изменить пароль.");
      } finally {
        endAction(actionKey);
      }
    }

    async function bootstrapApplication() {
      if (isStandaloneWeb) {
        document.body.classList.add("web-mode");
        webActionSlot.appendChild(mainButton);
        await runWebSessionRestore();
        return;
      }
      showWebApp();
      await refreshState();
      initSearchableSelects();
    }

    /* ── MutationObserver: apply searchable selects on DOM changes ── */
    new MutationObserver(function() {
      initSearchableSelects();
    }).observe(document.getElementById("appRoot") || document.body, {childList: true, subtree: true});

    document.getElementById("webLoginTab").addEventListener("click", () => setWebAuthMode("login"));
    document.getElementById("webRegisterTab").addEventListener("click", () => setWebAuthMode("register"));
    webConnectionRetry.addEventListener("click", () => {
      webSessionRetryAttempt = 0;
      runWebSessionRestore({manual: true});
    });
    window.addEventListener("online", () => {
      if (isStandaloneWeb && !connectionView.hidden) runWebSessionRestore({manual: true});
    });
    document.getElementById("qrScannerClose").addEventListener("click", stopWebQrScanner);
    document.getElementById("qrScannerManual").addEventListener("click", () => {
      stopWebQrScanner();
      promptCurrentScannerCode();
    });
    document.addEventListener("visibilitychange", () => {
      if (document.visibilityState === "hidden" && qrScannerStream) stopWebQrScanner();
      if (document.visibilityState === "visible" && isStandaloneWeb && !connectionView.hidden) {
        runWebSessionRestore({manual: true});
      }
    });
    webLoginForm.addEventListener("submit", loginWebApp);
    webRegisterForm.addEventListener("submit", registerWebApp);
    bootstrapApplication();
  </script>
</body>
</html>
"""
