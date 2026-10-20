"""Slack, the easy install and the long Marketplace.

Judgment: difficulty is Easy if the developer only needs to install the app
on workspaces they can reach. It becomes a multi-week project only when they
submit to the Slack Marketplace. Review is conditional for that reason.

Claims are sourced from Slack's public docs on 20 Oct 2026. No Slack app was created.
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

OAUTH = "https://docs.slack.dev/authentication/installing-with-oauth"
OAUTH_TITLE = "Installing via OAuth"
REVIEW = "https://docs.slack.dev/slack-marketplace/slack-marketplace-review-guide"
REVIEW_TITLE = "Slack Marketplace review process"
RULES = "https://docs.slack.dev/slack-marketplace/slack-marketplace-app-guidelines-and-requirements"
RULES_TITLE = "Submission guidelines and requirements"
MANAGED = "https://docs.composio.dev/toolkits/managed-auth"
MANAGED_TITLE = "Managed OAuth apps"
PROGRAMMATIC = "https://docs.composio.dev/docs/authentication/programmatic-auth-configs"
PROGRAMMATIC_TITLE = "Programmatic auth configs"

CHECKED = date(2026, 10, 20)


def build() -> Guide:
    return Guide(
        slug="slack",
        app_name="Slack",
        aliases=["slack app"],
        homepage_url="https://slack.com",
        docs_url=OAUTH,
        summary=(
            "Creating a Slack app and installing it with OAuth is a short, self-serve "
            "flow. Slack's install docs do not put a review in that path. The Slack "
            "Marketplace is a different project: 10 active workspaces before you can "
            "submit, then up to 10 business days of preliminary review and up to "
            "10 weeks of functional review for a new listing."
        ),
        last_checked=CHECKED,
        generated_by="curated",
        verdict=Verdict(
            difficulty="easy",
            review_required="conditional",
            difficulty_reason=sourced(
                "A Slack app gets its token from a three-step OAuth install: request "
                "scopes, wait for a user to approve, and exchange a short-lived code "
                "for an access token. That install guide does not include a review.",
                OAUTH,
                OAUTH_TITLE,
                note="Marketplace review exists, but it is documented on a separate page and only applies if you want a listing.",
            ),
            time_to_first_test=sourced(
                "The authorization code Slack returns is temporary and expires after "
                "ten minutes. You exchange it at oauth.v2.access with the client ID "
                "and client secret. Bot scopes go in scope, user scopes in user_scope.",
                OAUTH,
                OAUTH_TITLE,
                note="Slack does not publish how many minutes the app-creation form takes.",
            ),
            time_to_production=sourced(
                "Marketplace preliminary review takes up to 10 business days. Functional "
                "review takes up to 10 weeks for a new submission and 6 weeks for changes "
                "to an already published app. Slack will not expedite a review to hit a launch date.",
                REVIEW,
                REVIEW_TITLE,
                note="You can install and run the app without a Marketplace listing. These numbers are the listing path only.",
            ),
            review_summary=sourced(
                "Before Slack will accept a Marketplace submission, the app must be "
                "fully functional and already installed on 10 or more active workspaces "
                "(used in the past 28 days). Apps that are still in private beta or not "
                "fully tested are sent back. Once listed, the live app's configuration, "
                "features, and scopes are locked until you resubmit.",
                REVIEW,
                REVIEW_TITLE,
            ),
        ),
        requirements=[
            Requirement(
                name="Slack app and client secret",
                needed="required",
                detail=sourced(
                    "The install flow needs the app's client ID from the App Management "
                    "page, and the token exchange also needs the client secret. The secret "
                    "is how you prove you hold both the temporary code and the app.",
                    OAUTH,
                    OAUTH_TITLE,
                ),
            ),
            Requirement(
                name="HTTPS redirect URL",
                needed="required",
                detail=sourced(
                    "The redirect_uri must use HTTPS. Slack's guide marks http URLs as "
                    "invalid, including http on another host or port. A redirect URL "
                    "cannot contain a # anchor.",
                    OAUTH,
                    OAUTH_TITLE,
                    note="This page does not describe a localhost exception.",
                ),
            ),
            Requirement(
                name="At least one scope you can demo",
                needed="required",
                detail=sourced(
                    "You choose scopes while building the app, and those scopes are what "
                    "the user approves at install. Marketplace review will only approve "
                    "scopes whose features already work and can be tested or seen in a demo.",
                    REVIEW,
                    REVIEW_TITLE,
                ),
            ),
            Requirement(
                name="Privacy policy, home page, and Marketplace listing",
                needed="conditional",
                detail=sourced(
                    "A Marketplace submission reviews listing information, documentation, "
                    "links, and the reason for each scope. Direct install, if you enable "
                    "it, must 302 to a fully qualified slack.com/oauth/v2/authorize URL.",
                    RULES,
                    RULES_TITLE,
                    note="An unlisted app that you install yourself does not go through this checklist.",
                ),
            ),
            Requirement(
                name="Ten active workspace installs",
                needed="conditional",
                detail=sourced(
                    "Marketplace submission is blocked until the app is installed on 10 "
                    "or more active workspaces. An active workspace is one used in the "
                    "past 28 days. Security and compliance partners on the Discovery API "
                    "are the documented exception.",
                    REVIEW,
                    REVIEW_TITLE,
                ),
            ),
            Requirement(
                name="Security assessment",
                needed="not_needed",
                detail=uncertain(
                    "The Marketplace review guide describes a product review, not a "
                    "third-party security assessment like Google's CASA. A separate "
                    "Slack security-review page exists for Marketplace terms; this guide "
                    "did not treat that as a CASA-style audit.",
                    "Read the current Marketplace security terms before you promise a customer there is no assessment.",
                ),
            ),
            Requirement(
                name="Paid Slack plan",
                needed="not_needed",
                detail=uncertain(
                    "The OAuth install docs do not say you need a paid Slack plan to "
                    "create an app or complete OAuth. Some scopes and product surfaces "
                    "behave differently on the free plan, which is a separate question.",
                    "Check the scope you want against the current method docs.",
                ),
            ),
        ],
        steps=[
            Step(
                title="Create the app",
                who="human",
                console_url="https://api.slack.com/apps",
                console_label="Your Apps",
                instructions=(
                    "Open Your Apps and create an app from scratch or from a manifest. "
                    "You will land in the app settings. The client ID and client secret "
                    "are on Basic Information."
                ),
                detail=uncertain(
                    "The OAuth docs call this the App Management page. This guide did "
                    "not open api.slack.com/apps while logged in, so the exact field "
                    "order on the create form was not checked.",
                    "The dashboard link is the public app list. Expect a Slack login.",
                ),
            ),
            Step(
                title="Add a bot scope and an HTTPS redirect URL",
                who="human",
                console_url=OAUTH,
                console_label="OAuth install guide",
                instructions=(
                    "Under OAuth & Permissions, add the bot scopes you need and a "
                    "redirect URL that is HTTPS and has no hash fragment. If you set "
                    "more than one redirect URL, your code must send the same "
                    "redirect_uri on the authorize request and on the token exchange."
                ),
                detail=sourced(
                    "When several redirect URLs are configured, omitting redirect_uri "
                    "uses the first one in the list. Sending different values on the "
                    "authorize and access steps returns bad_redirect_uri. The redirect_uri "
                    "must match a configured URL or a subdirectory of one.",
                    OAUTH,
                    OAUTH_TITLE,
                ),
            ),
            Step(
                title="Install to your own workspace",
                who="human",
                console_url="https://api.slack.com/apps",
                console_label="Your Apps",
                instructions=(
                    "Install the app to a workspace you admin. Approve the consent "
                    "screen. Exchange the code within ten minutes. Store the bot token "
                    "(xoxb-) and, only if you asked for them, the user token under authed_user."
                ),
                detail=sourced(
                    "oauth.v2.access returns the bot access token, the granted scope "
                    "list, the bot user ID, and the team ID. User tokens, when requested, "
                    "come back on authed_user. The code expires after ten minutes.",
                    OAUTH,
                    OAUTH_TITLE,
                ),
            ),
            Step(
                title="Make one API call with the bot token",
                who="either",
                console_url=OAUTH,
                console_label="OAuth install guide",
                instructions=(
                    "Call a method that matches a scope you were granted, such as "
                    "posting a message if you requested chat:write. If you marked some "
                    "scopes optional, handle missing_scope when the installer declined them."
                ),
                detail=sourced(
                    "Optional scopes are chosen by the installer. The app must still "
                    "work for features that do not need the declined scopes, and it "
                    "should read the granted scopes from the oauth.v2.access response.",
                    OAUTH,
                    OAUTH_TITLE,
                ),
            ),
            Step(
                title="Distribute only as far as you need",
                who="human",
                console_url=REVIEW,
                console_label="Marketplace review guide",
                instructions=(
                    "Share the install link with other workspaces when you are ready "
                    "for more users. Do not submit to the Marketplace until the app is "
                    "installed on at least 10 active workspaces and you have tested "
                    "install, onboarding, use, and uninstall on a workspace that is "
                    "not your development workspace."
                ),
                detail=sourced(
                    "Slack reviews the app the way a new customer would, including "
                    "uninstall. You must provide a way for the reviewer to install it "
                    "themselves. Slack cannot access your Slack workspaces, even ones "
                    "you made for testing.",
                    REVIEW,
                    REVIEW_TITLE,
                ),
            ),
            Step(
                title="Submit to the Marketplace only if you want a listing",
                who="human",
                console_url=REVIEW,
                console_label="Marketplace review guide",
                instructions=(
                    "Submit from Submit to the Slack Marketplace on the app config page. "
                    "Explain every scope as how your app uses it, not as a definition of "
                    "the scope. Include a video of install, setup, use, and uninstall. "
                    "Provide test-account credentials for any external service. Fix "
                    "automated-check failures before you submit. Resubmitting during "
                    "preliminary review resets your place in that queue."
                ),
                detail=sourced(
                    "Preliminary feedback generally takes up to 10 business days, and "
                    "each resubmit in that stage resets the queue. Functional review "
                    "takes up to 10 weeks for a new app. Feedback arrives in the "
                    "submission flow and by email to the address you entered.",
                    REVIEW,
                    REVIEW_TITLE,
                ),
            ),
        ],
        scopes=[
            ScopeItem(
                name="chat:write",
                tier="bot",
                triggers_review="conditional",
                purpose="Post messages as the bot. A normal least-privilege starting point.",
                detail=sourced(
                    "Bot scopes are requested with the scope query parameter on "
                    "https://slack.com/oauth/v2/authorize. User scopes use user_scope. "
                    "The granted set is returned on the token response.",
                    OAUTH,
                    OAUTH_TITLE,
                ),
            ),
            ScopeItem(
                name="channels:history (and other *:history user scopes)",
                tier="broad",
                triggers_review="conditional",
                purpose="Read channel history. Easy to over-request.",
                detail=sourced(
                    "Slack says it is unlikely to approve broad access to workspace "
                    "message and file data, such as user-token *:history scopes, "
                    "without a clear use case it can test, such as real-time search "
                    "or an MCP server.",
                    RULES,
                    RULES_TITLE,
                ),
            ),
            ScopeItem(
                name="admin.*",
                tier="admin",
                triggers_review="yes",
                purpose="Workspace administration. Not a normal bot scope.",
                detail=sourced(
                    "Slack says it is unlikely to approve admin.* scopes for Marketplace "
                    "apps that are not in the partner program. The review guide also "
                    "lists admin.* among scopes that should not be requested.",
                    RULES,
                    RULES_TITLE,
                ),
            ),
            ScopeItem(
                name="Sign in with Slack user scopes",
                tier="identity",
                triggers_review="conditional",
                purpose="Identify the user. Must be a separate OAuth flow from other user scopes.",
                detail=sourced(
                    "Combining Sign in with Slack user scopes with non-Sign-in-with-Slack "
                    "scopes in the same OAuth flow is a scope conflict. Each set has to "
                    "be requested in its own flow.",
                    OAUTH,
                    OAUTH_TITLE,
                ),
            ),
        ],
        scope_advice=sourced(
            "Request the minimum scopes, prefer a bot token, and do not include scopes "
            "for features you have not built. There is no way to remove a scope from an "
            "existing token without revoking the token. Later installs add scopes; they "
            "do not replace them.",
            OAUTH,
            OAUTH_TITLE,
            note="The 'no future scopes' rule for Marketplace submissions is on the review guide. Token revocation and additive installs are on this OAuth page.",
        ),
        redirect_rules=sourced(
            "Redirect URLs must be HTTPS and must not contain a # anchor. The "
            "redirect_uri you send must match a configured redirect URL or be a "
            "subdirectory of one. With multiple redirect URLs, send the same "
            "redirect_uri on the authorize step and the oauth.v2.access step. "
            "Slack's examples mark http:// URLs as bad, including a different port.",
            OAUTH,
            OAUTH_TITLE,
        ),
        agent_can_do=[
            WorkItem(
                task="Draft the reason for each scope in the form Slack asks for: how the app uses it.",
                detail=sourced(
                    "Marketplace guidelines say to explain how the app uses each scope, "
                    "not what the scope does. Scopes for unbuilt features are rejected, "
                    "and reviewers can only approve functionality they can test or watch.",
                    RULES,
                    RULES_TITLE,
                ),
            ),
            WorkItem(
                task="Draft the install-to-uninstall demo script for the reviewer.",
                detail=sourced(
                    "A new submission should include a video of the full installation "
                    "and OAuth flow, setup, end-to-end use, and uninstallation.",
                    REVIEW,
                    REVIEW_TITLE,
                ),
            ),
            WorkItem(
                task="Turn the scope list into the authorize URL.",
                detail=sourced(
                    "The authorize URL is https://slack.com/oauth/v2/authorize with "
                    "client_id, scope for bot scopes, and user_scope for user scopes. "
                    "GovSlack uses slack-gov.com.",
                    OAUTH,
                    OAUTH_TITLE,
                ),
            ),
        ],
        human_must_do=[
            WorkItem(
                task="Create the Slack app while logged into the workspace that will own it.",
                detail=uncertain(
                    "App creation is behind Slack login. This guide did not open the "
                    "create-app form, so it does not claim a particular field list.",
                    "An agent can prepare the manifest JSON. A person still has to submit it in the dashboard until that is tested.",
                ),
            ),
            WorkItem(
                task="Install the app and approve the consent screen.",
                detail=sourced(
                    "A user in the workspace has to approve the requested scopes. "
                    "The app then exchanges the code. Slack does not send the token "
                    "directly to the app after approval.",
                    OAUTH,
                    OAUTH_TITLE,
                ),
            ),
            WorkItem(
                task="Get the app onto 10 active workspaces before a Marketplace submission.",
                detail=sourced(
                    "Submission is blocked below 10 active workspaces, defined as "
                    "workspaces used in the past 28 days.",
                    REVIEW,
                    REVIEW_TITLE,
                ),
            ),
            WorkItem(
                task="Give reviewers their own test login for your service, not a Slack workspace password.",
                detail=sourced(
                    "Slack cannot access Slack workspaces, even test ones. If your "
                    "service is paid, you provide credentials for an account at the "
                    "right tier, with a long trial if you use a trial, plus dummy data.",
                    REVIEW,
                    REVIEW_TITLE,
                ),
            ),
        ],
        blockers=[
            Blocker(
                title="bad_redirect_uri",
                what_happens=sourced(
                    "Slack returns bad_redirect_uri when the redirect_uri on the "
                    "authorize step and the access step differ, or when the URI does "
                    "not match a configured redirect URL or a subdirectory of one.",
                    OAUTH,
                    OAUTH_TITLE,
                ),
                how_to_unstick=(
                    "Copy the redirect URL from OAuth & Permissions into both calls, "
                    "byte for byte. Use HTTPS. Remove any # fragment. If you only have "
                    "one redirect URL and you omit the parameter, Slack uses that one."
                ),
                contact=None,
            ),
            Blocker(
                title="Scopes stuck on the token",
                what_happens=sourced(
                    "Installs add scopes. If you install once with channels:history and "
                    "again with channels:read, the token keeps both. You cannot remove "
                    "a scope without revoking the token.",
                    OAUTH,
                    OAUTH_TITLE,
                ),
                how_to_unstick=(
                    "Revoke the token and reinstall with the shorter list. For a listed "
                    "app, scope changes also have to go through Marketplace review "
                    "before the live install link can ask for them."
                ),
                contact=None,
            ),
            Blocker(
                title="Marketplace review is measured in weeks",
                what_happens=sourced(
                    "Functional review takes up to 10 weeks for a new submission. "
                    "Preliminary resubmits reset that queue. Slack will not skip the "
                    "line for a launch date. Bugs or a thin test pass get the submission returned.",
                    REVIEW,
                    REVIEW_TITLE,
                ),
                how_to_unstick=(
                    "Ship to customers with a direct install link first if a listing "
                    "is not required. Submit only when install, use, and uninstall "
                    "already work on a non-dev workspace, and attach the video."
                ),
                contact="Feedback arrives in the app's submission flow and by email to the address you entered when you submitted.",
            ),
            Blocker(
                title="Listed app is frozen",
                what_happens=sourced(
                    "After publication, the live app's configuration, features, and "
                    "scopes are locked. Changing a redirect URI or adding a scope does "
                    "not take effect until the update is submitted and published. An "
                    "install link that asks for unreviewed scopes shows customers an error.",
                    REVIEW,
                    REVIEW_TITLE,
                ),
                how_to_unstick=(
                    "Clone the manifest into a staging app (for example myapp-staging) "
                    "and point reviewers at that. Scope and feature changes need a video. "
                    "Copy, pricing, and URL edits do not."
                ),
                contact=None,
            ),
        ],
        composio=ComposioContext(
            managed=sourced(
                "Slack is on Composio's managed OAuth list under the slug SLACK "
                "(Slackbot is a separate slug, SLACKBOT). Managed auth avoids creating "
                "a Slack app if Composio's default scopes and branding are acceptable.",
                MANAGED,
                MANAGED_TITLE,
            ),
            custom_app=sourced(
                "For your own Slack app, register the redirect URI shown in the Composio "
                "dashboard. The programmatic docs name "
                "https://backend.composio.dev/api/v3/toolkits/auth/callback and note that "
                "some toolkits still default to "
                "https://backend.composio.dev/api/v1/auth-apps/add.",
                PROGRAMMATIC,
                PROGRAMMATIC_TITLE,
            ),
        ),
        sources=[
            {"title": OAUTH_TITLE, "url": OAUTH},
            {"title": REVIEW_TITLE, "url": REVIEW},
            {"title": RULES_TITLE, "url": RULES},
            {"title": MANAGED_TITLE, "url": MANAGED},
            {"title": PROGRAMMATIC_TITLE, "url": PROGRAMMATIC},
        ],
        research_log=[
            ResearchEvent(
                kind="note",
                detail=(
                    "Curated from Slack's public docs and Composio's auth docs on "
                    "20 Oct 2026. No Slack workspace login was attempted. The create-app "
                    "form fields are uncertain on purpose."
                ),
            )
        ],
    )
