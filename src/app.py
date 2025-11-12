import dash
from dash import html, dcc, Input, Output, State, callback
import os
from dotenv import load_dotenv
from agents.classifier import ClassifierAgent
from agents.drafter import DrafterAgent
from agents.refiner import RefinerAgent
from utils.email_reader import load_emails
from utils.logger import get_logger

load_dotenv()
logger = get_logger(__name__)

# Initialize agents
classifier = ClassifierAgent()
drafter = DrafterAgent()
refiner = RefinerAgent()

# Global cache
emails_cache = []

def update_emails_cache():
    global emails_cache
    emails_cache = load_emails(use_live=True)
    if not emails_cache:
        logger.warning("No live emails; falling back to sample")
        emails_cache = load_emails(use_live=False)

# Initial load
update_emails_cache()

app = dash.Dash(__name__, title="AI Email Responder")
app.config.suppress_callback_exceptions = True

# === STYLES ===
card_style = {
    "border": "1px solid #e0e0e0",
    "borderRadius": "12px",
    "padding": "20px",
    "margin": "15px auto",
    "boxShadow": "0 4px 12px rgba(0,0,0,0.05)",
    "backgroundColor": "#ffffff"
}
button_primary = {
    "backgroundColor": "#2563eb",
    "color": "white",
    "border": "none",
    "borderRadius": "8px",
    "padding": "12px 24px",
    "fontWeight": "500",
    "cursor": "pointer"
}

app.layout = html.Div([
    html.Div([
        html.H1("AI Gmail Responder", style={
            'textAlign': 'center', 'margin': '30px 0 10px', 'fontWeight': '700', 'color': '#1e40af'
        }),
        html.P("AI mail classifier and responder",
               style={'textAlign': 'center', 'color': '#6b7280', 'fontSize': '14px'})
    ]),

    # Refresh Button
    html.Div([
        html.Button([
            dcc.Loading(id="loading-refresh", type="circle", children="Refresh Live Emails")
        ], id="refresh-btn", n_clicks=0, style=button_primary),
        html.Div(id="email-count", style={
            'textAlign': 'center', 'marginTop': '12px', 'fontSize': '14px', 'color': '#374151'
        })
    ], style={'textAlign': 'center', 'marginBottom': '20px'}),

    # Email Selector
    html.Div([
        html.Label("Select an Email", style={'fontWeight': '600', 'marginBottom': '8px', 'display': 'block'}),
        dcc.Dropdown(id="email-dropdown", placeholder="Choose an email...", options=[], value=None)
    ], style=card_style | {'maxWidth': '900px'}),

    # Email Preview
    html.Div(id="email-display", children=[
        html.Div("Click 'Refresh' to load your inbox.", 
                 style={'color': '#9ca3af', 'fontStyle': 'italic', 'textAlign': 'center', 'padding': '40px'})
    ], style=card_style | {'maxWidth': '900px'}),

    # Classification
    html.Div(id="classification", style={'textAlign': 'center', 'margin': '10px 0'}),

    # Draft
    html.Div([
        html.H3("AI Draft", style={'margin': '0 0 12px', 'color': '#1e40af'}),
        dcc.Textarea(id="draft-output", readOnly=True, style={
            'width': '100%', 'height': '160px', 'resize': 'none', 'fontSize': '14px', 'borderRadius': '8px'
        })
    ], style=card_style | {'maxWidth': '900px'}),

    # Feedback
    html.Div([
        html.Label("Your Feedback (optional)", style={'fontWeight': '600', 'marginBottom': '8px'}),
        dcc.Textarea(id="feedback-input", placeholder="e.g., Make it shorter...", style={
            'width': '100%', 'height': '90px', 'resize': 'none', 'fontSize': '14px', 'borderRadius': '8px'
        }),
        html.Br(),
        html.Button("Refine Draft", id="refine-btn", n_clicks=0, style=button_primary | {'width': '100%'})
    ], style=card_style | {'maxWidth': '900px'}),

    # Refined Output
    html.Div(id="refined-output", style={'marginTop': '20px'}),

    # Hidden trigger
    dcc.Store(id="reset-trigger", data=0)
], style={
    'fontFamily': "'Inter', 'Segoe UI', sans-serif",
    'backgroundColor': '#f8fafc',
    'minHeight': '100vh',
    'paddingBottom': '50px'
})

# ================================
# CALLBACK: REFRESH + FULL RESET + INITIAL LOAD
# ================================
@callback(
    [Output("email-dropdown", "options"),
     Output("email-dropdown", "value"),
     Output("email-count", "children"),
     Output("email-display", "children"),
     Output("classification", "children"),
     Output("draft-output", "value"),
     Output("feedback-input", "value"),
     Output("refined-output", "children"),
     Output("reset-trigger", "data")],
    Input("refresh-btn", "n_clicks"),
    prevent_initial_call='initial_duplicate'  # This allows first load
)
def refresh_and_reset(n_clicks):
    update_emails_cache()

    options = [
        {"label": f"{e['subject'][:50]}{'...' if len(e['subject']) > 50 else ''} — {e['from'].split('@')[0]}",
         "value": e["id"]} for e in emails_cache
    ]
    value = options[0]["value"] if options else None
    count = f"Loaded {len(emails_cache)} unread email{'s' if len(emails_cache) != 1 else ''} from Gmail"

    return (
        options, value, count,
        "No email selected. Choose one above." if not value else "",
        "", "", "", "", n_clicks
    )

# ================================
# CALLBACK: SELECT EMAIL
# ================================
@callback(
    [Output("email-display", "children", allow_duplicate=True),
     Output("classification", "children", allow_duplicate=True),
     Output("draft-output", "value", allow_duplicate=True)],
    Input("email-dropdown", "value"),
    prevent_initial_call=True
)
def update_email(email_id):
    if not email_id or not emails_cache:
        return (
            html.Div("No email selected.", style={'color': '#9ca3af', 'textAlign': 'center', 'padding': '40px'}),
            "", ""
        )

    email = next((e for e in emails_cache if e["id"] == email_id), None)
    if not email:
        return "Email not found.", "", ""

    category = classifier.classify(email["body"])
    draft = drafter.draft(email["body"], email_id)

    display = html.Div([
        html.Div([html.Strong("Subject: "), html.Span(email["subject"])], style={'marginBottom': '8px'}),
        html.Div([html.Strong("From: "), html.Span(email["from"])], style={'marginBottom': '12px'}),
        html.Hr(style={'border': '1px dashed #e5e7eb', 'margin': '12px 0'}),
        html.P(email["body"][:800] + ("..." if len(email["body"]) > 800 else ""),
               style={'whiteSpace': 'pre-wrap', 'fontSize': '14px', 'lineHeight': '1.5'})
    ])

    badge_color = {"URGENT": "#dc2626", "WORK": "#f59e0b", "PERSONAL": "#10b981", "SPAM": "#6b7280"}.get(category, "#6366f1")
    badge = html.Span(f"Category: {category}", style={
        'backgroundColor': badge_color, 'color': 'white', 'padding': '6px 14px',
        'borderRadius': '999px', 'fontSize': '13px', 'fontWeight': '600'
    })

    return display, badge, draft

# ================================
# CALLBACK: REFINE DRAFT
# ================================
@callback(
    Output("refined-output", "children", allow_duplicate=True),
    Input("refine-btn", "n_clicks"),
    State("email-dropdown", "value"),
    State("draft-output", "value"),
    State("feedback-input", "value"),
    prevent_initial_call=True
)
def refine_draft(n_clicks, email_id, draft, feedback):
    if not feedback or not feedback.strip():
        return html.Div("Please provide feedback.", style={'color': '#ef4444'})

    email = next((e for e in emails_cache if e["id"] == email_id), None)
    if not email:
        return "Email not found."

    refined = refiner.refine(email["body"], draft, feedback, email_id)

    return html.Div([
        html.H4("Refined Reply", style={'margin': '0 0 12px', 'color': '#1e40af'}),
        dcc.Textarea(value=refined, readOnly=True, style={
            'width': '100%', 'height': '140px', 'resize': 'none', 'fontSize': '14px', 'borderRadius': '8px'
        }),
        html.Div("Feedback saved.", style={'marginTop': '8px', 'fontSize': '12px', 'color': '#10b981', 'fontStyle': 'italic'})
    ], style=card_style | {'maxWidth': '900px', 'borderLeft': '4px solid #10b981'})


@callback(
    Output("feedback-input", "value", allow_duplicate=True),
    Input("refine-btn", "n_clicks"),
    prevent_initial_call=True
)
def clear_feedback(n_clicks):
    return ""

if __name__ == "__main__":
    debug = os.getenv("DASH_DEBUG", "False").lower() == "true"
    app.run(host="0.0.0.0", port=8050, debug=debug)