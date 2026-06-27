# Database Layer

`app.db` owns the SQLAlchemy metadata and database initialization entrypoint.

- `GameState` stores one save slot per row in `game_states`.
- `init_db()` creates the configured database tables and returns the SQLAlchemy engine.
- `state_json` is intentionally a JSON column for the MVP stage.
- String lengths are schema metadata and portability hints. SQLite does not enforce
  them, so service/API layers must validate `save_slot`, `title`, and `scenario_id`
  before writing user input.
- Timestamps are generated in UTC. SQLite may return naive `datetime` values; treat
  them as UTC at the application boundary.

**IMPORTANT**: The JSON state is temporary. When the TRPG state shape stabilizes, split stable domains into dedicated columns or tables, especially inventory, quests, NPC relationships, factions, world events, combat state, and short-term memory.
