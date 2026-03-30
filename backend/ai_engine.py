import os

from dotenv import load_dotenv
from groq import Groq


LANGUAGE_INSTRUCTIONS = {
    "English": "Respond in English.",
    "Hindi": "Respond in Hindi.",
    "Marathi": "Respond in Marathi.",
    "Bengali": "Respond in Bengali.",
    "Telugu": "Respond in Telugu.",
    "Tamil": "Respond in Tamil.",
    "Malayalam": "Respond in Malayalam.",
}


def _build_product_lines(products: list[dict], empty_message: str) -> str:
    if not products:
        return f"- {empty_message}\n"

    lines = []
    for product in products[:4]:
        parts = [
            str(product.get("product", "Unknown")),
            f"sales {product.get('total_sales', 'N/A')}",
        ]

        if product.get("rank") is not None:
            parts.append(f"rank {product.get('rank')}")
        if product.get("share_of_catalog_sales_pct") is not None:
            parts.append(f"share {product.get('share_of_catalog_sales_pct')}%")
        if product.get("average_sales") is not None:
            parts.append(f"avg {product.get('average_sales')}")

        lines.append(f"- {', '.join(parts)}")

    return "\n".join(lines) + "\n"


def _build_period_lines(periods: list[dict]) -> str:
    if not periods:
        return "- No recent period trend summary was provided.\n"

    lines = []
    for period in periods[-4:]:
        lines.append(
            "- {label}: total sales {sales}, growth {growth}%".format(
                label=period.get("label", "Unknown period"),
                sales=period.get("total_sales", "N/A"),
                growth=period.get("growth_pct", "N/A"),
            )
        )
    return "\n".join(lines) + "\n"


def _build_festival_lines(festivals: list[dict]) -> str:
    if not festivals:
        return "- No strong festival pattern was detected.\n"

    lines = []
    for festival in festivals[:4]:
        lines.append(
            "- {name}: average sales {sales}".format(
                name=festival.get("festival", "Unknown festival"),
                sales=festival.get("average_sales", "N/A"),
            )
        )
    return "\n".join(lines) + "\n"


def build_prompt(sales_summary: dict, language: str) -> str:
    lang_instruction = LANGUAGE_INSTRUCTIONS.get(language, "Respond in English.")
    top_product_lines = _build_product_lines(
        sales_summary.get("product_stats") or [],
        "No top-product breakdown was available.",
    )
    slow_product_lines = _build_product_lines(
        sales_summary.get("slow_products") or [],
        "No weak-product list was available.",
    )
    period_lines = _build_period_lines(sales_summary.get("recent_periods") or [])
    festival_lines = _build_festival_lines(sales_summary.get("top_festivals") or [])
    festival_impact = sales_summary.get("festival_impact") or {}
    trend_highlights = sales_summary.get("trend_highlights") or {}
    comparison = sales_summary.get("comparison_to_current") or {}
    dataset_stats = sales_summary.get("dataset_stats") or {}

    return f"""
{lang_instruction}

You are an experienced business and sales advisor for a local shopkeeper.
Your job is to study the uploaded shop dataset and give practical advice that can help the owner improve sales and likely improve profit.

Important rules:
- Use only the provided dataset signals.
- If margin, cost, or profit data is not directly available, do not invent exact profit numbers.
- In that case, explain profit improvement through stock mix, pricing, bundles, display focus, festival preparation, and reducing slow-moving stock.
- Be practical, specific, and shopkeeper-friendly.
- Do not give generic motivational advice.
- Use short bullets, not long paragraphs.
- Keep the answer between 180 and 260 words.

Business context:
- Scope: {sales_summary.get("scope", "All products")}
- Market: {sales_summary.get("market", "Unknown")}
- Dataset date range: {dataset_stats.get("start_date", "N/A")} to {dataset_stats.get("end_date", "N/A")}
- Dataset rows: {dataset_stats.get("rows", "N/A")}
- Series points: {dataset_stats.get("series_points", "N/A")}
- Granularity: {sales_summary.get("granularity", "Daily")}
- Total Sales: {sales_summary.get("total_sales", "N/A")}
- Average Sales: {sales_summary.get("average_sales", "N/A")}
- Latest Sales: {sales_summary.get("latest_sales", "N/A")}
- Current Run Rate: {sales_summary.get("current_run_rate", "N/A")}
- Growth Rate: {sales_summary.get("growth_rate", "N/A")}
- Trend Direction: {sales_summary.get("trend", "stable")}
- Volatility: {sales_summary.get("volatility_pct", "N/A")}
- Forecast Direction: {sales_summary.get("forecast_direction", "stable")}
- Forecast Total: {sales_summary.get("forecast_total", "N/A")}
- Forecast Average Sales: {comparison.get("forecast_average_sales", "N/A")}
- Forecast vs Current Change: {comparison.get("delta_pct", "N/A")}
- Next Period Change: {comparison.get("next_period_delta_pct", "N/A")}
- Peak Forecast Date: {sales_summary.get("peak_forecast_date", "N/A")}
- Peak Forecast Sales: {sales_summary.get("peak_forecast_sales", "N/A")}
- Festival Signal: {sales_summary.get("festival", "None")}
- Festival Uplift %: {festival_impact.get("uplift_percentage", "N/A")}

Trend highlights:
- Momentum: {trend_highlights.get("momentum", "N/A")}
- Best Period: {trend_highlights.get("best_period", {}).get("label", "N/A")}
- Weakest Period: {trend_highlights.get("weakest_period", {}).get("label", "N/A")}

Top products:
{top_product_lines}

Slow or weak products:
{slow_product_lines}

Recent period movement:
{period_lines}

Festival performance:
{festival_lines}

Write the response in these exact sections only:
## Business Health
- 2 to 4 bullets on overall shop condition using the uploaded data.

## Problems To Fix
- 2 to 4 bullets on the biggest business risks or weak areas.

## Products To Push
- 2 to 4 bullets on what to stock more, promote more, or watch closely.

## Actions For Better Sales
- Give exactly 5 action bullets that a shopkeeper can follow.
- Include actions about stock, pricing/promo, display/focus, and festival preparation when relevant.

## Next Sales Outlook
- 2 to 4 bullets on near-term outlook from the forecast.
"""


def get_ai_insight(sales_summary: dict, language: str = "English") -> str:
    load_dotenv(override=True)

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or "gsk_xxxx" in api_key:
        return "AI insight unavailable: Please set a valid GROQ_API_KEY in backend/.env"

    model_name = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    client = Groq(api_key=api_key)
    prompt = build_prompt(sales_summary, language)

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a sharp retail business advisor for small shopkeepers. "
                        "You give practical sales and merchandising advice using only the supplied data. "
                        "Never invent margin, profit, cost, or demand facts that are not present."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.25,
            max_tokens=420,
        )
        return response.choices[0].message.content
    except Exception as error:
        return f"AI insight unavailable: {error}"
