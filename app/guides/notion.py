"""Notion, the easy public connection.

Judgment: difficulty is Easy. An internal connection or a personal access token
is enough for a first call in your own workspace. A public OAuth connection is
a form in the developer portal, and Marketplace listing is optional.

One real ambiguity is left uncertain on purpose. The authorization guide says
the Authorization URL field appears after the connection is submitted for review.
The Marketplace guide says a public connection works without a listing. Both
are quoted. Neither page explains the gap.

Claims were written from Notion's public docs on 20 Oct 2026. No Notion login.
"""

from datetime import date

from app.guides.claims import sourced, uncertain
from app.schema import (
    Blocker,
    ComposioContext,
    Guide,
    Requirement,
    ResearchEvent,
    ScopeItem,
    Step,
    Verdict,
    WorkItem,
)

AUTH = "https://developers.notion.com/guides/get-started/authorization"
AUTH_TITLE = "Authorization"
PUBLIC = "https://developers.notion.com/guides/get-started/public-connections"
PUBLIC_TITLE = "Public connections"
MARKET = "https://developers.notion.com/guides/get-started/marketplace-listing"
MARKET_TITLE = "List on the Marketplace"
TOKEN = "https://developers.notion.com/reference/create-a-token"
TOKEN_TITLE = "Create a token"
OVERVIEW = "https://developers.notion.com/guides/get-started/overview"
OVERVIEW_TITLE = "Overview"
MANAGED = "https://docs.composio.dev/toolkits/managed-auth"
MANAGED_TITLE = "Managed OAuth apps"
PROGRAMMATIC = "https://docs.composio.dev/docs/authentication/programmatic-auth-configs"
PROGRAMMATIC_TITLE = "Programmatic auth configs"

CHECKED = date(2026, 10, 20)


def build() -> Guide:
    return Guide(
        slug="notion",
        app_name="Notion",
        aliases=["notion api", "notion public connection"],
        homepage_url="https://www.notion.so",
        docs_url=PUBLIC,
        summary=(
            "Start with an internal connection if you only need your own workspace. "
            "A public connection is Notion's OAuth app: you set redirect URIs, "
            "capabilities, and an installation scope that you cannot change later. "
            "Users pick pages in a picker during consent. Listing in the Marketplace "
            "is optional and, if you do it, Notion says to expect a reply in 5–10 business days."
        ),
        last_checked=CHECKED,
        generated_by="curated",
        verdict=Verdict(
            difficulty="easy",
            review_required="conditional",
            difficulty_reason=sourced(
                "A public connection is created in the developer portal: name, "
                "development workspace, redirect URIs, installation scope, and "
                "capabilities. The OAuth client ID and secret are on the Configuration "
                "tab after that. Marketplace listing details are a separate section.",
                PUBLIC,
                PUBLIC_TITLE,
            ),
            time_to_first_test=sourced(
                "Internal connections are scoped to one workspace and use a static "
                "token. Personal access tokens are also static and tied to one user. "
                "Neither is the public OAuth flow. Use one of them for a first call "
                "against your own workspace.",
                AUTH,
                AUTH_TITLE,
                note="Notion does not publish how long the internal-connection form takes.",
            ),
            time_to_production=sourced(
                "Listing on the Marketplace is optional. A public connection can be "
                "used through its OAuth flow without being listed. If you do submit "
                "a listing, Notion says to expect a reply within 5–10 business days by email.",
                MARKET,
                MARKET_TITLE,
            ),
            review_summary=sourced(
                "Public connections must go through a Notion security review before "
                "they can be listed on the Marketplace. You can create and use a "
                "public connection without listing it.",
                OVERVIEW,
                OVERVIEW_TITLE,
            ),
        ),
        requirements=[
            Requirement(
                name="Notion account and a development workspace",
                needed="required",
                detail=sourced(
                    "Creating a public connection asks for a connection name and a "
                    "development workspace, plus redirect URIs, an installation scope, "
                    "and capabilities.",
                    PUBLIC,
                    PUBLIC_TITLE,
                ),
            ),
            Requirement(
                name="Redirect URI",
                needed="required",
                detail=sourced(
                    "You register redirect URIs in the OAuth configuration when you "
                    "create the public connection. After the user allows access, Notion "
                    "sends them to that URI with a temporary code.",
                    AUTH,
                    AUTH_TITLE,
                ),
            ),
            Requirement(
                name="Installation scope, chosen once",
                needed="required",
                detail=sourced(
                    "Any workspace means any Notion user can install it, and the "
                    "connection can be listed. Selected workspaces only means just the "
                    "workspaces you pick at creation, and it cannot be listed. The "
                    "choice cannot be edited later. Changing your mind means a new connection.",
                    PUBLIC,
                    PUBLIC_TITLE,
                ),
            ),
            Requirement(
                name="Capabilities (read, update, insert)",
                needed="required",
                detail=sourced(
                    "The create form asks for connection capabilities such as read "
                    "content, update content, and insert content. During OAuth, Notion "
                    "shows the user what those capabilities allow in their workspace.",
                    PUBLIC,
                    PUBLIC_TITLE,
                ),
            ),
            Requirement(
                name="Marketplace listing, logo, and review",
                needed="optional",
                detail=sourced(
                    "You do not have to list a public connection for OAuth to work. "
                    "A listing has its own draft: name, description, category, tags, "
                    "images, and logo, then a submit step. Notion reviews every listing.",
                    MARKET,
                    MARKET_TITLE,
                ),
            ),
            Requirement(
                name="Security assessment beyond Marketplace review",
                needed="conditional",
                detail=sourced(
                    "Notion's overview says public connections must undergo a security "
                    "review before being listed on the Marketplace.",
                    OVERVIEW,
                    OVERVIEW_TITLE,
                    note="The page does not describe a third-party audit, a price, or a review of unlisted connections.",
                ),
            ),
            Requirement(
                name="Paid Notion plan",
                needed="not_needed",
                detail=uncertain(
                    "The public-connection and authorization guides used here do not "
                    "say a paid Notion plan is required to create an OAuth connection.",
                    "Some API capabilities depend on the user's workspace plan. That is separate from creating the connection.",
                ),
            ),
        ],
        steps=[
            Step(
                title="Make a first API call with an internal connection",
                who="human",
                console_url=AUTH,
                console_label="Authorization guide",
                instructions=(
                    "If you only need your own workspace, create an internal connection "
                    "or a personal access token and call the API with that token. Skip "
                    "the public OAuth steps until a second workspace has to connect."
                ),
                detail=sourced(
                    "Internal connections use a static credential for one workspace. "
                    "Public connections use OAuth so each authorizing user gets their own token.",
                    AUTH,
                    AUTH_TITLE,
                ),
            ),
            Step(
                title="Create a public connection",
                who="human",
                console_url=PUBLIC,
                console_label="Public connections guide",
                instructions=(
                    "In the developer portal, open Build, then Public connections, then "
                    "Create new connection. Choose Any workspace if you may want the "
                    "Marketplace later. Add every redirect URI you will use. Select "
                    "capabilities that match the product. Submit the form."
                ),
                detail=sourced(
                    "The portal path in the guide is Build, then Public connections, "
                    "then Create new connection. Installation scope is fixed at creation.",
                    PUBLIC,
                    PUBLIC_TITLE,
                ),
            ),
            Step(
                title="Copy the client ID and client secret",
                who="human",
                console_url=PUBLIC,
                console_label="Public connections guide",
                instructions=(
                    "Open the Configuration tab. Copy the OAuth client ID and OAuth "
                    "client secret into a secret store. The token exchange sends them "
                    "as HTTP Basic auth, base64 of client_id:client_secret."
                ),
                detail=sourced(
                    "After creation, the OAuth client ID and OAuth client secret are on "
                    "the Configuration tab. Both are required to exchange the authorization code.",
                    PUBLIC,
                    PUBLIC_TITLE,
                ),
            ),
            Step(
                title="Send the user to the authorization URL",
                who="either",
                console_url=AUTH,
                console_label="Authorization guide",
                instructions=(
                    "Direct the user to the authorization URL from the Configuration "
                    "tab, or build https://api.notion.com/v1/oauth/authorize with "
                    "client_id, redirect_uri, response_type=code, and owner=user. "
                    "Add a state value and check it when the user returns."
                ),
                detail=sourced(
                    "The documented authorize URL is https://api.notion.com/v1/oauth/authorize. "
                    "Required parameters are client_id, redirect_uri, response_type=code, "
                    "and owner=user. state is optional and is how the docs suggest preventing CSRF.",
                    AUTH,
                    AUTH_TITLE,
                ),
            ),
            Step(
                title="Exchange the code, and store the refresh token",
                who="either",
                console_url=AUTH,
                console_label="Authorization guide",
                instructions=(
                    "POST the code to https://api.notion.com/v1/oauth/token with Basic "
                    "auth and JSON grant_type=authorization_code. Include redirect_uri "
                    "when you sent it on the authorize URL, or when more than one "
                    "redirect URI is configured. Store both the access token and the "
                    "refresh token. Refreshing returns a new pair."
                ),
                detail=sourced(
                    "The token response includes an access_token and a refresh_token. "
                    "A refresh grant (grant_type=refresh_token) returns a new access "
                    "token and a new refresh token. Send the refresh token to the same "
                    "https://api.notion.com/v1/oauth/token endpoint.",
                    AUTH,
                    AUTH_TITLE,
                    note="Older third-party pages say a Notion access token never expires and that there is no refresh token. The current authorization guide documents both tokens. Follow the current guide.",
                ),
            ),
            Step(
                title="Expect the page picker",
                who="human",
                console_url=PUBLIC,
                console_label="Public connections guide",
                instructions=(
                    "During consent the user chooses which pages the connection may "
                    "see, or duplicates a template if you offered one. Your first API "
                    "call should use a page they shared. A 404 on a page usually means "
                    "it was not shared, not that the token is bad."
                ),
                detail=sourced(
                    "Public connections use an OAuth page picker. The user grants "
                    "specific pages during authorization. The token acts as that user. "
                    "Each member of a workspace who wants to use the connection must "
                    "authorize it themselves.",
                    PUBLIC,
                    PUBLIC_TITLE,
                ),
            ),
            Step(
                title="List in the Marketplace only when you want discovery",
                who="human",
                console_url=MARKET,
                console_label="Marketplace listing guide",
                instructions=(
                    "From Listings, then Connections, start a draft and attach the "
                    "public connection. Submit when the listing is specific to the "
                    "integration. Track status on that page. Only an Any-workspace "
                    "connection can be submitted."
                ),
                detail=sourced(
                    "After you submit, Notion says to expect an email within 5–10 "
                    "business days. If they ask for changes, you can resubmit. "
                    "Approval puts the listing in the Marketplace.",
                    MARKET,
                    MARKET_TITLE,
                ),
            ),
        ],
        scopes=[
            ScopeItem(
                name="Read content",
                tier="capability",
                triggers_review="unknown",
                purpose="Read pages and databases the user shared.",
                detail=sourced(
                    "Read content is one of the capabilities the public-connection "
                    "form asks for. Notion shows the user a prompt describing the "
                    "connection's capabilities before they pick pages.",
                    PUBLIC,
                    PUBLIC_TITLE,
                ),
            ),
            ScopeItem(
                name="Update content",
                tier="capability",
                triggers_review="unknown",
                purpose="Edit content the user shared.",
                detail=sourced(
                    "Update content is listed alongside read content and insert content "
                    "as a capability you select when creating the connection.",
                    PUBLIC,
                    PUBLIC_TITLE,
                ),
            ),
            ScopeItem(
                name="Insert content",
                tier="capability",
                triggers_review="unknown",
                purpose="Create new content in the pages the user shared.",
                detail=sourced(
                    "Insert content is one of the example capabilities on the create form.",
                    PUBLIC,
                    PUBLIC_TITLE,
                ),
            ),
        ],
        scope_advice=uncertain(
            "Notion's public-connection docs describe capabilities, not a "
            "sensitive-versus-restricted scope tier like Google's. Whether a given "
            "capability triggers a review of an unlisted connection is not stated "
            "on the authorization, public-connection, or Marketplace pages used here.",
            "Select only the capabilities the product uses. The Marketplace path has a review; the unlisted OAuth path's review gate is the uncertain part below.",
        ),
        redirect_rules=sourced(
            "Send redirect_uri on the token request if the authorize URL included "
            "redirect_uri, or if the connection has more than one redirect URI saved "
            "under OAuth Domain & URIs. If there is exactly one saved redirect URI "
            "and you did not send redirect_uri on the authorize URL, the token request "
            "must not include redirect_uri.",
            TOKEN,
            TOKEN_TITLE,
            note="The authorization examples use an https redirect URI. Whether http://localhost is accepted is not stated on the create-token page.",
        ),
        agent_can_do=[
            WorkItem(
                task="Build the authorize URL and the token-exchange request.",
                detail=sourced(
                    "The authorize URL and the POST to https://api.notion.com/v1/oauth/token "
                    "are fully specified, including Basic auth with client_id:client_secret "
                    "and the refresh_token grant.",
                    AUTH,
                    AUTH_TITLE,
                ),
            ),
            WorkItem(
                task="Draft the Marketplace listing copy from the product's real behavior.",
                detail=sourced(
                    "A listing needs a name, description, category, tags, images, and "
                    "logo, and it is reviewed. The listing is separate from the connection.",
                    MARKET,
                    MARKET_TITLE,
                ),
            ),
            WorkItem(
                task="Handle a missing page as 'not shared' and tell the user how to add it.",
                detail=sourced(
                    "The user grants specific pages in the picker. Internal connections "
                    "instead need a member to share pages through Add connections. "
                    "The connection cannot see the rest of the workspace.",
                    PUBLIC,
                    PUBLIC_TITLE,
                    note="The internal-connection sharing sentence is on the same public-connections page, in the comparison with public connections.",
                ),
            ),
        ],
        human_must_do=[
            WorkItem(
                task="Create the connection in the developer portal while logged in.",
                detail=uncertain(
                    "The portal steps are documented, but this guide did not open the "
                    "form. Login, workspace choice, and the capabilities checkboxes "
                    "are a person's job until an unattended run is tested.",
                    "The docs call it the Developer portal and do not print a stable URL on the public-connections page.",
                ),
            ),
            WorkItem(
                task="Choose installation scope knowing it is permanent.",
                detail=sourced(
                    "Installation scope is set once. Selected workspaces only can never "
                    "be listed. Getting to the Marketplace later means creating a new "
                    "connection with Any workspace.",
                    PUBLIC,
                    PUBLIC_TITLE,
                ),
            ),
            WorkItem(
                task="Share a page in the picker during the first real install.",
                detail=sourced(
                    "Authorization includes the page picker. After approval, only that "
                    "user can use the connection in the workspace. Other members authorize separately.",
                    PUBLIC,
                    PUBLIC_TITLE,
                ),
            ),
            WorkItem(
                task="Submit a Marketplace listing and answer the review email.",
                detail=sourced(
                    "You submit from Listings, then Connections. Notion replies by email, "
                    "and the guide says to expect that within 5–10 business days.",
                    MARKET,
                    MARKET_TITLE,
                ),
            ),
        ],
        blockers=[
            Blocker(
                title="The authorization URL might be gated on a review",
                what_happens=sourced(
                    "Notion's authorization guide says the Authorization URL field "
                    "populates after a public connection is submitted for review.",
                    AUTH,
                    AUTH_TITLE,
                ),
                how_to_unstick=(
                    "After you create the connection, open the Configuration tab. If "
                    "the authorization URL is already filled in, you are not blocked "
                    "and you can run OAuth without a Marketplace listing. If the field "
                    "is empty, Notion is asking for a submission that the Marketplace "
                    "page describes as optional. Those two pages do not explain each "
                    "other. Use the internal-connection token for your own workspace "
                    "while you find out which submission the form wants."
                ),
                contact="The authorization guide does not name a support address for this field.",
            ),
            Blocker(
                title="The integration cannot see pages the user did not share",
                what_happens=sourced(
                    "During OAuth the user selects pages in the page picker, or duplicates "
                    "a template you configured. The access token only covers that grant. "
                    "A different member of the same workspace is not included.",
                    PUBLIC,
                    PUBLIC_TITLE,
                ),
                how_to_unstick=(
                    "In your empty state, link the user back to the authorization URL "
                    "and say which page to pick. Do not ask them to paste a page URL "
                    "and assume the token can open it."
                ),
                contact=None,
            ),
            Blocker(
                title="Wrong installation scope",
                what_happens=sourced(
                    "Selected workspaces only is not Marketplace-eligible, and the "
                    "scope cannot be changed after creation.",
                    PUBLIC,
                    PUBLIC_TITLE,
                ),
                how_to_unstick=(
                    "Create a new public connection with Any workspace. Update the "
                    "client ID and secret. Existing installs of the old connection "
                    "do not move over."
                ),
                contact=None,
            ),
            Blocker(
                title="redirect_uri rejected at token exchange",
                what_happens=sourced(
                    "redirect_uri is required on the token call when it was present on "
                    "the authorize URL, or when more than one redirect URI is saved. "
                    "It is forbidden on the token call when a single saved URI was used "
                    "and the authorize URL omitted the parameter.",
                    TOKEN,
                    TOKEN_TITLE,
                ),
                how_to_unstick=(
                    "Pick one pattern and stick to it. The simplest is one HTTPS "
                    "redirect URI in the portal, the same URI on the authorize URL, "
                    "and the same URI in the token POST."
                ),
                contact=None,
            ),
        ],
        composio=ComposioContext(
            managed=sourced(
                "Notion is on Composio's managed OAuth list under the slug NOTION. "
                "Managed auth is enough when Composio's scopes and consent-screen "
                "branding are acceptable.",
                MANAGED,
                MANAGED_TITLE,
            ),
            custom_app=sourced(
                "A custom Notion connection registers the redirect URI from the "
                "Composio dashboard. The programmatic docs name "
                "https://backend.composio.dev/api/v3/toolkits/auth/callback and a "
                "legacy default of https://backend.composio.dev/api/v1/auth-apps/add "
                "for some toolkits.",
                PROGRAMMATIC,
                PROGRAMMATIC_TITLE,
            ),
        ),
        sources=[
            {"title": AUTH_TITLE, "url": AUTH},
            {"title": PUBLIC_TITLE, "url": PUBLIC},
            {"title": MARKET_TITLE, "url": MARKET},
            {"title": TOKEN_TITLE, "url": TOKEN},
            {"title": OVERVIEW_TITLE, "url": OVERVIEW},
            {"title": MANAGED_TITLE, "url": MANAGED},
            {"title": PROGRAMMATIC_TITLE, "url": PROGRAMMATIC},
        ],
        research_log=[
            ResearchEvent(
                kind="note",
                detail=(
                    "Curated from Notion's public docs and Composio's auth docs on "
                    "20 Oct 2026. No developer-portal login. The Authorization URL "
                    "caption and the Marketplace 'listing is optional' sentence are "
                    "both kept, because they do not say the same thing."
                ),
            )
        ],
    )
