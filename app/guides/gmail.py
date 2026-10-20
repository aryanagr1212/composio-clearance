"""Gmail, the hard case.

Judgment: difficulty is Hard for a production agent that reads or modifies
mailbox data. The first test call is still self-serve, because an app can stay
in Testing. The long pole is restricted-scope verification plus, for a server,
Google's CASA security assessment.

Nothing here is marked tested. These claims were written from Google's public
docs on 20 Oct 2026. Nobody signed into Cloud Console.

Each sourced claim cites one page. Where a useful number is not on that page
(how many minutes the form takes, what CASA costs), the sentence is uncertain.
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

SCOPES = "https://developers.google.com/workspace/gmail/api/auth/scopes"
SCOPES_TITLE = "Choose Gmail API scopes"
RESTRICTED = "https://developers.google.com/identity/protocols/oauth2/production-readiness/restricted-scope-verification"
RESTRICTED_TITLE = "Restricted scope verification"
SENSITIVE = "https://developers.google.com/identity/protocols/oauth2/production-readiness/sensitive-scope-verification"
SENSITIVE_TITLE = "Sensitive scope verification"
WEB = "https://developers.google.com/identity/protocols/oauth2/web-server"
WEB_TITLE = "Using OAuth 2.0 for Web Server Applications"
AUDIENCE = "https://support.google.com/cloud/answer/15549945"
AUDIENCE_TITLE = "Manage App Audience"
OVERVIEW = "https://developers.google.com/identity/protocols/oauth2/production-readiness/overview"
OVERVIEW_TITLE = "OAuth app state overview"
MANAGED = "https://docs.composio.dev/toolkits/managed-auth"
MANAGED_TITLE = "Managed OAuth apps"
CUSTOM = "https://docs.composio.dev/docs/authentication/custom-app-vs-managed-app"
CUSTOM_TITLE = "Managed vs custom auth"
PROGRAMMATIC = "https://docs.composio.dev/docs/authentication/programmatic-auth-configs"
PROGRAMMATIC_TITLE = "Programmatic auth configs"

CHECKED = date(2026, 10, 20)


def build() -> Guide:
    return Guide(
        slug="gmail",
        app_name="Gmail",
        aliases=["google mail", "google gmail"],
        homepage_url="https://mail.google.com",
        docs_url=SCOPES,
        summary=(
            "A Gmail agent that reads or changes mail is a restricted-scope app. "
            "You can make a test call the same day by staying in Testing with "
            "yourself as a test user. Production for anyone with a Google account "
            "means brand verification, restricted-scope review, a demo video, and "
            "usually an annual CASA security assessment if your server sees the mail."
        ),
        last_checked=CHECKED,
        generated_by="curated",
        verdict=Verdict(
            difficulty="hard",
            review_required="conditional",
            difficulty_reason=sourced(
                "Google classifies gmail.readonly, gmail.modify, gmail.compose, "
                "gmail.insert, gmail.metadata, gmail.settings.basic, and "
                "https://mail.google.com/ as restricted. Restricted scopes require "
                "restricted-scope OAuth verification, and storing or transmitting "
                "that data on servers requires a security assessment. gmail.send "
                "is sensitive, not restricted.",
                SCOPES,
                SCOPES_TITLE,
            ),
            time_to_first_test=sourced(
                "In Testing, an external app is limited to test users you list, "
                "up to 100, and authorizations by a test user expire seven days "
                "after consent. A refresh token from that consent expires too. "
                "Apps that request only openid, email, and profile are exempt "
                "from the cap and the seven-day expiry.",
                AUDIENCE,
                AUDIENCE_TITLE,
                note=(
                    "Google does not publish how long the console clicks take. "
                    "The fact above is the token rule, not a review queue."
                ),
            ),
            time_to_production=sourced(
                "Brand verification typically takes 2–3 business days when branding "
                "has changed. The restricted-scope process can take several weeks, "
                "because an app that can access restricted data from or through a "
                "third-party server must pass an annual security assessment. Google "
                "standardizes that assessment as CASA, through the App Defense Alliance, "
                "and access has to be reassessed at least every 12 months after the "
                "assessor's letter of assessment.",
                RESTRICTED,
                RESTRICTED_TITLE,
                note=(
                    "If the app only needs gmail.send, that scope is sensitive. "
                    "The sensitive-scope page, not this one, gives the 3–5 business "
                    "day figure. CASA scheduling with the assessor is extra; Google "
                    "does not publish a price on this page."
                ),
            ),
            review_summary=sourced(
                "Verification is not required while Publishing status stays Testing, "
                "or when the consent screen user type is Internal to one Workspace. "
                "An external app that requests restricted scopes for any Google user "
                "must complete restricted-scope verification. A domain-wide install "
                "skips brand verification, but sensitive or restricted scopes still "
                "require app verification.",
                RESTRICTED,
                RESTRICTED_TITLE,
            ),
        ),
        requirements=[
            Requirement(
                name="Google Cloud project and OAuth client",
                needed="required",
                detail=sourced(
                    "A web server app registers an OAuth client and authorized "
                    "redirect URIs in the Cloud Console. The redirect URI in the "
                    "authorization request has to match one of those values exactly, "
                    "including scheme, case, and trailing slash, or Google returns "
                    "redirect_uri_mismatch.",
                    WEB,
                    WEB_TITLE,
                ),
            ),
            Requirement(
                name="OAuth consent screen branding",
                needed="required",
                detail=sourced(
                    "Brand verification needs an app name, support email, home page "
                    "URI, and privacy policy URI that match the app. The home page "
                    "must be public, must describe the app, and must link to the "
                    "privacy policy. A Play Store or Facebook link does not count "
                    "as a home page.",
                    RESTRICTED,
                    RESTRICTED_TITLE,
                ),
            ),
            Requirement(
                name="Verified domain",
                needed="required",
                detail=sourced(
                    "You verify ownership of the project's authorized domains in "
                    "Google Search Console, with a Google account that is an Owner "
                    "or Editor on the Cloud project.",
                    RESTRICTED,
                    RESTRICTED_TITLE,
                ),
            ),
            Requirement(
                name="Privacy policy on the same domain",
                needed="required",
                detail=sourced(
                    "The privacy policy has to be on the same domain as the home "
                    "page, linked from the consent screen, and it has to disclose "
                    "how the app accesses, uses, stores, or shares Google user data. "
                    "Restricted scopes also have to meet the Limited Use rules.",
                    RESTRICTED,
                    RESTRICTED_TITLE,
                ),
            ),
            Requirement(
                name="Demo video",
                needed="conditional",
                detail=sourced(
                    "Sensitive and restricted scope verification asks for an unlisted "
                    "YouTube video, in English, of the OAuth grant. It must show the "
                    "app name on the consent screen, the OAuth client ID in the "
                    "browser address bar, and the feature each requested scope enables.",
                    RESTRICTED,
                    RESTRICTED_TITLE,
                ),
            ),
            Requirement(
                name="CASA security assessment",
                needed="conditional",
                detail=sourced(
                    "If the app can access restricted-scope data from or through a "
                    "third-party server, it must pass a security assessment from a "
                    "Google-empanelled assessor. Google uses the CASA framework for "
                    "that assessment, and it is repeated at least every 12 months.",
                    RESTRICTED,
                    RESTRICTED_TITLE,
                    note=(
                        "A local-only script that never puts Gmail data on a server "
                        "is a different case. Confirm which side of that line you "
                        "are on before you book an assessor. Cost is not listed on this page."
                    ),
                ),
            ),
            Requirement(
                name="App logo",
                needed="conditional",
                detail=sourced(
                    "The branding page asks for branding information, including the "
                    "app name and logo. Branding changes are blocked while verification "
                    "is in progress, and a passed automated check expires if you do "
                    "not publish it within 7 days.",
                    RESTRICTED,
                    RESTRICTED_TITLE,
                ),
            ),
            Requirement(
                name="Paid Google Cloud plan",
                needed="not_needed",
                detail=uncertain(
                    "The Gmail OAuth docs used here do not say you must enable billing "
                    "or buy a paid plan to create an OAuth client or submit verification. "
                    "The CASA assessment is paid to a third-party assessor, not described "
                    "as a Google Cloud SKU.",
                    "Confirm billing separately if you turn on other Cloud APIs.",
                ),
            ),
        ],
        steps=[
            Step(
                title="Decide whether you need your own Google client",
                who="either",
                console_url=MANAGED,
                console_label="Composio managed OAuth list",
                instructions=(
                    "If Composio's managed Gmail app already requests the scopes you "
                    "need, and users can see Composio on the consent screen, you can "
                    "stop here. Continue only if you need your own brand, a scope "
                    "Composio does not request, or your own quota."
                ),
                detail=sourced(
                    "Composio lists Gmail (slug GMAIL) among toolkits where it can "
                    "provide the OAuth app. A custom auth config is how you supply "
                    "your own client ID and secret instead.",
                    MANAGED,
                    MANAGED_TITLE,
                    note="The managed list says an app is included when Composio manages at least one OAuth method. Check the Gmail toolkit page for the method you use.",
                ),
            ),
            Step(
                title="Create a Cloud project and enable the Gmail API",
                who="human",
                console_url="https://console.cloud.google.com/apis/library/gmail.googleapis.com",
                console_label="Gmail API library page",
                instructions=(
                    "Create a project in Google Cloud Console. Enable the Gmail API "
                    "on that project. Use a separate project for production and for "
                    "testing, which is what Google recommends."
                ),
                detail=sourced(
                    "Google recommends different projects for testing and production, "
                    "and recommends submitting for verification only when any Google "
                    "user should be able to use the app.",
                    RESTRICTED,
                    RESTRICTED_TITLE,
                ),
            ),
            Step(
                title="Configure the consent screen, but do not publish yet",
                who="human",
                console_url="https://console.cloud.google.com/auth/branding",
                console_label="OAuth branding",
                instructions=(
                    "Set user type to External unless every user is in your own "
                    "Workspace. Fill in the app name, user support email, and "
                    "developer contact email. Leave publishing status on Testing. "
                    "Add yourself as a test user."
                ),
                detail=sourced(
                    "Testing status means only listed test users can authorize the "
                    "app, with a hard cap of 100 test users. They see a testing "
                    "warning. An Internal user type is available to projects in a "
                    "Cloud organization and is limited to that organization.",
                    AUDIENCE,
                    AUDIENCE_TITLE,
                ),
            ),
            Step(
                title="Add the narrowest Gmail scope that does the job",
                who="either",
                console_url=SCOPES,
                console_label="Gmail scope reference",
                instructions=(
                    "On the Data Access page, add scopes one feature at a time. "
                    "For 'read the user's mail' that is gmail.readonly, which is "
                    "restricted. For 'send only' prefer gmail.send, which is "
                    "sensitive. Do not add https://mail.google.com/ unless you "
                    "must permanently delete mail while bypassing trash."
                ),
                detail=sourced(
                    "Google tells you to request the most narrowly focused scope "
                    "you can. The full https://mail.google.com/ scope is only for "
                    "immediate permanent delete that bypasses trash. Other mailbox "
                    "actions have less permissive scopes.",
                    SCOPES,
                    SCOPES_TITLE,
                ),
            ),
            Step(
                title="Create a web OAuth client and set the redirect URI",
                who="human",
                console_url="https://console.cloud.google.com/apis/credentials",
                console_label="Credentials",
                instructions=(
                    "Create an OAuth client ID of type Web application. Add the "
                    "exact redirect URI your server uses. For a local test, "
                    "http://localhost with a port is allowed. For Composio custom "
                    "auth, use the redirect URI shown in the Composio dashboard. "
                    "Copy the client ID and client secret into your secret store, "
                    "not into the repo."
                ),
                detail=sourced(
                    "Authorized redirect URIs for a web client must follow Google's "
                    "validation rules. The docs use http://localhost:8080 as a "
                    "testing example. The value sent at authorization time must "
                    "exactly match a registered URI.",
                    WEB,
                    WEB_TITLE,
                ),
            ),
            Step(
                title="Make one test call as a test user",
                who="human",
                console_url=WEB,
                console_label="Web server OAuth guide",
                instructions=(
                    "Send a test user through the consent screen, exchange the "
                    "code for tokens, and call the one Gmail method you need. "
                    "Expect the unverified-app warning. Plan on repeating consent "
                    "every seven days until the app is verified and in production."
                ),
                detail=sourced(
                    "Test-user authorizations expire seven days from consent, and "
                    "so do refresh tokens issued to those users. Google shows a "
                    "warning before a test user can authorize.",
                    AUDIENCE,
                    AUDIENCE_TITLE,
                ),
            ),
            Step(
                title="Prepare verification only when strangers must connect",
                who="human",
                console_url=RESTRICTED,
                console_label="Restricted scope verification",
                instructions=(
                    "Publish a public home page and a same-domain privacy policy "
                    "that describes the Gmail data you use. Verify the domain in "
                    "Search Console. Record the unlisted YouTube demo. Submit brand "
                    "verification first, publish the branding, then submit data "
                    "access. If a server stores or forwards mail, book the CASA "
                    "assessment. Watch the developer contact inbox; review pauses "
                    "until you answer."
                ),
                detail=sourced(
                    "You need a published branding status before data-access "
                    "verification. After you submit, Trust & Safety may email the "
                    "developer contact and the consent-screen support address. "
                    "The review can pause while Google waits for a reply. Restricted "
                    "data that is reachable through a server needs the annual assessment.",
                    RESTRICTED,
                    RESTRICTED_TITLE,
                ),
            ),
        ],
        scopes=[
            ScopeItem(
                name="https://www.googleapis.com/auth/gmail.readonly",
                tier="restricted",
                triggers_review="yes",
                purpose="Read messages and settings. The usual scope for an inbox agent.",
                detail=sourced(
                    "gmail.readonly is a restricted scope: view email messages and settings.",
                    SCOPES,
                    SCOPES_TITLE,
                ),
            ),
            ScopeItem(
                name="https://www.googleapis.com/auth/gmail.modify",
                tier="restricted",
                triggers_review="yes",
                purpose="Read, compose, and send. Does not allow permanent delete that bypasses trash.",
                detail=sourced(
                    "gmail.modify is restricted. It can read, compose, and send, and "
                    "it cannot immediately and permanently delete mail while bypassing trash.",
                    SCOPES,
                    SCOPES_TITLE,
                ),
            ),
            ScopeItem(
                name="https://www.googleapis.com/auth/gmail.send",
                tier="sensitive",
                triggers_review="conditional",
                purpose="Send mail only. Prefer this over a restricted scope when you do not read the mailbox.",
                detail=sourced(
                    "gmail.send is listed as a sensitive scope (send email on the user's "
                    "behalf), not as a restricted scope. Sensitive scopes require additional "
                    "OAuth app verification. The security assessment is described for "
                    "restricted scopes when that data is stored or transmitted on servers.",
                    SCOPES,
                    SCOPES_TITLE,
                    note=(
                        "A second page, Sensitive scope verification, says that review "
                        "typically takes 3–5 business days: "
                        "https://developers.google.com/identity/protocols/oauth2/production-readiness/sensitive-scope-verification"
                    ),
                ),
            ),
            ScopeItem(
                name="https://mail.google.com/",
                tier="restricted",
                triggers_review="yes",
                purpose="Full mailbox access, including permanent delete that bypasses trash.",
                detail=sourced(
                    "Request https://mail.google.com/ only if the app must immediately "
                    "and permanently delete threads and messages, bypassing trash. "
                    "Every other mailbox action has a narrower scope.",
                    SCOPES,
                    SCOPES_TITLE,
                ),
            ),
            ScopeItem(
                name="openid email profile",
                tier="non-sensitive",
                triggers_review="no",
                purpose="Sign-in only. Not enough to read or send mail.",
                detail=sourced(
                    "If the only scopes are name, email, and profile (userinfo.email, "
                    "userinfo.profile, openid, or the OpenID Connect equivalents), users "
                    "do not have to be test users, they do not see the testing warning, "
                    "and authorizations do not expire after seven days.",
                    AUDIENCE,
                    AUDIENCE_TITLE,
                ),
            ),
        ],
        scope_advice=sourced(
            "Request the narrowest scope that implements the feature. Declare every "
            "scope on the Data Access page. Scopes you declare are grouped there as "
            "non-sensitive, sensitive, or restricted, which is the list Google will review.",
            RESTRICTED,
            RESTRICTED_TITLE,
        ),
        redirect_rules=sourced(
            "The redirect URI must exactly match a URI registered on the OAuth client, "
            "including http versus https, letter case, and a trailing slash. A mismatch "
            "returns redirect_uri_mismatch. Local testing may use http://localhost "
            "(the docs use http://localhost:8080). Google's authorization endpoint "
            "itself is HTTPS only.",
            WEB,
            WEB_TITLE,
        ),
        agent_can_do=[
            WorkItem(
                task="Pick the smallest Gmail scope and write the justification Google asks for.",
                detail=sourced(
                    "Verification asks you to explain why each restricted scope is "
                    "required and why a narrower scope is not enough, and to declare "
                    "those scopes on the Data Access page.",
                    RESTRICTED,
                    RESTRICTED_TITLE,
                ),
            ),
            WorkItem(
                task="Draft the privacy-policy sentences that describe Gmail data use.",
                detail=sourced(
                    "The privacy policy must disclose how the app accesses, uses, "
                    "stores, or shares Google user data, and restricted scopes must "
                    "meet Limited Use. The policy has to live on the same domain as the home page.",
                    RESTRICTED,
                    RESTRICTED_TITLE,
                ),
            ),
            WorkItem(
                task="Write the demo-video shot list, including the client ID in the address bar.",
                detail=sourced(
                    "The demo must show the English consent flow, the app name, the "
                    "OAuth client ID in the address bar, and the feature behind each "
                    "sensitive or restricted scope. Upload it unlisted to YouTube.",
                    RESTRICTED,
                    RESTRICTED_TITLE,
                ),
            ),
            WorkItem(
                task="Build the verification checklist and the list of inboxes to watch.",
                detail=sourced(
                    "Google emails the developer contact and the consent-screen support "
                    "email when it needs something else. Those addresses have to stay current, "
                    "and so do the Owner and Editor accounts on the project.",
                    RESTRICTED,
                    RESTRICTED_TITLE,
                ),
            ),
        ],
        human_must_do=[
            WorkItem(
                task="Create the Cloud project, OAuth client, and test users while logged in.",
                detail=uncertain(
                    "This guide did not attempt the Cloud Console flow. The steps are "
                    "documented as console actions, and they sit behind a Google login.",
                    "Treat console clicks, 2FA, and billing prompts as human work until someone tests an unattended run.",
                ),
            ),
            WorkItem(
                task="Verify the domain in Search Console.",
                detail=sourced(
                    "Domain ownership is verified in Google Search Console by an account "
                    "that is an Owner or Editor on the API Console project.",
                    RESTRICTED,
                    RESTRICTED_TITLE,
                ),
            ),
            WorkItem(
                task="Publish the home page and privacy policy on a domain you control.",
                detail=sourced(
                    "The home page must be publicly reachable without a login, and the "
                    "privacy policy must be hosted on that same domain.",
                    RESTRICTED,
                    RESTRICTED_TITLE,
                ),
            ),
            WorkItem(
                task="Record the demo video and submit brand, then data access.",
                detail=sourced(
                    "Data-access verification cannot start until branding is published. "
                    "The video has to show a real consent screen for this client ID.",
                    RESTRICTED,
                    RESTRICTED_TITLE,
                ),
            ),
            WorkItem(
                task="Buy and complete the CASA assessment if a server touches Gmail data.",
                detail=sourced(
                    "The assessment is performed by an independent assessor empanelled "
                    "by Google, using CASA. Google emails you when the annual recertification is due.",
                    RESTRICTED,
                    RESTRICTED_TITLE,
                    note="Who pays the assessor, and how much, is not on this page.",
                ),
            ),
        ],
        blockers=[
            Blocker(
                title="Seven-day tokens and a 100-user cap",
                what_happens=sourced(
                    "Testing authorizations expire seven days after consent, including "
                    "refresh tokens. Only listed test users can grant access, up to 100. "
                    "Google shows a warning before a test user can authorize.",
                    AUDIENCE,
                    AUDIENCE_TITLE,
                ),
                how_to_unstick=(
                    "Stay in Testing until the demo video and policies are real. Do not "
                    "publish the consent screen just to clear the warning: an unverified "
                    "production app still cannot serve a real user base if it uses Gmail "
                    "scopes. Submit verification, then publish."
                ),
                contact="The warning is enforced by Google. There is no appeal that raises the test-user cap.",
            ),
            Blocker(
                title="Restricted scopes plus a server means CASA",
                what_happens=sourced(
                    "An app that requests restricted scopes and can access that data from "
                    "or through a third-party server must pass an annual third-party "
                    "security assessment. Google says this is why restricted verification "
                    "can take several weeks. The framework is CASA.",
                    RESTRICTED,
                    RESTRICTED_TITLE,
                ),
                how_to_unstick=(
                    "If you only send mail, drop to gmail.send and follow the sensitive-scope "
                    "path instead. If you truly read mail on a server, start the assessment "
                    "early and keep Owner or Editor accounts current so the renewal email "
                    "is not missed."
                ),
                contact="Google's Trust & Safety team emails the developer contact and the support email on the consent screen.",
            ),
            Blocker(
                title="Home page or privacy policy rejected",
                what_happens=sourced(
                    "The home page must be public, obviously about this app, and must link "
                    "to the privacy policy. The policy must be on the same domain and must "
                    "describe Google user data. A store listing is not a home page.",
                    RESTRICTED,
                    RESTRICTED_TITLE,
                ),
                how_to_unstick=(
                    "Host both URLs on the domain you verified in Search Console. Mention "
                    "Gmail data specifically: what you read, whether you store it, and how "
                    "a user asks you to delete it."
                ),
                contact=None,
            ),
            Blocker(
                title="Demo video does not show the client ID",
                what_happens=sourced(
                    "Reviewers look for the OAuth client ID in the address bar of the "
                    "consent screen, the app name, and a working use of each sensitive "
                    "or restricted scope. A task-automation platform also has to show "
                    "how workflows move user data.",
                    RESTRICTED,
                    RESTRICTED_TITLE,
                ),
                how_to_unstick=(
                    "Record one continuous English walkthrough from a fresh test user. "
                    "Pause on the consent screen long enough to read the client ID. "
                    "Upload as Unlisted, not Private."
                ),
                contact=None,
            ),
            Blocker(
                title="Workspace admin blocks the app",
                what_happens=sourced(
                    "A Workspace can control which third-party apps access its data. "
                    "Sensitive scopes can be limited to OAuth clients the organization "
                    "has marked trusted. An org_internal error means the user is outside "
                    "the Cloud project's organization.",
                    AUDIENCE,
                    AUDIENCE_TITLE,
                    note="Admin policy is the customer's, so a passed Google verification still does not guarantee a Workspace user can connect.",
                ),
                how_to_unstick=(
                    "Ask the customer's Workspace admin to trust your OAuth client ID. "
                    "That approval is theirs. Your verification does not override it."
                ),
                contact="The customer's Google Workspace administrator.",
            ),
        ],
        composio=ComposioContext(
            managed=sourced(
                "Gmail is on Composio's managed OAuth list under the slug GMAIL. "
                "Managed auth means you do not register a Google client or paste a "
                "client secret. Users see Composio on the consent screen, and you "
                "use Composio's default scopes and shared quota.",
                MANAGED,
                MANAGED_TITLE,
            ),
            custom_app=sourced(
                "Bring your own OAuth app when the consent screen must show your name, "
                "when you need scopes Composio does not request, or when you need your "
                "own quota. Register the redirect URI from the Composio dashboard. "
                "The programmatic docs name "
                "https://backend.composio.dev/api/v3/toolkits/auth/callback and say some "
                "toolkits still use the legacy https://backend.composio.dev/api/v1/auth-apps/add. "
                "If you omit the redirect, register whatever default the toolkit shows.",
                PROGRAMMATIC,
                PROGRAMMATIC_TITLE,
                note="The 'when to bring your own app' reasons are on the managed-vs-custom page. This claim cites the page that prints the callback URLs. Confirm the URI in the dashboard before you save it in Google.",
            ),
        ),
        sources=[
            {"title": SCOPES_TITLE, "url": SCOPES},
            {"title": RESTRICTED_TITLE, "url": RESTRICTED},
            {"title": SENSITIVE_TITLE, "url": SENSITIVE},
            {"title": WEB_TITLE, "url": WEB},
            {"title": AUDIENCE_TITLE, "url": AUDIENCE},
            {"title": OVERVIEW_TITLE, "url": OVERVIEW},
            {"title": MANAGED_TITLE, "url": MANAGED},
            {"title": CUSTOM_TITLE, "url": CUSTOM},
            {"title": PROGRAMMATIC_TITLE, "url": PROGRAMMATIC},
        ],
        research_log=[
            ResearchEvent(
                kind="note",
                detail=(
                    "Curated from Google's public docs and Composio's auth docs on "
                    "20 Oct 2026. No Cloud Console login was attempted, so no claim "
                    "is marked tested. The published-unverified 100-user cap is "
                    "described on the OAuth app state overview; the Testing cap cited "
                    "in the verdict is from Manage App Audience."
                ),
                url=OVERVIEW,
            )
        ],
    )
