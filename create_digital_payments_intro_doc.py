#!/usr/bin/env python3
"""
Creates ONE Google Doc: "Welcome to IDT Digital Payments (text version)".

Plain-prose rewrite of David Phelps' onboarding deck "Welcome to IDT Digital
Payments" (Google Slides, 17 Sep 2026). The deck is a sequence of terse slide
bullets; this document turns each section into readable paragraphs so a new
joiner can follow the whole story without the slides.

Source deck:
https://docs.google.com/presentation/d/1DeOIChMDlgLm6rgu5Pqp1oEBzC_MFFUDKJnoA7RVrEc/edit
"""

import time
from pathlib import Path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from linkify_refs import linkify

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
]
BASE = Path(__file__).parent
CREDS_FILE = BASE / "credentials.json"
TOKEN_FILE = BASE / "token.json"

TITLE = "Welcome to IDT Digital Payments (text version)"
DECK_URL = ("https://docs.google.com/presentation/d/"
            "1DeOIChMDlgLm6rgu5Pqp1oEBzC_MFFUDKJnoA7RVrEc/edit")

STYLE_MAP = {"t": "TITLE", "h1": "HEADING_1", "h2": "HEADING_2",
             "p": "NORMAL_TEXT", "b": "NORMAL_TEXT", "cap": "NORMAL_TEXT"}

# --------------------------------------------------------------- content ----
# (kind, text). kinds: t title, h1/h2 headings, p paragraph, b bullet, cap note.

BLOCKS = [
    ("t", "Welcome to IDT Digital Payments"),
    ("cap", "Text version of the onboarding deck by David Phelps. "
            f"Source slides: {DECK_URL}"),

    ("h1", "What this document covers"),
    ("p", "This is the story of how IDT rebuilt its digital payments business "
          "over the last five years. It starts with the legacy Mobile Top Up "
          "(MTU) and B2B systems and the problems they caused, moves through "
          "Project K2 (the top-up platform rebuild), the expansion into eGifts, "
          "Project Fuji and the Zendit brand (the reimagined B2B platform), and "
          "then the newer product lines built on top of that foundation: eSIM, "
          "International Bill Pay, Embeddables and Incentives."),
    ("p", "Read it top to bottom the first time. Each section stands on its own "
          "afterwards."),

    # ------------------------------------------------------------ backstory
    ("h1", "Part 1. The backstory"),

    ("h2", "Mobile Top Up (MTU) history"),
    ("p", "Mobile Top Ups are digital products that let a customer in one "
          "country add value and benefits to a mobile phone subscriber in "
          "another. The benefits include airtime, calling minutes, SMS messages "
          "and data packages. Products are sold either by airtime value, as "
          "data plans, or as bundles that combine any mix of airtime, minutes, "
          "SMS and data."),
    ("p", "IDT's original MTU business was built on the Calling Card platform "
          "and served the Retail and Direct to Consumer (DTC) channels. That "
          "platform was a set of large monolithic services, each performing "
          "many product features and business functions at once. The services "
          "were tightly coupled and written in .NET and C++, which made it "
          "difficult to introduce new products or features."),

    ("h2", "B2B history"),
    ("p", "The B2B (wholesale) business was built on the same infrastructure as "
          "MTU. It targeted the B2B channel and was backed by the Retail and "
          "legacy platforms. Onboarding a new partner was a difficult process, "
          "new products were hard to introduce, and there was no user console "
          "and only limited documentation."),
    ("p", "One operational problem stood out. Fulfillment requests could time "
          "out on the partner's side and then eventually succeed on IDT's side. "
          "The partner believed the top-up had failed while the customer had "
          "actually received it, which led to costly billing disputes."),

    ("h2", "Major pain points"),
    ("p", "Taken together, the legacy platforms suffered from:"),
    ("b", "Product generation and updates: creating or changing a product "
          "involved six teams on the legacy stack."),
    ("b", "Channel publishing: getting a product in front of a sales channel "
          "was difficult."),
    ("b", "Operations and maintenance: keeping the systems running was a "
          "constant struggle."),
    ("b", "Multi-currency: the supposed multi-currency flexibility was not "
          "flexible in practice."),
    ("b", "Buy and sell joined at the hip: the purchase side and the supply "
          "side were so tightly bound that swapping a provider meant creating "
          "a whole new product."),
    ("b", "The API: old technology, poor documentation and a lot of hand "
          "holding for every integration."),

    # ------------------------------------------------------------- K2
    ("h1", "Part 2. The solution: Project K2, reinventing top ups"),

    ("h2", "K2 goals"),
    ("p", "Project K2 was the rebuild of the top-up business on a modern "
          "platform. It was designed to coexist with the existing IMTU systems "
          "(B2B, PSF.core and PSP) rather than replace them overnight. Its "
          "goals were:"),
    ("b", "A new product catalog."),
    ("b", "An asynchronous, queue-driven microservice for handling top ups."),
    ("b", "A new microservice serving all client applications."),
    ("b", "Reuse of the existing IMTU gateway and supplier connectors."),
    ("b", "Channels handle payments themselves; K2 does not own the payment."),
    ("b", "Bulk loading of products into the catalog."),

    ("h2", "MVP scope"),
    ("p", "The minimum viable product deliberately cut old dependencies. There "
          "were to be no ClassIDs and no dependence on the Debit system. The "
          "MVP delivered a new catalog and an asynchronous purchase flow with "
          "queueing and retry built in. This directly addressed the B2B "
          "problem described above, where a 60 second timeout produced false "
          "positive failures."),
    ("p", "The MVP built the new services and APIs but made no changes to the "
          "existing supplier connectors. It integrated with the payment service "
          "(IDT Pay for DTC), shipped a user interface for product management, "
          "integrated with the DTC apps, and rolled out on a single DTC channel "
          "in the rest-of-world region: Germany."),

    ("h2", "The new platform"),
    ("p", "K2 was built on a modern stack: Go for the services, Couchbase as the "
          "database (migrated to MongoDB in FY2025), Pulsar for messaging "
          "(migrated to Kafka in FY2026), Kubernetes for infrastructure, "
          "Prometheus for event logging and Grafana for observability "
          "dashboards."),

    ("h2", "Major work under the hood"),
    ("p", "The heavy engineering happened in five areas: the providers and "
          "supply API, the catalog structure, the channel purchase sequence, "
          "the payment sequence, and the MTU supply sequence. Together these "
          "make up the K2 MVP architecture."),

    ("h2", "K2 leadership team"),
    ("p", "Product was led by Emilio del Rio, Keith Niechwiadowicz and David "
          "Phelps. Engineering leadership came from Eugene Lebedev, Pavel "
          "Poleshchuck, Karime Solomon, Juho \"JP\" Virolainen and Eino Lilius."),

    ("h2", "K2 MVP delivery"),
    ("p", "The MVP reached demo quality in August 2021. It shipped the new "
          "catalog and the new fulfillment process, was available for Germany, "
          "was integrated with the Calling App and a test console, and offered "
          "approximately 360 products."),

    # ------------------------------------------------------------- eGift
    ("h1", "Part 3. Moving beyond MTU and DTC: eGift expansion"),
    ("p", "eGifts are branded digital gift cards that can be redeemed at popular "
          "retail brands, both in brick and mortar locations and in e-commerce. "
          "Adding them meant expanding the K2 catalog to a second product type, "
          "with fulfillment running through both legacy and new supplier "
          "connections. eGifts rolled out first on the Retail portal."),
    ("p", "The eGift line was later expanded to include Prepaid Utilities, which "
          "cover gas, electricity and similar services in markets where "
          "utilities are paid in advance."),
    ("p", "Alongside the product work, K2 gained a back office: integration with "
          "Business Intelligence (BI), integration with Oracle Financials for "
          "DTC, and a round of catalog and fulfillment optimizations."),

    # ------------------------------------------------------------- Fuji
    ("h1", "Part 4. B2B reimagined: Project Fuji"),

    ("h2", "The ambition"),
    ("p", "Project Fuji set out to reimagine the B2B business. The aim was to "
          "expand the sales channel to B2B and enterprise customers and to tap "
          "the long tail of small and medium enterprises worldwide. It would "
          "widen the client verticals to fintechs, NGOs, advertisers, super apps, "
          "social media and more, offer prepaid (phase 1) and postpaid (phase 2) "
          "options, and be fully self service and self onboarding. The platform "
          "would be multi-tenant and, above all, developer friendly and "
          "developer first."),

    ("h2", "From prospects to resellers"),
    ("p", "Fuji was designed to convert a curious prospect into an active "
          "reseller with as little friction as possible. It offers multiple ways "
          "to integrate, from UI widgets dropped onto an existing site to full "
          "scale SDKs for deeper integration. A developer community allows the "
          "exchange of ideas and promoted content from internal and external "
          "participants. Feature-rich control panels and community services sit "
          "alongside quick-start SDKs in a variety of languages, with a sandbox "
          "available immediately. Setup, integration, funding and the move to "
          "production are all self service."),

    ("h2", "Client acquisition"),
    ("p", "Acquisition starts with a compelling marketing site that explains the "
          "wholesale opportunity and gives easy instructions for getting started. "
          "Sign up is driven through a simple registration that grants access to "
          "the SDKs, the sandbox and the community. The site was backed by a "
          "content management system from the start so that content could be "
          "refined and new product features published regularly."),

    ("h2", "Registration"),
    ("p", "Registration is a quick sign-up. It creates a user profile with access "
          "to the control panel, enrols the user in the developer community, and "
          "gives immediate access to SDKs, documentation and the sandbox."),

    ("h2", "Integration options"),
    ("p", "Fuji ships full-featured SDKs in popular languages: Go, PHP, .NET, "
          "Java, JavaScript and Python. For site developers without a full "
          "technical staff there are site widgets that can be dropped into an "
          "existing site for a quick integration. The range is deliberate: it "
          "equips everyone from technical novices to experts with a way to get "
          "on board and start selling."),

    ("h2", "A fully integrated user experience"),
    ("p", "Everything a reseller needs sits in one place. The user experience "
          "brings together all administrative and community features: self "
          "service account funding, reporting and settings management, "
          "browsing product catalogs and pricing, account alerts, a rich set of "
          "documentation and testing tools, participation in the developer "
          "community, and control over when to go live and start selling."),

    ("h2", "New services powering the integration"),
    ("p", "Under the surface, Fuji added new components providing all the "
          "services a wholesale business requires, plus integrations to a "
          "variety of IDT products and services. Through the SDKs, developers "
          "can access common funding information, top up their funds and "
          "respond to alerts. Callback functions allow asynchronous use of the "
          "SDKs so an integration can grow with the partner's sales volume."),

    ("h2", "Administration tools"),
    ("p", "On the IDT side there is an administrative console for managing client "
          "accounts and settings, integrated tooling for fraud detection and "
          "velocity rules, product catalog and FX management, multi-level sales "
          "agent controls, community service access for monitoring the message "
          "forums and managing curated content, and a chat service bot for "
          "handling direct developer contact."),

    ("h2", "The Fuji vision"),
    ("p", "The problem Fuji addresses is that innovators had no easy way to "
          "access international products and international customers. The "
          "solution is to give them easy, flexible and fast access to both. The "
          "vision is to become the go-to Prepaid-as-a-Service, developer-first "
          "platform in the market, targeting innovators, developers and "
          "entrepreneurs."),
    ("p", "The solution fundamentals are: plug and play, self onboarding, "
          "developers first (SDKs, widgets, plugins, sandbox), pay as you grow, "
          "and options and flexibility across code, low code and no code."),
    ("p", "The product set covers airtime, data, gifts and vouchers, payments, "
          "mobile money wallets and calling. The target markets include money "
          "transfer operators, loyalty and incentive programmes, apps and web, "
          "crypto, fintech, banks, gaming and NGOs. Developer community "
          "advocacy is treated as key, through forums, hackathons, meetups, "
          "articles and open libraries."),

    ("h2", "The Fuji platform"),
    ("p", "The platform choices mirror K2's. A compute platform that scales up "
          "fast when load demands, which keeps it cost effective and scalable. "
          "Message streaming that provides the throughput to handle large "
          "transaction volumes, giving high throughput and durability. A "
          "programming language chosen for the speed needed to service "
          "transactions, so it is fast and effective. And a monitoring system "
          "that combines all system insights into a set of connected "
          "dashboards, easy to use and industry standard."),

    ("h2", "Branding journey and launch: Zendit"),
    ("p", "Project Fuji went through a branding journey and launched to the "
          "market as Zendit at MWC Barcelona in 2023. At launch Zendit offered "
          "Mobile Top Up, mobile bundles, mobile data plans, eGifts and prepaid "
          "utilities, with a user console, an admin console, a marketing website "
          "and a developer website. The K2 catalog grew significantly, to over "
          "15,000 products in four days."),

    # ------------------------------------------------------------- eSIM
    ("h1", "Part 5. eSIM expansion"),
    ("h2", "What an eSIM is"),
    ("p", "eSIMs provide data plans for the travel market. An eSIM is a digital "
          "product that can be installed on a device using a SmartLink, a QR "
          "code or a manual install. It offers significant savings on data "
          "roaming when a customer travels outside their home service area. "
          "Plans come either as a fixed amount of data for a fixed duration or "
          "as unlimited plans for a set number of days, and a plan may cover a "
          "single country, a region or the whole globe. eSIMs are data only: "
          "there is no phone number and no SMS."),
    ("h2", "Introducing eSIMs"),
    ("p", "The K2 team worked in tandem with the Zendit team to integrate the "
          "catalog of esim-go, IDT's eSIM partner, and bring the product to "
          "market. The catalog spans more than 100 destination countries. New "
          "API endpoints on Zendit let partners onboard and start selling eSIM "
          "products. The MVP soft launched in November 2023 and the full launch "
          "took place at MWC Barcelona in 2024."),

    # ------------------------------------------------------------- BMK
    ("h1", "Part 6. Don and Dave's side quest: the Brand Media Kit"),
    ("h2", "eGift improvements and shopping"),
    ("p", "The Brand Media Kit (BMK) started as a rapid prototype built on "
          "WordPress with the Advanced Custom Fields plugin to create rich "
          "content types for eGift brands: brand images, logos, card images, "
          "eGift instructions and brand terms and conditions. It then expanded "
          "to include collections, categories, containers and home pages, "
          "which let product managers merchandise the DTC shopping experience. "
          "BMK supported multiple languages from the start, and Zendit exposes "
          "APIs that let clients obtain brand assets for eGift products."),
    ("h2", "BMK growth"),
    ("p", "BMK keeps growing with new data types: eSIM, Money Transfer, IMTU and "
          "Calling Plan destinations, eSIM install instructions, eSIM device "
          "brands and devices, MTU brands, IBP brands, and the DTC cross-selling "
          "collections and products. Looking ahead, BMK will provide "
          "customizable gift wrapping templates for eGift delivery and whatever "
          "media assets the product mix needs as it continues to expand."),

    # ------------------------------------------------------------- IBP
    ("h1", "Part 7. International Bill Pay (IBP) expansion"),
    ("p", "International Bill Payments are cross-border payments for everything "
          "postpaid, from utilities to parking meters. The catalog was seeded "
          "through a partner in Mexico covering Mexican payments. Integration "
          "continues with Banco Industrial in Guatemala to expand the catalog "
          "further, and the integration with Tigo Guatemala for postpaid "
          "telecom bills is being wrapped up. Future partnerships will bring "
          "more billers into the Digital Payments system."),

    # ------------------------------------------------------------- Embeddables
    ("h1", "Part 8. Rise of the Embeddable: from low code to no code"),
    ("p", "Embeddables let partners integrate with Zendit through drop-in "
          "components that deliver complete eSIM, MTU and eGift experiences "
          "without building the flow themselves. The eSIM embeddable kicked off "
          "at MWC Barcelona as an MVP with a Stripe payments integration. It is "
          "evolving to support more payment processors, better experiences and "
          "more partner control over the experience, so that partners can jump "
          "start their integration."),

    # ------------------------------------------------------------- Incentives
    ("h1", "Part 9. Incentives: a new business opportunity"),
    ("p", "Incentives opens up Zendit's gift card system to a new B2B and B2C "
          "gifting experience. The target personas are marketing professionals "
          "with no technical resources and marketing professionals with minimal "
          "technical resources, so the product has to work without an "
          "engineering team on the customer side."),
    ("h2", "Market release (mid October 2026)"),
    ("b", "Custom email setup."),
    ("b", "UI touch ups: fonts, colours and messaging."),
    ("b", "Ability to host the eGift on the customer's own website or app, or "
          "have Zendit host it on landing pages."),
    ("h2", "Roadmap (late October to early November 2026)"),
    ("b", "Scheduled campaigns and reminders."),
    ("b", "Budget and quantity limits."),
    ("b", "API integration for managing customers."),
    ("b", "Additional KPIs: customer counts, emails sent, emails opened, landing "
          "pages visited, gift shop visited."),
    ("h2", "Future planned features (based on market demand)"),
    ("b", "Analytics dashboard widgets that move beyond simple KPIs to "
          "visualizations on the Zendit dashboard, for insight into a single "
          "campaign or across several."),
    ("b", "Customer profiles: a new console for managing profiles of customers "
          "previously added, used to pick customers for a campaign."),
    ("b", "Date-driven gifting: set dates on a customer for when to send a gift "
          "as part of a campaign, such as birthdays or customer anniversaries."),
    ("b", "Multiple language support on templates and eGift redemption, routing "
          "customers by their language preference."),

    # ------------------------------------------------------------- summary
    ("h1", "The ecosystem in one paragraph"),
    ("p", "K2 is the product and fulfillment engine: catalog, asynchronous "
          "purchase flow, supplier connectors, back office. Zendit is the "
          "developer-first B2B face of that engine, with SDKs, widgets, "
          "consoles and a community. The DTC apps (Calling App, Money App, "
          "Retail portal) are the first-party channels on the same engine. "
          "eGift, eSIM, International Bill Pay, Embeddables and Incentives are "
          "product lines added on top, each widening either the catalog or the "
          "set of partners who can sell it. The Brand Media Kit supplies the "
          "content that makes those products presentable in every channel."),
]


# --------------------------------------------------------------- helpers ----

def get_credentials():
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_FILE.write_text(creds.to_json())
    return creds


def build_requests(blocks):
    reqs, cur = [], 1
    for kind, text in blocks:
        line = text + "\n"
        reqs.append({"insertText": {"location": {"index": cur}, "text": line}})
        reqs.append({"updateParagraphStyle": {
            "range": {"startIndex": cur, "endIndex": cur + len(line)},
            "paragraphStyle": {"namedStyleType": STYLE_MAP[kind]},
            "fields": "namedStyleType"}})
        if kind == "b":
            reqs.append({"createParagraphBullets": {
                "range": {"startIndex": cur, "endIndex": cur + len(line)},
                "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE"}})
        if kind == "cap":
            reqs.append({"updateTextStyle": {
                "range": {"startIndex": cur, "endIndex": cur + len(text)},
                "textStyle": {"italic": True,
                              "fontSize": {"magnitude": 9, "unit": "PT"}},
                "fields": "italic,fontSize"}})
        cur += len(line)
    return reqs


def batched(docs, doc_id, reqs, size=40):
    for i in range(0, len(reqs), size):
        docs.documents().batchUpdate(
            documentId=doc_id, body={"requests": reqs[i:i + size]}).execute()
        time.sleep(0.25)


def main():
    creds = get_credentials()
    docs = build("docs", "v1", credentials=creds)
    drive = build("drive", "v3", credentials=creds)

    doc = docs.documents().create(body={"title": TITLE}).execute()
    doc_id = doc["documentId"]
    print(f"Created doc: {doc_id}")

    reqs = build_requests(BLOCKS)
    batched(docs, doc_id, reqs)
    print(f"Inserted {len(reqs)} requests")

    # Bare URLs (the source deck) become clickable.
    linkify(docs, doc_id)

    drive.permissions().create(
        fileId=doc_id,
        body={"role": "writer", "type": "domain", "domain": "idt.net"},
    ).execute()

    url = f"https://docs.google.com/document/d/{doc_id}/edit"
    print(f"\nDone: {url}")
    return url


if __name__ == "__main__":
    main()
