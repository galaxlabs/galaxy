BUTTON_VARIANTS = {
    "solid": {
        "primary":   "galaxy-btn-solid galaxy-btn-primary",
        "neutral":   "galaxy-btn-solid galaxy-btn-neutral",
        "success":   "galaxy-btn-solid galaxy-btn-success",
        "warning":   "galaxy-btn-solid galaxy-btn-warning",
        "danger":    "galaxy-btn-solid galaxy-btn-danger",
        "info":      "galaxy-btn-solid galaxy-btn-info",
    },
    "outline": {
        "primary":   "galaxy-btn-outline galaxy-btn-primary",
        "neutral":   "galaxy-btn-outline galaxy-btn-neutral",
        "success":   "galaxy-btn-outline galaxy-btn-success",
        "warning":   "galaxy-btn-outline galaxy-btn-warning",
        "danger":    "galaxy-btn-outline galaxy-btn-danger",
        "info":      "galaxy-btn-outline galaxy-btn-info",
    },
    "ghost": {
        "primary":   "galaxy-btn-ghost galaxy-btn-primary",
        "neutral":   "galaxy-btn-ghost galaxy-btn-neutral",
        "success":   "galaxy-btn-ghost galaxy-btn-success",
        "warning":   "galaxy-btn-ghost galaxy-btn-warning",
        "danger":    "galaxy-btn-ghost galaxy-btn-danger",
        "info":      "galaxy-btn-ghost galaxy-btn-info",
    },
    "soft": {
        "primary":   "galaxy-btn-soft galaxy-btn-primary",
        "neutral":   "galaxy-btn-soft galaxy-btn-neutral",
        "success":   "galaxy-btn-soft galaxy-btn-success",
        "warning":   "galaxy-btn-soft galaxy-btn-warning",
        "danger":    "galaxy-btn-soft galaxy-btn-danger",
        "info":      "galaxy-btn-soft galaxy-btn-info",
    },
    "destructive": {
        "primary":   "galaxy-btn-solid galaxy-btn-danger",
        "danger":    "galaxy-btn-solid galaxy-btn-danger",
    },
    "link": {
        "primary":   "galaxy-btn-link galaxy-btn-primary",
        "neutral":   "galaxy-btn-link galaxy-btn-neutral",
        "danger":    "galaxy-btn-link galaxy-btn-danger",
    },
}

BUTTON_SIZES = {
    "xs": "galaxy-btn-xs",
    "sm": "galaxy-btn-sm",
    "md": "galaxy-btn-md",
    "lg": "galaxy-btn-lg",
    "xl": "galaxy-btn-xl",
}

BADGE_VARIANTS = {
    "solid": {
        "primary": "galaxy-badge-solid galaxy-badge-primary",
        "neutral": "galaxy-badge-solid galaxy-badge-neutral",
        "success": "galaxy-badge-solid galaxy-badge-success",
        "warning": "galaxy-badge-solid galaxy-badge-warning",
        "danger":  "galaxy-badge-solid galaxy-badge-danger",
        "info":    "galaxy-badge-solid galaxy-badge-info",
    },
    "soft": {
        "primary": "galaxy-badge-soft galaxy-badge-primary",
        "neutral": "galaxy-badge-soft galaxy-badge-neutral",
        "success": "galaxy-badge-soft galaxy-badge-success",
        "warning": "galaxy-badge-soft galaxy-badge-warning",
        "danger":  "galaxy-badge-soft galaxy-badge-danger",
        "info":    "galaxy-badge-soft galaxy-badge-info",
    },
    "outline": {
        "primary": "galaxy-badge-outline galaxy-badge-primary",
        "neutral": "galaxy-badge-outline galaxy-badge-neutral",
        "success": "galaxy-badge-outline galaxy-badge-success",
        "warning": "galaxy-badge-outline galaxy-badge-warning",
        "danger":  "galaxy-badge-outline galaxy-badge-danger",
        "info":    "galaxy-badge-outline galaxy-badge-info",
    },
}

CARD_VARIANTS = {
    "bordered":    "galaxy-card-bordered",
    "elevated":    "galaxy-card-elevated",
    "flat":        "galaxy-card-flat",
    "interactive": "galaxy-card-interactive",
}

ALERT_VARIANTS = {
    "info":    "galaxy-alert-info",
    "success": "galaxy-alert-success",
    "warning": "galaxy-alert-warning",
    "danger":  "galaxy-alert-danger",
    "neutral": "galaxy-alert-neutral",
}

def resolve(cls_map, variant, tone):
    return cls_map.get(variant, {}).get(tone, "")

def resolve_size(cls_map, size):
    return cls_map.get(size, "")
