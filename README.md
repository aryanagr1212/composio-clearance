# Clearance

A shareable guide for getting an OAuth app created and approved.

A developer types an app name. About a minute later they get a page that answers four questions:

1. How hard is this?
2. How long until a first test call, and how long until production approval, including the wait?
3. What will block approval?
4. What can an agent prepare, and what does a person still have to do?

That is the whole product. A library of 100 guides is the same page, generated in batch. This repo ships four reviewed examples and the live generator.

## Why this scope

The developer is not stuck because OAuth is a mystery. They are stuck because they cannot tell an hour of console work from a month of review, and the docs mix "create an app" with "get listed in the marketplace."

The guide separates those. Gmail is hard because mailbox scopes are restricted and a server that sees that data needs Google's CASA assessment. Slack is easy until you want the Marketplace, which is measured in weeks. Notion is a short form, with a page picker that surprises people. HubSpot lets you test first, then stops you at 25 installs until a listing review.

Composio already hosts a managed OAuth app for all four. The guide says when to use that and when to register your own client (your brand on the consent screen, a scope the managed app does not request, or your own quota). The redirect URI to register is the one in the Composio dashboard. The programmatic docs name `https://backend.composio.dev/api/v3/toolkits/auth/callback`, and some toolkits still use the legacy `https://backend.composio.dev/api/v1/auth-apps/add`.

## Run it

Python 3.11 or newer.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --host 127.0.0.1 --port 43123
```

Open [http://127.0.0.1:43123](http://127.0.0.1:43123).

```bash
pytest
```

The example guides render with an empty `.env`. Live generation does not.

## Example guides

| Guide | Difficulty | Why it is in the set |
| --- | --- | --- |
| [Gmail](http://127.0.0.1:43123/g/gmail) | Hard | Restricted Gmail scopes, verification, and usually CASA |
| [Slack](http://127.0.0.1:43123/g/slack) | Easy | Install is self-serve. Marketplace review is the long path |
| [Notion](http://127.0.0.1:43123/g/notion) | Easy | Public connection is a form. The page picker is the usual surprise |
| [HubSpot](http://127.0.0.1:43123/g/hubspot) | Medium | You can test before review, then you hit a 25-install cap |

Each guide has a permalink (`/g/{slug}`), a Markdown copy (`/g/{slug}.md`), and JSON (`/api/guides/{slug}`).

## Live generation

Set one model key and one search key in `.env`, then restart the server.

```bash
OPENAI_API_KEY=...          # or ANTHROPIC_API_KEY
OPENAI_MODEL=gpt-4.1-mini   # confirm this model exists on your key
TAVILY_API_KEY=...          # or SERPER_API_KEY
```

`LLM_PROVIDER=auto` uses OpenAI when `OPENAI_API_KEY` is set, otherwise Anthropic. `SEARCH_PROVIDER=auto` uses Tavily, otherwise Serper. If the provider rejects the model name, the job page shows that error and names the env var to change.

With no keys, submitting an unknown app returns a page that says live generation is off and names the missing variables. Submitting Gmail, Slack, Notion, or HubSpot still opens the reviewed guide.

Optional read-only browser check, which is the only way a live guide earns a **tested** label:

```bash
pip install playwright
playwright install chromium
# .env
BROWSER_CHECK=auto   # on if Playwright is installed, otherwise skipped
```

The browser opens one public page and does not type, click, or log in. A password field is recorded as a login wall. `BROWSER_CHECK=off` skips it.

Generated guides are JSON files in `data/`. A reviewed slug is never overwritten. Running the agent on Gmail saves `gmail-draft`.

## Architecture

```
name or URL
    → search (Tavily or Serper)
    → fetch up to 8 public docs pages
    → optional read-only browser check
    → model fills the guide schema (Pydantic)
    → grounding pass
    → HTML and Markdown
```

| Piece | Where |
| --- | --- |
| Guide schema | `app/schema.py` |
| Reviewed examples | `app/guides/` |
| Search, fetch, browser, extract, grounding | `app/pipeline/` |
| HTTP UI | `app/main.py`, `app/web/` |
| Saved guides | `data/*.json` |

The model is not the source of truth. After it returns JSON, `app/pipeline/ground.py` walks every claim:

- **Tested** survives only if the source URL is the page the browser check opened.
- **Sourced** survives only if this run fetched that URL.
- Anything else is rewritten to **uncertain**, and the note says it was downgraded.

Redirects to non-public hosts are refused before the fetch. That matters because the website field and the search results are URLs the server will open.

Jobs are in memory. A restart drops an in-flight run. Finished guides stay in `data/`.

## Confidence labels

| Label | Meaning |
| --- | --- |
| Tested | A read-only browser check opened the page, and the sentence is what that page showed. |
| Sourced | The sentence cites a link. On a live guide, this run opened that link. The plan called this "documented." |
| Uncertain | The pages did not say it. The note says what is missing. It is a lead, not a launch date. |

A sourced or tested claim without a link does not validate. The reviewed examples were written from public docs on 20 Oct 2026. Nobody logged into a provider console, so those guides have sourced and uncertain claims, and no tested claims. That is deliberate. A fetched doc is not the same as watching the console.

The task lines under "An agent can prepare" and "You have to do" are recommendations. The chip next to them is the provider fact the recommendation is based on.

## Demo script

Use this when someone types an unfamiliar app and watches.

1. Open the home page. Say the product answers four questions, and that the four cards are reviewed examples that do not need keys.
2. Open **Gmail**. Point at the difficulty, the seven-day Testing tokens, and CASA. Open one **sourced** chip and show the Google page. Then find an **uncertain** chip (billing, or the console form, which was not opened) and say why it is not stated as fact.
3. Open **Slack** and **Notion** only long enough to show the contrast: Slack's wait is the Marketplace, not the install. Notion's surprise is the page picker, and one blocker is left uncertain because two official pages do not agree about when the authorization URL appears.
4. Open **HubSpot** if you want the middle case: test now, 25 installs until listing, installer must be a Super Admin.
5. Go home. Type an app that is not one of the four. Paste the provider's docs URL if you have it. Leave the tab open. Talk while it runs: search, then the pages, then the write. It should finish inside two minutes when the keys and the network are healthy.
6. On the result, click a sourced chip and confirm the page actually says that. Open "How this guide was made" and read any grounding line. Those are sentences the model tried to cite that this run did not open.
7. Copy as Markdown. Paste it into the chat or a doc. Open the permalink in a second tab.

If the keys are missing, step 5 should show the clear error, not a spinner. Say that, and use the examples.

## Known limitations

- No provider console was completed. Tested evidence appears only when the browser check runs, and even then it cannot pass a login wall.
- Search quality decides whether an unfamiliar app gets official docs or a blog. Grounding removes invented links. It cannot add a fact the model skipped.
- The model name in `.env.example` is a default to edit. A key that cannot call that model fails the job with the provider's error.
- Cached guides do not expire. The date on the page is the day it was generated.
- Notion's authorization guide says the Authorization URL appears after a review. The Marketplace guide says a public connection works without a listing. Both sentences are in the Notion guide. Which submission the form wants was not confirmed in the portal.
- HubSpot's access-token lifetime is not stated on the pages used here, so the guide does not give a number of minutes.
- Google does not publish a CASA price on the verification page. The guide does not invent one.
- There is no login on this app. Do not put the live-generation endpoint on the public internet without a rate limit, or strangers will spend the API keys.
- Jobs are single-process and in memory.
- The fetcher blocks obvious non-public hosts. It is not a full SSRF suite.
- English docs only.

## Left to decide

- Deploy it (Render or Fly are enough; the app is one process and a folder of JSON).
- Turn the browser check on for the live demo if you want tested chips.
- Add Salesforce the same way as HubSpot if you want a second mid-tier CRM. HubSpot was chosen because the 25-install cap and the Acceptable Use Policy are concrete.
- Batch the long tail: a queue of app names, the same pipeline, a QA pass on the percent of claims that stayed sourced.
- Recheck guides whose `last_checked` is old.
- After you personally click through a console, upgrade the specific sentences you saw to tested and say what you clicked.
- Swap the search or model client in `app/pipeline/search.py` and `app/pipeline/extract.py` if you would rather call Composio's own tools.
