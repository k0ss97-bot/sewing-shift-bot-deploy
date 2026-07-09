"""Static HTML assets for the Telegram miniapp."""

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
      --bg: #f4eee6;
      --text: #241b16;
      --muted: #7b6d62;
      --soft: rgba(255, 250, 243, .78);
      --line: rgba(78, 56, 42, .13);
      --accent: #c36f55;
      --accent-dark: #a95640;
      --sage: #8f9f7f;
      --sage-dark: #6f805f;
      --cream: #fffaf3;
      --danger: #bd6758;
      --good: #789265;
      --shadow: 0 26px 80px rgba(55, 39, 29, .18);
      --inset-shadow: inset 0 1px 0 rgba(255,255,255,.72);
      --font: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Inter, Arial, sans-serif;
    }

    * { box-sizing: border-box; }

    html, body {
      margin: 0;
      min-height: 100%;
      font-family: var(--font);
      color: var(--text);
      background:
        radial-gradient(circle at 8% 8%, rgba(195,111,85,.18), transparent 28%),
        radial-gradient(circle at 92% 4%, rgba(143,159,127,.22), transparent 30%),
        linear-gradient(135deg, #fff8ee 0%, #f4eee6 48%, #eadfd2 100%);
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

    .app {
      min-height: 100vh;
      padding: 12px 12px 118px;
      background:
        radial-gradient(circle at 20% 0%, rgba(195,111,85,.12), transparent 33%),
        radial-gradient(circle at 90% 0%, rgba(143,159,127,.15), transparent 31%),
        var(--cream);
      position: relative;
      overflow: hidden;
    }

    .app::after {
      content: "";
      position: fixed;
      inset: 0;
      background-image: radial-gradient(circle, rgba(195,111,85,.10) 1px, transparent 1.7px);
      background-size: 22px 22px;
      opacity: .22;
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
      border: 1px solid rgba(78,56,42,.11);
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
      box-shadow: 0 9px 18px rgba(195,111,85,.20);
    }

    .tab:hover:not(.active) {
      color: var(--accent-dark);
      background: rgba(195,111,85,.10);
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
      border: 1px solid rgba(78,56,42,.11);
      background: rgba(255,250,244,.76);
      border-radius: 22px;
      box-shadow: 0 10px 24px rgba(80,55,36,.055), var(--inset-shadow);
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
      background: rgba(143,159,127,.16);
      border: 1px solid rgba(143,159,127,.18);
      border-radius: 99px;
      padding: 7px 9px;
      font-size: 10.5px;
      font-weight: 950;
      white-space: nowrap;
    }

    .status-chip.warn {
      color: var(--accent-dark);
      background: rgba(195,111,85,.12);
      border-color: rgba(195,111,85,.18);
    }

    .status-chip.gray {
      color: var(--muted);
      background: rgba(120,96,76,.10);
      border-color: rgba(120,96,76,.10);
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

    .kpi-top {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      color: var(--muted);
      font-size: 11px;
      font-weight: 900;
    }

    .kpi-ico {
      width: 34px;
      height: 34px;
      border-radius: 13px;
      background: rgba(195,111,85,.13);
      color: var(--accent-dark);
      display: grid;
      place-items: center;
      font-size: 16px;
    }

    .kpi.good .kpi-ico {
      background: rgba(143,159,127,.15);
      color: var(--sage-dark);
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

    .kpi span {
      display: block;
      margin-top: 4px;
      color: var(--muted);
      font-size: 11px;
      line-height: 1.3;
    }

    .progress {
      height: 7px;
      border-radius: 99px;
      background: rgba(120,96,76,.12);
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
      background: rgba(195,111,85,.13);
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
      border-color: rgba(195,111,85,.44);
      box-shadow: 0 12px 28px rgba(195,111,85,.12), var(--inset-shadow);
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
      border: 1px solid rgba(78,56,42,.13);
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
      background: rgba(195,111,85,.10);
    }

    .button-row {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 9px;
      margin-top: 11px;
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
      background: rgba(195,111,85,.12);
    }

    .small-button.danger {
      background: var(--danger);
    }

    .small-button:hover {
      filter: brightness(1.03);
      box-shadow: 0 10px 18px rgba(195,111,85,.15);
    }

    button,
    [data-go],
    [data-admin-home-period],
    [data-order-category],
    [data-report-section],
    [data-admin-home-view],
    [data-admin-home-employee],
    [data-admin-section],
    [data-admin-action],
    [data-order-action],
    [data-order-size],
    [data-order-color],
    [data-history-action],
    [data-feedback-action],
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
      border-color: rgba(195,111,85,.24);
      box-shadow: 0 9px 22px rgba(95,67,48,.07);
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
      border-color: rgba(195,111,85,.52);
      background: rgba(255,255,255,.72);
      box-shadow: 0 14px 28px rgba(195,111,85,.16);
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
      box-shadow: 0 7px 16px rgba(195,111,85,.12);
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
      background: rgba(195,111,85,.13);
      border-color: rgba(195,111,85,.18);
    }

    .choice-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 8px;
    }

    .choice-chip {
      min-width: 0;
      min-height: 38px;
      border: 1px solid rgba(78,56,42,.13);
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
      border-color: rgba(195,111,85,.44);
      background: rgba(195,111,85,.12);
      box-shadow: 0 8px 18px rgba(195,111,85,.10);
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

    .stock-pick-row {
      display: grid;
      grid-template-columns: 24px minmax(0, 1fr) 92px;
      gap: 10px;
      align-items: center;
      padding: 11px;
      border: 1px solid rgba(49,39,33,.10);
      border-radius: 18px;
      background: rgba(255,255,255,.58);
      transition: .16s ease;
    }

    .stock-pick-row.active,
    .stock-pick-row:hover {
      border-color: rgba(195,111,85,.42);
      background: rgba(195,111,85,.10);
      box-shadow: 0 8px 18px rgba(195,111,85,.10);
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
      border: 1px solid rgba(49,39,33,.12);
      border-radius: 14px;
      background: rgba(255,255,255,.78);
      padding: 0 10px;
      color: var(--text);
      font-size: 16px;
      font-weight: 900;
      outline: none;
    }

    .report-row input,
    .report-row select,
    .report-row textarea {
      width: 100%;
      min-height: 42px;
      border: 1px solid rgba(49,39,33,.12);
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
      border: 1px solid rgba(49,39,33,.12);
      border-radius: 14px;
      background: rgba(255,255,255,.78);
      padding: 0 12px;
      color: var(--text);
      font-size: 16px;
      font-weight: 900;
      outline: none;
    }

    .cutting-input-row input:focus {
      border-color: rgba(195,111,85,.48);
      box-shadow: 0 0 0 3px rgba(195,111,85,.12);
    }

    .stock-pick-qty input:focus {
      border-color: rgba(195,111,85,.48);
      box-shadow: 0 0 0 3px rgba(195,111,85,.12);
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
      border-color: rgba(195,111,85,.44);
      box-shadow: 0 12px 28px rgba(195,111,85,.12), var(--inset-shadow);
    }

    .order-card .order-head {
      padding: 4px 2px;
    }

    .route-order-head {
      grid-template-columns: 44px minmax(0, 1fr) auto;
      align-items: start;
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

    .order-detail {
      padding: 14px;
      background: linear-gradient(135deg, rgba(195,111,85,.12), rgba(143,159,127,.10));
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
      background: conic-gradient(var(--accent) calc(var(--p)*1%), rgba(195,111,85,.13) 0);
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
      box-shadow: inset 0 1px 2px rgba(80,55,36,.08);
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
      bottom: 88px;
      transform: translate(-50%, 26px);
      opacity: 0;
      min-width: min(360px, calc(100% - 32px));
      border: 1px solid rgba(255,255,255,.42);
      border-radius: 20px;
      background: rgba(36,27,22,.88);
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

    .main-button {
      position: fixed;
      z-index: 6;
      left: 16px;
      right: 16px;
      bottom: 78px;
      border: none;
      border-radius: 18px;
      padding: 15px 16px;
      color: white;
      background: linear-gradient(135deg, var(--accent), #d27c5e);
      font-size: 15px;
      font-weight: 950;
      box-shadow: 0 18px 36px rgba(195,111,85,.30);
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
      padding: 9px 12px 12px;
      background: rgba(255,250,243,.88);
      border-top: 1px solid rgba(78,56,42,.11);
      backdrop-filter: blur(18px);
      display: grid;
      grid-template-columns: repeat(var(--nav-count, 5), minmax(0, 1fr));
      gap: 2px;
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
      background: rgba(195,111,85,.12);
    }

    .nav-btn:hover {
      color: var(--accent-dark);
    }

    .nav-btn:hover .nav-ico {
      background: rgba(195,111,85,.10);
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
    }
  </style>
</head>
<body>
  <main class="app">
    <div class="appbar">
      <button class="icon-btn" id="backBtn" aria-label="Назад">‹</button>
      <div class="app-title">Шагаем вместе<small id="roleLabel">Загрузка</small></div>
      <button class="icon-btn" id="menuBtn" aria-label="Меню">⋯</button>
    </div>

    <div class="body">
      <div class="tabs" id="topTabs" hidden></div>
      <div id="mount"></div>
    </div>
  </main>

  <button class="main-button" id="mainButton">Загрузка</button>
  <nav class="bottom-nav" id="bottomNav" aria-label="Навигация миниаппа"></nav>
  <div class="toast" id="toast"><b></b><span></span></div>

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
    const state = {
      initData: tg ? tg.initData : "",
      screen: "shift",
      selectedOperation: 0,
      selectedOrder: 0,
      selectedReportTask: 0,
      selectedCuttingReportTask: 0,
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
      orderStockQuantities: {},
      orderFabricRolls: {},
      orderAttachment: null,
      fabricReceiptMaterial: "Ткань",
      fabricReceiptColor: "",
      fabricReceiptQuantity: "",
      adminSection: "reports",
      adminReportType: "period",
      adminStartDate: "",
      adminEndDate: "",
      adminEmployeeId: "",
      adminShiftEndTime: "",
      adminHomePeriod: "today",
      adminHomeView: "overview",
      adminHomeEmployee: "",
      userStartDate: "",
      userEndDate: "",
      data: null,
    };

    const mount = document.getElementById("mount");
    const mainButton = document.getElementById("mainButton");
    const topTabs = document.getElementById("topTabs");
    const bottomNav = document.getElementById("bottomNav");
    const toast = document.getElementById("toast");

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

    function escapeHtml(value) {
      return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }

    async function api(path, payload = {}) {
      const response = await fetch(path, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
          ...payload,
          initData: state.initData,
          authToken,
          telegram_id: debugTelegramId,
        }),
      });
      return await response.json();
    }

    function showToast(title, text) {
      toast.querySelector("b").textContent = title;
      toast.querySelector("span").textContent = text;
      toast.classList.add("show");
      clearTimeout(window.toastTimer);
      window.toastTimer = setTimeout(() => toast.classList.remove("show"), 2600);
    }

    function sewingIcon() {
      return `<svg viewBox="0 0 32 32" aria-hidden="true" width="25" height="25"><path d="M7 22h18v4H7z" fill="none" stroke="currentColor" stroke-width="2"/><path d="M10 22V8h9a5 5 0 0 1 5 5v2" fill="none" stroke="currentColor" stroke-width="2"/><path d="M6 14h5M19 15h8v7M13 8V5M22 15v-3M15 22v-5M13 17h4" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>`;
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

    function openTaskAttachment(taskId, action) {
      const url = attachmentFileUrl(taskId, action);

      if (!url) {
        showToast("Файл", "Файл не найден. Обновите задание.");
        return;
      }

      try {
        if (action === "download") {
          window.location.href = url;
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
          <div class="button-row"><button class="small-button secondary" data-attachment-action="download" data-attachment-task-id="${escapeHtml(attachment.task_id)}">Открыть файл</button><button class="small-button" data-attachment-action="open" data-attachment-task-id="${escapeHtml(attachment.task_id)}">Скачать</button></div>
        </div>
      `;
    }

    function renderTaskFabricRolls(task) {
      const rows = task && task.fabric_rolls ? task.fabric_rolls : [];
      if (!rows.length) return "";

      return `
        <div class="card field-card">
          <label>Списанные рулоны</label>
          <div class="op-list">
            ${rows.map((row) => `
              <div class="report-row"><div><b>${escapeHtml(row.product_color_label || row.product_color)}</b><span>${escapeHtml(row.material_name || "Ткань")}</span></div><span class="status-chip">${escapeHtml(row.rolls)} рул.</span></div>
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

    function getCompletedRouteTasks() {
      return state.data && state.data.routes && state.data.routes.completed_tasks ? state.data.routes.completed_tasks : [];
    }

    function getMyRouteTasks() {
      return getRouteTasks()
        .filter((task) => task.is_assigned_to_me)
        .map((task) => ({...task, task_kind: "route"}));
    }

    function getMyCuttingTasks() {
      return getCuttingTasks().map((task) => ({...task, task_kind: "cutting_stage"}));
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

    function selectCuttingTaskForReport(task) {
      const tasks = getMyCuttingTasks();
      const index = tasks.findIndex((row) => row.id === task.id && row.stage === task.stage);
      state.selectedCuttingReportTask = index >= 0 ? index : 0;
      state.reportSection = "work";
      setScreen("report");
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
      return `
        <div class="kpi-grid">
          <div class="card kpi"><div class="kpi-top"><span>План</span><div class="kpi-ico">◎</div></div><strong>${escapeHtml(entity.plan_text || "0")}</strong><span>Плановое количество</span><div class="progress"><i style="--w:0%"></i></div></div>
          <div class="card kpi good"><div class="kpi-top"><span>Факт</span><div class="kpi-ico">✓</div></div><strong>${escapeHtml(entity.fact_text || "0")}</strong><span>Сделано по отчётам</span><div class="progress sage"><i style="--w:${Math.min(100, Number(entity.fact || 0))}%"></i></div></div>
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
            <div class="card report-row"><div><b>${escapeHtml(defect.product || "-")}</b><span>${escapeHtml(defect.stage || "-")}<br>${escapeHtml(defect.reason || "Причина не указана")}</span></div><span class="status-chip gray">${escapeHtml(defect.date || "")}</span></div>
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
      }
    }

    async function sendFeedback() {
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
        if (message) message.value = "";
        render();
        showToast("Связь", data.message || "Сообщение отправлено.");
      } catch (error) {
        showToast("Ошибка", "Не удалось отправить сообщение.");
        mainButton.disabled = false;
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
        replaceAdminDashboard(data, "Статус сотрудника изменён.");
      } catch (error) {
        showToast("Ошибка", "Не удалось изменить статус.");
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
        replaceAdminDashboard(data, "Должность изменена.");
      } catch (error) {
        showToast("Ошибка", "Не удалось изменить должность.");
        mainButton.disabled = false;
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
        render();
        showToast("Отчёт", "Данные обновлены.");
      } catch (error) {
        showToast("Ошибка", "Не удалось загрузить отчёт.");
        mainButton.disabled = false;
      }
    }

    async function exportAdminReport() {
      if (!state.data || !state.data.is_admin) return;
      syncAdminForm();
      mainButton.disabled = true;

      try {
        const response = await fetch("/api/admin/report/export", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({
            ...getAdminReportPayload(),
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
        URL.revokeObjectURL(url);
        showToast("Выгрузка", "Файл отчёта сформирован.");
      } catch (error) {
        showToast("Ошибка", "Не удалось выгрузить отчёт.");
      } finally {
        mainButton.disabled = false;
      }
    }

    function renderShift() {
      if (state.data && state.data.is_admin) {
        renderAdminHome();
        return;
      }

      const employee = state.data && state.data.employee;
      const shift = state.data && state.data.shift;
      const operations = getReportOperations();
      const tasks = getTasks();
      const contourTasks = getContourTasks();
      const fabricRows = getProduction().fabric_stock || [];
      const hasOpen = state.data && state.data.has_open_shift;

      mainButton.textContent = hasOpen ? "Закрыть смену" : "Открыть смену";
      mainButton.disabled = Boolean(shift && shift.status === "closed");

      mount.innerHTML = `
        <div class="screen-head"><div><h2>Сегодня</h2><p>${escapeHtml(employee ? employee.full_name : "Откройте приложение из Telegram")}</p></div><div class="date">${escapeHtml(shift ? shift.date : "сегодня")}</div></div>
        <div class="card shift-card"><div><b>${escapeHtml(shiftText())}</b><span>${escapeHtml(employee ? employee.position : "-")} · профиль ${escapeHtml(employee ? employee.status : "-")}<br>${escapeHtml(shift ? `${shift.start_time || "-"}-${shift.end_time || ""}` : "Начните смену, чтобы вести отчёт")}</span></div><span class="status-chip ${hasOpen ? "" : "gray"}">● ${hasOpen ? "в процессе" : "ожидает"}</span></div>
        <div class="kpi-grid">
          <div class="card kpi"><div class="kpi-top"><span>Отчёт</span><div class="kpi-ico">${sewingIcon()}</div></div><strong>${operations.length}<small> строк</small></strong><span>Операции текущей смены</span><div class="progress"><i style="--w:${Math.min(100, operations.length * 12)}%"></i></div></div>
          <div class="card kpi good"><div class="kpi-top"><span>Задания</span><div class="kpi-ico">✓</div></div><strong>${tasks.length}<small> акт.</small></strong><span>Производственные задания</span><div class="progress sage"><i style="--w:${Math.min(100, tasks.length * 18)}%"></i></div></div>
          <div class="card kpi"><div class="kpi-top"><span>Контуры</span><div class="kpi-ico">▣</div></div><strong>${contourTasks.length}<small> шт</small></strong><span>Доступно раскройщику</span></div>
          <div class="card kpi"><div class="kpi-top"><span>Ткань</span><div class="kpi-ico">▦</div></div><strong>${fabricRows.length}<small> поз.</small></strong><span>Остатки ткани</span></div>
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

    function renderReport() {
      const feedback = getFeedbackRows();
      const history = getHistory();
      const workTasks = getMyRouteTasks();
      const cuttingWorkTasks = getMyCuttingTasks();
      const doneTasks = getCompletedRouteTasks();
      ensureUserDefaults();
      if (!["work", "done", "feedback"].includes(state.reportSection)) state.reportSection = "work";

      if (state.selectedReportTask >= workTasks.length) state.selectedReportTask = 0;
      if (state.selectedCuttingReportTask >= cuttingWorkTasks.length) state.selectedCuttingReportTask = 0;

      const selectedTask = workTasks[state.selectedReportTask] || workTasks[0];
      const selectedCuttingTask = cuttingWorkTasks[state.selectedCuttingReportTask] || cuttingWorkTasks[0];
      mainButton.textContent = state.reportSection === "work" && (selectedCuttingTask || selectedTask) ? (selectedCuttingTask ? "Выполнить этап" : "Выполнить задание") : "Обновить отчёт";
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
                  <div class="order-head"><div class="op-icon">▣</div><div><b>${escapeHtml(task.stage_title)}</b><span>${escapeHtml(task.product_name)}</span></div><span class="status-chip">${escapeHtml(task.status_text || task.status)}</span></div>
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
            <div class="card field-card">
              <label>${escapeHtml(selectedTask.operation)}</label>
              <div class="form-grid">
                <div class="field"><label>Годная продукция</label><input id="taskGoodQuantity" type="number" min="0" max="${escapeHtml(selectedTask.quantity)}" step="1" value="${escapeHtml(selectedTask.quantity)}"></div>
                <div class="field"><label>Брак</label><input id="taskDefectQuantity" type="number" min="0" max="${escapeHtml(selectedTask.quantity)}" step="1" value="0"></div>
                <div class="field full"><label>Остаток задания</label><input type="text" value="${escapeHtml(selectedTask.product_size)} · ${escapeHtml(selectedTask.product_color)} · ${escapeHtml(selectedTask.quantity)} шт" disabled></div>
              </div>
              <div class="button-row"><button class="small-button" data-report-action="complete-task">Выполнить задание</button></div>
            </div>
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
                <div class="order-head route-order-head"><div class="op-icon">✓</div><div><b>${escapeHtml(task.operation)}</b><span>${escapeHtml(task.product_name)}</span></div><span class="status-chip">Завершено</span></div>
                <div class="order-foot"><strong>${escapeHtml(task.product_size)} · ${escapeHtml(task.product_color)}</strong><strong>${escapeHtml(task.good_quantity || 0)} годн. · ${escapeHtml(task.defect_quantity || 0)} брак</strong></div>
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
            <div class="field full"><label>Раздел</label><select id="feedbackCategory"><option value="Производство">Производство</option><option value="Бытовое">Бытовое</option></select></div>
            <div class="field full"><label>Сообщение</label><textarea id="feedbackMessage" placeholder="Напишите сообщение"></textarea></div>
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
          <div class="card kpi"><div class="kpi-top"><span>Смены</span><div class="kpi-ico">◷</div></div><strong>${historySummary ? historySummary.shift_count : 0}<small> шт</small></strong><span>За выбранный период</span></div>
          <div class="card kpi good"><div class="kpi-top"><span>Часы</span><div class="kpi-ico">✓</div></div><strong>${escapeHtml(historySummary ? historySummary.total_time : "0:00")}</strong><span>Отработано суммарно</span></div>
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
      const stockQuantityInputs = document.querySelectorAll("[data-stock-quantity]");
      const fabricRollInputs = document.querySelectorAll("[data-fabric-rolls]");
      const previousProduct = state.orderProduct;
      const previousRouteStep = state.orderRouteStep;

      if (product) state.orderProduct = product.value;
      if (taskType) state.orderTaskType = taskType.value;
      if (routeStep) state.orderRouteStep = routeStep.value;
      if (material) state.orderMaterial = material.value;
      if (quantity) state.orderQuantity = quantity.value;
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
      const stockHtml = stockRows.length ? stockRows.map((row) => {
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
      }).join("") : itemEmpty(`На складе нет полуфабрикатов после раскроя${selectedOperation ? ` для ${selectedOperation.position}` : ""}.`);

      return `
        <div class="card field-card">
          <label>Вход</label>
          <div class="stock-picker">
            <div class="stock-picker-head"><span>Полуфабрикаты после раскроя</span><span>${selectedRows.length} поз. · ${selectedTotal} шт</span></div>
            ${stockRows.length ? `<div class="stock-picker-actions"><button class="small-button secondary" data-stock-action="clear">Очистить</button><button class="small-button" data-stock-action="all">Взять всё</button></div>` : ""}
            ${stockHtml}
          </div>
        </div>
      `;
    }

    async function createOrderTask() {
      if (!state.data || !state.data.is_admin) return;
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
        render();
        showToast("Задание", data.message || "Задание создано.");
      } catch (error) {
        showToast("Ошибка", "Не удалось создать задание.");
        mainButton.disabled = false;
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

    async function addFabricReceipt() {
      if (!state.data || !state.data.is_admin) return;
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
      }
    }

    async function deleteOrderTask() {
      if (!state.data || !state.data.is_admin) return;
      const rows = visibleOrderRows();
      const current = rows[state.selectedOrder] || rows[0];

      if (!current) {
        showToast("Задание", "Выберите задание.");
        return;
      }

      const confirmed = window.confirm(`Удалить задание #${current.id}?`);
      if (!confirmed) return;

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
        render();
        showToast("Задание", data.message || "Задание удалено.");
      } catch (error) {
        showToast("Ошибка", "Не удалось удалить задание.");
        mainButton.disabled = false;
      }
    }

    function renderCuttingStageDetail(current) {
      if (current.stage === "contours") {
        const rows = (current.colors || []).map((color) => (current.sizes || []).map((size) => `
          <div class="card cutting-input-row">
            <div><b>${escapeHtml(size)} · ${escapeHtml(color)}</b><span>Количество деталей</span></div>
            <input data-contour-key="${escapeHtml(`${size}|${color}`)}" type="number" inputmode="numeric" min="0" step="1" placeholder="0">
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
            <input data-layer-color="${escapeHtml(color)}" type="number" inputmode="numeric" min="0" step="1" placeholder="слои">
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
            <div class="form-grid"><div class="field full"><label>Готовность</label><select id="cuttingProgress"><option value="25">25%</option><option value="50">50%</option><option value="75">75%</option><option value="100" selected>100%</option></select></div></div>
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
        state.selectedOrder = 0;
        state.selectedCuttingReportTask = 0;
        render();
        showToast("Задание", data.message || "Этап выполнен.");
      } catch (error) {
        showToast("Ошибка", "Не удалось выполнить этап.");
        mainButton.disabled = false;
      }
    }

    async function completeOperationTask(current) {
      if (!current) return;
      const goodInput = document.getElementById("taskGoodQuantity");
      const defectInput = document.getElementById("taskDefectQuantity");
      mainButton.disabled = true;

      try {
        const data = await api("/api/routes/complete", {
          batch_id: current.id,
          good_quantity: goodInput ? goodInput.value : current.quantity,
          defect_quantity: defectInput ? defectInput.value : 0,
        });

        if (!data.ok) {
          showToast("Задание", data.message || "Не удалось завершить операцию.");
          mainButton.disabled = false;
          return;
        }

        if (state.data.routes) state.data.routes.tasks = data.tasks || [];
        if (state.data.routes) state.data.routes.completed_tasks = data.completed_tasks || [];
        state.data.production = data.production || state.data.production;
        state.selectedOrder = 0;
        state.selectedReportTask = 0;
        render();
        showToast("Задание", data.message || "Операция завершена.");
      } catch (error) {
        showToast("Ошибка", "Не удалось завершить операцию.");
        mainButton.disabled = false;
      }
    }

    async function startOperationTask(current) {
      if (!current || current.task_kind !== "route" || state.data.is_admin) return;

      if (current.is_assigned_to_me) {
        state.reportSection = "work";
        setScreen("report");
        return;
      }

      if (!current.can_take) {
        showToast("Задание", current.assigned_employee_name ? `Задание в работе у ${current.assigned_employee_name}.` : "Задание уже в работе.");
        return;
      }

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
        state.reportSection = "work";
        state.selectedReportTask = 0;
        setScreen("report");
        showToast("Задание", data.message || "Задание взято в работу.");
      } catch (error) {
        showToast("Ошибка", "Не удалось взять задание.");
        mainButton.disabled = false;
      }
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
        row.ready_for_position === selectedOperation.position
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

    function routeTaskCard(task, index, options = {}) {
      const isSelected = index === options.selectedIndex;
      const selectAttr = options.selectAttr || "data-select-order";
      const assignee = task.assigned_employee_name ? `<span class="route-assignee">В работе: ${escapeHtml(task.assigned_employee_name)}</span>` : "";
      const statusClass = task.work_status === "free" ? "gray" : (task.work_status === "done" ? "" : "warn");

      return `
        <div class="card order-card ${isSelected ? "selected" : ""}" ${selectAttr}="${index}">
          <div class="order-head route-order-head">
            <div class="op-icon">▣</div>
            <div><b>${escapeHtml(task.operation)}</b><span>${escapeHtml(task.product_name)}${assignee}</span></div>
            <span class="status-chip ${statusClass}">${escapeHtml(task.status_text || "Свободно")}</span>
          </div>
          <div class="order-foot"><strong>${escapeHtml(task.product_size)} · ${escapeHtml(task.product_color)}</strong><strong>${escapeHtml(task.quantity)} шт</strong></div>
        </div>
      `;
    }

    function renderOrders() {
      if (state.data && state.data.is_admin && state.orderMode === "create") {
        renderOrderCreate();
        return;
      }

      const allTasks = visibleOrderRows();
      if (state.selectedOrder >= allTasks.length) state.selectedOrder = 0;
      const tasks = allTasks.filter((task) => task.task_kind !== "route");
      const routeRows = allTasks.filter((task) => task.task_kind === "route");
      const current = allTasks[state.selectedOrder] || allTasks[0];
      mainButton.textContent = state.data && state.data.is_admin ? "Создать задание" : (current && current.task_kind === "route" && current.is_assigned_to_me ? "Открыть отчёт" : (current ? "Выбрать задание" : "Обновить статус"));
      mainButton.disabled = false;

      mount.innerHTML = `
        <div class="screen-head"><div><h2>${state.data && state.data.is_admin ? "Заказы в работе" : "Задания"}</h2><p>${state.data && state.data.is_admin ? "Создание и контроль заданий." : "Выберите свободное задание, чтобы взять его в работу."}</p></div><div class="date">${allTasks.length} активных</div></div>
        ${state.data && state.data.is_admin ? `<div class="card shift-card" data-order-action="new"><div><b>Создать задание</b><span>Раскрой и следующие операции из складского остатка.</span></div><span class="status-chip">+</span></div>` : ""}
        <div class="op-list">
          ${allTasks.length ? `
          ${tasks.map((task, index) => `
            <div class="card order-card ${index === state.selectedOrder ? "selected" : ""}" data-select-order="${index}">
              <div class="order-head"><div class="op-icon">▣</div><div><b>${task.task_kind === "cutting_stage" ? escapeHtml(task.stage_title) : `Задание #${escapeHtml(task.id)}`}</b><span>${escapeHtml(task.product_name)}</span></div><span class="status-chip ${task.status === "active" ? "warn" : ""}">${escapeHtml(task.status_text || task.status)}</span></div>
              <div class="progress"><i style="--w:${progressForTask(task)}%"></i></div>
              <div class="order-foot"><span>${escapeHtml((task.sizes || []).join(", ") || task.colors_text || task.sizes_text || "-")}</span><span>${task.task_kind === "cutting_stage" ? escapeHtml(task.next_action) : `${progressForTask(task)}%`}</span></div>
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
          <div class="card order-detail"><div class="order-head"><div class="op-icon">${sewingIcon()}</div><div><b>Задание #${escapeHtml(current.id)}</b><span>${escapeHtml(current.product_name)}</span></div><span class="status-chip">${escapeHtml(current.status_text || current.status)}</span></div><div class="detail-grid"><div class="detail-box"><span>Размеры</span><strong>${escapeHtml((current.sizes || []).join(", ") || "-")}</strong></div><div class="detail-box"><span>Цвета</span><strong>${escapeHtml((current.color_labels || current.colors || []).join(", ") || "-")}</strong></div><div class="detail-box"><span>Статус</span><strong>${escapeHtml(current.status_text || current.status)}</strong></div><div class="detail-box"><span>Создано</span><strong>${escapeHtml((current.created_at || "").slice(0, 10) || "-")}</strong></div></div></div>
          ${renderTaskFabricRolls(current)}
          ${renderTaskAttachment(current.attachment)}
        ` : current ? `
          <div class="card order-detail"><div class="order-head"><div class="op-icon">${sewingIcon()}</div><div><b>${escapeHtml(current.operation)}</b><span>${escapeHtml(current.product_name)}${current.assigned_employee_name ? `<br>В работе: ${escapeHtml(current.assigned_employee_name)}` : ""}</span></div><span class="status-chip">${escapeHtml(current.status_text || "Свободно")}</span></div><div class="detail-grid"><div class="detail-box"><span>Размер</span><strong>${escapeHtml(current.product_size || "-")}</strong></div><div class="detail-box"><span>Цвет</span><strong>${escapeHtml(current.product_color || "-")}</strong></div><div class="detail-box"><span>Количество</span><strong>${escapeHtml(current.quantity || 0)} шт</strong></div><div class="detail-box"><span>Статус</span><strong>${escapeHtml(current.status_text || "-")}</strong></div></div></div>
        ` : `<div class="card order-detail">${itemEmpty("Детали появятся после создания задания.")}</div>`}
        ${state.data && state.data.is_admin && current ? `<div class="button-row"><button class="small-button danger" data-order-action="delete">Удалить задание</button></div>` : ""}
      `;
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

      mainButton.textContent = state.data && state.data.is_admin ? "Открыть заказы" : "Открыть задания";
      mainButton.disabled = false;

      mount.innerHTML = `
        <div class="screen-head"><div><h2>Статус производства</h2><p>Аналитика по текущим данным миниаппа.</p></div><div class="date">сейчас</div></div>
        <div class="card chart-card">
          <div class="chart-top"><div><b>Готовый крой</b><strong>${formed}<small> из ${tasks.length}</small></strong><small>сформированные задания</small></div><div class="ring" style="--p:${donePercent}"><strong>${donePercent}%</strong></div></div>
          <svg class="chart" viewBox="0 0 330 150" role="img" aria-label="График производства">
            <defs><linearGradient id="area" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#c36f55" stop-opacity=".28"/><stop offset="1" stop-color="#c36f55" stop-opacity="0"/></linearGradient></defs>
            <path d="M10 130H320" stroke="rgba(80,55,36,.16)"/><path d="M10 95H320" stroke="rgba(80,55,36,.12)"/><path d="M10 60H320" stroke="rgba(80,55,36,.12)"/><path d="M10 25H320" stroke="rgba(80,55,36,.12)"/>
            <path d="M12 126 C45 108,54 106,78 92 C103 78,110 85,132 70 C155 52,168 64,190 48 C215 32,232 54,258 42 C282 31,296 30,318 22 L318 136 L12 136 Z" fill="url(#area)"/>
            <path d="M12 126 C45 108,54 106,78 92 C103 78,110 85,132 70 C155 52,168 64,190 48 C215 32,232 54,258 42 C282 31,296 30,318 22" fill="none" stroke="#c36f55" stroke-width="4" stroke-linecap="round"/>
          </svg>
          <div class="mini-metrics">
            <div class="card mini-metric"><div class="ring" style="--p:${Math.round(operations.length / Math.max(operations.length, 1) * 100)}"><strong>${operations.length}</strong></div><b>Операции</b><span>в отчёте</span></div>
            <div class="card mini-metric"><div class="ring" style="--p:${Math.round(inCutting / total * 100)}"><strong>${inCutting}</strong></div><b>В раскрое</b><span>заданий</span></div>
            <div class="card mini-metric"><div class="ring" style="--p:${Math.round(active / total * 100)}"><strong>${active}</strong></div><b>Ожидают</b><span>контуры</span></div>
          </div>
        </div>
        <div class="section-title"><b>Показатели</b><button data-go="orders">${state.data && state.data.is_admin ? "все заказы" : "все задания"}</button></div>
        <div class="op-list">
          <div class="card shift-card"><div><b>Остатки ткани</b><span>${fabricRows.length} позиций</span></div><span class="status-chip gray">склад</span></div>
          <div class="card shift-card"><div><b>Обратная связь</b><span>${feedback.length} сообщений за смену</span></div><span class="status-chip gray">связь</span></div>
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
      const fabricRows = getProduction().fabric_stock || [];
      const warehouseRows = getWarehouseStock();
      const receiptColors = getOrderColors();
      const semifinished = warehouseRows.filter((row) => row.item_type === "semifinished");
      const finished = warehouseRows.filter((row) => row.item_type === "finished");
      const cuttingReady = semifinished.filter((row) => row.ready_for_position === "Раскройщик");
      const sewingReady = semifinished.filter((row) => row.ready_for_position === "Швея");
      const packingReady = semifinished.filter((row) => row.ready_for_position === "Упаковщик");
      mainButton.textContent = "Обновить склад";
      mainButton.disabled = false;

      if ((!state.fabricReceiptColor || !receiptColors.includes(state.fabricReceiptColor)) && receiptColors.length) {
        state.fabricReceiptColor = receiptColors[0];
      }

      const receiptColorOptions = receiptColors.map((color) => `
        <option value="${escapeHtml(color)}" ${color === state.fabricReceiptColor ? "selected" : ""}>${escapeHtml(color)}</option>
      `).join("");
      const materialHtml = fabricRows.length ? fabricRows.map((row) => `
        <div class="card report-row"><div><b>${escapeHtml(row.material_name)}</b><span>${escapeHtml(row.product_color_label || row.product_color)}</span></div><span class="status-chip">${escapeHtml(row.quantity_text)} ${escapeHtml(row.unit === "рул" ? "рул." : row.unit)}</span></div>
      `).join("") : itemEmpty("Материалов пока нет.");
      const stockList = (rows) => rows.length ? rows.map((row) => `
        <div class="card report-row"><div><b>${escapeHtml(row.title)}</b><span>${escapeHtml(row.product_size)} · ${escapeHtml(row.product_color_label || row.product_color)}<br>Для: ${escapeHtml(row.ready_for_position)}</span></div><span class="status-chip">${escapeHtml(row.quantity_text)} ${escapeHtml(row.unit)}</span></div>
      `).join("") : itemEmpty("Нет остатков.");

      return `
        <div class="screen-head"><div><h2>Склад</h2><p>Материалы, полуфабрикаты и готовая продукция.</p></div><div class="date">${warehouseRows.length + fabricRows.length} поз.</div></div>
        ${includeTabs ? renderAdminTabs() : ""}
        <div class="kpi-grid">
          <div class="card kpi"><div class="kpi-top"><span>Материалы</span><div class="kpi-ico">▦</div></div><strong>${fabricRows.length}<small> поз</small></strong><span>Ткань и материалы</span></div>
          <div class="card kpi"><div class="kpi-top"><span>Полуфабрикаты</span><div class="kpi-ico">▣</div></div><strong>${semifinished.length}<small> поз</small></strong><span>После этапов</span></div>
          <div class="card kpi good"><div class="kpi-top"><span>Готовое</span><div class="kpi-ico">✓</div></div><strong>${finished.length}<small> поз</small></strong><span>Готовая продукция</span></div>
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
        <div class="section-title"><b>Материалы</b><span>${fabricRows.length}</span></div>
        <div class="op-list">${materialHtml}</div>
        <div class="section-title"><b>Для раскроя</b><span>${cuttingReady.length}</span></div>
        <div class="op-list">${stockList(cuttingReady)}</div>
        <div class="section-title"><b>Для швеи</b><span>${sewingReady.length}</span></div>
        <div class="op-list">${stockList(sewingReady)}</div>
        <div class="section-title"><b>Для упаковщика</b><span>${packingReady.length}</span></div>
        <div class="op-list">${stockList(packingReady)}</div>
        <div class="section-title"><b>Готовая продукция</b><span>${finished.length}</span></div>
        <div class="op-list">${stockList(finished)}</div>
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
          <div class="card kpi"><div class="kpi-top"><span>Смены</span><div class="kpi-ico">◷</div></div><strong>${totals.shifts}<small> шт</small></strong><span>Закрытые смены</span></div>
          <div class="card kpi good"><div class="kpi-top"><span>Часы</span><div class="kpi-ico">✓</div></div><strong>${escapeHtml(minutesLabel(totals.minutes))}</strong><span>Суммарно отработано</span></div>
          <div class="card kpi"><div class="kpi-top"><span>Операции</span><div class="kpi-ico">${sewingIcon()}</div></div><strong>${totals.operations}<small> строк</small></strong><span>Строки отчёта</span></div>
          <div class="card kpi"><div class="kpi-top"><span>Сотрудники</span><div class="kpi-ico">◎</div></div><strong>${totals.employees}<small> чел</small></strong><span>В выборке</span></div>
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
      const employees = admin && admin.employees ? admin.employees : [];
      const pending = admin && admin.pending_employees ? admin.pending_employees : [];
      const positions = admin && admin.positions ? admin.positions : [];
      mainButton.textContent = "Обновить сотрудников";

      const positionOptions = (employee) => positions.map((position) => `
        <option value="${escapeHtml(position)}" ${employee.position === position ? "selected" : ""}>${escapeHtml(position)}</option>
      `).join("");
      const employeeCards = employees.length ? employees.map((employee) => `
        <div class="card field-card">
          <label>ID ${escapeHtml(employee.id)} · ${escapeHtml(employee.status)}</label>
          <div class="report-row"><div><b>${escapeHtml(employee.full_name)}</b><span>${escapeHtml(employee.position)} · TG ${escapeHtml(employee.telegram_id || "-")}</span></div><span class="status-chip ${employee.status === "active" ? "" : "gray"}">${escapeHtml(employee.status)}</span></div>
          <div class="form-grid"><div class="field full"><select id="employeePosition${escapeHtml(employee.id)}">${positionOptions(employee)}</select></div></div>
          <div class="button-row"><button class="small-button secondary" data-admin-action="position" data-employee-id="${escapeHtml(employee.id)}">Должность</button><button class="small-button ${employee.status === "active" ? "danger" : ""}" data-admin-action="${employee.status === "active" ? "inactive" : "active"}" data-employee-id="${escapeHtml(employee.id)}">${employee.status === "active" ? "Отключить" : "Активировать"}</button></div>
        </div>
      `).join("") : itemEmpty("Сотрудников пока нет.");
      const pendingCards = pending.length ? pending.map((employee) => `
        <div class="card field-card">
          <label>Заявка · ${escapeHtml(employee.registered_at || "")}</label>
          <div class="report-row"><div><b>${escapeHtml(employee.full_name)}</b><span>${escapeHtml(employee.position)} · TG ${escapeHtml(employee.telegram_id || "-")}</span></div><span class="status-chip warn">pending</span></div>
          <div class="button-row"><button class="small-button secondary" data-admin-action="inactive" data-employee-id="${escapeHtml(employee.id)}">Отклонить</button><button class="small-button" data-admin-action="active" data-employee-id="${escapeHtml(employee.id)}">Активировать</button></div>
        </div>
      `).join("") : itemEmpty("Новых заявок нет.");

      return `
        <div class="screen-head"><div><h2>Сотрудники</h2><p>Заявки, статусы и должности.</p></div><div class="date">${employees.length} всего</div></div>
        ${renderAdminTabs()}
        <div class="kpi-grid">
          <div class="card kpi"><div class="kpi-top"><span>Заявки</span><div class="kpi-ico">◎</div></div><strong>${pending.length}<small> шт</small></strong><span>Ожидают решения</span></div>
          <div class="card kpi good"><div class="kpi-top"><span>Активные</span><div class="kpi-ico">✓</div></div><strong>${(admin.active_employees || []).length}<small> чел</small></strong><span>Могут работать</span></div>
        </div>
        <div class="section-title"><b>Заявки</b><span>${pending.length}</span></div>
        <div class="op-list">${pendingCards}</div>
        <div class="section-title"><b>Список сотрудников</b><button data-admin-action="refresh">обновить</button></div>
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

    function render() {
      if (!state.data) return;
      document.getElementById("roleLabel").textContent = roleLabel();
      if (state.screen === "shift") renderShift();
      if (state.screen === "operations") renderOperations();
      if (state.screen === "report") renderReport();
      if (state.screen === "warehouse") renderWarehouse();
      if (state.screen === "analytics") renderAnalytics();
      if (state.screen === "orders") renderOrders();
      if (state.screen === "admin") renderAdmin();
      renderBottomNav();
      renderTopTabs();
    }

    function setScreen(screen) {
      state.screen = screen;
      render();
    }

    async function refreshState(message = "") {
      mainButton.disabled = true;
      try {
        const data = await api("/api/app/state", {message});
        state.data = data;
        if (message) showToast("Готово", message);
        render();
      } catch (error) {
        showToast("Ошибка", "Не удалось связаться с сервером.");
      }
    }

    async function shiftAction(action) {
      mainButton.disabled = true;
      const data = await api(`/api/shift/${action}`);
      state.data = data;
      render();
      showToast("Смена", data.message || "Данные обновлены.");
    }

    document.addEventListener("click", (event) => {
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
          deleteOrderTask();
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

      const warehouseAction = event.target.closest("[data-warehouse-action]");
      if (warehouseAction) {
        syncWarehouseReceiptForm();
        if (warehouseAction.dataset.warehouseAction === "receipt") {
          addFabricReceipt();
        }
        if (warehouseAction.dataset.warehouseAction === "refresh") {
          refreshAdminDashboard("Склад обновлён.");
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
        render();
        return;
      }

      const reportSection = event.target.closest("[data-report-section]");
      if (reportSection) {
        state.reportSection = reportSection.dataset.reportSection;
        state.selectedReportTask = 0;
        state.selectedCuttingReportTask = 0;
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

      const go = event.target.closest("[data-go]");
      if (go) {
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
        if (adminAction.dataset.adminAction === "position") adminEmployeePosition(adminAction.dataset.employeeId);
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

      const reportAction = event.target.closest("[data-report-action]");
      if (reportAction) {
        if (reportAction.dataset.reportAction === "complete-task") {
          const tasks = getMyRouteTasks();
          completeOperationTask(tasks[state.selectedReportTask] || tasks[0]);
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
        render();
      }

      const cuttingReportTask = event.target.closest("[data-select-cutting-report-task]");
      if (cuttingReportTask) {
        state.selectedCuttingReportTask = Number(cuttingReportTask.dataset.selectCuttingReportTask);
        render();
      }
    });

    mainButton.addEventListener("click", () => {
      if (!state.data) return;
      if (state.screen === "shift") {
        if (state.data.is_admin) {
          refreshAdminDashboard("Главная обновлена.");
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
          if (current) { completeOperationTask(current); return; }
        }
        refreshState("Отчёт обновлён.");
        return;
      }
      if (state.screen === "warehouse") { refreshAdminDashboard("Склад обновлён."); return; }
      if (state.screen === "analytics") { setScreen("orders"); return; }
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
        if (current && current.task_kind === "route") { startOperationTask(current); return; }
        refreshState("Статус обновлён.");
        return;
      }
      if (state.screen === "admin") {
        if (state.adminSection === "reports") { exportAdminReport(); return; }
        if (state.adminSection === "feedback") { loadAdminFeedback(); return; }
        refreshAdminDashboard();
      }
    });

    document.addEventListener("change", (event) => {
      const attachmentInput = event.target.closest("#orderAttachment");
      if (attachmentInput) {
        readOrderAttachment(attachmentInput.files && attachmentInput.files[0]);
        return;
      }

      if (event.target.closest("#fabricReceiptMaterial") || event.target.closest("#fabricReceiptColor") || event.target.closest("#fabricReceiptQuantity")) {
        syncWarehouseReceiptForm();
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

      if (event.target.closest("#orderProduct") || event.target.closest("#orderTaskType") || event.target.closest("#orderRouteStep") || event.target.closest("#orderMaterial") || event.target.closest("#orderQuantity") || event.target.closest("[data-stock-quantity]") || event.target.closest("[data-fabric-rolls]")) {
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

      if (!event.target.closest("#adminReportType")) return;
      syncAdminForm();
      render();
    });

    document.getElementById("backBtn").addEventListener("click", () => {
      if (state.screen === "shift" && state.data && state.data.is_admin && state.adminHomeView !== "overview") {
        state.adminHomeView = state.adminHomeView === "employee" ? "employees" : "overview";
        state.adminHomeEmployee = "";
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
      if (state.data && state.data.is_admin) {
        setScreen("admin");
        return;
      }
      showToast("Меню", "Настройки профиля и уведомления подключим позже.");
    });

    refreshState();
  </script>
</body>
</html>
"""
