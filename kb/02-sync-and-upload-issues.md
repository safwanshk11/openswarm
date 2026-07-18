# Sync and Upload Issues

## Sync stuck at a percentage
This is almost always caused by a file with an unsupported character in its name (emoji, or characters outside UTF-8 BMP). The desktop client should skip and log these, but versions before 4.2.0 hang instead. Fix: update to the latest client, or rename the offending file.

## Uploads failing with "Error 503"
Error 503 during upload means the regional storage node is temporarily overloaded. This is not account-specific. It typically resolves within 15-30 minutes. If it persists longer than 2 hours, escalate to infrastructure on-call.

## Duplicate files after reconnecting
If a device loses connection mid-sync and reconnects, the client may re-upload files as "(1)" copies. This is a known issue in the conflict-resolution logic. Users can safely delete the duplicate; the original is always the one without the suffix.

## Mobile app not syncing photos
Photo sync on iOS requires "Background App Refresh" to be enabled in system settings for the Loomly app. This is an OS-level permission we cannot override.
