---
name: search-reservations
description: Search for restaurant reservations across Resy and OpenTable. Use when the user wants to find restaurants, check availability, or book a table. First researches restaurants matching the user's preferences via web search, then checks real-time availability on both platforms.
allowed-tools: Bash(agent-browser:*), WebSearch
---

# Restaurant Reservation Search

Find restaurants and check real-time availability across **Resy** and **OpenTable**.

## Workflow

### Step 1: Research restaurants via web search

Use `WebSearch` to find restaurants matching the user's criteria:
- Location / neighborhood
- Cuisine type or vibe (romantic, casual, trendy, outdoor, etc.)
- Price range
- Dietary needs
- Any specific restaurant names mentioned

Search queries like:
- `"best italian restaurants in SoHo NYC for date night"`
- `"highly rated sushi near downtown SF with outdoor seating"`
- `"romantic restaurants Chicago Michelin"`

Collect 5–10 candidate restaurants from search results.

### Step 2: Check availability on both platforms

For **each** candidate restaurant, check availability on both Resy and OpenTable in parallel.

#### Resy

```bash
agent-browser open "https://resy.com/cities/{city-slug}/venues/{restaurant-slug}?date={YYYY-MM-DD}&seats={N}"
agent-browser snapshot -i
```

- **city-slug**: e.g., `new-york-ny`, `los-angeles-ca`, `chicago-il`, `san-francisco-ca`
- **restaurant-slug**: lowercase hyphenated name (e.g., `carbone`, `don-angie`)
- If you don't know the slug, search first: `https://resy.com/cities/{city-slug}?query={restaurant+name}&date={YYYY-MM-DD}&seats={N}`

Look for available time slot buttons in the snapshot. Extract each slot's time.

Deep link format for a specific slot:
```
https://resy.com/cities/{city-slug}/venues/{restaurant-slug}?date={YYYY-MM-DD}&seats={N}
```
(Resy doesn't support time in URL — the user clicks the slot on the page.)

#### OpenTable

```bash
agent-browser open "https://www.opentable.com/r/{restaurant-slug}?dateTime={YYYY-MM-DD}T{HH}%3A{MM}&covers={N}"
agent-browser snapshot -i
```

- If you don't know the slug, search first: `https://www.opentable.com/s?dateTime={YYYY-MM-DD}T{HH}%3A{MM}&covers={N}&term={restaurant+name}`

Look for available time slot buttons. Extract each slot's time.

Deep link format for a specific slot:
```
https://www.opentable.com/r/{restaurant-slug}?dateTime={YYYY-MM-DD}T{HH}%3A{MM}&covers={N}
```

### Step 3: Present results

Return a consolidated list. For each restaurant with availability:

**Restaurant Name** — Neighborhood, Cuisine
- Why it fits: (1 sentence based on web research)
- Available on **Resy**: 6:00 PM, 7:30 PM, 9:15 PM
  - [Book on Resy](deep-link-url)
- Available on **OpenTable**: 6:30 PM, 8:00 PM
  - [Book on OpenTable](deep-link-url)

If a restaurant has **no availability** on either platform, still list it with:
- "No availability found for {date} at {time} — [check Resy](link) | [check OpenTable](link)"

Sort results by: restaurants with the most/best availability first, then by match quality to the user's request.

## Platform notes

- **Resy** is stronger for high-demand, trendy restaurants in major cities. Check for "Notify" buttons on sold-out spots — offer to help the user join the waitlist.
- **OpenTable** has broader coverage including casual dining. Booking may require the user to log in on their end.
- A restaurant may only appear on one platform — always check both.
- For same-day searches, Resy sometimes has last-minute cancellation slots worth checking.
