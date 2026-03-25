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


def _build_product_lines(sales_summary: dict) -> str:
    product_stats = sales_summary.get("product_stats") or []
    if not product_stats:
        return "- No product-level breakdown was provided.\n"

    lines = []
    for product in product_stats[:4]:
        lines.append(
            "- {name}: sales {sales}, share {share}%".format(
                name=product.get("product", "Unknown"),
                sales=product.get("total_sales", "N/A"),
                share=product.get("share_of_catalog_sales_pct", 0),
            )
        )
    return "\n".join(lines) + "\n"


def build_prompt(sales_summary: dict, language: str) -> str:
    lang_instruction = LANGUAGE_INSTRUCTIONS.get(language, "Respond in English.")
    product_lines = _build_product_lines(sales_summary)

    return f"""
{lang_instruction}

You are a retail AI analyst for store owners.
Your job is to produce a short, easy-to-scan decision brief.

Business context:
- Scope: {sales_summary.get("scope", "All products")}
- Market: {sales_summary.get("market", "Unknown")}
- Total Sales: {sales_summary.get("total_sales", "N/A")}
- Current Trend: {sales_summary.get("trend", "stable")}
- Growth Rate: {sales_summary.get("growth_rate", "N/A")}
- Granularity: {sales_summary.get("granularity", "Daily")}
- Current Run Rate: {sales_summary.get("current_run_rate", "N/A")}
- Latest Sales: {sales_summary.get("latest_sales", "N/A")}
- Forecast Direction: {sales_summary.get("forecast_direction", "stable")}
- Forecast Total: {sales_summary.get("forecast_total", "N/A")}
- Upcoming Festival Signal: {sales_summary.get("festival", "None")}

Top product context:
{product_lines}

Write the response in these exact sections only:
## Core Problem
- Mention the single biggest business issue.

## Focus Area
- Mention the main product, segment, or sales area to focus on now.
- Mention one supporting reason.

## Future Strategy
- Give exactly 3 short action bullets for the next 30-90 days.

## Forecast Signal
- Mention near-term outlook in one or two bullets.

Rules:
- Keep the full answer under 140 words.
- Use very simple language for a shop owner.
- Use short bullets only. No paragraphs.
- Be specific and practical, not generic.
- If data is broad or uncertain, say that clearly in one bullet.
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
                    "content": "You create concise retail action briefs for small business owners.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.3,
            max_tokens=260,
        )
        return response.choices[0].message.content
    except Exception as error:
        return f"AI insight unavailable: {error}"
