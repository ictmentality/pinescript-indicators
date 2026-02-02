For “Implement with Codex” on a TODO/comment:

- Do the smallest correct change to satisfy the comment.
- Keep diffs minimal (no refactors/cleanup/reformatting unless required).
- Don’t over-explore: touch only what’s necessary.
- Don’t add new `request.security*` calls or duplicate existing ones unless explicitly required.
- Prefer existing aligned/cached series packs + helpers over new plumbing.
- If multiple options exist, pick the simplest consistent with existing patterns.

Output:
- Implement the change directly; no extra files unless necessary; no long explanations.
