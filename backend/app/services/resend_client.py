import resend
from app.core.config import settings

resend.api_key = settings.RESEND_API_KEY


async def send_magic_link_email(to: str, token: str):
    magic_url = f"{settings.FRONTEND_URL}/auth/verify?token={token}"

    resend.Emails.send(
        {
            "from": f"Carry Trade Helper <onboarding@resend.dev>",
            "to": [to],
            "subject": "Sign in to Carry Trade Helper",
            "html": f"""
            <html>
            <body>
                <h2>Sign in to Carry Trade Helper</h2>
                <p>Click the link below to sign in:</p>
                <a href="{magic_url}" style="background-color: #3b82f6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px;">
                    Sign In
                </a>
                <p style="color: #666; margin-top: 16px;">This link will expire in 15 minutes.</p>
                <p style="color: #999; font-size: 12px;">If you didn't request this email, you can safely ignore it.</p>
            </body>
            </html>
        """,
        }
    )


async def send_daily_report(to: str, report_data: dict):
    html_content = f"""
        <html>
        <body>
            <h2>Daily Carry Trade Report</h2>
            <h3>Exchange Rates</h3>
            <ul>
    """

    for pair, rate in report_data.get("exchange_rates", {}).items():
        html_content += f"<li>{pair}: {rate}</li>"

    html_content += """
            </ul>
            <h3>Interest Rates</h3>
            <ul>
    """

    for country, rate in report_data.get("interest_rates", {}).items():
        html_content += f"<li>{country}: {rate}%</li>"

    html_content += """
            </ul>
            <p>Best regards,<br>Carry Trade Helper Team</p>
        </body>
        </html>
    """

    resend.Emails.send(
        {
            "from": f"Carry Trade Helper <reports@{settings.EMAIL_DOMAIN}>",
            "to": [to],
            "subject": f"Daily Carry Trade Report - {report_data.get('date', 'Today')}",
            "html": html_content,
        }
    )
