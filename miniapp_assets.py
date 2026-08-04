"""Shared HTML assets for Telegram Mini App and the standalone web app."""

MINIAPP_HTML = """<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
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

    .wms-product-rich { display: flex; align-items: center; gap: 12px; min-width: 0; }
    .wms-product-rich-copy { display: grid; gap: 4px; min-width: 0; }
    .wms-product-rich-copy b { line-height: 1.25; }
    .wms-product-rich-copy span,
    .wms-product-rich-copy small { color: var(--muted); line-height: 1.35; }

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

    .wms-shipment-picker {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 10px;
      align-items: end;
    }

    .wms-shipment-line {
      display: grid;
      grid-template-columns: minmax(0, 1fr) 118px auto;
      gap: 12px;
      align-items: center;
    }

    .wms-shipment-line .field { margin: 0; }

    .wms-shipment-summary {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      padding: 14px 16px;
      border-radius: 14px;
      background: rgba(25,89,243,.07);
    }

    /* ТСД работает как клавиатура: код не показываем в поле и очищаем после считывания. */
    .wms-hardware-scanner-input { color: transparent; caret-color: transparent; }
    .wms-hardware-scanner-input::placeholder { color: var(--muted); opacity: 1; }

    @media (max-width: 600px) {
      /* Physical coordinates must stay intact on mobile. The previous
         two-column override conflicted with inline grid coordinates and
         squeezed implicit columns until labels overlapped. */
      .wms-map-scroll {
        overflow-x: visible;
        padding: 2px 0 10px;
      }

      .wms-zone-map {
        min-width: 0;
        width: 100%;
        margin-bottom: 12px;
      }

      .wms-map-grid {
        grid-template-columns: repeat(var(--wms-columns), 94px) !important;
        grid-auto-columns: 94px;
        width: 100%;
        gap: 6px;
        padding: 9px 9px 12px;
        overflow-x: auto;
        overflow-y: hidden;
        scroll-snap-type: x proximity;
        overscroll-behavior-inline: contain;
        scrollbar-width: thin;
        -webkit-overflow-scrolling: touch;
      }

      .wms-cell {
        min-width: 94px;
        min-height: 72px;
        padding: 8px 9px;
        scroll-snap-align: start;
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

      .wms-shipment-picker,
      .wms-shipment-line {
        grid-template-columns: 1fr;
      }

      .wms-shipment-line .small-button { width: 100%; }
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

    .marketplace-overview-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
      margin-top: 14px;
    }
    .marketplace-supply-card { align-items: center; gap: 14px; }
    .supply-actions { display: flex; align-items: center; justify-content: flex-end; flex-wrap: wrap; gap: 7px; }
    .critical-text { color: #b42318; font-weight: 700; }
    @media (max-width: 720px) { .marketplace-overview-grid { grid-template-columns: 1fr; } .supply-actions { justify-content: flex-start; } }
    .marketplace-menu-strip { display: flex; flex-wrap: wrap; gap: 7px; margin: 0 0 14px; padding: 8px; border: 1px solid rgba(111,128,159,.14); border-radius: 16px; background: rgba(255,255,255,.72); }
    .marketplace-menu-link { border: 0; border-radius: 10px; padding: 9px 13px; color: var(--muted); background: transparent; font: inherit; font-size: 12px; cursor: pointer; }
    .marketplace-menu-link.active { color: #fff; background: #1557ed; box-shadow: 0 8px 18px rgba(21,87,237,.2); }
    .marketplace-dashboard-grid { display: grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap: 16px; margin: 16px 0; }
    .marketplace-provider-dashboard { padding: 18px; border-radius: 18px; border: 1px solid rgba(111,128,159,.16); background: rgba(255,255,255,.78); box-shadow: var(--inset-shadow); }
    .marketplace-provider-dashboard.ozon-panel { border-top: 4px solid #005bff; }
    .marketplace-provider-dashboard.wb-panel { border-top: 4px solid #cb11ab; }
    .marketplace-provider-dashboard .provider-heading { display:flex; align-items:center; justify-content:space-between; gap: 12px; margin-bottom: 14px; }
    .marketplace-provider-dashboard .provider-heading h3 { margin:0; font-size:18px; }
    .marketplace-provider-dashboard .provider-heading span { color:var(--muted); font-size:11px; }
    .marketplace-dashboard-kpis { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:8px; }
    .marketplace-dashboard-kpi { padding:11px; border-radius:12px; background:rgba(240,244,252,.75); }
    .marketplace-dashboard-kpi span,.marketplace-dashboard-kpi small { display:block; color:var(--muted); font-size:10px; }
    .marketplace-dashboard-kpi strong { display:block; margin-top:5px; color:var(--text); font-size:20px; }
    .marketplace-dashboard-lower { display:grid; grid-template-columns:minmax(0,1.2fr) minmax(0,.8fr); gap:14px; margin-top:14px; }
    .marketplace-chart { height:145px; min-height:145px; display:flex; align-items:flex-end; gap:7px; padding:14px 10px 8px; border-radius:13px; overflow:hidden; background:linear-gradient(180deg,rgba(238,243,255,.82),rgba(255,255,255,.4)); }
    .marketplace-chart-bar { flex:1; min-width:8px; height:var(--bar-height); border-radius:7px 7px 2px 2px; background:linear-gradient(180deg,#2a69ff,#1647ca); }
    .marketplace-chart-bar.wb { background:linear-gradient(180deg,#d72ac2,#9712a2); }
    .marketplace-dashboard-lower > div { min-width:0; }
    .marketplace-mini-list { display:grid; gap:8px; min-width:0; }
    .marketplace-mini-row { display:flex; justify-content:space-between; gap:8px; min-width:0; padding:10px 0; border-bottom:1px solid rgba(111,128,159,.12); font-size:12px; }
    .marketplace-mini-row:last-child { border-bottom:0; }
    .marketplace-mini-row span { color:var(--muted); overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
    .marketplace-wide-grid { display:grid; grid-template-columns:minmax(0,1.2fr) minmax(0,.8fr); gap:16px; margin-top:16px; }
    .marketplace-table { width:100%; border-collapse:collapse; font-size:11px; }
    .marketplace-table th,.marketplace-table td { padding:9px 7px; text-align:left; border-bottom:1px solid rgba(111,128,159,.12); }
    .marketplace-table th { color:var(--muted); font-weight:600; }
    .marketplace-notice { display:flex; align-items:flex-start; gap:9px; padding:10px 0; border-bottom:1px solid rgba(111,128,159,.12); font-size:11px; }
    .marketplace-notice:last-child { border-bottom:0; }
    .marketplace-notice b { display:block; margin-bottom:3px; }
    .marketplace-notice span { color:var(--muted); }
    .marketplace-notice-dot { width:8px; height:8px; margin-top:4px; flex:0 0 auto; border-radius:50%; background:#ff9f1c; }
    .marketplace-dashboard-grid.single { grid-template-columns:1fr; }
    @media (max-width: 800px) { .marketplace-dashboard-grid,.marketplace-wide-grid,.marketplace-dashboard-lower { grid-template-columns:1fr; } .marketplace-dashboard-kpis { grid-template-columns:repeat(2,minmax(0,1fr)); } }

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

    .cutting-formation-row {
      display: grid;
      grid-template-columns: minmax(150px, 1.25fr) minmax(90px, .55fr) minmax(90px, .55fr) minmax(170px, 1fr);
      gap: 10px;
      align-items: end;
      padding: 13px;
    }

    .cutting-formation-meta b,
    .cutting-formation-field label {
      display: block;
      font-size: 13px;
      line-height: 1.25;
    }

    .cutting-formation-meta span,
    .cutting-formation-field label {
      color: var(--muted);
    }

    .cutting-formation-meta span {
      display: block;
      margin-top: 5px;
      font-size: 12px;
    }

    .cutting-formation-field {
      display: grid;
      gap: 5px;
    }

    .cutting-formation-field input {
      width: 100%;
      min-height: 44px;
      border: 1px solid rgba(109,124,158,.16);
      border-radius: 12px;
      background: rgba(255,255,255,.9);
      padding: 0 10px;
      color: var(--text);
      font-size: 14px;
      font-weight: 700;
      outline: none;
    }

    .cutting-formation-field input:disabled {
      opacity: .55;
    }

    .cutting-formation-good {
      min-height: 44px;
      display: flex;
      align-items: center;
      padding: 0 11px;
      border-radius: 12px;
      background: rgba(34,197,94,.1);
      color: #16823d;
      font-size: 15px;
      font-weight: 800;
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
      .cutting-formation-row {
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }

      .cutting-formation-meta,
      .cutting-formation-comment {
        grid-column: 1 / -1;
      }

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
        display: none !important;
      }

      body.web-mode.marketplace-workspace .body {
        padding-left: 52px !important;
      }
    }

    body.web-mode.marketplace-workspace .bottom-nav {
      display: none !important;
    }

    @media (max-width: 899px) {
      body.web-mode.marketplace-workspace .body {
        padding-bottom: calc(28px + env(safe-area-inset-bottom)) !important;
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

    /* Operations center: desktop-first control room built on the existing data. */
    .operations-center { display: grid; gap: 18px; }
    .profile-btn svg { width: 21px; height: 21px; display: block; }
    .operations-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 18px; }
    .operations-head h2 { margin: 0; font-size: clamp(28px, 3vw, 38px); letter-spacing: -.045em; }
    .operations-head p { margin: 8px 0 0; color: var(--muted); }
    .live-indicator { display: inline-flex; align-items: center; gap: 7px; padding: 9px 12px; border-radius: 999px; background: rgba(49,168,107,.10); color: var(--sage-dark); font-size: 12px; font-weight: 800; white-space: nowrap; }
    .live-indicator::before { content: ""; width: 8px; height: 8px; border-radius: 50%; background: currentColor; box-shadow: 0 0 0 4px rgba(49,168,107,.11); }
    .operations-kpis { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; }
    .operations-kpi { min-height: 142px; padding: 18px; border: 1px solid var(--line); border-radius: 16px; background: rgba(255,255,255,.88); box-shadow: var(--inset-shadow), 0 10px 24px rgba(16,23,34,.06); text-align: left; }
    .operations-kpi span { display: block; color: var(--muted); font-size: 12px; font-weight: 800; text-transform: uppercase; letter-spacing: .06em; }
    .operations-kpi strong { display: block; margin: 16px 0 7px; color: var(--text); font-size: 31px; line-height: 1; letter-spacing: -.05em; }
    .operations-kpi small { display: block; color: var(--muted); font-size: 13px; font-weight: 600; }
    .operations-kpi.risk { border-color: rgba(242,162,58,.34); background: linear-gradient(135deg, rgba(255,247,232,.94), rgba(255,255,255,.92)); }
    .operations-kpi.overdue { border-color: rgba(221,79,93,.30); background: linear-gradient(135deg, rgba(255,239,242,.94), rgba(255,255,255,.92)); }
    .operations-layout { display: grid; grid-template-columns: minmax(0, 1.35fr) minmax(290px, .65fr); gap: 18px; }
    .operations-panel { padding: 19px; border: 1px solid var(--line); border-radius: 16px; background: rgba(255,255,255,.84); box-shadow: var(--inset-shadow), 0 10px 24px rgba(16,23,34,.05); }
    .operations-panel-head { display: flex; justify-content: space-between; align-items: baseline; gap: 12px; margin-bottom: 17px; }
    .operations-panel-head b { font-size: 16px; }
    .operations-panel-head span { color: var(--muted); font-size: 12px; }
    .shift-progress-value { display: grid; grid-template-columns: 1fr auto; gap: 10px; align-items: end; margin-bottom: 12px; }
    .shift-progress-value strong { font-size: 28px; letter-spacing: -.045em; }
    .shift-progress-value small { color: var(--muted); font-size: 12px; font-weight: 700; }
    .shift-team { margin-top: 16px; border: 1px solid var(--line); border-radius: 14px; background: rgba(247,249,253,.82); overflow: hidden; }
    .shift-team summary { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 13px 14px; cursor: pointer; font-weight: 800; list-style: none; }
    .shift-team summary::-webkit-details-marker { display: none; }
    .shift-team summary::after { content: "⌄"; color: var(--primary); font-size: 18px; transition: transform .18s ease; }
    .shift-team[open] summary::after { transform: rotate(180deg); }
    .shift-team-list { display: grid; border-top: 1px solid var(--line); }
    .shift-team-row { display: grid; grid-template-columns: minmax(170px, 1fr) minmax(130px, .65fr) minmax(150px, auto); gap: 14px; align-items: center; padding: 12px 14px; }
    .shift-team-row + .shift-team-row { border-top: 1px solid var(--line); }
    .shift-team-person, .shift-team-time { display: grid; gap: 3px; min-width: 0; }
    .shift-team-person b { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .shift-team-person span, .shift-team-time span { color: var(--muted); font-size: 12px; }
    .shift-team-time b { font-size: 13px; }
    .stage-stack { display: grid; gap: 13px; }
    .stage-row { display: grid; grid-template-columns: minmax(128px, 1fr) minmax(92px, 2.4fr) auto; align-items: center; gap: 11px; }
    .stage-row b { font-size: 13px; }
    .stage-row .progress { margin: 0; }
    .stage-row .status-chip { min-width: 76px; justify-content: center; }
    .operations-alerts { display: grid; gap: 9px; }
    .operations-alert { display: grid; grid-template-columns: 9px minmax(0, 1fr) auto; gap: 10px; align-items: start; padding: 11px 0; border-bottom: 1px solid var(--line); cursor: pointer; }
    .operations-alert:last-child { border-bottom: 0; padding-bottom: 0; }
    .operations-alert i { width: 8px; height: 8px; margin-top: 5px; border-radius: 50%; background: var(--warning); }
    .operations-alert.critical i { background: var(--danger); }
    .operations-alert b { display: block; font-size: 13px; }
    .operations-alert span { color: var(--muted); font-size: 12px; line-height: 1.35; }
    .operations-actions { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 9px; }
    .operations-actions button { min-height: 44px; border: 1px solid var(--line); border-radius: 11px; background: rgba(245,248,255,.88); color: var(--text); font-size: 12px; font-weight: 800; text-align: left; padding: 10px 12px; }
    .operations-actions button.primary { color: #fff; border-color: var(--accent); background: var(--accent); box-shadow: var(--blue-shadow); }
    .key-orders { display: grid; gap: 9px; }
    .key-order { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 12px; align-items: center; padding: 12px; border: 1px solid var(--line); border-radius: 12px; background: rgba(250,251,253,.94); cursor: pointer; }
    .key-order b { display: block; font-size: 13px; }
    .key-order span { color: var(--muted); font-size: 12px; }
    .orders-board { display: grid; grid-template-columns: repeat(4, minmax(220px, 1fr)); gap: 14px; overflow-x: auto; padding-bottom: 8px; }
    .orders-column { min-width: 220px; min-height: 290px; padding: 12px; border: 1px solid var(--line); border-radius: 15px; background: rgba(236,240,247,.62); }
    .orders-column-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 11px; font-size: 13px; font-weight: 800; }
    .orders-column-head span { display: grid; place-items: center; min-width: 24px; height: 24px; border-radius: 8px; background: #fff; color: var(--muted); font-size: 12px; }
    .board-order-card { display: grid; gap: 9px; margin-bottom: 10px; padding: 13px; border: 1px solid rgba(109,124,158,.15); border-radius: 12px; background: #fff; box-shadow: 0 6px 14px rgba(16,23,34,.05); cursor: pointer; }
    .board-order-card b { font-size: 13px; line-height: 1.3; }
    .board-order-meta { display: flex; justify-content: space-between; gap: 8px; color: var(--muted); font-size: 11px; }
    @media (max-width: 820px) {
      .operations-kpis { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .operations-layout { grid-template-columns: 1fr; }
      .shift-team-row { grid-template-columns: 1fr auto; }
      .shift-team-time { grid-column: 1 / -1; grid-row: 2; grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .operations-head { display: grid; }
    }
    @media (max-width: 720px) {
      .operations-actions { grid-template-columns: 1fr; }
      .orders-board { grid-template-columns: 1fr; overflow: visible; }
      .orders-column { min-width: 0; min-height: 0; }
    }
    @media (min-width: 900px) and (max-width: 1100px) {
      body.web-mode .appbar {
        grid-template-columns: 185px minmax(300px, 1fr) auto;
        gap: 12px;
      }
      body.web-mode .appbar-profile { display: none; }
      body.web-mode .workspace-nav button { font-size: 10px; }
    }
    /* Marketplace dashboard v2: one adaptive component for all providers. */
    body.marketplace-workspace {
      --marketplace-primary: #2563eb;
      --marketplace-soft: #eef4ff;
      --ozon-color: #005bff;
      --wildberries-color: #a100ff;
    }

    .marketplace-layout {
      display: grid;
      grid-template-columns: 220px minmax(0, 1fr);
      gap: 18px;
      width: min(100%, 1600px);
      margin: 0 auto;
    }

    .marketplace-main { min-width: 0; }

    .marketplace-layout .marketplace-menu-strip {
      position: sticky;
      top: 92px;
      align-self: start;
      display: flex;
      flex-direction: column;
      flex-wrap: nowrap;
      gap: 5px;
      margin: 0;
      padding: 12px;
      max-height: calc(100dvh - 116px);
      overflow-y: auto;
      border-radius: 18px;
    }

    .marketplace-layout .marketplace-menu-link {
      min-height: 44px;
      padding: 11px 13px;
      text-align: left;
      font-size: 13px;
      font-weight: 700;
    }

    .marketplace-layout .marketplace-menu-link.active {
      color: #1746b6;
      background: var(--marketplace-soft);
      box-shadow: inset 3px 0 0 var(--marketplace-primary);
    }

    .marketplace-v2-head { margin-bottom: 14px; }
    .marketplace-v2-head h2 { font-size: clamp(28px, 3vw, 34px); }

    .marketplace-brand-mark {
      min-width: 92px;
      padding: 10px 14px;
      border: 1px solid rgba(37,99,235,.18);
      border-radius: 13px;
      color: #1b4db5;
      background: #eef4ff;
      font-size: 14px;
      font-weight: 900;
      text-align: center;
      letter-spacing: .04em;
    }

    .marketplace-brand-mark.ozon { color: #005bff; background: #eaf1ff; }
    .marketplace-brand-mark.wb { color: #8d0aa5; background: #f7eaff; }

    .marketplace-filter-bar {
      display: grid;
      grid-template-columns: minmax(220px, 300px) 1fr auto;
      align-items: end;
      gap: 12px;
      margin: 14px 0;
      padding: 13px;
      border: 1px solid var(--line);
      border-radius: 15px;
      background: rgba(255,255,255,.86);
      box-shadow: var(--inset-shadow);
    }

    .marketplace-filter-bar label { display: grid; gap: 6px; }
    .marketplace-filter-bar label > span { color: var(--muted); font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: .05em; }
    .marketplace-filter-bar select { min-height: 44px; border: 1px solid var(--line); border-radius: 11px; padding: 8px 36px 8px 11px; background: #fff; }
    .marketplace-period-label { align-self: center; color: var(--muted); font-size: 13px; font-weight: 700; }

    .marketplace-filter-panel { margin-bottom: 14px; padding: 16px; }
    .marketplace-check { display: flex; align-items: center; gap: 9px; min-height: 44px; color: var(--text); font-size: 13px; font-weight: 700; }
    .marketplace-check input { width: 18px; height: 18px; }

    .marketplace-v2-kpis {
      display: grid;
      grid-template-columns: repeat(6, minmax(0, 1fr));
      gap: 10px;
      margin: 14px 0;
    }

    .marketplace-v2-kpi {
      min-height: 118px;
      padding: 16px;
      border: 1px solid var(--line);
      border-radius: 14px;
      background: rgba(255,255,255,.92);
      color: var(--text);
      text-align: left;
      box-shadow: var(--inset-shadow), 0 8px 22px rgba(16,23,34,.05);
    }

    .marketplace-v2-kpi > span { display: block; min-height: 30px; color: var(--muted); font-size: 12px; font-weight: 750; }
    .marketplace-v2-kpi strong { display: block; margin: 7px 0 8px; font-size: clamp(23px, 2vw, 30px); line-height: 1; letter-spacing: -.04em; }
    .marketplace-v2-kpi strong small { font-size: 12px; letter-spacing: 0; }
    .marketplace-v2-kpi > small { display: block; color: #237e52; font-size: 11px; line-height: 1.3; }
    .marketplace-v2-kpi.unavailable { cursor: default; background: rgba(248,250,252,.9); }
    .marketplace-v2-kpi.unavailable strong, .marketplace-v2-kpi.unavailable > small { color: var(--muted); }

    .marketplace-v2-analytics {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      margin: 14px 0;
    }

    .marketplace-analytic-card { min-height: 286px; padding: 16px; }
    .marketplace-chart-empty, .marketplace-empty-metric { min-height: 210px; display: grid; align-content: center; justify-items: center; gap: 7px; padding: 20px; border-radius: 13px; background: linear-gradient(180deg,#f7f9fd,#fff); color: var(--muted); text-align: center; }
    .marketplace-chart-empty b, .marketplace-empty-metric b { color: var(--text); font-size: 14px; }
    .marketplace-chart-empty span, .marketplace-empty-metric span { max-width: 260px; font-size: 12px; line-height: 1.45; }
    .marketplace-empty-metric { min-height: 210px; }

    .marketplace-order-bars { height: 210px; display: flex; align-items: flex-end; gap: 7px; padding: 16px 4px 4px; }
    .marketplace-order-bars i { flex: 1; min-width: 7px; height: var(--bar-height); border-radius: 6px 6px 2px 2px; background: linear-gradient(180deg,var(--marketplace-primary),#1647ca); }

    .marketplace-product-detail, .marketplace-sales-detail { margin-top: 14px; }
    .marketplace-table-scroll { max-width: 100%; overflow-x: auto; }
    .marketplace-table { font-size: 13px; }
    .marketplace-source { display: inline-flex; align-items: center; min-height: 25px; padding: 4px 8px; border-radius: 999px; font-size: 11px; font-weight: 800; }
    .marketplace-source.ozon { color: #005bff; background: #eaf1ff; }
    .marketplace-source.wb { color: #8d0aa5; background: #f7eaff; }

    .marketplace-placeholder { min-height: 330px; display: grid; align-content: center; justify-items: center; gap: 10px; text-align: center; }
    .marketplace-placeholder-icon { display: grid; place-items: center; width: 52px; height: 52px; border-radius: 16px; color: var(--marketplace-primary); background: var(--marketplace-soft); font-size: 26px; }
    .marketplace-placeholder h3, .marketplace-placeholder p { margin: 0; }
    .marketplace-placeholder p { max-width: 540px; color: var(--muted); line-height: 1.5; }

    @media (max-width: 1280px) {
      .marketplace-layout { grid-template-columns: 190px minmax(0, 1fr); }
      .marketplace-v2-kpis { grid-template-columns: repeat(3, minmax(0, 1fr)); }
      .marketplace-v2-analytics { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }

    @media (max-width: 899px) {
      body.web-mode main button { min-height: 44px; }
      .marketplace-layout { display: block; width: 100%; }
      .marketplace-layout .marketplace-menu-strip { position: sticky; top: 0; z-index: 18; flex-direction: row; overflow-x: auto; overflow-y: hidden; max-height: none; margin-bottom: 12px; padding: 5px; border-radius: 13px; scrollbar-width: none; }
      .marketplace-layout .marketplace-menu-strip::-webkit-scrollbar { display: none; }
      .marketplace-layout .marketplace-menu-link { flex: 0 0 auto; min-width: 104px; text-align: center; }
      .marketplace-layout .marketplace-menu-link.active { box-shadow: inset 0 -3px 0 var(--marketplace-primary); }
      .marketplace-provider-inline { display: block; }
      .marketplace-provider-inline .marketplace-provider-switch { display: grid; grid-template-columns: 1fr; }
      .marketplace-filter-bar { grid-template-columns: 1fr; align-items: stretch; }
      .marketplace-period-label { min-height: 24px; }
      .marketplace-v2-kpis { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .marketplace-v2-analytics { grid-template-columns: 1fr; }
      .marketplace-analytic-card { min-height: 250px; }
      .marketplace-v2-head { align-items: flex-start; }
      .marketplace-brand-mark { min-width: 74px; padding: 8px 10px; }
    }

    @media (max-width: 430px) {
      .marketplace-v2-kpis { gap: 8px; }
      .marketplace-v2-kpi { min-height: 112px; padding: 12px; }
      .marketplace-v2-kpi strong { font-size: 22px; }
    }

    /* Unified analytics overview. Every value in this block comes from the
       marketplace dashboard or production-control payload; unavailable data
       is deliberately kept separate from a confirmed zero. */
    .analytics-hub-tabs {
      display: flex; width: max-content; max-width: 100%; gap: 5px; overflow-x: auto;
      margin-top: 14px; padding: 5px; border: 1px solid var(--line); border-radius: 13px;
      background: rgba(255,255,255,.82); box-shadow: var(--inset-shadow); scrollbar-width: none;
    }
    .analytics-hub-tabs::-webkit-scrollbar { display: none; }
    .analytics-hub-tabs button {
      flex: 0 0 auto; min-height: 36px; padding: 8px 14px; border: 0; border-radius: 9px;
      background: transparent; color: var(--muted); font-size: 12px; font-weight: 800; cursor: pointer;
    }
    .analytics-hub-tabs button:hover { color: var(--text); background: rgba(37,99,235,.07); }
    .analytics-hub-tabs button.active { color: #fff; background: var(--marketplace-primary, #2563eb); box-shadow: 0 7px 16px rgba(37,99,235,.2); }
    .analytics-overview { display: grid; gap: 16px; margin-top: 14px; }
    .analytics-overview-notice {
      display: flex; align-items: flex-start; justify-content: space-between; gap: 14px;
      padding: 13px 15px; border: 1px solid rgba(37,99,235,.15); border-radius: 14px;
      background: rgba(239,245,255,.86); color: #24467f;
    }
    .analytics-overview-notice.warn { border-color: rgba(180,83,9,.2); background: #fff7e8; color: #8a4b08; }
    .analytics-overview-notice.error { border-color: rgba(180,35,53,.2); background: #fff0f2; color: #9c2536; }
    .analytics-overview-notice div { display: grid; gap: 3px; }
    .analytics-overview-notice b { color: inherit; font-size: 13px; }
    .analytics-overview-notice span { font-size: 12px; line-height: 1.45; }
    .analytics-overview-notice button { flex: 0 0 auto; }
    .analytics-period-bar {
      display: grid; grid-template-columns: minmax(210px, 290px) minmax(320px, 1fr) auto;
      align-items: end; gap: 12px; padding: 14px; border: 1px solid var(--line);
      border-radius: 15px; background: rgba(255,255,255,.88); box-shadow: var(--inset-shadow);
    }
    .analytics-period-bar label { display: grid; gap: 6px; min-width: 0; }
    .analytics-period-bar label > span {
      color: var(--muted); font-size: 10px; font-weight: 850; letter-spacing: .05em; text-transform: uppercase;
    }
    .analytics-period-bar select, .analytics-period-bar input { width: 100%; min-height: 42px; }
    .analytics-period-dates { display: grid; grid-template-columns: repeat(2, minmax(145px, 1fr)); gap: 10px; }
    .analytics-period-current { align-self: center; color: var(--muted); font-size: 12px; font-weight: 750; white-space: nowrap; }
    .analytics-overview-kpis {
      display: grid; grid-template-columns: repeat(7, minmax(0, 1fr)); gap: 10px;
    }
    .analytics-overview-kpi {
      min-width: 0; min-height: 132px; padding: 15px; border: 1px solid var(--line);
      border-radius: 15px; background: rgba(255,255,255,.94); box-shadow: var(--inset-shadow),0 8px 22px rgba(16,23,34,.045);
    }
    .analytics-overview-kpi.partial { border-color: rgba(180,83,9,.22); background: linear-gradient(145deg,#fff,#fff9ee); }
    .analytics-overview-kpi.unavailable { background: rgba(248,250,252,.9); }
    .analytics-overview-kpi.danger { border-color: rgba(180,35,53,.2); background: linear-gradient(145deg,#fff,#fff2f4); }
    .analytics-overview-kpi > span { display: block; min-height: 29px; color: var(--muted); font-size: 11px; font-weight: 800; line-height: 1.3; }
    .analytics-overview-kpi strong { display: block; overflow: hidden; margin: 8px 0; font-size: clamp(20px,2vw,29px); line-height: 1.05; letter-spacing: -.045em; text-overflow: ellipsis; white-space: nowrap; }
    .analytics-overview-kpi strong small { margin-left: 3px; font-size: 11px; letter-spacing: 0; }
    .analytics-overview-kpi > small { display: block; color: var(--muted); font-size: 10px; line-height: 1.35; }
    .analytics-overview-grid { display: grid; grid-template-columns: minmax(0,1.45fr) minmax(320px,.75fr); gap: 14px; }
    .analytics-overview-section { min-width: 0; padding: 17px !important; }
    .analytics-overview-section .section-title { margin-top: 0; }
    .analytics-combined-chart { min-height: 290px; margin-top: 10px; }
    .analytics-combined-chart svg { display: block; width: 100%; height: 270px; overflow: visible; }
    .analytics-chart-legend { display: flex; flex-wrap: wrap; gap: 9px 16px; margin-top: 9px; color: var(--muted); font-size: 11px; }
    .analytics-chart-legend span { display: inline-flex; align-items: center; gap: 6px; }
    .analytics-chart-legend i { width: 18px; height: 3px; border-radius: 99px; background: var(--legend-color); }
    .analytics-chart-source { margin-top: 8px; color: var(--muted); font-size: 10px; line-height: 1.45; }
    .analytics-provider-list { display: grid; gap: 10px; }
    .analytics-provider-card { padding: 13px; border: 1px solid var(--line); border-radius: 13px; background: rgba(248,250,254,.82); }
    .analytics-provider-head { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
    .analytics-provider-head b { font-size: 14px; }
    .analytics-provider-metrics { display: grid; grid-template-columns: repeat(2,minmax(0,1fr)); gap: 8px; margin-top: 11px; }
    .analytics-provider-metric { min-width: 0; padding: 9px; border-radius: 10px; background: #fff; }
    .analytics-provider-metric span, .analytics-provider-metric small { display: block; color: var(--muted); font-size: 9px; line-height: 1.35; }
    .analytics-provider-metric b { display: block; overflow: hidden; margin: 4px 0 2px; font-size: 14px; text-overflow: ellipsis; white-space: nowrap; }
    .analytics-three-grid { display: grid; grid-template-columns: repeat(3,minmax(0,1fr)); gap: 14px; }
    .analytics-risk-list, .analytics-matrix-list, .analytics-supply-list, .analytics-quality-list { display: grid; gap: 8px; }
    .analytics-risk-row, .analytics-matrix-row, .analytics-supply-row, .analytics-quality-row {
      display: grid; grid-template-columns: minmax(0,1fr) auto; align-items: center; gap: 12px;
      padding: 10px 0; border-bottom: 1px solid rgba(84,101,134,.11);
    }
    .analytics-risk-row:last-child, .analytics-matrix-row:last-child, .analytics-supply-row:last-child, .analytics-quality-row:last-child { border-bottom: 0; }
    .analytics-risk-copy, .analytics-matrix-copy, .analytics-supply-copy, .analytics-quality-copy { display: grid; gap: 3px; min-width: 0; }
    .analytics-risk-copy b, .analytics-matrix-copy b, .analytics-supply-copy b, .analytics-quality-copy b { overflow: hidden; font-size: 12px; line-height: 1.3; text-overflow: ellipsis; white-space: nowrap; }
    .analytics-risk-copy span, .analytics-matrix-copy span, .analytics-supply-copy span, .analytics-quality-copy span { color: var(--muted); font-size: 10px; line-height: 1.4; }
    .analytics-matrix-values { display: grid; grid-template-columns: repeat(2,minmax(66px,auto)); gap: 6px; text-align: right; }
    .analytics-matrix-values span { padding: 5px 7px; border-radius: 8px; background: rgba(238,243,252,.9); color: var(--text); font-size: 10px; font-weight: 800; white-space: nowrap; }
    .analytics-loading-card { position: relative; overflow: hidden; min-height: 132px; background: #f5f7fb; }
    .analytics-loading-card::after {
      content: ""; position: absolute; inset: 0; transform: translateX(-100%);
      background: linear-gradient(90deg,transparent,rgba(255,255,255,.8),transparent);
      animation: analytics-shimmer 1.15s infinite;
    }
    @keyframes analytics-shimmer { to { transform: translateX(100%); } }

    @media (max-width: 1380px) {
      .analytics-overview-kpis { grid-template-columns: repeat(4,minmax(0,1fr)); }
      .analytics-three-grid { grid-template-columns: repeat(2,minmax(0,1fr)); }
      .analytics-three-grid > :last-child { grid-column: 1 / -1; }
    }
    @media (max-width: 960px) {
      .analytics-period-bar, .analytics-overview-grid { grid-template-columns: 1fr; }
      .analytics-period-current { white-space: normal; }
      .analytics-overview-kpis { grid-template-columns: repeat(2,minmax(0,1fr)); }
      .analytics-three-grid { grid-template-columns: 1fr; }
      .analytics-three-grid > :last-child { grid-column: auto; }
    }
    @media (max-width: 540px) {
      .analytics-hub-tabs { width: 100%; }
      .analytics-hub-tabs button { flex: 1 0 auto; min-height: 42px; }
      .analytics-overview { gap: 12px; }
      .analytics-overview-notice { display: grid; }
      .analytics-overview-notice button { width: 100%; }
      .analytics-period-dates { grid-template-columns: 1fr; }
      .analytics-overview-kpis { gap: 8px; }
      .analytics-overview-kpi { min-height: 122px; padding: 12px; }
      .analytics-overview-kpi strong { font-size: 21px; }
      .analytics-overview-section { padding: 14px !important; }
      .analytics-provider-metrics { grid-template-columns: 1fr; }
      .analytics-matrix-row { grid-template-columns: 1fr; }
      .analytics-matrix-values { justify-content: start; text-align: left; }
    }

    /* Analytics center. The public application chrome remains shared, while
       this workspace follows prototype/ as an independent dense SaaS UI. */
    body.web-mode.analytics-mode .body {
      padding: 22px 24px 46px !important;
    }
    body.web-mode.analytics-mode #mount { width: 100%; }
    .ac-shell {
      --ac-bg: #f4f6fb;
      --ac-surface: #fff;
      --ac-border: #e3e8f1;
      --ac-text: #111827;
      --ac-muted: #718096;
      --ac-sidebar: #121a2c;
      --ac-blue: #2563eb;
      --ac-wb: #c915b8;
      display: grid;
      grid-template-columns: 236px minmax(0,1fr);
      min-height: calc(100vh - 150px);
      overflow: hidden;
      color: var(--ac-text);
      background: var(--ac-bg);
      border: 1px solid var(--ac-border);
      border-radius: 18px;
      box-shadow: 0 14px 42px rgba(15,23,42,.08);
    }
    .ac-sidebar {
      display: flex;
      flex-direction: column;
      min-width: 0;
      padding: 20px 14px;
      color: #a9b4c8;
      background: radial-gradient(circle at 12% 0,rgba(79,70,229,.18),transparent 34%),linear-gradient(180deg,#141d33,#101827);
    }
    .ac-brand { display:flex; align-items:center; gap:11px; padding:2px 8px 21px; border-bottom:1px solid rgba(255,255,255,.07); }
    .ac-brand-mark { width:36px; height:36px; display:grid; place-items:center; border-radius:10px; color:#fff; background:linear-gradient(135deg,#3867ff,#6f4ef6); font-weight:900; }
    .ac-brand strong,.ac-brand span { display:block; }
    .ac-brand strong { color:#fff; font-size:12px; letter-spacing:.12em; }
    .ac-brand span { margin-top:2px; color:#7f8da5; font-size:9px; }
    .ac-nav { display:grid; gap:4px; margin-top:18px; }
    .ac-nav button {
      position:relative; width:100%; min-height:42px; display:grid; grid-template-columns:22px minmax(0,1fr); align-items:center; gap:10px;
      padding:0 11px; border:0; border-radius:10px; color:#9da9bc; background:transparent; text-align:left; cursor:pointer;
      font-size:12px; font-weight:750;
    }
    .ac-nav button:hover { color:#fff; background:rgba(255,255,255,.055); }
    .ac-nav button.active { color:#fff; background:rgba(91,96,246,.22); box-shadow:inset 0 0 0 1px rgba(129,140,248,.14); }
    .ac-nav button.active::before { content:""; position:absolute; left:-14px; top:9px; width:3px; height:24px; border-radius:0 3px 3px 0; background:#818cf8; }
    .ac-nav-icon { width:20px; height:20px; display:grid; place-items:center; color:inherit; font-size:14px; }
    .ac-sidebar-status { margin-top:auto; padding:13px; border:1px solid rgba(255,255,255,.07); border-radius:12px; background:rgba(255,255,255,.045); }
    .ac-sidebar-status b,.ac-sidebar-status span { display:block; }
    .ac-sidebar-status b { color:#e7ebf4; font-size:10px; }
    .ac-sidebar-status span { margin-top:5px; color:#8290a6; font-size:9px; line-height:1.45; }
    .ac-main { min-width:0; }
    .ac-topbar {
      min-height:70px; display:flex; align-items:center; gap:12px; padding:14px 20px;
      border-bottom:1px solid var(--ac-border); background:rgba(255,255,255,.92); backdrop-filter:blur(14px);
    }
    .ac-search { flex:1 1 300px; max-width:420px; height:40px; display:flex; align-items:center; gap:8px; padding:0 12px; border:1px solid var(--ac-border); border-radius:10px; background:#f7f9fc; }
    .ac-search span { color:#98a3b5; }
    .ac-search input { min-width:0; flex:1; border:0; outline:0; background:transparent; color:var(--ac-text); font-size:11px; }
    .ac-market-switch { margin-left:auto; display:flex; gap:3px; padding:3px; border:1px solid var(--ac-border); border-radius:10px; background:#f3f5f9; }
    .ac-market-switch button { min-height:32px; padding:0 10px; border:0; border-radius:7px; color:#748095; background:transparent; font-size:10px; font-weight:800; cursor:pointer; }
    .ac-market-switch button.active { color:#111827; background:#fff; box-shadow:0 2px 8px rgba(15,23,42,.08); }
    .ac-market-switch button[data-provider="ozon"].active { color:#fff; background:var(--ac-blue); }
    .ac-market-switch button[data-provider="wildberries"].active { color:#fff; background:var(--ac-wb); }
    .ac-sync { min-height:38px; padding:0 13px; border:0; border-radius:10px; color:#fff; background:linear-gradient(135deg,#2563eb,#5b45ee); font-size:10px; font-weight:800; cursor:pointer; white-space:nowrap; }
    .ac-content { padding:22px; }
    .ac-heading { display:flex; align-items:flex-end; justify-content:space-between; gap:18px; margin-bottom:18px; }
    .ac-eyebrow { display:block; margin-bottom:5px; color:#4f46e5; font-size:9px; font-weight:900; letter-spacing:.13em; text-transform:uppercase; }
    .ac-heading h1 { margin:0; color:#101827; font-size:clamp(25px,2.1vw,34px); line-height:1.08; letter-spacing:-.045em; }
    .ac-heading p { margin:6px 0 0; color:var(--ac-muted); font-size:11px; }
    .ac-business-state { display:inline-flex; align-items:center; gap:7px; min-height:30px; padding:0 10px; border:1px solid #cce8dd; border-radius:9px; color:#13795b; background:#edf9f4; font-size:9px; font-weight:800; white-space:nowrap; }
    .ac-business-state.partial,.ac-business-state.stale { color:#9a6508; border-color:#f1ddb1; background:#fff8e9; }
    .ac-business-state.unavailable,.ac-business-state.error { color:#9b3342; border-color:#f0cbd1; background:#fff2f4; }
    .ac-filterbar { display:grid; grid-template-columns:minmax(190px,260px) minmax(260px,1fr) auto; gap:10px; align-items:end; margin-bottom:12px; padding:12px; border:1px solid var(--ac-border); border-radius:13px; background:#fff; }
    .ac-filterbar label { display:grid; gap:5px; color:#8792a4; font-size:8px; font-weight:900; letter-spacing:.08em; text-transform:uppercase; }
    .ac-filterbar select,.ac-filterbar input { width:100%; min-height:38px; border:1px solid var(--ac-border); border-radius:9px; background:#fafbfd; color:var(--ac-text); padding:0 10px; font-size:11px; }
    .ac-filter-range { align-self:center; color:#6f7b8e; font-size:10px; font-weight:750; }
    .ac-kpis { display:grid; grid-template-columns:repeat(6,minmax(0,1fr)); gap:10px; margin-bottom:12px; }
    .ac-kpi { position:relative; min-width:0; min-height:128px; padding:15px; border:1px solid var(--ac-border); border-radius:16px; background:#fff; box-shadow:0 3px 12px rgba(15,23,42,.035); }
    .ac-kpi.accent { border-color:#d8ddff; background:linear-gradient(145deg,#fff,#f8f8ff); }
    .ac-kpi-label { display:flex; align-items:flex-start; justify-content:space-between; gap:7px; min-height:27px; color:#758196; font-size:9px; font-weight:750; }
    .ac-kpi-value { margin:11px 0 9px; color:#0f172a; font-size:clamp(20px,1.65vw,28px); font-weight:850; line-height:1.05; letter-spacing:-.045em; overflow-wrap:anywhere; }
    .ac-kpi-meta { color:#909aaa; font-size:8px; line-height:1.4; }
    .ac-grid { display:grid; grid-template-columns:repeat(12,minmax(0,1fr)); gap:12px; }
    .ac-span-12 { grid-column:span 12; }.ac-span-8 { grid-column:span 8; }.ac-span-7 { grid-column:span 7; }.ac-span-6 { grid-column:span 6; }.ac-span-5 { grid-column:span 5; }.ac-span-4 { grid-column:span 4; }
    .ac-panel { min-width:0; padding:16px; border:1px solid var(--ac-border); border-radius:16px; background:#fff; box-shadow:0 3px 12px rgba(15,23,42,.035); }
    .ac-panel-head { display:flex; align-items:flex-start; justify-content:space-between; gap:12px; margin-bottom:12px; }
    .ac-panel-head small,.ac-panel-head strong { display:block; }
    .ac-panel-head small { margin-bottom:3px; color:#9aa4b4; font-size:8px; font-weight:900; letter-spacing:.11em; text-transform:uppercase; }
    .ac-panel-head strong { color:#172033; font-size:14px; }
    .ac-panel-head span { color:#7a8699; font-size:9px; }
    .ac-empty { min-height:190px; display:grid; align-content:center; justify-items:center; gap:7px; padding:22px; text-align:center; border:1px dashed #dce2ec; border-radius:12px; background:#fafbfd; }
    .ac-empty b { font-size:12px; }.ac-empty span { max-width:440px; color:#7f8a9d; font-size:10px; line-height:1.5; }
    .ac-empty button { min-height:34px; padding:0 11px; border:1px solid #dce2ec; border-radius:8px; color:#31569f; background:#fff; font-size:9px; font-weight:800; cursor:pointer; }
    .ac-list { display:grid; }
    .ac-list-row { display:grid; grid-template-columns:minmax(0,1fr) auto; align-items:center; gap:12px; min-height:54px; padding:9px 0; border-bottom:1px solid #edf0f5; }
    .ac-list-row:last-child { border-bottom:0; }
    .ac-list-row b,.ac-list-row span { display:block; overflow-wrap:anywhere; }
    .ac-list-row b { font-size:10px; }.ac-list-row span { margin-top:3px; color:#7f8a9c; font-size:9px; line-height:1.4; }
    .ac-pill { display:inline-flex; align-items:center; min-height:25px; padding:0 8px; border-radius:8px; color:#526075; background:#f0f3f8; font-size:8px; font-weight:850; white-space:nowrap; }
    .ac-pill.risk { color:#a53745; background:#fff0f2; }.ac-pill.warning { color:#9a6508; background:#fff6df; }.ac-pill.good { color:#13795b; background:#eaf8f2; }
    .ac-chart { min-height:300px; }.ac-chart .analytics-combined-chart { min-height:270px; margin-top:0; }.ac-chart .analytics-combined-chart svg { height:255px; }
    .ac-provider-split { display:grid; gap:14px; padding-top:4px; }
    .ac-provider-row { display:grid; grid-template-columns:104px minmax(0,1fr) auto; align-items:center; gap:10px; }
    .ac-provider-row b { font-size:10px; }.ac-provider-row strong { font-size:10px; white-space:nowrap; }
    .ac-track { height:6px; overflow:hidden; border-radius:99px; background:#edf0f5; }.ac-track i { display:block; height:100%; border-radius:inherit; background:var(--track,#2563eb); }
    .ac-table-wrap { width:100%; overflow:auto; border:1px solid #e8ecf2; border-radius:12px; }
    .ac-table { width:100%; min-width:820px; border-collapse:collapse; font-size:9px; }
    .ac-table th { position:sticky; top:0; z-index:1; padding:10px 11px; color:#7a8698; background:#f7f9fc; text-align:left; font-size:8px; letter-spacing:.04em; text-transform:uppercase; white-space:nowrap; }
    .ac-table td { padding:11px; border-top:1px solid #edf0f4; color:#5e6a7d; vertical-align:top; }
    .ac-table td strong { display:block; color:#172033; font-size:9.5px; overflow-wrap:anywhere; }.ac-table td span { display:block; margin-top:2px; color:#8a95a6; }
    .ac-waterfall { min-height:300px; display:flex; align-items:flex-end; gap:10px; padding:30px 8px 10px; }
    .ac-waterfall-item { flex:1; min-width:64px; display:grid; align-content:end; gap:7px; text-align:center; }
    .ac-waterfall-bar { min-height:18px; display:grid; align-items:start; padding-top:5px; border-radius:8px 8px 3px 3px; color:#fff; background:#2563eb; font-size:8px; font-weight:850; }
    .ac-waterfall-item.negative .ac-waterfall-bar { background:#ee6478; }.ac-waterfall-item.total .ac-waterfall-bar { background:#18a979; }
    .ac-waterfall-item span { color:#697589; font-size:8px; line-height:1.3; }
    .ac-map { min-height:500px; position:relative; overflow:hidden; border:1px solid #e5eaf2; border-radius:14px; background:linear-gradient(180deg,#f6f8fc,#eef2fa); }
    .ac-map-shape { position:absolute; inset:20% 8% 20%; border:2px solid #cdd7ec; border-radius:48% 35% 42% 31% / 37% 48% 32% 45%; transform:skewX(-8deg); background:linear-gradient(135deg,#eef2ff,#f5ebff); }
    .ac-map-note { position:absolute; left:18px; right:18px; bottom:16px; padding:10px; border:1px solid #dce3ef; border-radius:9px; color:#728096; background:rgba(255,255,255,.88); font-size:9px; }
    .ac-recommendations { display:grid; gap:8px; }.ac-recommendation { padding:11px; border:1px solid #e7ebf2; border-radius:11px; background:#fbfcfe; }.ac-recommendation b,.ac-recommendation span { display:block; }.ac-recommendation b { font-size:10px; }.ac-recommendation span { margin-top:4px; color:#7d889a; font-size:9px; line-height:1.45; }
    .ac-skeleton { position:relative; min-height:118px; overflow:hidden; background:#eef2f7; }
    .ac-skeleton::after { content:""; position:absolute; inset:0; transform:translateX(-100%); background:linear-gradient(90deg,transparent,rgba(255,255,255,.85),transparent); animation:analytics-shimmer 1.15s infinite; }
    .ac-brand b,.ac-brand span{display:block}.ac-brand b{color:#fff;font-size:12px;letter-spacing:.12em}.ac-brand span{margin-top:3px;color:#7f8da5;font-size:9px}
    .ac-nav i{width:20px;height:20px;display:grid;place-items:center;font-style:normal;color:inherit}
    .ac-heading h2{margin:0;color:#101827;font-size:clamp(25px,2.1vw,34px);line-height:1.08;letter-spacing:-.045em}.ac-heading p{margin:6px 0 0}
    .ac-business-state.ok{color:#13795b;border-color:#cce8dd;background:#edf9f4}.ac-business-state.unknown{color:#667085;border-color:#d8dee8;background:#f5f7fa}
    .ac-market-switch button.active.ozon{color:#fff;background:var(--ac-blue)}.ac-market-switch button.active.wb{color:#fff;background:var(--ac-wb)}
    .ac-filterbar button,.ac-toolbar button{min-height:38px;padding:0 14px;border:0;border-radius:9px;color:#fff;background:#2563eb;font-size:10px;font-weight:800;cursor:pointer}.ac-period-label{align-self:center;color:#6f7b8e;font-size:10px;font-weight:750}
    .ac-kpi>span{display:block;min-height:27px;color:#758196;font-size:9px;font-weight:750}.ac-kpi>strong{display:block;margin:11px 0 9px;color:#0f172a;font-size:clamp(20px,1.65vw,28px);font-weight:850;line-height:1.05;letter-spacing:-.045em;overflow-wrap:anywhere}.ac-kpi>small{display:block;color:#909aaa;font-size:8px;line-height:1.4}
    .ac-panel.span-12{grid-column:span 12}.ac-panel.span-8{grid-column:span 8}.ac-panel.span-6{grid-column:span 6}.ac-panel.span-4{grid-column:span 4}.ac-panel-head h3{margin:0;color:#172033;font-size:14px}
    .ac-list-row>strong{color:#526075;font-size:9px;white-space:normal;text-align:right}.ac-panel-copy{color:#6f7b8e;font-size:10px;line-height:1.55}
    .ac-toolbar{display:flex;align-items:end;gap:12px;margin-bottom:12px;padding:12px;border:1px solid var(--ac-border);border-radius:13px;background:#fff}.ac-toolbar>span{margin-left:auto;color:#6f7b8e;font-size:10px;font-weight:750}.ac-page-search{display:grid;gap:5px;flex:1;color:#8792a4;font-size:8px;font-weight:900;letter-spacing:.05em;text-transform:uppercase}.ac-page-search input{min-height:40px;padding:0 11px;border:1px solid var(--ac-border);border-radius:9px;background:#fafbfd;color:#111827;font-size:11px}
    .ac-waterfall>div{flex:1;min-width:72px;display:grid;align-content:end;gap:7px;text-align:center}.ac-waterfall>div i{display:block;height:var(--bar);min-height:18px;border-radius:8px 8px 3px 3px;background:#2563eb}.ac-waterfall>div.negative i{background:#ee6478}.ac-waterfall>div.total i{background:#18a979}.ac-waterfall>div span{color:#697589;font-size:8px}.ac-waterfall>div strong{font-size:9px;overflow-wrap:anywhere}
    .ac-russia-shape{position:absolute;inset:15% 8% 25%;border:2px solid #cdd7ec;border-radius:48% 35% 42% 31% / 37% 48% 32% 45%;transform:skewX(-8deg);background:linear-gradient(135deg,#eef2ff,#f5ebff)}.ac-map>.ac-empty{position:absolute;left:18px;right:18px;bottom:16px;min-height:110px;background:rgba(255,255,255,.92)}
    @media (max-width:1380px) { .ac-kpis{grid-template-columns:repeat(3,minmax(0,1fr));}.ac-span-8,.ac-span-7,.ac-panel.span-8{grid-column:span 12}.ac-span-5,.ac-span-4,.ac-panel.span-4{grid-column:span 6} }
    @media (max-width:899px) {
      body.web-mode.analytics-mode .body{padding:12px 14px 90px!important}.ac-shell{display:block;min-height:0;border-radius:14px}.ac-sidebar{padding:10px}.ac-brand,.ac-sidebar-status{display:none}.ac-nav{display:flex;overflow-x:auto;margin:0;scrollbar-width:none}.ac-nav button{flex:0 0 auto;width:auto;grid-template-columns:18px auto;padding:0 12px}.ac-nav button.active::before{left:8px;right:8px;top:auto;bottom:-1px;width:auto;height:3px;border-radius:3px}.ac-topbar{flex-wrap:wrap;padding:10px}.ac-search{order:2;flex-basis:100%;max-width:none}.ac-market-switch{margin-left:0}.ac-content{padding:14px}.ac-heading{align-items:flex-start}.ac-filterbar{grid-template-columns:1fr}.ac-kpis{grid-template-columns:repeat(2,minmax(0,1fr))}.ac-span-6,.ac-span-5,.ac-span-4,.ac-panel.span-8,.ac-panel.span-6,.ac-panel.span-4{grid-column:span 12}.ac-map{min-height:340px}
    }
    @media (max-width:520px) { .ac-kpis{grid-template-columns:1fr 1fr;gap:8px}.ac-kpi{min-height:116px;padding:12px}.ac-kpi-value{font-size:21px}.ac-heading{display:grid}.ac-business-state{width:max-content}.ac-sync{width:100%}.ac-topbar{display:grid;grid-template-columns:1fr}.ac-market-switch{width:100%}.ac-market-switch button{flex:1}.ac-search{order:initial}.ac-content{padding:12px}.ac-provider-row{grid-template-columns:86px minmax(0,1fr)}.ac-provider-row strong{grid-column:2}.ac-waterfall{overflow-x:auto}.ac-waterfall-item{flex:0 0 72px}}

    /* Canonical responsive layer. Keep this block last so legacy rules cannot
       silently override the desktop and mobile application shells. */
    :where(button, [role="button"], .tab, .nav-item, .workspace-tab) {
      touch-action: manipulation;
    }

    :where(.tab, .nav-item, .workspace-tab, .bottom-nav button) {
      min-height: 44px;
    }

    :where(button, input, select, textarea):focus-visible {
      outline: 3px solid rgba(25, 89, 243, .28);
      outline-offset: 2px;
    }

    @media (max-width: 899px) {
      body.web-mode .app-shell,
      body.web-mode .screen,
      body.web-mode .screen-content {
        min-width: 0;
        max-width: 100%;
      }

      body.web-mode .screen {
        padding-left: 14px;
        padding-right: 14px;
      }

      body.web-mode .page-heading h1,
      body.web-mode .screen-title {
        font-size: clamp(26px, 8vw, 34px);
        line-height: 1.05;
      }

      body.web-mode .tabs,
      body.web-mode .segmented,
      body.web-mode .workspace-tabs {
        gap: 4px;
        padding: 4px;
      }

      body.web-mode .tab,
      body.web-mode .segmented button,
      body.web-mode .workspace-tab {
        min-height: 44px;
        padding: 9px 10px;
        font-size: 12px;
        line-height: 1.15;
      }

      body.web-mode .operations-kpis {
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 9px;
      }

      body.web-mode .operations-kpi {
        min-height: 116px;
        padding: 14px;
        border-radius: 14px;
      }

      body.web-mode .operations-kpi span {
        font-size: 10px;
        letter-spacing: .045em;
      }

      body.web-mode .operations-kpi strong {
        margin: 11px 0 6px;
        font-size: 27px;
      }

      body.web-mode .operations-kpi small {
        font-size: 11px;
        line-height: 1.3;
      }

      body.web-mode .operations-actions {
        grid-template-columns: 1fr;
      }

      body.web-mode .operations-actions button {
        min-height: 48px;
        font-size: 13px;
      }

      body.web-mode .orders-board {
        display: grid;
        grid-template-columns: none;
        grid-auto-flow: column;
        grid-auto-columns: min(86vw, 390px);
        gap: 12px;
        width: calc(100% + 14px);
        margin-right: -14px;
        padding: 2px 14px 14px 1px;
        overflow-x: auto;
        overflow-y: visible;
        scroll-snap-type: x mandatory;
        scroll-padding-left: 1px;
        overscroll-behavior-inline: contain;
        -webkit-overflow-scrolling: touch;
      }

      body.web-mode .orders-board > * {
        min-width: 0;
        scroll-snap-align: start;
        scroll-snap-stop: always;
      }

      body.web-mode .form-grid,
      body.web-mode .details-grid,
      body.web-mode .admin-grid,
      body.web-mode .analytics-grid {
        grid-template-columns: minmax(0, 1fr);
      }

      body.web-mode .card,
      body.web-mode .panel,
      body.web-mode .form-card {
        max-width: 100%;
        border-radius: 16px;
      }

      body.web-mode .table-wrap,
      body.web-mode .data-table-wrap {
        max-width: 100%;
        overflow-x: auto;
        overscroll-behavior-inline: contain;
        -webkit-overflow-scrolling: touch;
      }
    }

    @media (max-width: 430px) {
      body.web-mode .operations-kpi {
        min-height: 108px;
        padding: 12px;
      }

      body.web-mode .operations-kpi strong {
        font-size: 24px;
      }

      body.web-mode .orders-board {
        grid-auto-columns: calc(100vw - 42px);
      }
    }

    /* Shared loading and connection states. */
    #connectionView[hidden] { display: none !important; }
    #connectionView:not([hidden]) {
      min-height: 100dvh;
      display: grid;
      place-items: center;
      padding: 24px;
    }

    #connectionView:not([hidden]) .connection-card,
    #connectionView:not([hidden]) [role="status"] {
      width: min(100%, 460px);
      padding: 22px;
      border: 1px solid var(--line);
      border-radius: 20px;
      background: rgba(255,255,255,.92);
      box-shadow: var(--shadow-soft), var(--inset-shadow);
    }

    #connectionView:not([hidden]) [role="status"]::before {
      content: "";
      display: block;
      width: 42px;
      height: 4px;
      margin-bottom: 16px;
      border-radius: 999px;
      background: linear-gradient(90deg, var(--accent), #8eb2ff, var(--accent));
      background-size: 200% 100%;
      animation: connection-progress 1.2s linear infinite;
    }

    @keyframes connection-progress {
      to { background-position: -200% 0; }
    }

    /* Consistent semantic statuses across production, warehouse and reports. */
    :where(.status, .status-pill, .badge)[data-status="free"],
    :where(.status, .status-pill, .badge).free {
      color: #1746b6;
      border-color: rgba(25,89,243,.24);
      background: #edf3ff;
    }

    :where(.status, .status-pill, .badge)[data-status="active"],
    :where(.status, .status-pill, .badge).active,
    :where(.status, .status-pill, .badge).in-progress {
      color: #8c5300;
      border-color: rgba(242,162,58,.32);
      background: #fff5e6;
    }

    :where(.status, .status-pill, .badge)[data-status="done"],
    :where(.status, .status-pill, .badge).done,
    :where(.status, .status-pill, .badge).completed {
      color: #176b43;
      border-color: rgba(49,168,107,.28);
      background: #eaf8f1;
    }

    :where(.status, .status-pill, .badge)[data-status="blocked"],
    :where(.status, .status-pill, .badge).blocked,
    :where(.status, .status-pill, .badge).overdue {
      color: #a92d3a;
      border-color: rgba(221,79,93,.30);
      background: #fff0f2;
    }

    @media (max-width: 899px) {
      body.web-mode .web-appbar {
        min-height: 58px;
        gap: 8px;
        padding: max(8px, env(safe-area-inset-top)) 12px 8px;
      }

      body.web-mode .web-role-block {
        display: none !important;
      }

      body.web-mode .workspace-tabs {
        position: sticky;
        top: 0;
        z-index: 20;
        display: flex;
        width: 100%;
        overflow-x: auto;
        scroll-snap-type: x proximity;
        scrollbar-width: none;
        background: rgba(247,249,253,.94);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
      }

      body.web-mode .workspace-tabs::-webkit-scrollbar { display: none; }

      body.web-mode .workspace-tab {
        flex: 0 0 auto;
        min-width: 148px;
        scroll-snap-align: start;
      }

      body.web-mode .bottom-nav {
        padding-bottom: max(8px, env(safe-area-inset-bottom));
        background: rgba(255,255,255,.95);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
      }

      body.web-mode :where(.form-actions, .create-actions, .wizard-actions, .action-row):has(.primary) {
        position: sticky;
        bottom: calc(68px + env(safe-area-inset-bottom));
        z-index: 12;
        padding: 8px;
        border: 1px solid var(--line);
        border-radius: 14px;
        background: rgba(255,255,255,.94);
        box-shadow: 0 10px 30px rgba(16,23,34,.14);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
      }

      body.web-mode :where(.warehouse-map, .storage-map, .location-grid) {
        max-width: 100%;
        overflow-x: auto;
        overscroll-behavior-inline: contain;
        scroll-snap-type: x proximity;
        -webkit-overflow-scrolling: touch;
      }

      body.web-mode :where(.warehouse-cell, .storage-cell, [data-location-code]) {
        min-width: 116px;
        min-height: 82px;
        scroll-snap-align: start;
      }

      body.web-mode :where(.employee-card, .staff-card) {
        padding: 14px;
        border-radius: 15px;
      }

      body.web-mode :where(.employee-card, .staff-card) :where(button, .button) {
        min-height: 44px;
      }
    }

    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after {
        scroll-behavior: auto !important;
        animation-duration: .01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: .01ms !important;
      }
    }

    @media (min-width: 900px) and (max-width: 1100px) {
      body.web-mode .web-role-block {
        display: none !important;
      }

      body.web-mode .web-appbar,
      body.web-mode .workspace-tabs {
        min-width: 0;
      }

      body.web-mode .operations-kpis {
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }
    }
    .marketplace-product-avatar {
      width: 48px; height: 58px; flex: 0 0 48px; position: relative;
      display: inline-grid; place-items: center; overflow: hidden;
      border: 1px solid rgba(25, 54, 112, .12); border-radius: 12px;
      background: linear-gradient(145deg, #f8faff, #edf2fb); color: #718096;
      font-size: 18px;
    }
    .marketplace-product-avatar img {
      position: absolute; inset: 0; z-index: 1; width: 100%; height: 100%;
      object-fit: contain; padding: 3px; background: #fff;
    }
    .marketplace-product-avatar.compact { width: 34px; height: 42px; flex-basis: 34px; border-radius: 9px; }
    .marketplace-product-avatar.large {
      width: 92px; height: 116px; flex-basis: 92px; border-radius: 14px; background: #fff;
    }
    .marketplace-product-heading, .marketplace-table-product {
      display: flex; align-items: center; gap: 11px; min-width: 0;
    }
    .marketplace-product-heading > div, .marketplace-table-product > span:last-child { min-width: 0; }
    .marketplace-product-heading strong, .marketplace-table-product strong {
      display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
    }
    .marketplace-variant-grid {
      display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px;
    }
    .marketplace-color-sections { display: grid; gap: 20px; }
    .marketplace-color-section { display: grid; gap: 10px; }
    .marketplace-color-heading {
      display: flex; align-items: center; justify-content: space-between; gap: 12px;
      padding: 10px 13px; border-left: 4px solid #2462ec; border-radius: 0 11px 11px 0;
      background: linear-gradient(90deg, rgba(35, 96, 236, .10), rgba(35, 96, 236, .025));
    }
    .marketplace-color-heading b { font-size: 14px; }
    .marketplace-color-heading span { color: var(--muted); font-size: 11px; font-weight: 800; }
    .marketplace-product-card {
      min-width: 0; min-height: 148px; padding: 15px !important;
      display: grid !important; grid-template-columns: 92px minmax(0, 1fr) auto;
      align-items: center !important; gap: 15px !important; text-align: left;
    }
    .marketplace-product-card-body {
      display: grid; align-content: center; gap: 8px; min-width: 0;
    }
    .marketplace-product-card .product-title { display: block; min-width: 0; }
    .marketplace-product-card .product-title b {
      display: -webkit-box; overflow: hidden; -webkit-line-clamp: 2;
      -webkit-box-orient: vertical; font-size: 16px; line-height: 1.22;
    }
    .marketplace-product-primary-meta,
    .marketplace-product-commercial {
      display: flex; flex-wrap: wrap; gap: 7px 14px; color: var(--ink);
      font-size: 13px; font-weight: 750;
    }
    .marketplace-product-primary-meta span,
    .marketplace-product-commercial span {
      display: inline-flex; align-items: center; min-height: 26px; padding: 4px 8px;
      border-radius: 8px; background: rgba(238, 243, 252, .86);
    }
    .marketplace-product-secondary-meta {
      overflow: hidden; color: var(--muted); font-size: 12px; line-height: 1.4;
      text-overflow: ellipsis; white-space: nowrap;
    }
    .marketplace-card-arrow { align-self: start; margin-top: 2px; }
    .marketplace-stock-section { display: grid; gap: 14px; }
    .marketplace-stock-filters {
      display: grid; grid-template-columns: repeat(auto-fit, minmax(185px, 1fr)); gap: 12px;
      padding: 15px; border: 1px solid rgba(35, 75, 160, .12); border-radius: 15px;
      background: rgba(255, 255, 255, .78);
    }
    .marketplace-stock-filters label { display: grid; gap: 6px; min-width: 0; }
    .marketplace-stock-filters label > span {
      color: var(--muted); font-size: 11px; font-weight: 850; text-transform: uppercase; letter-spacing: .04em;
    }
    .marketplace-stock-filters select { width: 100%; }
    .marketplace-chart-panel {
      padding: 20px !important; display: grid; gap: 18px; min-height: 430px;
    }
    .marketplace-chart-head {
      display: flex; align-items: flex-start; justify-content: space-between; gap: 18px;
    }
    .marketplace-chart-summary { display: grid; gap: 6px; }
    .marketplace-chart-summary > span {
      color: var(--muted); font-size: 11px; font-weight: 850; text-transform: uppercase; letter-spacing: .06em;
    }
    .marketplace-chart-summary strong { font-size: clamp(26px, 3vw, 40px); line-height: 1; }
    .marketplace-chart-summary small { color: var(--muted); font-size: 12px; }
    .marketplace-chart-switch {
      display: inline-grid; grid-template-columns: repeat(2, minmax(130px, 1fr)); gap: 4px;
      padding: 4px; border: 1px solid var(--line); border-radius: 13px; background: rgba(238, 242, 249, .9);
    }
    .marketplace-chart-switch button {
      min-height: 38px; padding: 8px 13px; border: 0; border-radius: 9px;
      background: transparent; color: var(--muted); font: inherit; font-size: 12px; font-weight: 850; cursor: pointer;
    }
    .marketplace-chart-switch button.active {
      color: #fff; background: linear-gradient(135deg, #2765f4, #1144c8); box-shadow: 0 8px 18px rgba(25, 77, 207, .22);
    }
    .marketplace-chart-canvas {
      min-height: 300px; padding: 12px 8px 0; border-radius: 15px;
      background: linear-gradient(180deg, rgba(243, 247, 255, .78), rgba(255, 255, 255, .32));
    }
    .marketplace-chart-canvas .marketplace-line-chart { min-height: 280px; }
    .marketplace-chart-canvas .marketplace-line-chart svg { width: 100%; height: 280px; overflow: visible; }
    .marketplace-chart-note { color: var(--muted); font-size: 12px; }
    .marketplace-line-chart { position: relative; }
    .chart-point-hit { fill: transparent; stroke: transparent; pointer-events: all; cursor: crosshair; }
    .marketplace-point-tooltip {
      position: absolute; z-index: 5; min-width: 152px; padding: 9px 11px;
      border-radius: 10px; background: #111827; color: #fff;
      box-shadow: 0 10px 26px rgba(15, 23, 42, .28); pointer-events: none;
      transform: translate(-50%, calc(-100% - 14px)); text-align: center;
    }
    .marketplace-point-tooltip[hidden] { display: none !important; }
    .marketplace-point-tooltip b { display: block; font-size: 13px; white-space: nowrap; }
    .marketplace-point-tooltip span { display: block; margin-top: 3px; color: #cbd5e1; font-size: 11px; }
    .marketplace-date-range {
      display: grid; grid-template-columns: repeat(2, minmax(150px, 1fr)); gap: 10px; min-width: min(100%, 330px);
    }
    .marketplace-date-range label { display: grid; gap: 5px; }
    .marketplace-date-range label > span {
      color: var(--muted); font-size: 10px; font-weight: 850; text-transform: uppercase; letter-spacing: .05em;
    }
    .marketplace-date-range input { width: 100%; min-height: 42px; }
    .marketplace-stock-grid {
      display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px;
    }
    .marketplace-stock-card {
      min-width: 0; padding: 14px !important; display: grid !important;
      grid-template-columns: 56px minmax(0, 1fr) auto; align-items: center !important; gap: 12px !important;
    }
    .marketplace-stock-card[hidden] { display: none !important; }
    .marketplace-stock-card-body { display: grid; gap: 7px; min-width: 0; text-align: left; }
    .marketplace-stock-card-body b {
      overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: 14px;
    }
    .marketplace-stock-card-body > small { color: var(--muted); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .marketplace-stock-breakdown { display: flex; flex-wrap: wrap; gap: 6px; }
    .marketplace-stock-breakdown span {
      padding: 4px 7px; border-radius: 7px; background: rgba(237, 242, 250, .9);
      color: var(--muted); font-size: 11px; font-weight: 750;
    }
    .marketplace-stock-result { display: grid; justify-items: end; gap: 7px; }
    .marketplace-stock-level.enough { color: #176b44; background: #e1f4e9; }
    .marketplace-stock-level.low { color: #9a5a00; background: #fff0d6; }
    .marketplace-stock-level.absent { color: #b42335; background: #ffe4e8; }
    .marketplace-stock-empty { display: none; }
    .marketplace-stock-empty.visible { display: block; }
    .marketplace-menu-strip {
      padding: 14px !important; gap: 5px !important; align-content: start;
      border: 1px solid rgba(25, 54, 112, .10); border-radius: 18px;
      background: rgba(255, 255, 255, .86); box-shadow: 0 12px 34px rgba(35, 61, 115, .08);
    }
    .marketplace-menu-label {
      margin: 10px 9px 5px; color: #8a96aa; font-size: 9px; font-weight: 900;
      letter-spacing: .12em; text-transform: uppercase;
    }
    .marketplace-menu-label:first-child { margin-top: 2px; }
    .marketplace-menu-link, .marketplace-provider-menu-button {
      width: 100%; min-height: 42px; padding: 9px 11px !important; display: flex !important;
      align-items: center; gap: 10px; border: 0; border-radius: 11px !important;
      background: transparent; color: #566276; font-size: 12px; font-weight: 800;
      text-align: left; cursor: pointer;
    }
    .marketplace-menu-link:hover, .marketplace-provider-menu-button:hover { background: #f0f4fc; color: #1748c9; }
    .marketplace-menu-link.active, .marketplace-provider-menu-button.active {
      color: #fff !important; background: linear-gradient(135deg, #2364f5, #0f43c7) !important;
      box-shadow: 0 8px 18px rgba(27, 78, 204, .22);
    }
    .marketplace-menu-icon {
      width: 24px; height: 24px; flex: 0 0 24px; display: inline-grid; place-items: center;
      border-radius: 7px; background: rgba(40, 91, 211, .09); color: #2355ca; font-size: 12px;
    }
    .active .marketplace-menu-icon { background: rgba(255,255,255,.18); color: #fff; }
    .marketplace-provider-menu-button small { margin-left: auto; color: #99a3b5; font-size: 9px; }
    .marketplace-provider-menu-button.active small { color: rgba(255,255,255,.75); }
    .marketplace-provider-menu-button:disabled { opacity: .52; cursor: not-allowed; }
    .marketplace-line-chart { width: 100%; min-height: 230px; display: grid; align-items: center; }
    .marketplace-line-chart svg { width: 100%; height: 230px; overflow: visible; }
    .marketplace-line-chart .chart-grid { stroke: #dfe6f1; stroke-width: 1; stroke-dasharray: 4 6; }
    .marketplace-line-chart .chart-axis-label { fill: #8b97aa; font-size: 10px; }
    .marketplace-line-chart .chart-area { fill: url(#marketplaceChartArea); opacity: .7; }
    .marketplace-line-chart .chart-line-primary { fill: none; stroke: #1764f5; stroke-width: 3; stroke-linecap: round; stroke-linejoin: round; }
    .marketplace-line-chart .chart-line-secondary { fill: none; stroke: #7da6ff; stroke-width: 2.5; stroke-linecap: round; stroke-linejoin: round; }
    .marketplace-line-chart .chart-point-primary { fill: #fff; stroke: #1764f5; stroke-width: 2.5; }
    .marketplace-line-chart .chart-point-secondary { fill: #fff; stroke: #7da6ff; stroke-width: 2; }
    .marketplace-chart-legend { display: flex; flex-wrap: wrap; gap: 14px; color: var(--muted); font-size: 11px; }
    .marketplace-chart-legend span { display: inline-flex; align-items: center; gap: 6px; }
    .marketplace-chart-legend i { width: 16px; height: 3px; border-radius: 3px; background: #1764f5; }
    .marketplace-chart-legend i.secondary { background: #7da6ff; }
    @media (max-width: 700px) {
      .marketplace-product-avatar { width: 42px; height: 52px; flex-basis: 42px; }
      .marketplace-product-avatar.compact { width: 32px; height: 40px; flex-basis: 32px; }
      .marketplace-variant-grid { grid-template-columns: 1fr; gap: 10px; }
      .marketplace-product-card {
        min-height: 130px; grid-template-columns: 76px minmax(0, 1fr) auto;
        gap: 11px !important; padding: 12px !important;
      }
      .marketplace-product-avatar.large { width: 76px; height: 98px; flex-basis: 76px; }
      .marketplace-product-card .product-title b { font-size: 14px; }
      .marketplace-product-primary-meta, .marketplace-product-commercial { gap: 5px 8px; font-size: 12px; }
      .marketplace-product-secondary-meta { white-space: normal; }
      .marketplace-stock-filters { grid-template-columns: 1fr; padding: 12px; }
      .marketplace-chart-panel { min-height: 390px; padding: 14px !important; }
      .marketplace-chart-head { display: grid; }
      .marketplace-chart-switch { width: 100%; grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .marketplace-chart-canvas { min-height: 250px; padding-inline: 0; }
      .marketplace-chart-canvas .marketplace-line-chart,
      .marketplace-chart-canvas .marketplace-line-chart svg { min-height: 240px; height: 240px; }
      .marketplace-date-range { width: 100%; min-width: 0; grid-template-columns: 1fr; }
      .marketplace-stock-grid { grid-template-columns: 1fr; }
      .marketplace-stock-card { grid-template-columns: 48px minmax(0, 1fr) auto; padding: 11px !important; gap: 9px !important; }
      .marketplace-stock-card-body b, .marketplace-stock-card-body > small { white-space: normal; }
      .marketplace-menu-strip {
        display: flex !important; overflow-x: auto; padding: 8px !important; gap: 6px !important;
        border-radius: 14px; position: static !important; scrollbar-width: none;
      }
      .marketplace-menu-strip::-webkit-scrollbar { display: none; }
      .marketplace-menu-label { display: none; }
      .marketplace-menu-link, .marketplace-provider-menu-button {
        width: auto; min-width: max-content; min-height: 38px; padding: 7px 10px !important;
      }
      .marketplace-provider-menu-button small { display: none; }
      .marketplace-menu-icon { width: 21px; height: 21px; flex-basis: 21px; }
      .marketplace-line-chart, .marketplace-line-chart svg { min-height: 190px; height: 190px; }
    }
    .wms-stock-product-balance {
      display: grid;
      justify-items: end;
      gap: 6px;
      min-width: 112px;
      text-align: right;
    }

    .wms-stock-product-balance small {
      color: var(--muted);
      font-size: 11px;
      line-height: 1.3;
    }

    .wms-stock-product-balance .small-button {
      min-height: 34px;
      padding: 8px 14px;
    }

    .wms-location-detail > .button-row > :last-child:nth-child(3) {
      grid-column: 1 / -1;
    }

    @media (max-width: 520px) {
      .wms-stock-product-row {
        grid-template-columns: minmax(0, 1fr);
        align-items: stretch;
        gap: 12px;
        padding: 12px !important;
      }

      .wms-stock-product-row .wms-product-rich {
        align-items: flex-start;
        gap: 10px;
      }

      .wms-stock-product-row .marketplace-product-avatar.large {
        width: 64px;
        height: 82px;
        flex-basis: 64px;
        border-radius: 11px;
      }

      .wms-stock-product-row .wms-product-rich-copy b {
        font-size: 14px;
        line-height: 1.25;
        overflow-wrap: anywhere;
      }

      .wms-stock-product-row .wms-product-rich-copy span,
      .wms-stock-product-row .wms-product-rich-copy small {
        font-size: 11px;
        overflow-wrap: anywhere;
      }

      .wms-stock-product-balance {
        width: 100%;
        min-width: 0;
        grid-template-columns: auto minmax(0, 1fr);
        align-items: center;
        justify-items: start;
        text-align: left;
      }

      .wms-stock-product-balance small {
        justify-self: end;
        text-align: right;
      }

      .wms-stock-product-balance .small-button {
        grid-column: 1 / -1;
        width: 100%;
      }

      .wms-guided-scanner .report-row {
        grid-template-columns: minmax(0, 1fr) 34px;
        padding: 10px 8px;
      }

      .wms-guided-scanner .button-row,
      .wms-guided-scanner .small-button {
        width: 100%;
      }

      .bottom-nav {
        padding-left: 5px;
        padding-right: 5px;
        gap: 0;
      }

      .nav-btn {
        padding-inline: 1px;
        font-size: 9px;
      }

      .nav-btn span:last-child {
        overflow-wrap: normal;
        word-break: normal;
        white-space: nowrap;
      }
    }

    /* Functional-only workspace: keep controls, values and operational states. */
    .screen-head p,
    .employee-detail-title p,
    .operations-kpi small,
    .card.kpi > span:not(.kpi-top),
    .summary-card > small,
    .marketplace-v2-kpi > small,
    .analytics-overview-kpi > small,
    .analytics-provider-metric > small,
    .analytics-chart-source,
    .marketplace-dashboard-kpi > small,
    .marketplace-chart-note,
    .ac-kpi > small,
    .ac-heading p,
    .ac-brand span,
    .ac-panel-copy,
    .marketplace-placeholder p,
    .ac-map-note,
    .arbitrary-operation-head span,
    .arbitrary-operation-help,
    .ac-empty span {
      display: none !important;
    }

    .screen-head p.operational-message {
      display: block !important;
    }

    .operations-kpi,
    .marketplace-v2-kpi,
    .analytics-overview-kpi,
    .ac-kpi,
    .marketplace-chart-panel {
      min-height: 0;
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
        <button type="button" data-workspace="analytics">Отчёт</button>
      </nav>
      <div class="appbar-profile"><span>Должность на проекте</span><small id="roleLabel">Загрузка</small></div>
      <div class="appbar-actions">
        <button class="icon-btn" id="backBtn" aria-label="Назад">‹</button>
        <button class="icon-btn profile-btn" id="menuBtn" aria-label="Открыть профиль" title="Профиль"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 12a4.1 4.1 0 1 0 0-8.2A4.1 4.1 0 0 0 12 12Zm0 2.1c-4.4 0-8 2.3-8 5.2 0 .5.4.9.9.9h14.2c.5 0 .9-.4.9-.9 0-2.9-3.6-5.2-8-5.2Z" fill="currentColor"/></svg></button>
      </div>
    </div>

    <nav class="mobile-workspace-nav" id="mobileWorkspaceNav" aria-label="Рабочая среда" hidden>
      <button class="active" type="button" data-workspace="production" aria-current="page">Производство</button>
      <button type="button" data-workspace="warehouse">Склад</button>
      <button type="button" data-workspace="marketplaces" hidden>Маркетплейсы</button>
      <button type="button" data-workspace="analytics" hidden>Отчёт</button>
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
      "ordersPresentationVersion",
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
      "analyticsHubTab",
      "analyticsSearch",
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
      workspace: window.location.pathname.startsWith("/app/marketplaces") ? "marketplaces" : "production",
      marketplaceView: "overview",
      marketplaceProvider: "all",
      marketplacePeriod: "30d",
      marketplaceChartMetric: "revenue",
      marketplaceDateFrom: "",
      marketplaceDateTo: "",
      marketplaceFiltersOpen: false,
      marketplaceFilters: {onlyProblems: false, inStockOnly: false, orderStatus: "all"},
      marketplaceLocationInitialized: false,
      analyticsHubTab: "general",
      analyticsSearch: "",
      screen: window.location.pathname.startsWith("/app/marketplaces") ? "marketplaces" : "shift",
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
      orderMode: "board",
      ordersPresentationVersion: "2",
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
      adminReportType: "timesheet",
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
      wmsData: {loading: false, loaded: false, error: "", locations: [], stock: [], movements: [], shipmentTasks: []},
      wmsCatalogSearch: "",
      wmsCatalogGroup: "",
      wmsCatalog: {loading: false, loaded: false, error: "", products: [], lastSyncAt: ""},
      wmsShipmentDetail: null,
      wmsShipmentTaskDetail: null,
      wmsShipmentTaskTab: "required",
      wmsShipmentTaskLocation: "",
      wmsShipmentTaskScannedAllocationId: "",
      wmsShipmentTaskExpectedAllocationId: "",
      wmsShipmentCreate: false,
      wmsShipmentDraft: {destination: "", comment: "", lines: {}},
      wmsLookup: {barcode: "", productKey: null, error: ""},
      wmsAdminAdjustment: {mode: "inventory", locationId: "", stockId: "", quantity: "", reason: "", targetState: "SCRAPPED", returnView: "admin-stock-control"},
      pushDeviceActive: null,
      pushDeviceSyncing: false,
      wmsDraft: {itemType: "finished", productName: "", productSize: "", productColor: "", productScanned: false, fromLocationScanned: false, toLocationScanned: false, matchedStock: null, matchedLocationCode: "", stageName: "Готово", readyForPosition: "Склад", quantity: "", unit: "шт", materialUnit: "рул", fromLocation: "", toLocation: "", reason: "", targetState: "SCRAPPED", barcode: "", locationZone: "STORAGE", locationName: ""},
      wmsMaterialReceipt: {name: "Ткань", color: "", unit: "рул", quantity: "", comment: ""},
      marketplaceData: {loading: false, loaded: false, error: "", payload: null},
      marketplaceQuality: {loading: false, syncing: false, polling: false, loaded: false, error: "", payload: null, products: null, page: 1, query: ""},
      analyticsQuality: {loading: false, loaded: false, error: "", payload: null},
      analyticsOverview: {loading: false, loaded: false, error: "", payload: null, requestKey: ""},
      marketplaceDetail: null,
      ...persistedUiState,
      data: null,
    };

    if (!state.taskCompletionDrafts || typeof state.taskCompletionDrafts !== "object") state.taskCompletionDrafts = {};
    if (state.ordersPresentationVersion !== "2") {
      state.ordersPresentationVersion = "2";
      if (state.orderMode === "list") state.orderMode = "board";
    }
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
    if (!state.wmsAdminAdjustment || typeof state.wmsAdminAdjustment !== "object") state.wmsAdminAdjustment = {mode: "inventory", locationId: "", stockId: "", quantity: "", reason: "", targetState: "SCRAPPED", returnView: "admin-stock-control"};

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
    const warehouseMoreViews = new Set(["more", "lookup", "products", "transfer", "stock", "movements", "inventory", "scrap", "admin-stock-control", "reports", "map"]);

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

    function requestTaskQuantity(task) {
      const total = Math.max(1, Number(task && task.quantity) || 0);
      const entered = window.prompt(`Сколько изделий взять в работу? Доступно: ${total} шт.`, String(total));
      if (entered === null) return null;
      const quantity = Number.parseInt(String(entered).trim(), 10);
      if (!Number.isInteger(quantity) || quantity <= 0 || quantity > total) {
        showToast("Количество", `Введите целое число от 1 до ${total}.`);
        return null;
      }
      return quantity;
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
      if (state.workspace === "analytics") {
        bottomNav.hidden = true;
        bottomNav.innerHTML = "";
        return;
      }
      bottomNav.hidden = false;
      if (state.workspace === "warehouse") {
        const wmsItems = [
          {id: "overview", label: "Главная", icon: "⌂"},
          {id: "receive", label: "Приёмка", icon: "↓"},
          {id: "putaway", label: "Размещение", icon: "→"},
          {id: "shipments", label: "Отгрузки", icon: "↑"},
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
          {id: "orders", label: "Отгрузки", icon: "↑"},
          {id: "supplies", label: "Поставки", icon: "↓"},
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

    function renderOperationsCenter() {
      const admin = getAdmin() || {};
      const control = admin.production_control || {};
      const period = getAdminHomePeriod();
      const stages = control.stages || [];
      const alerts = control.alerts || [];
      const routeTasks = getRouteTasks().filter((task) => task.work_state !== "cancelled");
      const openShifts = admin.open_shifts || [];
      const todayShiftRows = (period.employees || [])
        .filter((employee) => employee.start_time)
        .sort((left, right) => Number(Boolean(right.on_shift)) - Number(Boolean(left.on_shift)) || String(left.start_time || "").localeCompare(String(right.start_time || "")) || String(left.name || "").localeCompare(String(right.name || ""), "ru"));
      const plan = Number(control.plan || 0);
      const fact = Number(control.fact || 0);
      const activeTasks = Number(control.active_tasks || routeTasks.filter((task) => task.work_state === "in_work").length);
      const overdue = Number(control.overdue_tasks || alerts.filter((alert) => alert.type === "overdue").length);
      const riskCount = alerts.filter((alert) => alert.type === "overdue" || alert.type === "defect" || alert.type === "shortage").length;
      const maxStage = Math.max(1, ...stages.map((stage) => Number(stage.quantity || 0)));
      const planPercent = plan > 0 ? Math.min(100, Math.round(fact / plan * 100)) : 0;
      const keyOrders = [...routeTasks]
        .sort((left, right) => Number(Boolean(right.due_date)) - Number(Boolean(left.due_date)) || Number(right.priority === "urgent") - Number(left.priority === "urgent"))
        .slice(0, 5);

      mainButton.textContent = "Обновить центр";
      mainButton.disabled = false;
      mount.innerHTML = `
        <div class="operations-center">
          <div class="operations-head">
            <div><h2>Операционный центр</h2><p>Производство сейчас · ${escapeHtml(periodDateLabel(period) || "текущий период")}</p></div>
            <div class="live-indicator">Данные актуальны</div>
          </div>
          <div class="operations-kpis">
            <button class="operations-kpi" data-go="analytics"><span>План / факт</span><strong>${escapeHtml(fact)} / ${escapeHtml(plan)}</strong><small>${plan ? `${planPercent}% выполнения плана` : "План пока не задан"}</small></button>
            <button class="operations-kpi" data-go="orders"><span>В работе</span><strong>${escapeHtml(activeTasks)}</strong><small>активных заданий в потоке</small></button>
            <button class="operations-kpi risk" data-go="analytics"><span>Риск срыва</span><strong>${escapeHtml(riskCount)}</strong><small>сигналов требуют внимания</small></button>
            <button class="operations-kpi overdue" data-go="orders"><span>Просрочено</span><strong>${escapeHtml(overdue)}</strong><small>заданий требуют решения</small></button>
          </div>
          <div class="operations-layout">
            <div class="operations-panel">
              <div class="operations-panel-head"><b>Ход смены</b><span>${escapeHtml(openShifts.length)} сотрудников на смене</span></div>
              <div class="shift-progress-value"><div><strong>${escapeHtml(planPercent)}%</strong><small>факт ${escapeHtml(fact)} из ${escapeHtml(plan || 0)} шт</small></div><span class="status-chip ${openShifts.length ? "" : "gray"}">${openShifts.length ? "смена идёт" : "нет открытых смен"}</span></div>
              <div class="progress sage"><i style="--w:${planPercent}%"></i></div>
              <details class="shift-team" open>
                <summary><span>Сотрудники смены</span><small>${escapeHtml(todayShiftRows.length)} за сегодня</small></summary>
                <div class="shift-team-list">${todayShiftRows.length ? todayShiftRows.map((employee) => `
                  <div class="shift-team-row">
                    <div class="shift-team-person"><b>${escapeHtml(employee.name || "Сотрудник")}</b><span>${escapeHtml(employee.position || "Должность не указана")}</span></div>
                    <div class="shift-team-time"><span>Открыл смену <b>${escapeHtml(employee.start_time || "—")}</b></span><span>Закрыл смену <b>${employee.on_shift ? "смена идёт" : escapeHtml(employee.end_time || "не закрыта")}</b></span></div>
                    <span class="status-chip ${employee.on_shift ? "" : "gray"}">${employee.on_shift ? "сейчас на смене" : "смена закрыта"}</span>
                  </div>
                `).join("") : itemEmpty("Сегодня смены ещё не открывали.")}</div>
              </details>
              <div class="operations-panel-head" style="margin-top:23px"><b>Производственные этапы</b><span>WIP и загрузка</span></div>
              <div class="stage-stack">${stages.length ? stages.map((stage) => {
                const quantity = Number(stage.quantity || 0);
                const percent = Math.min(100, Math.round(quantity / maxStage * 100));
                const delayed = Number(stage.overdue || 0) > 0;
                const waiting = !quantity && Number(stage.free || 0) > 0;
                const status = delayed ? "отстаёт" : waiting ? "ожидает" : quantity ? "в работе" : "норма";
                return `<div class="stage-row"><b>${escapeHtml(stage.stage)}</b><div class="progress ${delayed ? "" : "sage"}"><i style="--w:${percent}%"></i></div><span class="status-chip ${delayed ? "warn" : waiting ? "gray" : ""}">${status}</span></div>`;
              }).join("") : itemEmpty("Активных этапов пока нет.")}</div>
            </div>
            <div class="operations-panel">
              <div class="operations-panel-head"><b>Быстрые действия</b><span>управление</span></div>
              <div class="operations-actions">
                <button class="primary" data-operations-action="create-order">Создать заказ</button>
                <button data-go="orders">Перераспределить задачи</button>
                <button data-go="analytics">Открыть аналитику</button>
                <button data-go="admin" data-operations-action="employees">Назначить сотрудника</button>
                <button data-operations-action="scan">Сканировать QR</button>
                <button data-go="admin" data-operations-action="alerts">Оповещения</button>
              </div>
              <div class="operations-panel-head" style="margin-top:24px"><b>Оповещения</b><span>${alerts.length}</span></div>
              <div class="operations-alerts">${alerts.length ? alerts.slice(0, 5).map((alert) => `<div class="operations-alert ${alert.type === "overdue" || alert.type === "defect" ? "critical" : ""}" ${alert.batch_id ? `data-analytics-task-id="${escapeHtml(alert.batch_id)}"` : `data-go="analytics"`}><i></i><div><b>${escapeHtml(alert.title)}</b><span>${escapeHtml(alert.detail)}</span></div><span>›</span></div>`).join("") : itemEmpty("Критичных отклонений не найдено.")}</div>
            </div>
          </div>
          <div class="operations-panel">
            <div class="operations-panel-head"><b>Ключевые заказы</b><button type="button" class="small-button secondary" data-go="orders">Все заказы</button></div>
            <div class="key-orders">${keyOrders.length ? keyOrders.map((task) => `<div class="key-order" data-go="orders"><div><b>${escapeHtml(task.product_name || "Изделие")}: ${escapeHtml(task.operation || "Операция")}</b><span>${escapeHtml(task.product_size || "-")} · ${escapeHtml(task.product_color || "-")} · ${escapeHtml(task.quantity || 0)} шт${task.due_date ? ` · срок ${escapeHtml(task.due_date)}` : ""}</span></div><span class="status-chip ${task.work_state === "free" ? "gray" : task.work_state === "blocked" ? "warn" : ""}">${escapeHtml(task.status_text || "в работе")}</span></div>`).join("") : itemEmpty("Ключевых производственных заданий пока нет.")}</div>
          </div>
        </div>
      `;
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
        if (["marketplaces", "analytics"].includes(state.workspace)) render();
      }
    }

    async function refreshAnalyticsQuality({silent = false} = {}) {
      if (!canAccessMarketplaces() || state.analyticsQuality.loading) return;
      state.analyticsQuality.loading = true;
      state.analyticsQuality.error = "";
      if (!silent && state.workspace === "analytics") render();
      try {
        const quality = await api("/api/marketplaces/data-quality");
        if (!quality.ok) throw new Error(quality.message || "Не удалось загрузить качество данных.");
        state.analyticsQuality.payload = quality;
        state.analyticsQuality.loaded = true;
        // The full data-quality screen owns product pagination. Sharing only
        // the envelope lets the overview prefer PostgreSQL totals without
        // falsely marking that product page as loaded.
        state.marketplaceQuality.payload = quality;
      } catch (error) {
        state.analyticsQuality.error = error.apiMessage || error.message || "Не удалось загрузить качество данных.";
      } finally {
        state.analyticsQuality.loading = false;
        if (state.workspace === "analytics") render();
      }
    }

    function marketplaceLocalIsoDate(value = new Date()) {
      const parts = new Intl.DateTimeFormat("en-CA", {
        timeZone: "Asia/Yekaterinburg", year: "numeric", month: "2-digit", day: "2-digit",
      }).formatToParts(value);
      const byType = Object.fromEntries(parts.map((part) => [part.type, part.value]));
      return `${byType.year}-${byType.month}-${byType.day}`;
    }

    function analyticsOverviewRequest() {
      const period = marketplacePeriodMeta(state.marketplacePeriod);
      const payload = {start_date: period.startKey, end_date: period.endKey};
      return {payload, key: `${payload.start_date}|${payload.end_date}`};
    }

    async function refreshAnalyticsOverview({silent = false} = {}) {
      if (!canAccessMarketplaces() || state.analyticsOverview.loading) return;
      const request = analyticsOverviewRequest();
      state.analyticsOverview.loading = true;
      state.analyticsOverview.error = "";
      state.analyticsOverview.requestKey = request.key;
      if (!silent && state.workspace === "analytics") render();
      try {
        const overview = await api("/api/analytics/overview", request.payload);
        if (!overview.ok) throw new Error(overview.message || "Не удалось загрузить общую аналитику.");
        if (state.analyticsOverview.requestKey !== request.key) return;
        state.analyticsOverview.payload = overview;
        state.analyticsOverview.loaded = true;
      } catch (error) {
        if (state.analyticsOverview.requestKey !== request.key) return;
        state.analyticsOverview.payload = null;
        state.analyticsOverview.loaded = false;
        state.analyticsOverview.error = error.apiMessage || error.message || "Не удалось загрузить общую аналитику.";
      } finally {
        if (state.analyticsOverview.requestKey === request.key) {
          state.analyticsOverview.loading = false;
          if (state.workspace === "analytics") render();
        } else {
          state.analyticsOverview.loading = false;
          if (state.workspace === "analytics") {
            window.setTimeout(() => refreshAnalyticsOverview({silent: true}), 0);
          }
        }
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
        if (state.wmsData.loaded) await refreshWmsWorkspace({silent: true});
        state.marketplaceData.loaded = true;
      } catch (error) {
        state.marketplaceData.error = error.apiMessage || error.message || "Не удалось синхронизировать маркетплейс.";
        showToast("Ошибка", state.marketplaceData.error);
      } finally {
        state.marketplaceData.loading = false;
        render();
      }
    }

    async function refreshMarketplaceQuality({silent = false} = {}) {
      if (!canAccessMarketplaces() || state.marketplaceQuality.loading) return;
      state.marketplaceQuality.loading = true;
      state.marketplaceQuality.error = "";
      if (!silent) render();
      try {
        const page = Math.max(1, Number(state.marketplaceQuality.page || 1));
        const query = String(state.marketplaceQuality.query || "").trim().slice(0, 200);
        const [quality, products] = await Promise.all([
          api("/api/marketplaces/data-quality"),
          api("/api/marketplaces/products/page", {page, page_size: 20, query}),
        ]);
        if (!quality.ok) throw new Error(quality.message || "Не удалось загрузить качество данных.");
        if (!products.ok) throw new Error(products.message || "Не удалось загрузить каталог PostgreSQL.");
        state.marketplaceQuality.payload = quality;
        state.marketplaceQuality.products = products;
        state.marketplaceQuality.page = Number(products.page || page);
        state.marketplaceQuality.loaded = true;
      } catch (error) {
        state.marketplaceQuality.error = error.apiMessage || error.message || "Не удалось загрузить качество данных.";
      } finally {
        state.marketplaceQuality.loading = false;
        if (state.workspace === "marketplaces") render();
        const workerRunning = Boolean(state.marketplaceQuality.payload?.phase1a?.worker?.running);
        if (workerRunning && !state.marketplaceQuality.polling) {
          window.setTimeout(() => pollMarketplaceQualityWorker(), 0);
        }
      }
    }

    async function pollMarketplaceQualityWorker() {
      if (state.marketplaceQuality.polling) return;
      state.marketplaceQuality.polling = true;
      state.marketplaceQuality.syncing = true;
      render();
      try {
        for (let attempt = 0; attempt < 120; attempt += 1) {
          await new Promise((resolve) => window.setTimeout(resolve, 2500));
          await refreshMarketplaceQuality({silent: true});
          const worker = state.marketplaceQuality.payload?.phase1a?.worker || {};
          if (!worker.running) {
            const result = worker.last_result;
            if (result && typeof result.ok === "boolean") {
              showToast(
                result.ok ? "PostgreSQL Phase 1A" : "Phase 1A завершена с ошибкой",
                result.message || (result.ok ? "Синхронизация завершена." : "Проверьте экран качества данных."),
              );
            } else {
              showToast("PostgreSQL Phase 1A", "Внешняя синхронизация завершена. Состояние наборов обновлено.");
            }
            return;
          }
        }
        showToast("PostgreSQL Phase 1A", "Синхронизация ещё выполняется. Состояние можно обновить вручную.");
      } finally {
        state.marketplaceQuality.polling = false;
        state.marketplaceQuality.syncing = false;
        if (state.workspace === "marketplaces") render();
      }
    }

    async function syncMarketplacePhase1A() {
      const workerRunning = Boolean(state.marketplaceQuality.payload?.phase1a?.worker?.running);
      if (!canAccessMarketplaces() || state.marketplaceQuality.loading || state.marketplaceQuality.syncing || workerRunning) return;
      state.marketplaceQuality.syncing = true;
      state.marketplaceQuality.loading = true;
      state.marketplaceQuality.error = "";
      render();
      try {
        const result = await api("/api/marketplaces/phase1a/sync", {datasets: ["catalog", "prices", "stocks", "orders", "returns", "finance", "rating"]});
        if (!result.ok) throw new Error(result.message || "Phase 1A не запущена.");
        showToast("PostgreSQL Phase 1A", result.message || "Синхронизация запущена.");
      } catch (error) {
        state.marketplaceQuality.error = error.apiMessage || error.message || "Не удалось запустить Phase 1A.";
        showToast("Ошибка", state.marketplaceQuality.error);
      } finally {
        state.marketplaceQuality.loading = false;
        await refreshMarketplaceQuality({silent: true});
        const running = Boolean(state.marketplaceQuality.payload?.phase1a?.worker?.running);
        if (running) {
          window.setTimeout(() => pollMarketplaceQualityWorker(), 0);
        } else {
          state.marketplaceQuality.syncing = false;
          render();
        }
      }
    }

    function searchMarketplaceQualityProducts() {
      const input = document.getElementById("marketplaceQualitySearch");
      state.marketplaceQuality.query = String(input?.value || state.marketplaceQuality.query || "").trim().slice(0, 200);
      state.marketplaceQuality.page = 1;
      refreshMarketplaceQuality();
    }

    function changeMarketplaceQualityPage(delta) {
      const products = state.marketplaceQuality.products || {};
      const current = Math.max(1, Number(products.page || state.marketplaceQuality.page || 1));
      const pages = Math.max(0, Number(products.pages || 0));
      const next = Math.max(1, Math.min(pages || 1, current + Number(delta || 0)));
      if (next === current) return;
      state.marketplaceQuality.page = next;
      refreshMarketplaceQuality();
    }

    async function createMarketplaceShipment(supplyId) {
      if (!supplyId || state.marketplaceData.loading) return;
      state.marketplaceData.loading = true;
      render();
      try {
        const result = await api("/api/marketplaces/supply/create-shipment", {supply_id: Number(supplyId)});
        if (!result.ok) throw new Error(result.message || "Не удалось создать складскую отгрузку.");
        showToast("Отгрузка МП", result.created ? `Создан документ ${result.shipment.number}.` : "Документ уже существует.");
        const data = await api("/api/marketplaces/dashboard");
        state.marketplaceData.payload = data;
        if (state.wmsData.loaded) await refreshWmsWorkspace({silent: true});
      } catch (error) {
        showToast("Отгрузка МП", error.apiMessage || error.message || "Не удалось создать складскую отгрузку.");
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
            ...getAdminReportPayload(),
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
        renderOperationsCenter();
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
            ${packingOptions.length ? `<div class="field full"><label>Вариант упаковки</label><select id="taskPackagingOption">${packingOptions.map((option) => `<option value="${escapeHtml(option.id)}" ${draft.packaging_option === option.id ? "selected" : ""}>${escapeHtml(option.label)}</option>`).join("")}</select></div>` : ""}
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
        ? (selectedCuttingTask ? (selectedCuttingTask.stage === "formation" ? "Подтвердить готовый крой" : "Выполнить этап") : (selectedTask.can_complete ? "Выполнить задание" : "Продолжить задание"))
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
              <div class="button-row"><button class="small-button" data-report-action="complete-cutting-stage">${selectedCuttingTask.stage === "formation" ? "Подтвердить готовый крой" : "Выполнить этап"}</button></div>
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

    async function manageFabricStock(button) {
      if (!state.data || !state.data.is_admin) return;
      const action = button.dataset.fabricManage || "";
      const stockId = Number(button.dataset.fabricId || 0);
      const currentQuantity = Number(button.dataset.fabricQuantity || 0);
      const currentName = button.dataset.fabricName || "Ткань";
      const currentColor = button.dataset.fabricColor || "";
      const currentUnit = button.dataset.fabricUnit || "рул";
      const payload = {action, stock_id: stockId};

      if (action === "edit") {
        const materialName = window.prompt("Название материала", currentName);
        if (materialName === null) return;
        const productColor = window.prompt("Цвет материала", currentColor);
        if (productColor === null) return;
        const unit = window.prompt("Единица измерения", currentUnit);
        if (unit === null) return;
        payload.material_name = materialName.trim();
        payload.product_color = productColor.trim();
        payload.unit = unit.trim() || "рул";
      } else if (action === "writeoff") {
        const raw = window.prompt(`Сколько списать? Доступно: ${currentQuantity}`, String(currentQuantity));
        if (raw === null) return;
        const quantity = Number.parseInt(String(raw).trim(), 10);
        if (!Number.isInteger(quantity) || quantity <= 0 || quantity > currentQuantity) {
          showToast("Материалы", `Введите целое число от 1 до ${currentQuantity}.`);
          return;
        }
        payload.quantity = quantity;
      } else if (action === "delete") {
        if (currentQuantity > 0) {
          showToast("Материалы", "Сначала спишите остаток до нуля, затем удалите карточку.");
          return;
        }
        if (!window.confirm(`Удалить пустую карточку «${currentName} · ${currentColor}»?`)) return;
      } else {
        return;
      }

      const defaultReason = action === "edit" ? "Редактирование карточки" : action === "writeoff" ? "Списание материала" : "Удаление пустой карточки";
      const reason = window.prompt("Причина операции", defaultReason);
      if (reason === null || !reason.trim()) {
        showToast("Материалы", "Причина обязательна.");
        return;
      }
      payload.reason = reason.trim();
      const actionKey = `fabric-manage:${action}:${stockId}`;
      if (!beginAction(actionKey)) return;
      try {
        const data = await api("/api/production/manage-fabric-stock", payload);
        if (!data.ok) {
          showToast("Материалы", data.message || "Операция не выполнена.");
          return;
        }
        state.data.production = data.production || state.data.production;
        render();
        showToast("Материалы", data.message || "Готово.");
      } catch (error) {
        showToast("Ошибка", "Не удалось изменить материал.");
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

    function setWmsDraftProductKey(productKey) {
      const pk = productKey || {};
      state.wmsDraft.itemType = pk.item_type || "finished";
      state.wmsDraft.productName = pk.product_name || "";
      state.wmsDraft.productSize = pk.product_size || "";
      state.wmsDraft.productColor = pk.product_color || "";
      state.wmsDraft.stageName = pk.stage_name || "Готово";
      state.wmsDraft.readyForPosition = pk.ready_for_position || "Склад";
      state.wmsDraft.productScanned = Boolean(state.wmsDraft.productName);
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
      if (!d.toLocationScanned) {
        showToast("Склад", "Сначала отсканируйте ячейку размещения.");
        return;
      }
      if (!d.productScanned) {
        showToast("Склад", "Отсканируйте штрихкод товара.");
        return;
      }
      if (d.itemType !== "finished") {
        showToast("Склад", "Адресное размещение работает только для готовой продукции.");
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
          unit: "шт",
          request_key: requestKey,
          to_location_code: toLoc,
          reason: "Размещение готовой продукции (ТСД)",
          tsd_device_id: navigator.userAgent.slice(0, 40),
        });
        const ok = data.status === "ok" || data.status === "duplicate";
        showToast("Склад", ok ? `Размещено: ${qty} шт. → ${toLoc}` : (data.reason || "Ошибка размещения."));
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
      const stockRow = wmsResolvedStock(fromLoc, wmsProductKey(d));
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
      if (!d.productName || !d.productScanned || Number.isNaN(countedQty) || countedQty < 0) {
        showToast("ТСД", "Сначала отсканируйте товар, затем укажите фактическое количество.");
        return;
      }
      if (!locationCode || !d.fromLocationScanned) {
        showToast("ТСД", "Сначала отсканируйте ячейку пересчёта.");
        return;
      }
      const stockRow = wmsResolvedStock(locationCode, wmsProductKey(d));
      if (!stockRow) {
        showToast("ТСД", "Этого товара нет в отсканированной ячейке.");
        return;
      }
      const actionKey = `wms:inventory:${locationCode}:${d.productName}`;
      if (!beginAction(actionKey)) return;
      mainButton.disabled = true;
      try {
        const data = await api("/api/wms/inventory", {
          location_code: locationCode,
          counted: [{product_key: stockRow.product_key, counted_quantity: countedQty}],
          request_key: `wms:inventory:${createRequestId()}`,
        });
        const ok = data.status === "ok" || data.status === "duplicate";
        showToast("ТСД", ok ? `Пересчёт сохранён: ${countedQty} шт.` : (data.reason || "Ошибка пересчёта."));
        if (ok) {
          state.wmsDraft.quantity = "";
          state.wmsDraft.productName = "";
          state.wmsDraft.productSize = "";
          state.wmsDraft.productColor = "";
          state.wmsDraft.productScanned = false;
          render();
          refreshWmsWorkspace({silent: true});
        }
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

    async function wmsAdminAdjustmentSubmit() {
      const draft = syncWmsAdminAdjustmentFromForm();
      const location = wmsAdminSelectedLocation();
      const stock = wmsAdminSelectedStock();
      const quantity = Number(draft.quantity);
      const reason = String(draft.reason || "").trim();
      if (!location || !stock || Number(stock.location_id) !== Number(location.id)) {
        showToast("Склад", "Выберите ячейку и товар.");
        return;
      }
      if (!Number.isInteger(quantity) || quantity < (draft.mode === "inventory" ? 0 : 1)) {
        showToast("Склад", "Введите целое количество.");
        return;
      }
      if (!reason) {
        showToast("Склад", "Укажите причину для журнала.");
        return;
      }
      const reserved = Number(stock.reserved_quantity || 0);
      const available = Math.max(0, Number(stock.quantity || 0) - reserved);
      if (draft.mode === "inventory" && quantity < reserved) {
        showToast("Склад", `Фактический остаток не может быть меньше резерва ${reserved} шт.`);
        return;
      }
      if (draft.mode === "scrap" && quantity > available) {
        showToast("Склад", `Можно списать не больше ${available} шт.; резерв защищён.`);
        return;
      }
      const actionLabel = draft.mode === "inventory" ? `установить фактический остаток ${quantity} шт.` : `списать ${quantity} шт.`;
      if (!window.confirm(`Подтвердите: ${actionLabel}\n${wmsProductLabel(stock.product_key)}\n${location.code}`)) return;
      const actionKey = `wms:admin-adjustment:${draft.mode}:${stock.id}:${quantity}`;
      if (!beginAction(actionKey)) return;
      try {
        const payload = draft.mode === "inventory"
          ? {location_code: location.code, counted: [{product_key: stock.product_key, counted_quantity: quantity}], reason, request_key: `wms:admin-inventory:${createRequestId()}`}
          : {product_key: stock.product_key, quantity, from_location_code: location.code, target_state: draft.targetState || "SCRAPPED", reason, request_key: `wms:admin-scrap:${createRequestId()}`};
        const endpoint = draft.returnView === "cell"
          ? "/api/wms/scrap"
          : (draft.mode === "inventory" ? "/api/wms/admin/inventory" : "/api/wms/admin/scrap");
        const data = await api(endpoint, payload);
        const ok = data.status === "ok" || data.status === "duplicate";
        showToast("Склад", ok ? (draft.mode === "inventory" ? "Инвентаризация сохранена." : `Списано: ${quantity} шт.`) : (data.reason || data.message || "Операция не выполнена."));
        if (ok) {
          draft.quantity = "";
          draft.reason = "";
          if (draft.returnView === "cell") draft.returnView = "";
          render();
          refreshWmsWorkspace({silent: true});
        }
      } catch (error) {
        showToast("Ошибка", error.apiMessage || "Не удалось сохранить складскую операцию.");
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
              <div class="arbitrary-operation-head"><div><b>Произвольная операция</b></div><button type="button" class="small-button secondary" data-arbitrary-add>Добавить строку</button></div>
              ${arbitraryMarkup}
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

      const formationRows = (current.formation_rows || []).map((row) => {
        const rowKey = `${row.product_size}|${row.product_color}`;
        const rawDefect = (draft.formation_defects || {})[rowKey] ?? 0;
        const defect = Math.max(0, Math.min(Number(row.planned_quantity || 0), Number(rawDefect || 0)));
        const comment = (draft.formation_comments || {})[rowKey] || "";
        return `
          <div class="card cutting-formation-row" data-formation-row data-formation-size="${escapeHtml(row.product_size)}" data-formation-color="${escapeHtml(row.product_color)}" data-formation-total="${escapeHtml(row.planned_quantity)}">
            <div class="cutting-formation-meta"><b>Размер ${escapeHtml(row.product_size)} · ${escapeHtml(row.product_color)}</b><span>Раскроено: ${escapeHtml(row.planned_quantity)} шт.</span></div>
            <div class="cutting-formation-field"><label>Брак, шт.</label><input data-formation-defect type="number" inputmode="numeric" min="0" max="${escapeHtml(row.planned_quantity)}" step="1" value="${escapeHtml(rawDefect)}"></div>
            <div class="cutting-formation-field"><label>Годно, шт.</label><div class="cutting-formation-good" data-formation-good>${escapeHtml(Number(row.planned_quantity || 0) - defect)}</div></div>
            <div class="cutting-formation-field cutting-formation-comment"><label>Комментарий к браку</label><input data-formation-comment type="text" maxlength="300" placeholder="Причина брака" value="${escapeHtml(comment)}" ${defect > 0 ? "" : "disabled"}></div>
          </div>
        `;
      }).join("");

      return `
        <div class="card order-detail">
          <div class="order-head"><div class="op-icon">${sewingIcon()}</div><div><b>${escapeHtml(current.stage_title)}</b><span>${escapeHtml(current.product_name)}</span></div><span class="status-chip">4 этап</span></div>
          <div class="task-note"><b>Сверьте готовый крой</b><br>Укажите брак отдельно по каждому размеру и цвету. При браке комментарий обязателен.</div>
          <div class="op-list">${formationRows || itemEmpty("Нет строк готового кроя.")}</div>
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

      if (current.stage === "formation") {
        payload.formation_rows = [...document.querySelectorAll("[data-formation-row]")].map((row) => ({
          product_size: row.dataset.formationSize || "",
          product_color: row.dataset.formationColor || "",
          defect_quantity: row.querySelector("[data-formation-defect]")?.value || "0",
          defect_comment: row.querySelector("[data-formation-comment]")?.value || "",
        }));
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

      const quantity = requestTaskQuantity(current);
      if (quantity === null) return;

      const actionKey = `start-operation-task:${current.id}`;
      if (!beginAction(actionKey)) return;

      mainButton.disabled = true;

      try {
        const data = await api("/api/routes/start", {batch_id: current.id, quantity});

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
        shipment_cell: "Наведите камеру на штрихкод ячейки отгрузки",
        shipment_product: "Наведите камеру на штрихкод товара из ячейки",
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

    function normalizeWmsScannedBarcode(rawValue) {
      let value = String(rawValue || "").replace(/[\\u0000-\\u001f\\u007f]/g, "").trim();
      if (value.startsWith("]") && /^[A-Za-z][0-9]/.test(value.slice(1, 3))) value = value.slice(3).trim();
      return value;
    }

    async function handleWmsScan(rawValue) {
      const v = normalizeWmsScannedBarcode(rawValue);
      if (!v) return;
      clearWmsHardwareScannerInput();
      const field = state.wmsScanField || "product";
      if (field === "shipment_cell") {
        const location = wmsLocationByScan(v);
        const code = location ? String(location.code) : v.replace(/^LOC:/i, "").trim().toUpperCase();
        const task = state.wmsShipmentTaskDetail;
        const allowed = task ? task.items.flatMap((item) => item.allocations || []).some((allocation) => String(allocation.location_code || "").toUpperCase() === code) : false;
        if (!allowed) {
          showToast("Отгрузка", "Эта ячейка не входит в текущую отгрузку.");
          return;
        }
        state.wmsShipmentTaskLocation = code;
        state.wmsShipmentTaskExpectedAllocationId = "";
        render();
        showToast("Отгрузка", `Открыта ячейка ${code}.`);
        return;
      }
      if (field === "shipment_product") {
        const task = state.wmsShipmentTaskDetail;
        const expectedId = String(state.wmsShipmentTaskExpectedAllocationId || "");
        const allocation = task && task.items.flatMap((item) => (item.allocations || []).map((entry) => ({...entry, item}))).find((entry) => String(entry.id) === expectedId);
        if (!task || !allocation || !state.wmsShipmentTaskLocation) {
          showToast("Отгрузка", "Сначала откройте ячейку и выберите позицию.");
          return;
        }
        try {
          const data = await api("/api/wms/barcode/resolve", {barcode: v, location_code: state.wmsShipmentTaskLocation});
          const scannedKey = data.product_key || {};
          const expectedKey = JSON.parse(allocation.product_key_json || "{}");
          const sameProduct = ["item_type", "product_name", "product_size", "product_color", "stage_name", "ready_for_position"].every((key) => String(scannedKey[key] || "") === String(expectedKey[key] || ""));
          if (!sameProduct) {
            showToast("Отгрузка", "Этот товар не соответствует выбранной позиции отгрузки.");
            return;
          }
          state.wmsShipmentTaskScannedAllocationId = expectedId;
          state.wmsShipmentTaskExpectedAllocationId = "";
          render();
          showToast("Отгрузка", "Товар подтверждён. Укажите количество и выполните подбор.");
        } catch (error) {
          showToast("Отгрузка", error.apiMessage || "Штрихкод товара не зарегистрирован в этой ячейке.");
        }
        return;
      }
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
        state.wmsDraft.matchedStock = null;
        state.wmsDraft.matchedLocationCode = "";
        render();
        showToast("ТСД", `Ячейка: ${code}`);
      } else if (/^LPN:/i.test(v)) {
        showToast("ТСД", `Контейнер: ${v} (поддержка LPN — в разработке)`);
      } else {
        try {
          const locationCode = state.wmsView === "putaway" ? state.wmsDraft.toLocation : state.wmsDraft.fromLocation;
          const data = await api("/api/wms/barcode/resolve", {barcode: v, location_code: locationCode || ""});
          const pk = data.product_key || {};
          if (field === "lookup_product") {
            state.wmsLookup = {barcode: v, productKey: pk, error: ""};
            render();
            focusWmsHardwareScanner();
            showToast("ТСД", `Товар найден: ${wmsProductLabel(pk)}.`);
            return;
          }
          setWmsDraftProductKey(pk);
          const requiresStockInCell = ["pick", "inventory"].includes(state.wmsView);
          const stockRow = requiresStockInCell && locationCode ? (data.stock_row || wmsFindScannedStock(locationCode, pk)) : null;
          if (requiresStockInCell && locationCode && !stockRow) {
            state.wmsDraft.productName = "";
            state.wmsDraft.productSize = "";
            state.wmsDraft.productColor = "";
            state.wmsDraft.productScanned = false;
            state.wmsDraft.matchedStock = null;
            state.wmsDraft.matchedLocationCode = "";
            render();
            showToast("Склад", "Этого товара нет в отсканированной ячейке.");
          } else {
            if (stockRow) {
              setWmsDraftProductKey(stockRow.product_key);
              state.wmsDraft.matchedStock = stockRow;
              state.wmsDraft.matchedLocationCode = String(locationCode || "").replace(/^LOC:/i, "").trim().toUpperCase();
            }
            if (state.wmsView === "inventory") state.wmsDraft.quantity = "0";
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
        <div class="tabs order-mode-tabs" role="tablist" aria-label="Раздел заказов"><button type="button" class="tab" data-order-mode="board">Канбан</button><button type="button" class="tab" data-order-mode="list" role="tab" aria-selected="false">Список</button><button type="button" class="tab active" data-order-mode="create" role="tab" aria-selected="true">Создать задание</button></div>
        <div class="card field-card">
          <div class="form-grid">
            <div class="field full"><label>Изделия в одном настиле</label>${renderChoiceChips("product", catalog.map((item) => item.product_name), state.orderProducts)}</div>
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

    function renderOrdersBoard() {
      const seenTasks = new Set();
      const allTasks = [...currentOrderRows(), ...getCompletedOrderRows()].filter((task) => {
        const key = taskIdentity(task);
        if (seenTasks.has(key) || !orderTaskMatchesFilters(task)) return false;
        seenTasks.add(key);
        return true;
      });
      const filterRows = allTasks;
      const columns = [
        ["in_work", "В работе"],
        ["free", "Ожидают"],
        ["blocked", "Ожидают материалы / проблема"],
        ["done", "Завершённые"],
      ];
      const bucketFor = (task) => {
        if (task.work_state === "blocked" || task.work_state === "paused") return "blocked";
        return orderTaskStatusBucket(task);
      };
      mainButton.textContent = "Обновить заказы";
      mainButton.disabled = false;
      mount.innerHTML = `
        <div class="screen-head"><div><h2>Заказы</h2><p>Поток производственных заданий по этапам и статусам.</p></div><div class="date">${allTasks.length} заданий</div></div>
        <div class="tabs order-mode-tabs" role="tablist" aria-label="Представление заказов">
          <button type="button" class="tab active" data-order-mode="board">Канбан</button>
          <button type="button" class="tab" data-order-mode="list">Список</button>
          <button type="button" class="tab" data-order-mode="create">Создать заказ</button>
        </div>
        ${renderOrderFilters(filterRows)}
        <div class="orders-board">${columns.map(([id, label]) => {
          const rows = allTasks.filter((task) => bucketFor(task) === id);
          return `<section class="orders-column"><div class="orders-column-head"><b>${label}</b><span>${rows.length}</span></div>${rows.length ? rows.map((task) => {
            const title = task.task_kind === "route" ? task.operation : (task.stage_title || `Задание #${task.id}`);
            const product = task.product_name || task.product || "Изделие";
            const quantity = task.quantity || task.total_quantity || 0;
            return `<article class="board-order-card" data-board-order-key="${escapeHtml(taskIdentity(task))}"><b>${escapeHtml(title)}</b><span>${escapeHtml(product)}</span><div class="progress ${id === "blocked" ? "" : "sage"}"><i style="--w:${progressForTask(task)}%"></i></div><div class="board-order-meta"><span>${escapeHtml(quantity)} шт · ${escapeHtml(task.product_size || "-")}</span><span>${escapeHtml(priorityLabel(task.priority))}</span></div></article>`;
          }).join("") : `<div class="empty">Нет заданий</div>`}</section>`;
        }).join("")}</div>
      `;
    }

    function renderOrders() {
      if (state.data && state.data.is_admin && state.orderMode === "create") {
        renderOrderCreate();
        return;
      }

      if (state.data && state.data.is_admin && state.orderMode === "board") {
        renderOrdersBoard();
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
        ${state.data && state.data.is_admin ? `<div class="tabs order-mode-tabs" role="tablist" aria-label="Раздел заказов"><button type="button" class="tab" data-order-mode="board">Канбан</button><button type="button" class="tab ${state.orderMode === "list" ? "active" : ""}" data-order-mode="list" role="tab" aria-selected="${state.orderMode === "list" ? "true" : "false"}">Список</button><button type="button" class="tab ${state.orderMode === "create" ? "active" : ""}" data-order-mode="create" role="tab" aria-selected="${state.orderMode === "create" ? "true" : "false"}">Создать задание</button></div>` : ""}
        <div class="tabs admin-task-status-tabs" role="tablist" aria-label="Статус заданий">${["all", "free", "in_work", "done"].map((status) => `<button type="button" class="tab ${state.adminTaskStatus === status ? "active" : ""}" data-admin-task-status="${status}" role="tab" aria-selected="${state.adminTaskStatus === status ? "true" : "false"}">${adminTaskStatusLabel(status)}</button>`).join("")}</div>
        ${renderOrderFilters(filterRows)}
        <div class="op-list">
          ${allTasks.length ? `
          ${tasks.map((task, index) => {
            const filterValues = orderTaskFilterValues(task);
            const statusBucket = orderTaskStatusBucket(task);
            return `
            <div class="card order-card ${index === state.selectedOrder ? "selected" : ""}" data-select-order="${index}">
              <div class="order-head"><div class="op-icon">${uiIcon("work")}</div><div><b>${task.task_kind === "cutting_stage" ? escapeHtml(task.stage_title) : `Задание #${escapeHtml(task.id)}`}</b><span>${escapeHtml(filterValues.product || "Изделие не указано")}<br><strong>Этап: ${escapeHtml(task.stage_title || task.process_status_text || "Раскрой")}</strong>${task.assigned_employee_name ? `<br>В работе: ${escapeHtml(task.assigned_employee_name)}` : ""}</span></div><span class="status-chip ${statusBucket === "free" ? "gray" : (statusBucket === "done" ? "" : "warn")}">${escapeHtml(orderTaskStatusText(task))}</span></div>
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
          <div class="card order-detail"><div class="order-head"><div class="op-icon">${sewingIcon()}</div><div><b>Задание #${escapeHtml(current.id)}</b><span>${escapeHtml(current.product_name)}<br><strong>Этап: ${escapeHtml(current.stage_title || current.process_status_text || "Раскрой")}</strong></span></div><span class="status-chip">${escapeHtml(orderTaskStatusText(current))}</span></div><div class="detail-grid"><div class="detail-box"><span>Этап</span><strong>${escapeHtml(current.stage_title || current.process_status_text || "Раскрой")}</strong></div><div class="detail-box"><span>Размеры</span><strong>${escapeHtml((current.sizes || []).join(", ") || "-")}</strong></div><div class="detail-box"><span>Цвета</span><strong>${escapeHtml((current.color_labels || current.colors || []).join(", ") || "-")}</strong></div><div class="detail-box"><span>Приоритет</span><strong>${escapeHtml(priorityLabel(current.priority))}</strong></div><div class="detail-box"><span>Срок</span><strong>${escapeHtml(current.due_date || "Не задан")}</strong></div><div class="detail-box"><span>Статус</span><strong>${escapeHtml(orderTaskStatusText(current))}</strong></div><div class="detail-box"><span>Создано</span><strong>${escapeHtml((current.created_at || "").slice(0, 10) || "-")}</strong></div></div></div>
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
        <div class="screen-head"><div><h2>Аналитика производства</h2><p>План, качество, загрузка и риски по текущему периоду.</p></div><div class="date">${escapeHtml(control.start_date === control.end_date ? control.start_date || "" : `${control.start_date || ""} — ${control.end_date || ""}`)}</div></div>
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
        ["integrations", "Интеграции"],
      ];

      return `<div class="segment-row">${sections.map(([id, label]) => `
        <button class="segment-button ${state.adminSection === id ? "active" : ""}" data-admin-section="${id}">${label}</button>
      `).join("")}</div>`;
    }

    function renderAdminIntegrations() {
      const root = state.marketplaceData && state.marketplaceData.payload && typeof state.marketplaceData.payload === "object" ? state.marketplaceData.payload : {};
      const runs = [
        ...(Array.isArray(root.sync_runs) ? root.sync_runs.map((row) => ({...row, marketplace: row.marketplace || "ozon"})) : []),
        ...(root.wildberries && Array.isArray(root.wildberries.sync_runs) ? root.wildberries.sync_runs.map((row) => ({...row, marketplace: row.marketplace || "wildberries"})) : []),
      ].sort((a, b) => String(b.finished_at || b.started_at || "").localeCompare(String(a.finished_at || a.started_at || "")));
      const events = [
        ...(Array.isArray(root.sync_events) ? root.sync_events : []),
        ...(root.wildberries && Array.isArray(root.wildberries.sync_events) ? root.wildberries.sync_events : []),
      ];
      const rows = runs.slice(0, 40).map((row) => `<tr><td>${escapeHtml(row.marketplace || "—")}</td><td>${escapeHtml(row.started_at || "—")}</td><td>${escapeHtml(row.finished_at || "—")}</td><td>${escapeHtml(row.status || "unknown")}</td><td>${escapeHtml(row.error_message || row.message || "—")}</td></tr>`).join("");
      const eventRows = events.slice(0, 20).map((row) => `<div class="report-row"><div><b>${escapeHtml(row.code || row.event_type || "event")}</b><span>${escapeHtml(row.message || row.detail || "—")}</span></div><span class="status-chip gray">${escapeHtml(row.created_at || row.timestamp || "—")}</span></div>`).join("");
      mainButton.hidden = true;
      return `<div class="screen-head"><div><h2>Интеграции · Диагностика</h2><p>Технические статусы API и журнал синхронизации. Этот экран доступен только администратору.</p></div><div class="date">${runs.length} запусков</div></div>${renderAdminTabs()}<div class="card field-card"><div class="button-row"><button class="small-button" data-ac-action="sync">Синхронизировать площадки</button><button class="small-button secondary" data-ac-action="refresh">Обновить аналитику</button></div></div><div class="card field-card"><div class="section-title"><b>Журнал синхронизации</b><span>Технические статусы</span></div>${rows ? `<div class="ac-table-wrap"><table class="ac-table"><thead><tr><th>Площадка</th><th>Начало</th><th>Завершение</th><th>Статус</th><th>Ошибка / сообщение</th></tr></thead><tbody>${rows}</tbody></table></div>` : itemEmpty("Запусков синхронизации пока нет.")}</div><div class="card field-card"><div class="section-title"><b>События интеграций</b><span>${events.length}</span></div>${eventRows || itemEmpty("Технических событий нет.")}</div>`;
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
      const fabricRows = getProduction().fabric_stock || [];
      const warehouseRows = getWarehouseStock().filter((row) => Number(row.quantity || 0) > 0);
      const receiptColors = getOrderColors().filter((color) => color !== "Капучино");
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
        <div class="card report-row"><div><b>${escapeHtml(row.material_name)}</b><span>${escapeHtml(row.product_color_label || row.product_color)}</span></div><div><span class="status-chip">${escapeHtml(row.quantity_text)} ${escapeHtml(row.unit === "рул" ? "рул." : row.unit)}</span><div class="button-row compact"><button type="button" class="small-button secondary" data-fabric-manage="edit" data-fabric-id="${escapeHtml(row.id)}" data-fabric-name="${escapeHtml(row.material_name)}" data-fabric-color="${escapeHtml(row.product_color)}" data-fabric-unit="${escapeHtml(row.unit)}" data-fabric-quantity="${escapeHtml(row.quantity)}">Редактировать</button><button type="button" class="small-button secondary" data-fabric-manage="writeoff" data-fabric-id="${escapeHtml(row.id)}" data-fabric-name="${escapeHtml(row.material_name)}" data-fabric-color="${escapeHtml(row.product_color)}" data-fabric-unit="${escapeHtml(row.unit)}" data-fabric-quantity="${escapeHtml(row.quantity)}">Списать</button><button type="button" class="small-button danger" data-fabric-manage="delete" data-fabric-id="${escapeHtml(row.id)}" data-fabric-name="${escapeHtml(row.material_name)}" data-fabric-color="${escapeHtml(row.product_color)}" data-fabric-unit="${escapeHtml(row.unit)}" data-fabric-quantity="${escapeHtml(row.quantity)}">Удалить</button></div></div></div>
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
      return wmsStockAtLocation("RECEIVE-01").filter((row) => row.product_key && row.product_key.item_type === "finished");
    }

    function wmsReceivingMaterials() {
      return wmsReceivingStock().filter((row) => row.product_key && row.product_key.item_type === "material");
    }

    function wmsProductKeysEqual(first, second) {
      const normalize = (value) => String(value || "")
        .normalize("NFKC")
        .trim()
        .replace(/\\s+/g, " ")
        .replace(/ё/g, "е")
        .toLocaleLowerCase("ru");
      const identityKeys = ["item_type", "product_name", "product_size", "product_color"];
      return identityKeys.every((key) => normalize((first || {})[key]) === normalize((second || {})[key]));
    }

    function wmsFindScannedStock(locationCode, productKey) {
      return wmsStockAtLocation(locationCode).find((row) => wmsProductKeysEqual(row.product_key, productKey)) || null;
    }

    function wmsResolvedStock(locationCode, productKey) {
      const normalizedLocation = String(locationCode || "").replace(/^LOC:/i, "").trim().toUpperCase();
      const matched = state.wmsDraft.matchedStock;
      if (
        matched
        && normalizedLocation
        && normalizedLocation === String(state.wmsDraft.matchedLocationCode || "").toUpperCase()
        && wmsProductKeysEqual(matched.product_key, productKey)
      ) return matched;
      return wmsFindScannedStock(locationCode, productKey);
    }

    function renderWmsGuidedScanner(locationField, locationCode, productDetected, locationLabel) {
      const locationWasScanned = locationField === "from_location" ? state.wmsDraft.fromLocationScanned : state.wmsDraft.toLocationScanned;
      const locationReady = Boolean(locationWasScanned && locationCode && wmsLocationByCode(locationCode));
      const expectedField = locationReady ? "product" : locationField;
      const expectedText = locationReady ? "Отсканируйте товар" : `Отсканируйте ${locationLabel.toLowerCase()}`;
      return `
        <div class="card field-card wms-guided-scanner">
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
          return renderWmsStockProductRow(row, available);
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

    function renderWmsStockProductRow(row, available = null, allowWriteoff = false) {
      const product = row.marketplace_product || null;
      const free = available == null ? Math.max(0, Number(row.quantity || 0) - Number(row.reserved_quantity || 0)) : available;
      const identity = product
        ? `<div class="wms-product-rich">${marketplaceProductAvatar(product, false, true)}<div class="wms-product-rich-copy"><b>${escapeHtml(product.group_name || product.name || "Товар Ozon")}</b><span>Артикул: ${escapeHtml(product.offer_id || "—")} · SKU: ${escapeHtml(product.sku || "—")}</span><small>Размер ${escapeHtml(product.size || row.product_key?.product_size || "—")} · цвет ${escapeHtml(product.color || row.product_key?.product_color || "—")}</small></div></div>`
        : `<div><b>${escapeHtml(wmsProductLabel(row.product_key))}</b><span>Складская номенклатура</span></div>`;
      return `<div class="card report-row wms-stock-product-row">${identity}<div class="wms-stock-product-balance"><span class="status-chip">${escapeHtml(row.quantity)} ${escapeHtml(row.unit || "шт")}</span><small>Доступно ${escapeHtml(free)} · резерв ${escapeHtml(row.reserved_quantity || 0)}</small>${allowWriteoff ? `<button type="button" class="small-button secondary" data-wms-cell-writeoff="${escapeHtml(row.id)}" ${free > 0 ? "" : "disabled"}>Списать</button>` : ""}</div></div>`;
    }

    function wmsAdminSelectedLocation() {
      return (state.wmsData.locations || []).find((row) => Number(row.id) === Number(state.wmsAdminAdjustment.locationId || 0)) || null;
    }

    function wmsAdminStockRows(locationId = state.wmsAdminAdjustment.locationId) {
      return (state.wmsData.stock || []).filter((row) => Number(row.location_id) === Number(locationId || 0) && row.item_state === "SELLABLE" && Number(row.quantity || 0) > 0);
    }

    function wmsAdminSelectedStock() {
      return (state.wmsData.stock || []).find((row) => Number(row.id) === Number(state.wmsAdminAdjustment.stockId || 0)) || null;
    }

    function syncWmsAdminAdjustmentFromForm() {
      const draft = state.wmsAdminAdjustment;
      const location = document.getElementById("wmsAdminLocation");
      const stock = document.getElementById("wmsAdminStock");
      const quantity = document.getElementById("wmsAdminQuantity");
      const reason = document.getElementById("wmsAdminReason");
      const targetState = document.getElementById("wmsAdminTargetState");
      if (location) draft.locationId = location.value;
      if (stock) draft.stockId = stock.value;
      if (quantity) draft.quantity = quantity.value;
      if (reason) draft.reason = reason.value;
      if (targetState) draft.targetState = targetState.value;
      return draft;
    }

    function renderWmsAdminAdjustmentForm(cellMode = false) {
      const draft = state.wmsAdminAdjustment;
      const location = wmsAdminSelectedLocation();
      const rows = wmsAdminStockRows();
      const stock = wmsAdminSelectedStock();
      const available = stock ? Math.max(0, Number(stock.quantity || 0) - Number(stock.reserved_quantity || 0)) : 0;
      const locationOptions = (state.wmsData.locations || []).filter((row) => wmsAdminStockRows(row.id).length).map((row) => `<option value="${escapeHtml(row.id)}" ${Number(row.id) === Number(draft.locationId) ? "selected" : ""}>${escapeHtml(wmsLocationDisplayName(row))}</option>`).join("");
      const stockOptions = rows.map((row) => `<option value="${escapeHtml(row.id)}" ${Number(row.id) === Number(draft.stockId) ? "selected" : ""}>${escapeHtml(wmsProductLabel(row.product_key))} · ${escapeHtml(row.quantity)} шт.</option>`).join("");
      return `<div class="card field-card">
        ${cellMode ? `<div class="section-title"><b>Списать из ячейки</b><span>частично</span></div>` : ""}
        <div class="form-grid">
          ${cellMode ? `<div class="field full"><label>Ячейка</label><input value="${escapeHtml(location ? wmsLocationDisplayName(location) : "—")}" readonly></div>` : `<div class="field full"><label>Ячейка без сканирования</label><select id="wmsAdminLocation" data-wms-admin-field="location"><option value="">Выберите ячейку</option>${locationOptions}</select></div>`}
          <div class="field full"><label>Товар</label><select id="wmsAdminStock" data-wms-admin-field="stock"><option value="">Выберите товар</option>${stockOptions}</select></div>
          ${stock ? `<div class="field"><label>В системе</label><input value="${escapeHtml(stock.quantity)} шт." readonly></div><div class="field"><label>Резерв / доступно</label><input value="${escapeHtml(stock.reserved_quantity || 0)} / ${escapeHtml(available)} шт." readonly></div>` : ""}
          ${stock ? `<div class="field"><label>${draft.mode === "inventory" ? "Фактическое количество" : "Количество к списанию"}</label><input id="wmsAdminQuantity" type="number" inputmode="numeric" min="${draft.mode === "inventory" ? escapeHtml(stock.reserved_quantity || 0) : "1"}" max="${draft.mode === "inventory" ? "" : escapeHtml(available)}" step="1" value="${escapeHtml(draft.quantity || "")}" placeholder="0"></div>` : ""}
          ${stock && draft.mode === "scrap" ? `<div class="field"><label>Результат</label><select id="wmsAdminTargetState"><option value="SCRAPPED" ${draft.targetState === "SCRAPPED" ? "selected" : ""}>Списано</option><option value="DAMAGED" ${draft.targetState === "DAMAGED" ? "selected" : ""}>Брак</option><option value="QUARANTINE" ${draft.targetState === "QUARANTINE" ? "selected" : ""}>Карантин</option></select></div>` : ""}
          ${stock ? `<div class="field full"><label>Причина</label><textarea id="wmsAdminReason" rows="3" placeholder="Обязательная причина для журнала">${escapeHtml(draft.reason || "")}</textarea></div>` : ""}
        </div>
        <div class="button-row"><button type="button" class="small-button secondary" data-wms-admin-action="cancel">Отмена</button>${stock ? `<button type="button" class="small-button" data-wms-admin-action="submit">${draft.mode === "inventory" ? "Сохранить пересчёт" : "Списать"}</button>` : ""}</div>
      </div>`;
    }

    function wmsMovementLabel(type) {
      return ({
        receive: "Приёмка",
        production_receipt: "Приёмка",
        material_receipt: "Приёмка материалов",
        putaway: "Размещение",
        putaway_direct: "Размещение",
        transfer: "Перемещение",
        pick: "Выдача из ячейки",
        ship: "Отгрузка",
        inventory: "Инвентаризация",
        count: "Инвентаризация",
        inventory_adjustment: "Корректировка",
        scrap: "Списание",
        test_receipt: "Тестовая приёмка",
        test_putaway: "Тестовое размещение",
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
          <button type="button" class="card summary-card clickable" data-wms-view="shipments"><span>Отгрузки</span><strong>↑</strong><small>Созданные отправки</small></button>
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
          ${state.data && state.data.is_admin ? `<button type="button" class="card summary-card clickable" data-wms-view="admin-stock-control"><span>Инвентаризация / списание</span><strong>✎</strong><small>Без сканирования штрихкода</small></button>` : `<button type="button" class="card summary-card clickable" data-wms-view="scrap"><span>Списание</span><strong>×</strong><small>Брак и карантин</small></button>`}
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
        </div>
        ${lookup.error ? `<div class="card field-card"><div class="task-note"><b>Товар не найден</b><br>${escapeHtml(lookup.error)}</div></div>` : ""}
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
        <div class="button-row"><button type="button" class="small-button" data-wms-cell-action="putaway" data-wms-cell-code="${escapeHtml(location.code)}">Разместить сюда</button><button type="button" class="small-button secondary" data-wms-cell-action="pick" data-wms-cell-code="${escapeHtml(location.code)}">Выдать из ячейки</button>${summary.available > 0 ? `<button type="button" class="small-button secondary" data-wms-cell-writeoff="">Списать</button>` : ""}</div>
        ${state.wmsAdminAdjustment.returnView === "cell" && Number(state.wmsAdminAdjustment.locationId) === Number(location.id) ? renderWmsAdminAdjustmentForm(true) : ""}
        <div class="section-title"><b>Содержимое</b><span>${summary.rows.length} поз.</span></div>
        <div class="wms-location-products">${summary.rows.length ? summary.rows.map((row) => renderWmsStockProductRow(row, null, true)).join("") : itemEmpty("Ячейка свободна.")}</div>
        <div class="section-title"><b>История ячейки</b><span>${movements.length}</span></div>
        <div class="wms-location-products">${movements.length ? movements.map((movement) => `<div class="report-row"><div><b>${escapeHtml(wmsMovementLabel(movement.movement_type))}</b><span>${escapeHtml(wmsProductLabel(movement.product_key))}<br>${escapeHtml(wmsMovementTime(movement.occurred_at))}</span></div><span class="status-chip gray">${escapeHtml(movement.quantity)} шт.</span></div>`).join("") : itemEmpty("Движений по ячейке пока нет.")}</div>
      </div>`;
    }

    function renderWmsWarehouseMap() {
      const stockRows = arguments.length ? arguments[0] : wmsFilteredStock();
      if (!wmsHasAddressMapForCurrentStock()) {
        state.wmsSelectedLocationId = "";
        const definition = wmsCurrentStockFilter();
        return `<div class="card field-card">${itemEmpty(`Адресные ячейки для раздела «${escapeHtml(definition.label)}» не настроены.`)}</div>`;
      }
      const locations = (state.wmsData.locations || []).map((location) => ({location, parts: wmsPhysicalLocationParts(location)})).filter((row) => row.parts);
      if (!locations.length) return `<div class="card field-card">${itemEmpty("Физические ячейки ещё не загружены.")}</div>`;
      const zones = [...new Set(locations.map((row) => row.parts.zone))].sort((a, b) => a - b);
      return `<div class="wms-map-shell">
        <div class="section-title"><b>Карта адресного хранения</b><span>${locations.length} яч.</span></div>
        <div class="wms-map-legend"><span><i></i> свободна</span><span class="occupied"><i></i> занята</span><span class="reserved"><i></i> есть резерв</span><span class="blocked"><i></i> заблокирована</span></div>
        ${state.wmsSelectedLocationId ? `<div id="wms-location-detail" tabindex="-1">${renderWmsLocationDetail(stockRows)}</div>` : ""}
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
          return `<section class="wms-zone-map"><div class="wms-zone-map-head"><b>Зона №${zone}</b><span>${zoneRows.length} ячеек · ${zoneQuantity} ${escapeHtml(wmsCurrentStockFilter().unit)}</span></div><div class="wms-map-grid" style="--wms-columns:${maxSection * maxPosition};grid-template-columns:repeat(${maxSection * maxPosition},minmax(62px,1fr));grid-template-rows:repeat(${maxLevel},minmax(64px,auto))">${cells.join("")}</div></section>`;
        }).join("")}</div>
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
          <div class="card report-row wms-catalog-product"><div><b>${escapeHtml(selectedGroup.name)}</b><span>Размер: ${escapeHtml(product.size || "—")}<br>Артикул: ${escapeHtml(product.offer_id || "—")}<br>${product.route_configured ? `Производство: ${escapeHtml(product.production_product_name)} · ${escapeHtml(product.production_size)} · ${escapeHtml(product.production_color)}` : `Единая карточка: ${escapeHtml(product.production_product_name)} · маршрут производства пока не настроен`}</span></div><div><span class="status-chip ${product.route_configured ? "" : "gray"}">${product.route_configured ? "маршрут связан" : "каталог связан"}</span><span class="status-chip gray">Штрихкод: ${escapeHtml(product.barcode || "—")}</span><small>SKU: ${escapeHtml(product.sku || "—")}</small></div></div>`).join("")}</div></section>`;
      }).join("") : "";
      mount.innerHTML = `
        <div class="screen-head"><div><h2>${selectedGroup ? escapeHtml(selectedGroup.name) : "Товары Ozon"}</h2><p>${selectedGroup ? "Варианты сгруппированы по цвету, затем по размеру." : "Выберите изделие, затем увидите его цвета и размеры."}</p></div><div class="date">${catalog.loaded ? `${products.length} из ${(catalog.products || []).length}` : "загрузка"}</div></div>
        <div class="card field-card"><div class="warehouse-v2-filter-row"><div class="field"><label>Поиск по артикулу, названию, цвету, размеру или штрихкоду</label><input id="wmsCatalogSearch" value="${escapeHtml(state.wmsCatalogSearch || "")}" placeholder="Например 1073896068 или Чёрный"></div><button type="button" class="small-button" data-wms-catalog-action="apply">Показать</button></div></div>
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
        <div class="screen-head"><div><h2>${definition.itemType === "finished" ? "Адресные остатки" : `Остатки: ${escapeHtml(definition.label)}`}</h2><p>${definition.itemType === "finished" ? "Готовая продукция по адресным ячейкам." : "Остатки без адресного размещения."}</p></div><div class="date">${stock.length} поз.</div></div>
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
        ${wmsHasAddressMapForCurrentStock() ? renderWmsWarehouseMap(stock) : ""}
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

    function renderWmsShipments() {
      const shipments = new Map();
      (state.wmsData.movements || []).filter((movement) => movement.movement_type === "ship" || movement.source_type === "shipment").forEach((movement) => {
        const reference = String(movement.reason || "Отгрузка без номера");
        const number = (reference.match(/(?:ТЕСТОВАЯ )?ОТГРУЗКА\\s+([A-Z0-9-]+)/i) || [])[1] || "Без номера";
        const item = shipments.get(reference) || {number, reference, rows: [], total: 0, locations: new Set(), occurredAt: movement.occurred_at};
        item.rows.push(movement);
        item.total += Number(movement.quantity || 0);
        if (movement.from_location_id) item.locations.add(wmsLocationLabel(movement.from_location_id));
        if (String(movement.occurred_at || "") > String(item.occurredAt || "")) item.occurredAt = movement.occurred_at;
        shipments.set(reference, item);
      });
      const rows = [...shipments.values()].sort((first, second) => String(second.occurredAt || "").localeCompare(String(first.occurredAt || "")));
      const allTasks = state.wmsData.shipmentTasks || [];
      const taskStatusLabels = {WAITING_RESERVATION:"Требует подготовки",SHORTAGE:"Не хватает товара",READY_TO_PICK:"В работе",PICKING:"Собирается",PICKED:"Собрана",PACKING:"Упаковка",READY_TO_HANDOVER:"Готова к отгрузке",SHIPPED:"Отгружено",HANDED_OVER:"Передана",ACCEPTED:"Принята"};
      const taskBuckets = {
        required: allTasks.filter((task) => ["WAITING_RESERVATION", "SHORTAGE"].includes(task.status)),
        progress: allTasks.filter((task) => ["READY_TO_PICK", "PICKING", "PICKED", "PACKING", "READY_TO_HANDOVER"].includes(task.status)),
        shipped: allTasks.filter((task) => ["SHIPPED", "HANDED_OVER", "ACCEPTED"].includes(task.status)),
      };
      const activeTaskTab = taskBuckets[state.wmsShipmentTaskTab] ? state.wmsShipmentTaskTab : "required";
      const pendingTasks = taskBuckets[activeTaskTab];
      const taskTabLabels = {required:"Требуют отгрузки",progress:"В работе",shipped:"Отгружено"};
      const pendingTasksBlock = `<div class="button-row">${Object.entries(taskTabLabels).map(([key,label]) => `<button type="button" class="small-button ${key === activeTaskTab ? "" : "secondary"}" data-wms-task-tab="${key}">${label} · ${taskBuckets[key].length}</button>`).join("")}</div><div class="section-title"><b>${taskTabLabels[activeTaskTab]}</b><span>${escapeHtml(pendingTasks.length)}</span></div><div class="op-list">${pendingTasks.length ? pendingTasks.map((task) => `<button type="button" class="card field-card marketplace-clickable" data-wms-shipment-task-number="${escapeHtml(task.number)}"><div class="section-title"><b>${escapeHtml(task.number)}</b><span class="status-chip ${task.status === "SHORTAGE" ? "warn" : ""}">${escapeHtml(taskStatusLabels[task.status] || task.status)}</span></div><div class="detail-grid"><div class="detail-box"><span>Маркетплейс</span><strong>${escapeHtml(task.marketplace === "wildberries" ? "Wildberries" : "Ozon")}</strong></div><div class="detail-box"><span>Поставка</span><strong>${escapeHtml(task.external_supply_id || "—")}</strong></div><div class="detail-box"><span>Позиций</span><strong>${escapeHtml(task.item_count || 0)}</strong></div><div class="detail-box"><span>Собрано</span><strong>${escapeHtml(task.picked_quantity || 0)} / ${escapeHtml(task.total_quantity || 0)} шт.</strong></div></div><div class="task-note">${escapeHtml(task.destination_name || "Направление не указано")} · открыть ›</div></button>`).join("") : itemEmpty(activeTaskTab === "shipped" ? "Подтверждённых отгрузок пока нет." : "Заданий в этом разделе нет.")}</div>`;
      const detail = state.wmsShipmentDetail || null;
      const taskDetail = state.wmsShipmentTaskDetail || null;
      const selectedTaskLocation = String(state.wmsShipmentTaskLocation || "").trim().toUpperCase();
      const taskAllocations = taskDetail ? taskDetail.items.flatMap((item) => (item.allocations || []).map((allocation) => ({...allocation, item}))) : [];
      const taskCells = [...new Set(taskAllocations.map((allocation) => allocation.location_code))];
      const selectedTaskAllocations = taskAllocations.filter((allocation) => !selectedTaskLocation || String(allocation.location_code).toUpperCase() === selectedTaskLocation);
      const taskScannerIsProduct = Boolean(state.wmsShipmentTaskExpectedAllocationId);
      const taskScannerField = taskScannerIsProduct ? "shipment_product" : "shipment_cell";
      const taskScannerLabel = taskScannerIsProduct ? "Отсканируйте товар из выбранной ячейки" : "Отсканируйте ячейку";
      const taskRequiredLines = taskDetail ? `<div class="section-title"><b>Состав отгрузки и ячейки</b><span>${escapeHtml(taskDetail.items.length)} поз.</span></div><div class="op-list">${taskDetail.items.map((item) => { const allocations = item.allocations || []; const cells = allocations.length ? allocations.map((allocation) => `${allocation.location_code} · ${allocation.reserved_quantity || 0} шт.`).join(", ") : "Не найдено ни в одной ячейке"; return `<div class="card report-row"><div><b>${escapeHtml(item.article || item.product_key || "Артикул не указан")} · ${escapeHtml(item.name || "Товар")}</b><span>Размер ${escapeHtml(item.size || "—")} · Цвет ${escapeHtml(item.color || "—")}<br><b>Ячейки:</b> ${escapeHtml(cells)}</span></div><span class="status-chip ${allocations.length ? "" : "warn"}">${escapeHtml(item.quantity || 0)} шт.</span></div>`; }).join("")}</div>` : "";
      const taskDetailBlock = taskDetail ? `<div class="button-row"><button type="button" class="small-button secondary" data-wms-task-action="back">‹ Все задания</button>${taskDetail.can_start ? `<button type="button" class="small-button" data-wms-task-action="start">Подготовить ячейки</button>` : ""}${taskDetail.can_confirm ? `<button type="button" class="small-button" data-wms-task-action="confirm">Подтвердить отгрузку</button>` : ""}</div><div class="card field-card"><div class="section-title"><b>${escapeHtml(taskDetail.number)}</b><span class="status-chip ${taskDetail.status === "SHORTAGE" ? "warn" : ""}">${escapeHtml(taskStatusLabels[taskDetail.status] || taskDetail.status)}</span></div><div class="detail-grid"><div class="detail-box"><span>Маркетплейс</span><strong>${escapeHtml(taskDetail.marketplace === "wildberries" ? "Wildberries" : "Ozon")}</strong></div><div class="detail-box"><span>Поставка</span><strong>${escapeHtml(taskDetail.external_supply_id || "—")}</strong></div><div class="detail-box"><span>Собрано</span><strong>${escapeHtml(taskDetail.picked_quantity || 0)} / ${escapeHtml(taskDetail.total_quantity || 0)} шт.</strong></div><div class="detail-box"><span>Ячеек</span><strong>${escapeHtml(taskCells.length)}</strong></div></div><div class="task-note">${escapeHtml(taskDetail.destination_name || "Направление не указано")}</div></div>${taskRequiredLines}${taskDetail.can_start ? `<div class="card field-card"><b>Подготовьте задание</b><p>Система проверит остатки и закрепит за этой поставкой конкретные ячейки. После этого сотрудник сможет сканировать ячейки и товары.</p></div>` : taskCells.length ? `<div class="card field-card"><div class="field full"><label>${taskScannerLabel}</label><div class="wms-shipment-picker"><input id="wmsShipmentTaskCell" class="wms-hardware-scanner-input" data-wms-hardware-field="${taskScannerField}" inputmode="none" autocomplete="off" placeholder="${taskScannerIsProduct ? "Штрихкод товара" : "Например, Z1-S1-P1-1"}" value="${taskScannerIsProduct ? "" : escapeHtml(selectedTaskLocation)}"><button type="button" class="small-button secondary" data-wms-task-action="select-cell">${taskScannerIsProduct ? "Сканируйте ТСД" : "Открыть ячейку"}</button></div></div><div class="button-row">${taskCells.map((code) => `<button type="button" class="small-button ${String(code).toUpperCase() === selectedTaskLocation ? "" : "secondary"}" data-wms-task-location="${escapeHtml(code)}">${escapeHtml(code)}</button>`).join("")}</div></div><div class="section-title"><b>${selectedTaskLocation ? `Ячейка ${escapeHtml(selectedTaskLocation)}` : "Позиции и ячейки"}</b><span>${escapeHtml(selectedTaskAllocations.length)}</span></div><div class="op-list">${selectedTaskAllocations.map((allocation) => { const remaining = Math.max(0, Number(allocation.reserved_quantity || 0) - Number(allocation.picked_quantity || 0)); const complete = remaining === 0; const scanned = String(state.wmsShipmentTaskScannedAllocationId) === String(allocation.id); return `<div class="card report-row"><div><b>${escapeHtml(allocation.item.article || allocation.item.product_key || "Артикул не указан")} · ${escapeHtml(allocation.item.name || "Товар")}</b><span>Размер ${escapeHtml(allocation.item.size || "—")} · Цвет ${escapeHtml(allocation.item.color || "—")}<br>Ячейка: ${escapeHtml(allocation.location_code)} · ${complete ? "позиция собрана" : `осталось ${remaining} шт.`}</span></div><div>${complete ? `<span class="status-chip">✓ Собрано</span>` : `<button type="button" class="small-button secondary" data-wms-task-scan-product="${escapeHtml(allocation.id)}">${scanned ? "✓ Товар отсканирован" : "Сканировать товар"}</button><div class="field"><label>Количество</label><input type="number" min="1" max="${escapeHtml(remaining)}" value="${escapeHtml(remaining)}" data-wms-task-quantity="${escapeHtml(allocation.id)}"></div><button type="button" class="small-button" data-wms-task-pick="${escapeHtml(allocation.id)}" ${scanned ? "" : "disabled"}>Выполнить</button>`}</div></div>`; }).join("")}</div>` : ""}${taskDetail.can_confirm ? `<div class="card field-card"><b>Все позиции собраны.</b><p>Подтвердите отгрузку: задание перейдёт в раздел «Отгружено», а поставка маркетплейса получит статус «Отгружено на производстве».</p></div>` : ""}` : "";
      const creating = Boolean(state.wmsShipmentCreate && state.data && state.data.is_admin);
      const availableRows = (state.wmsData.stock || []).filter((row) => row.product_key?.item_type === "finished" && row.location_id && Math.max(0, Number(row.quantity || 0) - Number(row.reserved_quantity || 0)) > 0);
      const draftLines = Object.entries(state.wmsShipmentDraft.lines || {}).map(([stockId, quantity]) => {
        const stock = availableRows.find((row) => String(row.id) === String(stockId));
        return stock ? {stock, quantity} : null;
      }).filter(Boolean);
      const selectedIds = new Set(draftLines.map((line) => String(line.stock.id)));
      const pickerRows = availableRows.filter((row) => !selectedIds.has(String(row.id)));
      const draftTotal = draftLines.reduce((sum, line) => sum + Math.max(0, Number(line.quantity || 0)), 0);
      mainButton.textContent = "Обновить отгрузки";
      mainButton.disabled = state.wmsData.loading;
      mount.innerHTML = `
        <div class="screen-head"><div><h2>${taskDetail ? `Комплектация ${escapeHtml(taskDetail.number)}` : (detail ? `Отгрузка ${escapeHtml(detail.number)}` : (creating ? "Новая отгрузка" : "Отгрузки со склада"))}</h2><p>${taskDetail ? "Сканируйте ячейку, выберите товар и подтвердите фактически отобранное количество." : (detail ? "Лист отбора: что взять и из какой ячейки." : (creating ? "Добавьте товары из доступных адресных остатков и подтвердите документ." : "Задания сотрудников на комплектацию и выполненные отгрузки."))}</p></div><div class="date">${taskDetail ? `${escapeHtml(taskDetail.picked_quantity || 0)} / ${escapeHtml(taskDetail.total_quantity || 0)} шт.` : (detail ? `${detail.total} шт.` : `${allTasks.length + rows.length} док.`)}</div></div>
        ${renderWmsDataNotice()}
        ${!detail && !creating && !taskDetail ? pendingTasksBlock : ""}
        ${taskDetail ? taskDetailBlock : (detail ? `<div class="button-row"><button type="button" class="small-button secondary" data-wms-shipment-action="back">‹ Все отгрузки</button><button type="button" class="small-button secondary" data-wms-shipment-export="xlsx">Excel</button><button type="button" class="small-button" data-wms-shipment-export="pdf">PDF</button></div><div class="card field-card"><div class="detail-grid"><div class="detail-box"><span>Позиций</span><strong>${escapeHtml(detail.lines.length)}</strong></div><div class="detail-box"><span>Всего</span><strong>${escapeHtml(detail.total)} шт.</strong></div><div class="detail-box"><span>Ячеек</span><strong>${escapeHtml(detail.locations)}</strong></div><div class="detail-box"><span>Дата</span><strong>${escapeHtml(wmsMovementTime(detail.occurred_at) || "—")}</strong></div></div><div class="task-note">${escapeHtml(detail.reason || "")}</div></div><div class="section-title"><b>Лист отбора</b><span>${detail.lines.length} поз.</span></div><div class="op-list">${detail.lines.map((line, index) => `<div class="card report-row"><div><b>${index + 1}. ${escapeHtml(line.product_name)}</b><span>Размер ${escapeHtml(line.product_size)} · Цвет ${escapeHtml(line.product_color)}<br>Взять из: ${escapeHtml(line.from_location_code)}${line.from_location_name ? ` · ${escapeHtml(line.from_location_name)}` : ""}</span></div><span class="status-chip">${escapeHtml(line.quantity)} шт.</span></div>`).join("")}</div>` : creating ? `<div class="card field-card"><div class="form-grid"><div class="field"><label>Получатель или назначение</label><input id="wmsShipmentDestination" maxlength="120" placeholder="Например, магазин или контрагент" value="${escapeHtml(state.wmsShipmentDraft.destination || "")}"></div><div class="field"><label>Комментарий</label><input id="wmsShipmentComment" maxlength="300" placeholder="Необязательно" value="${escapeHtml(state.wmsShipmentDraft.comment || "")}"></div></div><div class="wms-shipment-picker"><div class="field"><label>Добавить товар из ячейки</label><select id="wmsShipmentProduct">${pickerRows.length ? `<option value="">Выберите товар</option>${pickerRows.map((row) => `<option value="${escapeHtml(row.id)}">${escapeHtml(wmsProductLabel(row.product_key))} · ${escapeHtml(wmsLocationLabel(row.location_id))} · доступно ${escapeHtml(Math.max(0, Number(row.quantity || 0) - Number(row.reserved_quantity || 0)))}</option>`).join("")}` : `<option value="">Все доступные позиции добавлены</option>`}</select></div><button type="button" class="small-button secondary" data-wms-shipment-action="add">Добавить позицию</button></div></div><div class="section-title"><b>Состав отгрузки</b><span>${draftLines.length} поз.</span></div><div class="op-list">${draftLines.length ? draftLines.map(({stock, quantity}) => { const available = Math.max(0, Number(stock.quantity || 0) - Number(stock.reserved_quantity || 0)); return `<div class="card wms-shipment-line">${stock.marketplace_product ? `<div class="wms-product-rich">${marketplaceProductAvatar(stock.marketplace_product, false, true)}<div class="wms-product-rich-copy"><b>${escapeHtml(stock.marketplace_product.group_name || stock.marketplace_product.name || wmsProductLabel(stock.product_key))}</b><span>${escapeHtml(wmsProductLabel(stock.product_key))}</span><small>Ячейка ${escapeHtml(wmsLocationLabel(stock.location_id))} · доступно ${escapeHtml(available)} ${escapeHtml(stock.unit || "шт")}</small></div></div>` : `<div><b>${escapeHtml(wmsProductLabel(stock.product_key))}</b><span>Ячейка ${escapeHtml(wmsLocationLabel(stock.location_id))} · доступно ${escapeHtml(available)} ${escapeHtml(stock.unit || "шт")}</span></div>`}<div class="field"><label>Количество</label><input type="number" min="1" max="${escapeHtml(available)}" step="1" inputmode="numeric" data-wms-shipment-qty="${escapeHtml(stock.id)}" value="${escapeHtml(quantity)}"></div><button type="button" class="small-button danger" data-wms-shipment-remove="${escapeHtml(stock.id)}">Убрать</button></div>`; }).join("") : itemEmpty("Добавьте товары из списка выше.")}</div><div class="wms-shipment-summary"><div><b>Итого к отгрузке</b><br><span>${draftLines.length} позиций</span></div><strong>${escapeHtml(draftTotal)} шт.</strong></div><div class="button-row"><button type="button" class="small-button secondary" data-wms-shipment-action="cancel">Отмена</button><button type="button" class="small-button" data-wms-shipment-action="submit" ${draftLines.length ? "" : "disabled"}>Создать и списать со склада</button></div>` : `<div class="button-row">${state.data && state.data.is_admin ? `<button type="button" class="small-button" data-wms-shipment-action="new">+ Создать отгрузку</button>` : ""}</div><div class="op-list">${rows.length ? rows.map((shipment) => `<button type="button" class="card field-card marketplace-clickable" data-wms-shipment-number="${escapeHtml(shipment.number)}"><div class="section-title"><b>${escapeHtml(shipment.number)}</b><span class="status-chip">открыть ›</span></div><div class="detail-grid"><div class="detail-box"><span>Позиций</span><strong>${escapeHtml(shipment.rows.length)}</strong></div><div class="detail-box"><span>Всего</span><strong>${escapeHtml(shipment.total)} шт.</strong></div><div class="detail-box"><span>Ячеек</span><strong>${escapeHtml(shipment.locations.size)}</strong></div><div class="detail-box"><span>Дата</span><strong>${escapeHtml(wmsMovementTime(shipment.occurredAt) || "—")}</strong></div></div></button>`).join("") : itemEmpty("Отгрузок пока нет.")}</div>`)}
      `;
    }

    function syncWmsShipmentDraft() {
      const destination = document.getElementById("wmsShipmentDestination");
      const comment = document.getElementById("wmsShipmentComment");
      if (destination) state.wmsShipmentDraft.destination = destination.value.trim();
      if (comment) state.wmsShipmentDraft.comment = comment.value.trim();
      document.querySelectorAll("[data-wms-shipment-qty]").forEach((input) => {
        state.wmsShipmentDraft.lines[input.dataset.wmsShipmentQty] = input.value;
      });
    }

    async function createWmsShipment() {
      if (!(state.data && state.data.is_admin)) return;
      syncWmsShipmentDraft();
      const stockRows = state.wmsData.stock || [];
      const lines = Object.entries(state.wmsShipmentDraft.lines || {}).map(([stockId, quantity]) => {
        const stock = stockRows.find((row) => String(row.id) === String(stockId));
        if (!stock) return null;
        return {product_key: stock.product_key, quantity: Number(quantity || 0), from_location_code: wmsLocationLabel(stock.location_id), unit: stock.unit || "шт"};
      }).filter(Boolean);
      if (!state.wmsShipmentDraft.destination) return showToast("Отгрузка", "Укажите получателя или назначение.");
      if (!lines.length || lines.some((line) => !Number.isInteger(line.quantity) || line.quantity <= 0)) return showToast("Отгрузка", "Проверьте количество во всех позициях.");
      try {
        const result = await api("/api/wms/shipment/create", {destination: state.wmsShipmentDraft.destination, comment: state.wmsShipmentDraft.comment, lines});
        if (!result.ok) throw new Error(result.message || "Не удалось создать отгрузку.");
        state.wmsShipmentCreate = false;
        state.wmsShipmentDraft = {destination: "", comment: "", lines: {}};
        await refreshWmsWorkspace({silent: true});
        await loadWmsShipment(result.shipment.number);
        showToast("Отгрузка", result.message || "Документ создан.");
      } catch (error) {
        showToast("Отгрузка", error.apiMessage || error.message || "Не удалось создать отгрузку.");
      }
    }

    async function loadWmsShipment(number) {
      try {
        const data = await api("/api/wms/shipment/detail", {shipment_number: number});
        if (!data.ok) throw new Error(data.message || "Не удалось открыть отгрузку.");
        state.wmsShipmentDetail = data.shipment;
        render();
      } catch (error) {
        showToast("Отгрузка", error.apiMessage || error.message || "Не удалось открыть отгрузку.");
      }
    }

    async function loadWmsShipmentTask(number) {
      try {
        const data = await api("/api/wms/shipment/task-detail", {shipment_number: number});
        if (!data.ok) throw new Error(data.message || "Не удалось открыть задание.");
        state.wmsShipmentTaskDetail = data.shipment;
        state.wmsShipmentDetail = null;
        state.wmsShipmentTaskLocation = "";
        state.wmsShipmentTaskScannedAllocationId = "";
        state.wmsShipmentTaskExpectedAllocationId = "";
        render();
      } catch (error) {
        showToast("Отгрузка", error.apiMessage || error.message || "Не удалось открыть задание.");
      }
    }

    async function startWmsShipmentTask() {
      const task = state.wmsShipmentTaskDetail;
      if (!task) return;
      try {
        const data = await api("/api/wms/shipment/task-start", {shipment_number: task.number});
        if (!data.ok) throw new Error(data.message || "Не удалось подготовить задание.");
        state.wmsShipmentTaskDetail = data.shipment;
        state.wmsShipmentTaskScannedAllocationId = "";
        state.wmsShipmentTaskExpectedAllocationId = "";
        await refreshWmsWorkspace({silent: true});
        render();
        showToast("Отгрузка", data.message || "Ячейки подготовлены.");
      } catch (error) {
        showToast("Отгрузка", error.apiMessage || error.message || "Не удалось подготовить задание.");
      }
    }

    async function pickWmsShipmentTask(allocationId) {
      const task = state.wmsShipmentTaskDetail;
      if (!task) return;
      const quantityInput = [...document.querySelectorAll("[data-wms-task-quantity]")].find((input) => String(input.dataset.wmsTaskQuantity) === String(allocationId));
      const locationInput = document.getElementById("wmsShipmentTaskCell");
      const locationCode = String((locationInput && locationInput.value) || state.wmsShipmentTaskLocation || "").trim().toUpperCase();
      const quantity = Number(quantityInput && quantityInput.value);
      if (!locationCode) { showToast("Отгрузка", "Сначала отсканируйте ячейку."); return; }
      if (String(state.wmsShipmentTaskScannedAllocationId) !== String(allocationId)) { showToast("Отгрузка", "Сначала отсканируйте нужный товар."); return; }
      if (!Number.isInteger(quantity) || quantity <= 0) { showToast("Отгрузка", "Укажите целое количество для подбора."); return; }
      try {
        const data = await api("/api/wms/shipment/task-pick", {
          shipment_number: task.number, allocation_id: Number(allocationId), quantity,
          location_code: locationCode, request_key: `web-pick:${task.number}:${allocationId}:${Date.now()}`,
        });
        if (!data.ok) throw new Error(data.message || "Не удалось выполнить подбор.");
        state.wmsShipmentTaskDetail = data.shipment;
        state.wmsShipmentTaskLocation = locationCode;
        state.wmsShipmentTaskScannedAllocationId = "";
        state.wmsShipmentTaskExpectedAllocationId = "";
        await refreshWmsWorkspace({silent: true});
        render();
        showToast("Отгрузка", data.message || "Позиция отобрана.");
      } catch (error) {
        showToast("Отгрузка", error.apiMessage || error.message || "Не удалось выполнить подбор.");
      }
    }

    async function confirmWmsShipmentTask() {
      const task = state.wmsShipmentTaskDetail;
      if (!task) return;
      try {
        const data = await api("/api/wms/shipment/task-confirm", {shipment_number: task.number});
        if (!data.ok) throw new Error(data.message || "Не удалось подтвердить отгрузку.");
        state.wmsShipmentTaskDetail = data.shipment;
        state.wmsShipmentTaskTab = "shipped";
        await refreshWmsWorkspace({silent: true});
        render();
        showToast("Отгрузка", data.message || "Отгрузка подтверждена.");
      } catch (error) {
        showToast("Отгрузка", error.apiMessage || error.message || "Не удалось подтвердить отгрузку.");
      }
    }

    async function exportWmsShipment(format) {
      const shipment = state.wmsShipmentDetail;
      if (!shipment) return;
      try {
        const headers = {"Content-Type": "application/json"};
        if (isStandaloneWeb && webCsrfToken) headers["X-CSRF-Token"] = webCsrfToken;
        const response = await fetch("/api/wms/shipment/export", {method: "POST", headers, credentials: "same-origin", body: JSON.stringify({shipment_number: shipment.number, format, telegram_id: debugTelegramId})});
        if (!response.ok) {
          const error = await response.json().catch(() => ({}));
          throw new Error(error.message || "Не удалось выгрузить отгрузку.");
        }
        const blob = await response.blob();
        const disposition = response.headers.get("Content-Disposition") || "";
        const match = disposition.match(/filename\\*=UTF-8''([^;]+)/);
        const filename = match ? decodeURIComponent(match[1]) : `shipment.${format}`;
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        link.remove();
        URL.revokeObjectURL(link.href);
        showToast("Отгрузка", format === "pdf" ? "PDF сформирован." : "Excel сформирован.");
      } catch (error) {
        showToast("Отгрузка", error.message || "Не удалось выгрузить отгрузку.");
      }
    }

    async function refreshWmsWorkspace({silent = false} = {}) {
      if (!canAccessWms() || state.wmsData.loading) return;
      state.wmsData.loading = true;
      state.wmsData.error = "";
      if (!silent) render();
      try {
        const [locations, stock, movements, shipmentTasks] = await Promise.all([
          api("/api/wms/locations"),
          api("/api/wms/stock"),
          api("/api/wms/movements", {limit: 100}),
          api("/api/wms/shipment/tasks"),
        ]);
        state.wmsData.locations = locations.locations || [];
        state.wmsData.stock = stock.stock || [];
        state.wmsData.movements = movements.movements || [];
        state.wmsData.shipmentTasks = shipmentTasks.shipments || [];
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

    function marketplaceProductionStockText(row) {
      if (row?.production_stock_available === false) return "WMS недоступен";
      if (!row?.production_linked && row?.products == null) return "Маршрут не настроен";
      if (row?.products != null && Number(row.production_linked_products || 0) === 0) return "Маршрут не настроен";
      return `${Number(row?.production_available || 0)} шт.`;
    }

    function marketplaceBackButton(label = "Назад") {
      return `<button type="button" class="small-button secondary" data-marketplace-action="back">‹ ${escapeHtml(label)}</button>`;
    }

    function marketplaceProductAvatar(row, compact = false, large = false) {
      const imageUrl = String((row && row.image_url) || "");
      const name = String((row && row.name) || "Товар");
      const sizeClass = large ? " large" : (compact ? " compact" : "");
      return `<span class="marketplace-product-avatar${sizeClass}"><span aria-hidden="true">▦</span>${imageUrl ? `<img src="${escapeHtml(imageUrl)}" alt="${escapeHtml(name)}" loading="lazy" referrerpolicy="no-referrer">` : ""}</span>`;
    }

    function marketplaceStockLevel(quantity) {
      const value = Number(quantity || 0);
      if (value <= 0) return {key: "absent", label: "Отсутствует"};
      if (value < 10) return {key: "low", label: "Нужно пополнить"};
      return {key: "enough", label: "Хватает"};
    }

    function filterMarketplaceStocks(control) {
      const section = control.closest(".marketplace-stock-section");
      if (!section) return;
      const warehouse = section.querySelector('[data-stock-filter="warehouse"]')?.value || "all";
      const product = section.querySelector('[data-stock-filter="product"]')?.value || "all";
      const color = section.querySelector('[data-stock-filter="color"]')?.value || "all";
      const size = section.querySelector('[data-stock-filter="size"]')?.value || "all";
      const criticality = section.querySelector('[data-stock-filter="criticality"]')?.value || "all";
      let visible = 0;
      section.querySelectorAll(".marketplace-stock-card").forEach((card) => {
        const stocks = Object.fromEntries(String(card.dataset.stockMap || "").split("|").filter(Boolean).map((part) => {
          const splitAt = part.lastIndexOf(":");
          return [part.slice(0, splitAt), Number(part.slice(splitAt + 1) || 0)];
        }));
        const quantity = warehouse === "all" ? Number(card.dataset.stockTotal || 0) : Number(stocks[warehouse] || 0);
        const level = marketplaceStockLevel(quantity);
        const matches = (product === "all" || card.dataset.stockProduct === product)
          && (color === "all" || card.dataset.stockColor === color)
          && (size === "all" || card.dataset.stockSize === size)
          && (criticality === "all" || level.key === criticality);
        card.hidden = !matches;
        if (matches) visible += 1;
        const quantityNode = card.querySelector("[data-stock-quantity]");
        const levelNode = card.querySelector("[data-stock-level]");
        if (quantityNode) quantityNode.textContent = `${quantity} шт.`;
        if (levelNode) {
          levelNode.textContent = level.label;
          levelNode.className = `status-chip marketplace-stock-level ${level.key}`;
        }
      });
      const countNode = section.querySelector("[data-stock-visible-count]");
      const emptyNode = section.querySelector(".marketplace-stock-empty");
      if (countNode) countNode.textContent = String(visible);
      if (emptyNode) emptyNode.classList.toggle("visible", visible === 0);
    }

    function marketplaceLineChart(rows, primaryKey = "revenue", secondaryKey = "net") {
      const source = Array.isArray(rows) ? rows.filter(Boolean) : [];
      if (!source.length) return itemEmpty("За выбранный период данных нет.");
      const width = 720, height = 230, left = 48, right = 18, top = 18, bottom = 34;
      const chartWidth = width - left - right, chartHeight = height - top - bottom;
      const primary = source.map((row) => Number(row[primaryKey] || 0));
      const secondary = secondaryKey ? source.map((row) => Number(row[secondaryKey] || 0)) : [];
      const minimum = Math.min(0, ...primary, ...secondary);
      const maximum = Math.max(minimum + 1, 0, ...primary, ...secondary);
      const valueRange = maximum - minimum;
      const x = (index) => source.length === 1 ? left + chartWidth / 2 : left + chartWidth * index / (source.length - 1);
      const y = (value) => top + chartHeight * (maximum - Number(value || 0)) / valueRange;
      const points = (values) => values.map((value, index) => `${x(index).toFixed(1)},${y(value).toFixed(1)}`).join(" ");
      const primaryPoints = points(primary);
      const secondaryPoints = points(secondary);
      const areaPoints = source.length > 1 ? `${left},${y(0)} ${primaryPoints} ${x(source.length - 1)},${y(0)}` : "";
      const labelIndexes = [...new Set([0, Math.floor((source.length - 1) / 2), source.length - 1])];
      const valueLabel = (value) => { const number = Number(value || 0); const absolute = Math.abs(number); return absolute >= 1000000 ? `${(number / 1000000).toFixed(1)}м` : absolute >= 1000 ? `${Math.round(number / 1000)}к` : String(Math.round(number)); };
      const pointEvents = 'tabindex="0" role="button" onmouseenter="showMarketplaceChartTooltip(this)" onmouseleave="hideMarketplaceChartTooltip(this)" onfocus="showMarketplaceChartTooltip(this)" onblur="hideMarketplaceChartTooltip(this)" onclick="showMarketplaceChartTooltip(this)" ontouchstart="showMarketplaceChartTooltip(this)"';
      return `<div class="marketplace-line-chart"><svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Динамика показателей"><defs><linearGradient id="marketplaceChartArea" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#4f83ff" stop-opacity=".28"/><stop offset="100%" stop-color="#4f83ff" stop-opacity="0"/></linearGradient></defs>${[0,.25,.5,.75,1].map((ratio) => { const gridY = top + chartHeight * ratio; const tickValue = maximum - valueRange * ratio; return `<line class="chart-grid" x1="${left}" y1="${gridY}" x2="${width-right}" y2="${gridY}"/><text class="chart-axis-label" x="${left-8}" y="${gridY+4}" text-anchor="end">${valueLabel(tickValue)}</text>`; }).join("")}${minimum < 0 && maximum > 0 ? `<line x1="${left}" y1="${y(0)}" x2="${width-right}" y2="${y(0)}" stroke="#7d8799" stroke-width="1.5"/>` : ""}${areaPoints ? `<polygon class="chart-area" points="${areaPoints}"/>` : ""}${source.length > 1 ? `<polyline class="chart-line-primary" points="${primaryPoints}"/>` : ""}${secondary.length ? `<polyline class="chart-line-secondary" points="${secondaryPoints}"/>` : ""}${primary.map((value,index) => { const pointLabel = `${source[index].date || "Дата не указана"} · ${marketplaceMoney(value)}`; return `<circle class="chart-point-primary" cx="${x(index)}" cy="${y(value)}" r="${source.length === 1 ? 6 : 3.6}"/><circle class="chart-point-hit" cx="${x(index)}" cy="${y(value)}" r="12" ${pointEvents} aria-label="${escapeHtml(pointLabel)}" data-chart-date="${escapeHtml(source[index].date || "")}" data-chart-value="${escapeHtml(value)}"><title>${escapeHtml(pointLabel)}</title></circle>${source.length === 1 ? `<text class="chart-axis-label" x="${x(index)}" y="${Math.max(top + 16, y(value) - 14)}" text-anchor="middle">${escapeHtml(valueLabel(value))}</text>` : ""}`; }).join("")}${secondary.map((value,index) => { const pointLabel = `${source[index].date || "Дата не указана"} · ${marketplaceMoney(value)}`; return `<circle class="chart-point-secondary" cx="${x(index)}" cy="${y(value)}" r="3"/><circle class="chart-point-hit" cx="${x(index)}" cy="${y(value)}" r="10" ${pointEvents} aria-label="${escapeHtml(pointLabel)}" data-chart-date="${escapeHtml(source[index].date || "")}" data-chart-value="${escapeHtml(value)}"><title>${escapeHtml(pointLabel)}</title></circle>`; }).join("")}${labelIndexes.map((index) => `<text class="chart-axis-label" x="${x(index)}" y="${height-9}" text-anchor="middle">${escapeHtml(String(source[index].date || "").slice(5))}</text>`).join("")}</svg><div class="marketplace-point-tooltip" hidden></div></div>`;
    }

    function marketplaceOrderLineChart(orders) {
      const daily = new Map();
      (orders || []).forEach((row) => {
        const date = String(row.shipment_date || row.updated_at || "").slice(0, 10);
        if (date) daily.set(date, (daily.get(date) || 0) + 1);
      });
      return marketplaceLineChart([...daily.entries()].sort((a,b) => a[0].localeCompare(b[0])).map(([date,value]) => ({date,value})), "value", null);
    }

    function showMarketplaceChartTooltip(point) {
      const chart = point.closest(".marketplace-line-chart");
      const tooltip = chart?.querySelector(".marketplace-point-tooltip");
      if (!chart || !tooltip) return;
      const chartRect = chart.getBoundingClientRect();
      const pointRect = point.getBoundingClientRect();
      const rawDate = String(point.dataset.chartDate || "");
      const date = rawDate ? new Date(`${rawDate}T00:00:00`) : null;
      const dateLabel = date && !Number.isNaN(date.getTime()) ? date.toLocaleDateString("ru-RU") : (rawDate || "Дата не указана");
      tooltip.innerHTML = `<b>${escapeHtml(marketplaceMoney(Number(point.dataset.chartValue || 0)))}</b><span>${escapeHtml(dateLabel)}</span>`;
      tooltip.style.left = `${pointRect.left - chartRect.left + pointRect.width / 2}px`;
      tooltip.style.top = `${pointRect.top - chartRect.top + pointRect.height / 2}px`;
      tooltip.hidden = false;
    }

    function hideMarketplaceChartTooltip(point) {
      const tooltip = point.closest(".marketplace-line-chart")?.querySelector(".marketplace-point-tooltip");
      if (tooltip) tooltip.hidden = true;
    }

    function renderMarketplaceDetail(products, orders, runs) {
      const detail = state.marketplaceDetail || {};
      const providerLabel = state.marketplaceProvider === "wildberries" ? "Wildberries" : (state.marketplaceProvider === "all" ? "маркетплейсы" : "Ozon");
      const rootPayload = state.marketplaceData.payload || {};
      const selectedPayload = state.marketplaceProvider === "wildberries" ? (rootPayload.wildberries || {}) : rootPayload;
      const selectedAnalytics = selectedPayload.analytics || {};
      const selectedCapabilityStatuses = selectedAnalytics.capability_statuses || {};
      const selectedStockCapability = selectedCapabilityStatuses.stocks || {};
      const selectedStocksUsable = state.marketplaceProvider !== "wildberries"
        || selectedStockCapability.status === "available"
        || (!selectedCapabilityStatuses.stocks && selectedAnalytics.capabilities?.stocks === true);
      const selectedProductHistoryCapability = selectedCapabilityStatuses.product_history || {};
      const selectedProductHistoryUsable = state.marketplaceProvider !== "wildberries"
        || selectedProductHistoryCapability.status === "available"
        || selectedAnalytics.capabilities?.product_history === true;
      if (detail.kind === "group") {
        const groupRows = products.filter((row) => String(row.group_key || "other") === String(detail.key)).sort((left, right) => {
          const colorCompare = String(left.color || "Цвет не указан").localeCompare(String(right.color || "Цвет не указан"), "ru");
          if (colorCompare) return colorCompare;
          return String(left.size || "").localeCompare(String(right.size || ""), "ru", {numeric: true, sensitivity: "base"});
        });
        const colorGroups = [];
        groupRows.forEach((row) => {
          const color = String(row.color || "Цвет не указан");
          let colorGroup = colorGroups.find((item) => item.color === color);
          if (!colorGroup) {
            colorGroup = {color, rows: []};
            colorGroups.push(colorGroup);
          }
          colorGroup.rows.push(row);
        });
        const group = marketplaceGroups(selectedPayload, products).find((row) => String(row.key) === String(detail.key));
        if (!group) return "";
        const groupStock = selectedStocksUsable && group.available !== null && group.available !== undefined ? `${Number(group.available || 0)} шт.` : "—";
        return `
          <div class="marketplace-detail-head"><div>${marketplaceBackButton("К группам")}</div><div><h3>${escapeHtml(group.name)}</h3><p>${groupRows.length} позиций · ${group.articles || groupRows.length} артикулов · ${escapeHtml(providerLabel)} ${escapeHtml(groupStock)} · производство ${escapeHtml(marketplaceProductionStockText(group))}</p></div></div>
          <div class="marketplace-detail-grid">
            ${marketplaceDetailField("Товаров в группе", group.products || groupRows.length)}
            ${marketplaceDetailField("Артикулов", group.articles || groupRows.length)}
            ${marketplaceDetailField(`Остаток ${providerLabel}`, groupStock)}
            ${marketplaceDetailField("Остаток производства", marketplaceProductionStockText(group))}
            ${marketplaceDetailField("Цена от", marketplaceMoney(group.price_min))}
            ${marketplaceDetailField("Цена до", marketplaceMoney(group.price_max))}
          </div>
          <div class="section-title"><b>Товары группы</b><span>${groupRows.length}</span></div>
          <div class="marketplace-color-sections">${groupRows.length ? colorGroups.map((colorGroup) => `<section class="marketplace-color-section"><div class="marketplace-color-heading"><b>${escapeHtml(colorGroup.color)}</b><span>${colorGroup.rows.length} вариантов</span></div><div class="marketplace-variant-grid">${colorGroup.rows.map((row) => `
            <button type="button" class="card marketplace-clickable marketplace-product-card" data-marketplace-product-id="${escapeHtml(row.id)}">
              ${marketplaceProductAvatar(row, false, true)}
              <span class="marketplace-product-card-body">
                <span class="product-title"><b>${escapeHtml(row.name || `Товар ${providerLabel}`)}</b></span>
                <span class="marketplace-product-primary-meta"><span>${escapeHtml(row.size || "Размер не указан")}</span><span>${escapeHtml(row.color || "Цвет не указан")}</span></span>
                <span class="marketplace-product-secondary-meta">Артикул: ${escapeHtml(row.offer_id || "—")} · SKU: ${escapeHtml(row.sku || "—")}</span>
                <span class="marketplace-product-commercial"><span>${escapeHtml(providerLabel)}: ${selectedStocksUsable && row.available != null ? `${escapeHtml(row.available)} шт.` : "—"}</span><span>Производство: ${escapeHtml(marketplaceProductionStockText(row))}</span><span>${marketplaceMoney(row.current_price)}</span></span>
              </span>
              <span class="status-chip marketplace-card-arrow">›</span>
            </button>`).join("")}</div></section>`).join("") : itemEmpty("В этой группе пока нет товаров.")}</div>
        `;
      }
      if (detail.kind === "product") {
        const product = products.find((row) => String(row.id) === String(detail.id));
        if (!product) return "";
        const productPeriod = state.marketplaceProductPeriod || "7d";
        const history = Array.isArray(product.history) ? product.history : [];
        const periodHistory = selectedProductHistoryUsable
          ? (productPeriod === "all" ? history : history.filter((row) => marketplaceDateInPeriod(row.date, marketplacePeriodMeta(productPeriod))))
          : [];
        const historyTotals = periodHistory.reduce((result, row) => ({
          orders: result.orders + Number(row.orders || 0),
          units: result.units + Number(row.units || 0),
          returns: result.returns + Number(row.returns || 0),
          accruals: result.accruals + Number(row.accruals || 0),
        }), {orders: 0, units: 0, returns: 0, accruals: 0});
        const warehouseStocks = product.warehouse_stocks || {};
        const productHistoryValue = (value, suffix = "") => selectedProductHistoryUsable ? `${escapeHtml(value)}${suffix}` : "—";
        const productChart = !selectedProductHistoryUsable
          ? `<div class="marketplace-chart-empty"><b>История товара недоступна</b><span>${escapeHtml(providerLabel)} пока не предоставляет подтверждённую историю заказов, продаж, возвратов и начислений по этой карточке.</span></div>`
          : periodHistory.length
          ? `${marketplaceLineChart(periodHistory, "units", "orders")}<div class="marketplace-chart-legend"><span><i></i>Продано, шт.</span><span><i class="secondary"></i>Заказы</span></div>`
          : `<div class="marketplace-chart-empty"><b>За выбранный период операций нет</b><span>Источник истории доступен и подтвердил пустой период.</span></div>`;
        return `
          <div class="marketplace-detail-head"><div>${marketplaceBackButton("К группе")}</div><div class="marketplace-product-heading">${marketplaceProductAvatar(product, false, true)}<span><h3>${escapeHtml(product.name || product.offer_id || product.sku || "Товар")}</h3><p>${escapeHtml(product.group_name || "Товар маркетплейса")}</p></span></div></div>
          <div class="marketplace-detail-grid">
            ${marketplaceDetailField("Артикул", product.offer_id)}
            ${marketplaceDetailField("SKU", product.sku)}
            ${marketplaceDetailField("Штрихкод", product.barcode)}
            ${marketplaceDetailField("Размер", product.size)}
            ${marketplaceDetailField("Цвет", product.color)}
            ${marketplaceDetailField(`Остаток ${providerLabel}`, selectedStocksUsable && product.available != null ? `${product.available} шт.` : "—")}
            ${marketplaceDetailField("Остаток производства", marketplaceProductionStockText(product))}
            ${marketplaceDetailField(`${providerLabel} · склады`, selectedStocksUsable ? `${Object.values(warehouseStocks).reduce((sum, value) => sum + Number(value || 0), 0)} шт.` : "—")}
            ${marketplaceDetailField("Текущая цена", marketplaceMoney(product.current_price))}
            ${marketplaceDetailField("Старая цена", marketplaceMoney(product.old_price))}
            ${marketplaceDetailField("Обновлено", product.updated_at)}
          </div>
          <div class="marketplace-filter-bar"><label><span>Период по товару</span><select onchange="state.marketplaceProductPeriod=this.value;renderMarketplaces()"><option value="7d" ${productPeriod === "7d" ? "selected" : ""}>Последние 7 дней</option><option value="30d" ${productPeriod === "30d" ? "selected" : ""}>Последние 30 дней</option><option value="all" ${productPeriod === "all" ? "selected" : ""}>Всё время</option></select></label><div class="marketplace-period-label">${productPeriod === "all" ? "Вся загруженная история" : escapeHtml(marketplacePeriodMeta(productPeriod).label)}</div></div>
          <div class="marketplace-v2-kpis">
            <div class="card marketplace-v2-kpi"><span>Заказы</span><strong>${productHistoryValue(historyTotals.orders, " шт.")}</strong><small>${selectedProductHistoryUsable ? "Связанные с товаром" : "Источник не подтверждён"}</small></div>
            <div class="card marketplace-v2-kpi"><span>Продано</span><strong>${productHistoryValue(historyTotals.units, " шт.")}</strong><small>${selectedProductHistoryUsable ? "По загруженным заказам" : "Источник не подтверждён"}</small></div>
            <div class="card marketplace-v2-kpi"><span>Возвраты</span><strong>${productHistoryValue(historyTotals.returns, " шт.")}</strong><small>${selectedProductHistoryUsable ? `По данным ${escapeHtml(providerLabel)}` : "Источник не подтверждён"}</small></div>
            <div class="card marketplace-v2-kpi"><span>Начисления</span><strong>${selectedProductHistoryUsable ? marketplaceMoney(historyTotals.accruals) : "—"}</strong><small>${selectedProductHistoryUsable ? "Связанные по SKU" : "Источник не подтверждён"}</small></div>
          </div>
          <section class="card marketplace-analytic-card"><div class="section-title"><b>Динамика товара</b><span>${selectedProductHistoryUsable ? `${periodHistory.length} дней с данными` : "нет подтверждённого источника"}</span></div>${productChart}</section>
        `;
      }
      if (detail.kind === "order") {
        const order = orders.find((row) => String(row.id) === String(detail.id));
        if (!order) return "";
        return `
          <div class="marketplace-detail-head"><div>${marketplaceBackButton("К отгрузкам")}</div><div><h3>${escapeHtml(order.posting_number || order.external_order_id || "Отгрузка")}</h3><p>Отгрузка ${escapeHtml(providerLabel)} · подробности доступны только для чтения</p></div></div>
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

    const marketplaceRouteMap = {
      overview: "", products: "/products", orders: "/orders", supplies: "/supplies",
      finance: "/finance", analytics: "/analytics", reviews: "/reviews", settings: "/settings",
      "data-quality": "/data-quality",
      stocks: "/stocks", "warehouse-shipments": "/warehouse-shipments", sync: "/sync",
    };

    function marketplaceViewFromPath(pathname) {
      const path = String(pathname || "");
      const marker = "/app/marketplaces";
      const suffix = path.startsWith(marker) ? path.slice(marker.length).split("/").filter(Boolean)[0] || "" : "";
      if (!suffix) return "overview";
      const found = Object.entries(marketplaceRouteMap).find(([, route]) => route === `/${suffix}`);
      return found ? found[0] : "overview";
    }

    function applyMarketplaceLocation() {
      if (!isStandaloneWeb || !window.location.pathname.startsWith("/app/marketplaces")) return;
      const params = new URLSearchParams(window.location.search);
      const scope = params.get("scope");
      const period = params.get("period");
      const dateFrom = params.get("from") || "";
      const dateTo = params.get("to") || "";
      state.marketplaceProvider = ["all", "ozon", "wildberries"].includes(scope) ? scope : "all";
      state.marketplaceView = marketplaceViewFromPath(window.location.pathname);
      state.marketplacePeriod = ["today", "yesterday", "7d", "30d", "month", "previous-month", "custom"].includes(period) ? period : "7d";
    state.marketplaceDateFrom = /^\\d{4}-\\d{2}-\\d{2}$/.test(dateFrom) ? dateFrom : "";
      state.marketplaceDateTo = /^\\d{4}-\\d{2}-\\d{2}$/.test(dateTo) ? dateTo : "";
    }

    function syncMarketplaceLocation() {
      if (!isStandaloneWeb || !window.history || typeof window.history.replaceState !== "function") return;
      const route = marketplaceRouteMap[state.marketplaceView] || "";
      const params = new URLSearchParams();
      params.set("scope", ["all", "ozon", "wildberries"].includes(state.marketplaceProvider) ? state.marketplaceProvider : "all");
      params.set("period", state.marketplacePeriod || "7d");
      if (state.marketplacePeriod === "custom" && state.marketplaceDateFrom && state.marketplaceDateTo) {
        params.set("from", state.marketplaceDateFrom);
        params.set("to", state.marketplaceDateTo);
      }
      window.history.replaceState(null, "", `/app/marketplaces${route}?${params.toString()}`);
    }

    function marketplacePeriodMeta(period) {
      const todayKey = marketplaceLocalIsoDate();
      const end = new Date(`${todayKey}T00:00:00Z`);
      const start = new Date(end);
      const key = period || "7d";
      if (key === "custom" && state.marketplaceDateFrom && state.marketplaceDateTo) {
        const customStart = new Date(`${state.marketplaceDateFrom}T00:00:00Z`);
        const customEnd = new Date(`${state.marketplaceDateTo}T00:00:00Z`);
        if (!Number.isNaN(customStart.getTime()) && !Number.isNaN(customEnd.getTime())) {
          start.setTime(Math.min(customStart.getTime(), customEnd.getTime()));
          end.setTime(Math.max(customStart.getTime(), customEnd.getTime()));
        }
      }
      if (key === "yesterday") { start.setUTCDate(start.getUTCDate() - 1); end.setUTCDate(end.getUTCDate() - 1); }
      if (key === "7d") start.setUTCDate(start.getUTCDate() - 6);
      if (key === "30d") start.setUTCDate(start.getUTCDate() - 29);
      if (key === "month") start.setUTCDate(1);
      if (key === "previous-month") { start.setUTCMonth(start.getUTCMonth() - 1, 1); end.setUTCDate(0); }
      const dateKey = (value) => value.toISOString().slice(0, 10);
      const formatKey = (value) => `${value.slice(8, 10)}.${value.slice(5, 7)}.${value.slice(0, 4)}`;
      const startKey = dateKey(start);
      const endKey = dateKey(end);
      return {start, end, startKey, endKey, label: `${formatKey(startKey)} — ${formatKey(endKey)}`};
    }

    function marketplaceDateInPeriod(value, meta) {
      const match = String(value || "").match(/^(\\d{4}-\\d{2}-\\d{2})/);
      if (!match) return false;
      return match[1] >= meta.startKey && match[1] <= meta.endKey;
    }

    function marketplaceUnavailable(label) {
      return `<div class="marketplace-empty-metric"><b>${escapeHtml(label)}</b><span>Нет данных от API</span></div>`;
    }

    function renderMarketplaces() {
      if (!canAccessMarketplaces()) {
        mainButton.textContent = "Обновить";
        mainButton.disabled = false;
        mount.innerHTML = `<div class="screen-head"><div><h2>Маркетплейсы</h2><p>Раздел доступен администратору.</p></div></div><div class="card field-card">${itemEmpty("Нет прав администратора.")}</div>`;
        return;
      }
      if (!state.marketplaceLocationInitialized) {
        applyMarketplaceLocation();
        state.marketplaceLocationInitialized = true;
      }
      const payload = state.marketplaceData.payload || {};
      const selectedProvider = ["all", "ozon", "wildberries"].includes(state.marketplaceProvider) ? state.marketplaceProvider : "all";
      const isOzon = selectedProvider === "ozon";
      const isWildberries = selectedProvider === "wildberries";
      const isAll = selectedProvider === "all";
      const providerPayload = isWildberries ? (payload.wildberries || {}) : payload;
      const summary = providerPayload.summary || {};
      const periodMeta = marketplacePeriodMeta(state.marketplacePeriod);
      const allProducts = providerPayload.products_rows || [];
      const allOrders = providerPayload.orders_rows || [];
      const analytics = providerPayload.analytics || {};
      const wbCapabilities = analytics.capabilities && typeof analytics.capabilities === "object" ? analytics.capabilities : {};
      const wbCapabilityStatuses = analytics.capability_statuses && typeof analytics.capability_statuses === "object" ? analytics.capability_statuses : {};
      const wbCatalogStatus = wbCapabilityStatuses.catalog?.status || (wbCapabilities.catalog ? "legacy" : "no_data");
      const wbStocksStatus = wbCapabilityStatuses.stocks?.status || (wbCapabilities.stocks ? "legacy" : "no_data");
      const wbCatalogUsable = ["available", "legacy"].includes(wbCatalogStatus);
      const wbStocksUsable = ["available", "legacy"].includes(wbStocksStatus);
      const financeDaily = analytics.finance_daily || [];
      const periodFinance = financeDaily.filter((row) => marketplaceDateInPeriod(row.date, periodMeta));
      const periodRevenue = periodFinance.reduce((sum, row) => sum + Number(row.revenue || 0), 0);
      const periodNet = periodFinance.reduce((sum, row) => sum + Number(row.net || 0), 0);
      const allReturns = analytics.returns_rows || [];
      const periodReturnDays = (analytics.returns_daily || []).filter((row) => marketplaceDateInPeriod(row.date, periodMeta));
      const periodReturnRecords = periodReturnDays.reduce((sum, row) => sum + Number(row.records || 0), 0);
      const returnQuantity = periodReturnDays.reduce((sum, row) => sum + Number(row.quantity || 0), 0);
      const ratingValue = analytics.rating;
      const wbReviews = analytics.reviews_rows || [];
      const wbReviewSummary = analytics.reviews_summary || {};
      const wbFeedbacksCapability = wbCapabilityStatuses.feedbacks || {};
      const wbFeedbacksStatus = wbFeedbacksCapability.status || (wbCapabilities.reviews ? "legacy" : "no_data");
      const wbFeedbacksCurrent = wbFeedbacksStatus === "available";
      const wbHistoricalRating = wbReviewSummary.rating != null ? wbReviewSummary.rating : ratingValue;
      const effectiveRating = isWildberries ? (wbFeedbacksCurrent ? wbHistoricalRating : null) : ratingValue;
      if (isWildberries && !wbStocksUsable) state.marketplaceFilters.inStockOnly = false;
      if (isWildberries) state.marketplaceFilters.onlyProblems = false;
      const applyInStockFilter = state.marketplaceFilters.inStockOnly && (!isWildberries || wbStocksUsable);
      const applyProblemFilter = state.marketplaceFilters.onlyProblems && !isWildberries;
      const products = allProducts.filter((row) => !applyInStockFilter || Number(row.available || 0) > 0);
      const orders = allOrders.filter((row) => marketplaceDateInPeriod(row.shipment_date || row.created_at, periodMeta)).filter((row) => state.marketplaceFilters.orderStatus === "all" || String(row.status || "") === state.marketplaceFilters.orderStatus).filter((row) => !applyProblemFilter || !["delivering", "awaiting_packaging"].includes(String(row.status || "")));
      const runs = providerPayload.sync_runs || [];
      const supplies = isWildberries ? (payload.supplies || []).filter((row) => row.marketplace === "wildberries") : (payload.supplies || []).filter((row) => isAll || row.marketplace === "ozon");
      const wbSuppliesCapability = wbCapabilityStatuses.supplies || {};
      const wbSuppliesStatus = wbSuppliesCapability.status || (wbCapabilities.supplies ? "legacy" : "no_data");
      const wbSuppliesCurrent = wbSuppliesStatus === "available";
      const warehouseShipments = (payload.warehouse_shipments || []).filter((row) => isAll || row.marketplace === selectedProvider);
      const accounts = providerPayload.accounts || [];
      const account = accounts[0] || {};
      const wildberries = (payload.connectors || []).find((item) => item.marketplace === "wildberries") || {};
      const wildberriesConnected = Boolean((payload.wildberries || {}).configured || wildberries.configured);
      const providerName = isAll ? "маркетплейсов" : (isOzon ? "Ozon" : "Wildberries");
      const providerConfigured = isAll
        ? Boolean(payload.configured || wildberriesConnected)
        : (isOzon ? Boolean(payload.configured) : wildberriesConnected);
      const providerStatus = isAll
        ? `Ozon: ${payload.configured ? "подключён" : "не подключён"} · Wildberries: ${wildberriesConnected ? "подключён" : "не подключён"}`
        : (isOzon
          ? (providerConfigured ? `Подключён · ${account.account_name || "Основной аккаунт"}` : "Не настроен · добавьте ключи")
          : (providerConfigured ? `Подключён · ${account.account_name || "Основной Wildberries"}` : "Токен пока не задан"));
      const providerTitle = isAll ? "маркетплейсами" : providerName;
      const groups = marketplaceGroups(applyInStockFilter ? {...providerPayload, product_groups: []} : providerPayload, products);
      const qualityView = state.marketplaceView === "data-quality";
      const qualityActionBusy = isWildberries ? state.marketplaceData.loading : (state.marketplaceQuality.loading
        || state.marketplaceQuality.syncing
        || Boolean(state.marketplaceQuality.payload?.phase1a?.worker?.running));
      mainButton.hidden = false;
      mainButton.textContent = qualityView
        ? (qualityActionBusy ? "Синхронизация выполняется…" : (isWildberries ? "Синхронизировать Wildberries" : "Запустить PostgreSQL sync"))
        : (state.marketplaceData.loading ? "Синхронизация…" : `Синхронизировать ${isWildberries ? "Wildberries" : isAll ? "маркетплейсы" : "Ozon"}`);
      mainButton.disabled = qualityView ? qualityActionBusy : state.marketplaceData.loading;
      const errorNotice = state.marketplaceData.error ? `<div class="card field-card"><div class="task-note"><b>Ошибка маркетплейса</b><br>${escapeHtml(state.marketplaceData.error)}</div><div class="button-row"><button type="button" class="small-button" data-marketplace-action="refresh">Повторить</button></div></div>` : "";
      const notConfigured = !providerConfigured ? `<div class="card field-card"><div class="task-note"><b>${isAll ? "Маркетплейсы не подключены" : `${providerName} не подключён`}</b></div></div>` : "";
      const kpiUnavailable = (label, hint) => `<div class="card marketplace-v2-kpi unavailable" title="${escapeHtml(hint)}"><span>${escapeHtml(label)}</span><strong>—</strong><small>Нет данных от API</small></div>`;
      const kpiValue = (label, value, suffix, hint, view = "") => `${view ? `<button type="button" class="card marketplace-v2-kpi" data-marketplace-view="${view}">` : `<div class="card marketplace-v2-kpi">`}<span>${escapeHtml(label)}</span><strong>${escapeHtml(value)}<small>${escapeHtml(suffix)}</small></strong><small>${escapeHtml(hint)}</small>${view ? "</button>" : "</div>"}`;
      const groupMarketplaceStockText = (group) => isWildberries && !wbStocksUsable || group.available === null || group.available === undefined ? "—" : `${Number(group.available || 0)} шт.`;
      const productsBlock = groups.length ? `<div class="op-list marketplace-group-grid">${groups.map((group) => `<button type="button" class="card marketplace-clickable marketplace-group-card" data-marketplace-group="${escapeHtml(group.key)}"><div class="group-title"><span class="marketplace-product-heading">${marketplaceProductAvatar(group)}<span><b>${escapeHtml(group.name)}</b></span></span><span class="status-chip">›</span></div><div class="marketplace-group-meta"><span>${escapeHtml(group.products || 0)} поз.</span><span>${escapeHtml(group.articles || group.products || 0)} артикулов</span><span>${escapeHtml(providerName)}: ${escapeHtml(groupMarketplaceStockText(group))}</span><span>Производство: ${escapeHtml(marketplaceProductionStockText(group))}</span></div><div class="marketplace-group-meta"><span>Цена: ${marketplaceMoney(group.price_min)}${group.price_max != null && group.price_max !== group.price_min ? ` — ${marketplaceMoney(group.price_max)}` : ""}</span><span>Открыть группу ›</span></div></button>`).join("")}</div>` : itemEmpty("Товары ещё не загружены.");
      const warehouseOptions = Array.isArray(providerPayload.warehouses) ? providerPayload.warehouses : [{key:"fbo",name:"FBO — склады маркетплейса"},{key:"fbs",name:"FBS — собственный склад"}];
      const stockColors = [...new Set(products.map((row) => String(row.color || "").trim()).filter(Boolean))].sort((a, b) => a.localeCompare(b, "ru"));
      const stockSizes = [...new Set(products.map((row) => String(row.size || "").trim()).filter(Boolean))].sort((a, b) => a.localeCompare(b, "ru", {numeric: true, sensitivity: "base"}));
      const stocksBlock = products.length ? `<section class="marketplace-stock-section"><div class="marketplace-stock-filters"><label><span>Реальный склад ${escapeHtml(providerName)}</span><select data-stock-filter="warehouse" onchange="filterMarketplaceStocks(this)"><option value="all">Все склады ${escapeHtml(providerName)}</option>${warehouseOptions.map((warehouse) => `<option value="${escapeHtml(warehouse.key)}">${escapeHtml(warehouse.name)}</option>`).join("")}</select></label><label><span>Номенклатура</span><select data-stock-filter="product" onchange="filterMarketplaceStocks(this)"><option value="all">Вся номенклатура</option>${groups.map((group) => `<option value="${escapeHtml(group.key)}">${escapeHtml(group.name)}</option>`).join("")}</select></label><label><span>Цвет</span><select data-stock-filter="color" onchange="filterMarketplaceStocks(this)"><option value="all">Все цвета</option>${stockColors.map((color) => `<option value="${escapeHtml(color)}">${escapeHtml(color)}</option>`).join("")}</select></label><label><span>Размер</span><select data-stock-filter="size" onchange="filterMarketplaceStocks(this)"><option value="all">Все размеры</option>${stockSizes.map((size) => `<option value="${escapeHtml(size)}">${escapeHtml(size)}</option>`).join("")}</select></label><label><span>Критичность</span><select data-stock-filter="criticality" onchange="filterMarketplaceStocks(this)"><option value="all">Все состояния</option><option value="enough">Хватает · от 10 шт.</option><option value="low">Нужно пополнить · 1–9 шт.</option><option value="absent">Отсутствует · 0 шт.</option></select></label></div><div class="section-title"><b>Остатки по товарам</b><span data-stock-visible-count>${products.length}</span></div><div class="marketplace-stock-grid">${products.map((row) => { const stockMap = row.warehouse_stocks || {}; const total = Number(row.available || 0); const level = marketplaceStockLevel(total); const nonEmptyWarehouses = warehouseOptions.filter((warehouse) => Number(stockMap[warehouse.key] || 0) > 0); const encodedStockMap = escapeHtml(warehouseOptions.map((warehouse) => `${warehouse.key}:${Number(stockMap[warehouse.key] || 0)}`).join("|")); return `<button type="button" class="card marketplace-clickable marketplace-stock-card" data-marketplace-product-id="${escapeHtml(row.id)}" data-stock-product="${escapeHtml(row.group_key || "other")}" data-stock-color="${escapeHtml(String(row.color || ""))}" data-stock-size="${escapeHtml(String(row.size || ""))}" data-stock-total="${total}" data-stock-map="${encodedStockMap}">${marketplaceProductAvatar(row)}<span class="marketplace-stock-card-body"><b>${escapeHtml(row.name || `Товар ${providerName}`)}</b><small>${escapeHtml(row.group_name || "Прочие товары")} · ${escapeHtml(row.color || "Цвет не указан")} · ${escapeHtml(row.size || "Размер не указан")} · Артикул: ${escapeHtml(row.offer_id || "—")}</small><span class="marketplace-stock-breakdown">${nonEmptyWarehouses.slice(0, 3).map((warehouse) => `<span>${escapeHtml(warehouse.name)}: ${Number(stockMap[warehouse.key] || 0)} шт.</span>`).join("")}${nonEmptyWarehouses.length > 3 ? `<span>Ещё складов: ${nonEmptyWarehouses.length - 3}</span>` : ""}</span></span><span class="marketplace-stock-result"><b data-stock-quantity>${total} шт.</b><span data-stock-level class="status-chip marketplace-stock-level ${level.key}">${level.label}</span></span></button>`; }).join("")}</div><div class="marketplace-stock-empty">${itemEmpty("По выбранным фильтрам товаров нет.")}</div></section>` : itemEmpty("Остатки ещё не загружены.");
      const wbPeriodCapability = (name, fallback) => {
        const capability = wbCapabilityStatuses[name] && typeof wbCapabilityStatuses[name] === "object" ? wbCapabilityStatuses[name] : {};
        const status = capability.status || (fallback ? "legacy" : "no_data");
        const coverageStart = String(capability.coverage_start_date || "");
        const coverageEnd = String(capability.coverage_end_date || "");
        const hasCoverage = /^\\d{4}-\\d{2}-\\d{2}$/.test(coverageStart) && /^\\d{4}-\\d{2}-\\d{2}$/.test(coverageEnd);
        const selectedStart = periodMeta.startKey;
        const selectedEnd = periodMeta.endKey;
        return {
          status,
          coverageStart,
          coverageEnd,
          hasCoverage,
          covered: hasCoverage && selectedStart >= coverageStart && selectedEnd <= coverageEnd,
          usable: ["available", "partial", "legacy"].includes(status),
        };
      };
      const wbRowsInCoverage = (rows, coverage, dateKeys = ["date"]) => (Array.isArray(rows) ? rows : []).filter((row) => {
        const rowDate = String(dateKeys.map((key) => row?.[key]).find(Boolean) || "").slice(0, 10);
        if (!marketplaceDateInPeriod(rowDate, periodMeta)) return false;
        return !coverage.hasCoverage || (rowDate >= coverage.coverageStart && rowDate <= coverage.coverageEnd);
      });
      const wbOrdersCoverage = wbPeriodCapability("orders", wbCapabilities.orders);
      const wbFinanceCoverage = wbPeriodCapability("finance", wbCapabilities.finance);
      const wbSalesCoverage = wbPeriodCapability("sales", wbCapabilities.sales);
      const verifiedOrders = isWildberries ? wbRowsInCoverage(orders, wbOrdersCoverage, ["shipment_date", "created_at", "updated_at"]) : orders;
      const verifiedOrdersAvailable = !isWildberries || (wbOrdersCoverage.usable && (wbOrdersCoverage.covered || verifiedOrders.length > 0));
      const verifiedPeriodFinance = isWildberries ? wbRowsInCoverage(financeDaily, wbFinanceCoverage) : periodFinance;
      const verifiedPeriodRevenue = verifiedPeriodFinance.reduce((sum, row) => sum + Number(row.revenue || 0), 0);
      const verifiedPeriodNet = verifiedPeriodFinance.reduce((sum, row) => sum + Number(row.net || 0), 0);
      const verifiedReturnDays = isWildberries ? wbRowsInCoverage(analytics.returns_daily, wbSalesCoverage) : periodReturnDays;
      const verifiedReturnRecords = verifiedReturnDays.reduce((sum, row) => sum + Number(row.records || 0), 0);
      const verifiedReturnQuantity = verifiedReturnDays.reduce((sum, row) => sum + Number(row.quantity || 0), 0);
      const wbFunnelCoverage = wbPeriodCapability("funnel", wbCapabilities.sales_funnel);
      const wbFunnelDaily = wbRowsInCoverage(analytics.sales_funnel_daily, wbFunnelCoverage);
      const wbAdvertising = analytics.advertising || {};
      const wbAdvertisingCoverage = wbPeriodCapability("advertising", wbCapabilities.advertising);
      const wbAdvertisingDaily = wbRowsInCoverage(wbAdvertising.daily, wbAdvertisingCoverage);
      const wbAdSummaryBase = wbAdvertising.summary || {};
      const wbAdSummary = {
        ...wbAdSummaryBase,
        views: wbAdvertisingDaily.reduce((sum, row) => sum + Number(row.views || 0), 0),
        clicks: wbAdvertisingDaily.reduce((sum, row) => sum + Number(row.clicks || 0), 0),
        spend: wbAdvertisingDaily.reduce((sum, row) => sum + Number(row.spend || 0), 0),
        orders: wbAdvertisingDaily.reduce((sum, row) => sum + Number(row.orders || 0), 0),
        revenue: wbAdvertisingDaily.reduce((sum, row) => sum + Number(row.revenue || 0), 0),
      };
      wbAdSummary.ctr = wbAdSummary.views ? wbAdSummary.clicks * 100 / wbAdSummary.views : 0;
      wbAdSummary.roas = wbAdSummary.spend ? wbAdSummary.revenue / wbAdSummary.spend : 0;
      const wbFunnelChart = !wbFunnelCoverage.usable
        ? marketplaceUnavailable("Воронка продаж")
        : wbFunnelDaily.length
          ? marketplaceLineChart(wbFunnelDaily, "order_sum", null)
          : wbFunnelCoverage.covered
            ? `<div class="marketplace-chart-empty"><b>За выбранный период заказов нет</b><span>Источник Wildberries доступен; в выбранном диапазоне подтверждён пустой ряд.</span></div>`
            : `<div class="marketplace-chart-empty"><b>Период покрыт частично</b><span>WB подтвердил только ${escapeHtml(wbFunnelCoverage.coverageStart || "часть периода")} — ${escapeHtml(wbFunnelCoverage.coverageEnd || "текущую дату")}.</span></div>`;
      const wbAdvertisingChart = !wbAdvertisingCoverage.usable
        ? marketplaceUnavailable("Расходы на рекламу")
        : wbAdvertisingDaily.length
          ? marketplaceLineChart(wbAdvertisingDaily, "spend", null)
          : wbAdvertisingCoverage.covered
            ? `<div class="marketplace-chart-empty"><b>За выбранный период расходов нет</b><span>Источник рекламы доступен; в выбранном диапазоне подтверждён пустой ряд.</span></div>`
            : `<div class="marketplace-chart-empty"><b>Период рекламы не подтверждён</b><span>Данные вне подтверждённого окна не подменяются нулём.</span></div>`;
      const wbCoverageNotice = (!wbFunnelCoverage.covered && wbFunnelCoverage.usable) || (!wbAdvertisingCoverage.covered && wbAdvertisingCoverage.usable)
        ? `<div class="analytics-overview-notice warn"><div><b>Графики покрывают выбранный период не полностью</b><span>Показаны только даты внутри подтверждённых API-окон; сохранённые старые строки за их пределами скрыты.</span></div></div>`
        : "";
      const wbAnalyticsBlock = `
        <div class="marketplace-v2-kpis">
          ${wbCatalogUsable ? kpiValue("Карточки", summary.products || 0, " шт.", `Каталог Wildberries${wbCatalogStatus === "legacy" ? " · прежний snapshot" : ""}`, "products") : kpiUnavailable("Карточки", "Каталог Wildberries недоступен")}
          ${wbStocksUsable ? kpiValue("Остатки", products.reduce((sum,row) => sum + Number(row.available || 0), 0), " шт.", `По складам WB${wbStocksStatus === "legacy" ? " · прежний snapshot" : ""}`, "stocks") : kpiUnavailable("Остатки", "Для API остатков нужны права токена Wildberries")}
          ${wbOrdersCoverage.usable && (wbOrdersCoverage.covered || verifiedOrders.length) ? kpiValue("Заказы", verifiedOrders.length, " шт.", `${periodMeta.label}${wbOrdersCoverage.covered ? "" : " · частичное покрытие"}`, "orders") : kpiUnavailable("Заказы", "Выбранный период не покрыт API заказов Wildberries")}
          ${wbCapabilities.advertising ? kpiValue("Реклама", wbAdSummary.campaigns || 0, " камп.", `${wbAdSummary.active_campaigns || 0} активных`) : kpiUnavailable("Реклама", "API рекламы Wildberries недоступен")}
          ${wbAdvertisingCoverage.usable && (wbAdvertisingCoverage.covered || wbAdvertisingDaily.length) ? kpiValue("Расходы", marketplaceMoney(wbAdSummary.spend || 0), "", `${periodMeta.label}${wbAdvertisingCoverage.covered ? "" : " · частичное покрытие"} · CTR ${Number(wbAdSummary.ctr || 0).toFixed(2)}%`) : kpiUnavailable("Расходы", "Выбранный период не покрыт API рекламы Wildberries")}
          ${wbAdvertisingCoverage.usable && (wbAdvertisingCoverage.covered || wbAdvertisingDaily.length) ? kpiValue("ROAS", Number(wbAdSummary.roas || 0).toFixed(2), "", `${wbAdSummary.orders || 0} заказов из рекламы${wbAdvertisingCoverage.covered ? "" : " · частично"}`) : kpiUnavailable("ROAS", "Выбранный период не покрыт API рекламы Wildberries")}
        </div>
        ${wbCoverageNotice}
        <div class="marketplace-wide-grid">
          <section class="card marketplace-chart-panel"><div class="marketplace-chart-head"><div class="marketplace-chart-summary"><span>Воронка продаж</span><strong>${wbFunnelCoverage.usable && (wbFunnelCoverage.covered || wbFunnelDaily.length) ? marketplaceMoney(wbFunnelDaily.reduce((sum,row) => sum + Number(row.order_sum || 0), 0)) : "—"}</strong><small>${escapeHtml(periodMeta.label)}${wbFunnelCoverage.covered ? "" : " · частичное покрытие"} · заказы по данным аналитики WB</small></div></div><div class="marketplace-chart-canvas">${wbFunnelChart}</div></section>
          <section class="card marketplace-chart-panel"><div class="marketplace-chart-head"><div class="marketplace-chart-summary"><span>Расходы на рекламу</span><strong>${wbAdvertisingCoverage.usable && (wbAdvertisingCoverage.covered || wbAdvertisingDaily.length) ? marketplaceMoney(wbAdSummary.spend || 0) : "—"}</strong><small>${escapeHtml(periodMeta.label)}${wbAdvertisingCoverage.covered ? "" : " · частичное покрытие"} · ${wbAdSummary.views || 0} показов · ${wbAdSummary.clicks || 0} кликов</small></div></div><div class="marketplace-chart-canvas">${wbAdvertisingChart}</div></section>
        </div>
        <div class="card field-card"><div class="section-title"><b>Рекламные кампании</b><span>${(wbAdvertising.campaigns || []).length}</span></div>${(wbAdvertising.campaigns || []).length ? `<div class="marketplace-table-scroll"><table class="marketplace-table"><thead><tr><th>Кампания</th><th>Статус</th><th>Оплата</th><th>Бюджет в день</th></tr></thead><tbody>${wbAdvertising.campaigns.map((row) => `<tr><td>${escapeHtml(row.name || row.campaign_id)}</td><td>${escapeHtml(row.status || "—")}</td><td>${escapeHtml(row.payment_type || "—")}</td><td>${marketplaceMoney(row.daily_budget || 0)}</td></tr>`).join("")}</tbody></table></div>` : itemEmpty("Кампании появятся после синхронизации.")}</div>
        <div class="card field-card"><div class="section-title"><b>Доступность данных WB</b><span>${escapeHtml(account.last_sync_at || "нет данных")}</span></div><div class="marketplace-mini-list">${Object.entries(analytics.capabilities || {}).map(([key,value]) => { const capabilityKey = key === "sales_funnel" ? "funnel" : key; const status = wbCapabilityStatuses[capabilityKey]?.status || (value ? "available" : "no_data"); const statusLabel = {available:"Подключено",partial:"Доступно частично",permission_required:"Нужны права токена",unauthorized:"Токен отклонён",payment_required:"Нужен платный доступ",error:"Ошибка источника",unavailable:"Временно недоступно",no_data:"Нет подтверждённых данных"}[status] || status; return `<div class="marketplace-mini-row"><span>${escapeHtml({catalog:"Товары и карточки",prices:"Цены и скидки",orders:"Заказы",sales_funnel:"Воронка продаж",advertising:"Реклама",stocks:"Остатки по складам",finance:"Финансы"}[key] || key)}</span><b>${escapeHtml(statusLabel)}</b></div>`; }).join("")}</div></div>
      `;
      const analyticsBlock = isWildberries ? wbAnalyticsBlock : `
        <div class="kpi-grid">
          <div class="card kpi"><div class="kpi-top"><span>Карточки товаров</span><span class="kpi-ico">▤</span></div><strong>${escapeHtml(summary.products || 0)}</strong><span>Загружено из ${providerName}</span></div>
          <div class="card kpi"><div class="kpi-top"><span>Строк остатков</span><span class="kpi-ico">▦</span></div><strong>${escapeHtml(summary.stock_rows || 0)}</strong><span>FBO и FBS</span></div>
          <div class="card kpi"><div class="kpi-top"><span>Открытые отгрузки</span><span class="kpi-ico">↑</span></div><strong>${escapeHtml(summary.open_orders || 0)}</strong><span>Требуют контроля</span></div>
        </div>
        <div class="card field-card"><div class="section-title"><b>Состояние синхронизации</b><span>${escapeHtml(account.last_sync_at || "нет данных")}</span></div></div>
      `;
      const ordersBlock = verifiedOrdersAvailable && verifiedOrders.length ? `<div class="op-list">${verifiedOrders.map((row) => `<button type="button" class="card report-row marketplace-clickable" data-marketplace-order-id="${escapeHtml(row.id)}"><div><b>${escapeHtml(row.posting_number || row.external_order_id)}</b><span>Заказ: ${escapeHtml(row.external_order_id)}<br>${escapeHtml(row.shipment_date || "Срок не указан")}</span></div><span class="status-chip ${row.status && !["delivering", "awaiting_packaging"].includes(row.status) ? "warn" : "gray"}">${escapeHtml(row.status || "Без статуса")} ›</span></button>`).join("")}</div>` : itemEmpty(isWildberries && !verifiedOrdersAvailable ? "Выбранный период или источник заказов WB не подтверждён." : "За выбранный период отгрузок нет.");
      const supplyStatusLabels = {PLANNED:"Актуальная",WAITING_RESERVATION:"Ожидает резерв",SHORTAGE:"Дефицит",READY_TO_PICK:"Готова к отбору",PICKING:"Отбор",PICKED:"Отобрана",PACKING:"Упаковка",READY_TO_HANDOVER:"Готова к передаче",SHIPPED_FROM_PRODUCTION:"Отгружено на производстве"};
      const suppliesBlock = supplies.length
        ? `${isWildberries && !wbSuppliesCurrent ? `<div class="analytics-overview-notice warn"><div><b>Показана сохранённая история поставок WB</b><span>${escapeHtml(wbSuppliesCapability.safe_message || "Текущий источник поставок не подтверждён; создание складских заданий отключено.")}</span></div></div>` : ""}<div class="op-list">${supplies.map((row) => `<div class="card report-row marketplace-supply-card"><div><b>${escapeHtml(row.marketplace === "wildberries" ? "Wildberries" : "Ozon")} · ${escapeHtml(row.external_supply_id)}</b><span>${escapeHtml(row.destination_name || "Направление не указано")} · ${escapeHtml(row.item_count || 0)} поз. · ${escapeHtml(row.total_quantity || 0)} шт.${row.unmatched_count ? `<br><span class="critical-text">Не сопоставлено: ${escapeHtml(row.unmatched_count)}</span>` : ""}</span></div><div class="supply-actions"><span class="status-chip ${["SHORTAGE","SYNC_ERROR"].includes(row.canonical_status) ? "warn" : ""}">${escapeHtml(supplyStatusLabels[row.canonical_status] || row.canonical_status)}</span>${row.warehouse_shipment_id ? `<span class="status-chip">${escapeHtml(row.warehouse_shipment_number || `MP-${String(row.warehouse_shipment_id).padStart(6, "0")}`)}</span>` : (isWildberries && !wbSuppliesCurrent ? `<span class="status-chip warn">только история</span>` : (!row.is_actionable ? `<span class="status-chip warn">Недоступна для задания</span>` : (Number(row.item_count || 0) <= 0 ? `<span class="status-chip warn">Нет состава</span>` : (!row.unmatched_count ? `<button type="button" class="small-button" data-marketplace-supply-create="${escapeHtml(row.id)}">Создать задание складу</button>` : `<span class="status-chip warn">Нужно сопоставление</span>`))))}</div></div>`).join("")}</div>`
        : itemEmpty(isWildberries && wbSuppliesCurrent ? "Источник поставок WB доступен; активных поставок нет." : "Актуальных поставок нет.");
      const warehouseShipmentsBlock = warehouseShipments.length ? `<div class="op-list">${warehouseShipments.map((row) => `<div class="card report-row"><div><b>${escapeHtml(row.number)}</b><span>${escapeHtml(row.marketplace === "wildberries" ? "Wildberries" : "Ozon")} · ${escapeHtml(row.destination_name || "Направление не указано")}<br>${escapeHtml(row.total_quantity || 0)} шт. · резерв ${escapeHtml(row.reserved_quantity || 0)} · отобрано ${escapeHtml(row.picked_quantity || 0)}</span></div><span class="status-chip">${escapeHtml(row.status)}</span></div>`).join("")}</div>` : itemEmpty("Внутренних складских отгрузок пока нет.");
      const topProducts = isWildberries && !wbStocksUsable ? [] : [...products].sort((a, b) => Number(b.available || 0) - Number(a.available || 0)).slice(0, 5);
      const topProductsBlock = topProducts.length ? `<div class="marketplace-mini-list">${topProducts.map((row) => `<div class="marketplace-mini-row"><span>${escapeHtml(row.name || row.offer_id || "Товар")}</span><b>${escapeHtml(row.available == null ? 0 : row.available)} шт.</b></div>`).join("")}</div>` : itemEmpty("После синхронизации здесь появятся товары-лидеры.");
      const recentOrdersBlock = verifiedOrdersAvailable && verifiedOrders.length ? `<table class="marketplace-table"><thead><tr><th>Заказ</th><th>Товар</th><th>Статус</th></tr></thead><tbody>${verifiedOrders.slice(0, 5).map((row) => `<tr><td>${escapeHtml(row.posting_number || row.external_order_id || "—")}</td><td>${escapeHtml(row.external_order_id || "—")}</td><td>${escapeHtml(row.status || "—")}</td></tr>`).join("")}</tbody></table>` : itemEmpty(isWildberries && !verifiedOrdersAvailable ? "Период или источник заказов не подтверждён API Wildberries." : "За выбранный период заказов нет.");
      const notificationsBlock = (payload.sync_events || []).slice(0, 4).map((row) => `<div class="marketplace-notice"><i class="marketplace-notice-dot"></i><div><b>${escapeHtml(row.marketplace === "wildberries" ? "Wildberries" : "Ozon")} · ${escapeHtml(row.event_type || "Событие")}</b><span>${escapeHtml(row.message || "Обновление данных")}</span></div></div>`).join("") || `<div class="marketplace-notice"><i class="marketplace-notice-dot"></i><div><b>Система готова</b><span>Уведомления о синхронизации и поставках появятся здесь.</span></div></div>`;
      const chartBars = (values, wb = false) => { const max = Math.max(1, ...values.map((value) => Number(value || 0))); return values.map((value) => `<i class="marketplace-chart-bar ${wb ? "wb" : ""}" style="--bar-height:${Math.max(8, (Number(value || 0) / max) * 100)}%" title="${escapeHtml(value || 0)}"></i>`).join(""); };
      const providerDashboard = (key, label, configured, wb = false) => {
        const providerProducts = wb ? [] : products;
        const providerOrders = wb ? [] : orders;
        const providerSummary = wb ? {} : summary;
        const chartValues = wb ? [0, 0, 0, 0, 0] : [providerSummary.products || 0, providerSummary.stock_rows || 0, providerSummary.open_orders || 0, supplies.length || 0, warehouseShipments.length || 0];
        return `<section class="marketplace-provider-dashboard ${wb ? "wb-panel" : "ozon-panel"}"><div class="provider-heading"><div><h3>${label}</h3><span>${configured ? "Подключён · только чтение" : "Не подключён"}</span></div><span class="status-chip">${configured ? "готов" : "настроить"}</span></div><div class="marketplace-dashboard-kpis"><div class="marketplace-dashboard-kpi"><span>Заказы</span><strong>${escapeHtml(providerSummary.open_orders || 0)}</strong><small>открыто</small></div><div class="marketplace-dashboard-kpi"><span>Товары</span><strong>${escapeHtml(providerSummary.products || 0)}</strong><small>позиций</small></div><div class="marketplace-dashboard-kpi"><span>Остатки</span><strong>${escapeHtml(providerSummary.stock_rows || 0)}</strong><small>строк</small></div></div><div class="marketplace-dashboard-lower"><div><div class="section-title"><b>Показатели</b><span>из синхронизации</span></div><div class="marketplace-chart">${configured ? chartBars(chartValues) : itemEmpty("Нет данных")}</div></div><div><div class="section-title"><b>Топ товары</b><span>${providerProducts.length}</span></div>${wb ? itemEmpty("Нет синхронизированных товаров.") : topProductsBlock}</div></div></section>`;
      };
      const runsBlock = runs.length ? `<div class="op-list">${runs.map((row) => `<button type="button" class="card report-row marketplace-clickable" data-marketplace-sync-id="${escapeHtml(row.id)}"><div><b>${escapeHtml(row.started_at || "Синхронизация")}</b><span>Товары ${escapeHtml(row.products_count)} · цены ${escapeHtml(row.prices_count)} · остатки ${escapeHtml(row.stocks_count)} · отгрузки ${escapeHtml(row.orders_count)}${row.error_message ? `<br>${escapeHtml(row.error_message)}` : ""}</span></div><span class="status-chip ${row.status === "success" ? "" : "warn"}">${escapeHtml(row.status)} ›</span></button>`).join("")}</div>` : itemEmpty("Синхронизаций ещё не было.");
      const sourceLabel = isAll ? "Ozon и Wildberries" : (isOzon ? "Ozon" : "Wildberries");
      const salesChart = verifiedPeriodFinance.length ? `${marketplaceLineChart(verifiedPeriodFinance)}<div class="marketplace-chart-legend"><span><i></i>Начислено</span><span><i class="secondary"></i>Итог после удержаний</span></div><div class="marketplace-chart-caption"><span>Начислено ${marketplaceMoney(verifiedPeriodRevenue)}</span><span>Итог ${marketplaceMoney(verifiedPeriodNet)}</span></div>` : `<div class="marketplace-chart-empty"><b>${isWildberries && !wbFinanceCoverage.covered ? "Период финансов не подтверждён" : "За период начислений нет"}</b><span>${isWildberries && !wbFinanceCoverage.covered ? "Старые строки вне фактического API-окна скрыты." : `Источник доступен, но операций ${providerName} в диапазоне нет.`}</span></div>`;
      const chartMetric = state.marketplaceChartMetric === "net" ? "net" : "revenue";
      const chartMetricTitle = chartMetric === "net" ? "После удержаний" : "Начислено";
      const chartMetricTotal = chartMetric === "net" ? verifiedPeriodNet : verifiedPeriodRevenue;
      const financeConfirmed = isWildberries ? wbFinanceCoverage.usable && wbFinanceCoverage.covered : analytics.finance_available === true;
      const financePartiallyUsable = isWildberries && wbFinanceCoverage.usable && verifiedPeriodFinance.length > 0;
      const overviewFinanceChart = verifiedPeriodFinance.length && (financeConfirmed || financePartiallyUsable)
        ? marketplaceLineChart(verifiedPeriodFinance, chartMetric, null)
        : financeConfirmed
          ? `<div class="marketplace-chart-empty"><b>За выбранный период операций нет</b><span>Финансовый источник доступен; в выбранном диапазоне подтверждён пустой ряд.</span></div>`
          : `<div class="marketplace-chart-empty"><b>Финансовая динамика недоступна</b><span>Синхронизация финансов ${escapeHtml(providerName)} не подтверждена.</span></div>`;
      const revenueKpi = financeConfirmed || financePartiallyUsable ? kpiValue("Начисления", marketplaceMoney(verifiedPeriodRevenue), "", `Итог после удержаний: ${marketplaceMoney(verifiedPeriodNet)}${financeConfirmed ? "" : " · частичное покрытие"}`, "finance") : kpiUnavailable("Начисления", "Выбранный период не покрыт финансовой выгрузкой");
      const returnsConfirmed = isWildberries ? wbSalesCoverage.usable && wbSalesCoverage.covered : analytics.returns_available;
      const returnsPartiallyUsable = isWildberries && wbSalesCoverage.usable && verifiedReturnDays.length > 0;
      const returnsKpi = returnsConfirmed || returnsPartiallyUsable ? kpiValue("Возвраты", verifiedReturnQuantity, " шт.", `${verifiedReturnRecords} записей за период${returnsConfirmed ? "" : " · частично"}`, "reviews") : kpiUnavailable("Возвраты", "Выбранный период не покрыт выгрузкой возвратов");
      const ratingCurrent = isWildberries ? wbFeedbacksCurrent && effectiveRating != null : (analytics.rating_available || effectiveRating != null);
      const ratingKpi = ratingCurrent ? kpiValue("Рейтинг магазина", Number(effectiveRating).toFixed(2), "", `Актуальная сводка ${providerName}`, "reviews") : kpiUnavailable("Рейтинг магазина", isWildberries ? "Текущий API отзывов WB не подтверждён" : "Рейтинг ещё не синхронизирован");
      const overviewOrdersKpi = isWildberries
        ? (wbOrdersCoverage.usable && (wbOrdersCoverage.covered || verifiedOrders.length) ? kpiValue("Заказы", verifiedOrders.length, " шт.", `${periodMeta.label}${wbOrdersCoverage.covered ? "" : " · частично"}`, "orders") : kpiUnavailable("Заказы", "Выбранный период не покрыт API заказов WB"))
        : kpiValue("Заказы", orders.length, " шт.", `${sourceLabel} · выбранный период`, "orders");
      const overviewProductsKpi = isWildberries
        ? (wbCatalogUsable ? kpiValue("Товары в продаже", products.length, " шт.", `Wildberries${wbCatalogStatus === "legacy" ? " · прежний snapshot" : " · подтверждено"}`, "products") : kpiUnavailable("Товары в продаже", "Каталог WB сейчас недоступен"))
        : kpiValue("Товары в продаже", products.length, " шт.", `${sourceLabel} · синхронизировано`, "products");
      const overviewStockKpi = isWildberries
        ? (wbStocksUsable ? kpiValue("Остатки на складах", products.reduce((sum, row) => sum + Number(row.available || 0), 0), " шт.", `Wildberries${wbStocksStatus === "legacy" ? " · прежний snapshot" : " · подтверждено"}`, "stocks") : kpiUnavailable("Остатки на складах", "API остатков WB сейчас недоступен"))
        : kpiValue("Остатки на складах", products.reduce((sum, row) => sum + Number(row.available || 0), 0), " шт.", isAll ? "Сумма доступных остатков" : sourceLabel, "stocks");
      const calendarMax = marketplaceLocalIsoDate();
      const overviewBlock = `
        <div class="marketplace-filter-bar"><label><span>Период</span><select id="marketplacePeriod"><option value="today" ${state.marketplacePeriod === "today" ? "selected" : ""}>Сегодня</option><option value="yesterday" ${state.marketplacePeriod === "yesterday" ? "selected" : ""}>Вчера</option><option value="7d" ${state.marketplacePeriod === "7d" ? "selected" : ""}>Последние 7 дней</option><option value="30d" ${state.marketplacePeriod === "30d" ? "selected" : ""}>Последние 30 дней</option><option value="month" ${state.marketplacePeriod === "month" ? "selected" : ""}>Текущий месяц</option><option value="previous-month" ${state.marketplacePeriod === "previous-month" ? "selected" : ""}>Предыдущий месяц</option><option value="custom" ${state.marketplacePeriod === "custom" ? "selected" : ""}>Произвольный диапазон</option></select></label><div class="marketplace-date-range"><label><span>С даты</span><input type="date" max="${calendarMax}" value="${escapeHtml(state.marketplaceDateFrom)}" onchange="state.marketplaceDateFrom=this.value;if(state.marketplaceDateFrom&&state.marketplaceDateTo){state.marketplacePeriod='custom';syncMarketplaceLocation();renderMarketplaces()}"></label><label><span>По дату</span><input type="date" max="${calendarMax}" value="${escapeHtml(state.marketplaceDateTo)}" onchange="state.marketplaceDateTo=this.value;if(state.marketplaceDateFrom&&state.marketplaceDateTo){state.marketplacePeriod='custom';syncMarketplaceLocation();renderMarketplaces()}"></label></div><div class="marketplace-period-label">${escapeHtml(periodMeta.label)}</div><button type="button" class="small-button secondary" data-marketplace-filter-action="toggle">Фильтры${state.marketplaceFilters.onlyProblems || state.marketplaceFilters.inStockOnly || state.marketplaceFilters.orderStatus !== "all" ? " · активны" : ""}</button></div>
        ${state.marketplaceFiltersOpen ? `<div class="card marketplace-filter-panel"><div class="form-grid"><div class="field"><label>Статус заказа</label><select id="marketplaceOrderStatus"><option value="all">Все статусы</option>${[...new Set(allOrders.map((row) => String(row.status || "")).filter(Boolean))].map((status) => `<option value="${escapeHtml(status)}" ${state.marketplaceFilters.orderStatus === status ? "selected" : ""}>${escapeHtml(status)}</option>`).join("")}</select></div><label class="marketplace-check"><input id="marketplaceInStockOnly" type="checkbox" ${state.marketplaceFilters.inStockOnly ? "checked" : ""} ${isWildberries && !wbStocksUsable ? "disabled" : ""}> Только товары в наличии${isWildberries && !wbStocksUsable ? " · остатки не подтверждены" : ""}</label><label class="marketplace-check"><input id="marketplaceOnlyProblems" type="checkbox" ${state.marketplaceFilters.onlyProblems ? "checked" : ""} ${isWildberries ? "disabled" : ""}> ${isWildberries ? "Проблемные статусы WB пока не классифицированы" : "Только проблемные позиции"}</label></div><div class="button-row"><button type="button" class="small-button" data-marketplace-filter-action="apply">Применить</button><button type="button" class="small-button secondary" data-marketplace-filter-action="reset">Сбросить</button><button type="button" class="small-button secondary" data-marketplace-filter-action="cancel">Отмена</button></div></div>` : ""}
        <div class="marketplace-v2-kpis">${overviewOrdersKpi}${revenueKpi}${overviewProductsKpi}${returnsKpi}${isAll ? `${overviewStockKpi}${kpiUnavailable("Упущенная выручка", "Расчёт упущенной выручки требует данных о спросе")}` : `${ratingKpi}${overviewStockKpi}`}</div>
        <section class="card marketplace-chart-panel"><div class="marketplace-chart-head"><div class="marketplace-chart-summary"><span>${escapeHtml(chartMetricTitle)}</span><strong>${financeConfirmed || financePartiallyUsable ? marketplaceMoney(chartMetricTotal) : "—"}</strong><small>${escapeHtml(periodMeta.label)} · ${financeConfirmed || financePartiallyUsable ? `${escapeHtml(verifiedPeriodFinance.length)} дней с операциями${financeConfirmed ? "" : " · частично"}` : "источник или период недоступен"}</small></div><div class="marketplace-chart-switch" aria-label="Показатель графика"><button type="button" class="${chartMetric === "revenue" ? "active" : ""}" onclick="state.marketplaceChartMetric='revenue';renderMarketplaces()">Начислено</button><button type="button" class="${chartMetric === "net" ? "active" : ""}" onclick="state.marketplaceChartMetric='net';renderMarketplaces()">После удержаний</button></div></div><div class="marketplace-chart-canvas">${overviewFinanceChart}</div><div class="marketplace-chart-note">Наведите, коснитесь или выберите точку с клавиатуры, чтобы увидеть дату и сумму. Период выбирается над графиком.</div></section>
        <div class="marketplace-wide-grid"><div class="card field-card"><div class="section-title"><b>Последние заказы</b><button type="button" class="small-button secondary" data-marketplace-view="orders">Все заказы ›</button></div>${recentOrdersBlock}</div><div class="card field-card"><div class="section-title"><b>Уведомления</b><span>${(payload.sync_events || []).length}</span></div>${notificationsBlock}</div></div>
        <section class="card field-card marketplace-product-detail"><div class="section-title"><b>Детализация по товарам</b><button type="button" class="small-button secondary" data-marketplace-view="products">Все товары ›</button></div>${(!isWildberries || wbCatalogUsable) && products.length ? `<div class="marketplace-table-scroll"><table class="marketplace-table"><thead><tr><th>Товар</th><th>Маркетплейс</th><th>Артикул</th><th>В продаже</th><th>Остаток</th></tr></thead><tbody>${products.slice(0, 12).map((row) => `<tr><td><span class="marketplace-table-product">${marketplaceProductAvatar(row, true)}<span><strong>${escapeHtml(row.name || "Без названия")}</strong></span></span></td><td><span class="marketplace-source ${isWildberries ? "wildberries" : "ozon"}">${isWildberries ? "Wildberries" : "Ozon"}</span></td><td>${escapeHtml(row.offer_id || "—")}</td><td>${!isWildberries || wbStocksUsable ? (Number(row.available || 0) > 0 ? "Да" : "Нет") : "—"}</td><td>${!isWildberries || wbStocksUsable ? `${escapeHtml(row.available || 0)} шт.` : "—"}</td></tr>`).join("")}</tbody></table></div>` : itemEmpty(isWildberries && !wbCatalogUsable ? "Текущий каталог Wildberries не подтверждён." : "Товары появятся после синхронизации выбранной площадки.")}</section>
        <section class="card field-card marketplace-sales-detail"><div class="section-title"><b>Аналитика продаж</b><button type="button" class="small-button secondary" data-workspace="analytics">Открыть общий отчёт ›</button></div>${salesChart}</section>
        <div class="marketplace-overview-grid"><div class="card field-card"><div class="section-title"><b>Поставки маркетплейсов</b><button type="button" class="small-button secondary" data-marketplace-view="supplies">Открыть ›</button></div>${suppliesBlock}</div><div class="card field-card"><div class="section-title"><b>Задания складу</b><button type="button" class="small-button secondary" data-marketplace-view="warehouse-shipments">Открыть ›</button></div>${warehouseShipmentsBlock}</div></div>`;
      const financeTableRows = isWildberries ? verifiedPeriodFinance : financeDaily;
      const financeBlock = financeTableRows.length && (financeConfirmed || financePartiallyUsable || !isWildberries) ? `<div class="card field-card"><div class="section-title"><b>Начисления ${escapeHtml(providerName)} по дням</b><span>${financeTableRows.length} дней${isWildberries && !financeConfirmed ? " · частично" : ""}</span></div><div class="marketplace-table-scroll"><table class="marketplace-table"><thead><tr><th>Дата</th><th>Положительные начисления</th><th>Итог после удержаний</th><th>Операций</th></tr></thead><tbody>${[...financeTableRows].reverse().map((row) => `<tr><td>${escapeHtml(row.date)}</td><td>${marketplaceMoney(row.revenue || 0)}</td><td>${marketplaceMoney(row.net || 0)}</td><td>${escapeHtml(row.records || 0)}</td></tr>`).join("")}</tbody></table></div></div>` : itemEmpty(financeConfirmed ? "Финансовый источник доступен; операций в выбранном диапазоне нет." : "Финансовый источник или выбранный период не подтверждён.");
      const reviewsRating = isWildberries ? wbHistoricalRating : effectiveRating;
      const reviewsBlock = `<div class="marketplace-wide-grid"><div class="card field-card"><div class="section-title"><b>Рейтинг ${escapeHtml(providerName)}</b><span>${isWildberries && !wbFeedbacksCurrent ? "сохранённая история" : reviewsRating != null ? "актуально" : "нет данных"}</span></div><div class="marketplace-empty-metric"><b>${reviewsRating == null ? "—" : Number(reviewsRating).toFixed(2)}</b><span>${isWildberries ? `${escapeHtml(wbReviewSummary.total || 0)} отзывов · без ответа ${escapeHtml(wbReviewSummary.unanswered || 0)}${wbFeedbacksCurrent ? "" : " · не подтверждено текущим API"}` : "Актуальная сводка рейтинга магазина"}</span></div></div>${isWildberries ? `<div class="card field-card"><div class="section-title"><b>Отзывы покупателей</b><span>${wbReviews.length}</span></div>${!wbFeedbacksCurrent && wbReviews.length ? `<div class="analytics-overview-notice warn"><div><b>Отзывы показаны из сохранённой истории</b><span>${escapeHtml(wbFeedbacksCapability.safe_message || "Текущий API отзывов WB недоступен.")}</span></div></div>` : ""}${wbReviews.length ? `<div class="op-list">${wbReviews.map((row) => `<div class="report-row"><div><b>${escapeHtml(row.product_name || `Артикул WB ${row.nm_id || "—"}`)}</b><span>${escapeHtml(row.text || "Отзыв без текста")}<br>${escapeHtml(row.created_at || "дата не указана")}${row.answer_text ? ` · ответ продавца: ${escapeHtml(row.answer_text)}` : ""}</span></div><span class="status-chip ${row.answered ? "gray" : "warn"}">★ ${escapeHtml(row.rating || "—")}</span></div>`).join("")}</div>` : itemEmpty(wbFeedbacksCurrent ? "Источник отзывов доступен; отзывов нет." : "Отзывы ещё не подтверждены.")}</div>` : ""}<div class="card field-card"><div class="section-title"><b>Возвраты</b><span>${allReturns.length}</span></div>${allReturns.length ? `<div class="op-list">${allReturns.slice(0, 100).map((row) => `<div class="report-row"><div><b>${escapeHtml(row.product_name || row.posting_number || "Возврат")}</b><span>${escapeHtml(row.scheme || providerName)} · ${escapeHtml(row.status || "статус не указан")} · ${escapeHtml(row.returned_at || "дата не указана")}</span></div><span class="status-chip gray">${escapeHtml(row.quantity || 1)} шт.</span></div>`).join("")}</div>` : itemEmpty("Возвратов не найдено.")}</div></div>`;
      const qualityEnvelope = state.marketplaceQuality.payload || {};
      const quality = qualityEnvelope.phase1a || {};
      const qualityDatasets = Array.isArray(quality.datasets) ? quality.datasets : [];
      const qualityCapabilities = Array.isArray(quality.capabilities) ? quality.capabilities : [];
      const ozonRolesCapability = qualityCapabilities.find((row) => row.capability === "roles") || {};
      const ozonRolesDetails = ozonRolesCapability.details_json && typeof ozonRolesCapability.details_json === "object" ? ozonRolesCapability.details_json : {};
      const ozonRoleNames = Array.isArray(ozonRolesDetails.role_names) ? ozonRolesDetails.role_names : [];
      const ozonMethodPaths = Array.isArray(ozonRolesDetails.method_paths) ? ozonRolesDetails.method_paths : [];
      const qualityTotals = quality.totals || {};
      const qualityProductsEnvelope = state.marketplaceQuality.products || {};
      const qualityStateLabel = {disabled:"выключен",unavailable:"недоступен",no_data:"нет данных",ready:"готов",attention:"нужна проверка",success:"успешно",partial:"частично",error:"ошибка",failed:"ошибка",running:"выполняется",stale:"устарело",fresh:"актуально",unknown:"неизвестно",zero:"реальный ноль",value:"есть данные"};
      const qualityDatasetLabel = {catalog:"Каталог",prices:"Цены",stocks:"Остатки",orders:"Заказы",returns:"Возвраты",finance:"Финансы",rating:"Рейтинг",supplies:"FBO-поставки"};
      const qualityChipClass = (value) => ["success","fresh","ready","available","value","zero"].includes(String(value || "")) ? "" : (["disabled","no_data","unknown"].includes(String(value || "")) ? "gray" : "warn");
      const qualityDataset = (dataset) => qualityDatasets.find((row) => row.dataset === dataset) || null;
      const qualityDatasetUsable = (dataset) => {
        const row = qualityDataset(dataset);
        if (!row) return false;
        return row.status === "success" || Boolean(row.last_success_at);
      };
      const qualityProductsAvailable = qualityProductsEnvelope.available === true && qualityDatasetUsable("catalog");
      const qualityProducts = qualityProductsAvailable && Array.isArray(qualityProductsEnvelope.items) ? qualityProductsEnvelope.items : [];
      const qualityMetric = (key, dataset) => qualityDatasetUsable(dataset) && Object.prototype.hasOwnProperty.call(qualityTotals, key) ? escapeHtml(qualityTotals[key]) : "—";
      const qualityWorkerRunning = Boolean(quality.worker?.running);
      const qualityBusy = state.marketplaceQuality.loading || state.marketplaceQuality.syncing || qualityWorkerRunning;
      const qualityMoment = (value) => value ? escapeHtml(String(value).replace("T", " ").replace("Z", " UTC")) : "никогда";
      const qualityError = state.marketplaceQuality.error ? `<div class="task-note"><b>Ошибка экрана качества</b><br>${escapeHtml(state.marketplaceQuality.error)}</div>` : "";
      const qualityIntro = quality.state === "disabled"
        ? `<div class="task-note"><b>PostgreSQL-контур выключен</b><br>Временно используется аварийный SQLite fallback. Для основного каталога, остатков и заказов включите MARKETPLACE_PHASE1A_ENABLED=1.</div>`
        : quality.state === "unavailable"
          ? `<div class="task-note"><b>PostgreSQL marketplace недоступен</b><br>Примените migrations 005–007 и проверьте WMS_DATABASE_URL. Экран не подменяет эти данные устаревшей SQLite-копией.</div>`
          : "";
      const qualityDatasetCards = qualityDatasets.length ? qualityDatasets.map((row) => `<div class="card field-card"><div class="section-title"><b>${escapeHtml(qualityDatasetLabel[row.dataset] || row.dataset)}</b><span class="status-chip ${qualityChipClass(row.status)}">${escapeHtml(qualityStateLabel[row.status] || row.status)}</span></div><div class="marketplace-mini-list"><div class="marketplace-mini-row"><span>Последний пригодный sync</span><b>${qualityMoment(row.last_usable_at || row.last_success_at || (row.status === "success" ? row.finished_at : ""))}</b></div><div class="marketplace-mini-row"><span>Свежесть</span><b>${escapeHtml(qualityStateLabel[row.freshness] || row.freshness || "неизвестно")}</b></div><div class="marketplace-mini-row"><span>Строки: получено / уникально / ожидалось</span><b>${escapeHtml(row.received_count == null ? "—" : row.received_count)} / ${escapeHtml(row.unique_count == null ? "—" : row.unique_count)} / ${escapeHtml(row.expected_count == null ? "—" : row.expected_count)}</b></div><div class="marketplace-mini-row"><span>Страницы / retry</span><b>${escapeHtml(row.page_count == null ? "—" : row.page_count)} / ${escapeHtml(row.retry_count == null ? "—" : row.retry_count)}</b></div><div class="marketplace-mini-row"><span>Завершение</span><b>${escapeHtml(row.termination_reason || "—")}</b></div></div>${row.error_summary ? `<div class="task-note"><b>Диагностика</b><br>${escapeHtml(row.error_summary)}</div>` : ""}</div>`).join("") : `<div class="card field-card">${itemEmpty("Запусков Phase 1A ещё нет.")}</div>`;
      const capabilityRows = qualityCapabilities.length ? qualityCapabilities.map((row) => `<tr><td>${escapeHtml(row.capability)}</td><td><span class="status-chip ${qualityChipClass(row.status)}">${escapeHtml(qualityStateLabel[row.status] || row.status)}</span></td><td>${qualityMoment(row.checked_at)}</td><td>${escapeHtml(row.safe_message || "—")}</td></tr>`).join("") : `<tr><td colspan="4">Capabilities ещё не проверены.</td></tr>`;
      const qualityProductsState = qualityProductsEnvelope.available !== true
        ? "Каталог PostgreSQL сейчас недоступен: это не нулевой остаток."
        : !qualityDatasetUsable("catalog")
          ? "Каталог ещё не прошёл полную сверку: неполные строки не показываются как итог."
          : state.marketplaceQuality.query
            ? "По запросу ничего не найдено."
            : "Подтверждённый каталог пуст: это реальный ноль.";
      const qualityProductRows = qualityProducts.length ? qualityProducts.map((row) => `<tr><td><b>${escapeHtml(row.name || "Без названия")}</b><br><small>${escapeHtml(row.external_product_id || "—")}</small></td><td>${escapeHtml(row.offer_id || "—")}</td><td>${!qualityDatasetUsable("prices") ? "не подтверждено" : row.current_price == null ? "нет данных" : marketplaceMoney(row.current_price)}</td><td>${!qualityDatasetUsable("stocks") ? "не подтверждено" : row.stock == null ? "нет данных" : escapeHtml(row.stock)}</td><td>${!qualityDatasetUsable("stocks") ? "не подтверждено" : row.reserved == null ? "нет данных" : escapeHtml(row.reserved)}</td><td>${!qualityDatasetUsable("stocks") ? "не подтверждено" : row.available == null ? "нет данных" : escapeHtml(row.available)}</td></tr>`).join("") : `<tr><td colspan="6">${qualityProductsState}</td></tr>`;
      const qualityProductPage = Math.max(1, Number(qualityProductsEnvelope.page || state.marketplaceQuality.page || 1));
      const qualityProductPages = Math.max(0, Number(qualityProductsEnvelope.pages || 0));
      const qualityProductTotal = qualityProductsAvailable && qualityProductsEnvelope.total != null ? qualityProductsEnvelope.total : null;
      const qualityBlock = `
        <div class="button-row">
          <button type="button" class="small-button" data-marketplace-action="phase1a-sync" ${qualityBusy ? "disabled" : ""}>Запустить read-only sync</button>
          <button type="button" class="small-button secondary" data-marketplace-action="quality-refresh" ${state.marketplaceQuality.loading ? "disabled" : ""}>Обновить состояние</button>
          <span class="status-chip ${qualityChipClass(qualityWorkerRunning ? "running" : quality.state)}">${state.marketplaceQuality.loading ? "загрузка" : qualityWorkerRunning ? "sync выполняется" : escapeHtml(qualityStateLabel[quality.state] || quality.state || "не загружено")}</span>
        </div>
        ${qualityError}${qualityIntro}
        <div class="marketplace-dashboard-kpis">
          <div class="marketplace-dashboard-kpi"><span>Товары current</span><strong>${qualityMetric("products", "catalog")}</strong><small>неархивные</small></div>
          <div class="marketplace-dashboard-kpi"><span>Цены current</span><strong>${qualityMetric("prices", "prices")}</strong><small>точный NUMERIC</small></div>
          <div class="marketplace-dashboard-kpi"><span>Строки остатков</span><strong>${qualityMetric("stock_rows", "stocks")}</strong><small>seller-схемы</small></div>
          <div class="marketplace-dashboard-kpi"><span>Доступно</span><strong>${qualityMetric("stock_available", "stocks")}</strong><small>0 только после sync</small></div>
        </div>
        <div class="marketplace-wide-grid">${qualityDatasetCards}</div>
        <section class="card field-card">
          <div class="section-title"><b>Capabilities Ozon</b><span>${qualityCapabilities.length}</span></div>
          <div class="marketplace-table-scroll"><table class="marketplace-table"><thead><tr><th>Набор данных</th><th>Состояние</th><th>Проверено</th><th>Сообщение</th></tr></thead><tbody>${capabilityRows}</tbody></table></div>
        </section>
        <section class="card field-card">
          <div class="section-title"><b>Проверка current-товаров Ozon в PostgreSQL</b><span>${escapeHtml(qualityProductTotal == null ? "—" : qualityProductTotal)}</span></div>
          <div class="marketplace-filter-bar">
            <label><span>Название, артикул, SKU или штрихкод</span><input id="marketplaceQualitySearch" type="search" maxlength="200" value="${escapeHtml(state.marketplaceQuality.query || "")}" placeholder="Найти товар"></label>
            <button type="button" class="small-button secondary" data-marketplace-action="quality-search" ${state.marketplaceQuality.loading ? "disabled" : ""}>Найти</button>
            <div class="marketplace-period-label">Страница ${qualityProductsAvailable ? qualityProductPage : "—"} из ${qualityProductsAvailable ? Math.max(1, qualityProductPages) : "—"}</div>
            <div class="button-row"><button type="button" class="small-button secondary" data-marketplace-action="quality-prev" ${state.marketplaceQuality.loading || !qualityProductsAvailable || qualityProductPage <= 1 ? "disabled" : ""}>← Назад</button><button type="button" class="small-button secondary" data-marketplace-action="quality-next" ${state.marketplaceQuality.loading || !qualityProductsAvailable || qualityProductPages === 0 || qualityProductPage >= qualityProductPages ? "disabled" : ""}>Вперёд →</button></div>
          </div>
          <div class="marketplace-table-scroll"><table class="marketplace-table"><thead><tr><th>Товар</th><th>Offer ID</th><th>Цена</th><th>Present</th><th>Reserved</th><th>Available</th></tr></thead><tbody>${qualityProductRows}</tbody></table></div>
        </section>`;
      const wbQualityRows = Array.isArray(analytics.capability_rows)
        ? analytics.capability_rows
        : Object.entries(wbCapabilityStatuses).map(([capability, value]) => ({capability, ...(value || {})}));
      const wbQualityReady = wbQualityRows.length > 0 && wbQualityRows.every((row) => row.status === "available");
      const wbQualityLabels = {catalog:"Каталог",prices:"Цены",stocks:"Остатки",orders:"Заказы",sales:"Продажи и возвраты",finance:"Финансы",funnel:"Воронка",advertising:"Реклама",feedbacks:"Отзывы",supplies:"Поставки"};
      const wbQualityStatuses = {available:"доступно",partial:"частично",permission_required:"нужны права",unauthorized:"токен отклонён",payment_required:"нужен платный доступ",error:"ошибка",unavailable:"недоступно",unknown:"не проверено"};
      const wbQualityCards = wbQualityRows.length ? wbQualityRows.map((row) => {
        const coverage = row.coverage_start_date && row.coverage_end_date ? `${row.coverage_start_date} — ${row.coverage_end_date}` : "не указан";
        return `<div class="card field-card"><div class="section-title"><b>${escapeHtml(wbQualityLabels[row.capability] || row.capability)}</b><span class="status-chip ${row.status === "available" ? "" : "warn"}">${escapeHtml(wbQualityStatuses[row.status] || row.status || "не проверено")}</span></div><div class="marketplace-mini-list"><div class="marketplace-mini-row"><span>Проверено</span><b>${escapeHtml(row.checked_at || "никогда")}</b></div><div class="marketplace-mini-row"><span>Строк получено</span><b>${escapeHtml(row.row_count == null ? "—" : row.row_count)}</b></div><div class="marketplace-mini-row"><span>Покрытие</span><b>${escapeHtml(coverage)}</b></div></div>${row.safe_message ? `<div class="task-note"><b>Диагностика</b><br>${escapeHtml(row.safe_message)}</div>` : ""}</div>`;
      }).join("") : `<div class="card field-card">${itemEmpty("Wildberries ещё не записал результаты проверки источников.")}</div>`;
      const wbQualityBlock = `
        <div class="button-row">
          <button type="button" class="small-button" data-marketplace-action="sync" ${state.marketplaceData.loading ? "disabled" : ""}>Запустить read-only sync Wildberries</button>
          <button type="button" class="small-button secondary" data-marketplace-action="refresh" ${state.marketplaceData.loading ? "disabled" : ""}>Обновить состояние</button>
          <span class="status-chip ${wbQualityReady ? "" : "warn"}">${wbQualityReady ? "все источники доступны" : "нужна проверка"}</span>
        </div>
        <div class="marketplace-dashboard-kpis">
          <div class="marketplace-dashboard-kpi"><span>Товары</span><strong>${escapeHtml(summary.products == null ? "—" : summary.products)}</strong><small>текущий snapshot</small></div>
          <div class="marketplace-dashboard-kpi"><span>Строки остатков</span><strong>${escapeHtml(summary.stock_rows == null ? "—" : summary.stock_rows)}</strong><small>подтверждённые склады</small></div>
          <div class="marketplace-dashboard-kpi"><span>Заказы</span><strong>${escapeHtml(summary.open_orders == null ? "—" : summary.open_orders)}</strong><small>подтверждённый период</small></div>
          <div class="marketplace-dashboard-kpi"><span>Источники</span><strong>${escapeHtml(wbQualityRows.length)}</strong><small>проверено раздельно</small></div>
        </div>
        <div class="marketplace-wide-grid">${wbQualityCards}</div>`;
      const placeholderSection = (name, description) => `<div class="card field-card marketplace-placeholder"><div class="marketplace-placeholder-icon">◇</div><h3>${escapeHtml(name)}</h3><p>${escapeHtml(description)}</p><span class="status-chip gray">Раздел подготовлен</span></div>`;
      const ozonSettingsBlock = `<div class="card field-card"><div class="section-title"><b>Доступ Ozon Seller API</b><span class="status-chip ${ozonRolesCapability.status === "available" ? "" : "warn"}">${escapeHtml(ozonRolesCapability.status === "available" ? "проверен" : "не проверен")}</span></div><div class="marketplace-mini-list"><div class="marketplace-mini-row"><span>Роль ключа</span><b>${escapeHtml(ozonRoleNames.join(", ") || "не определена")}</b></div><div class="marketplace-mini-row"><span>Методов разрешено Ozon</span><b>${escapeHtml(ozonMethodPaths.length || "—")}</b></div><div class="marketplace-mini-row"><span>Интегрированные наборы PostgreSQL</span><b>${escapeHtml(qualityDatasets.length)}</b></div><div class="marketplace-mini-row"><span>Изменение данных в Ozon</span><b>${ozonRoleNames.some((name) => String(name).toLowerCase().includes("read only")) ? "заблокировано ключом" : "зависит от прав ключа"}</b></div></div><div class="task-note"><b>Что означает «подключён»</b><br>Сайт показывает только данные, реально подтверждённые отдельными синхронизациями. Внутренние задания склада создаются у нас и не изменяют кабинет Ozon.</div></div>`;
      const safeProductsBlock = isWildberries && !wbCatalogUsable ? itemEmpty("Текущий snapshot каталога Wildberries не подтверждён.") : productsBlock;
      const safeStocksBlock = isWildberries && !wbStocksUsable ? itemEmpty("Текущий snapshot остатков Wildberries не подтверждён; исторический ноль скрыт.") : stocksBlock;
      const sectionContent = {overview: overviewBlock, orders: ordersBlock, supplies: suppliesBlock, "warehouse-shipments": warehouseShipmentsBlock, sync: runsBlock, stocks: safeStocksBlock, analytics: analyticsBlock, products: safeProductsBlock, finance: financeBlock, reviews: reviewsBlock, "data-quality": isWildberries ? wbQualityBlock : qualityBlock, settings: isWildberries ? placeholderSection("Настройки", "Подключение Wildberries управляется на сервере.") : ozonSettingsBlock};
      const content = sectionContent[state.marketplaceView] || safeProductsBlock;
      const sectionTitles = {overview:"Обзор", orders:"Заказы", supplies:"Поставки", "warehouse-shipments":"Отгрузки на склад", sync:"Журнал синхронизации", stocks:"Остатки", analytics:"Аналитика", products:"Товары", finance:"Финансы", reviews:"Отзывы", "data-quality":"Качество данных", settings:"Настройки"};
      const title = sectionTitles[state.marketplaceView] || "Товары";
      const detail = renderMarketplaceDetail(products, orders, runs);
      const marketplaceMenuItems = [["overview","⌂","Обзор"],["products","▤","Товары"],["stocks","▦","Остатки"],["orders","▣","Заказы"],["supplies","⇧","Поставки"],["finance","₽","Финансы"],["reviews","☆","Отзывы"],["data-quality","◉","Качество данных"],["settings","⚙","Настройки"]];
      const marketplaceMenu = `<nav class="marketplace-menu-strip" aria-label="Разделы маркетплейсов"><div class="marketplace-menu-label">Площадки</div><button type="button" class="marketplace-provider-menu-button ${isAll ? "active" : ""}" data-marketplace-provider="all"><span class="marketplace-menu-icon">∞</span><span>Все площадки</span></button><button type="button" class="marketplace-provider-menu-button ${isOzon ? "active" : ""}" data-marketplace-provider="ozon"><span class="marketplace-menu-icon">O</span><span>Ozon</span><small>${payload.configured ? "подключён" : "нет связи"}</small></button><button type="button" class="marketplace-provider-menu-button ${isWildberries ? "active" : ""}" data-marketplace-provider="wildberries" ${wildberriesConnected ? "" : "disabled"}><span class="marketplace-menu-icon">W</span><span>Wildberries</span><small>${wildberriesConnected ? "подключён" : "не подключён"}</small></button><div class="marketplace-menu-label">Разделы</div>${marketplaceMenuItems.map(([id,icon,label]) => `<button type="button" class="marketplace-menu-link ${state.marketplaceView === id ? "active" : ""}" data-marketplace-view="${id}"><span class="marketplace-menu-icon">${icon}</span><span>${label}</span></button>`).join("")}</nav>`;
      mount.innerHTML = `<div class="marketplace-layout">${marketplaceMenu}<div class="marketplace-main">
        <div class="screen-head marketplace-v2-head"><div><h2>${isAll ? "Маркетплейсы" : providerName}</h2><p>${isAll ? "Общая статистика и управление продажами на маркетплейсах" : (isOzon ? "Продажи, заказы, остатки и показатели магазина Ozon" : "Продажи, заказы, остатки и показатели магазина Wildberries")}</p></div><div class="marketplace-brand-mark ${isWildberries ? "wb" : isOzon ? "ozon" : "all"}">${isWildberries ? "WB" : isOzon ? "OZON" : "Ozon + WB"}</div></div><div class="marketplace-provider-status"><b>${isAll ? "Общий обзор" : providerName}</b><span>${escapeHtml(providerStatus)}</span></div>
        ${errorNotice}${notConfigured}
        ${state.marketplaceDetail ? detail : `<div class="section-title"><b>${title}</b><span>${state.marketplaceView === "orders" ? (isWildberries && !verifiedOrdersAvailable ? "—" : orders.length) : state.marketplaceView === "supplies" ? (isWildberries && !wbSuppliesCurrent ? "—" : supplies.length) : state.marketplaceView === "warehouse-shipments" ? warehouseShipments.length : state.marketplaceView === "sync" ? runs.length : state.marketplaceView === "stocks" ? (isWildberries && !wbStocksUsable ? "—" : products.length) : state.marketplaceView === "data-quality" ? (isWildberries ? wbQualityRows.length : qualityDatasets.length) : state.marketplaceView === "analytics" ? "" : (isWildberries && !wbCatalogUsable ? "—" : groups.length)}</span></div>${content}`}
      </div></div>`;
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
        ["shipments", "↑", "Отгрузки"],
        ["stock", "▤", "Остатки"],
        ["lookup", "⌕", "Проверка товара"],
        ["products", "▤", "Товары"],
        ["inventory", "≡", "Инвентаризация"],
        ...((state.data && state.data.is_admin) ? [["admin-stock-control", "✎", "Инвентаризация / списание"]] : []),
        ["reports", "↧", "Отчёты"],
        ["more", "•••", "Ещё"],
      ];
      return `<aside class="warehouse-v2-sidebar" aria-label="Разделы склада"><h3>Управление складом</h3>${items.map(([id, icon, label]) => `
        <button type="button" class="warehouse-v2-nav ${state.wmsView === id || (id === "more" && warehouseMoreViews.has(state.wmsView) && !["map", "reports", "products", "lookup", "inventory", "stock", "transfer", "admin-stock-control"].includes(state.wmsView)) ? "active" : ""}" data-wms-view="${id}"><span class="warehouse-v2-icon">${icon}</span><span>${label}</span></button>
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
      else if (state.wmsView === "shipments") renderWmsShipments();
      else if (state.wmsView === "inventory") renderWmsInventory();
      else if (state.wmsView === "admin-stock-control") renderWmsAdminStockControl();
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
      const materialDraft = state.wmsMaterialReceipt;
      const total = receiving.reduce((sum, row) => sum + Number(row.quantity || 0), 0);
      const selectedProduct = receiving.find((row) => wmsProductKeysEqual(row.product_key, wmsProductKey(d)));
      mainButton.textContent = state.wmsData.loading ? "Обновляем…" : "Обновить приёмку";
      mainButton.disabled = state.wmsData.loading;
      mount.innerHTML = `
        <div class="screen-head"><div><h2>Зона приёмки</h2><p>Готовая продукция появляется здесь автоматически после упаковки. Материалы поступают сразу на склад материалов.</p></div><div class="date">${escapeHtml(total)} ед.</div></div>
        ${renderWmsDataNotice()}
        <div class="section-title"><b>Ожидает размещения</b><span>${receiving.length} поз.</span></div>
        <div class="op-list">${receiving.length ? receiving.map((row, index) => {
          const available = Math.max(0, Number(row.quantity || 0) - Number(row.reserved_quantity || 0));
          return `<div class="card report-row"><div><b>${escapeHtml(wmsProductLabel(row.product_key))}</b><span>Готовая продукция · доступно ${escapeHtml(available)}</span></div><div><span class="status-chip">${escapeHtml(row.quantity)} ${escapeHtml(row.unit || "шт")}</span>${state.data && state.data.is_admin ? `<button type="button" class="link-button" data-wms-receipt-product="${index}">штрихкод</button>` : ""}</div></div>`;
        }).join("") : itemEmpty("Приёмка пуста.")}</div>
        <div class="section-title"><b>Ручная приёмка материалов</b><span>без штрихкода</span></div>
        <div class="card field-card">
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
            <div class="report-row"><div><b>${escapeHtml(wmsProductLabel(selectedProduct.product_key))}</b></div><span class="status-chip">выбран</span></div>
            <div class="field full"><label>Новый штрихкод</label><input id="wmsBarcode" value="${escapeHtml(d.barcode || "")}" placeholder="EAN-13 / Code 128"></div>
            <div class="button-row"><button class="small-button" data-wms-scan="bind_product">📷 Сканировать код</button><button class="small-button secondary" data-wms-action="register_barcode">Привязать код</button></div>
          </div>
        ` : ""}
      `;
    }

    function renderWmsPutaway() {
      const d = state.wmsDraft;
      const locationCode = (d.toLocation || "").replace(/^LOC:/i, "").trim();
      const productDetected = Boolean(d.productScanned && d.productName && d.productSize && d.productColor);
      mainButton.textContent = "Разместить";
      mainButton.disabled = false;
      mount.innerHTML = `
        <div class="screen-head"><div><h2>Размещение готовой продукции</h2><p>Сначала ячейка, затем товар и количество. Приёмка не является обязательным шагом.</p></div></div>
        ${renderWmsGuidedScanner("to_location", locationCode, productDetected, "Ячейка размещения")}
        <div class="card field-card">
          <label>Данные размещения</label>
          <div class="form-grid">
            <div class="field full"><label>Ячейка</label><input id="wmsToLocation" value="${escapeHtml(d.toLocation || "")}" placeholder="Сначала отсканируйте ячейку" readonly></div>
            ${productDetected ? `<div class="field full"><label>Товар</label><div class="report-row"><div><b>${escapeHtml(wmsProductLabel(wmsProductKey(d)))}</b><span>Штрихкод распознан</span></div><span class="status-chip">✓</span></div></div>` : ""}
            ${productDetected ? `<div class="field full"><label>Количество</label><input id="wmsQuantity" type="number" inputmode="numeric" min="1" step="1" value="${escapeHtml(d.quantity || "")}" placeholder="0"></div>` : ""}
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
      const stockRow = productDetected ? wmsResolvedStock(locationCode, wmsProductKey(d)) : null;
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
      const locationCode = (d.fromLocation || "").replace(/^LOC:/i, "").trim();
      const locationReady = Boolean(d.fromLocationScanned && locationCode && wmsLocationByCode(locationCode));
      const productDetected = Boolean(locationReady && d.productScanned && d.productName);
      const stockRow = productDetected ? wmsResolvedStock(locationCode, wmsProductKey(d)) : null;
      const systemQuantity = stockRow ? Number(stockRow.quantity || 0) : null;
      const countedQuantity = String(d.quantity ?? "");
      const canConfirm = Boolean(stockRow && /^\\d+$/.test(countedQuantity));
      mainButton.hidden = true;
      mount.innerHTML = `
        <div class="screen-head"><div><h2>Инвентаризация</h2><p>Сначала отсканируйте ячейку, затем товар и введите фактическое количество.</p></div></div>
        ${renderWmsGuidedScanner("from_location", locationCode, productDetected, "Ячейка пересчёта")}
        ${locationReady ? renderWmsLocationContents(locationCode) : ""}
        ${productDetected ? `
          <div class="card field-card">
            <label>Пересчёт товара</label>
            <div class="report-row"><div><b>${escapeHtml(wmsProductLabel(wmsProductKey(d)))}</b><span>Ячейка ${escapeHtml(locationCode)}</span></div><span class="status-chip">товар найден</span></div>
            <div class="form-grid">
              <div class="field"><label>В системе</label><input value="${escapeHtml(systemQuantity)}" readonly></div>
              <div class="field"><label>Фактическое количество</label><input id="wmsQuantity" type="number" inputmode="numeric" min="0" step="1" value="${escapeHtml(countedQuantity)}" placeholder="0" autofocus></div>
            </div>
          </div>
        ` : ""}
        <div class="button-row">
          <button class="small-button secondary" data-wms-action="inventory_back">Назад</button>
          ${productDetected ? `<button class="small-button" data-wms-action="inventory" ${canConfirm ? "" : "disabled"}>Подтвердить</button>` : ""}
        </div>
      `;
    }

    function renderWmsAdminStockControl() {
      if (!(state.data && state.data.is_admin)) {
        state.wmsView = "overview";
        renderWmsOverview();
        return;
      }
      const draft = state.wmsAdminAdjustment;
      draft.returnView = "admin-stock-control";
      mainButton.hidden = true;
      mount.innerHTML = `
        <div class="screen-head"><div><h2>Инвентаризация / списание</h2><p>Ручная корректировка без сканирования штрихкодов. Доступно только администратору.</p></div></div>
        ${renderWmsDataNotice()}
        <div class="card field-card"><div class="button-row"><button type="button" class="small-button ${draft.mode === "inventory" ? "" : "secondary"}" data-wms-admin-mode="inventory">Инвентаризация</button><button type="button" class="small-button ${draft.mode === "scrap" ? "" : "secondary"}" data-wms-admin-mode="scrap">Списание</button></div></div>
        ${renderWmsAdminAdjustmentForm(false)}
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
      const isTimesheetReport = state.adminReportType === "timesheet";
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
        <div class="screen-head"><div><h2>Админ отчёты</h2><p>Общий табель, производственный отчёт или данные конкретного сотрудника.</p></div><div class="date">${escapeHtml(report ? `${report.start_date} — ${report.end_date}` : "период")}</div></div>
        ${renderAdminTabs()}
        <div class="card field-card">
          <div class="form-grid">
            <div class="field full"><label>Тип отчёта</label><select id="adminReportType"><option value="timesheet" ${isTimesheetReport ? "selected" : ""}>Табель — все сотрудники</option><option value="today" ${state.adminReportType === "today" ? "selected" : ""}>Сегодня</option><option value="period" ${state.adminReportType === "period" ? "selected" : ""}>Производственный отчёт за период</option><option value="employee" ${isEmployeeReport ? "selected" : ""}>Один сотрудник</option></select></div>
            <div class="field"><label>Начало</label><input id="adminStartDate" type="date" value="${escapeHtml(state.adminStartDate)}"></div>
            <div class="field"><label>Окончание</label><input id="adminEndDate" type="date" value="${escapeHtml(state.adminEndDate)}"></div>
            ${isEmployeeReport ? `<div class="field full"><label>Сотрудник</label><select id="adminEmployeeId">${employeeOptions || `<option value="">Нет сотрудников</option>`}</select></div>` : ""}
          </div>
          <div class="button-row"><button class="small-button secondary" data-admin-action="load-report">Показать</button><button class="small-button" data-admin-action="export-report">Скачать Excel</button></div>
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
        ${isTimesheetReport ? "" : `<div class="section-title"><b>Операции</b><span>${operations.length}</span></div><div class="op-list">${operationsHtml}</div>`}
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
        <div class="screen-head"><div><h2>Сотрудники</h2><p>Управление персоналом, ролями, доступами и сменами.</p></div><div class="date">${employees.length} всего</div></div>
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
      if (state.adminSection === "integrations") {
        mount.innerHTML = renderAdminIntegrations();
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

    function analyticsHubTabs() {
      const tabs = [
        ["general", "Общая"],
        ["production", "Производство"],
        ["ozon", "Ozon"],
        ["wildberries", "Wildberries"],
      ];
      return `<div class="top-tabs analytics-hub-tabs" role="tablist" aria-label="Раздел аналитики">${tabs.map(([id, label]) => `<button type="button" role="tab" aria-selected="${state.analyticsHubTab === id ? "true" : "false"}" class="${state.analyticsHubTab === id ? "active" : ""}" onclick="state.analyticsHubTab='${id}';state.marketplaceView='overview';state.marketplaceDetail=null;render()">${label}</button>`).join("")}</div>`;
    }

    function analyticsHubHas(row, key) {
      return Boolean(row && Object.prototype.hasOwnProperty.call(row, key));
    }

    function analyticsHubDate(row, keys) {
      for (const key of keys) {
        const value = String((row && row[key]) || "").slice(0, 10);
        if (/^\\d{4}-\\d{2}-\\d{2}$/.test(value)) return value;
      }
      return "";
    }

    function analyticsHubPeriodRows(rows, keys, periodMeta) {
      return (Array.isArray(rows) ? rows : []).filter((row) => {
        const value = analyticsHubDate(row, keys);
        return value ? marketplaceDateInPeriod(value, periodMeta) : false;
      });
    }

    function analyticsHubFreshness(value) {
      if (!value) return {key: "unknown", label: "время sync неизвестно", age: ""};
      const raw = String(value);
      const parsed = new Date(raw.includes("T") ? raw : raw.replace(" ", "T"));
      if (Number.isNaN(parsed.getTime())) return {key: "unknown", label: "время sync неизвестно", age: raw};
      const ageMs = Math.max(0, Date.now() - parsed.getTime());
      const ageHours = ageMs / 3600000;
      const age = ageHours < 1
        ? `${Math.max(0, Math.round(ageMs / 60000))} мин назад`
        : ageHours < 48
          ? `${Math.round(ageHours)} ч назад`
          : `${Math.round(ageHours / 24)} дн назад`;
      return ageHours > 6 ? {key: "stale", label: "данные устарели", age} : {key: "fresh", label: "актуально", age};
    }

    function analyticsHubQualityModel() {
      const envelope = state.analyticsQuality.payload || state.marketplaceQuality.payload || {};
      const phase = envelope.phase1a || {};
      const datasets = Array.isArray(phase.datasets) ? phase.datasets : [];
      const totals = phase.totals && typeof phase.totals === "object" ? phase.totals : {};
      const dataset = (key) => datasets.find((row) => row.dataset === key) || null;
      const usable = (key) => {
        const row = dataset(key);
        return Boolean(row && (row.status === "success" || row.last_success_at || row.last_usable_at));
      };
      const latest = datasets.map((row) => row.last_usable_at || row.last_success_at || row.finished_at || "").filter(Boolean).sort().pop() || "";
      return {
        known: Boolean(state.analyticsQuality.loaded || envelope.phase1a),
        loading: Boolean(state.analyticsQuality.loading),
        error: state.analyticsQuality.error || "",
        enabled: phase.enabled === true,
        state: phase.state || "unknown",
        datasets,
        totals,
        latest,
        catalogUsable: usable("catalog"),
        pricesUsable: usable("prices"),
        stocksUsable: usable("stocks"),
      };
    }

    function analyticsHubProviderModel(key, providerPayload, rootPayload, periodMeta, marketplaceReady, pgQuality) {
      const provider = providerPayload && typeof providerPayload === "object" ? providerPayload : {};
      const analytics = provider.analytics && typeof provider.analytics === "object" ? provider.analytics : {};
      const summary = provider.summary && typeof provider.summary === "object" ? provider.summary : {};
      const products = Array.isArray(provider.products_rows) ? provider.products_rows : [];
      const orderRows = Array.isArray(provider.orders_rows) ? provider.orders_rows : [];
      const runs = Array.isArray(provider.sync_runs) ? provider.sync_runs : [];
      const account = Array.isArray(provider.accounts) ? (provider.accounts[0] || {}) : {};
      const capabilities = analytics.capabilities && typeof analytics.capabilities === "object" ? analytics.capabilities : {};
      const latestRun = runs[0] || {};
      const configured = key === "ozon"
        ? Boolean(rootPayload.configured || provider.configured)
        : Boolean(provider.configured || (rootPayload.connectors || []).some((row) => row.marketplace === "wildberries" && row.configured));
      const financeAll = Array.isArray(analytics.finance_daily) ? analytics.finance_daily : [];
      const financeAvailable = key === "wildberries"
        ? capabilities.finance === true
        : Boolean(analytics.finance_available === true || financeAll.length);
      const finance = analyticsHubPeriodRows(financeAll, ["date"], periodMeta);
      const recognized = financeAvailable ? finance.reduce((sum, row) => sum + Number(row.revenue || 0), 0) : null;
      const net = financeAvailable ? finance.reduce((sum, row) => sum + Number(row.net || 0), 0) : null;
      const funnelAll = key === "wildberries" && Array.isArray(analytics.sales_funnel_daily) ? analytics.sales_funnel_daily : [];
      const funnel = analyticsHubPeriodRows(funnelAll, ["date"], periodMeta);
      const gmvAvailable = key === "wildberries" && (capabilities.sales_funnel === true || funnelAll.length > 0);
      const gmv = gmvAvailable ? funnel.reduce((sum, row) => sum + Number(row.order_sum || 0), 0) : null;
      const datedOrders = analyticsHubPeriodRows(orderRows, ["shipment_date", "created_at", "updated_at"], periodMeta);
      let ordersAvailable = configured && marketplaceReady && Array.isArray(provider.orders_rows);
      let orders = null;
      if (key === "wildberries" && capabilities.orders === false) ordersAvailable = false;
      if (gmvAvailable) {
        ordersAvailable = true;
        orders = funnel.reduce((sum, row) => sum + Number(row.order_count || 0), 0);
      } else if (ordersAvailable) {
        if (!orderRows.length) orders = 0;
        else if (datedOrders.length) orders = datedOrders.length;
        else ordersAvailable = false;
      }
      const pgActive = key === "ozon" && pgQuality.known && pgQuality.enabled && !["disabled", "unavailable"].includes(pgQuality.state);
      let stockAvailable = false;
      let stock = null;
      let stockSource = "";
      let stockDetailAvailable = false;
      if (pgActive) {
        stockAvailable = pgQuality.stocksUsable && analyticsHubHas(pgQuality.totals, "stock_available");
        stock = stockAvailable ? Number(pgQuality.totals.stock_available || 0) : null;
        stockSource = "PostgreSQL current";
        // The aggregate quality endpoint does not expose all current product
        // rows. Legacy per-product values must not be presented as PG-fresh.
        stockDetailAvailable = false;
      } else if (key === "wildberries") {
        stockAvailable = capabilities.stocks === true || (Array.isArray(provider.warehouses) && provider.warehouses.length > 0);
        stock = stockAvailable ? products.reduce((sum, row) => sum + Number(row.available || 0), 0) : null;
        stockSource = stockAvailable ? "склады Wildberries" : "нет разрешения API";
        stockDetailAvailable = stockAvailable;
      } else if (!pgQuality.loading && pgQuality.known && !pgQuality.enabled) {
        stockAvailable = configured && marketplaceReady && (Number(summary.stock_rows || 0) > 0 || products.some((row) => analyticsHubHas(row, "available")));
        stock = stockAvailable ? products.reduce((sum, row) => sum + Number(row.available || 0), 0) : null;
        stockSource = stockAvailable ? "SQLite fallback" : "остатки не подтверждены";
        stockDetailAvailable = stockAvailable;
      }
      const pgLastSync = pgActive ? pgQuality.latest : "";
      const lastSync = pgLastSync || account.last_sync_at || latestRun.finished_at || latestRun.started_at || "";
      const freshness = analyticsHubFreshness(lastSync);
      const capabilityValues = Object.values(capabilities).filter((value) => typeof value === "boolean");
      const missingCapabilities = Object.entries(capabilities).filter(([, value]) => value === false).map(([name]) => name);
      const runStatus = String(latestRun.status || "").toLowerCase();
      const lastError = String(account.last_error || latestRun.error_message || "");
      let status = "ready";
      if (!marketplaceReady) status = state.marketplaceData.loading ? "loading" : "unknown";
      else if (!configured) status = "disconnected";
      else if (lastError || ["error", "failed"].includes(runStatus)) status = "error";
      else if (freshness.key === "stale") status = "stale";
      else if (["partial", "attention"].includes(runStatus) || missingCapabilities.length || (pgActive && pgQuality.state !== "ready")) status = "partial";
      else if (!lastSync) status = "partial";
      const commercialRows = key === "wildberries" && gmvAvailable
        ? funnel.map((row) => ({date: analyticsHubDate(row, ["date"]), value: Number(row.order_sum || 0)}))
        : financeAvailable
          ? finance.map((row) => ({date: analyticsHubDate(row, ["date"]), value: Number(row.revenue || 0)}))
          : [];
      return {
        key,
        label: key === "wildberries" ? "Wildberries" : "Ozon",
        configured,
        status,
        lastSync,
        freshness,
        lastError,
        capabilities,
        capabilityCount: capabilityValues.filter(Boolean).length,
        capabilityTotal: capabilityValues.length,
        missingCapabilities,
        summary,
        products,
        orderRows,
        analytics,
        financeAvailable,
        recognized,
        net,
        gmvAvailable,
        gmv,
        ordersAvailable,
        orders,
        stockAvailable,
        stock,
        stockSource,
        stockDetailAvailable,
        commercialAvailable: key === "wildberries" ? gmvAvailable || financeAvailable : financeAvailable,
        commercialLabel: key === "wildberries" && gmvAvailable ? "GMV заказов" : "начислено",
        commercialRows,
      };
    }

    function analyticsHubMetricCard(label, value, suffix, hint, status = "ready") {
      const unavailable = value === null || value === undefined;
      const classes = ["analytics-overview-kpi", unavailable ? "unavailable" : "", status].filter(Boolean).join(" ");
      return `<div class="card ${classes}"><span>${escapeHtml(label)}</span><strong>${unavailable ? "—" : escapeHtml(value)}${!unavailable && suffix ? `<small>${escapeHtml(suffix)}</small>` : ""}</strong><small>${escapeHtml(unavailable ? hint || "Источник не предоставляет показатель" : hint)}</small></div>`;
    }

    function analyticsHubCombinedChart(models) {
      const colors = {ozon: "#1764e8", wildberries: "#9c27b0"};
      const series = models.filter((model) => model.commercialAvailable).map((model) => ({
        key: model.key,
        label: `${model.label} · ${model.commercialLabel}`,
        rows: model.commercialRows,
        color: colors[model.key],
        status: model.status,
      }));
      if (!series.length) return `<div class="marketplace-chart-empty"><b>Финансовая динамика недоступна</b><span>Ни одна площадка не предоставила подтверждённые операции после удержаний за выбранный период.</span></div>`;
      const dates = [...new Set(series.flatMap((item) => item.rows.map((row) => row.date).filter(Boolean)))].sort();
      if (!dates.length) return `<div class="marketplace-chart-empty"><b>За выбранный период операций нет</b><span>Источники доступны, но в диапазоне нет финансовых операций или заказов.</span></div><div class="analytics-chart-legend">${series.map((item) => `<span><i style="--legend-color:${item.color}"></i>${escapeHtml(item.label)}</span>`).join("")}</div>`;
      const width = 760, height = 250, left = 54, right = 20, top = 20, bottom = 36;
      const chartWidth = width - left - right, chartHeight = height - top - bottom;
      const allValues = series.flatMap((item) => item.rows.map((row) => Number(row.value || 0)));
      const minimum = Math.min(0, ...allValues);
      const maximum = Math.max(minimum + 1, 0, ...allValues);
      const valueRange = maximum - minimum;
      const x = (date) => dates.length === 1 ? left + chartWidth / 2 : left + chartWidth * dates.indexOf(date) / (dates.length - 1);
      const y = (value) => top + chartHeight * (maximum - Number(value || 0)) / valueRange;
      const compact = (value) => { const number = Number(value || 0); const absolute = Math.abs(number); return absolute >= 1000000 ? `${(number / 1000000).toFixed(1)}м` : absolute >= 1000 ? `${Math.round(number / 1000)}к` : String(Math.round(number)); };
      const labels = [...new Set([0, Math.floor((dates.length - 1) / 2), dates.length - 1])];
      const svgSeries = series.map((item) => {
        const points = item.rows.filter((row) => row.date && dates.includes(row.date)).map((row) => `${x(row.date).toFixed(1)},${y(row.value).toFixed(1)}`).join(" ");
        const dash = ["partial", "stale"].includes(item.status) ? ` stroke-dasharray="7 5"` : "";
        const line = item.rows.length > 1 ? `<polyline fill="none" stroke="${item.color}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"${dash} points="${points}"/>` : "";
        const dots = item.rows.filter((row) => row.date && dates.includes(row.date)).map((row) => { const pointLabel = `${item.label} · ${row.date} · ${marketplaceMoney(row.value)}`; return `<circle cx="${x(row.date)}" cy="${y(row.value)}" r="4" fill="${item.color}"/><circle class="chart-point-hit" cx="${x(row.date)}" cy="${y(row.value)}" r="13" tabindex="0" role="button" aria-label="${escapeHtml(pointLabel)}" data-chart-date="${escapeHtml(row.date)}" data-chart-value="${escapeHtml(row.value)}" onmouseenter="showMarketplaceChartTooltip(this)" onmouseleave="hideMarketplaceChartTooltip(this)" onfocus="showMarketplaceChartTooltip(this)" onblur="hideMarketplaceChartTooltip(this)" onclick="showMarketplaceChartTooltip(this)" ontouchstart="showMarketplaceChartTooltip(this)"><title>${escapeHtml(pointLabel)}</title></circle>`; }).join("");
        return line + dots;
      }).join("");
      return `<div class="marketplace-line-chart analytics-combined-chart"><svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Коммерческая динамика Ozon и Wildberries">${[0,.25,.5,.75,1].map((ratio) => { const gridY = top + chartHeight * ratio; const tickValue = maximum - valueRange * ratio; return `<line class="chart-grid" x1="${left}" y1="${gridY}" x2="${width-right}" y2="${gridY}"/><text class="chart-axis-label" x="${left-8}" y="${gridY+4}" text-anchor="end">${compact(tickValue)}</text>`; }).join("")}${minimum < 0 && maximum > 0 ? `<line x1="${left}" y1="${y(0)}" x2="${width-right}" y2="${y(0)}" stroke="#7d8799" stroke-width="1.5"/>` : ""}${svgSeries}${labels.map((index) => `<text class="chart-axis-label" x="${x(dates[index])}" y="${height-9}" text-anchor="middle">${escapeHtml(dates[index].slice(5))}</text>`).join("")}</svg><div class="marketplace-point-tooltip" hidden></div></div><div class="analytics-chart-legend">${series.map((item) => `<span><i style="--legend-color:${item.color}"></i>${escapeHtml(item.label)}</span>`).join("")}</div>`;
    }

    function renderAnalyticsOverviewFromApi(hubHead) {
      const overviewState = state.analyticsOverview;
      const payload = overviewState.payload && typeof overviewState.payload === "object" ? overviewState.payload : {};
      const periodMeta = marketplacePeriodMeta(state.marketplacePeriod);
      const periodLabel = payload.period && payload.period.label ? payload.period.label : periodMeta.label;
      const rows = Array.isArray(payload.metrics) ? payload.metrics : [];
      const metric = (code) => rows.find((row) => row.code === code || row.key === code) || {value: null, status: "unavailable", meta: {warnings: []}};
      const providers = Array.isArray(payload.providers) ? payload.providers : [];
      const risks = Array.isArray(payload.risks) ? payload.risks : [];
      const suppliesEnvelope = payload.supplies && typeof payload.supplies === "object" ? payload.supplies : {};
      const supplies = Array.isArray(suppliesEnvelope.shipments) ? suppliesEnvelope.shipments : [];
      const production = payload.production && typeof payload.production === "object" ? payload.production : {};
      const quality = payload.data_quality && typeof payload.data_quality === "object" ? payload.data_quality : {};
      const qualityStatusLabels = {ready:"готово",fresh:"актуально",partial:"частично",attention:"нужна проверка",stale:"устарело",error:"ошибка",loading:"загрузка",unknown:"нет данных",disconnected:"не подключён",disabled:"выключено",unavailable:"недоступно",no_data:"нет данных",success:"успешно",permission_required:"нужны права"};
      const providerStatusClass = (status) => ["ready", "fresh", "success"].includes(status) ? "" : (["unknown", "disconnected", "disabled", "no_data", "unavailable"].includes(status) ? "gray" : "warn");
      const formatInteger = (value) => Number(value || 0).toLocaleString("ru-RU", {maximumFractionDigits: 0});
      const moneyValue = (value) => value === null || value === undefined ? null : marketplaceMoney(Number(value));
      const metricHint = (row, fallback) => {
        const meta = row && row.meta && typeof row.meta === "object" ? row.meta : {};
        const warnings = Array.isArray(meta.warnings) ? meta.warnings.filter(Boolean) : [];
        if (warnings.length) return warnings[0];
        return qualityStatusLabels[row.status] || row.source_hint || meta.source_hint || fallback || "Источник не подтверждён";
      };
      const displayMetric = (code, format, fallback) => {
        const row = metric(code);
        const value = row.value === null || row.value === undefined ? null : format(row.value);
        return analyticsHubMetricCard(row.label || fallback, value, "", metricHint(row, fallback), row.status || "unavailable");
      };
      const highRisks = risks.filter((row) => String(row.severity || "").toLowerCase() === "high");
      const planKnown = production.plan !== null && production.plan !== undefined;
      const factKnown = production.fact !== null && production.fact !== undefined;
      const productionDisplay = planKnown && factKnown ? `${formatInteger(production.plan)} / ${formatInteger(production.fact)}` : null;
      const sourceLoading = overviewState.loading || (!overviewState.loaded && !overviewState.error);
      const calendarMax = marketplaceLocalIsoDate();
      const periodOptions = [["today","Сегодня"],["yesterday","Вчера"],["7d","Последние 7 дней"],["30d","Последние 30 дней"],["month","Текущий месяц"],["previous-month","Предыдущий месяц"],["custom","Произвольный диапазон"]];
      const periodBar = `<div class="analytics-period-bar"><label><span>Период</span><select id="analyticsHubPeriod">${periodOptions.map(([value,label]) => `<option value="${value}" ${state.marketplacePeriod === value ? "selected" : ""}>${label}</option>`).join("")}</select></label><div class="analytics-period-dates"><label><span>С даты</span><input id="analyticsHubDateFrom" type="date" max="${calendarMax}" value="${escapeHtml(state.marketplaceDateFrom)}"></label><label><span>По дату</span><input id="analyticsHubDateTo" type="date" max="${calendarMax}" value="${escapeHtml(state.marketplaceDateTo)}"></label></div><div class="analytics-period-current">${escapeHtml(periodLabel)}</div></div>`;
      if (sourceLoading) {
        mainButton.hidden = true;
        mount.innerHTML = `${hubHead}<div class="analytics-overview">${periodBar}<div class="analytics-overview-notice"><div><b>Собираем единую аналитику</b><span>Проверяем PostgreSQL Ozon, Wildberries, производство и поставки.</span></div><span class="status-chip gray">загрузка</span></div><div class="analytics-overview-kpis">${Array.from({length: 7}, () => `<div class="card analytics-overview-kpi analytics-loading-card"></div>`).join("")}</div></div>`;
        return;
      }
      if (overviewState.error || !payload.ok) {
        mainButton.hidden = true;
        mount.innerHTML = `${hubHead}<div class="analytics-overview">${periodBar}<div class="analytics-overview-notice error"><div><b>Общая аналитика временно недоступна</b><span>${escapeHtml(overviewState.error || payload.message || "Источники не ответили.")}</span></div><button type="button" class="small-button secondary" data-analytics-overview-action="refresh">Повторить</button></div></div>`;
        return;
      }

      const overallMeta = payload.meta && typeof payload.meta === "object" ? payload.meta : {};
      const overallWarnings = Array.isArray(overallMeta.warnings) ? overallMeta.warnings.filter(Boolean) : [];
      const productionMeta = production.meta && typeof production.meta === "object" ? production.meta : {};
      const suppliesMeta = suppliesEnvelope.meta && typeof suppliesEnvelope.meta === "object" ? suppliesEnvelope.meta : {};
      const providerCoverageComplete = providers.length > 0 && providers.every((provider) => provider.status === "fresh");
      const supplyCoverageComplete = suppliesMeta.status === "fresh";
      const riskCoverageComplete = overallMeta.status === "fresh" && productionMeta.status === "fresh" && supplyCoverageComplete && providerCoverageComplete;
      const riskCountValue = highRisks.length ? formatInteger(highRisks.length) : (riskCoverageComplete ? "0" : null);
      const riskCountStatus = highRisks.length ? "danger" : (riskCoverageComplete ? "ready" : "partial");
      const riskCountHint = highRisks.length
        ? `${riskCoverageComplete ? "Подтверждено" : "Не менее"} ${highRisks.length}: данные, производство и поставки`
        : (riskCoverageComplete ? "Все источники проверены" : "Проверены не все источники — ноль не подтверждён");
      const notice = overallMeta.status && overallMeta.status !== "fresh"
        ? `<div class="analytics-overview-notice warn"><div><b>Данные доступны частично</b><span>${escapeHtml(overallWarnings.slice(0, 3).join(" · ") || "Некоторые источники недоступны или устарели; они не подменены нулями.")}</span></div><button type="button" class="small-button secondary" data-analytics-overview-action="refresh">Обновить</button></div>`
        : "";
      const kpis = `<div class="analytics-overview-kpis">
        ${displayMetric("recognized_sales", moneyValue, "Продажи / GMV")}
        ${displayMetric("contribution_margin", moneyValue, "Маржинальный доход")}
        ${displayMetric("net_payout", moneyValue, "После удержаний")}
        ${displayMetric("orders", formatInteger, "Заказы")}
        ${displayMetric("stock_available", formatInteger, "Остатки на площадках")}
        ${analyticsHubMetricCard("Производство: план / факт", productionDisplay, "", planKnown && factKnown ? `${production.start_date || ""} — ${production.end_date || ""}` : "Производственный источник недоступен", production.meta && production.meta.status || "unavailable")}
        ${analyticsHubMetricCard("Критические сигналы", riskCountValue, "", riskCountHint, riskCountStatus)}
      </div>`;

      const financeRows = payload.series && Array.isArray(payload.series.finance) ? payload.series.finance : [];
      const chartModels = providers.map((provider) => {
        const key = provider.marketplace === "wildberries" ? "wildberries" : "ozon";
        const metricStatuses = provider.metric_status && typeof provider.metric_status === "object" ? provider.metric_status : {};
        const financeStatus = metricStatuses.net_payout || "unknown";
        const commercialRows = financeRows
          .filter((row) => row[key] !== null && row[key] !== undefined)
          .map((row) => ({date: row.date, value: Number(row[key])}));
        const blockedStatuses = new Set(["error", "permission_required", "unavailable", "no_data", "unknown", "disconnected"]);
        const statusSuffix = ["fresh", "ready", "success"].includes(financeStatus) ? "" : ` · ${qualityStatusLabels[financeStatus] || financeStatus}`;
        return {key, label: provider.label || key, status: financeStatus, commercialAvailable: commercialRows.length > 0 && !blockedStatuses.has(financeStatus), commercialLabel: `после удержаний${statusSuffix}`, commercialRows};
      });
      const providerCards = providers.map((provider) => {
        const status = provider.status || "unknown";
        const providerMeta = provider.meta && typeof provider.meta === "object" ? provider.meta : {};
        const metricStatuses = provider.metric_status && typeof provider.metric_status === "object" ? provider.metric_status : {};
        const warnings = Array.isArray(providerMeta.warnings) ? providerMeta.warnings.filter(Boolean) : [];
        const freshness = analyticsHubFreshness(provider.last_sync_at || providerMeta.last_successful_sync_at);
        const fields = [
          ["products", "Товары", provider.products, "шт."],
          ["net_payout", "После удержаний", provider.net_payout, "₽"],
          ["orders", "Заказы", provider.orders, "шт."],
          ["stock_available", "Остаток", provider.stock_available, "шт."],
        ];
        return `<div class="analytics-provider-card"><div class="analytics-provider-head"><b>${escapeHtml(provider.label || provider.marketplace || "Площадка")}</b><span class="status-chip ${providerStatusClass(status)}">${escapeHtml(qualityStatusLabels[status] || status)}</span></div><div class="analytics-provider-metrics">${fields.map(([key,label,value,unit]) => { const valueStatus = metricStatuses[key] || (value === null || value === undefined ? "no_data" : status); const statusText = ["fresh", "ready", "success"].includes(valueStatus) ? "подтверждено" : (qualityStatusLabels[valueStatus] || valueStatus); return `<div class="analytics-provider-metric"><span>${escapeHtml(label)}</span><b>${value === null || value === undefined ? "—" : unit === "₽" ? escapeHtml(marketplaceMoney(Number(value))) : `${escapeHtml(formatInteger(value))} ${unit}`}</b><small>${escapeHtml(statusText)}</small></div>`; }).join("")}</div><div class="analytics-chart-source">${provider.last_sync_at ? `Sync: ${escapeHtml(freshness.age || provider.last_sync_at)}.` : "Время успешной синхронизации не получено."}${warnings.length ? ` ${escapeHtml(warnings.slice(0, 2).join(" · "))}` : ""}</div></div>`;
      }).join("");

      const riskRows = risks.slice(0, 8);
      const risksBlock = riskRows.length
        ? `<div class="analytics-risk-list">${riskRows.map((row) => `<div class="analytics-risk-row"><div class="analytics-risk-copy"><b>${escapeHtml(row.title || "Риск")}</b><span>${escapeHtml(row.reason || row.detail || "Требуется проверка")}${row.action ? ` · ${escapeHtml(row.action)}` : ""}</span></div><span class="status-chip ${String(row.severity).toLowerCase() === "high" ? "warn" : "gray"}">${escapeHtml(row.marketplace || row.type || row.entity_type || "контроль")}</span></div>`).join("")}</div>`
        : riskCoverageComplete
          ? `<div class="marketplace-chart-empty"><b>Критичных рисков не найдено</b><span>Все источники проверены; подтверждённых отклонений нет.</span></div>`
          : `<div class="marketplace-chart-empty"><b>Проверка рисков неполная</b><span>Часть источников недоступна или устарела, поэтому ноль рисков не подтверждён.</span></div>`;
      const matrixBlock = `<div class="marketplace-chart-empty"><b>SKU-матрица пока недоступна</b><span>Действия «пополнить / в производство» появятся после server-side сопоставления current-остатков с производственными SKU. Старые строки не используются.</span></div>`;
      const criticalSupplyStatuses = new Set(["SHORTAGE", "SYNC_ERROR", "PARTIALLY_ACCEPTED", "DOCUMENTS_REQUIRED"]);
      const supplyStatusLabels = {EXTERNAL_DRAFT:"Черновик",PLANNED:"Запланирована",WAITING_RESERVATION:"Ожидает резерв",SHORTAGE:"Дефицит",READY_TO_PICK:"Готова к отбору",PICKING:"Отбор",PICKED:"Отобрана",PACKING:"Упаковка",DOCUMENTS_REQUIRED:"Нужны документы",READY_TO_HANDOVER:"К передаче",HANDED_OVER:"Передана",ACCEPTING:"Приёмка",ACCEPTED:"Принята",PARTIALLY_ACCEPTED:"Принята частично",SHIPPED_FROM_PRODUCTION:"Отгружено на производстве",CANCELLED:"Отменена",SYNC_ERROR:"Ошибка sync"};
      const suppliesBlock = supplies.length
        ? `<div class="analytics-supply-list">${supplies.slice(0, 8).map((row) => { const status = String(row.canonical_status || row.status || "UNKNOWN"); return `<div class="analytics-supply-row"><div class="analytics-supply-copy"><b>${escapeHtml(row.marketplace === "wildberries" ? "Wildberries" : "Ozon")} · ${escapeHtml(row.external_supply_id || row.number || "без номера")}</b><span>${escapeHtml(row.destination_name || "направление не указано")}${row.total_quantity !== null && row.total_quantity !== undefined ? ` · ${escapeHtml(row.total_quantity)} шт.` : ""}${row.unmatched_count ? ` · не сопоставлено ${escapeHtml(row.unmatched_count)}` : ""}</span></div><span class="status-chip ${criticalSupplyStatuses.has(status) ? "warn" : "gray"}">${escapeHtml(supplyStatusLabels[status] || status)}</span></div>`; }).join("")}</div>`
        : supplyCoverageComplete
          ? `<div class="marketplace-chart-empty"><b>Активных поставок нет</b><span>Источник поставок проверен; подтверждён пустой список.</span></div>`
          : `<div class="marketplace-chart-empty"><b>Поставки не подтверждены</b><span>Пустая локальная таблица не считается доказательством нулевого количества у площадок.</span></div>`;

      const qualityRows = providers.map((provider) => {
        const status = provider.status || "unknown";
        const providerMeta = provider.meta && typeof provider.meta === "object" ? provider.meta : {};
        const warning = Array.isArray(providerMeta.warnings) ? providerMeta.warnings[0] : "";
        return `<div class="analytics-quality-row"><div class="analytics-quality-copy"><b>${escapeHtml(provider.label || provider.marketplace)}</b><span>${escapeHtml(provider.last_sync_at || providerMeta.last_successful_sync_at || "Нет подтверждённого времени sync")}${warning ? ` · ${escapeHtml(warning)}` : ""}</span></div><span class="status-chip ${providerStatusClass(status)}">${escapeHtml(qualityStatusLabels[status] || status)}</span></div>`;
      }).join("");
      const ozonDatasets = quality.ozon && Array.isArray(quality.ozon.datasets) ? quality.ozon.datasets : [];
      const wbCapabilities = quality.wildberries && Array.isArray(quality.wildberries.capabilities) ? quality.wildberries.capabilities : [];
      const datasetChips = [
        ...ozonDatasets.map((row) => `<span class="status-chip ${providerStatusClass(row.freshness || row.status)}">Ozon ${escapeHtml({catalog:"каталог",prices:"цены",stocks:"остатки"}[row.dataset] || row.dataset)} · ${escapeHtml(qualityStatusLabels[row.freshness] || qualityStatusLabels[row.status] || row.status || "unknown")}</span>`),
        ...wbCapabilities.map((row) => `<span class="status-chip ${providerStatusClass(row.status === "available" ? "fresh" : row.status)}">WB ${escapeHtml(row.capability || "источник")} · ${escapeHtml(qualityStatusLabels[row.status] || (row.status === "available" ? "актуально" : row.status) || "unknown")}</span>`),
      ].join("");

      mainButton.hidden = true;
      mount.innerHTML = `${hubHead}<div class="analytics-overview">${periodBar}${notice}${kpis}
        <div class="analytics-overview-grid"><section class="card analytics-overview-section"><div class="section-title"><b>После удержаний: динамика</b><span>${escapeHtml(periodLabel)}</span></div>${analyticsHubCombinedChart(chartModels)}<div class="analytics-chart-source">Серии строятся сервером из Decimal-значений. Если источник недоступен, линия отсутствует, а не становится нулевой.</div></section><section class="card analytics-overview-section"><div class="section-title"><b>Площадки</b><span>${providers.filter((row) => row.configured).length} подключено</span></div><div class="analytics-provider-list">${providerCards || `<div class="marketplace-chart-empty"><b>Площадки не настроены</b><span>Нет доступных коннекторов.</span></div>`}</div></section></div>
        <div class="analytics-three-grid"><section class="card analytics-overview-section"><div class="section-title"><b>Критические и товарные риски</b><span>${riskCoverageComplete || risks.length ? escapeHtml(risks.length) : "—"}</span></div>${risksBlock}</section><section class="card analytics-overview-section"><div class="section-title"><b>Остатки → производство</b><span>по подтверждённым данным</span></div>${matrixBlock}</section><section class="card analytics-overview-section"><div class="section-title"><b>Поставки</b><span>${supplyCoverageComplete || supplies.length ? escapeHtml(supplies.length) : "—"}</span></div>${suppliesBlock}</section></div>
        <section class="card analytics-overview-section"><div class="section-title"><b>Качество и свежесть данных</b><span>${escapeHtml(qualityStatusLabels[overallMeta.status] || overallMeta.status || "источники")}</span></div><div class="analytics-quality-list">${qualityRows}</div>${datasetChips ? `<div class="analytics-chart-legend">${datasetChips}</div>` : ""}</section>
      </div>`;
    }

    function renderAnalyticsHub() {
      const pages = [
        ["general", "⌂", "Обзор"], ["sales", "↗", "Продажи"], ["products", "▤", "Товары"],
        ["inventory", "▦", "Остатки"], ["production", "⚙", "Производство"], ["supplies", "↓", "Поставки"],
        ["finance", "₽", "Финансы"], ["map", "○", "Карта"], ["data-quality", "✓", "Качество данных"],
      ];
      const allowed = new Set(pages.map(([id]) => id));
      const page = allowed.has(state.analyticsHubTab) ? state.analyticsHubTab : "general";
      state.analyticsHubTab = page;
      const overviewState = state.analyticsOverview || {};
      const payload = overviewState.payload && typeof overviewState.payload === "object" ? overviewState.payload : {};
      const root = state.marketplaceData && state.marketplaceData.payload && typeof state.marketplaceData.payload === "object" ? state.marketplaceData.payload : {};
      const marketplace = ["ozon", "wildberries"].includes(state.marketplaceProvider) ? state.marketplaceProvider : "all";
      const providerRoot = marketplace === "wildberries" && root.wildberries && typeof root.wildberries === "object" ? root.wildberries : root;
      const providers = Array.isArray(payload.providers) ? payload.providers : [];
      const metricRows = Array.isArray(payload.metrics) ? payload.metrics : [];
      const metric = (code) => metricRows.find((row) => row.code === code || row.key === code) || {value: null, status: "unavailable"};
      const production = payload.production && typeof payload.production === "object" ? payload.production : {};
      const suppliesEnvelope = payload.supplies && typeof payload.supplies === "object" ? payload.supplies : {};
      const supplyRows = Array.isArray(suppliesEnvelope.shipments) ? suppliesEnvelope.shipments : Array.isArray(suppliesEnvelope.rows) ? suppliesEnvelope.rows : [];
      const risks = Array.isArray(payload.risks) ? payload.risks : [];
      const products = Array.isArray(providerRoot.products_rows) ? providerRoot.products_rows : [];
      const orders = Array.isArray(providerRoot.orders_rows) ? providerRoot.orders_rows : [];
      const period = payload.period && payload.period.label ? payload.period.label : marketplacePeriodMeta(state.marketplacePeriod).label;
      const status = String((payload.meta && payload.meta.status) || (overviewState.loading ? "loading" : overviewState.error ? "error" : "unknown"));
      const businessStatus = ["fresh", "ready", "success"].includes(status)
        ? ["Данные актуальны", "ok"]
        : ["partial", "attention"].includes(status) ? ["Данные загружены частично", "partial"]
        : status === "stale" ? ["Обновление задерживается", "stale"]
        : ["Показатель пока недоступен", "unknown"];
      const fmt = (value) => value === null || value === undefined ? "—" : Number(value).toLocaleString("ru-RU", {maximumFractionDigits: 0});
      const money = (value) => value === null || value === undefined ? "—" : `${Number(value).toLocaleString("ru-RU", {maximumFractionDigits: 0})} ₽`;
      const safeValue = (row, formatter = fmt) => row && row.value !== null && row.value !== undefined ? formatter(row.value) : "—";
      const kpi = (label, value, hint, tone = "") => `<article class="ac-kpi ${tone}"><span>${escapeHtml(label)}</span><strong>${escapeHtml(value)}</strong><small>${escapeHtml(hint || "Показатель пока недоступен")}</small></article>`;
      const empty = (title, text, action = "") => `<div class="ac-empty"><b>${escapeHtml(title)}</b><span>${escapeHtml(text)}</span>${action ? `<button type="button" class="small-button secondary" data-ac-action="${escapeHtml(action)}">Перейти к настройке</button>` : ""}</div>`;
      const panel = (title, meta, body, wide = "") => `<section class="ac-panel ${wide}"><div class="ac-panel-head"><h3>${escapeHtml(title)}</h3><span>${escapeHtml(meta || "")}</span></div>${body}</section>`;
      const table = (headers, rows, emptyText) => rows.length ? `<div class="ac-table-wrap"><table class="ac-table"><thead><tr>${headers.map((head) => `<th>${escapeHtml(head)}</th>`).join("")}</tr></thead><tbody>${rows.join("")}</tbody></table></div>` : empty("Нет данных", emptyText);
      const providerFilter = (row) => marketplace === "all" || String(row.marketplace || row.provider || "ozon").toLowerCase().includes(marketplace === "wildberries" ? "wild" : "ozon");
      const filteredRisks = risks.filter(providerFilter);
      const providerCards = providers.filter(providerFilter);
      const search = String(state.analyticsSearch || "").trim().toLowerCase();
      const filteredProducts = products.filter((row) => !search || [row.name, row.product_name, row.offer_id, row.article, row.sku, row.barcode, row.color, row.size].some((value) => String(value || "").toLowerCase().includes(search)));
      const chartModels = providers.filter(providerFilter).map((provider) => {
        const key = provider.marketplace === "wildberries" ? "wildberries" : "ozon";
        const financeRows = payload.series && Array.isArray(payload.series.finance) ? payload.series.finance : [];
        const rows = financeRows.filter((row) => row[key] !== null && row[key] !== undefined).map((row) => ({date: row.date, value: Number(row[key])}));
        return {key, label: provider.label || key, status: provider.status || "unknown", commercialAvailable: rows.length > 0, commercialLabel: "после удержаний", commercialRows: rows};
      });
      const nav = pages.map(([id, icon, label]) => `<button type="button" class="${page === id ? "active" : ""}" data-ac-page="${id}"><i>${icon}</i><span>${label}</span></button>`).join("");
      const marketplaceSwitch = `<div class="ac-market-switch" aria-label="Маркетплейс"><button data-ac-provider="all" class="${marketplace === "all" ? "active all" : ""}">Все</button><button data-ac-provider="ozon" class="${marketplace === "ozon" ? "active ozon" : ""}">Ozon</button><button data-ac-provider="wildberries" class="${marketplace === "wildberries" ? "active wb" : ""}">WB</button></div>`;
      const periodOptions = [["7d","7 дней"],["30d","30 дней"],["month","Месяц"],["previous-month","Прошлый месяц"]];
      const filterbar = `<div class="ac-filterbar"><label><span>Период</span><select id="analyticsHubPeriod">${periodOptions.map(([id,label]) => `<option value="${id}" ${state.marketplacePeriod === id ? "selected" : ""}>${label}</option>`).join("")}</select></label><span class="ac-period-label">${escapeHtml(period)}</span><button type="button" data-ac-action="refresh">Обновить</button></div>`;
      const sourceState = overviewState.loading ? `<div class="ac-skeleton"></div>` : overviewState.error ? empty("Не удалось обновить данные", "Структура экрана сохранена. Повторите загрузку или откройте диагностику.", "diagnostics") : "";

      function renderOverviewPage() {
        const sales = metric("recognized_sales"), net = metric("net_payout"), margin = metric("contribution_margin"), orderMetric = metric("orders"), stock = metric("stock_available");
        const productionValue = production.plan !== null && production.plan !== undefined && production.fact !== null && production.fact !== undefined ? `${fmt(production.fact)} / ${fmt(production.plan)}` : "—";
        const cards = `<div class="ac-kpis">${kpi("Продажи", safeValue(sales, money), "Начисления за период")}${kpi("После удержаний", safeValue(net, money), "Чистые начисления")}${kpi("Маржинальный доход", safeValue(margin, money), "По доступным данным")}${kpi("Заказы", safeValue(orderMetric), "За выбранный период")}${kpi("Остатки", safeValue(stock), "На складах площадок")}${kpi("Производство", productionValue, "Факт / план")}</div>`;
        const providerRows = providerCards.map((row) => `<div class="ac-list-row"><div><b>${escapeHtml(row.label || row.marketplace || "Площадка")}</b><span>${escapeHtml(row.last_sync_at || "Время обновления не подтверждено")}</span></div><strong>${escapeHtml(row.status === "fresh" ? "Актуально" : row.status === "stale" ? "Задерживается" : "Частично")}</strong></div>`).join("");
        const riskRows = filteredRisks.slice(0, 5).map((row) => `<div class="ac-list-row"><div><b>${escapeHtml(row.title || "Товарный риск")}</b><span>${escapeHtml(row.reason || row.detail || "Требует внимания")}</span></div><strong>${escapeHtml(row.severity === "high" ? "Важно" : "Проверить")}</strong></div>`).join("");
        const supplyList = supplyRows.filter(providerFilter).slice(0, 5).map((row) => `<div class="ac-list-row"><div><b>${escapeHtml(row.name || row.supply_id || row.shipment_id || "Поставка")}</b><span>${escapeHtml(row.status_label || row.status || "Статус не указан")}</span></div><strong>${escapeHtml(row.quantity !== undefined ? fmt(row.quantity) : "")}</strong></div>`).join("");
        const stages = Array.isArray(production.stages) ? production.stages.slice(0, 5) : [];
        const stageRows = stages.map((row) => `<div class="ac-list-row"><div><b>${escapeHtml(row.stage || row.name || "Этап")}</b><span>${fmt(row.tasks || 0)} заданий</span></div><strong>${fmt(row.quantity || 0)} шт.</strong></div>`).join("");
        const recommendations = filteredRisks.slice(0, 3).map((row) => `<div class="ac-recommendation"><b>${escapeHtml(row.title || "Проверить товар")}</b><span>${escapeHtml(row.action || row.recommendation || row.reason || "Откройте детальную карточку и проверьте источник данных.")}</span></div>`).join("");
        return `${filterbar}${cards}${sourceState}<div class="ac-grid">${panel("Продажи и финансы", period, analyticsHubCombinedChart(chartModels), "span-8")}${panel("Сравнение площадок", `${providerCards.length} источника`, providerRows || empty("Нет подключённых площадок", "Подключите Ozon или Wildberries в настройках."), "span-4")}${panel("Товарные риски", `${filteredRisks.length} сигналов`, riskRows || empty("Критических рисков нет", "Новых подтверждённых рисков за период не найдено."), "span-4")}${panel("Остатки → производство", "Реальные этапы", stageRows || empty("Связь пока недоступна", "Производственные этапы не были получены."), "span-4")}${panel("Поставки", `${supplyRows.filter(providerFilter).length} записей`, supplyList || empty("Поставок нет", "За выбранный период поставки не найдены."), "span-4")}${panel("Рекомендации", "На основе рисков", recommendations || empty("Рекомендаций нет", "Данных достаточно или источники пока не сформировали рекомендации."), "span-12")}</div>`;
      }

      function renderSalesPage() {
        const orderRows = orders.slice(0, 100).map((row) => `<tr><td>${escapeHtml(row.created_at || row.shipment_date || "—")}</td><td>${escapeHtml(row.order_id || row.posting_number || row.id || "—")}</td><td>${escapeHtml(row.product_name || row.name || row.offer_id || "—")}</td><td>${escapeHtml(row.status || "—")}</td><td>${escapeHtml(row.amount !== undefined ? money(row.amount) : row.price !== undefined ? money(row.price) : "—")}</td></tr>`);
        return `${filterbar}<div class="ac-kpis">${kpi("Продажи", safeValue(metric("recognized_sales"), money), "Начисления")}${kpi("Заказы", safeValue(metric("orders")), "Подтверждённые заказы")}${kpi("После удержаний", safeValue(metric("net_payout"), money), "К перечислению")}</div><div class="ac-grid">${panel("Динамика продаж", period, analyticsHubCombinedChart(chartModels), "span-8")}${panel("Сравнение Ozon / Wildberries", "Реальные источники", providerCards.map((row) => `<div class="ac-list-row"><b>${escapeHtml(row.label || row.marketplace)}</b><strong>${escapeHtml(row.status === "fresh" ? "Актуально" : "Частично")}</strong></div>`).join("") || empty("Нет данных", "Площадки не вернули продажи."), "span-4")}${panel("Заказы", `${orders.length} записей`, table(["Дата","Заказ","Товар","Статус","Сумма"], orderRows, "Заказы за выбранный период не получены."), "span-12")}</div>`;
      }

      function renderProductsPage() {
        const rows = filteredProducts.slice(0, 300).map((row) => `<tr><td>${escapeHtml(row.name || row.product_name || "—")}</td><td>${escapeHtml(row.offer_id || row.article || "—")}</td><td>${escapeHtml(row.color || "—")}</td><td>${escapeHtml(row.size || "—")}</td><td>${escapeHtml(row.barcode || "—")}</td><td>${escapeHtml(row.available !== undefined ? fmt(row.available) : "—")}</td></tr>`);
        return `<div class="ac-toolbar"><label class="ac-page-search"><span>Поиск по товару, артикулу или штрихкоду</span><input id="analyticsSearch" value="${escapeHtml(state.analyticsSearch || "")}" placeholder="Название, артикул, штрихкод"></label><span>${fmt(filteredProducts.length)} из ${fmt(products.length)}</span></div><div class="ac-grid">${panel("Каталог SKU", `${filteredProducts.length} позиций`, table(["Товар","Артикул","Цвет","Размер","Штрихкод","Остаток"], rows, "Каталог площадки пока не загружен."), "span-12")}</div>`;
      }

      function renderInventoryPage() {
        const rows = filteredProducts.filter((row) => row.available !== undefined).slice(0, 300).map((row) => `<tr><td>${escapeHtml(row.name || row.product_name || "—")}</td><td>${escapeHtml(row.offer_id || row.article || "—")}</td><td>${escapeHtml(row.size || "—")}</td><td>${escapeHtml(row.color || "—")}</td><td>${fmt(row.available || 0)}</td><td>${fmt(row.reserved || 0)}</td></tr>`);
        const riskList = filteredRisks.slice(0, 8).map((row) => `<div class="ac-list-row"><div><b>${escapeHtml(row.title || "Риск остатка")}</b><span>${escapeHtml(row.reason || "Требует проверки")}</span></div><strong>${escapeHtml(row.severity === "high" ? "Важно" : "Проверить")}</strong></div>`).join("");
        return `<div class="ac-kpis">${kpi("Доступно", safeValue(metric("stock_available")), "На площадках")}${kpi("SKU", fmt(products.length), "Загружено из каталога")}${kpi("Риски", fmt(filteredRisks.length), "Товарные сигналы")}</div><div class="ac-grid">${panel("Остатки по SKU", `${rows.length} строк`, table(["Товар","Артикул","Размер","Цвет","Доступно","Резерв"], rows, "Остатки выбранной площадки пока недоступны."), "span-8")}${panel("Что передать в производство", "На основе подтверждённых рисков", riskList || empty("Заданий нет", "Недостаток товара не подтверждён или данные ещё загружаются."), "span-4")}</div>`;
      }

      function renderProductionPage() {
        const stages = Array.isArray(production.stages) ? production.stages : [];
        const alerts = Array.isArray(production.alerts) ? production.alerts : [];
        const stageRows = stages.map((row) => `<tr><td>${escapeHtml(row.stage || row.name || "—")}</td><td>${fmt(row.tasks || 0)}</td><td>${fmt(row.free || 0)}</td><td>${fmt(row.quantity || 0)}</td><td>${fmt(row.overdue || 0)}</td></tr>`);
        const alertRows = alerts.slice(0, 12).map((row) => `<div class="ac-list-row"><div><b>${escapeHtml(row.title || "Отклонение")}</b><span>${escapeHtml(row.detail || "Требует внимания")}</span></div><strong>${escapeHtml(row.type === "overdue" ? "Просрочено" : "Проверить")}</strong></div>`).join("");
        return `<div class="ac-kpis">${kpi("План", production.plan !== undefined && production.plan !== null ? fmt(production.plan) : "—", "Изделий")}${kpi("Факт", production.fact !== undefined && production.fact !== null ? fmt(production.fact) : "—", "Изделий")}${kpi("В работе", production.active_quantity !== undefined && production.active_quantity !== null ? fmt(production.active_quantity) : "—", "Активный WIP")}${kpi("Брак", production.defect_quantity !== undefined && production.defect_quantity !== null ? fmt(production.defect_quantity) : "—", "Подтверждённые записи")}</div><div class="ac-grid">${panel("Этапы производства", `${stages.length} этапов`, table(["Этап","Задания","Свободно","Количество","Просрочено"], stageRows, "Активных производственных этапов нет."), "span-8")}${panel("Требует внимания", `${alerts.length} сигналов`, alertRows || empty("Отклонений нет", "Новых подтверждённых производственных отклонений не найдено."), "span-4")}</div>`;
      }

      function renderSuppliesPage() {
        const rows = supplyRows.filter(providerFilter).map((row) => `<tr><td>${escapeHtml(row.marketplace || row.provider || "—")}</td><td>${escapeHtml(row.name || row.supply_id || row.shipment_id || "—")}</td><td>${escapeHtml(row.status_label || row.status || "—")}</td><td>${escapeHtml(row.destination || row.warehouse_name || "—")}</td><td>${escapeHtml(row.quantity !== undefined ? fmt(row.quantity) : "—")}</td><td>${escapeHtml(row.updated_at || row.date || "—")}</td></tr>`);
        return `<div class="ac-kpis">${kpi("Поставки", fmt(rows.length), "За выбранный период")}${kpi("Площадка", marketplace === "all" ? "Все" : marketplace === "ozon" ? "Ozon" : "Wildberries", "Текущий фильтр")}</div><div class="ac-grid">${panel("Поставки", `${rows.length} записей`, table(["Площадка","Поставка","Статус","Склад","Количество","Обновлено"], rows, "Поставок за выбранный период нет."), "span-12")}</div>`;
      }

      function renderFinancePage() {
        const recognized = metric("recognized_sales"), net = metric("net_payout"), margin = metric("contribution_margin");
        const waterfall = [
          ["Продажи", recognized.value, "positive"],
          ["Удержания", recognized.value !== null && recognized.value !== undefined && net.value !== null && net.value !== undefined ? Number(net.value) - Number(recognized.value) : null, "negative"],
          ["После удержаний", net.value, "total"],
          ["Маржинальный доход", margin.value, "total"],
        ].filter(([,value]) => value !== null && value !== undefined);
        const max = Math.max(1, ...waterfall.map(([,value]) => Math.abs(Number(value))));
        const bars = waterfall.length ? `<div class="ac-waterfall">${waterfall.map(([label,value,tone]) => `<div class="${tone}"><span>${escapeHtml(label)}</span><i style="--bar:${Math.max(5, Math.abs(Number(value)) / max * 100)}%"></i><strong>${escapeHtml(money(value))}</strong></div>`).join("")}</div>` : empty("Финансы пока недоступны", "Площадка не предоставила подтверждённые начисления и удержания.");
        const compareRows = providerCards.map((row) => `<tr><td>${escapeHtml(row.label || row.marketplace || "—")}</td><td>${escapeHtml(row.status === "fresh" ? "Данные актуальны" : row.status === "stale" ? "Обновление задерживается" : "Данные загружены частично")}</td><td>${escapeHtml(row.last_sync_at || "—")}</td></tr>`);
        return `${filterbar}<div class="ac-kpis">${kpi("Продажи", safeValue(recognized, money), "За период")}${kpi("После удержаний", safeValue(net, money), "К перечислению")}${kpi("Маржинальный доход", safeValue(margin, money), "По доступным расходам")}</div><div class="ac-grid">${panel("Финансовая динамика", period, analyticsHubCombinedChart(chartModels), "span-8")}${panel("Финансовый waterfall", "Только доступные компоненты", bars, "span-4")}${panel("Источники", `${providerCards.length} площадки`, table(["Площадка","Состояние","Обновлено"], compareRows, "Финансовые источники не подключены."), "span-12")}</div>`;
      }

      function renderMapPage() {
        return `<div class="ac-grid">${panel("Карта России", "Склады и продажи по регионам", `<div class="ac-map"><div class="ac-russia-shape"></div>${empty("Региональные данные пока недоступны", "Карта готова к отображению складов и продаж, когда API передаст региональную разбивку.")}</div>`, "span-8")}${panel("Регионы", "Без выдуманных значений", empty("Нет региональной детализации", "Ozon и Wildberries пока не передали данные, необходимые для достоверного рейтинга регионов."), "span-4")}</div>`;
      }

      function renderQualityPage() {
        const rows = providerCards.map((row) => `<tr><td>${escapeHtml(row.label || row.marketplace || "—")}</td><td>${escapeHtml(row.status === "fresh" ? "Данные актуальны" : row.status === "stale" ? "Обновление задерживается" : row.status === "partial" ? "Данные загружены частично" : "Показатель пока недоступен")}</td><td>${escapeHtml(row.last_sync_at || "—")}</td></tr>`);
        return `<div class="ac-kpis">${kpi("Источники", fmt(providerCards.length), "Подключённые площадки")}${kpi("Состояние", businessStatus[0], "Без технических кодов")}${kpi("Обновлено", payload.generated_at || payload.as_of || "—", "Время аналитического среза")}</div><div class="ac-grid">${panel("Качество данных", "Понятные бизнес-состояния", table(["Источник","Состояние","Последнее обновление"], rows, "Источники аналитики пока не подключены."), "span-8")}${panel("Диагностика", "Для администратора", `<p class="ac-panel-copy">Технические коды, ответы API и журнал синхронизации вынесены из аналитики.</p><button type="button" class="small-button" data-ac-action="diagnostics">Открыть диагностику</button>`, "span-4")}</div>`;
      }

      const renderers = {general: renderOverviewPage, sales: renderSalesPage, products: renderProductsPage, inventory: renderInventoryPage, production: renderProductionPage, supplies: renderSuppliesPage, finance: renderFinancePage, map: renderMapPage, "data-quality": renderQualityPage};
      const title = pages.find(([id]) => id === page)[2];
      mainButton.hidden = true;
      mount.innerHTML = `<div class="ac-shell"><aside class="ac-sidebar"><div class="ac-brand"><b>АНАЛИТИКА</b><span>центр управления</span></div><nav class="ac-nav">${nav}</nav></aside><div class="ac-main"><header class="ac-topbar"><label class="ac-search"><span>⌕</span><input id="analyticsSearchTop" value="${escapeHtml(state.analyticsSearch || "")}" placeholder="Найти товар, артикул, поставку"></label>${marketplaceSwitch}<button type="button" class="ac-sync" data-ac-action="sync">↻ Синхронизировать</button></header><main class="ac-content"><div class="ac-heading"><div><h2>${escapeHtml(title)}</h2><p>Продажи, остатки, производство и качество данных в едином центре.</p></div><span class="ac-business-state ${businessStatus[1]}">${escapeHtml(businessStatus[0])}</span></div>${renderers[page]()}</main></div></div>`;
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
      if (!canAccessMarketplaces() && ["marketplaces", "analytics"].includes(state.workspace)) {
        state.workspace = "production";
        state.screen = "shift";
      }
      if (!['production', 'warehouse', 'marketplaces', 'analytics'].includes(state.workspace)) {
        state.workspace = state.screen === "warehouse" ? "warehouse" : "production";
      }
      if (state.workspace === "warehouse" && !["warehouse", "profile"].includes(state.screen)) {
        state.screen = "warehouse";
      }
      if (state.workspace === "marketplaces") state.screen = "marketplaces";
      if (state.workspace === "analytics") state.screen = "analytics";

      const allowedProductionScreens = state.data.is_admin
        ? ["shift", "analytics", "orders", "admin", "passport", "profile"]
        : ["shift", "report", "analytics", "orders", "admin", "passport", "profile"];
      if (state.workspace === "production" && !allowedProductionScreens.includes(state.screen)) {
        state.screen = "shift";
      }
      document.getElementById("roleLabel").textContent = roleLabel();
      const isWarehouseWorkspace = state.workspace === "warehouse";
      const isMarketplaceWorkspace = state.workspace === "marketplaces";
      const isAnalyticsWorkspace = state.workspace === "analytics";
      document.body.classList.toggle("analytics-mode", isAnalyticsWorkspace);
      if (!isMarketplaceWorkspace) mainButton.hidden = false;
      document.body.classList.toggle("warehouse-workspace", isWarehouseWorkspace);
      document.body.classList.toggle("warehouse-v2-enabled", Boolean(isWarehouseWorkspace && state.data.features && state.data.features.warehouse_ui_v2));
      document.body.classList.toggle("marketplace-workspace", isMarketplaceWorkspace);
      document.body.classList.toggle("has-wms-access", canAccessWms());
      const mobileWorkspaceNav = document.getElementById("mobileWorkspaceNav");
      mobileWorkspaceNav.hidden = !canAccessWms() && !canAccessMarketplaces();
      document.querySelectorAll("[data-workspace]").forEach((button) => {
        if (button.dataset.workspace === "warehouse") button.hidden = !canAccessWms();
        if (button.dataset.workspace === "marketplaces") button.hidden = !canAccessMarketplaces();
        if (button.dataset.workspace === "analytics") button.hidden = !canAccessMarketplaces();
        const isActive = button.dataset.workspace === "warehouse" ? isWarehouseWorkspace : button.dataset.workspace === "marketplaces" ? isMarketplaceWorkspace : button.dataset.workspace === "analytics" ? isAnalyticsWorkspace : !isWarehouseWorkspace && !isMarketplaceWorkspace && !isAnalyticsWorkspace;
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
      if (state.screen === "analytics") state.workspace === "analytics" ? renderAnalyticsHub() : renderAnalytics();
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
      if ((isMarketplaceWorkspace || isAnalyticsWorkspace) && !state.marketplaceData.loaded && !state.marketplaceData.loading && !state.marketplaceData.error) {
        window.setTimeout(() => refreshMarketplaces({silent: true}), 0);
      }
      if (isAnalyticsWorkspace) {
        const overviewRequest = analyticsOverviewRequest();
        const overviewNeedsLoad = state.analyticsOverview.requestKey !== overviewRequest.key
          || (!state.analyticsOverview.loaded && !state.analyticsOverview.error);
        if (overviewNeedsLoad && !state.analyticsOverview.loading) {
          window.setTimeout(() => refreshAnalyticsOverview({silent: true}), 0);
        }
      }
      if (isMarketplaceWorkspace && state.marketplaceView === "data-quality" && !state.marketplaceQuality.loaded && !state.marketplaceQuality.loading && !state.marketplaceQuality.error) {
        window.setTimeout(() => refreshMarketplaceQuality({silent: true}), 0);
      }
      if (state.data.is_admin && state.workspace === "production" && state.screen === "shift") window.setTimeout(syncWebPushDeviceState, 0);
    }

    function safeRenderAfterState() {
      if (
        isStandaloneWeb
        && !state.marketplaceLocationInitialized
        && window.location.pathname.startsWith("/app/marketplaces")
        && canAccessMarketplaces()
      ) {
        applyMarketplaceLocation();
        state.marketplaceLocationInitialized = true;
        state.workspace = "marketplaces";
        state.screen = "marketplaces";
      }
      try {
        render();
        return;
      } catch (error) {
        console.error("Render failed", error);
      }

      state.workspace = "production";
      if (state.data && state.data.is_admin) {
        state.screen = "admin";
        state.productionScreen = "admin";
        state.adminSection = "employees";
      } else {
        state.screen = "orders";
        state.productionScreen = "orders";
      }
      render();
      showToast("Интерфейс", "Открыт безопасный раздел после ошибки экрана.");
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
        applyMarketplaceLocation();
        state.marketplaceLocationInitialized = true;
        state.workspace = "marketplaces";
        state.screen = "marketplaces";
        syncMarketplaceLocation();
      } else if (workspace === "analytics") {
        if (!canAccessMarketplaces()) {
          showToast("Отчёт", "Аналитический центр доступен только администратору.");
          return;
        }
        if (state.workspace === "production" && !["profile", "passport"].includes(state.screen) && productionScreens.has(state.screen)) state.productionScreen = state.screen;
        state.workspace = "analytics";
        state.screen = "analytics";
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
        safeRenderAfterState();
        if (getCompletionQueue().length && navigator.onLine) window.setTimeout(() => flushCompletionQueue(true), 0);
      } catch (error) {
        state.data = null;
        document.getElementById("roleLabel").textContent = "Нет соединения";
      mount.innerHTML = `<div class="screen-head"><div><h2>Не удалось загрузить приложение</h2><p class="operational-message">${escapeHtml(error.apiMessage || "Проверьте соединение и повторите попытку.")}</p></div></div>`;
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

      const operationsAction = event.target.closest("[data-operations-action]");
      if (operationsAction && state.data && state.data.is_admin) {
        const action = operationsAction.dataset.operationsAction;
        if (action === "create-order") {
          resetOrderDraft();
          setScreen("orders");
          return;
        }
        if (action === "employees" || action === "alerts") {
          state.adminSection = action === "employees" ? "employees" : "feedback";
          setScreen("admin");
          return;
        }
        if (action === "scan") {
          setScreen("orders");
          window.setTimeout(() => openQrScanner("route"), 0);
          return;
        }
      }

      const orderMode = event.target.closest("[data-order-mode]");
      if (orderMode && state.data && state.data.is_admin) {
        if (orderMode.dataset.orderMode === "create") {
          resetOrderDraft();
        } else {
          state.orderMode = orderMode.dataset.orderMode === "board" ? "board" : "list";
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

      const fabricManage = event.target.closest("[data-fabric-manage]");
      if (fabricManage) {
        manageFabricStock(fabricManage);
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

      const wmsShipment = event.target.closest("[data-wms-shipment-number]");
      if (wmsShipment) {
        loadWmsShipment(wmsShipment.dataset.wmsShipmentNumber || "");
        return;
      }

      const wmsShipmentTask = event.target.closest("[data-wms-shipment-task-number]");
      if (wmsShipmentTask) {
        loadWmsShipmentTask(wmsShipmentTask.dataset.wmsShipmentTaskNumber || "");
        return;
      }

      const wmsTaskTab = event.target.closest("[data-wms-task-tab]");
      if (wmsTaskTab) {
        state.wmsShipmentTaskTab = wmsTaskTab.dataset.wmsTaskTab || "required";
        render();
        return;
      }

      const wmsTaskLocation = event.target.closest("[data-wms-task-location]");
      if (wmsTaskLocation) {
        state.wmsShipmentTaskLocation = String(wmsTaskLocation.dataset.wmsTaskLocation || "").trim().toUpperCase();
        state.wmsShipmentTaskScannedAllocationId = "";
        state.wmsShipmentTaskExpectedAllocationId = "";
        render();
        return;
      }

      const wmsTaskProduct = event.target.closest("[data-wms-task-scan-product]");
      if (wmsTaskProduct) {
        state.wmsShipmentTaskScannedAllocationId = "";
        state.wmsShipmentTaskExpectedAllocationId = wmsTaskProduct.dataset.wmsTaskScanProduct || "";
        state.wmsScanField = "shipment_product";
        scanWms("shipment_product");
        return;
      }

      const wmsTaskPick = event.target.closest("[data-wms-task-pick]");
      if (wmsTaskPick) {
        pickWmsShipmentTask(wmsTaskPick.dataset.wmsTaskPick || "");
        return;
      }

      const wmsTaskAction = event.target.closest("[data-wms-task-action]");
      if (wmsTaskAction) {
        const action = wmsTaskAction.dataset.wmsTaskAction;
        if (action === "back") { state.wmsShipmentTaskDetail = null; state.wmsShipmentTaskLocation = ""; state.wmsShipmentTaskScannedAllocationId = ""; state.wmsShipmentTaskExpectedAllocationId = ""; render(); return; }
        if (action === "start") { startWmsShipmentTask(); return; }
        if (action === "confirm") { confirmWmsShipmentTask(); return; }
        if (action === "select-cell") {
          if (state.wmsShipmentTaskExpectedAllocationId) {
            focusWmsHardwareScanner();
            return;
          }
          const input = document.getElementById("wmsShipmentTaskCell");
          state.wmsShipmentTaskLocation = String(input && input.value || "").trim().replace(/^LOC:/i, "").toUpperCase();
          state.wmsShipmentTaskScannedAllocationId = "";
          state.wmsShipmentTaskExpectedAllocationId = "";
          render();
          return;
        }
      }

      const wmsShipmentAction = event.target.closest("[data-wms-shipment-action]");
      if (wmsShipmentAction) {
        const action = wmsShipmentAction.dataset.wmsShipmentAction;
        if (action === "back") state.wmsShipmentDetail = null;
        if (action === "new") { state.wmsShipmentCreate = true; state.wmsShipmentDetail = null; state.wmsShipmentTaskDetail = null; }
        if (action === "cancel") { state.wmsShipmentCreate = false; state.wmsShipmentDraft = {destination: "", comment: "", lines: {}}; }
        if (action === "add") {
          syncWmsShipmentDraft();
          const picker = document.getElementById("wmsShipmentProduct");
          if (!picker || !picker.value) { showToast("Отгрузка", "Выберите товар для добавления."); return; }
          state.wmsShipmentDraft.lines[picker.value] = "1";
        }
        if (action === "submit") { createWmsShipment(); return; }
        render();
        return;
      }

      const wmsShipmentRemove = event.target.closest("[data-wms-shipment-remove]");
      if (wmsShipmentRemove) {
        syncWmsShipmentDraft();
        delete state.wmsShipmentDraft.lines[wmsShipmentRemove.dataset.wmsShipmentRemove];
        render();
        return;
      }

      const wmsShipmentExport = event.target.closest("[data-wms-shipment-export]");
      if (wmsShipmentExport) {
        exportWmsShipment(wmsShipmentExport.dataset.wmsShipmentExport || "xlsx");
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
        // On a phone the map can be several screens high.  The detail card is
        // rendered above it, so deliberately bring it into view after a tap.
        window.setTimeout(() => {
          document.getElementById("wms-location-detail")?.scrollIntoView({behavior: "smooth", block: "start"});
        }, 0);
        return;
      }

      const wmsCellWriteoff = event.target.closest("[data-wms-cell-writeoff]");
      if (wmsCellWriteoff) {
        const locationId = state.wmsSelectedLocationId;
        const rows = wmsAdminStockRows(locationId);
        state.wmsAdminAdjustment = {
          mode: "scrap",
          locationId: String(locationId || ""),
          stockId: String(wmsCellWriteoff.dataset.wmsCellWriteoff || (rows[0] && rows[0].id) || ""),
          quantity: "",
          reason: "",
          targetState: "SCRAPPED",
          returnView: "cell",
        };
        render();
        return;
      }

      const wmsAdminMode = event.target.closest("[data-wms-admin-mode]");
      if (wmsAdminMode) {
        syncWmsAdminAdjustmentFromForm();
        state.wmsAdminAdjustment.mode = wmsAdminMode.dataset.wmsAdminMode === "scrap" ? "scrap" : "inventory";
        state.wmsAdminAdjustment.quantity = "";
        render();
        return;
      }

      const wmsAdminAction = event.target.closest("[data-wms-admin-action]");
      if (wmsAdminAction) {
        if (wmsAdminAction.dataset.wmsAdminAction === "submit") {
          wmsAdminAdjustmentSubmit();
        } else {
          state.wmsAdminAdjustment.quantity = "";
          state.wmsAdminAdjustment.reason = "";
          if (state.wmsAdminAdjustment.returnView === "cell") state.wmsAdminAdjustment.returnView = "";
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
        if (nextView !== state.wmsView && ["putaway", "pick", "inventory"].includes(nextView)) {
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
          if (nextView === "inventory") {
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
        else if (action === "inventory_back") {
          if (state.wmsDraft.productScanned) {
            state.wmsDraft.productName = "";
            state.wmsDraft.productSize = "";
            state.wmsDraft.productColor = "";
            state.wmsDraft.productScanned = false;
            state.wmsDraft.quantity = "";
          } else if (state.wmsDraft.fromLocationScanned) {
            state.wmsDraft.fromLocation = "";
            state.wmsDraft.fromLocationScanned = false;
          } else {
            state.wmsView = "more";
          }
          render();
        }
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
        syncMarketplaceLocation();
        render();
        if (state.marketplaceView === "data-quality") {
          if (state.marketplaceProvider === "wildberries") refreshMarketplaces();
          else refreshMarketplaceQuality({silent: true});
        }
        return;
      }

      const marketplaceFilterAction = event.target.closest("[data-marketplace-filter-action]");
      if (marketplaceFilterAction) {
        const action = marketplaceFilterAction.dataset.marketplaceFilterAction;
        if (action === "toggle") state.marketplaceFiltersOpen = !state.marketplaceFiltersOpen;
        if (action === "apply" || action === "cancel") state.marketplaceFiltersOpen = false;
        if (action === "reset") {
          state.marketplaceFilters = {onlyProblems: false, inStockOnly: false, orderStatus: "all"};
          state.marketplaceFiltersOpen = false;
        }
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
        syncMarketplaceLocation();
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
      const marketplaceSupplyCreate = event.target.closest("[data-marketplace-supply-create]");
      if (marketplaceSupplyCreate) {
        event.preventDefault();
        createMarketplaceShipment(marketplaceSupplyCreate.dataset.marketplaceSupplyCreate || "");
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
        if (marketplaceAction.dataset.marketplaceAction === "quality-refresh") refreshMarketplaceQuality();
        if (marketplaceAction.dataset.marketplaceAction === "phase1a-sync") syncMarketplacePhase1A();
        if (marketplaceAction.dataset.marketplaceAction === "quality-search") searchMarketplaceQualityProducts();
        if (marketplaceAction.dataset.marketplaceAction === "quality-prev") changeMarketplaceQualityPage(-1);
        if (marketplaceAction.dataset.marketplaceAction === "quality-next") changeMarketplaceQualityPage(1);
        return;
      }

      const analyticsOverviewAction = event.target.closest("[data-analytics-overview-action]");
      if (analyticsOverviewAction) {
        if (analyticsOverviewAction.dataset.analyticsOverviewAction === "refresh") {
          state.analyticsOverview.error = "";
          refreshAnalyticsOverview();
        }
        return;
      }

      const analyticsCenterPage = event.target.closest("[data-ac-page]");
      if (analyticsCenterPage) {
        state.analyticsHubTab = analyticsCenterPage.dataset.acPage || "general";
        render();
        return;
      }

      const analyticsCenterProvider = event.target.closest("[data-ac-provider]");
      if (analyticsCenterProvider) {
        state.marketplaceProvider = analyticsCenterProvider.dataset.acProvider || "all";
        render();
        return;
      }

      const analyticsCenterAction = event.target.closest("[data-ac-action]");
      if (analyticsCenterAction) {
        const action = analyticsCenterAction.dataset.acAction;
        if (action === "sync") syncMarketplaces();
        if (action === "refresh") refreshAnalyticsOverview();
        if (action === "diagnostics") {
          state.workspace = "production";
          state.screen = "admin";
          state.productionScreen = "admin";
          state.adminSection = "integrations";
          render();
        }
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

      const boardOrder = event.target.closest("[data-board-order-key]");
      if (boardOrder && state.data && state.data.is_admin) {
        const boardKey = boardOrder.dataset.boardOrderKey || "";
        const allRows = [...currentOrderRows(), ...getCompletedOrderRows()];
        const current = allRows.find((task) => taskIdentity(task) === boardKey);
        if (!current) return;
        state.orderCategory = adminOrderCategoryForTask(current);
        state.adminTaskStatus = orderTaskStatusBucket(current) === "done" ? "done" : "all";
        state.orderMode = "list";
        state.selectedOrder = 0;
        state.selectedOrderKey = boardKey;
        render();
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
        if (state.marketplaceView === "data-quality" && state.marketplaceProvider !== "wildberries") syncMarketplacePhase1A();
        else syncMarketplaces();
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
      const qualitySearch = event.target.closest("#marketplaceQualitySearch");
      if (qualitySearch && event.key === "Enter") {
        event.preventDefault();
        searchMarketplaceQualityProducts();
        return;
      }
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
      if (event.target.closest("#wmsShipmentDestination, #wmsShipmentComment, [data-wms-shipment-qty]")) {
        syncWmsShipmentDraft();
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

      if (cuttingTask && (event.target.matches("[data-contour-key]") || event.target.matches("[data-layer-color]") || event.target.matches("[data-arbitrary-size], [data-arbitrary-color], [data-arbitrary-parts], [data-arbitrary-layers]") || event.target.matches("[data-formation-defect], [data-formation-comment]") || event.target.id === "cuttingProgress")) {
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
        const formationRow = event.target.closest("[data-formation-row]");
        if (formationRow) {
          const formationKey = `${formationRow.dataset.formationSize || ""}|${formationRow.dataset.formationColor || ""}`;
          draft.formation_defects = draft.formation_defects || {};
          draft.formation_comments = draft.formation_comments || {};
          if (event.target.matches("[data-formation-defect]")) {
            draft.formation_defects[formationKey] = event.target.value;
            const total = Number(formationRow.dataset.formationTotal || 0);
            const defect = Math.max(0, Math.min(total, Number(event.target.value || 0)));
            const good = formationRow.querySelector("[data-formation-good]");
            const comment = formationRow.querySelector("[data-formation-comment]");
            if (good) good.textContent = String(total - defect);
            if (comment) comment.disabled = defect <= 0;
          }
          if (event.target.matches("[data-formation-comment]")) {
            draft.formation_comments[formationKey] = event.target.value;
          }
        }
        if (event.target.id === "cuttingProgress") draft.progress = event.target.value;
        state.cuttingStageDrafts[key] = draft;
      }

      if (event.target.id === "feedbackCategory") state.feedbackDraft.category = event.target.value;
      if (event.target.id === "feedbackMessage") state.feedbackDraft.message = event.target.value;
      if (event.target.id === "marketplaceQualitySearch") state.marketplaceQuality.query = event.target.value.slice(0, 200);
      if (["analyticsSearch", "analyticsSearchTop"].includes(event.target.id)) state.analyticsSearch = event.target.value.slice(0, 200);

      if (event.target.closest("#adminStartDate, #adminEndDate, #adminEmployeeId, #adminShiftEndTime")) {
        syncAdminForm();
        if (event.target.id === "adminShiftEndTime") state.adminShiftEndTime = event.target.value;
      }
      if (event.target.closest("#userStartDate, #userEndDate")) syncHistoryForm();
      persistUiState();
    });

    document.addEventListener("change", (event) => {
      if (["analyticsSearch", "analyticsSearchTop"].includes(event.target.id)) {
        state.analyticsSearch = event.target.value.slice(0, 200);
        if (state.analyticsHubTab !== "products") state.analyticsHubTab = "products";
        render();
        return;
      }
      if (event.target.id === "analyticsHubPeriod") {
        state.marketplacePeriod = event.target.value || "7d";
        state.analyticsOverview.loaded = false;
        state.analyticsOverview.payload = null;
        state.analyticsOverview.error = "";
        state.analyticsOverview.requestKey = "";
        render();
        return;
      }
      if (["analyticsHubDateFrom", "analyticsHubDateTo"].includes(event.target.id)) {
        if (event.target.id === "analyticsHubDateFrom") state.marketplaceDateFrom = event.target.value || "";
        if (event.target.id === "analyticsHubDateTo") state.marketplaceDateTo = event.target.value || "";
        if (state.marketplaceDateFrom && state.marketplaceDateTo) state.marketplacePeriod = "custom";
        state.analyticsOverview.loaded = false;
        state.analyticsOverview.payload = null;
        state.analyticsOverview.error = "";
        state.analyticsOverview.requestKey = "";
        render();
        return;
      }
      if (event.target.id === "marketplacePeriod") {
        state.marketplacePeriod = event.target.value || "7d";
        syncMarketplaceLocation();
        render();
        return;
      }
      if (event.target.id === "marketplaceOrderStatus") {
        state.marketplaceFilters.orderStatus = event.target.value || "all";
        return;
      }
      if (event.target.id === "marketplaceInStockOnly") {
        state.marketplaceFilters.inStockOnly = Boolean(event.target.checked);
        return;
      }
      if (event.target.id === "marketplaceOnlyProblems") {
        state.marketplaceFilters.onlyProblems = Boolean(event.target.checked);
        return;
      }
      if (event.target.id === "wmsAdminLocation") {
        state.wmsAdminAdjustment.locationId = event.target.value;
        state.wmsAdminAdjustment.stockId = "";
        state.wmsAdminAdjustment.quantity = "";
        state.wmsAdminAdjustment.reason = "";
        render();
        return;
      }
      if (event.target.id === "wmsAdminStock") {
        syncWmsAdminAdjustmentFromForm();
        state.wmsAdminAdjustment.quantity = "";
        state.wmsAdminAdjustment.reason = "";
        render();
        return;
      }
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
        if (isStandaloneWeb) window.history.replaceState(null, "", "/app");
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
      // Android TSDs honor the manifest after installation; this covers
      // browsers that also expose the Screen Orientation API. iOS simply
      // ignores the unsupported call without affecting the application.
      if (screen.orientation && typeof screen.orientation.lock === "function") {
        try { await screen.orientation.lock("portrait"); } catch (_) {}
      }
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
