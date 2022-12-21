# Troubleshooting

## Scrapeworker

Very useful to set `DEBUG=1 LOG_LEVEL=debug` for debugging scrapeworker. Be aware that the log level debug will turn on debug for _all_ libs which may be more than you care about. You can filter debug logs by tag as well.

Setting the debug flag will disable headless mode and enable slowmo and devtools within playwright. This allows you to see the browser window and interact with it and/or the devtools.

tldr;

```bash
LOG_LEVEL=debug DEBUG=1 python backend/scrapeworker/main.py
```

``
