# Recording plan — target 2 minutes 20 seconds

Record only after successful live AWS verification. Hide credentials, account IDs
and billing screens. Use the synthetic fixture. Publish the video as public, under
three minutes. This file is a recording plan, not evidence of a completed run.

- 0:00–0:15: Explain the question: can a storyteller continue a chapter it cannot access?
- 0:15–0:40: Run `python agent.py --mode before`. Show the actual response.
- 0:40–1:00: Show the fixture: Nia, Pip, a golden seed in a green pouch, a promise to plant it by the pond.
- 1:00–1:35: Run `python agent.py --mode after`. Show the actual S3 retrieval trace and continuation.
- 1:35–2:00: Point out which details the continuation preserved. If it did not, report that honestly and debug before submission.
- 2:00–2:20: Show the single tool definition, fixed S3 prefix and loop limit. Explain that the agent was built during the challenge; do not claim it predates the event.

Before recording, confirm eligibility with the organizers. After recording, replace
the pending verification paragraph in submission.md with what was actually observed,
add the genuine repository/video URLs, and publish the entry.
