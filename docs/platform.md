# Backing Platform — FreshRSS

`freshrss-agent` is a **client** of a backing service instance. This page provides a
Docker recipe for deploying one locally to serve as the target of
`FRESHRSS_URL`.

!!! note "Backing-system recipe"
    Each connector in the ecosystem follows the same convention — a
    `docs/platform.md` recipe for the system it integrates with, accompanied by a
    sample Compose stack. Systems offered only as a managed service have no local
    recipe.

## Single-node deployment (Compose)

```yaml
# docker/platform.compose.yml — FreshRSS backing instance
services:
  freshrss:
    image: freshrss/freshrss:latest
    restart: unless-stopped
    environment:
      TZ: Etc/UTC
      CRON_MIN: "*/15"
    volumes:
      - freshrss_data:/var/www/FreshRSS/data
      - freshrss_extensions:/var/www/FreshRSS/extensions
    ports:
      - "8080:80"

volumes:
  freshrss_data:
  freshrss_extensions:
```

After the container is up, complete the web installer at `http://localhost:8080`,
then enable the API under **Settings → Authentication → Allow API access** and set
an **API password** for your user. `freshrss-agent` authenticates against the
GReader endpoint using:

- `FRESHRSS_URL` — base URL of the instance (e.g. `http://freshrss.arpa`).
- `FRESHRSS_USER` — the FreshRSS username (the GReader `Email` field).
- `FRESHRSS_API_PASSWORD` — the **API password** set in FreshRSS (not the login
  password).
