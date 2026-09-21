"""
Global CSS Theme — NiceGUI 3.x (Quasar) Compatible
"""

FONT_LINK = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons+Round">
"""

GLOBAL_CSS = """
/* ═══════════════════════════════════════════════
   CSS TOKENS
═══════════════════════════════════════════════ */
:root {
  --color-primary:       #2563EB;
  --color-primary-light: #3B82F6;
  --color-primary-dark:  #1D4ED8;
  --color-secondary:     #6366F1;
  --color-success:       #10B981;
  --color-warning:       #F59E0B;
  --color-danger:        #EF4444;
  --color-info:          #06B6D4;
  --bg:         #F8FAFC;
  --bg-surface: #FFFFFF;
  --bg-subtle:  #F1F5F9;
  --border:     #E2E8F0;
  --text-primary:   #0F172A;
  --text-secondary: #64748B;
  --text-muted:     #94A3B8;
  --radius-sm: 6px;
  --radius:    12px;
  --radius-lg: 16px;
  --radius-xl: 24px;
  --shadow-sm: 0 1px 3px rgba(0,0,0,.06),0 1px 2px rgba(0,0,0,.04);
  --shadow:    0 4px 6px -1px rgba(0,0,0,.07),0 2px 4px -1px rgba(0,0,0,.04);
  --shadow-md: 0 10px 15px -3px rgba(0,0,0,.08),0 4px 6px -2px rgba(0,0,0,.04);
  --shadow-lg: 0 20px 25px -5px rgba(0,0,0,.10),0 10px 10px -5px rgba(0,0,0,.04);
  --shadow-xl: 0 25px 50px -12px rgba(0,0,0,.18);
  --transition:      .2s cubic-bezier(.4,0,.2,1);
  --transition-slow: .35s cubic-bezier(.4,0,.2,1);
}

body.dark-mode {
  --bg:         #0F172A;
  --bg-surface: #1E293B;
  --bg-subtle:  #0F172A;
  --border:     #334155;
  --text-primary:   #F1F5F9;
  --text-secondary: #94A3B8;
  --text-muted:     #64748B;
}

/* ═══════════════════════════════════════════════
   BASE RESET
═══════════════════════════════════════════════ */
*, *::before, *::after { box-sizing: border-box; }
html, body {
  font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
  font-size: 14px; line-height: 1.6;
  color: var(--text-primary); background: var(--bg);
  -webkit-font-smoothing: antialiased;
  height: 100%; margin: 0; padding: 0;
}

/* ═══════════════════════════════════════════════
   NICEGUI / QUASAR OVERRIDES
═══════════════════════════════════════════════ */
.q-layout, #q-app { width: 100% !important; max-width: none !important; }
.q-page { padding: 0 !important; min-height: 0 !important; background: var(--bg) !important; width: 100% !important; max-width: none !important; }
.nicegui-content { padding: 0 !important; flex: 1 !important; min-height: 0 !important; max-width: none !important; width: 100% !important; }

.q-header {
  background: var(--bg-surface) !important;
  color: var(--text-primary) !important;
  border-bottom: 1px solid var(--border) !important;
  box-shadow: none !important;
  transition: background var(--transition-slow), border-color var(--transition-slow) !important;
}
.q-drawer {
  background: var(--bg-surface) !important;
  border-right: 1px solid var(--border) !important;
  transition: background var(--transition-slow) !important;
}
.q-drawer .q-scrollarea, .q-drawer .q-scrollarea__content { width: 100% !important; }

/* ═══════════════════════════════════════════════
   SCROLLBAR
═══════════════════════════════════════════════ */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 99px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }

/* ═══════════════════════════════════════════════
   TOPBAR (inside ui.header)
═══════════════════════════════════════════════ */
.topbar {
  display: flex; align-items: center;
  padding: 0 24px; gap: 16px;
  height: 64px; width: 100%;
  background: transparent;
}
.topbar-breadcrumb {
  flex: 1; display: flex; align-items: center;
  gap: 6px; color: var(--text-secondary); font-size: 13px;
}
.topbar-breadcrumb .crumb-active { color: var(--text-primary); font-weight: 600; }
.topbar-actions { display: flex; align-items: center; gap: 10px; }

.clock-display {
  font-size: 13px; font-weight: 500;
  color: var(--text-secondary); padding: 6px 12px;
  background: var(--bg-subtle); border-radius: var(--radius);
  font-variant-numeric: tabular-nums;
}
.icon-btn {
  width: 36px; height: 36px; border-radius: var(--radius);
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; color: var(--text-secondary);
  transition: background var(--transition), color var(--transition);
  border: none; background: transparent;
}
.icon-btn:hover { background: var(--bg-subtle); color: var(--text-primary); }

/* ═══════════════════════════════════════════════
   SIDEBAR NAV (inside ui.left_drawer)
═══════════════════════════════════════════════ */
.sidebar-logo {
  padding: 14px 18px; display: flex; align-items: center;
  gap: 10px; border-bottom: 1px solid var(--border);
  height: 64px; flex-shrink: 0;
}
.sidebar-logo-icon {
  width: 36px; height: 36px;
  background: linear-gradient(135deg,var(--color-primary),var(--color-secondary));
  border-radius: var(--radius-sm);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; box-shadow: 0 4px 12px rgba(37,99,235,.35);
}
.sidebar-nav { flex:1; padding: 12px 10px; overflow-y: auto; }
.nav-section-label {
  font-size: 10px; font-weight: 600; text-transform: uppercase;
  letter-spacing: .8px; color: var(--text-muted); padding: 10px 8px 4px;
  white-space: nowrap;
}
.nav-item {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 12px; border-radius: var(--radius);
  cursor: pointer; transition: background var(--transition),color var(--transition);
  color: var(--text-secondary); text-decoration: none !important;
  position: relative; margin-bottom: 2px;
  border-left: 3px solid transparent;
}
.nav-item:hover { background: var(--bg-subtle); color: var(--text-primary); }
.nav-item.active {
  background: rgba(37,99,235,.1); color: var(--color-primary) !important;
  font-weight: 600; border-left-color: var(--color-primary);
}
.nav-item .material-icons-round { font-size: 20px; flex-shrink: 0; }
.nav-label { font-size: 13.5px; font-weight: 500; }
.sidebar-footer { padding: 12px 10px; border-top: 1px solid var(--border); }
.separator { height: 1px; background: var(--border); margin: 8px 0; }

/* ═══════════════════════════════════════════════
   PAGE AREA
═══════════════════════════════════════════════ */
.page-area { padding: 28px; background: var(--bg); min-height: 100%; transition: background var(--transition-slow); }
.page-header { margin-bottom: 24px; }
.page-title { font-size: 24px; font-weight: 700; color: var(--text-primary); letter-spacing: -.4px; }
.page-subtitle { font-size: 13.5px; color: var(--text-secondary); margin-top: 4px; }

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(16px); }
  to   { opacity: 1; transform: translateY(0); }
}
.page-fade-in { animation: fadeInUp .35s ease both; }

/* ═══════════════════════════════════════════════
   STAT CARDS
═══════════════════════════════════════════════ */
.stat-card {
  background: var(--bg-surface); border-radius: var(--radius-lg);
  padding: 22px 24px; border: 1px solid var(--border);
  box-shadow: var(--shadow-sm); overflow: hidden; position: relative;
  transition: transform var(--transition),box-shadow var(--transition),border-color var(--transition);
  animation: fadeInUp .4s ease both;
}
.stat-card:hover { transform: translateY(-3px); box-shadow: var(--shadow-md); border-color: rgba(37,99,235,.2); }
.stat-card-gradient { position: absolute; top: -30px; right: -30px; width: 120px; height: 120px; border-radius: 50%; opacity: .08; }
.stat-icon { width: 44px; height: 44px; border-radius: var(--radius); display: flex; align-items: center; justify-content: center; margin-bottom: 14px; }
.stat-icon .material-icons-round { font-size: 22px; color: #fff; }
.stat-value { font-size: 28px; font-weight: 800; letter-spacing: -1px; color: var(--text-primary); font-variant-numeric: tabular-nums; }
.stat-label { font-size: 12px; font-weight: 500; text-transform: uppercase; letter-spacing: .6px; color: var(--text-muted); margin-top: 2px; }
.stat-trend { display: flex; align-items: center; gap: 4px; font-size: 12px; font-weight: 500; margin-top: 8px; }

/* ═══════════════════════════════════════════════
   CARDS
═══════════════════════════════════════════════ */
.card { background: var(--bg-surface); border-radius: var(--radius-lg); border: 1px solid var(--border); box-shadow: var(--shadow-sm); transition: background var(--transition-slow),border-color var(--transition-slow); }
.card-header { display: flex; align-items: center; justify-content: space-between; padding: 18px 22px; border-bottom: 1px solid var(--border); }
.card-title { font-size: 15px; font-weight: 600; color: var(--text-primary); }
.card-body { padding: 22px; }

/* ═══════════════════════════════════════════════
   BUTTONS (VIBRANT MODERN DESIGN)
═══════════════════════════════════════════════ */
.btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 8px;
  padding: 9px 18px; border-radius: 10px;
  font-size: 13.5px; font-weight: 600; font-family: inherit;
  cursor: pointer; border: 1px solid transparent;
  transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative; overflow: hidden; outline: none; text-decoration: none;
  user-select: none;
}
.btn::after {
  content: ''; position: absolute; inset: 0;
  background: radial-gradient(circle, rgba(255,255,255,.35) 0%, transparent 70%);
  opacity: 0; transition: opacity .15s;
}
.btn:active::after { opacity: 1; }

.btn-primary {
  background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
  color: #ffffff !important;
  box-shadow: 0 4px 14px rgba(37, 99, 235, 0.35) !important;
}
.btn-primary:hover {
  transform: translateY(-1.5px);
  box-shadow: 0 6px 20px rgba(37, 99, 235, 0.48) !important;
  filter: brightness(1.05);
}
.btn-primary:active {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(37, 99, 235, 0.3) !important;
}

.btn-success {
  background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
  color: #ffffff !important;
  box-shadow: 0 4px 14px rgba(16, 185, 129, 0.35) !important;
}
.btn-success:hover {
  transform: translateY(-1.5px);
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.48) !important;
  filter: brightness(1.05);
}
.btn-success:active {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3) !important;
}

.btn-danger {
  background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%) !important;
  color: #ffffff !important;
  box-shadow: 0 4px 14px rgba(239, 68, 68, 0.35) !important;
}
.btn-danger:hover {
  transform: translateY(-1.5px);
  box-shadow: 0 6px 20px rgba(239, 68, 68, 0.48) !important;
  filter: brightness(1.05);
}
.btn-danger:active {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.3) !important;
}

.btn-warning {
  background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%) !important;
  color: #ffffff !important;
  box-shadow: 0 4px 14px rgba(245, 158, 11, 0.35) !important;
}
.btn-warning:hover {
  transform: translateY(-1.5px);
  box-shadow: 0 6px 20px rgba(245, 158, 11, 0.48) !important;
}

.btn-info {
  background: linear-gradient(135deg, #0EA5E9 0%, #0284C7 100%) !important;
  color: #ffffff !important;
  box-shadow: 0 4px 14px rgba(14, 165, 233, 0.35) !important;
}
.btn-info:hover {
  transform: translateY(-1.5px);
  box-shadow: 0 6px 20px rgba(14, 165, 233, 0.48) !important;
}

.btn-secondary {
  background: #F1F5F9 !important;
  color: #334155 !important;
  border: 1px solid #CBD5E1 !important;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05) !important;
}
.btn-secondary:hover {
  background: #E2E8F0 !important;
  color: #0F172A !important;
  border-color: #94A3B8 !important;
  transform: translateY(-1px);
}

.btn-reset {
  background: #FEF2F2 !important;
  color: #DC2626 !important;
  border: 1px solid #FECACA !important;
  font-weight: 600 !important;
  box-shadow: 0 1px 2px rgba(239, 68, 68, 0.05) !important;
}
.btn-reset:hover {
  background: #FEE2E2 !important;
  color: #B91C1C !important;
  border-color: #FCA5A5 !important;
  transform: translateY(-1px);
  box-shadow: 0 3px 8px rgba(239, 68, 68, 0.18) !important;
}

.btn-sm  { padding: 6px 14px; font-size: 12.5px; border-radius: 8px; }
.btn-lg  { padding: 12px 26px; font-size: 15px; border-radius: 12px; }
.btn:disabled, .btn[disabled] { opacity: .5; cursor: not-allowed; transform: none !important; box-shadow: none !important; }

/* Quasar Native Button Enhancements */
.q-btn {
  font-weight: 600 !important;
  letter-spacing: 0.2px !important;
  border-radius: 8px !important;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
}
.q-btn--unelevated.bg-primary {
  background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
}
.q-btn--unelevated.bg-primary:hover {
  transform: translateY(-1.5px) !important;
  box-shadow: 0 6px 18px rgba(37, 99, 235, 0.42) !important;
}
.q-btn--unelevated.bg-negative {
  background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%) !important;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3) !important;
}
.q-btn--unelevated.bg-positive {
  background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3) !important;
}

/* Action Icons inside Table Rows */
.action-btn-edit {
  background: #EFF6FF !important;
  color: #2563EB !important;
  border-radius: 8px !important;
  width: 32px !important;
  height: 32px !important;
  min-height: 32px !important;
  padding: 0 !important;
  transition: all 0.2s ease !important;
}
.action-btn-edit:hover {
  background: #2563EB !important;
  color: #ffffff !important;
  transform: scale(1.1) !important;
  box-shadow: 0 4px 10px rgba(37, 99, 235, 0.35) !important;
}
.action-btn-delete {
  background: #FEF2F2 !important;
  color: #EF4444 !important;
  border-radius: 8px !important;
  width: 32px !important;
  height: 32px !important;
  min-height: 32px !important;
  padding: 0 !important;
  transition: all 0.2s ease !important;
}
.action-btn-delete:hover {
  background: #EF4444 !important;
  color: #ffffff !important;
  transform: scale(1.1) !important;
  box-shadow: 0 4px 10px rgba(239, 68, 68, 0.35) !important;
}
.action-btn-view {
  background: #ECFDF5 !important;
  color: #059669 !important;
  border-radius: 8px !important;
  width: 32px !important;
  height: 32px !important;
  min-height: 32px !important;
  padding: 0 !important;
  transition: all 0.2s ease !important;
}
.action-btn-view:hover {
  background: #10B981 !important;
  color: #ffffff !important;
  transform: scale(1.1) !important;
  box-shadow: 0 4px 10px rgba(16, 185, 129, 0.35) !important;
}
.action-btn-download {
  background: #F0F9FF !important;
  color: #0284C7 !important;
  border-radius: 8px !important;
  width: 32px !important;
  height: 32px !important;
  min-height: 32px !important;
  padding: 0 !important;
  transition: all 0.2s ease !important;
}
.action-btn-download:hover {
  background: #0284C7 !important;
  color: #ffffff !important;
  transform: scale(1.1) !important;
  box-shadow: 0 4px 10px rgba(2, 132, 199, 0.35) !important;
}

/* ═══════════════════════════════════════════════
   BADGES
═══════════════════════════════════════════════ */
.badge { display: inline-flex; align-items: center; gap: 4px; padding: 4px 11px; border-radius: 99px; font-size: 11.5px; font-weight: 600; letter-spacing: 0.2px; }
.badge-success { background: rgba(16,185,129,.14); color: #059669; border: 1px solid rgba(16,185,129,.25); }
.badge-danger  { background: rgba(239,68,68,.14);  color: #DC2626; border: 1px solid rgba(239,68,68,.25); }
.badge-warning { background: rgba(245,158,11,.14); color: #D97706; border: 1px solid rgba(245,158,11,.25); }
.badge-info    { background: rgba(37,99,235,.12);   color: #2563EB; border: 1px solid rgba(37,99,235,.25); }
.badge-gray    { background: #F1F5F9;     color: #475569; border: 1px solid #E2E8F0; }

/* ═══════════════════════════════════════════════
   FORM ELEMENTS & DROPDOWNS
═══════════════════════════════════════════════ */
.form-label { display: block; font-size: 12.5px; font-weight: 700; color: #475569; margin-bottom: 6px; text-transform: uppercase; letter-spacing: .5px; }
.form-control { width: 100%; padding: 9px 13px; border: 1.5px solid #CBD5E1; border-radius: 10px; background: #F8FAFC; color: var(--text-primary); font-family: inherit; font-size: 14px; transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1); outline: none; }
.form-control:focus { border-color: #2563EB; background: #FFFFFF; box-shadow: 0 0 0 3.5px rgba(37,99,235,.18); }
.form-control::placeholder { color: var(--text-muted); }

/* Quasar Input & Select Styling for Admin Pages */
.q-field--outlined:not(.glass-input):not(.login-input) .q-field__control {
  border-radius: 10px !important;
  background: #F8FAFC !important;
  border: 1.5px solid #CBD5E1 !important;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
}
.q-field--outlined:not(.glass-input):not(.login-input) .q-field__control:before {
  display: none !important;
}
.q-field--outlined:not(.glass-input):not(.login-input):hover .q-field__control {
  border-color: #6366F1 !important;
  background: #FFFFFF !important;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.08) !important;
}
.q-field--focused:not(.glass-input):not(.login-input) .q-field__control,
.q-field--highlighted:not(.glass-input):not(.login-input) .q-field__control {
  border-color: #2563EB !important;
  background: #FFFFFF !important;
  box-shadow: 0 0 0 3.5px rgba(37, 99, 235, 0.18) !important;
}
.q-field:not(.glass-input):not(.login-input) .q-field__label {
  font-size: 13px !important;
  font-weight: 600 !important;
  color: #64748B !important;
  letter-spacing: 0.2px !important;
}
.q-field--focused:not(.glass-input):not(.login-input) .q-field__label {
  color: #2563EB !important;
  font-weight: 700 !important;
}
.q-select:not(.glass-input):not(.login-input) .q-field__marginal {
  color: #6366F1 !important;
}
.q-field__marginal .q-icon {
  font-size: 20px !important;
  transition: transform 0.2s ease, color 0.2s ease !important;
}
.q-field--focused:not(.glass-input):not(.login-input) .q-field__marginal .q-icon {
  color: #2563EB !important;
}
.q-field:not(.glass-input):not(.login-input) .q-field__native,
.q-field:not(.glass-input):not(.login-input) .q-field__input,
.q-field:not(.glass-input):not(.login-input) input {
  color: #0F172A !important;
  font-size: 14px !important;
}

/* Dark Mode Form & Select Controls */
body.dark-mode .q-field--outlined:not(.glass-input):not(.login-input) .q-field__control {
  background: #1E293B !important;
  border-color: #334155 !important;
}
body.dark-mode .q-field--outlined:not(.glass-input):not(.login-input) .q-field__control:hover {
  border-color: #60A5FA !important;
  background: #0F172A !important;
}
body.dark-mode .q-field--focused:not(.glass-input):not(.login-input) .q-field__control {
  border-color: #3B82F6 !important;
  background: #0F172A !important;
  box-shadow: 0 0 0 3.5px rgba(59, 130, 246, 0.25) !important;
}
body.dark-mode .q-field:not(.glass-input):not(.login-input) .q-field__native,
body.dark-mode .q-field:not(.glass-input):not(.login-input) .q-field__input,
body.dark-mode .q-field:not(.glass-input):not(.login-input) input {
  color: #F8FAFC !important;
}

/* Prevent text wrapping in select dropdowns and input fields */
.q-select .q-field__native,
.q-field .q-field__native,
.q-field .q-field__input,
.q-select .q-field__native span {
  white-space: nowrap !important;
  text-overflow: ellipsis !important;
  overflow: hidden !important;
  flex-wrap: nowrap !important;
  line-height: normal !important;
}

.q-select .q-field__control {
  flex-wrap: nowrap !important;
}

/* ═══════════════════════════════════════════════
   TABLES (DATA TABLE & TABLE WRAPPERS)
═══════════════════════════════════════════════ */
.data-table-wrapper {
  width: 100%;
  overflow-x: auto;
  border-radius: var(--radius-lg);
  border: 1px solid var(--border);
  background: var(--bg-surface);
  box-shadow: var(--shadow-sm);
}
.data-table {
  width: 100% !important;
  border-collapse: collapse !important;
  font-size: 13.5px !important;
  table-layout: auto !important;
}
.data-table thead th {
  padding: 13px 18px !important;
  text-align: left !important;
  font-size: 11.5px !important;
  font-weight: 700 !important;
  text-transform: uppercase !important;
  letter-spacing: .6px !important;
  color: var(--text-secondary) !important;
  background: var(--bg-subtle) !important;
  border-bottom: 1px solid var(--border) !important;
  white-space: nowrap !important;
  cursor: pointer !important;
  user-select: none !important;
}
.data-table thead th:hover {
  color: var(--text-primary) !important;
}
.data-table tbody tr {
  border-bottom: 1px solid var(--border) !important;
  transition: background var(--transition) !important;
  animation: tableRowFadeIn .25s ease both !important;
}
.data-table tbody tr:last-child {
  border-bottom: none !important;
}
.data-table tbody tr:hover {
  background: var(--bg-subtle) !important;
}
.data-table td {
  padding: 13px 18px !important;
  color: var(--text-primary) !important;
  vertical-align: middle !important;
}
@keyframes tableRowFadeIn {
  from { opacity: 0; transform: translateX(-6px); }
  to   { opacity: 1; transform: translateX(0); }
}

/* ═══════════════════════════════════════════════
   MODAL
═══════════════════════════════════════════════ */
.modal-box {
  background: var(--bg-surface);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  max-width: 560px;
  width: calc(100% - 48px);
  animation: scaleIn .25s cubic-bezier(.34,1.56,.64,1);
  border: 1px solid var(--border);
}
@keyframes scaleIn {
  from { opacity: 0; transform: scale(.92) translateY(10px); }
  to   { opacity: 1; transform: scale(1) translateY(0); }
}
.modal-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 20px 24px; border-bottom: 1px solid var(--border);
}
.modal-title { font-size: 17px; font-weight: 700; color: var(--text-primary); }
.modal-body { padding: 24px; }
.modal-footer {
  display: flex; justify-content: flex-end; gap: 10px;
  padding: 16px 24px; border-top: 1px solid var(--border);
}

/* ═══════════════════════════════════════════════
   TOAST NOTIFICATIONS
═══════════════════════════════════════════════ */
#toast-container {
  position: fixed; top: 20px; right: 20px; z-index: 9999;
  display: flex; flex-direction: column; gap: 10px; pointer-events: none;
}
.toast {
  display: flex; align-items: flex-start; gap: 12px; padding: 14px 18px;
  border-radius: var(--radius-lg); background: var(--bg-surface);
  box-shadow: var(--shadow-xl); border: 1px solid var(--border);
  min-width: 300px; max-width: 400px; pointer-events: auto;
  animation: toastSlideIn .3s cubic-bezier(.34,1.56,.64,1);
  position: relative;
}
.toast.hiding { animation: toastSlideOut .25s ease forwards; }
@keyframes toastSlideIn { from { opacity: 0; transform: translateX(60px) scale(.9); } to { opacity: 1; transform: translateX(0) scale(1); } }
@keyframes toastSlideOut { from { opacity: 1; transform: translateX(0); max-height: 100px; } to { opacity: 0; transform: translateX(60px); max-height: 0; padding: 0; margin: 0; } }
.toast-icon {
  width: 32px; height: 32px; border-radius: var(--radius);
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.toast-icon .material-icons-round { font-size: 18px; color: #fff; }
.toast-success .toast-icon { background: var(--color-success); }
.toast-error   .toast-icon { background: var(--color-danger); }
.toast-warning .toast-icon { background: var(--color-warning); }
.toast-info    .toast-icon { background: var(--color-info); }
.toast-content { flex: 1; }
.toast-title   { font-size: 13.5px; font-weight: 700; color: var(--text-primary); }
.toast-message { font-size: 12.5px; color: var(--text-secondary); margin-top: 2px; }
.toast-progress {
  position: absolute; bottom: 0; left: 0; height: 3px;
  border-radius: 0 0 var(--radius-lg) var(--radius-lg);
  animation: toastProgress linear forwards;
}
.toast-success .toast-progress { background: var(--color-success); }
.toast-error   .toast-progress { background: var(--color-danger); }
@keyframes toastProgress { from { width: 100%; } to { width: 0%; } }

/* ═══════════════════════════════════════════════
   UPLOAD AREA
═══════════════════════════════════════════════ */
.upload-zone {
  border: 2px dashed var(--border); border-radius: var(--radius-xl);
  padding: 60px 40px; text-align: center; cursor: pointer;
  transition: all var(--transition); background: var(--bg-subtle);
}
.upload-zone:hover, .upload-zone.dragover {
  border-color: var(--color-primary); background: rgba(37,99,235,.04); transform: scale(1.005);
}
.upload-icon {
  width: 64px; height: 64px;
  background: linear-gradient(135deg,rgba(37,99,235,.1),rgba(99,102,241,.1));
  border-radius: var(--radius-xl); display: flex; align-items: center;
  justify-content: center; margin: 0 auto 16px; transition: transform var(--transition);
}
.upload-zone:hover .upload-icon { transform: scale(1.08); }
.upload-icon .material-icons-round { font-size: 32px; color: var(--color-primary); }

/* ═══════════════════════════════════════════════
   PROGRESS BAR
═══════════════════════════════════════════════ */
.progress-bar-wrapper { background: var(--bg-subtle); border-radius: 99px; height: 8px; overflow: hidden; }
.progress-bar-fill {
  height: 100%; border-radius: 99px;
  background: linear-gradient(90deg,var(--color-primary),var(--color-secondary));
  transition: width .4s ease; position: relative; overflow: hidden;
}
.progress-bar-fill::after {
  content: ''; position: absolute; top: 0; left: -100%; width: 100%; height: 100%;
  background: linear-gradient(90deg,transparent,rgba(255,255,255,.4),transparent);
  animation: shimmer 1.5s infinite;
}
@keyframes shimmer { to { left: 100%; } }

/* ═══════════════════════════════════════════════
   LOGIN PAGE & PORTAL — Full screen fixed overlay
═══════════════════════════════════════════════ */
.login-bg {
  position: fixed !important; top: 0; left: 0; right: 0; bottom: 0;
  background: linear-gradient(135deg, #0B1221 0%, #1a2744 50%, #0B1221 100%);
  display: flex !important; align-items: center !important; justify-content: center !important;
  z-index: 100; overflow-y: auto; overflow-x: hidden; padding: 24px;
}
@media (max-height: 800px) {
  .login-bg { align-items: flex-start !important; }
}
.login-orb {
  position: absolute; border-radius: 50%; filter: blur(80px);
  opacity: .18; animation: orb 8s ease-in-out infinite alternate; pointer-events: none;
}
.login-orb-1 { width: 600px; height: 600px; background: #2563EB; top: -200px; right: -100px; }
.login-orb-2 { width: 400px; height: 400px; background: #6366F1; bottom: -100px; left: -50px; animation-delay: -4s; }
@keyframes orb {
  from { transform: scale(1) translate(0,0); }
  to   { transform: scale(1.1) translate(20px,20px); }
}
.login-card {
  position: relative; z-index: 1;
  background: rgba(15,28,54,.85);
  backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px);
  border: 1px solid rgba(255,255,255,.1);
  border-radius: 24px; padding: 32px 24px; width: 100%; max-width: 420px; margin: 0 auto;
  box-shadow: 0 25px 50px -12px rgba(0,0,0,.6);
  animation: fadeInUp .5s ease;
}
/* Login Card Form Inputs */
.login-card .q-field--outlined .q-field__control,
.login-input.q-field--outlined .q-field__control {
  background: rgba(255, 255, 255, 0.08) !important;
  border: 1.5px solid rgba(255, 255, 255, 0.18) !important;
  border-radius: 12px !important;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
}
.login-card .q-field--outlined .q-field__control:before,
.login-input.q-field--outlined .q-field__control:before {
  display: none !important;
}
.login-card .q-field--outlined:hover .q-field__control,
.login-input.q-field--outlined:hover .q-field__control {
  background: rgba(255, 255, 255, 0.12) !important;
  border-color: rgba(255, 255, 255, 0.35) !important;
}
.login-card .q-field--focused .q-field__control,
.login-card .q-field--highlighted .q-field__control,
.login-input.q-field--focused .q-field__control,
.login-input.q-field--highlighted .q-field__control {
  background: rgba(15, 23, 42, 0.75) !important;
  border-color: #3B82F6 !important;
  box-shadow: 0 0 0 3.5px rgba(59, 130, 246, 0.3) !important;
}
.login-card .q-field__native,
.login-card .q-field__input,
.login-card input,
.login-input .q-field__native,
.login-input .q-field__input,
.login-input input {
  color: #FFFFFF !important;
  font-size: 14.5px !important;
  font-weight: 500 !important;
}
.login-card .q-field__native::placeholder,
.login-card input::placeholder,
.login-input input::placeholder {
  color: rgba(255, 255, 255, 0.4) !important;
}
.login-card .q-field__label,
.login-input .q-field__label {
  color: #94A3B8 !important;
  font-size: 13.5px !important;
  font-weight: 500 !important;
}
.login-card .q-field--focused .q-field__label,
.login-input.q-field--focused .q-field__label {
  color: #60A5FA !important;
  font-weight: 700 !important;
}
.login-card .q-field__marginal,
.login-card .q-field__marginal .q-icon,
.login-input .q-field__marginal,
.login-input .q-field__marginal .q-icon {
  color: #94A3B8 !important;
}
.login-card .q-field--focused .q-field__marginal .q-icon,
.login-input.q-field--focused .q-field__marginal .q-icon {
  color: #60A5FA !important;
}

/* ═══════════════════════════════════════════════
   DTR PREVIEW
═══════════════════════════════════════════════ */
.dtr-preview-table { width: 100%; border-collapse: collapse; font-size: 12.5px; }
.dtr-preview-table th, .dtr-preview-table td { border: 1px solid #CBD5E1; padding: 7px 10px; text-align: center; }
.dtr-preview-table th { background: #F1F5F9; font-weight: 700; font-size: 11px; text-transform: uppercase; }
.dtr-preview-table tr:hover td { background: #F8FAFC; }
@media print { .q-drawer,.q-header,.no-print { display: none !important; } .q-page-container { padding-left: 0 !important; } }

/* ═══════════════════════════════════════════════
   EMPTY STATE
═══════════════════════════════════════════════ */
.empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 60px 20px; color: var(--text-muted); text-align: center; }
.empty-state .material-icons-round { font-size: 56px; margin-bottom: 16px; opacity: .4; }
.empty-state-title { font-size: 15px; font-weight: 600; color: var(--text-secondary); }
.empty-state-desc  { font-size: 13px; color: var(--text-muted); margin-top: 4px; }

/* ═══════════════════════════════════════════════
   PAGINATION
═══════════════════════════════════════════════ */
.pagination { display: flex; align-items: center; gap: 4px; padding: 14px 16px; border-top: 1px solid var(--border); }
.page-btn { width: 34px; height: 34px; display: flex; align-items: center; justify-content: center; border-radius: var(--radius); border: 1px solid var(--border); background: var(--bg-surface); color: var(--text-secondary); font-size: 13px; font-weight: 500; cursor: pointer; transition: all var(--transition); }
.page-btn:hover  { background: var(--bg-subtle); color: var(--text-primary); }
.page-btn.active { background: var(--color-primary); border-color: var(--color-primary); color: #fff; box-shadow: 0 2px 8px rgba(37,99,235,.3); }
.page-btn:disabled { opacity: .4; cursor: not-allowed; }

/* ═══════════════════════════════════════════════
   UTILITIES
═══════════════════════════════════════════════ */
.text-primary { color: var(--color-primary) !important; }
.text-success { color: var(--color-success) !important; }
.text-danger  { color: var(--color-danger)  !important; }
.text-warning { color: var(--color-warning) !important; }
.text-muted   { color: var(--text-muted)    !important; }
.flex    { display: flex; }
.flex-1  { flex: 1; }
.items-center { align-items: center; }
.justify-between { justify-content: space-between; }
.gap-2  { gap: 8px; }
.gap-3  { gap: 12px; }
.gap-4  { gap: 16px; }
.grid-cols-2 { display: grid; grid-template-columns: repeat(2,1fr); gap: 16px; }
.grid-cols-3 { display: grid; grid-template-columns: repeat(3,1fr); gap: 16px; }
.grid-cols-4 { display: grid; grid-template-columns: repeat(4,1fr); gap: 16px; }
.mt-2 { margin-top: 8px; }
.mt-4 { margin-top: 16px; }
.mb-4 { margin-bottom: 16px; }
.w-full { width: 100%; }

/* ═══════════════════════════════════════════════
   DROPDOWN POPUP MENU (SEARCH SELECT & SELECTS)
═══════════════════════════════════════════════ */
.q-menu.q-select__menu,
.q-menu.q-position-engine {
  border-radius: 14px !important;
  border: 1px solid #E2E8F0 !important;
  box-shadow: 0 20px 35px -5px rgba(15, 23, 42, 0.16), 0 10px 15px -5px rgba(15, 23, 42, 0.06) !important;
  padding: 6px !important;
  background: #FFFFFF !important;
  max-height: 380px !important;
}
.q-menu.q-select__menu .q-virtual-scroll__content {
  padding: 4px 0 !important;
}

/* Sticky Search Header in Dropdown Popup */
.search-select-header {
  background: #FFFFFF !important;
  border-bottom: 2px solid #F1F5F9 !important;
  padding: 8px 6px 10px 6px !important;
  margin-bottom: 4px !important;
}
.search-select-header .q-field--outlined .q-field__control {
  background: #F1F5F9 !important;
  border: 1.5px solid #E2E8F0 !important;
  border-radius: 8px !important;
  height: 36px !important;
  min-height: 36px !important;
}
.search-select-header .q-field--outlined:hover .q-field__control {
  border-color: #3B82F6 !important;
  background: #FFFFFF !important;
}
.search-select-header .q-field--focused .q-field__control {
  border-color: #2563EB !important;
  background: #FFFFFF !important;
  box-shadow: 0 0 0 2.5px rgba(37, 99, 235, 0.18) !important;
}
.search-select-header .q-field__native,
.search-select-header input {
  font-size: 13px !important;
  padding: 4px 8px !important;
}
.search-select-header .q-field__marginal {
  color: #2563EB !important;
}

/* Dropdown Menu Items */
.q-menu.q-select__menu .q-item,
.q-menu .q-item {
  border-radius: 8px !important;
  margin: 2px 4px !important;
  padding: 8px 12px !important;
  font-size: 13.5px !important;
  font-weight: 500 !important;
  color: #1E293B !important;
  min-height: 36px !important;
  transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

/* Hover Item */
.q-menu.q-select__menu .q-item:hover,
.q-menu.q-select__menu .q-manual-focusable--focused,
.q-menu .q-item:hover {
  background: #EEF2FF !important;
  color: #1D4ED8 !important;
  transform: translateX(3px) !important;
  font-weight: 600 !important;
}

/* Selected / Active Item */
.q-menu.q-select__menu .q-item.q-item--active,
.q-menu.q-select__menu .q-item[aria-selected="true"],
.q-menu .q-item.q-item--active {
  background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
  color: #FFFFFF !important;
  font-weight: 700 !important;
  box-shadow: 0 3px 10px rgba(37, 99, 235, 0.35) !important;
  transform: none !important;
}
.q-menu.q-select__menu .q-item.q-item--active .q-item__label,
.q-menu .q-item.q-item--active .q-item__label {
  color: #FFFFFF !important;
}

/* Dark Mode Dropdown Menu */
body.dark-mode .q-menu.q-select__menu,
body.dark-mode .q-menu.q-position-engine,
.q-dark.q-menu {
  background: #1E293B !important;
  border-color: #334155 !important;
  box-shadow: 0 20px 35px -5px rgba(0, 0, 0, 0.5) !important;
}
body.dark-mode .search-select-header,
.q-dark .search-select-header {
  background: #1E293B !important;
  border-bottom-color: #334155 !important;
}
body.dark-mode .search-select-header .q-field--outlined .q-field__control,
.q-dark .search-select-header .q-field--outlined .q-field__control {
  background: #0F172A !important;
  border-color: #334155 !important;
}
body.dark-mode .q-menu.q-select__menu .q-item,
body.dark-mode .q-menu .q-item,
.q-dark .q-item {
  color: #F1F5F9 !important;
}
body.dark-mode .q-menu.q-select__menu .q-item:hover,
body.dark-mode .q-menu .q-item:hover,
.q-dark .q-item:hover {
  background: rgba(59, 130, 246, 0.18) !important;
  color: #60A5FA !important;
}
body.dark-mode .q-menu.q-select__menu .q-item.q-item--active,
.q-dark .q-item.q-item--active {
  background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%) !important;
  color: #FFFFFF !important;
}

/* ═══════════════════════════════════════════════
   MODERN CALENDAR PICKER (Q-DATE & POPUP)
═══════════════════════════════════════════════ */
.q-date {
  font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
  border-radius: 14px !important;
  border: 1px solid var(--border) !important;
  box-shadow: 0 16px 36px -4px rgba(15, 23, 42, 0.16), 0 8px 16px -4px rgba(15, 23, 42, 0.08) !important;
  overflow: hidden !important;
}
.q-date__header {
  background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
  color: #FFFFFF !important;
  padding: 14px 16px !important;
}
.q-date__header-title-label {
  font-size: 20px !important;
  font-weight: 700 !important;
  letter-spacing: -0.3px !important;
}
.q-date__header-subtitle {
  font-size: 12.5px !important;
  font-weight: 500 !important;
  opacity: 0.85 !important;
}
.q-date__navigation {
  padding: 6px 10px !important;
  font-weight: 600 !important;
  color: var(--text-primary) !important;
}
.q-date__navigation .q-btn {
  font-weight: 600 !important;
  border-radius: 8px !important;
}
.q-date__calendar-weekdays > div {
  font-size: 11px !important;
  font-weight: 700 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.5px !important;
  color: var(--text-muted) !important;
}
.q-date__calendar-days-container .q-date__calendar-item button {
  font-size: 12.5px !important;
  font-weight: 500 !important;
  border-radius: 8px !important;
  transition: all 0.15s ease !important;
}
.q-date__calendar-days-container .q-date__calendar-item button:hover {
  background: #EFF6FF !important;
  color: #2563EB !important;
  font-weight: 700 !important;
}
.q-date__calendar-days-container .q-date__calendar-item--selected button,
.q-date__calendar-days-container .q-date__edit-range--from button,
.q-date__calendar-days-container .q-date__edit-range--to button {
  background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
  color: #FFFFFF !important;
  font-weight: 700 !important;
  box-shadow: 0 3px 8px rgba(37, 99, 235, 0.4) !important;
}
.q-date__actions {
  padding: 8px 12px !important;
  border-top: 1px solid var(--border) !important;
  background: var(--bg-subtle) !important;
}

/* Style HTML5 date & month inputs so clicking anywhere triggers picker cleanly */
input[type="date"],
input[type="month"] {
  cursor: pointer !important;
}
input[type="date"]::-webkit-calendar-picker-indicator,
input[type="month"]::-webkit-calendar-picker-indicator {
  opacity: 0 !important;
  position: absolute !important;
  right: 0 !important;
  top: 0 !important;
  width: 100% !important;
  height: 100% !important;
  cursor: pointer !important;
}

/* Dark Mode for Calendar */
body.dark-mode .q-date {
  background: #1E293B !important;
  border-color: #334155 !important;
}
body.dark-mode .q-date__navigation {
  color: #F1F5F9 !important;
}
body.dark-mode .q-date__calendar-days-container .q-date__calendar-item button:hover {
  background: rgba(59, 130, 246, 0.2) !important;
  color: #60A5FA !important;
}
body.dark-mode .q-date__actions {
  background: #0F172A !important;
  border-top-color: #334155 !important;
}
"""

GLOBAL_JS = """
window.DTR = window.DTR || {};

DTR.showToast = function(type, title, message, duration) {
  duration = duration || 4000;
  var container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }
  var icons = { success: 'check_circle', error: 'error', warning: 'warning', info: 'info' };
  var toast = document.createElement('div');
  toast.className = 'toast toast-' + type;
  toast.innerHTML =
    '<div class="toast-icon"><span class="material-icons-round">' + (icons[type]||'info') + '</span></div>' +
    '<div class="toast-content">' +
      '<div class="toast-title">' + title + '</div>' +
      (message ? '<div class="toast-message">' + message + '</div>' : '') +
    '</div>' +
    '<button onclick="this.parentElement.remove()" style="background:none;border:none;cursor:pointer;color:var(--text-muted);font-size:20px;padding:0 0 0 8px;line-height:1;flex-shrink:0;">&times;</button>' +
    '<div class="toast-progress" style="animation-duration:' + duration + 'ms;"></div>';
  container.appendChild(toast);
  setTimeout(function() {
    toast.classList.add('hiding');
    setTimeout(function() { toast.remove(); }, 300);
  }, duration);
};

DTR.animateCounter = function(el, target, duration) {
  if (!el) return;
  duration = duration || 1200;
  el._startTime = null;
  var step = function(timestamp) {
    if (!el._startTime) el._startTime = timestamp;
    var progress = Math.min((timestamp - el._startTime) / duration, 1);
    var eased = 1 - Math.pow(1 - progress, 3);
    el.textContent = Math.floor(eased * target).toLocaleString();
    if (progress < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
};

DTR.toggleDarkMode = function() {
  document.body.classList.toggle('dark-mode');
  localStorage.setItem('dtr_dark', document.body.classList.contains('dark-mode') ? '1' : '');
};

if (localStorage.getItem('dtr_dark')) {
  document.body.classList.add('dark-mode');
}

DTR.startClock = function(el) {
  if (!el) return;
  var update = function() {
    el.textContent = new Date().toLocaleTimeString('en-PH', {hour12:true, hour:'2-digit', minute:'2-digit', second:'2-digit'});
  };
  update();
  setInterval(update, 1000);
};

// Global click handler to open native date/month picker when clicking input field
document.addEventListener("click", function(e) {
  var qField = e.target.closest('.q-field');
  if (qField && !e.target.closest('.q-field__append .q-icon[name="cancel"], .q-field__append .q-field__focusable-action')) {
    var dateInput = qField.querySelector('input[type="date"], input[type="month"]');
    if (dateInput && typeof dateInput.showPicker === 'function') {
      try { dateInput.showPicker(); } catch (err) {}
    }
  }
});
"""
