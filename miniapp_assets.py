"""Shared HTML assets for Telegram Mini App and the standalone web app."""

MINIAPP_HTML = """<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover">
  <title>Шагаем вместе</title>
  <script src="https://telegram.org/js/telegram-web-app.js"></script>
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
      font-weight: 750;
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
      font-weight: 900;
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
      font-weight: 900;
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
      font-weight: 950;
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
      font-weight: 950;
      line-height: 1.05;
      letter-spacing: 0;
    }

    .app-title small {
      display: block;
      margin-top: 3px;
      color: var(--muted);
      font-size: 10px;
      font-weight: 850;
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
      font-weight: 900;
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
      font-weight: 900;
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
      font-weight: 950;
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
      font-weight: 850;
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
      font-weight: 900;
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
      font-weight: 900;
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
      font-weight: 850;
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
      font-weight: 900;
      font-size: 11px;
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
      font-weight: 900;
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
      font-weight: 900;
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
      font-weight: 850;
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

    .segment-row.warehouse-segments {
      grid-template-columns: repeat(3, minmax(0, 1fr));
    }

    .segment-button {
      min-width: 0;
      min-height: 34px;
      border: none;
      border-radius: 13px;
      padding: 8px 5px;
      background: rgba(255,255,255,.56);
      color: var(--muted);
      font-size: 10.5px;
      line-height: 1.05;
      font-weight: 950;
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
      font-weight: 950;
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
      font-weight: 900;
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
      font-weight: 850;
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
      font-weight: 950;
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
      font-weight: 800;
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
      font-weight: 900;
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
      font-weight: 850;
      line-height: 1.3;
    }

    .route-input-row span:last-child {
      flex: 0 0 auto;
      color: var(--accent-dark);
      font-weight: 950;
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
      font-weight: 900;
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
      font-weight: 900;
      outline: none;
    }

    .cutting-input-row input:focus {
      border-color: rgba(25,89,243,.48);
      box-shadow: 0 0 0 3px rgba(25,89,243,.12);
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
      font-weight: 900;
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
      font-weight: 950;
    }

    .order-foot {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 10px;
      margin-top: 8px;
      color: var(--muted);
      font-size: 12px;
      font-weight: 850;
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
      font-weight: 950;
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
      font-weight: 800;
      line-height: 1.35;
    }

    .trace-code {
      display: inline-flex;
      margin-top: 7px;
      color: var(--accent-dark);
      font-size: 10.5px;
      font-weight: 950;
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
      width: 100%;
      height: 100%;
      object-fit: cover;
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
      font-weight: 950;
    }

    .qr-scanner-actions {
      bottom: 14px;
      justify-content: center;
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
      font-weight: 950;
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
      font-weight: 850;
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
      font-weight: 900;
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
      font-weight: 950;
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
  </style>
</head>
<body>
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
      <button class="icon-btn" id="backBtn" aria-label="Назад">‹</button>
      <div class="app-title">
        <div class="brand-lockup app-brand-lockup">
          <img class="brand-mark" src="/brand/mark.svg" alt="" aria-hidden="true">
          <span class="brand-wordmark"><span class="brand-wordmark-primary">Шагаем</span><span class="brand-wordmark-secondary">вместе</span></span>
        </div>
        <small id="roleLabel">Загрузка</small>
      </div>
      <button class="icon-btn" id="menuBtn" aria-label="Меню">⋯</button>
    </div>

    <div class="body">
      <div class="tabs" id="topTabs" hidden></div>
      <div id="mount"></div>
      <div id="webActionSlot"></div>
    </div>
  </main>

  <button class="main-button" id="mainButton" hidden>Загрузка</button>
  <nav class="bottom-nav" id="bottomNav" aria-label="Навигация приложения" hidden></nav>
  <div class="toast" id="toast"><b></b><span></span></div>
  <section class="qr-scanner" id="qrScanner" aria-label="Сканер QR-кода" hidden>
    <div class="qr-scanner-shell">
      <video id="qrScannerVideo" playsinline muted></video>
      <div class="qr-scanner-frame"></div>
      <div class="qr-scanner-head"><span>QR-код партии</span><button class="qr-scanner-close" id="qrScannerClose" type="button" aria-label="Закрыть">×</button></div>
      <div class="qr-scanner-actions"><button class="small-button" id="qrScannerManual" type="button">Ввести код</button></div>
    </div>
  </section>

  <script>
    const tg = window.Telegram && window.Telegram.WebApp;
    const urlParams = new URLSearchParams(window.location.search);
    const debugTelegramId = urlParams.get("debug_tg_id");
    const queryAuthToken = urlParams.get("auth");
    let storedAuthToken = "";

    try {
      if (queryAuthToken) {
        window.localStorage.setItem("miniapp_auth", queryAuthToken);
      }
      storedAuthToken = window.localStorage.getItem("miniapp_auth") || "";
    } catch (error) {
      storedAuthToken = "";
    }

    const authToken = queryAuthToken || storedAuthToken;
    const telegramUserId = tg && tg.initDataUnsafe && tg.initDataUnsafe.user ? String(tg.initDataUnsafe.user.id || "") : "";
    const isStandaloneWeb = !debugTelegramId && !authToken && !(tg && tg.initData);
    let webCsrfToken = "";
    let webSessionProfile = {};
    let storedWebIdentity = "";
    try {
      storedWebIdentity = window.sessionStorage.getItem("webapp_identity") || "";
    } catch (error) {
      storedWebIdentity = "";
    }
    const authIdentity = debugTelegramId || telegramUserId || storedWebIdentity || (isStandaloneWeb ? "web_anonymous" : "telegram_anonymous");
    const uiStateStorageKey = `miniapp_ui_state_${authIdentity}`;
    const completionQueueKey = `miniapp_completion_queue_${authIdentity}`;
    const persistedUiStateKeys = [
      "screen",
      "selectedOrder",
      "selectedOrderKey",
      "selectedReportTask",
      "selectedReportTaskKey",
      "selectedCuttingReportTask",
      "selectedCuttingReportTaskKey",
      "orderCategory",
      "orderMode",
      "orderProduct",
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
      "adminSection",
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
      initData: tg ? tg.initData : "",
      screen: "shift",
      selectedOperation: 0,
      selectedOrder: 0,
      selectedOrderKey: "",
      selectedReportTask: 0,
      selectedReportTaskKey: "",
      selectedCuttingReportTask: 0,
      selectedCuttingReportTaskKey: "",
      orderCategory: "",
      reportSection: "work",
      orderMode: "list",
      orderProduct: "",
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
      ...persistedUiState,
      data: null,
    };

    if (!state.taskCompletionDrafts || typeof state.taskCompletionDrafts !== "object") state.taskCompletionDrafts = {};
    if (!state.cuttingStageDrafts || typeof state.cuttingStageDrafts !== "object") state.cuttingStageDrafts = {};
    if (!state.feedbackDraft || typeof state.feedbackDraft !== "object") state.feedbackDraft = {category: "Производство", message: ""};
    if (!Array.isArray(state.orderSizes)) state.orderSizes = [];
    if (!Array.isArray(state.orderColors)) state.orderColors = [];
    if (!state.orderStockQuantities || typeof state.orderStockQuantities !== "object") state.orderStockQuantities = {};
    if (!state.orderFabricRolls || typeof state.orderFabricRolls !== "object") state.orderFabricRolls = {};
    if (!state.taskDefectPhotos || typeof state.taskDefectPhotos !== "object") state.taskDefectPhotos = {};

    const mount = document.getElementById("mount");
    const appRoot = document.getElementById("appRoot");
    const loginView = document.getElementById("loginView");
    const webLoginForm = document.getElementById("webLoginForm");
    const webRegisterForm = document.getElementById("webRegisterForm");
    const webActionSlot = document.getElementById("webActionSlot");
    const mainButton = document.getElementById("mainButton");
    const topTabs = document.getElementById("topTabs");
    const bottomNav = document.getElementById("bottomNav");
    const toast = document.getElementById("toast");
    const qrScanner = document.getElementById("qrScanner");
    const qrScannerVideo = document.getElementById("qrScannerVideo");
    const pendingActions = new Set();
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
          initData: state.initData,
          authToken,
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

      if (state.initData) url.searchParams.set("initData", state.initData);
      if (authToken) url.searchParams.set("authToken", authToken);
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

    function visibleOrderRows() {
      const rows = currentOrderRows();

      if (state.data && state.data.is_admin) {
        ensureOrderCategory();
        return rows.filter((task) => adminOrderCategoryForTask(task) === state.orderCategory);
      }

      const categories = employeeOrderCategories();
      if (!categories.length) return rows;

      ensureOrderCategory();
      return rows.filter((task) => (task.category || "") === state.orderCategory);
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

    function shiftText() {
      const shift = state.data && state.data.shift;
      if (!shift) return "Смена не открыта";
      return shift.status === "open" ? "Смена открыта" : "Смена закрыта";
    }

    function navItems() {
      if (state.data && state.data.is_admin) {
        return [
          { id: "shift", label: "Главная", icon: "⌂" },
          { id: "warehouse", label: "Склад", icon: "▦" },
          { id: "analytics", label: "Аналитика", icon: "▥" },
          { id: "orders", label: "Заказы", icon: "▣" },
          { id: "admin", label: "Админ", icon: "◎" },
        ];
      }
      return [...baseNav];
    }

    function renderBottomNav() {
      const items = navItems();
      bottomNav.style.setProperty("--nav-count", items.length);
      bottomNav.innerHTML = items.map((item) => `
        <button class="nav-btn ${state.screen === item.id ? "active" : ""}" data-go="${item.id}">
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
      return employee.position || "Сотрудник";
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
      render();
      showToast("Админ", data.message || fallbackMessage || "Данные обновлены.");
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
              <div><b>${escapeHtml(employee.name)}</b><span>${escapeHtml(employee.position)}${employee.on_shift ? ` · на смене${employee.start_time ? ` с ${escapeHtml(employee.start_time)}` : ""}` : ""}<br>План ${escapeHtml(employee.plan_text || "0")} · факт ${escapeHtml(employee.fact_text || "0")}</span></div>
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
            initData: state.initData,
            authToken,
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

      return `
        <div class="card task-completion-card">
          <div class="task-completion-head"><b>${escapeHtml(task.operation)}</b><span class="status-chip ${task.work_state === "in_work" ? "" : "warn"}">${escapeHtml(task.status_text || "В работе")}</span></div>
          ${renderRouteTaskInputs(task)}
          ${(paused || blocked) ? `<div class="task-note">${escapeHtml(task.blocked_reason || (paused ? "Работа приостановлена" : "Задание заблокировано"))}</div>` : ""}
          <div class="form-grid" style="margin-top:11px">
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
      state.orderTaskType = "cutting";
      state.orderRouteStep = "";
      state.orderMaterial = "Ткань";
      state.orderSizes = [];
      state.orderColors = [];
      state.orderQuantity = "1";
      state.orderPriority = "normal";
      state.orderDueDate = "";
      state.orderStockQuantities = {};
      state.orderFabricRolls = {};
      state.orderAttachment = null;
    }

    function ensureOrderDraftDefaults() {
      const catalog = getRouteCatalog();
      if (!catalog.length) return null;

      let product = routeProduct(state.orderProduct);
      if (!product) {
        product = catalog[0];
        state.orderProduct = product.product_name;
      }

      const availableSizes = product.sizes || [];
      const availableColors = getOrderColors();
      state.orderSizes = state.orderSizes.filter((size) => availableSizes.includes(size));
      state.orderColors = state.orderColors.filter((color) => availableColors.includes(color));
      Object.keys(state.orderFabricRolls).forEach((color) => {
        if (!state.orderColors.includes(color)) delete state.orderFabricRolls[color];
      });

      const operations = routeOperations(product);
      if (state.orderTaskType === "route" && !operations.some((operation) => String(operation.index) === String(state.orderRouteStep))) {
        state.orderRouteStep = operations[0] ? String(operations[0].index) : "";
      }

      return product;
    }

    function syncOrderDraft() {
      const product = document.getElementById("orderProduct");
      const taskType = document.getElementById("orderTaskType");
      const routeStep = document.getElementById("orderRouteStep");
      const material = document.getElementById("orderMaterial");
      const quantity = document.getElementById("orderQuantity");
      const priority = document.getElementById("orderPriority");
      const dueDate = document.getElementById("orderDueDate");
      const stockQuantityInputs = document.querySelectorAll("[data-stock-quantity]");
      const fabricRollInputs = document.querySelectorAll("[data-fabric-rolls]");
      const previousProduct = state.orderProduct;
      const previousRouteStep = state.orderRouteStep;

      if (product) state.orderProduct = product.value;
      if (taskType) state.orderTaskType = taskType.value;
      if (routeStep) state.orderRouteStep = routeStep.value;
      if (material) state.orderMaterial = material.value;
      if (quantity) state.orderQuantity = quantity.value;
      if (priority) state.orderPriority = priority.value;
      if (dueDate) state.orderDueDate = dueDate.value;
      stockQuantityInputs.forEach((input) => {
        state.orderStockQuantities[input.dataset.stockQuantity] = input.value;
      });
      fabricRollInputs.forEach((input) => {
        state.orderFabricRolls[input.dataset.fabricRolls] = input.value;
      });

      if (previousProduct && previousProduct !== state.orderProduct) {
        state.orderSizes = [];
        state.orderColors = [];
        state.orderRouteStep = "";
        state.orderStockQuantities = {};
        state.orderFabricRolls = {};
      }

      if (previousRouteStep && previousRouteStep !== state.orderRouteStep) {
        state.orderStockQuantities = {};
      }

      ensureOrderDraftDefaults();
    }

    function toggleOrderValue(kind, value) {
      const key = kind === "size" ? "orderSizes" : "orderColors";
      const values = state[key];
      const isSelected = values.includes(value);
      state[key] = isSelected ? values.filter((item) => item !== value) : [...values, value];

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
        <button class="choice-chip ${selectedValues.includes(value) ? "active" : ""}" data-order-${kind}="${escapeHtml(value)}">${escapeHtml(value)}</button>
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
      const stockItems = Object.entries(state.orderStockQuantities)
        .map(([stockId, quantity]) => ({stock_id: stockId, quantity}))
        .filter((item) => Number(item.quantity || 0) > 0);

      try {
        const data = await api("/api/production/create-order-task", {
          product_name: state.orderProduct,
          task_type: state.orderTaskType,
          route_step_index: state.orderRouteStep,
          material_name: state.orderTaskType === "cutting" ? state.orderMaterial : "",
          sizes: state.orderSizes,
          colors: state.orderColors,
          quantity: state.orderQuantity,
          priority: state.orderPriority,
          due_date: state.orderDueDate,
          fabric_rolls: state.orderFabricRolls,
          attachment: state.orderTaskType === "cutting" ? state.orderAttachment : null,
          stock_items: stockItems,
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

    function syncWarehouseFilters() {
      const product = document.getElementById("warehouseProductFilter");
      const size = document.getElementById("warehouseSizeFilter");
      const color = document.getElementById("warehouseColorFilter");

      if (product) state.warehouseProductFilter = product.value;
      if (size) state.warehouseSizeFilter = size.value;
      if (color) state.warehouseColorFilter = color.value;
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
            <div><b>${escapeHtml(size)} · ${escapeHtml(color)}</b><span>Количество деталей</span></div>
            <input data-contour-key="${escapeHtml(`${size}|${color}`)}" type="number" inputmode="numeric" min="0" step="1" placeholder="0" value="${escapeHtml((draft.quantities || {})[`${size}|${color}`] || "")}">
          </div>
        `).join("")).join("");

        return `
          <div class="card order-detail">
            <div class="order-head"><div class="op-icon">${sewingIcon()}</div><div><b>${escapeHtml(current.stage_title)}</b><span>${escapeHtml(current.product_name)}</span></div><span class="status-chip">1 этап</span></div>
            <div class="op-list">${rows || itemEmpty("Нет размеров или цветов.")}</div>
          </div>
          ${renderTaskFabricRolls(current)}
          ${renderTaskAttachment(current.attachment)}
        `;
      }

      if (current.stage === "layout") {
        const rows = (current.colors || []).map((color) => `
          <div class="card cutting-input-row">
            <div><b>${escapeHtml(color)}</b><span>${escapeHtml(current.sizes_text || "Размеры задания")}</span></div>
            <input data-layer-color="${escapeHtml(color)}" type="number" inputmode="numeric" min="0" step="1" placeholder="слои" value="${escapeHtml((draft.color_layers || {})[color] || "")}">
          </div>
        `).join("");

        return `
          <div class="card order-detail">
            <div class="order-head"><div class="op-icon">${sewingIcon()}</div><div><b>${escapeHtml(current.stage_title)}</b><span>${escapeHtml(current.product_name)}</span></div><span class="status-chip">2 этап</span></div>
            <div class="op-list">${rows || itemEmpty("Нет цветов для настила.")}</div>
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
      if (state.initData) url.searchParams.set("initData", state.initData);
      if (authToken) url.searchParams.set("authToken", authToken);
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
    }

    async function openWebQrScanner() {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia || typeof window.BarcodeDetector !== "function") {
        promptRouteCode();
        return;
      }

      try {
        qrScannerStream = await navigator.mediaDevices.getUserMedia({
          audio: false,
          video: {facingMode: {ideal: "environment"}},
        });
        qrScanner.hidden = false;
        qrScannerVideo.srcObject = qrScannerStream;
        await qrScannerVideo.play();
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
      const operations = routeOperations(product);
      const sizes = product ? product.sizes || [] : [];
      const colors = getOrderColors();
      const operationOptions = operations.map((operation) => `
        <option value="${operation.index}" ${String(operation.index) === String(state.orderRouteStep) ? "selected" : ""}>${escapeHtml(operation.position)} — ${escapeHtml(operation.operation)}</option>
      `).join("");
      const selectedOperation = operations.find((operation) => String(operation.index) === String(state.orderRouteStep)) || operations[0] || null;
      const stockRows = selectedOperation ? getWarehouseStock().filter((row) =>
        row.item_type === "semifinished" &&
        row.product_name === state.orderProduct &&
        row.ready_for_position === selectedOperation.position &&
        (selectedOperation.accepted_stock_stages || []).includes(row.stage_name)
      ) : [];
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
        <div class="screen-head"><div><h2>Создать задание</h2><p>Массовое задание по размерам и цветам.</p></div><div class="date">админ</div></div>
        <div class="card field-card">
          <div class="form-grid">
            <div class="field full"><label>Изделие</label><select id="orderProduct">${catalog.map((item) => `<option value="${escapeHtml(item.product_name)}" ${item.product_name === state.orderProduct ? "selected" : ""}>${escapeHtml(item.product_name)}</option>`).join("")}</select></div>
            <div class="field full"><label>Тип задания</label><select id="orderTaskType"><option value="cutting" ${state.orderTaskType === "cutting" ? "selected" : ""}>Раскрой</option><option value="route" ${state.orderTaskType === "route" ? "selected" : ""}>Операция</option></select></div>
            ${state.orderTaskType === "route" ? `<div class="field full"><label>Операция</label><select id="orderRouteStep">${operationOptions || `<option value="">Нет операций</option>`}</select></div>` : ""}
            ${state.orderTaskType === "cutting" ? `<div class="field full"><label>Материал</label><select id="orderMaterial"><option value="Ткань" selected>Ткань</option></select></div>` : ""}
          </div>
        </div>
        <div class="card field-card">
          <label>Планирование</label>
          <div class="form-grid">
            <div class="field"><label>Приоритет</label><select id="orderPriority"><option value="low" ${state.orderPriority === "low" ? "selected" : ""}>Низкий</option><option value="normal" ${state.orderPriority === "normal" ? "selected" : ""}>Обычный</option><option value="high" ${state.orderPriority === "high" ? "selected" : ""}>Высокий</option><option value="urgent" ${state.orderPriority === "urgent" ? "selected" : ""}>Срочный</option></select></div>
            <div class="field"><label>Срок</label><input id="orderDueDate" type="date" value="${escapeHtml(state.orderDueDate || "")}"></div>
          </div>
        </div>
        ${state.orderTaskType === "cutting" ? `
          <div class="card field-card"><label>Размеры</label>${sizes.length ? renderChoiceChips("size", sizes, state.orderSizes) : itemEmpty("У изделия нет размеров.")}</div>
          <div class="card field-card"><label>Цвета ткани</label>${colors.length ? renderChoiceChips("color", colors, state.orderColors) : itemEmpty("У изделия нет цветов.")}</div>
          ${rollInputs}
          <div class="card field-card"><label>Файл задания</label><div class="form-grid"><div class="field full"><input id="orderAttachment" type="file" accept=".doc,.docx,.xls,.xlsx,.pdf,application/pdf,application/msword,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"></div></div><p class="empty">${escapeHtml(attachmentText)}</p></div>
        ` : `
          ${renderStockPicker(stockRows, selectedOperation)}
        `}
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
          ${(task.due_date || task.priority === "urgent" || task.parent_batch_id) ? `<div class="route-inputs"><div class="route-input-row"><span>${task.parent_batch_id ? `Переделка задания #${escapeHtml(task.parent_batch_id)}` : `Приоритет: ${escapeHtml(priorityLabel(task.priority))}`}</span><span>${task.due_date ? `до ${escapeHtml(task.due_date)}` : ""}</span></div></div>` : ""}
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

    function renderOrders() {
      if (state.data && state.data.is_admin && state.orderMode === "create") {
        renderOrderCreate();
        return;
      }

      const allTasks = visibleOrderRows();
      state.selectedOrder = selectedTaskIndex(allTasks, state.selectedOrderKey, state.selectedOrder);
      const tasks = allTasks.filter((task) => task.task_kind !== "route");
      const routeRows = allTasks.filter((task) => task.task_kind === "route");
      const current = allTasks[state.selectedOrder] || allTasks[0];
      state.selectedOrderKey = taskIdentity(current);
      mainButton.textContent = state.data && state.data.is_admin
        ? "Создать задание"
        : (current && current.task_kind === "route" && current.is_assigned_to_me
          ? (current.can_complete ? "Выполнить задание" : "Продолжить задание")
          : (current && current.is_assigned_to_me ? "Открыть отчёт" : (current ? "Выбрать задание" : "Обновить статус")));
      mainButton.disabled = false;

      mount.innerHTML = `
        <div class="screen-head"><div><h2>${state.data && state.data.is_admin ? "Заказы в работе" : "Задания"}</h2><p>${state.data && state.data.is_admin ? "Создание и контроль заданий." : "Выберите свободное задание, чтобы взять его в работу."}</p></div><div class="date">${allTasks.length} активных</div></div>
        <div class="scan-row"><button type="button" class="small-button secondary" data-task-action="scan">Сканировать QR</button></div>
        ${state.data && state.data.is_admin ? `<div class="card shift-card" data-order-action="new"><div><b>Создать задание</b><span>Раскрой и следующие операции из складского остатка.</span></div><span class="status-chip">+</span></div>` : ""}
        <div class="op-list">
          ${allTasks.length ? `
          ${tasks.map((task, index) => `
            <div class="card order-card ${index === state.selectedOrder ? "selected" : ""}" data-select-order="${index}">
              <div class="order-head"><div class="op-icon">${uiIcon("work")}</div><div><b>${task.task_kind === "cutting_stage" ? escapeHtml(task.stage_title) : `Задание #${escapeHtml(task.id)}`}</b><span>${escapeHtml(task.product_name)}${task.assigned_employee_name ? `<br>В работе: ${escapeHtml(task.assigned_employee_name)}` : ""}</span></div><span class="status-chip ${task.work_status === "free" ? "gray" : "warn"}">${escapeHtml(task.status_text || task.status)}</span></div>
              <div class="progress"><i style="--w:${progressForTask(task)}%"></i></div>
              <div class="order-foot"><span>${escapeHtml((task.sizes || []).join(", ") || task.colors_text || task.sizes_text || "-")}</span><span>${task.task_kind === "cutting_stage" ? escapeHtml(task.next_action) : `${progressForTask(task)}%`}</span></div>
              ${state.data && state.data.is_admin ? `<div class="order-card-actions"><button type="button" class="order-delete-button" data-order-action="delete" data-task-kind="${escapeHtml(task.task_kind)}" data-task-id="${escapeHtml(task.id)}">Удалить</button></div>` : ""}
            </div>
          `).join("")}
          ${routeRows.map((task, routeIndex) => {
            const index = tasks.length + routeIndex;
            return routeTaskCard(task, index, {selectedIndex: state.selectedOrder});
          }).join("")}
          ` : itemEmpty("Активных заданий пока нет.")}
        </div>
        <div class="section-title"><b>Детали выбранного</b><span>${current ? progressForTask(current) : 0}%</span></div>
        ${current && current.task_kind === "cutting_stage" ? renderCuttingStageSummary(current) : current && current.task_kind === "production" ? `
          <div class="card order-detail"><div class="order-head"><div class="op-icon">${sewingIcon()}</div><div><b>Задание #${escapeHtml(current.id)}</b><span>${escapeHtml(current.product_name)}</span></div><span class="status-chip">${escapeHtml(current.status_text || current.status)}</span></div><div class="detail-grid"><div class="detail-box"><span>Размеры</span><strong>${escapeHtml((current.sizes || []).join(", ") || "-")}</strong></div><div class="detail-box"><span>Цвета</span><strong>${escapeHtml((current.color_labels || current.colors || []).join(", ") || "-")}</strong></div><div class="detail-box"><span>Приоритет</span><strong>${escapeHtml(priorityLabel(current.priority))}</strong></div><div class="detail-box"><span>Срок</span><strong>${escapeHtml(current.due_date || "Не задан")}</strong></div><div class="detail-box"><span>Статус</span><strong>${escapeHtml(current.status_text || current.status)}</strong></div><div class="detail-box"><span>Создано</span><strong>${escapeHtml((current.created_at || "").slice(0, 10) || "-")}</strong></div></div></div>
          ${renderTaskFabricRolls(current)}
          ${renderTaskAttachment(current.attachment)}
        ` : current ? `
          <div class="card order-detail"><div class="order-head route-order-head"><div class="op-icon">${sewingIcon()}</div><div><b>${escapeHtml(current.operation)}</b><span>${escapeHtml(current.product_name)}</span>${current.assigned_employee_name ? `<span class="route-assignee">В работе: ${escapeHtml(current.assigned_employee_name)}</span>` : ""}<span class="trace-code">${escapeHtml(current.trace_code || `RB-${current.id}`)}</span></div><span class="status-chip ${current.work_state === "free" ? "gray" : "warn"}">${escapeHtml(current.status_text || "Свободно")}</span></div><div class="detail-grid"><div class="detail-box"><span>Размер</span><strong>${escapeHtml(current.product_size || "-")}</strong></div><div class="detail-box"><span>Цвет</span><strong>${escapeHtml(current.product_color || "-")}</strong></div><div class="detail-box"><span>Количество</span><strong>${escapeHtml(current.quantity || 0)} шт</strong></div><div class="detail-box"><span>Статус</span><strong>${escapeHtml(current.status_text || "-")}</strong></div></div>${renderRouteTaskInputs(current)}${current.blocked_reason ? `<div class="task-note">${escapeHtml(current.blocked_reason)}</div>` : ""}<div class="button-row"><button type="button" class="small-button secondary" data-task-action="passport" data-task-id="${escapeHtml(current.id)}">Паспорт / QR</button></div></div>
          ${!state.data.is_admin && current.is_assigned_to_me ? renderTaskCompletionForm(current) : ""}
        ` : `<div class="card order-detail">${itemEmpty("Детали появятся после создания задания.")}</div>`}
        ${state.data && state.data.is_admin && current ? `<div class="button-row"><button class="small-button danger" data-order-action="delete" data-task-kind="${escapeHtml(current.task_kind)}" data-task-id="${escapeHtml(current.id)}">Удалить задание</button></div>` : ""}
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
        ["employees", "Сотрудники"],
        ["shifts", "Смены"],
        ["feedback", "Связь"],
      ];

      return `<div class="segment-row">${sections.map(([id, label]) => `
        <button class="segment-button ${state.adminSection === id ? "active" : ""}" data-admin-section="${id}">${label}</button>
      `).join("")}</div>`;
    }

    function renderAdminWarehouse(includeTabs = false) {
      const fabricRows = (getProduction().fabric_stock || []).filter((row) => Number(row.quantity || 0) > 0);
      const warehouseRows = getWarehouseStock().filter((row) => Number(row.quantity || 0) > 0);
      const receiptColors = getOrderColors();
      const semifinished = warehouseRows.filter((row) => row.item_type === "semifinished");
      const finished = warehouseRows.filter((row) => row.item_type === "finished");
      mainButton.textContent = "Обновить склад";
      mainButton.disabled = false;

      if ((!state.fabricReceiptColor || !receiptColors.includes(state.fabricReceiptColor)) && receiptColors.length) {
        state.fabricReceiptColor = receiptColors[0];
      }

      const receiptColorOptions = receiptColors.map((color) => `
        <option value="${escapeHtml(color)}" ${color === state.fabricReceiptColor ? "selected" : ""}>${escapeHtml(color)}</option>
      `).join("");
      const viewDefinitions = {
        materials: {label: "Материалы", rows: fabricRows, icon: "▦"},
        semifinished: {label: "Полуфабрикаты", rows: semifinished, icon: "▣"},
        finished: {label: "Готовая продукция", rows: finished, icon: "✓"},
      };

      if (state.warehouseView === "overview" || !viewDefinitions[state.warehouseView]) {
        state.warehouseView = "overview";
        return `
          <div class="screen-head"><div><h2>Склад</h2><p>Материалы, полуфабрикаты и готовая продукция.</p></div><div class="date">${warehouseRows.length + fabricRows.length} поз.</div></div>
          ${includeTabs ? renderAdminTabs() : ""}
          <div class="kpi-grid">
            <button type="button" class="card kpi warehouse-category" data-warehouse-view="materials"><span class="kpi-top"><span>Материалы</span><span class="kpi-ico">${uiIcon("fabric")}</span></span><strong>${fabricRows.length}<small> поз</small></strong><span>Открыть остатки</span></button>
            <button type="button" class="card kpi warehouse-category" data-warehouse-view="semifinished"><span class="kpi-top"><span>Полуфабрикаты</span><span class="kpi-ico">${uiIcon("layers")}</span></span><strong>${semifinished.length}<small> поз</small></strong><span>Открыть остатки</span></button>
            <button type="button" class="card kpi good warehouse-category" data-warehouse-view="finished"><span class="kpi-top"><span>Готовое</span><span class="kpi-ico">${uiIcon("quality")}</span></span><strong>${finished.length}<small> поз</small></strong><span>Открыть остатки</span></button>
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
        <div class="segment-row warehouse-segments">
          ${Object.entries(viewDefinitions).map(([id, item]) => `<button class="segment-button ${state.warehouseView === id ? "active" : ""}" data-warehouse-view="${id}">${escapeHtml(item.label)}</button>`).join("")}
        </div>
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

    function renderWarehouse() {
      if (!state.data || !state.data.is_admin) {
        mainButton.textContent = "Обновить";
        mainButton.disabled = false;
        mount.innerHTML = `
          <div class="screen-head"><div><h2>Склад</h2><p>Раздел доступен только администратору.</p></div></div>
          <div class="card field-card">${itemEmpty("Нет прав администратора.")}</div>
        `;
        return;
      }

      mount.innerHTML = renderAdminWarehouse(false);
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
            <div class="field full"><label>Сотрудник</label><select id="adminEmployeeId" ${isEmployeeReport ? "" : "disabled"}>${employeeOptions || `<option value="">Нет сотрудников</option>`}</select></div>
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
      const currentTelegramId = Number(state.data && state.data.employee ? state.data.employee.telegram_id : 0);
      mainButton.textContent = "Обновить сотрудников";

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
      const employeeCards = listedEmployees.length ? listedEmployees.map((employee) => `
        <div class="card field-card">
          <label>ID ${escapeHtml(employee.id)} · ${employee.role === "admin" ? "администратор" : "сотрудник"}</label>
          <div class="report-row"><div><b>${escapeHtml(employee.full_name)}</b><span>${escapeHtml(employee.position)} · ${employeeContact(employee)}</span></div><span class="status-chip ${employee.status === "active" ? "" : "gray"}">${escapeHtml(employeeStatusLabel(employee.status))}</span></div>
          ${employee.role === "admin" && Number(employee.telegram_id) === currentTelegramId ? "" : `<div class="form-grid"><div class="field full"><label>${employee.role === "admin" ? "Должность после снятия прав" : "Должность"}</label><select id="employeePosition${escapeHtml(employee.id)}">${positionOptions(employee)}</select></div></div>`}
          ${employee.role === "admin" ? `
            <div class="button-row">
              ${Number(employee.telegram_id) === currentTelegramId ? `<span class="status-chip gray">Это ваш аккаунт</span>` : `<button class="small-button secondary" data-admin-action="role-employee" data-employee-id="${escapeHtml(employee.id)}">Снять права</button><button class="small-button ${employee.status === "active" ? "danger" : ""}" data-admin-action="${employee.status === "active" ? "inactive" : "active"}" data-employee-id="${escapeHtml(employee.id)}">${employee.status === "active" ? "Отключить" : "Активировать"}</button>`}
            </div>
          ` : `
            <div class="button-row"><button class="small-button secondary" data-admin-action="position" data-employee-id="${escapeHtml(employee.id)}">Сохранить должность</button><button class="small-button ${employee.status === "active" ? "danger" : ""}" data-admin-action="${employee.status === "active" ? "inactive" : "active"}" data-employee-id="${escapeHtml(employee.id)}">${employee.status === "active" ? "Отключить" : "Активировать"}</button></div>
            <div class="button-row"><button class="small-button" data-admin-action="role-admin" data-employee-id="${escapeHtml(employee.id)}">Назначить администратором</button></div>
          `}
        </div>
      `).join("") : itemEmpty("Сотрудников пока нет.");
      const pendingCards = pending.length ? pending.map((employee) => `
        <div class="card field-card">
          <label>Заявка · ${escapeHtml(employee.registered_at || "")}</label>
          <div class="report-row"><div><b>${escapeHtml(employee.full_name)}</b><span>${employeeContact(employee)}</span></div><span class="status-chip warn">ожидает</span></div>
          <div class="form-grid"><div class="field full"><label>Должность</label><select id="employeePosition${escapeHtml(employee.id)}">${positionOptions(employee)}</select></div></div>
          <div class="button-row"><button class="small-button secondary" data-admin-action="inactive" data-employee-id="${escapeHtml(employee.id)}">Отклонить</button><button class="small-button" data-admin-action="approve" data-employee-id="${escapeHtml(employee.id)}">Назначить и активировать</button></div>
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
      const allowedScreens = state.data.is_admin
        ? ["shift", "warehouse", "analytics", "orders", "admin", "passport", "profile"]
        : ["shift", "report", "analytics", "orders", "admin", "passport", "profile"];

      if (!allowedScreens.includes(state.screen)) state.screen = "shift";
      document.getElementById("roleLabel").textContent = roleLabel();
      if (state.screen === "shift") renderShift();
      if (state.screen === "operations") renderOperations();
      if (state.screen === "report") renderReport();
      if (state.screen === "warehouse") renderWarehouse();
      if (state.screen === "analytics") renderAnalytics();
      if (state.screen === "orders") renderOrders();
      if (state.screen === "admin") renderAdmin();
      if (state.screen === "passport") renderPassport();
      if (state.screen === "profile") renderProfile();
      renderBottomNav();
      renderTopTabs();
      persistUiState();
    }

    function setScreen(screen) {
      state.screen = screen;
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
      } catch (error) {
        showToast("Ошибка", "Не удалось обновить смену.");
        mainButton.disabled = false;
      } finally {
        endAction(actionKey);
      }
    }

    document.addEventListener("click", (event) => {
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

      const orderAction = event.target.closest("[data-order-action]");
      if (orderAction) {
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
        if (adminAction.dataset.adminAction === "refresh") refreshAdminDashboard();
        if (adminAction.dataset.adminAction === "load-report") loadAdminReport();
        if (adminAction.dataset.adminAction === "export-report") exportAdminReport();
        if (adminAction.dataset.adminAction === "load-feedback") loadAdminFeedback();
        if (adminAction.dataset.adminAction === "active") adminEmployeeStatus(adminAction.dataset.employeeId, "active");
        if (adminAction.dataset.adminAction === "inactive") adminEmployeeStatus(adminAction.dataset.employeeId, "inactive");
        if (adminAction.dataset.adminAction === "approve") adminApproveEmployee(adminAction.dataset.employeeId);
        if (adminAction.dataset.adminAction === "position") adminEmployeePosition(adminAction.dataset.employeeId);
        if (adminAction.dataset.adminAction === "role-admin") adminEmployeeRole(adminAction.dataset.employeeId, "admin");
        if (adminAction.dataset.adminAction === "role-employee") adminEmployeeRole(adminAction.dataset.employeeId, "employee");
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
      if (state.screen === "warehouse") { refreshState("Склад обновлён."); return; }
      if (state.screen === "analytics") {
        if (state.data && state.data.is_admin) { refreshAdminDashboard("Контроль производства обновлён."); return; }
        setScreen("orders");
        return;
      }
      if (state.screen === "orders" && state.data && state.data.is_admin) {
        if (state.orderMode === "create") { createOrderTask(); return; }
        resetOrderDraft();
        render();
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

    document.addEventListener("input", (event) => {
      if (event.target.closest("#orderProduct, #orderTaskType, #orderRouteStep, #orderMaterial, #orderQuantity, #orderPriority, #orderDueDate, [data-stock-quantity], [data-fabric-rolls]")) {
        syncOrderDraft();
      }
      if (event.target.closest("#fabricReceiptMaterial, #fabricReceiptColor, #fabricReceiptQuantity")) {
        syncWarehouseReceiptForm();
      }

      const routeTask = getDisplayedRouteTask();

      if (routeTask && event.target.closest("#taskGoodQuantity, #taskDefectQuantity, #taskDefectReason, #taskDefectDisposition, #taskDefectComment")) {
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
        state.taskCompletionDrafts[routeTask.id] = draft;
      }

      const cuttingTasks = getMyCuttingTasks();
      const cuttingTask = cuttingTasks[state.selectedCuttingReportTask] || cuttingTasks[0];

      if (cuttingTask && (event.target.matches("[data-contour-key]") || event.target.matches("[data-layer-color]") || event.target.id === "cuttingProgress")) {
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
      const defectPhotoInput = event.target.closest("#taskDefectPhoto");
      if (defectPhotoInput) {
        const task = getDisplayedRouteTask();
        readDefectPhoto(defectPhotoInput.files && defectPhotoInput.files[0], task).catch(() => {
          showToast("Фото брака", "Не удалось прочитать фотографию.");
        });
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

      if (event.target.closest("#warehouseProductFilter") || event.target.closest("#warehouseSizeFilter") || event.target.closest("#warehouseColorFilter")) {
        syncWarehouseFilters();
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

      if (state.screen === "warehouse" && state.warehouseView !== "overview") {
        state.warehouseView = "overview";
        resetWarehouseFilters();
        render();
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
        ? ["shift", "warehouse", "analytics", "orders", "admin"]
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
      const focusTarget = isRegistration ? "webFullName" : "webUsername";
      window.setTimeout(() => document.getElementById(focusTarget)?.focus(), 60);
    }

    function showWebLogin(message = "") {
      state.data = null;
      appRoot.hidden = true;
      mainButton.hidden = true;
      bottomNav.hidden = true;
      loginView.hidden = false;
      setWebAuthMode("login", message);
    }

    function showWebApp() {
      loginView.hidden = true;
      appRoot.hidden = false;
      mainButton.hidden = false;
      bottomNav.hidden = false;
    }

    async function restoreWebSession() {
      try {
        const response = await fetch("/api/web/session", {credentials: "same-origin", cache: "no-store"});
        const data = await response.json().catch(() => ({}));
        if (!response.ok || !data.ok) return false;
        webCsrfToken = data.csrf_token || "";
        webSessionProfile = data;
        const identity = String(data.telegram_id || data.username || "web");
        if (identity !== storedWebIdentity) {
          window.sessionStorage.setItem("webapp_identity", identity);
          window.location.reload();
          return false;
        }
        return true;
      } catch (error) {
        return false;
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
        window.sessionStorage.setItem("webapp_identity", String(data.telegram_id || data.username || "web"));
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
      try {
        await fetch("/api/web/logout", {
          method: "POST",
          headers: {"Content-Type": "application/json", "X-CSRF-Token": webCsrfToken},
          credentials: "same-origin",
          body: "{}",
        });
      } finally {
        try { window.sessionStorage.removeItem("webapp_identity"); } catch (error) {}
        webCsrfToken = "";
        window.location.reload();
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
        try { window.sessionStorage.removeItem("webapp_identity"); } catch (error) {}
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
        const restored = await restoreWebSession();
        if (!restored) {
          if (document.visibilityState !== "hidden") showWebLogin();
          return;
        }
      }
      showWebApp();
      await refreshState();
    }

    document.getElementById("webLoginTab").addEventListener("click", () => setWebAuthMode("login"));
    document.getElementById("webRegisterTab").addEventListener("click", () => setWebAuthMode("register"));
    document.getElementById("qrScannerClose").addEventListener("click", stopWebQrScanner);
    document.getElementById("qrScannerManual").addEventListener("click", () => {
      stopWebQrScanner();
      promptRouteCode();
    });
    document.addEventListener("visibilitychange", () => {
      if (document.visibilityState === "hidden" && qrScannerStream) stopWebQrScanner();
    });
    webLoginForm.addEventListener("submit", loginWebApp);
    webRegisterForm.addEventListener("submit", registerWebApp);
    bootstrapApplication();
  </script>
</body>
</html>
"""
