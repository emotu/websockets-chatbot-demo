# How to run

- Start the app with `uv run fastapi dev`
- Create users and threads assets using the post enpoints (`/users`, `/threads`) using httpx or postman
- Create at least one Agent user and set the ID as `AGENT` in the `app.agents.runner` file
- Connect to a thread channel using `ws://localhost:8000/ws/<thread_id>`
- Post messages using via rest `/messages` via postman
- View the websockets response channel for AI responses.
