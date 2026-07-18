# API and Integrations

## Rate limits
The Loomly API allows 300 requests/minute on Pro and 1000 requests/minute on Team. Exceeding this returns HTTP 429 with a Retry-After header.

## Webhook delivery failures
Webhooks are retried with exponential backoff for 24 hours, then dropped. Check Settings > Developer > Webhook Logs for delivery status and response codes from the receiving endpoint.

## OAuth token expiration
Access tokens expire after 1 hour; refresh tokens are valid for 90 days of inactivity. Integrations should implement refresh-token rotation, not prompt users to re-auth hourly.

## Zapier/Slack integration not triggering
Most common cause is the integration losing its OAuth grant after a password change. Ask the user to disconnect and reconnect the integration in Settings > Integrations.
