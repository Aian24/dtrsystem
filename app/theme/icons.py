"""
Material Icons Round — Named constants for all icons used in the app.
Usage: from app.theme.icons import IC
       ui.html(f'<span class="material-icons-round">{IC.DASHBOARD}</span>')
"""


class IC:
    # Navigation
    DASHBOARD    = "dashboard"
    EMPLOYEES    = "people"
    COMPANIES    = "business"
    UPLOAD       = "upload_file"
    LOOKUP       = "manage_search"
    REPORTS      = "assessment"
    SETTINGS     = "settings"
    LOGOUT       = "logout"

    # Actions
    ADD          = "add"
    EDIT         = "edit"
    DELETE       = "delete"
    SAVE         = "save"
    CANCEL       = "close"
    SEARCH       = "search"
    FILTER       = "filter_list"
    REFRESH      = "refresh"
    DOWNLOAD     = "download"
    PRINT        = "print"
    EXPORT_PDF   = "picture_as_pdf"
    EXPORT_EXCEL = "table_view"
    BACK         = "arrow_back"
    NEXT         = "arrow_forward"
    EXPAND       = "expand_more"
    COLLAPSE     = "expand_less"
    MENU         = "menu"

    # Status
    CHECK        = "check_circle"
    ERROR        = "error"
    WARNING      = "warning"
    INFO         = "info"
    PENDING      = "pending"

    # DTR Specific
    ATTENDANCE   = "event_available"
    ABSENT       = "event_busy"
    LATE         = "schedule"
    CLOCK_IN     = "login"
    CLOCK_OUT    = "logout"
    CALENDAR     = "calendar_month"
    DATE_RANGE   = "date_range"
    LOG_FILE     = "description"
    CHART_BAR    = "bar_chart"
    CHART_LINE   = "show_chart"
    TREND_UP     = "trending_up"
    TREND_DOWN   = "trending_down"

    # UI
    SUN          = "light_mode"
    MOON         = "dark_mode"
    DRAG_DROP    = "cloud_upload"
    LOCK         = "lock"
    USER         = "person"
    BADGE        = "badge"
    BUILDING     = "corporate_fare"
    VISIBLE      = "visibility"
    HIDDEN       = "visibility_off"
