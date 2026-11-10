import time

import httpx

USER_AGENT = "monitor-crises/0.1 (+https://github.com/)"


def get(url, *, timeout=60, retries=3, **params):
    last = None
    for attempt in range(retries):
        try:
            r = httpx.get(url, params=params or None, timeout=timeout, follow_redirects=True,
                          headers={"User-Agent": USER_AGENT})
            r.raise_for_status()
            return r
        except httpx.HTTPError as e:
            last = e
            time.sleep(2 * (attempt + 1))
    raise last


def get_json(url, **kw):
    return get(url, **kw).json()
