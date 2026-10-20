"""HubSpot, the middle case.

Judgment: difficulty is Medium. You can create an app and complete OAuth
without waiting for Marketplace review, but distribution is gated. Until the
Acceptable Use Policy is signed, installs stay on developer test accounts.
Until HubSpot's Ecosystem Quality team lists the app, installs are capped at 25,
and the user has to type that they accept the risk.

HubSpot publishes two OAuth guides, one for legacy public apps and one for the
newer developer platform. The steps below follow the newer platform pages.
Where a fact was only read on the legacy page, the claim says so.

No HubSpot login was attempted. Checked 20 Oct 2026.
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

OAUTH = "https://developers.hubspot.com/docs/apps/developer-platform/build-apps/authentication/oauth/working-with-oauth"
OAUTH_TITLE = "Working with OAuth (developer platform)"
LEGACY = "https://developers.hubspot.com/docs/guides/apps/authentication/working-with-oauth"
LEGACY_TITLE = "Working with OAuth (legacy public apps)"
MANAGE = "https://developers.hubspot.com/docs/apps/developer-platform/build-apps/manage-apps-in-hubspot"
MANAGE_TITLE = "Manage apps in HubSpot"
LISTING = "https://developers.hubspot.com/docs/apps/developer-platform/list-apps/listing-your-app/app-marketplace-listing-requirements"
LISTING_TITLE = "App listing requirements"
LISTING_HOW = "https://developers.hubspot.com/docs/apps/developer-platform/list-apps/listing-your-app/listing-your-app"
LISTING_HOW_TITLE = "Listing your app"
MANAGED = "https://docs.composio.dev/toolkits/managed-auth"
MANAGED_TITLE = "Managed OAuth apps"
PROGRAMMATIC = "https://docs.composio.dev/docs/authentication/programmatic-auth-configs"
PROGRAMMATIC_TITLE = "Programmatic auth configs"

CHECKED = date(2026, 10, 20)


def build() -> Guide:
    return Guide(
        slug="hubspot",
        app_name="HubSpot",
        aliases=["hubspot crm"],
        homepage_url="https://www.hubspot.com",
        docs_url=OAUTH,
        summary=(
            "HubSpot OAuth is self-serve up to a point. You need a developer account, "
            "an app, and an installer who is a Super Admin or has Marketplace Access. "
            "You can test before review. You cannot install into ordinary customer "
            "accounts until the Acceptable Use Policy is signed, and you cannot pass "
            "25 installs until the app is reviewed and listed. Customers see an "
            "unverified-app warning and must type that they accept the risk."
        ),
        last_checked=CHECKED,
        generated_by="curated",
        verdict=Verdict(
            difficulty="medium",
            review_required="conditional",
            difficulty_reason=sourced(
                "Until the Acceptable Use Policy is signed, an OAuth marketplace app "
                "can only be installed in developer test accounts. Until the Ecosystem "
                "Quality team reviews the app and it is listed, installs are limited "
                "to 25. An unlisted app shows a warning, and the user must type that "
                "they accept the risk before connecting.",
                MANAGE,
                MANAGE_TITLE,
            ),
            time_to_first_test=sourced(
                "Setup is: create an app, take the client ID and client secret from "
                "the Auth page, and send the user to HubSpot's authorize URL with "
                "client_id, redirect_uri, and scope. After consent, the redirect "
                "carries a code that you exchange for tokens.",
                OAUTH,
                OAUTH_TITLE,
                note="HubSpot does not publish how long app creation takes, and this guide did not time a logged-in run.",
            ),
            time_to_production=uncertain(
                "HubSpot's listing pages say the Ecosystem Quality team reviews "
                "submissions manually and follows up by email. They do not publish "
                "a turnaround time on the listing-requirements page or the listing guide.",
                "Do not quote a number of days. The cap of 25 installs is the production limit you can plan around before that email arrives.",
            ),
            review_summary=sourced(
                "Marketplace review is what removes the 25-install cap. Testing does "
                "not require the app to be listed. OAuth marketplace apps do not use "
                "an allowlist of accounts. Begin publishing on the Distribution tab "
                "and sign the Acceptable Use Policy before you install outside developer test accounts.",
                MANAGE,
                MANAGE_TITLE,
            ),
        ),
        requirements=[
            Requirement(
                name="HubSpot developer account and an app",
                needed="required",
                detail=sourced(
                    "The OAuth guide starts by creating an app. The client ID and "
                    "client secret are on the app's Auth page.",
                    OAUTH,
                    OAUTH_TITLE,
                ),
            ),
            Requirement(
                name="Installer is a Super Admin, or has Marketplace Access",
                needed="required",
                detail=sourced(
                    "The user who installs the app must be a Super Admin or have "
                    "HubSpot Marketplace Access permissions. Any app meant for multiple "
                    "HubSpot accounts, or for the Marketplace, must use OAuth.",
                    OAUTH,
                    OAUTH_TITLE,
                ),
            ),
            Requirement(
                name="HTTPS redirect URL",
                needed="required",
                detail=sourced(
                    "The redirect URL must use https in production. http is allowed "
                    "when testing with localhost. IP addresses are not supported; use a domain.",
                    OAUTH,
                    OAUTH_TITLE,
                ),
            ),
            Requirement(
                name="Required scopes, and optional scopes for tiers you can live without",
                needed="required",
                detail=sourced(
                    "Scopes you mark required in the app settings must be sent in the "
                    "scope parameter or the authorization page errors. Optional scopes "
                    "are dropped if the HubSpot account the user picks does not include "
                    "that product. The app has to check which scopes were actually granted.",
                    OAUTH,
                    OAUTH_TITLE,
                ),
            ),
            Requirement(
                name="Signed Acceptable Use Policy",
                needed="conditional",
                detail=sourced(
                    "On the Distribution tab, Begin publishing asks you to sign the "
                    "Acceptable Use Policy. Until it is signed, the app cannot be "
                    "installed in accounts other than developer test accounts.",
                    MANAGE,
                    MANAGE_TITLE,
                ),
            ),
            Requirement(
                name="Marketplace listing",
                needed="optional",
                detail=sourced(
                    "A listing must use OAuth as its only authorization method, request "
                    "only the scopes it needs, and have at least three active installs "
                    "on unique production accounts that are not affiliated with you and "
                    "that showed successful app activity in the past 30 days.",
                    LISTING,
                    LISTING_TITLE,
                ),
            ),
            Requirement(
                name="Security assessment",
                needed="not_needed",
                detail=uncertain(
                    "The listing requirements describe a manual Ecosystem Quality review, "
                    "not a third-party security assessment like Google's CASA. This guide "
                    "did not find a CASA-style requirement on the pages it used.",
                    "Ask HubSpot if a customer security questionnaire is required for your category. Do not assume there is none.",
                ),
            ),
            Requirement(
                name="Paid HubSpot subscription for the developer",
                needed="not_needed",
                detail=uncertain(
                    "The OAuth and listing pages used here do not say the developer must "
                    "buy a paid HubSpot subscription to create an OAuth app. The customer's "
                    "account tier does decide which optional scopes they can grant.",
                    "Use a developer test account for the first install.",
                ),
            ),
        ],
        steps=[
            Step(
                title="Create a developer account and an app on the current platform",
                who="human",
                console_url=OAUTH,
                console_label="Developer platform OAuth guide",
                instructions=(
                    "Create the app in a HubSpot developer account, using the developer "
                    "platform docs rather than the legacy public-app guide, unless you "
                    "already have a legacy app. Open the Auth page and copy the client "
                    "ID and client secret."
                ),
                detail=sourced(
                    "HubSpot's older OAuth guide says it applies to legacy public apps "
                    "and points developers at a different article for apps built on the "
                    "new developer platform.",
                    LEGACY,
                    LEGACY_TITLE,
                    note="Create the app on the platform that article describes, then take the client ID and secret from that app's Auth page.",
                ),
            ),
            Step(
                title="Set the redirect URL and the scopes",
                who="human",
                console_url=OAUTH,
                console_label="Working with OAuth",
                instructions=(
                    "Add an https redirect URL. For a local test, http://localhost is "
                    "allowed; a raw IP is not. Mark a scope required only if every "
                    "customer account can grant it. Put tier-specific products in "
                    "optional scopes so a free account can still install."
                ),
                detail=sourced(
                    "Required scopes have to be included in the authorization URL. "
                    "Optional scopes are removed automatically when the selected account "
                    "does not have that tool. Check the token afterwards to see what you got.",
                    OAUTH,
                    OAUTH_TITLE,
                ),
            ),
            Step(
                title="Send a test user through the authorize URL",
                who="either",
                console_url=OAUTH,
                console_label="Working with OAuth",
                instructions=(
                    "Build https://app.hubspot.com/oauth/authorize with client_id, "
                    "a space-separated scope list, and redirect_uri. To target one "
                    "account, put its ID in the path: /oauth/{accountId}/authorize. "
                    "The installer must be a Super Admin or have Marketplace Access. "
                    "Your redirect receives ?code=."
                ),
                detail=sourced(
                    "The documented any-account URL is "
                    "https://app.hubspot.com/oauth/authorize and the account-specific "
                    "form is https://app.hubspot.com/oauth/{accountId}/authorize. "
                    "Both take client_id, scope, and redirect_uri. state is optional "
                    "and is echoed back.",
                    OAUTH,
                    OAUTH_TITLE,
                ),
            ),
            Step(
                title="Exchange the code before you look for a Connected App",
                who="either",
                console_url=LEGACY,
                console_label="Legacy OAuth guide",
                instructions=(
                    "Exchange the code with the client secret for an access token and "
                    "a refresh token. Call one API method with the access token. When "
                    "it expires, use the refresh token. The app does not show up as a "
                    "Connected App in the account until those first tokens exist."
                ),
                detail=sourced(
                    "The legacy OAuth guide says the app will not appear as a Connected "
                    "App until you generate the refresh token and the initial access "
                    "token. Access tokens expire; the refresh token gets a new one. "
                    "The token's scopes are the ones requested, not the installing "
                    "user's own permission limits.",
                    LEGACY,
                    LEGACY_TITLE,
                    note="The lifetime in seconds is not stated on this page. Do not hard-code a guess.",
                ),
            ),
            Step(
                title="Sign the Acceptable Use Policy before real accounts install",
                who="human",
                console_url=MANAGE,
                console_label="Manage apps",
                instructions=(
                    "On the Distribution tab, click Begin publishing and sign the "
                    "Acceptable Use Policy. You can close the listing panel if you are "
                    "not ready to submit a Marketplace listing. Use the sample install "
                    "URL to install into an account. Expect the unverified warning."
                ),
                detail=sourced(
                    "Signing the Acceptable Use Policy is what allows installs beyond "
                    "developer test accounts. Until the app is reviewed and listed, "
                    "you are limited to 25 installs, and the user must type that they "
                    "accept the risk on the unverified-app dialog.",
                    MANAGE,
                    MANAGE_TITLE,
                ),
            ),
            Step(
                title="List the app when you need more than 25 installs",
                who="human",
                console_url=LISTING,
                console_label="Listing requirements",
                instructions=(
                    "Get at least three active installs on unaffiliated production "
                    "accounts. Use OAuth only. Cut scopes you do not need. Fill the "
                    "listing with integration-specific copy and live public URLs. "
                    "Submit as a Super Admin. Provide testing credentials when HubSpot asks."
                ),
                detail=sourced(
                    "Listing requirements include a unique app, one public app ID and "
                    "OAuth client ID, OAuth as the only auth method, least-privilege "
                    "scopes, and three active unaffiliated production installs with "
                    "successful activity in the past 30 days. The Ecosystem Quality "
                    "team rejects listings that miss these.",
                    LISTING,
                    LISTING_TITLE,
                ),
            ),
        ],
        scopes=[
            ScopeItem(
                name="crm.objects.contacts.read",
                tier="required or optional",
                triggers_review="conditional",
                purpose="Read contacts. A common first scope for a CRM agent.",
                detail=uncertain(
                    "The OAuth guides show sample scope values such as contacts and "
                    "automation, and they say the full list lives in the scopes reference. "
                    "This guide did not re-check the current string for contacts-read "
                    "against that reference, so treat crm.objects.contacts.read as a "
                    "likely name to confirm in the Auth settings of your app.",
                    "Copy the scope strings from your app's Auth page, not from memory.",
                ),
            ),
            ScopeItem(
                name="Required scopes",
                tier="required",
                triggers_review="conditional",
                purpose="Permissions every installing account must be able to grant.",
                detail=sourced(
                    "If a required scope is missing from the authorize URL, the "
                    "authorization page shows an error. If the account cannot use a "
                    "required scope, the user also gets an error and cannot install.",
                    OAUTH,
                    OAUTH_TITLE,
                ),
            ),
            ScopeItem(
                name="Optional scopes",
                tier="optional",
                triggers_review="unknown",
                purpose="Permissions that should disappear on accounts without that HubSpot product.",
                detail=sourced(
                    "Optional scopes are dropped when the selected account does not "
                    "have the tool, for example a Content Hub Enterprise scope on a "
                    "free account. Read the granted scopes from the token.",
                    OAUTH,
                    OAUTH_TITLE,
                ),
            ),
        ],
        scope_advice=sourced(
            "Put only scopes you need on the app. Required scopes are a promise that "
            "every customer can grant them. Use optional_scope for anything that depends "
            "on a paid HubSpot product, and handle the case where it was not granted.",
            OAUTH,
            OAUTH_TITLE,
        ),
        redirect_rules=sourced(
            "In production the redirect URL must be https. http is allowed for "
            "localhost testing. IP addresses are not accepted; use a hostname. The "
            "redirect_uri on the authorize URL has to be the one configured on the app.",
            OAUTH,
            OAUTH_TITLE,
        ),
        agent_can_do=[
            WorkItem(
                task="Build the authorize URL and separate required scopes from optional ones.",
                detail=sourced(
                    "Required scopes go in scope, space-separated. Optional scopes go "
                    "in optional_scope. state is returned unchanged on the redirect.",
                    OAUTH,
                    OAUTH_TITLE,
                ),
            ),
            WorkItem(
                task="Draft listing copy that is about the integration, and a scope list that matches it.",
                detail=sourced(
                    "Listing content has to describe the integration, not the product "
                    "in general. Every URL in the listing must be a live public page. "
                    "Extra scopes are a reason for rejection.",
                    LISTING,
                    LISTING_TITLE,
                ),
            ),
            WorkItem(
                task="After install, read the granted scopes and hide features the account did not allow.",
                detail=sourced(
                    "Optional scopes may be missing from the token. The access token "
                    "also does not shrink to the installing user's personal permissions: "
                    "a user who can only see their own contacts can still grant a token "
                    "that can read all contacts.",
                    LEGACY,
                    LEGACY_TITLE,
                    note="The optional-scope drop is on the developer-platform OAuth page as well. This claim cites the legacy page because that is where the permission-versus-scope warning was read.",
                ),
            ),
        ],
        human_must_do=[
            WorkItem(
                task="Create the developer account and the app.",
                detail=uncertain(
                    "The docs assume you can create an app in a developer account. "
                    "This guide did not open that signup or the app form.",
                    "Signup URLs change. Start from the developer-platform OAuth guide rather than a remembered link.",
                ),
            ),
            WorkItem(
                task="Sign the Acceptable Use Policy.",
                detail=sourced(
                    "Begin publishing on the Distribution tab includes signing the "
                    "Acceptable Use Policy. Without that signature, installs stay on "
                    "developer test accounts.",
                    MANAGE,
                    MANAGE_TITLE,
                ),
            ),
            WorkItem(
                task="Install with a Super Admin, and type the unverified-app confirmation.",
                detail=sourced(
                    "Before the app is verified, the install flow shows a warning and "
                    "the user has to type that they accept the risk. Signing the "
                    "Acceptable Use Policy is what allows installs outside developer test accounts.",
                    MANAGE,
                    MANAGE_TITLE,
                ),
            ),
            WorkItem(
                task="Collect three unaffiliated production installs before you ask to be listed.",
                detail=sourced(
                    "A listing needs at least three active unique installs: production "
                    "accounts not affiliated with your organization, with successful "
                    "OAuth API activity or signed webhook or extension requests in the past 30 days.",
                    LISTING,
                    LISTING_TITLE,
                ),
            ),
        ],
        blockers=[
            Blocker(
                title="Install stuck on developer test accounts",
                what_happens=sourced(
                    "Until the Acceptable Use Policy is signed, the app cannot be "
                    "installed in accounts other than developer test accounts.",
                    MANAGE,
                    MANAGE_TITLE,
                ),
                how_to_unstick=(
                    "Open the Distribution tab, Begin publishing, and sign the policy. "
                    "You can leave the Marketplace listing draft closed and still use "
                    "the sample install URL."
                ),
                contact=None,
            ),
            Blocker(
                title="The 25-install cap",
                what_happens=sourced(
                    "Until the Ecosystem Quality team reviews the app and it is listed, "
                    "installs are limited to 25. After publication the limit is lifted.",
                    MANAGE,
                    MANAGE_TITLE,
                ),
                how_to_unstick=(
                    "Use the 25 on real design partners and count them toward the three "
                    "unaffiliated active installs the listing requires. Then submit the listing."
                ),
                contact="The listing guide says the Ecosystem Quality team follows up by email.",
            ),
            Blocker(
                title="Customer cannot finish the consent screen",
                what_happens=sourced(
                    "Install fails if the user is not a Super Admin and does not have "
                    "Marketplace Access, or if the account cannot use a scope you marked required.",
                    OAUTH,
                    OAUTH_TITLE,
                ),
                how_to_unstick=(
                    "Ask the customer for a Super Admin install. Move paid-product "
                    "scopes to optional_scope so smaller accounts are not rejected."
                ),
                contact=None,
            ),
            Blocker(
                title="The app never appears under Connected Apps",
                what_happens=sourced(
                    "The legacy OAuth guide says the app does not appear as a Connected "
                    "App until the first access token and refresh token have been created.",
                    LEGACY,
                    LEGACY_TITLE,
                ),
                how_to_unstick=(
                    "Finish the code exchange on your server. Reloading the consent "
                    "screen is not enough. Then look again in the account."
                ),
                contact=None,
            ),
            Blocker(
                title="Two different HubSpot app platforms",
                what_happens=sourced(
                    "The older working-with-OAuth page says it pertains to legacy public "
                    "apps and points to a different article for apps on the new developer platform.",
                    LEGACY,
                    LEGACY_TITLE,
                ),
                how_to_unstick=(
                    "Match the guide to the app you created. If you are listing the app, "
                    "read the current platform-version rule on the listing-requirements page "
                    "before you build on an older project type."
                ),
                contact=None,
            ),
        ],
        composio=ComposioContext(
            managed=sourced(
                "HubSpot is on Composio's managed OAuth list under the slug HUBSPOT. "
                "Use managed auth when the default scopes and a Composio consent screen "
                "are fine.",
                MANAGED,
                MANAGED_TITLE,
            ),
            custom_app=sourced(
                "A custom HubSpot app should register the redirect URI from the Composio "
                "dashboard. The programmatic docs name "
                "https://backend.composio.dev/api/v3/toolkits/auth/callback, and some "
                "toolkits still use https://backend.composio.dev/api/v1/auth-apps/add.",
                PROGRAMMATIC,
                PROGRAMMATIC_TITLE,
            ),
        ),
        sources=[
            {"title": OAUTH_TITLE, "url": OAUTH},
            {"title": LEGACY_TITLE, "url": LEGACY},
            {"title": MANAGE_TITLE, "url": MANAGE},
            {"title": LISTING_TITLE, "url": LISTING},
            {"title": LISTING_HOW_TITLE, "url": LISTING_HOW},
            {"title": MANAGED_TITLE, "url": MANAGED},
            {"title": PROGRAMMATIC_TITLE, "url": PROGRAMMATIC},
        ],
        research_log=[
            ResearchEvent(
                kind="note",
                detail=(
                    "Curated on 20 Oct 2026 from HubSpot's developer-platform docs, "
                    "the legacy OAuth page, and Composio's auth docs. No developer-account "
                    "login. Review duration is uncertain because HubSpot does not publish one."
                ),
            )
        ],
    )
