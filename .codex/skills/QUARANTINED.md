# Skills quarantined

The previous `.codex/skills` set was ported from Atly before this website's real workflow contracts were verified. It contained Atly repository names, iOS/TestFlight assumptions, AtlyTests paths, Fibery/Project rules, and provider identifiers that do not belong to davidsulitzer.com.

Those skills are intentionally inactive. Git history preserves them if forensic comparison is needed.

Before restoring any repo-local skill:

1. Verify this repository's current stack, default branch, test/build/deploy path, issue tracker, design source, hosting target, and Doppler project/config.
2. Start from the reusable contract, not an Atly file copy.
3. Use a unique repository-specific name when a global skill already owns the generic name.
4. Validate the new skill and its negative routing cases.
5. Keep secrets in Doppler and never commit `.codex/environments` contents.

Until that re-audit happens, use the current global Codex skills plus ordinary repository documentation.
