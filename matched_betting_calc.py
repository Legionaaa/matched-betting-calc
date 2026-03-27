from __future__ import annotations

import json
import platform
from pathlib import Path

try:
    from nicegui import app, native, ui
except ModuleNotFoundError as exc:
    missing_name = exc.name or "dependency"
    raise SystemExit(
        f"Missing dependency '{missing_name}'. Install with: python -m pip install -r requirements.txt"
    ) from exc

from matched_betting_core import (
    FREE_BET_SNR,
    MONEY_BACK_IF_STAKE_LOSES,
    QUALIFIER,
    calculate_matched_bet,
    format_currency,
)


ACCENT = "#186241"
ACCENT_DARK = "#124a31"
ACCENT_TINT = "#eaf5ee"
ACCENT_TINT_STRONG = "#dfeee4"
TEXT = "#173329"
MUTED = "#647a6e"
WIN = "#15754b"
LOSS = "#b45448"
UNDERLAY = "#b68634"
SETTINGS_PATH = Path.home() / ".matched_betting_calc_settings.json"

BET_TYPE_OPTIONS = {
    QUALIFIER: "Qualifier",
    FREE_BET_SNR: "SNR",
    MONEY_BACK_IF_STAKE_LOSES: "Money Back",
}

HELP_BY_TYPE = {
    QUALIFIER: "Standard qualifying bet using your own stake.",
    FREE_BET_SNR: "Free bet with stake not returned.",
    MONEY_BACK_IF_STAKE_LOSES: "Cashback if your back bet loses.",
}


def resource_path(relative_path: str) -> Path:
    return Path(__file__).resolve().parent / relative_path


def load_theme_preference() -> bool:
    try:
        data = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return False
    return bool(data.get("dark_mode", False))


def save_theme_preference(enabled: bool) -> None:
    try:
        SETTINGS_PATH.write_text(
            json.dumps({"dark_mode": bool(enabled)}, indent=2),
            encoding="utf-8",
        )
    except OSError:
        pass


app.add_static_files("/images", str(resource_path("images")))

HEAD_HTML = f"""
    <style>
      :root {{
        --brand: {ACCENT};
        --brand-dark: {ACCENT_DARK};
        --brand-tint: {ACCENT_TINT};
        --brand-tint-strong: {ACCENT_TINT_STRONG};
        --text-main: {TEXT};
        --text-muted: {MUTED};
        --win: {WIN};
        --loss: {LOSS};
        --underlay: {UNDERLAY};
        --panel-bg: rgba(255, 255, 255, 0.94);
        --panel-shadow: 0 12px 34px rgba(24, 98, 65, 0.08);
        --field-bg: var(--brand-tint);
        --table-alt-bg: #ffffff;
        --toggle-bg: #e4efe8;
        --toggle-off-bg: transparent;
        --toggle-off-text: var(--brand-dark);
        --toggle-on-bg: var(--brand);
        --toggle-on-text: #ffffff;
      }}
      html, body {{
        background:
          radial-gradient(circle at top, rgba(24, 98, 65, 0.12), transparent 34%),
          linear-gradient(180deg, #f6fbf8 0%, #ffffff 62%);
      }}
      body {{
        color: var(--text-main);
      }}
      body.body--dark {{
        --brand-tint: #173428;
        --brand-tint-strong: #1d4533;
        --text-main: #edf5f1;
        --text-muted: #a8beb4;
        --win: #52c28a;
        --loss: #e18275;
        --underlay: #d7ab58;
        --panel-bg: rgba(18, 28, 23, 0.96);
        --panel-shadow: 0 18px 40px rgba(0, 0, 0, 0.34);
        --field-bg: #173428;
        --table-alt-bg: #16241d;
        --toggle-bg: #13261d;
        --toggle-off-bg: transparent;
        --toggle-off-text: #b9cec4;
        --toggle-on-bg: #2f8c53;
        --toggle-on-text: #ffffff;
        background:
          radial-gradient(circle at top, rgba(24, 98, 65, 0.28), transparent 34%),
          linear-gradient(180deg, #0d1511 0%, #121d17 64%);
      }}
      .nicegui-content {{
        display: block;
        padding: 0 !important;
      }}
      .app-shell {{
        width: 100%;
        max-width: 410px;
        margin: 0 auto;
        padding: 14px 14px 24px;
        box-sizing: border-box;
      }}
      .topbar {{
        display: grid;
        grid-template-columns: minmax(0, 1fr) auto;
        align-items: flex-start;
        width: 100%;
        box-sizing: border-box;
        padding: 0 15px;
        gap: 12px;
        margin-bottom: 6px;
      }}
      .topbar-main {{
        min-width: 0;
        display: flex;
        align-items: center;
        gap: 10px;
      }}
      .topbar-logo {{
        width: 36px;
        height: 36px;
        border-radius: 12px;
        box-shadow: 0 8px 20px rgba(24, 98, 65, 0.10);
      }}
      .topbar-title {{
        font-size: 1.14rem;
        line-height: 1.05;
        font-weight: 900;
        letter-spacing: -0.02em;
        color: var(--text-main);
      }}
      .topbar-subtitle {{
        margin-top: 2px;
        font-size: 0.74rem;
        color: var(--text-muted);
      }}
      .theme-toggle {{
        display: flex;
        align-items: center;
        justify-content: flex-end;
        justify-self: end;
        align-self: start;
        gap: 5px;
        margin-top: 2px;
        white-space: nowrap;
      }}
      .theme-toggle-label {{
        font-size: 0.68rem;
        font-weight: 800;
        color: var(--text-muted);
      }}
      .theme-switch {{
        margin: 0;
      }}
      .theme-switch .q-toggle__track {{
        opacity: 0.24;
      }}
      .theme-switch .q-toggle__inner--truthy .q-toggle__track {{
        opacity: 0.5;
      }}
      .panel {{
        width: 100%;
        background: var(--panel-bg);
        border-radius: 22px;
        padding: 15px;
        box-sizing: border-box;
        box-shadow: var(--panel-shadow);
        backdrop-filter: blur(10px);
        margin-bottom: 12px;
      }}
      .panel-title {{
        font-size: 0.82rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--brand);
      }}
      .panel-copy {{
        margin-top: 5px;
        font-size: 0.79rem;
        line-height: 1.35;
        color: var(--text-muted);
      }}
      .pro-expansion {{
        width: 100%;
      }}
      .pro-expansion .q-expansion-item__container {{
        background: transparent;
      }}
      .pro-expansion .q-item {{
        padding: 0;
        min-height: auto;
      }}
      .pro-expansion .q-item__label {{
        font-size: 0.82rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--brand);
      }}
      .pro-expansion .q-item__label--caption {{
        margin-top: 4px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: none;
        letter-spacing: 0;
        color: var(--text-muted);
      }}
      .pro-expansion .q-item__section--side .q-icon {{
        color: var(--brand);
      }}
      .pro-expansion .q-expansion-item__content {{
        padding-top: 10px;
      }}
      .mode-toggle {{
        width: 100%;
        margin-top: 10px;
      }}
      .mode-toggle .q-btn-group {{
        width: 100%;
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 0;
        padding: 4px;
        background: var(--toggle-bg);
        border-radius: 16px;
        box-shadow: inset 0 0 0 1px rgba(24, 98, 65, 0.08);
        overflow: hidden;
      }}
      .mode-toggle .q-btn {{
        min-height: 36px;
        border-radius: 12px !important;
        font-weight: 800;
        font-size: 0.76rem;
        letter-spacing: 0;
        box-shadow: none !important;
        background: var(--toggle-off-bg) !important;
        color: var(--toggle-off-text) !important;
      }}
      .mode-toggle .q-btn:not(:last-child) {{
        border-right: 1px solid rgba(24, 98, 65, 0.10);
      }}
      .mode-toggle .q-btn.q-btn--active {{
        background: var(--toggle-on-bg) !important;
        color: var(--toggle-on-text) !important;
      }}
      .mode-toggle .q-focus-helper {{
        display: none;
      }}
      .section-space {{
        margin-top: 12px;
      }}
      .field-grid {{
        width: 100%;
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 8px;
      }}
      .field-grid-three {{
        grid-template-columns: repeat(3, minmax(0, 1fr));
      }}
      .full-span {{
        grid-column: 1 / -1;
      }}
      .field-label {{
        margin-bottom: 5px;
        font-size: 0.74rem;
        font-weight: 800;
        color: var(--text-main);
      }}
      .app-input {{
        width: 100%;
      }}
      .app-input .q-field__control {{
        min-height: 42px !important;
        border-radius: 14px !important;
        background: var(--field-bg);
        box-shadow: inset 0 0 0 1px rgba(24, 98, 65, 0.08);
        padding: 0 7px;
      }}
      .app-input .q-field__native,
      .app-input .q-field__input {{
        font-size: 0.93rem !important;
        font-weight: 700;
        color: var(--text-main) !important;
      }}
      .app-input .q-field__append,
      .app-input .q-field__prepend,
      .app-input .q-field__label {{
        color: var(--text-muted) !important;
      }}
      .app-input .q-field__bottom {{
        display: none;
      }}
      .pill-row {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 10px;
      }}
      .adjustment-pill {{
        padding: 7px 12px;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 800;
        background: var(--brand-tint);
        color: var(--brand);
        white-space: nowrap;
      }}
      .app-slider {{
        width: 100%;
        margin-top: 12px;
      }}
      .app-slider .q-slider__track-container {{
        color: var(--brand);
      }}
      .app-slider .q-slider__track {{
        background: linear-gradient(90deg, rgba(182,134,52,0.85) 0%, rgba(24,98,65,0.2) 48%, rgba(24,98,65,1) 100%);
      }}
      .app-slider .q-slider__track-markers {{
        display: none;
      }}
      .adjustment-scale {{
        display: flex;
        justify-content: space-between;
        gap: 10px;
        margin-top: 8px;
        font-size: 0.77rem;
        font-weight: 800;
      }}
      .underlay-text {{
        color: var(--underlay);
      }}
      .overlay-text {{
        color: var(--brand);
      }}
      .tiny-copy {{
        margin-top: 10px;
        font-size: 0.79rem;
        color: var(--text-muted);
        line-height: 1.35;
      }}
      .reset-button {{
        min-height: 34px;
        border-radius: 12px !important;
        font-weight: 800;
      }}
      .result-hero {{
        margin-top: 8px;
      }}
      .result-row {{
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 12px;
      }}
      .result-value {{
        font-size: 1.72rem;
        line-height: 0.98;
        font-weight: 900;
        letter-spacing: -0.03em;
        color: var(--text-main);
      }}
      .result-caption {{
        margin-top: 5px;
        font-size: 0.78rem;
        color: var(--text-muted);
      }}
      .copy-button {{
        min-width: 40px;
        min-height: 40px;
        border-radius: 12px !important;
        flex-shrink: 0;
        background: var(--brand-dark) !important;
        color: white !important;
      }}
      .copy-button:hover {{
        background: var(--brand) !important;
      }}
      .stat-card {{
        background: var(--brand-tint);
        border-radius: 18px;
        padding: 12px;
        margin-top: 12px;
      }}
      .stat-card.strong {{
        background: var(--brand);
      }}
      .stat-title {{
        font-size: 0.76rem;
        font-weight: 800;
        color: var(--text-muted);
      }}
      .stat-card.strong .stat-title {{
        color: rgba(255,255,255,0.75);
      }}
      .stat-value {{
        margin-top: 6px;
        font-size: 1.18rem;
        line-height: 1;
        font-weight: 900;
        letter-spacing: -0.02em;
        color: var(--text-main);
      }}
      .stat-card.strong .stat-value {{
        color: white;
      }}
      .results-table {{
        margin-top: 14px;
      }}
      .profit-line {{
        margin-top: 12px;
        font-size: 0.96rem;
        font-weight: 800;
        color: var(--brand-dark);
        text-align: center;
      }}
      .profit-line.win {{
        color: var(--win);
      }}
      .profit-line.loss {{
        color: var(--loss);
      }}
      .table-head,
      .table-row {{
        display: grid;
        grid-template-columns: 1.55fr 0.95fr 0.95fr 0.8fr;
        gap: 8px;
        align-items: center;
      }}
      .table-head.cashback,
      .table-row.cashback {{
        grid-template-columns: 1.25fr 0.85fr 0.85fr 0.85fr 0.8fr;
      }}
      .table-head {{
        padding: 11px 12px;
        border-radius: 15px;
        background: var(--brand-dark);
        color: white;
        font-size: 0.7rem;
        font-weight: 800;
      }}
      .table-row {{
        margin-top: 8px;
        padding: 11px 12px;
        border-radius: 15px;
        background: var(--brand-tint);
        font-size: 0.76rem;
      }}
      .table-row.alt {{
        background: var(--table-alt-bg);
        box-shadow: inset 0 0 0 1px rgba(24, 98, 65, 0.08);
      }}
      .right {{
        text-align: right;
      }}
      .win {{
        color: var(--win);
        font-weight: 800;
      }}
      .loss {{
        color: var(--loss);
        font-weight: 800;
      }}
      .muted {{
        color: var(--text-muted);
      }}
      .status-line {{
        margin-top: 10px;
        font-size: 0.79rem;
        color: var(--text-muted);
        text-align: center;
      }}
      .footer-line {{
        margin-top: 2px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        color: var(--text-muted);
        text-align: center;
      }}
    </style>
    """


def parse_number(raw_value: str, label: str) -> float:
    try:
        return float(raw_value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be a number.") from exc


def outcome_class(value: float) -> str:
    if value > 0.005:
        return "win"
    if value < -0.005:
        return "loss"
    return "muted"


def adjustment_copy(adjustment: float) -> tuple[str, str, str]:
    if abs(adjustment) < 0.05:
        return "", ACCENT_TINT, ACCENT
    if adjustment < 0:
        return f"Underlay {abs(adjustment):.1f}%", "#f4ead6", UNDERLAY
    return f"Overlay {adjustment:.1f}%", ACCENT_TINT, ACCENT


def stat_card_html(title: str, value: str, *, strong: bool = False, full: bool = False) -> str:
    classes = ["stat-card"]
    if strong:
        classes.append("strong")
    if full:
        classes.append("full")
    joined = " ".join(classes)
    return (
        f'<div class="{joined}"><div class="stat-title">{title}</div>'
        f'<div class="stat-value">{value}</div></div>'
    )


def row_html(
    outcome: str,
    bookmaker: float | None,
    exchange: float | None,
    cashback: float | None,
    total: float | None,
    *,
    alt: bool,
    show_cashback: bool,
) -> str:
    row_class = "table-row alt" if alt else "table-row"
    if show_cashback:
        row_class += " cashback"

    if bookmaker is None or exchange is None or total is None:
        if show_cashback:
            return (
                f'<div class="{row_class}"><div>{outcome}</div><div class="right muted">-</div>'
                '<div class="right muted">-</div><div class="right muted">-</div>'
                '<div class="right muted">-</div></div>'
            )
        return (
            f'<div class="{row_class}"><div>{outcome}</div><div class="right muted">-</div>'
            '<div class="right muted">-</div><div class="right muted">-</div></div>'
        )

    if show_cashback:
        cashback_value = 0.0 if cashback is None else cashback
        return (
            f'<div class="{row_class}"><div>{outcome}</div>'
            f'<div class="right {outcome_class(bookmaker)}">{format_currency(bookmaker)}</div>'
            f'<div class="right {outcome_class(exchange)}">{format_currency(exchange)}</div>'
            f'<div class="right {outcome_class(cashback_value)}">{format_currency(cashback_value)}</div>'
            f'<div class="right {outcome_class(total)}">{format_currency(total)}</div></div>'
        )

    return (
        f'<div class="{row_class}"><div>{outcome}</div>'
        f'<div class="right {outcome_class(bookmaker)}">{format_currency(bookmaker)}</div>'
        f'<div class="right {outcome_class(exchange)}">{format_currency(exchange)}</div>'
        f'<div class="right {outcome_class(total)}">{format_currency(total)}</div></div>'
    )


@ui.page("/")
def index() -> None:
    ui.colors(primary=ACCENT, positive=WIN, secondary=ACCENT_TINT_STRONG)
    ui.add_head_html(HEAD_HTML)
    theme_enabled = load_theme_preference()
    dark_mode = ui.dark_mode(theme_enabled)

    state = {
        "bet_type": QUALIFIER,
        "stake": "",
        "back_odds": "",
        "lay_odds": "",
        "cashback": "",
        "back_commission": "0",
        "lay_commission": "0",
        "adjustment": 0.0,
        "copy_lay_stake": "",
    }

    with ui.column().classes("app-shell gap-0"):
        with ui.element("header").classes("topbar"):
            with ui.element("div").classes("topbar-main"):
                ui.image("/images/logo.png").classes("topbar-logo")
                with ui.column().classes("gap-0"):
                    ui.label("Matched Betting Calculator").classes("topbar-title")
                    ui.label("A PenarthLan App").classes("topbar-subtitle")
            with ui.element("div").classes("theme-toggle"):
                ui.label("Dark").classes("theme-toggle-label")
                theme_switch = (
                    ui.switch(value=theme_enabled)
                    .props("dense color=green-8 keep-color")
                    .classes("theme-switch")
                )

        with ui.element("section").classes("panel"):
            ui.label("Bet Type").classes("panel-title")

            bet_type_toggle = ui.toggle(BET_TYPE_OPTIONS, value=state["bet_type"]).classes(
                "mode-toggle"
            ).props("unelevated no-caps rounded")

            bet_type_hint = ui.label(HELP_BY_TYPE[state["bet_type"]]).classes("panel-copy")

            with ui.element("div").classes("field-grid field-grid-three section-space"):
                with ui.column().classes("gap-0"):
                    ui.label("Stake").classes("field-label")
                    stake_input = (
                        ui.input(value=state["stake"])
                        .props("type=number step=0.01 borderless dense inputmode=decimal")
                        .classes("app-input")
                    )

                with ui.column().classes("gap-0"):
                    ui.label("Back odds").classes("field-label")
                    back_odds_input = (
                        ui.input(value=state["back_odds"])
                        .props("type=number step=0.01 borderless dense inputmode=decimal")
                        .classes("app-input")
                    )

                with ui.column().classes("gap-0"):
                    ui.label("Lay odds").classes("field-label")
                    lay_odds_input = (
                        ui.input(value=state["lay_odds"])
                        .props("type=number step=0.01 borderless dense inputmode=decimal")
                        .classes("app-input")
                    )

            with ui.element("div").classes("field-grid q-mt-sm"):
                cashback_row = ui.column().classes("full-span gap-0")
                with cashback_row:
                    ui.label("Cashback").classes("field-label")
                    cashback_input = (
                        ui.input(value=state["cashback"])
                        .props("type=number step=0.01 borderless dense inputmode=decimal")
                        .classes("app-input")
                    )

            with ui.element("div").classes("field-grid q-mt-sm"):
                with ui.column().classes("gap-0"):
                    ui.label("Back commission").classes("field-label")
                    back_commission_input = (
                        ui.input(value=state["back_commission"])
                        .props("type=number step=0.01 borderless dense suffix=% inputmode=decimal")
                        .classes("app-input")
                    )

                with ui.column().classes("gap-0"):
                    ui.label("Lay commission").classes("field-label")
                    lay_commission_input = (
                        ui.input(value=state["lay_commission"])
                        .props("type=number step=0.01 borderless dense suffix=% inputmode=decimal")
                        .classes("app-input")
                    )

        with ui.element("section").classes("panel"):
            with ui.expansion(
                "Underlay / Overlay",
                caption="(Advanced)",
                icon="tune",
                value=False,
            ).classes("pro-expansion"):
                with ui.element("div").classes("pill-row"):
                    ui.label("Drag left to underlay or right to overlay.").classes("panel-copy")
                    adjustment_badge = ui.html("")

                adjustment_slider = ui.slider(min=-50, max=50, value=0, step=0.5).classes(
                    "app-slider"
                ).props("color=green-8 track-color=green-2 thumb-color=green-8")

                ui.html(
                    '<div class="adjustment-scale"><span class="underlay-text">-50% Underlay</span>'
                    '<span class="muted">Matched</span>'
                    '<span class="overlay-text">+50% Overlay</span></div>'
                )

                with ui.row().classes("w-full items-center justify-between q-mt-sm"):
                    ui.label("Negative lowers the lay stake. Positive increases it.").classes(
                        "tiny-copy"
                    )
                    reset_button = (
                        ui.button("Reset")
                        .props("unelevated no-caps color=green-8")
                        .classes("reset-button")
                    )

        with ui.element("section").classes("panel"):
            ui.label("Results").classes("panel-title")

            with ui.element("div").classes("result-hero"):
                with ui.element("div").classes("result-row"):
                    with ui.column().classes("gap-0"):
                        summary_label = ui.label("Lay £0.00").classes("result-value")
                        summary_caption = ui.label("Matched lay stake").classes("result-caption")
                    copy_button = (
                        ui.button(icon="content_copy")
                        .props("unelevated round")
                        .classes("copy-button")
                    )
                ui.tooltip("Copy lay stake")

            liability_card = ui.html(stat_card_html("Lay liability", "£0.00"))

            current_adjustment = ui.label("").classes("panel-copy q-mt-sm")

            with ui.element("div").classes("results-table"):
                table_head = ui.html("")
                back_row = ui.html("")
                lay_row = ui.html("")

            profit_label = ui.label("").classes("profit-line")
            status_label = ui.label("").classes("status-line")

        ui.label("Version 1.0").classes("footer-line")

    def update_adjustment_ui() -> None:
        text, bg, fg = adjustment_copy(float(state["adjustment"]))
        if text:
            adjustment_badge.set_content(
                f'<span class="adjustment-pill" style="background:{bg};color:{fg};">{text}</span>'
            )
        else:
            adjustment_badge.set_content("")
        current_adjustment.set_text(text)
        current_adjustment.set_visibility(bool(text))

        if abs(float(state["adjustment"])) < 0.05:
            adjustment_slider.props("color=green-8 track-color=green-2 thumb-color=green-8")
        elif float(state["adjustment"]) < 0:
            adjustment_slider.props(
                "color=amber-7 track-color=green-2 thumb-color=amber-7"
            )
        else:
            adjustment_slider.props("color=green-8 track-color=green-2 thumb-color=green-8")
        adjustment_slider.update()

    def update_cashback_ui() -> None:
        is_cashback_mode = state["bet_type"] == MONEY_BACK_IF_STAKE_LOSES
        cashback_row.set_visibility(is_cashback_mode)

    def update_table_head() -> None:
        if state["bet_type"] == MONEY_BACK_IF_STAKE_LOSES:
            table_head.set_content(
                '<div class="table-head cashback"><div>Outcome</div>'
                '<div class="right">Bookmaker</div><div class="right">Exchange</div>'
                '<div class="right">Cashback</div><div class="right">Total</div></div>'
            )
        else:
            table_head.set_content(
                '<div class="table-head"><div>Outcome</div><div class="right">Bookmaker</div>'
                '<div class="right">Exchange</div><div class="right">Total</div></div>'
            )

    def reset_results(message: str) -> None:
        state["copy_lay_stake"] = ""
        summary_label.set_text("Lay £0.00")
        summary_caption.set_text("Awaiting betting values")
        liability_card.set_content(stat_card_html("Lay liability", "£0.00"))
        update_table_head()
        show_cashback = state["bet_type"] == MONEY_BACK_IF_STAKE_LOSES
        back_row.set_content(
            row_html("If bookmaker (back) bet wins", None, None, None, None, alt=True, show_cashback=show_cashback)
        )
        lay_row.set_content(
            row_html("If exchange (lay) bet wins", None, None, None, None, alt=False, show_cashback=show_cashback)
        )
        profit_label.set_text("")
        profit_label.classes(remove="win loss")
        copy_button.disable()
        status_label.set_text("-" if message else "")
        status_label.set_visibility(bool(message))

    def update_results() -> None:
        try:
            result = calculate_matched_bet(
                back_stake=parse_number(state["stake"], "Stake"),
                back_odds=parse_number(state["back_odds"], "Back odds"),
                lay_odds=parse_number(state["lay_odds"], "Lay odds"),
                back_commission_percentage=parse_number(
                    state["back_commission"], "Back commission"
                ),
                lay_commission_percentage=parse_number(
                    state["lay_commission"], "Lay commission"
                ),
                bet_type=state["bet_type"],
                adjustment_percentage=float(state["adjustment"]),
                cashback_amount=parse_number(state["cashback"], "Cashback")
                if state["bet_type"] == MONEY_BACK_IF_STAKE_LOSES
                else 0.0,
            )
        except ValueError as exc:
            reset_results(str(exc))
            return

        adjustment = float(state["adjustment"])
        show_cashback = state["bet_type"] == MONEY_BACK_IF_STAKE_LOSES
        update_table_head()
        summary_label.set_text(f"Lay {format_currency(result.placed_lay_stake)}")
        if abs(adjustment) < 0.05:
            summary_caption.set_text("Lay stake to place")
        else:
            summary_caption.set_text("Adjusted lay stake to place")
        state["copy_lay_stake"] = f"{result.placed_lay_stake:.2f}"

        liability_card.set_content(
            stat_card_html("Lay liability", format_currency(result.lay_liability))
        )
        back_row.set_content(
            row_html(
                "If bookmaker (back) bet wins",
                result.bookmaker_if_back_wins,
                result.exchange_if_back_wins,
                result.cashback_if_back_wins,
                result.total_if_back_wins,
                alt=True,
                show_cashback=show_cashback,
            )
        )
        lay_row.set_content(
            row_html(
                "If exchange (lay) bet wins",
                result.bookmaker_if_lay_wins,
                result.exchange_if_lay_wins,
                result.cashback_if_lay_wins,
                result.total_if_lay_wins,
                alt=False,
                show_cashback=show_cashback,
            )
        )
        if abs(adjustment) < 0.05:
            profit_label.set_text(f"Total profit {format_currency(result.profit_floor)}")
            profit_label.classes(remove="win loss")
            profit_label.classes(add="win" if result.profit_floor > 0.005 else "loss" if result.profit_floor < -0.005 else "")
        else:
            profit_label.set_text("")
            profit_label.classes(remove="win loss")
        copy_button.enable()
        status_label.set_text("")
        status_label.set_visibility(False)

    def copy_lay_stake() -> None:
        if not state["copy_lay_stake"]:
            ui.notify("Enter valid values first.", color="negative")
            return
        ui.clipboard.write(state["copy_lay_stake"])
        ui.notify(f'Copied lay stake {state["copy_lay_stake"]}', color="positive")

    def set_theme(enabled: bool) -> None:
        if enabled:
            dark_mode.enable()
        else:
            dark_mode.disable()
        save_theme_preference(enabled)

    def refresh() -> None:
        bet_type_hint.set_text(HELP_BY_TYPE[state["bet_type"]])
        update_cashback_ui()
        update_adjustment_ui()
        update_results()

    bet_type_toggle.on_value_change(lambda e: state.update(bet_type=e.value))
    bet_type_toggle.on_value_change(lambda _e: refresh())

    def bind_input(control, key: str) -> None:
        control.on_value_change(lambda e, field=key: state.update({field: str(e.value)}))
        control.on_value_change(lambda _e: refresh())

    bind_input(stake_input, "stake")
    bind_input(back_odds_input, "back_odds")
    bind_input(lay_odds_input, "lay_odds")
    bind_input(cashback_input, "cashback")
    bind_input(back_commission_input, "back_commission")
    bind_input(lay_commission_input, "lay_commission")

    adjustment_slider.on_value_change(lambda e: state.update(adjustment=float(e.value)))
    adjustment_slider.on_value_change(lambda _e: refresh())
    reset_button.on_click(lambda: adjustment_slider.set_value(0))
    copy_button.on_click(copy_lay_stake)
    theme_switch.on_value_change(lambda e: set_theme(bool(e.value)))

    refresh()


def main() -> None:
    is_windows = platform.system() == "Windows"

    ui.run(
        title="Matched Betting Calculator",
        favicon=resource_path("images/logo.ico"),
        viewport="width=device-width, initial-scale=1, maximum-scale=1",
        dark=False,
        show=False,
        native=is_windows,
        window_size=(430, 1020) if is_windows else None,
        reload=False,
        host="127.0.0.1",
        port=native.find_open_port() if is_windows else 8080,
    )


if __name__ in {"__main__", "__mp_main__"}:
    main()
