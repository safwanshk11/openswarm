# Account and Security

## Password reset not arriving
Reset emails can take up to 10 minutes. Check spam first. If using a corporate email with strict filtering, ask the user to whitelist mail@loomlycloud.com.

## Two-factor authentication lockout
If a user loses access to their 2FA device, identity must be verified via the account's registered phone number before we disable 2FA manually. We never disable 2FA based on email request alone, this is a hard security policy.

## Suspicious login alerts
These are triggered by new device or new country logins. If the user confirms it wasn't them, immediately advise a password reset and review of active sessions under Settings > Security > Active Sessions.

## Account deletion
Account deletion is permanent after a 30-day grace period, during which the user can cancel the deletion by logging back in. We cannot expedite permanent deletion faster than the 30-day window, this is a legal/compliance requirement.
