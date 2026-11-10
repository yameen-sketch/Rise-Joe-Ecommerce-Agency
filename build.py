import json
import re
from datetime import date
#!/usr/bin/env python3
"""
Rise Joe — static site generator.

All website content lives in this file. Run:

    python3 build.py

and every page in ./website is regenerated. Upload the contents of
./website to Hostinger's public_html folder (see DEPLOY.md).
"""
from pathlib import Path
from html import escape

ROOT = Path(__file__).parent
OUT = ROOT / "website"

# ------------------------------------------------------------------
# CONFIG — edit these before going live
# ------------------------------------------------------------------
CONFIG = {
    "site_url": "https://yourdomain.com",          # your live domain, no trailing slash
    "email": "admin@risejoe.com",                   # public contact email
    "phone_display": "+92 346 7969486",             # how the number is shown on the site
    "whatsapp": "923467969486",                     # WhatsApp number, digits only, with country code
    "instagram": "https://www.instagram.com/risejoe.official/",   # social links (leave "" to hide)
    "facebook": "https://www.facebook.com/profile.php?id=61575902971052",
    "tiktok": "https://www.tiktok.com/@risejoeecommerce",
    "linkedin": "https://www.linkedin.com/in/malik-yaseen-awan-5b06772ab/",  # founder's profile
    "address": "Plaza No. 26B, Pak Arab Housing Society, Lahore, Pakistan",
    "maps": "https://www.google.com/maps/search/?api=1&query=Plaza+26B+Pak+Arab+Housing+Society+Lahore",
    "hours": [("Monday – Friday", "By appointment only"), ("Saturday – Sunday", "Closed")],
}
WA = f"https://wa.me/{CONFIG['whatsapp']}"

# ------------------------------------------------------------------
# ICONS (24×24 line icons)
# ------------------------------------------------------------------
ICONS = {
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "arrow-ur": '<path d="M7 17L17 7M8 7h9v9"/>',
    "search": '<circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/>',
    "cap": '<path d="M2 9l10-5 10 5-10 5L2 9z"/><path d="M6 11v5c3 2.5 9 2.5 12 0v-5"/><path d="M22 9v6"/>',
    "handshake": '<path d="M11 17l2 2a2 2 0 0 0 3-3"/><path d="M14 14l2.5 2.5a2 2 0 0 0 3-3l-3.9-3.9a3 3 0 0 0-4.2 0l-.9.9a2 2 0 0 1-3-3L10.4 4.6a5 5 0 0 1 6.2-.6L21 7"/><path d="M3 7l4-3 4 2"/><path d="M3 7v6l7 7"/>',
    "chart": '<path d="M3 3v18h18"/><path d="M7 15l4-4 3 3 6-7"/><path d="M16 7h4v4"/>',
    "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/>',
    "server": '<rect x="3" y="4" width="18" height="7" rx="2"/><rect x="3" y="13" width="18" height="7" rx="2"/><path d="M7 7.5h.01M7 16.5h.01M11 7.5h6M11 16.5h6"/>',
    "warehouse": '<path d="M3 21V8l9-5 9 5v13"/><path d="M7 21v-8h10v8"/><path d="M7 17h10"/>',
    "box": '<path d="M21 8l-9-5-9 5 9 5 9-5z"/><path d="M3 8v8l9 5 9-5V8"/><path d="M12 13v8"/><path d="M7.5 5.5l9 5"/>',
    "stack": '<path d="M12 3l9 5-9 5-9-5 9-5z"/><path d="M3 13l9 5 9-5"/><path d="M3 17l9 5 9-5"/>',
    "pulse": '<path d="M3 12h4l3-8 4 16 3-8h4"/>',
    "building": '<rect x="4" y="3" width="16" height="18" rx="1"/><path d="M9 7h1M14 7h1M9 11h1M14 11h1M9 15h1M14 15h1M10 21v-3h4v3"/>',
    "flag": '<path d="M4 21V4"/><path d="M4 4h13l-2 4 2 4H4"/>',
    "key": '<circle cx="8" cy="15" r="4"/><path d="M11 12l9-9M17 6l3 3M14 9l2 2"/>',
    "store": '<path d="M3 9l1.5-5h15L21 9"/><path d="M3 9a3 3 0 0 0 6 0 3 3 0 0 0 6 0 3 3 0 0 0 6 0"/><path d="M5 12v9h14v-9"/><path d="M10 21v-5h4v5"/>',
    "code": '<path d="M8 8l-5 4 5 4M16 8l5 4-5 4M14 4l-4 16"/>',
    "star": '<path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1-4.4-4.3 6.1-.9L12 3z"/>',
    "users": '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0"/><circle cx="17" cy="9" r="2.5"/><path d="M16 14.5a5 5 0 0 1 5.5 5"/>',
    "target": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',
    "route": '<circle cx="6" cy="19" r="2"/><circle cx="18" cy="5" r="2"/><path d="M8 19h8a3 3 0 0 0 0-6H8a3 3 0 0 1 0-6h8"/>',
    "shield": '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6l8-3z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>',
    "pin": '<path d="M12 21s-7-6.2-7-12a7 7 0 0 1 14 0c0 5.8-7 12-7 12z"/><circle cx="12" cy="9" r="2.5"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>',
    "phone": '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "chat": '<path d="M21 12a8 8 0 0 1-11.8 7L4 20l1-4.6A8 8 0 1 1 21 12z"/><path d="M8.5 12h.01M12 12h.01M15.5 12h.01"/>',
    "plane": '<path d="M10.5 13.5L3 11l1.5-1.5 8 1 4-4.5c1-1 2.8-1.2 3.5-.5s.5 2.5-.5 3.5l-4.5 4 1 8L14.5 21l-2.5-7.5"/>',
    "ship": '<path d="M3 17l2 4h14l2-4-9-3-9 3z"/><path d="M5 15V9h14v6"/><path d="M12 9V4M9 6h6"/>',
    "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7.5h.01"/>',
    "spark": '<path d="M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5L18 18M6 18l2.5-2.5M15.5 8.5L18 6"/>',
    "layers": '<path d="M12 3l9 5-9 5-9-5 9-5z"/><path d="M3 12l9 5 9-5"/>',
    "lock": '<rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
    "doc": '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8l-5-5z"/><path d="M14 3v5h5M9 13h6M9 17h6"/>',
    "check": '<path d="M5 12.5l4.5 4.5L19 7"/>',
    "seed": '<path d="M12 21v-9"/><path d="M12 12C12 7 8 4 3 4c0 5 4 8 9 8z"/><path d="M12 14c0-4 3-7 8-7 0 4-3 7-8 7z"/>',
    "insta": '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><path d="M17.5 6.5h.01"/>',
    "fb": '<path d="M14 8h3V4h-3a4 4 0 0 0-4 4v3H7v4h3v6h4v-6h3l1-4h-4V8z"/>',
    "tiktok": '<path d="M14 3v11.5a3.5 3.5 0 1 1-3.5-3.5"/><path d="M14 3c.4 2.6 2.4 4.6 5 5"/>',
    "in": '<rect x="3" y="3" width="18" height="18" rx="3"/><path d="M8 10v7M8 7v.01M12 17v-4a2 2 0 0 1 4 0v4M12 10v7"/>',
}
WA_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M17.5 14.4c-.3-.1-1.8-.9-2-1-.3-.1-.5-.1-.7.1-.2.3-.8 1-.9 1.2-.2.2-.3.2-.6.1-.3-.1-1.3-.5-2.4-1.5-.9-.8-1.5-1.8-1.7-2.1-.2-.3 0-.5.1-.6l.5-.5.3-.5c.1-.2 0-.4 0-.5l-.9-2.2c-.2-.6-.5-.5-.7-.5h-.6c-.2 0-.5.1-.8.4-.3.3-1 1-1 2.5s1.1 2.9 1.2 3.1c.1.2 2.1 3.2 5.1 4.5 2.5 1 3 .8 3.6.7.6-.1 1.8-.7 2-1.4.2-.7.2-1.3.2-1.4-.1-.1-.3-.2-.6-.3zM12 21.8c-1.8 0-3.5-.5-5-1.4l-.4-.2-3.7 1 1-3.6-.2-.4A9.8 9.8 0 1 1 12 21.8zM12 0C5.4 0 0 5.4 0 12c0 2.1.6 4.2 1.6 6L0 24l6.2-1.6A12 12 0 1 0 12 0z"/></svg>'


def icon(name, cls=""):
    c = f' class="{cls}"' if cls else ""
    return (f'<svg{c} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>')


def lines(*parts):
    return "".join(f'<span class="line-mask"><span class="line-inner">{p}</span></span>' for p in parts)


def btn(label, href, kind="gold", extra="", ic="arrow-ur"):
    return (f'<a class="btn btn--{kind}" href="{href}" data-magnetic="0.25"{extra}>'
            f'<span>{label}{icon(ic)}</span></a>')


# ------------------------------------------------------------------
# SHARED DATA
# ------------------------------------------------------------------
COUNTRIES = ["Pakistan", "United Kingdom", "United States", "Australia", "Canada",
             "United Arab Emirates", "Saudi Arabia", "Other"]
PLATFORMS = ["Amazon", "eBay", "Etsy", "Walmart", "Shopify", "TikTok Shop", "Temu", "Other"]
MARKETS5 = ["United Kingdom", "United States", "Australia", "Canada", "Pakistan"]
MARKETS4 = ["United Kingdom", "United States", "Australia", "Canada"]

NAV = [("Home", "index.html", "home"), ("About", "about.html", "about"),
       ("Students", "students.html", "students"), ("Clients", "clients.html", "clients"),
       ("Investors", "investors.html", "investors"), ("Services", "services.html", "services"),
       ("Contact", "contact.html", "contact")]

CATEGORIES = [("all", "All services"), ("growth", "Marketplace growth"), ("company", "Company & accounts"),
              ("tech", "Tech & infrastructure"), ("supply", "Logistics & supply")]

# ------------------------------------------------------------------
# SERVICES
# ------------------------------------------------------------------
SERVICES = [
    {
        "slug": "marketplace-account-setup", "icon": "store", "wide": True,
        "title": "Ecommerce Marketplace Account Setup",
        "short_title": "Marketplace Account Setup",
        "tag": "Setup & onboarding", "cats": "company growth",
        "keywords": "amazon ebay etsy walmart shopify tiktok temu seller account store onboarding verification",
        "short": "Guided seller and store account creation on Amazon, eBay, Etsy, Walmart, Shopify, TikTok Shop, Temu and more.",
        "lead": "Guided, compliant seller and store onboarding for the world's leading marketplaces, from first application to a launch-ready storefront.",
        "overview": [
            "Opening a seller account is the first real step of any e-commerce business, and often the most confusing. Every marketplace has its own eligibility, identity, business and ownership requirements, and they differ again by country.",
            "Our team walks you through the right platform for your goals, prepares you for each stage of registration, helps you troubleshoot setup and verification difficulties, and gets your store configured for launch. We follow each platform's rules precisely and never use shortcuts that could put your business at risk.",
        ],
        "benefits": [
            ("Every major marketplace", "Amazon, eBay, Etsy, Walmart Marketplace, Shopify, TikTok Shop, Temu and other supported platforms, all under one team."),
            ("Country-aware guidance", "Requirements change by jurisdiction. We prepare you for the rules that apply to your location and business type."),
            ("Verification support", "Clear help preparing documents and understanding each verification step, so setup issues are resolved properly."),
            ("Launch-ready store", "After approval we help configure settings, policies and storefront basics so you can start listing with confidence."),
        ],
        "steps": [
            ("Choose platform & country", "Tell us where you want to sell and whether you are starting fresh or growing an existing business."),
            ("Eligibility review", "We review the platform's requirements for your status and list exactly what you will need."),
            ("Guided application", "Step-by-step support through registration, documentation and any verification stages."),
            ("Store configuration", "Once your account is live, we help set up your store so it's ready for products and orders."),
        ],
        "chips_title": "Supported marketplaces",
        "chips": ["Amazon", "eBay", "Etsy", "Walmart Marketplace", "Shopify", "TikTok Shop", "Temu", "Other supported platforms"],
        "note": "Account approval is always the marketplace's decision. We provide guidance and preparation; we never guarantee approval, and we never offer account rental, identity lending or verification workarounds.",
        "faqs": [
            ("Which marketplace should I start with?", "It depends on your products, target country, budget and experience. During your enquiry we recommend the platform (or combination) that best fits your goals."),
            ("Can you help if my verification is stuck?", "Yes. Describe the difficulty in the form and we'll review what the platform is asking for and guide you through providing the correct information."),
            ("Do you set up accounts for businesses as well as individuals?", "Yes. We support both individual and registered business sellers, following each platform's ownership and identity rules."),
            ("Will you need my passwords?", "No. We never ask for passwords, OTP codes or verification credentials. You stay in full control of your account at all times."),
        ],
        "fields": [
            {"t": "check", "n": "platforms", "l": "Platform(s)", "o": PLATFORMS, "r": True, "full": True},
            {"t": "select", "n": "jurisdiction", "l": "Jurisdiction / country of registration", "o": COUNTRIES, "r": True},
            {"t": "radio", "n": "seller_status", "l": "You are registering as", "o": ["Individual", "Business"], "r": True},
            {"t": "radio", "n": "business_stage", "l": "Business type", "o": ["New business", "Existing business"], "r": True},
            {"t": "select", "n": "registration_stage", "l": "Current registration stage", "o": ["Not started", "Preparing documents", "Application submitted", "Under verification", "Stuck — need help", "Account live, need store setup"], "r": True},
            {"t": "textarea", "n": "difficulties", "l": "Describe any setup or verification difficulties", "ph": "What has happened so far, and where are you stuck?", "full": True},
            {"t": "radio", "n": "contact_method", "l": "Best way to contact you", "o": ["WhatsApp", "Email", "Phone call"], "full": True},
        ],
    },
    {
        "slug": "free-account-checkup", "icon": "pulse", "wide": True,
        "title": "Free Ecommerce Account Consultation & Checkup",
        "short_title": "Free Account Checkup",
        "tag": "Free · All marketplaces", "cats": "growth",
        "keywords": "free consultation audit diagnostic no sales low sales account health listing ppc ads conversion",
        "short": "Not getting sales? Get a free expert diagnostic of your listings, pricing, visibility and account health, on any marketplace.",
        "lead": "Not getting the sales you expected? Get a free expert review of your store on Amazon, eBay, Etsy, Walmart, TikTok Shop, Shopify or any supported marketplace.",
        "overview": [
            "Many sellers do everything they believe is right and still see few or no orders. The cause is often hidden: listings that don't convert, pricing that misses the market, weak visibility, account health warnings, fulfilment problems or ads that burn budget.",
            "Our free initial consultation looks at your situation and gives you practical, prioritised recommendations. It's an honest first assessment from people who work on marketplaces every day. It's not a sales pitch, and not a promise of results.",
        ],
        "benefits": [
            ("Listing & conversion review", "Titles, images, content, keywords and pricing assessed against what actually converts in your category."),
            ("Visibility & traffic", "Why buyers may not be finding you, from search placement to ads structure and traffic sources."),
            ("Account health & policy", "A look at notices, defects, performance metrics and policy warnings, with steps to address them."),
            ("A practical action plan", "Clear, prioritised recommendations you can act on yourself, or with our team if you choose."),
        ],
        "steps": [
            ("Tell us the issue", "Share your platform, market and the main problem: no sales, low sales, account health, listings, ads or something else."),
            ("Expert review", "An account specialist reviews the details you provide and any public listing information."),
            ("Consultation", "We walk you through what we found and what is most likely holding your account back."),
            ("Recommendations", "You receive practical next steps, with optional support if you want us to help implement them."),
        ],
        "chips_title": "Checkups available for",
        "chips": ["Amazon", "eBay", "Etsy", "Walmart", "Shopify", "TikTok Shop", "Temu", "Other marketplaces"],
        "note": "This is an initial assessment with practical recommendations. It is not a guarantee of sales. We will never request passwords, OTP codes or sensitive credentials.",
        "hero_ctas": [("Get Free Account Checkup", "#enquiry", "gold", "main_issue=No sales"), ("Ask an Account Expert", "#enquiry", "ghost", "")],
        "faqs": [
            ("Is the checkup really free?", "Yes. The initial consultation and diagnostic checkup is free. If you'd like ongoing help afterwards, we'll explain the options clearly, with no obligation."),
            ("Is this only for Amazon sellers?", "No. We review accounts across all supported marketplaces, including eBay, Etsy, Walmart, Shopify, TikTok Shop and Temu."),
            ("Do you need access to my account?", "No. We never ask for passwords or OTPs. We work from the information you share and publicly visible listings."),
            ("How quickly will I hear back?", "Once you submit the form you'll receive an email confirmation, and the account team will contact you to arrange your consultation."),
        ],
        "fields": [
            {"t": "select", "n": "platform", "l": "Platform", "o": PLATFORMS, "r": True},
            {"t": "select", "n": "market", "l": "Marketplace / country", "o": MARKETS5 + ["Other"], "r": True},
            {"t": "select", "n": "account_age", "l": "Account age", "o": ["Less than 3 months", "3–12 months", "1–3 years", "3+ years"], "r": True},
            {"t": "select", "n": "account_status", "l": "Account status", "o": ["Active", "Active with warnings", "Under review", "Restricted / suspended", "Not sure"], "r": True},
            {"t": "radio", "n": "main_issue", "l": "Main issue", "o": ["No sales", "Low sales", "Account health", "Listings", "Ads", "Other"], "r": True, "full": True},
            {"t": "text", "n": "approx_performance", "l": "Approximate performance", "ph": "e.g. 20 listings, ~5 orders/month", "full": True},
            {"t": "textarea", "n": "issue_description", "l": "Short description of the problem", "ph": "Tell us what's happening and what you've tried so far.", "r": True, "full": True},
        ],
    },
    {
        "slug": "product-hunting-sourcing", "icon": "search",
        "title": "Product Hunting & Product Sourcing",
        "short_title": "Product Hunting & Sourcing",
        "tag": "Research → procurement", "cats": "growth supply",
        "keywords": "product research hunting sourcing supplier wholesaler manufacturer china uk usa moq landed cost roi",
        "short": "From data-driven product research to supplier quotes and landed costs, for any marketplace you sell on.",
        "lead": "A complete research-to-procurement service for products on Amazon, eBay, Etsy, Walmart, Shopify, TikTok Shop and other marketplaces.",
        "overview": [
            "The right product is the foundation of a profitable store. Our product hunting covers market research, demand, competition, selling-price analysis and preliminary margin and ROI estimates, so decisions are based on evidence rather than guesswork.",
            "Already chosen a product? Our sourcing team finds distributor, wholesaler, manufacturer and China/UK/USA supplier options, collects quotes and MOQs, checks sample and quality requirements, compares shipping methods and builds landed-cost estimates. Choose hunting, sourcing, or both together.",
        ],
        "benefits": [
            ("Demand & competition data", "Market research showing what sells, how competitive it is, and where the opportunity really is."),
            ("Margin & ROI estimates", "Selling-price analysis with preliminary margin and ROI estimates before you commit capital."),
            ("Verified supplier options", "Distributors, wholesalers and manufacturers across China, the UK and the USA, with quotes and MOQs."),
            ("Landed-cost clarity", "Shipping methods, sample and quality requirements and full landed-cost estimates in one view."),
        ],
        "steps": [
            ("Brief", "Tell us your platform, market, budget and whether you need hunting, sourcing, or both."),
            ("Research", "We analyse demand, competition, pricing and preliminary margins for candidate products."),
            ("Source", "We gather supplier options, quotes, MOQs, sample requirements and shipping routes."),
            ("Decide", "You receive a clear recommendation with landed-cost estimates to make a confident decision."),
        ],
        "options": [
            ("Product Hunting", "Market research, demand, competition, selling-price analysis and preliminary ROI estimates.", "Request Product Hunting", "request_type=hunt", "search"),
            ("Product Sourcing", "You already have a product. We find suppliers, quotes, MOQs, quality checks and landed costs.", "Source My Product", "request_type=source", "route"),
            ("Hunt & Source", "The complete journey, from finding a winning product to sourcing it at the right cost.", "Hunt & Source a Product", "request_type=both", "layers"),
        ],
        "chips_title": "For products sold on",
        "chips": ["Amazon", "eBay", "Etsy", "Walmart", "Shopify", "TikTok Shop", "Temu", "Other marketplaces"],
        "note": "Margin, ROI and lead-time figures are estimates for planning purposes and are not guaranteed outcomes.",
        "faqs": [
            ("Can I request sourcing only?", "Yes. If you've already selected a product, choose 'Source My Product' and share the product name, link or photos."),
            ("Which supplier regions do you work with?", "We look at distributors, wholesalers and manufacturers across China, the UK and the USA, and other suitable regions where it makes sense."),
            ("Is product hunting only for Amazon?", "No. We research products for any supported marketplace, including eBay, Etsy, Walmart, Shopify and TikTok Shop."),
            ("Are the ROI estimates guaranteed?", "No. They're preliminary planning estimates based on current market data, designed to help you make informed decisions."),
        ],
        "fields": [
            {"t": "mode", "n": "request_type", "l": "What do you need?", "o": [("hunt", "Product Hunting"), ("source", "Product Sourcing"), ("both", "Hunt & Source")], "r": True},
            {"t": "group", "l": "Product hunting brief", "when": "request_type:hunt|both"},
            {"t": "select", "n": "target_platform", "l": "Target platform", "o": PLATFORMS, "r": True, "when": "request_type:hunt|both"},
            {"t": "select", "n": "marketplace_country", "l": "Marketplace / country", "o": MARKETS5 + ["Other"], "r": True, "when": "request_type:hunt|both"},
            {"t": "text", "n": "category_niche", "l": "Category or niche", "ph": "e.g. Home & kitchen, pet supplies", "when": "request_type:hunt|both"},
            {"t": "select", "n": "hunting_budget", "l": "Investment budget", "o": ["Under $1,000", "$1,000 – $5,000", "$5,000 – $15,000", "$15,000+", "Not sure yet"], "when": "request_type:hunt|both"},
            {"t": "text", "n": "desired_price_range", "l": "Desired selling-price range", "ph": "e.g. $20 – $45", "when": "request_type:hunt|both"},
            {"t": "text", "n": "target_roi", "l": "Target ROI (if any)", "ph": "e.g. 30%", "when": "request_type:hunt|both"},
            {"t": "text", "n": "restrictions", "l": "Restrictions", "ph": "Brands, categories or materials to avoid", "when": "request_type:hunt|both"},
            {"t": "radio", "n": "existing_ideas", "l": "Do you already have product ideas?", "o": ["Yes", "No"], "when": "request_type:hunt|both"},
            {"t": "textarea", "n": "research_requirements", "l": "Research requirements", "ph": "Anything specific you want us to analyse?", "full": True, "when": "request_type:hunt|both"},
            {"t": "group", "l": "Product sourcing brief", "when": "request_type:source|both"},
            {"t": "text", "n": "product_name_link", "l": "Product name or link", "r": True, "ph": "Paste a product link or name", "when": "request_type:source"},
            {"t": "text", "n": "product_photos", "l": "Link to product photos (optional)", "ph": "Google Drive, Dropbox, etc.", "when": "request_type:source"},
            {"t": "text", "n": "quantity", "l": "Quantity", "ph": "e.g. 500 units", "r": True, "when": "request_type:source|both"},
            {"t": "text", "n": "target_cost", "l": "Target unit cost", "ph": "e.g. $4.50 per unit", "when": "request_type:source|both"},
            {"t": "check", "n": "supplier_region", "l": "Desired supplier region", "o": ["China", "United Kingdom", "United States", "Best available"], "when": "request_type:source|both"},
            {"t": "select", "n": "destination_market", "l": "Destination market", "o": MARKETS5 + ["Other"], "r": True, "when": "request_type:source|both"},
            {"t": "select", "n": "logistics_preference", "l": "Logistics preference", "o": ["Air (faster)", "Sea (lower cost)", "Courier / express", "Not sure — advise me"], "when": "request_type:source|both"},
            {"t": "select", "n": "sourcing_timeline", "l": "Timeline", "o": ["As soon as possible", "Within 1 month", "1–3 months", "Flexible"], "when": "request_type:source|both"},
        ],
    },
    {
        "slug": "stock-wholesale-supply", "icon": "stack",
        "title": "Stock Products & Wholesale Supply",
        "short_title": "Stock & Wholesale Supply",
        "tag": "Ready stock & custom", "cats": "supply",
        "keywords": "stock products wholesale inventory ready stock custom sourcing distributor uk usa supply",
        "short": "Request ready stock and wholesale inventory, or have us source your own selected product from UK/USA suppliers.",
        "lead": "Ready stock and wholesale inventory for eligible markets, plus custom sourcing of your selected product from UK and USA suppliers.",
        "overview": [
            "Speed matters in e-commerce. Our stock and wholesale service gives you access to available or requestable stock products and wholesale inventory for eligible markets, helping you launch or restock without long sourcing cycles.",
            "Have a specific product in mind? Share the link or image and we'll source it from UK/USA distributors, wholesalers, manufacturers or other suitable suppliers, matched to your quantity, budget and delivery date.",
        ],
        "benefits": [
            ("Ready & requestable stock", "Access to available stock products and wholesale inventory for eligible marketplaces."),
            ("Custom product requests", "Send us your chosen product and we'll find the right supplier for it."),
            ("UK & USA supplier network", "Distributors, wholesalers and manufacturers across key Western markets."),
            ("Brand-safe sourcing", "Brand restrictions and marketplace requirements are taken into account from the start."),
        ],
        "steps": [
            ("Share your request", "Ready stock or a custom product: tell us the category, quantity and target country."),
            ("Supplier matching", "We match your request to available inventory or suitable distributors and wholesalers."),
            ("Quote & confirm", "You receive availability, pricing and delivery options to review and confirm."),
            ("Delivery", "Stock is prepared for delivery to your preferred destination or fulfilment centre."),
        ],
        "options": [
            ("Ready Stock", "Browse and request available stock products and wholesale inventory for your market.", "Request Ready Stock", "request_kind=Ready stock", "box"),
            ("Custom Product Sourcing", "Send a product link or image and we'll source it from UK/USA suppliers.", "Source a Custom Product", "request_kind=Custom product sourcing", "route"),
        ],
        "chips_title": "Eligible markets",
        "chips": ["United Kingdom", "United States", "Australia", "Canada"],
        "note": "Stock availability, pricing and delivery dates are confirmed per request. Brand and category restrictions may apply.",
        "faqs": [
            ("Can I see a list of available stock?", "Share your category and target market and we'll send current available and requestable stock options that match your needs."),
            ("Can you source a specific product I found?", "Yes. Send us the product link or image, the quantity and target country, and we'll look for suitable UK/USA suppliers."),
            ("Do you handle brand-restricted products?", "Tell us about any brand restrictions upfront. We only source in line with marketplace and brand requirements."),
            ("What is the minimum order?", "Minimums depend on the supplier and product. We'll confirm MOQ and pricing in your quote."),
        ],
        "fields": [
            {"t": "radio", "n": "request_kind", "l": "Request type", "o": ["Ready stock", "Custom product sourcing"], "r": True, "full": True},
            {"t": "text", "n": "product_link", "l": "Product link or image link", "ph": "Paste a URL", "full": True},
            {"t": "text", "n": "category", "l": "Category", "ph": "e.g. Health & beauty", "r": True},
            {"t": "select", "n": "target_country", "l": "Target country", "o": MARKETS4 + ["Other"], "r": True},
            {"t": "text", "n": "quantity", "l": "Quantity", "ph": "e.g. 1,000 units", "r": True},
            {"t": "select", "n": "budget", "l": "Budget", "o": ["Under $1,000", "$1,000 – $5,000", "$5,000 – $20,000", "$20,000+"]},
            {"t": "date", "n": "preferred_delivery", "l": "Preferred delivery date"},
            {"t": "text", "n": "brand_restrictions", "l": "Brand restrictions", "ph": "Any brands to include or avoid?"},
        ],
    },
    {
        "slug": "warehousing-fulfilment", "icon": "warehouse",
        "title": "Warehousing & Fulfilment",
        "short_title": "Warehousing & Fulfilment",
        "tag": "USA · UK · AU · CA", "cats": "supply",
        "keywords": "warehouse storage inventory pick pack shipping fulfilment prep 3pl usa uk",
        "short": "Warehouse storage, inventory management, pick & pack and shipping support in key international markets.",
        "lead": "Warehouse storage, inventory management, pick & pack and shipping support, so your products move smoothly from supplier to customer.",
        "overview": [
            "Great products need reliable logistics. Our warehousing and fulfilment support helps you store inventory close to your customers, keep stock levels accurate and get orders out the door efficiently.",
            "Whether you need a staging point for marketplace fulfilment centres or full pick, pack and ship for your own store orders, we'll match your requirements to the right warehouse solution in your target market.",
        ],
        "benefits": [
            ("Secure storage", "Warehouse space in key markets to hold your inventory close to buyers."),
            ("Inventory management", "Accurate stock tracking so you always know what is available and what to reorder."),
            ("Pick, pack & ship", "Orders prepared and dispatched with care, ready for your customers or marketplace centres."),
            ("Flexible volumes", "Support that scales from a first shipment to regular high-volume inbound stock."),
        ],
        "steps": [
            ("Share requirements", "Tell us your market, product type, stock volume and fulfilment needs."),
            ("Solution & quote", "We propose a warehouse and fulfilment plan matched to your requirements."),
            ("Inbound stock", "Your products are received, checked and stored in the agreed facility."),
            ("Fulfilment", "Orders are picked, packed and shipped with ongoing inventory updates."),
        ],
        "chips_title": "Warehouse markets",
        "chips": ["United States", "United Kingdom", "Australia", "Canada"],
        "note": "Warehouse coverage, capacity and pricing are confirmed per enquiry.",
        "faqs": [
            ("Which countries do you offer warehousing in?", "We support warehousing enquiries for the USA, UK, Australia and Canada. Exact coverage is confirmed based on your requirements."),
            ("Can you prepare stock for marketplace fulfilment centres?", "Yes. Let us know which marketplace and fulfilment programme you use and we'll plan around its requirements."),
            ("Do you handle returns?", "Returns handling can be included. Select it in your fulfilment requirements and we'll confirm the options."),
            ("Is there a minimum volume?", "Requirements vary by facility. Share your estimated volume and we'll recommend the most suitable option."),
        ],
        "fields": [
            {"t": "radio", "n": "warehouse_market", "l": "Warehouse market", "o": MARKETS4, "r": True, "full": True},
            {"t": "text", "n": "product_type", "l": "Product type", "ph": "e.g. Small electronics", "r": True},
            {"t": "select", "n": "stock_volume", "l": "Estimated stock volume", "o": ["Under 500 units", "500 – 2,000 units", "2,000 – 10,000 units", "10,000+ units", "Pallets / bulk"], "r": True},
            {"t": "check", "n": "fulfilment_requirements", "l": "Fulfilment requirements", "o": ["Storage", "Inventory management", "Pick & pack", "Shipping", "Marketplace prep", "Returns"], "r": True, "full": True},
        ],
    },
    {
        "slug": "website-development", "icon": "code",
        "title": "Website Design & Development",
        "short_title": "Website Development",
        "tag": "Design · Build · Maintain", "cats": "tech",
        "keywords": "website design development ecommerce store shopify woocommerce landing page redesign maintenance",
        "short": "Custom business websites, high-converting ecommerce stores, landing pages, redesigns and ongoing maintenance.",
        "lead": "Custom business websites, ecommerce stores and landing pages designed to look premium, load fast and convert visitors into customers.",
        "overview": [
            "Your website is often the first impression of your brand. We design and build websites that communicate credibility, guide visitors clearly and are built for performance on every device.",
            "From a full ecommerce store to a focused landing page, a complete redesign or ongoing maintenance, our team handles strategy, design and development, and keeps your site running smoothly after launch.",
        ],
        "benefits": [
            ("Conversion-focused design", "Layouts, messaging and calls to action built around what makes visitors buy or enquire."),
            ("Ecommerce expertise", "Stores built by a team that understands products, checkout and marketplace selling."),
            ("Fast & responsive", "Optimised for speed, SEO and a polished experience on mobile, tablet and desktop."),
            ("Ongoing care", "Maintenance, updates and improvements so your site keeps performing."),
        ],
        "steps": [
            ("Discovery", "We learn about your business, audience, platform preference and goals."),
            ("Design", "A tailored design direction for your brand, reviewed with you before build."),
            ("Development", "We build, test and optimise across devices and browsers."),
            ("Launch & support", "Go live with confidence, with maintenance options after launch."),
        ],
        "chips_title": "We build",
        "chips": ["Business websites", "Ecommerce stores", "Shopify", "WordPress / WooCommerce", "Custom builds", "Landing pages", "Redesigns", "Maintenance"],
        "note": "Final scope, pricing and timeline are confirmed in your proposal.",
        "faqs": [
            ("Which platforms do you build on?", "We build on Shopify, WordPress/WooCommerce and custom code, and recommend what best fits your business and budget."),
            ("Can you redesign my existing website?", "Yes. Share your current site and reference sites you like, and we'll propose a redesign approach."),
            ("Do you offer maintenance after launch?", "Yes. We offer ongoing maintenance, updates and improvements."),
            ("How long does a website take?", "It depends on scope. A landing page can be quick, while a full store takes longer. Your timeline is confirmed in the proposal."),
        ],
        "fields": [
            {"t": "radio", "n": "project_type", "l": "Project type", "o": ["Business website", "Ecommerce store", "Landing page", "Redesign", "Maintenance"], "r": True, "full": True},
            {"t": "text", "n": "business_type", "l": "Business type", "ph": "e.g. Fashion brand, consultancy", "r": True},
            {"t": "select", "n": "desired_platform", "l": "Desired platform", "o": ["Shopify", "WordPress / WooCommerce", "Custom build", "Not sure — advise me"]},
            {"t": "text", "n": "reference_sites", "l": "Reference sites", "ph": "Websites you like", "full": True},
            {"t": "textarea", "n": "features", "l": "Features needed", "ph": "e.g. Online payments, booking, blog, multilingual…", "full": True},
            {"t": "select", "n": "budget_range", "l": "Budget range", "o": ["Under $500", "$500 – $1,500", "$1,500 – $5,000", "$5,000+", "Not sure"]},
            {"t": "select", "n": "timeline", "l": "Timeline", "o": ["ASAP", "Within 1 month", "1–3 months", "Flexible"]},
        ],
    },
    {
        "slug": "vps-services", "icon": "server",
        "title": "VPS Services",
        "short_title": "VPS Services",
        "tag": "UK · USA · AU · CA · PK", "cats": "tech",
        "keywords": "vps virtual private server hosting remote desktop region uk usa australia canada pakistan",
        "short": "Reliable virtual private servers in the UK, USA, Australia, Canada and Pakistan, configured for your needs.",
        "lead": "Reliable virtual private servers in supported country locations, configured for e-commerce operations and business workloads.",
        "overview": [
            "A dependable VPS gives your business a stable, dedicated environment for running tools, hosting applications and managing operations from the right region.",
            "Choose your preferred location, plan and duration, and our VPS team will confirm specifications, availability and pricing, then get your server ready. Order directly or request a custom quote.",
        ],
        "benefits": [
            ("Multiple regions", "Locations in the UK, USA, Australia, Canada and Pakistan, subject to availability."),
            ("Flexible plans", "Plans from starter to performance, with custom specifications on request."),
            ("Flexible durations", "Monthly, quarterly, half-yearly or annual terms to suit your needs."),
            ("Dedicated VPS team", "Your request goes straight to our VPS specialists for setup and support."),
        ],
        "steps": [
            ("Choose region", "Select the country location that suits your operations."),
            ("Pick a plan", "Choose a plan tier and duration, or describe custom requirements."),
            ("Confirm", "Our VPS team confirms specification, availability and pricing."),
            ("Go live", "Your server is provisioned and access details are shared securely."),
        ],
        "chips_title": "Available regions",
        "chips": ["United Kingdom", "United States", "Australia", "Canada", "Pakistan"],
        "note": "Plan specifications, pricing and regional availability are confirmed by our VPS team at the time of order.",
        "faqs": [
            ("Which VPS locations are available?", "We offer VPS in the UK, USA, Australia, Canada and Pakistan, subject to current availability."),
            ("Can I get a custom specification?", "Yes. Choose 'Custom' and describe your CPU, RAM, storage or OS requirements."),
            ("How quickly is a VPS ready?", "Once your order is confirmed, our team will share the expected setup time for your chosen region."),
            ("Can I order or just request a quote?", "Both. Select 'Place an order' or 'Request a quote' in the form."),
        ],
        "fields": [
            {"t": "radio", "n": "region", "l": "Region", "o": MARKETS5, "r": True, "full": True},
            {"t": "select", "n": "plan", "l": "Plan", "o": ["Starter", "Business", "Performance", "Custom specification"], "r": True},
            {"t": "select", "n": "duration", "l": "Duration", "o": ["1 month", "3 months", "6 months", "12 months"], "r": True},
            {"t": "textarea", "n": "specification", "l": "Specification / use case", "ph": "e.g. 4 GB RAM, Windows, for store management tools", "full": True},
            {"t": "radio", "n": "order_type", "l": "I'd like to", "o": ["Place an order", "Request a quote"], "r": True, "full": True},
        ],
    },
    {
        "slug": "distributor-wholesale-accounts", "icon": "key",
        "title": "Distributor & Wholesale Account Creation",
        "short_title": "Distributor Accounts",
        "tag": "Trade accounts", "cats": "company supply",
        "keywords": "distributor wholesale trade account application reseller supplier uk usa",
        "short": "Assistance applying for genuine distributor and wholesaler trade accounts for your business.",
        "lead": "Assistance preparing and applying for genuine distributor and wholesaler trade accounts, the foundation of reliable, profitable supply.",
        "overview": [
            "Buying direct from distributors and wholesalers gives you better pricing, authentic stock and a more reliable supply chain. Getting approved, however, requires the right business setup and documentation.",
            "We help you understand what distributors look for, prepare your business details and company documents, and submit strong applications to suitable trade suppliers in your product category.",
        ],
        "benefits": [
            ("Right supplier fit", "We identify distributors and wholesalers that match your category and market."),
            ("Document preparation", "Guidance on the company documents and details trade suppliers typically require."),
            ("Stronger applications", "Applications presented clearly and professionally to improve your chances."),
            ("Long-term supply", "Build relationships with genuine suppliers for consistent, authentic inventory."),
        ],
        "steps": [
            ("Business review", "Share your business details, country, product category and purchasing volume."),
            ("Supplier shortlist", "We shortlist suitable distributors and wholesalers for your category."),
            ("Application support", "We guide you through preparing and submitting each application."),
            ("Follow-up", "We help you respond to any supplier questions during review."),
        ],
        "chips_title": "Typical requirements",
        "chips": ["Company registration", "VAT / sales tax ID", "Proof of address", "Bank details", "Reseller certificate", "Purchasing volume"],
        "note": "Account acceptance remains the distributor's or wholesaler's decision. We help you apply properly; we do not guarantee approval.",
        "faqs": [
            ("Do I need a registered company?", "Most distributors require a registered business. If you don't have one yet, see our LTD and LLC registration assistance."),
            ("Which countries do you support?", "We commonly assist with UK and USA distributors, and other markets on request."),
            ("Can you guarantee approval?", "No. Approval is always the supplier's decision, but a well-prepared application gives you the best chance."),
            ("What should I prepare?", "Typically company registration documents, tax IDs, proof of address and an estimate of your purchasing volume."),
        ],
        "fields": [
            {"t": "text", "n": "business_name", "l": "Business name", "r": True},
            {"t": "select", "n": "company_type", "l": "Company type", "o": ["UK LTD", "US LLC", "Sole trader", "Other", "Not registered yet"], "r": True},
            {"t": "select", "n": "supplier_country", "l": "Supplier country", "o": ["United Kingdom", "United States", "Other"], "r": True},
            {"t": "text", "n": "product_category", "l": "Product category", "ph": "e.g. Toys, grocery, beauty", "r": True},
            {"t": "check", "n": "documents_available", "l": "Company documents available", "o": ["Company registration", "VAT / sales tax ID", "Proof of address", "Bank statement", "Reseller certificate"], "full": True},
            {"t": "select", "n": "purchasing_volume", "l": "Intended monthly purchasing volume", "o": ["Under $2,000", "$2,000 – $10,000", "$10,000 – $50,000", "$50,000+"], "r": True, "full": True},
        ],
    },
    {
        "slug": "ltd-company-registration", "icon": "building", "wide": True,
        "title": "LTD Company Registration Assistance",
        "short_title": "UK LTD Registration",
        "tag": "United Kingdom", "cats": "company",
        "keywords": "uk limited company ltd registration companies house onboarding",
        "short": "UK limited company registration support and onboarding guidance for e-commerce businesses.",
        "lead": "UK limited company registration support and onboarding guidance, giving your e-commerce business a credible, professional foundation.",
        "overview": [
            "A UK limited company is a popular foundation for selling on international marketplaces and opening trade accounts. We help you understand the registration process and prepare everything needed.",
            "Our team supports you through registration requirements and related onboarding guidance. Approvals sit with the relevant authorities, and legal or tax advice should come from qualified professionals, and we'll point you in the right direction.",
        ],
        "benefits": [
            ("Clear process", "A step-by-step explanation of UK company registration requirements."),
            ("Preparation support", "Help gathering the details and information needed to register."),
            ("Onboarding guidance", "Practical next steps after registration for e-commerce operations."),
            ("Business-ready foundation", "A structure that supports marketplace and distributor applications."),
        ],
        "steps": [
            ("Requirements", "Share your company name ideas, directors and residency."),
            ("Preparation", "We guide you on the information and documents needed."),
            ("Registration support", "Assistance through the registration process with the relevant authority."),
            ("Onboarding", "Guidance on next steps for your e-commerce operations."),
        ],
        "chips_title": "Support covers",
        "chips": ["Registration requirements", "Company details", "Director information", "Onboarding guidance", "Next-step planning"],
        "note": "Registration approvals are made by the relevant authorities. Legal and tax advice remains with qualified professionals.",
        "faqs": [
            ("Can non-UK residents register a UK LTD?", "In many cases, yes. Requirements depend on your circumstances. Tell us your residency and we'll explain what applies."),
            ("Do you provide legal or tax advice?", "No. We provide registration assistance and guidance. For legal or tax advice, consult a qualified professional."),
            ("How long does registration take?", "Timing depends on the authority's processing. We'll share current expectations when we review your requirements."),
            ("Will an LTD help with marketplace accounts?", "A registered company is often useful for business seller accounts and distributor applications."),
        ],
        "fields": [
            {"t": "text", "n": "company_name_ideas", "l": "Proposed company name(s)", "full": True},
            {"t": "select", "n": "directors", "l": "Number of directors", "o": ["1", "2", "3+"], "r": True},
            {"t": "select", "n": "residency", "l": "Director residency", "o": ["UK resident", "Non-UK resident", "Mixed"], "r": True},
            {"t": "check", "n": "support_needed", "l": "Support needed", "o": ["Registration", "Registered address guidance", "Onboarding guidance", "Next steps for marketplaces"], "r": True, "full": True},
            {"t": "select", "n": "timeline", "l": "When do you want to register?", "o": ["Immediately", "Within 1 month", "1–3 months", "Just exploring"], "full": True},
        ],
    },
    {
        "slug": "llc-company-registration", "icon": "flag", "wide": True,
        "title": "LLC Company Registration Assistance",
        "short_title": "US LLC Registration",
        "tag": "United States", "cats": "company",
        "keywords": "us llc formation state wyoming delaware registration documentation",
        "short": "US LLC formation support, state selection guidance, documentation help and follow-up.",
        "lead": "US LLC formation support, from state selection and documentation guidance through to follow-up after filing.",
        "overview": [
            "A US LLC is a flexible structure for e-commerce businesses selling in the American market. Choosing the right state and preparing correct documentation are important first decisions.",
            "We support your state selection enquiry, guide you through documentation and follow up on progress. Filing outcomes and tax or legal treatment depend on applicable rules, so we'll always be clear about what we do and don't cover.",
        ],
        "benefits": [
            ("State selection guidance", "Understand the general differences between common formation states."),
            ("Documentation help", "Guidance on the information and documents required for formation."),
            ("Follow-up", "We stay with you through the process and next steps."),
            ("E-commerce ready", "A foundation suited to US marketplaces and supplier relationships."),
        ],
        "steps": [
            ("Enquiry", "Tell us your preferred state (or ask for guidance), members and residency."),
            ("Documentation", "We guide you on the details and documents needed for formation."),
            ("Formation support", "Assistance through the filing process."),
            ("Follow-up", "Next-step guidance for operating and selling."),
        ],
        "chips_title": "Common states enquired",
        "chips": ["Wyoming", "Delaware", "New Mexico", "Florida", "Texas", "Other states"],
        "note": "Filing outcomes and tax/legal treatment depend on applicable rules. Consult a qualified professional for legal or tax advice.",
        "faqs": [
            ("Which state should I choose?", "It depends on your situation. We explain the general considerations; for tax or legal advice, speak with a qualified professional."),
            ("Can non-US residents form an LLC?", "Often, yes. Tell us your residency and we'll explain the general process that applies."),
            ("Do you guarantee filing approval?", "No. Filing outcomes depend on the relevant authority and applicable rules."),
            ("What happens after formation?", "We provide guidance on typical next steps for running an e-commerce business."),
        ],
        "fields": [
            {"t": "select", "n": "preferred_state", "l": "Preferred state", "o": ["Wyoming", "Delaware", "New Mexico", "Florida", "Texas", "Other", "Not sure — need guidance"], "r": True},
            {"t": "select", "n": "members", "l": "Number of members", "o": ["1 (single-member)", "2", "3+"], "r": True},
            {"t": "select", "n": "residency", "l": "Member residency", "o": ["US resident", "Non-US resident", "Mixed"], "r": True},
            {"t": "check", "n": "support_needed", "l": "Support needed", "o": ["Formation", "State selection", "Documentation guidance", "Follow-up & next steps"], "r": True},
        ],
    },
]
SVC_BY_SLUG = {s["slug"]: s for s in SERVICES}


# ------------------------------------------------------------------
# LAYOUT
# ------------------------------------------------------------------
HEAD_SCRIPT = ("<script>(function(d){var r=d.documentElement;r.classList.add('js');"
               "if(!(window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches))r.classList.add('anim');"
               "try{if(sessionStorage.getItem('rj-loaded'))r.classList.add('no-preload');"
               "if(sessionStorage.getItem('rj-transition')){r.classList.add('is-entering');sessionStorage.removeItem('rj-transition');}}"
               "catch(e){r.classList.add('no-preload');}"
               "setTimeout(function(){if(!window.__rjReady){r.classList.remove('anim','is-entering');}},4000);"
               "})(document);</script>")


def header(active, p):
    on = ' class="is-active" aria-current="page"'
    links = "".join(
        f'<a href="{p}{href}"{on if key == active else ""}>{label}</a>'
        for label, href, key in NAV)
    mlinks = "".join(
        f'<a href="{p}{href}"><small>0{i+1}</small><span>{label}</span></a>'
        for i, (label, href, key) in enumerate(NAV))
    return f'''
<div class="progress" aria-hidden="true"><i></i></div>
<header class="header">
  <div class="container header__inner">
    <a class="brand" href="{p}index.html" aria-label="Rise Joe home">
      <img src="{p}assets/img/logo-mark.png" alt="" width="42" height="43">
      <span class="brand__text"><b>RISE JOE</b><small>E-COMMERCE AGENCY</small></span>
    </a>
    <nav class="nav" aria-label="Main">{links}</nav>
    <div class="header__cta">
      {btn("Free Checkup", p + "services/free-account-checkup.html", "gold", "", "arrow-ur").replace("btn--gold", "btn--gold btn--sm")}
      <button class="burger" aria-label="Open menu" aria-expanded="false"><i></i><i></i></button>
    </div>
  </div>
</header>
<div class="menu" aria-label="Mobile menu">
  <nav class="menu__links">{mlinks}</nav>
  <div class="menu__foot">
    <a class="btn btn--gold" href="{p}services/free-account-checkup.html"><span>Get a Free Account Checkup{icon("arrow-ur")}</span></a>
    <div>{escape(CONFIG["address"])}</div>
    <div><a href="{WA}" target="_blank" rel="noopener">WhatsApp {escape(CONFIG["phone_display"])}</a> · <a href="mailto:{CONFIG["email"]}">{CONFIG["email"]}</a></div>
  </div>
</div>'''


def footer(p):
    svc_links = "".join(f'<li><a href="{p}services/{s["slug"]}.html">{s["short_title"]}</a></li>' for s in SERVICES)
    socials = "".join(
        f'<a href="{CONFIG[k]}" target="_blank" rel="noopener" aria-label="{lab}">{icon(ic)}</a>'
        for k, ic, lab in (("instagram", "insta", "Instagram"), ("facebook", "fb", "Facebook"), ("tiktok", "tiktok", "TikTok"), ("linkedin", "in", "LinkedIn")) if CONFIG.get(k))
    hours = "".join(f"<li>{a}: {b}</li>" for a, b in CONFIG["hours"])
    return f'''
<footer class="footer">
  <div class="container">
    <div class="footer__grid">
      <div class="footer__brand">
        <a class="brand" href="{p}index.html"><img src="{p}assets/img/logo-mark.png" alt="" width="42" height="43"><span class="brand__text"><b>RISE JOE</b><small>E-COMMERCE AGENCY</small></span></a>
        <p>People. Products. Progress. A Lahore-based e-commerce agency helping students, sellers and investors build real businesses on global marketplaces.</p>
        <div class="socials">{socials}</div>
      </div>
      <div><p class="footer__title">Explore</p><ul>{"".join(f'<li><a href="{p}{h}">{l}</a></li>' for l, h, _ in NAV[1:])}</ul></div>
      <div><p class="footer__title">Services</p><ul>{svc_links}<li><a href="{p}services.html">All services →</a></li></ul></div>
      <div><p class="footer__title">Head Office</p><ul>
        <li>{escape(CONFIG["address"])}</li>
        <li><a href="{WA}" target="_blank" rel="noopener">WhatsApp: {escape(CONFIG["phone_display"])}</a></li>
        <li><a href="mailto:{CONFIG["email"]}">{CONFIG["email"]}</a></li>
        {hours}
      </ul></div>
    </div>
    <div class="footer__word" aria-hidden="true">RISE JOE</div>
    <div class="footer__bottom">
      <span>© <span data-year>2026</span> Rise Joe E-Commerce Agency. All rights reserved.</span>
      <span><a href="{p}privacy.html">Privacy Notice</a> &nbsp;·&nbsp; <a href="{p}terms.html">Terms</a></span>
    </div>
  </div>
</footer>
<a class="fab" href="{WA}" target="_blank" rel="noopener" aria-label="Chat on WhatsApp">{WA_SVG}</a>'''


# ------------------------------------------------------------------
# SEO — titles (≤ 60 chars) and meta descriptions (≈ 140–160 chars)
# ------------------------------------------------------------------
SEO = {
    "index.html": ("Rise Joe | E-Commerce Agency in Lahore, Pakistan",
                   "Rise Joe is a Lahore e-commerce agency helping sellers, students and investors launch and grow on Amazon, eBay, Etsy, Walmart, Shopify and TikTok Shop."),
    "about.html": ("About Rise Joe | E-Commerce Agency in Lahore",
                   "Meet Rise Joe: founder Malik Yaseen Tanveer, 6+ years of marketplace experience, our values and three offices in Lahore. People, products, progress."),
    "students.html": ("E-Commerce Student Program in Lahore | Rise Joe",
                      "Learn e-commerce on real Amazon, eBay and Etsy projects. Our student program offers two pathways: launch your own business or gain agency experience."),
    "clients.html": ("E-Commerce Partnerships for Sellers | Rise Joe",
                     "Client-funded and agency-funded e-commerce partnerships. Rise Joe builds and runs marketplace stores for clients in Pakistan, the UK, USA, Australia and Canada."),
    "investors.html": ("E-Commerce Investment Partnerships | Rise Joe",
                       "Invest in researched e-commerce projects and inventory with Rise Joe. Documented terms, transparent reporting and regular progress updates for every partner."),
    "services/index.html": ("E-Commerce Services: Amazon, eBay & More | Rise Joe",
                            "Ten e-commerce services under one roof: seller account setup, product sourcing, wholesale stock, warehousing, websites, VPS and UK LTD / US LLC registration."),
    "contact.html": ("Contact Rise Joe | E-Commerce Agency in Lahore",
                     "Contact Rise Joe E-Commerce Agency in Lahore by WhatsApp, email or enquiry form. Head office at Plaza No. 26B, Pak Arab Housing Society. Visits by appointment."),
    "privacy.html": ("Privacy Notice | Rise Joe E-Commerce Agency",
                     "How Rise Joe E-Commerce Agency collects, uses and protects the personal information you submit through our website enquiry forms, and the choices you have."),
    "terms.html": ("Terms of Use | Rise Joe E-Commerce Agency",
                   "The terms that apply when you use the Rise Joe E-Commerce Agency website, including information accuracy, enquiries, intellectual property and liability."),
    "404.html": ("Page Not Found | Rise Joe", "Sorry, the page you were looking for could not be found."),
    "services/marketplace-account-setup.html": ("Amazon, eBay & Etsy Seller Account Setup | Rise Joe",
        "Guided seller account setup on Amazon, eBay, Etsy, Walmart, Shopify, TikTok Shop and Temu. Get verified and onboarded correctly with Rise Joe's experts."),
    "services/free-account-checkup.html": ("Free E-Commerce Seller Account Checkup | Rise Joe",
        "Not getting sales? Get a free expert checkup of your Amazon, eBay or Etsy account: listings, pricing, visibility, ads and account health, with clear next steps."),
    "services/product-hunting-sourcing.html": ("Product Hunting & Sourcing Services | Rise Joe",
        "Data-driven product research and supplier sourcing for Amazon, eBay and every marketplace. Get winning product ideas, supplier quotes and landed cost estimates."),
    "services/stock-wholesale-supply.html": ("Wholesale Stock & Inventory Supply | Rise Joe",
        "Request ready stock and wholesale inventory for your e-commerce store, or have Rise Joe source your chosen product from trusted UK and USA suppliers."),
    "services/warehousing-fulfilment.html": ("Warehousing & Fulfilment Services UK/USA | Rise Joe",
        "E-commerce warehousing and fulfilment: storage, inventory management, prep, pick & pack and shipping support in the UK, USA and other key markets."),
    "services/website-development.html": ("E-Commerce Website Design & Development | Rise Joe",
        "Custom business websites and high-converting Shopify and WooCommerce stores. Landing pages, redesigns and ongoing maintenance from Rise Joe's web team."),
    "services/vps-services.html": ("VPS Servers: UK, USA, Australia & Canada | Rise Joe",
        "Reliable virtual private servers (VPS) for e-commerce sellers in the UK, USA, Australia, Canada and Pakistan, configured and set up for your needs."),
    "services/distributor-wholesale-accounts.html": ("Distributor & Wholesale Trade Accounts | Rise Joe",
        "Get help applying for genuine distributor and wholesale trade accounts in the UK and USA, with application support and preparation for your business."),
    "services/ltd-company-registration.html": ("UK LTD Company Registration for Sellers | Rise Joe",
        "UK limited company (LTD) registration support for e-commerce sellers: Companies House formation guidance, documentation help and onboarding next steps."),
    "services/llc-company-registration.html": ("US LLC Formation for E-Commerce Sellers | Rise Joe",
        "US LLC formation support for e-commerce sellers: state selection guidance (Wyoming, Delaware and more), documentation help and follow-up after filing."),
}

AREAS = ["Pakistan", "United Kingdom", "United States", "Australia", "Canada"]
PAGE_TYPES = {"about.html": "AboutPage", "contact.html": "ContactPage", "services/index.html": "CollectionPage"}
CRUMB_NAMES = {"about.html": "About", "students.html": "Student Program", "clients.html": "Client Partnerships",
               "investors.html": "Investor Partnerships", "services/index.html": "Services", "contact.html": "Contact",
               "privacy.html": "Privacy Notice", "terms.html": "Terms of Use"}


def _socials():
    out = []
    for k in ("instagram", "facebook", "tiktok"):
        v = CONFIG.get(k, "")
        if v and v.rstrip("/").count("/") > 2:   # skip bare placeholder domains
            out.append(v)
    return out


def org_node():
    site = CONFIG["site_url"]
    node = {
        "@type": "ProfessionalService", "@id": site + "/#organization",
        "name": "Rise Joe E-Commerce Agency", "alternateName": "Rise Joe",
        "url": site + "/", "slogan": "People · Products · Progress",
        "description": SEO["index.html"][1],
        "logo": {"@type": "ImageObject", "url": site + "/assets/img/favicon-512.png", "width": 512, "height": 512},
        "image": site + "/assets/img/og-image.jpg",
        "email": CONFIG["email"], "telephone": "+" + CONFIG["whatsapp"],
        "address": {"@type": "PostalAddress", "streetAddress": "Plaza No. 26B, Pak Arab Housing Society",
                    "addressLocality": "Lahore", "addressRegion": "Punjab", "addressCountry": "PK"},
        "hasMap": CONFIG["maps"],
        "areaServed": [{"@type": "Country", "name": c} for c in AREAS],
        "founder": {"@id": site + "/#founder"},
        "knowsAbout": ["E-commerce", "Amazon seller accounts", "eBay", "Etsy", "Walmart Marketplace", "Shopify",
                       "TikTok Shop", "Product sourcing", "Wholesale", "Warehousing and fulfilment",
                       "UK LTD company registration", "US LLC formation"],
        "contactPoint": {"@type": "ContactPoint", "contactType": "customer service", "email": CONFIG["email"],
                         "telephone": "+" + CONFIG["whatsapp"], "availableLanguage": ["English", "Urdu"]},
    }
    if _socials():
        node["sameAs"] = _socials()
    return node


def founder_node():
    site = CONFIG["site_url"]
    return {"@type": "Person", "@id": site + "/#founder", "name": "Malik Yaseen Tanveer", "jobTitle": "Founder & CEO",
            "image": site + "/assets/img/founder.jpg", "worksFor": {"@id": site + "/#organization"},
            **({"sameAs": [CONFIG["linkedin"]]} if CONFIG.get("linkedin") else {})}


def build_schema(path, title, desc, extra):
    site = CONFIG["site_url"]
    url = site + "/" + clean_url(path)
    graph = [org_node(), founder_node(),
             {"@type": "WebSite", "@id": site + "/#website", "url": site + "/", "name": "Rise Joe E-Commerce Agency",
              "alternateName": "Rise Joe", "publisher": {"@id": site + "/#organization"}, "inLanguage": "en"}]
    webpage = {"@type": PAGE_TYPES.get(path, "WebPage"), "@id": url + "#webpage", "url": url, "name": title,
               "description": desc, "isPartOf": {"@id": site + "/#website"}, "inLanguage": "en",
               "primaryImageOfPage": {"@type": "ImageObject", "url": site + "/assets/img/og-image.jpg"}}
    if path in ("index.html", "about.html", "contact.html"):
        webpage["about"] = {"@id": site + "/#organization"}
    if path != "index.html":
        items = [("Home", site + "/")]
        if path.startswith("services/") and path != "services/index.html":
            items.append(("Services", site + "/services/"))
            svc = next(x for x in SERVICES if path == f'services/{x["slug"]}.html')
            items.append((svc["short_title"], url))
        else:
            items.append((CRUMB_NAMES.get(path, title), url))
        graph.append({"@type": "BreadcrumbList", "@id": url + "#breadcrumb", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(items)]})
        webpage["breadcrumb"] = {"@id": url + "#breadcrumb"}
    graph.append(webpage)
    graph += extra or []
    data = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":"))
    return '<script type="application/ld+json">' + data.replace("</", "<\\/") + "</script>"


def faq_node(url, items):
    return {"@type": "FAQPage", "@id": url + "#faq", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in items]}


def clean_url(path):
    """File path -> public clean URL path (no .html)."""
    path = path[:-5] if path.endswith(".html") else path
    if path == "index":
        return ""
    if path.endswith("/index"):
        return path[:-5]
    return path


def _clean_href(m):
    name = m.group(1)
    if name == "index" or name.endswith("/index"):
        name = name[:-5] or "./"
    elif name == "services" or name.endswith("/services"):
        name += "/"
    return 'href="' + name


def clean_links(html):
    """Rewrite internal href=\"x.html\" links to extension-less clean URLs."""
    return re.sub(r'href="(?!https?:|//)([^"#?:]*?)\.html(?=[#?"])', _clean_href, html)


def page(path, title, desc, body, active="", schema="", prefix=None, nodes=None):
    depth = path.count("/")
    p = "../" * depth if prefix is None else prefix
    url = CONFIG["site_url"] + "/" + clean_url(path)
    if path in SEO:
        full_title, desc = SEO[path]
    else:
        full_title = title if "Rise Joe" in title else f"{title} | Rise Joe E-Commerce Agency"
    noindex = path == "404.html"
    robots = "noindex, follow" if noindex else "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1"
    if not noindex:
        schema = build_schema(path, full_title, desc, nodes)
    og_img = CONFIG["site_url"] + "/assets/img/og-image.jpg"
    preloader = f'''
<div class="preloader" aria-hidden="true">
  <div class="preloader__panel preloader__panel--top"></div><div class="preloader__panel preloader__panel--bot"></div>
  <div class="preloader__inner">
    <img class="preloader__mark" src="{p}assets/img/logo-mark.png" alt="">
    <div class="preloader__bar"><i></i></div>
    <div class="preloader__count">000</div>
  </div>
</div>''' if path == "index.html" else ""
    html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{escape(full_title)}</title>
<meta name="description" content="{escape(desc)}">
<meta name="robots" content="{robots}">
{"" if noindex else f'<link rel="canonical" href="{url}">'}
<meta name="theme-color" content="#070605">
<meta name="author" content="Rise Joe E-Commerce Agency">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Rise Joe E-Commerce Agency">
<meta property="og:locale" content="en_US">
<meta property="og:title" content="{escape(full_title)}">
<meta property="og:description" content="{escape(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{og_img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Rise Joe E-Commerce Agency: People · Products · Progress">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{escape(full_title)}">
<meta name="twitter:description" content="{escape(desc)}">
<meta name="twitter:image" content="{og_img}">
<link rel="icon" type="image/png" sizes="32x32" href="{p}assets/img/favicon-32.png">
<link rel="apple-touch-icon" href="{p}assets/img/favicon-180.png">
{HEAD_SCRIPT}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Instrument+Serif:ital@0;1&family=Outfit:wght@300;400;500;600;700&display=swap">
<link rel="stylesheet" href="{p}assets/css/style.css?v=2">
{schema}
</head>
<body>
{preloader}
<div class="curtain" aria-hidden="true"><img src="{p}assets/img/logo-mark.png" alt=""></div>
{header(active, p)}
<main id="main">
{body}
</main>
{footer(p)}
<script src="{p}assets/vendor/gsap.min.js" defer></script>
<script src="{p}assets/vendor/ScrollTrigger.min.js" defer></script>
<script src="{p}assets/vendor/lenis.min.js" defer></script>
<script src="{p}assets/js/main.js?v=2" defer></script>
</body>
</html>
'''
    out = OUT / path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(clean_links(html), encoding="utf-8")
    PAGES.append(path)


PAGES = []


# ------------------------------------------------------------------
# COMPONENTS
# ------------------------------------------------------------------
def page_hero(eyebrow, title_lines, lead, actions="", crumbs=None, aside="", ic=None, p=""):
    crumb = ""
    if crumbs:
        crumb = '<nav class="breadcrumb" data-hero aria-label="Breadcrumb"><a href="' + p + 'index.html">Home</a>' + "".join(
            f'<span><a href="{h}">{l}</a></span>' if h else f"<span>{l}</span>" for l, h in crumbs) + "</nav>"
    icn = f'<div class="page-hero__icon" data-hero>{icon(ic)}</div>' if ic else ""
    return f'''
<section class="page-hero">
  <canvas class="hero__canvas" data-constellation="0.6" aria-hidden="true"></canvas>
  <div class="container">
    {crumb}
    <div class="page-hero__grid">
      <div>
        {icn}
        <span class="eyebrow" data-hero>{eyebrow}</span>
        <h1 class="h1 page-hero__title" data-split>{lines(*title_lines)}</h1>
        <p class="lead" data-hero>{lead}</p>
        {f'<div class="btn-row mt-40" data-hero>{actions}</div>' if actions else ""}
      </div>
      <div class="page-hero__aside" data-hero>{aside}</div>
    </div>
  </div>
</section>'''


def section_head(eyebrow, title_lines, lead="", mode="", extra=""):
    cls = {"split": " section-head--split", "center": " section-head--center"}.get(mode, "")
    ecls = " eyebrow--center" if mode == "center" else ""
    left = f'<div><span class="eyebrow{ecls}" data-reveal>{eyebrow}</span><h2 class="h2" data-split style="margin-top:24px">{lines(*title_lines)}</h2></div>'
    right = f'<div>{f"<p class=lead data-reveal>{lead}</p>" if lead else ""}{extra}</div>' if (lead or extra) else ""
    if mode == "center":
        return f'<div class="section-head{cls}"><span class="eyebrow{ecls}" data-reveal>{eyebrow}</span><h2 class="h2" data-split>{lines(*title_lines)}</h2>{f"<p class=lead data-reveal>{lead}</p>" if lead else ""}</div>'
    return f'<div class="section-head{cls}">{left}{right}</div>'


def svc_card(s, i, p, cls_extra=""):
    wide = " svc--wide" if s.get("wide") and not cls_extra else ""
    return f'''<a class="svc spot{wide}{cls_extra}" href="{p}services/{s["slug"]}.html" data-cat="{s["cats"]}" data-keywords="{escape(s["keywords"])}" data-tilt="4">
  <div class="svc__top"><div class="svc__icon">{icon(s["icon"])}</div><span class="svc__num">{i:02d}</span></div>
  <div class="svc__body"><span class="svc__tag">{s["tag"]}</span><h3>{s["short_title"]}</h3><p>{s["short"]}</p></div>
  <span class="svc__go">{icon("arrow")}</span>
</a>'''


def marquee(items, big=False, reverse=False):
    cls = "marquee" + (" marquee--big" if big else "") + (" marquee--reverse" if reverse else "")
    group = "".join(f'<span class="marquee__item">{x}</span>' for x in items)
    track = f'<div class="marquee__track"><div class="marquee__group">{group}</div><div class="marquee__group" aria-hidden="true">{group}</div></div>'
    if big:
        track = f'<div class="marquee__drift">{track}</div>'
    return f'<div class="{cls}" aria-label="{", ".join(items)}">{track}</div>'


def faq(items):
    out = "".join(f'''<div class="faq__item"><button class="faq__q" aria-expanded="false">{escape(q)}<span class="faq__icon" aria-hidden="true"></span></button><div class="faq__a"><p>{escape(a)}</p></div></div>''' for q, a in items)
    return f'<div class="faq" data-stagger="0.07">{out}</div>'


def cta(p, title=None, text=None):
    title = title or f'Ready to <span class="serif gold">rise?</span>'
    text = text or "Tell us where you are today and where you want to be. The right team will take it from there."
    return f'''
<section class="section section--tight">
  <div class="container">
    <div class="cta" data-reveal="scale">
      <img class="cta__mark" src="{p}assets/img/logo-mark.png" alt="">
      <h2 data-split>{lines(title)}</h2>
      <p data-reveal>{text}</p>
      <div class="btn-row" data-reveal>{btn("Start your enquiry", p + "contact.html")}{btn("Chat on WhatsApp", WA, "ghost", ' target="_blank" rel="noopener"', "chat")}</div>
    </div>
  </div>
</section>'''


def disclaimer(text):
    return f'<div class="disclaimer" data-reveal>{icon("info")}<span>{text}</span></div>'


# ---------- Form rendering ----------
def _attrs(f):
    a = ""
    if f.get("when"):
        a += f' data-when="{f["when"]}"'
    return a


def render_field(f):
    t = f["t"]
    req = f.get("r")
    star = " <em>*</em>" if req else ""
    full = " field--full" if f.get("full") or t in ("textarea", "group", "mode") else ""
    when = _attrs(f)
    if t == "group":
        return f'<div class="form__group-title"{when}>{f["l"]}</div>'
    n = f.get("n")
    fid = f"f-{n}-{FORM_COUNTER[0]}"
    err = f'<span class="field__error">{"Please choose at least one option." if t == "check" else "Please complete this field."}</span>'
    if t in ("text", "email", "tel", "date", "url", "number"):
        ph = f' placeholder="{escape(f["ph"])}"' if f.get("ph") else ""
        ac = {"name": ' autocomplete="name"', "email": ' autocomplete="email"', "phone": ' autocomplete="tel"'}.get(n, "")
        ctl = f'<input class="input" id="{fid}" type="{t}" name="{n}"{ph}{ac}{" required" if req else ""}>'
        return f'<div class="field{full}"{when}><label for="{fid}">{f["l"]}{star}</label>{ctl}{err}</div>'
    if t == "select":
        opts = '<option value="" selected disabled>Select…</option>' + "".join(f'<option>{escape(o)}</option>' for o in f["o"])
        return f'<div class="field{full}"{when}><label for="{fid}">{f["l"]}{star}</label><select class="select" id="{fid}" name="{n}"{" required" if req else ""}>{opts}</select>{err}</div>'
    if t == "textarea":
        ph = f' placeholder="{escape(f["ph"])}"' if f.get("ph") else ""
        return f'<div class="field{full}"{when}><label for="{fid}">{f["l"]}{star}</label><textarea class="textarea" id="{fid}" name="{n}" rows="4"{ph}{" required" if req else ""}></textarea>{err}</div>'
    if t == "radio":
        opts = "".join(f'<label class="choice"><input type="radio" name="{n}" value="{escape(o)}"{" required" if req else ""}><span>{escape(o)}</span></label>' for o in f["o"])
        return f'<div class="field{full}"{when}><span class="label">{f["l"]}{star}</span><div class="choice-group" role="radiogroup">{opts}</div>{err}</div>'
    if t == "check":
        opts = "".join(f'<label class="choice"><input type="checkbox" name="{n}[]" value="{escape(o)}"><span>{escape(o)}</span></label>' for o in f["o"])
        rg = " data-required-group" if req else ""
        return f'<div class="field{full}"{when}><span class="label">{f["l"]}{star}</span><div class="choice-group"{rg}>{opts}</div>{err}</div>'
    if t == "mode":
        opts = "".join(f'<label class="choice"><input type="radio" name="{n}" value="{v}"{" checked" if i == 0 else ""} required><span>{lab}</span></label>' for i, (v, lab) in enumerate(f["o"]))
        return f'<div class="field field--full"{when}><span class="label">{f["l"]}{star}</span><div class="mode-switch" role="radiogroup">{opts}</div></div>'
    raise ValueError(t)


FORM_COUNTER = [0]


def enquiry_form(service_name, fields, p, details_label="Enquiry details", details_req=False, submit="Send enquiry"):
    FORM_COUNTER[0] += 1
    shared = [
        {"t": "group", "l": "Your details"},
        {"t": "text", "n": "name", "l": "Full name", "r": True, "ph": "Your name"},
        {"t": "email", "n": "email", "l": "Email", "r": True, "ph": "you@example.com"},
        {"t": "tel", "n": "phone", "l": "Phone / WhatsApp (optional)", "ph": "+92 …"},
        {"t": "select", "n": "country", "l": "Country", "o": COUNTRIES, "r": True},
    ]
    body = "".join(render_field(f) for f in shared)
    if fields:
        if fields[0]["t"] not in ("group", "mode"):
            body += render_field({"t": "group", "l": "About your request"})
        body += "".join(render_field(f) for f in fields)
    body += render_field({"t": "group", "l": "Anything else"})
    body += render_field({"t": "textarea", "n": "details", "l": details_label, "r": details_req, "ph": "Share any other details that will help our team."})
    return f'''
<div class="form-card spot">
  <form class="form" action="{p}send.php" method="post" novalidate data-enquiry data-fallback="{WA}">
    <input type="hidden" name="_service" value="{escape(service_name)}">
    <input type="hidden" name="_ts" value="">
    <label class="hp" aria-hidden="true">Leave this empty<input type="text" name="website" tabindex="-1" autocomplete="off"></label>
    {body}
    <div class="field field--full">
      <label class="consent"><input type="checkbox" name="consent" value="yes" required><i></i><span>I agree that Rise Joe may use these details to respond to my enquiry, as described in the <a href="{p}privacy.html">Privacy Notice</a>. <em style="color:var(--gold);font-style:normal">*</em></span></label>
      <span class="field__error">Please accept to continue.</span>
    </div>
    <div class="form__status" role="alert"></div>
    <div class="form__foot">
      <p class="form__note">{icon("lock").replace('class=""', "")} We will never ask for passwords, OTP codes or verification credentials.</p>
      <button class="btn btn--gold" type="submit" data-magnetic="0.2"><span>{submit}{icon("arrow-ur")}</span></button>
    </div>
  </form>
  <div class="form-success" aria-live="polite">
    <div class="form-success__icon"><svg viewBox="0 0 24 24" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7"/></svg></div>
    <h3>Enquiry received</h3>
    <p>Thank you. We've sent a confirmation to your email<span data-ref-wrap hidden> with reference <b class="gold" data-ref></b></span>. Here's what happens next:</p>
    <ol><li>Your enquiry is routed to the right team</li><li>A specialist reviews your details</li><li>We contact you to discuss next steps</li></ol>
    <button class="btn btn--ghost btn--sm" type="button" data-form-reset><span>Send another enquiry</span></button>
  </div>
</div>'''


def form_section(p, title_lines, lead, service_name, fields, eyebrow="Enquiry", **kw):
    hours = "<br>".join(f"{a}: {b}" for a, b in CONFIG["hours"])
    return f'''
<section class="section" id="enquiry">
  <div class="container form-wrap">
    <div class="sticky">
      <span class="eyebrow" data-reveal>{eyebrow}</span>
      <h2 class="h2" data-split style="margin:24px 0 24px">{lines(*title_lines)}</h2>
      <p class="lead" data-reveal>{lead}</p>
      <div class="contact-list" data-stagger>
        <a class="contact-item" href="{WA}" target="_blank" rel="noopener"><span class="contact-item__icon">{icon("chat")}</span><span><small>WhatsApp</small><b>{escape(CONFIG["phone_display"])}</b><span>Fastest response</span></span></a>
        <a class="contact-item" href="mailto:{CONFIG["email"]}"><span class="contact-item__icon">{icon("mail")}</span><span><small>Email</small><b>{CONFIG["email"]}</b></span></a>
        <div class="contact-item"><span class="contact-item__icon">{icon("clock")}</span><span><small>Office hours</small><span>{hours}</span></span></div>
      </div>
    </div>
    <div data-reveal>{enquiry_form(service_name, fields, p, **kw)}</div>
  </div>
</section>'''


# ------------------------------------------------------------------
# HOME
# ------------------------------------------------------------------
def build_home():
    p = ""
    stats = [("6", "+", "Years of e-commerce experience"), ("500", "+", "Active seller community"),
             ("3", "", "Offices in Lahore"), ("10", "", "Specialist services")]
    stat_html = "".join(f'<div class="stat"><b><span data-count="{n}">{n}</span><sup>{s}</sup></b><span>{l}</span></div>' for n, s, l in stats)
    badge = f'''<div class="badge-rotate" aria-hidden="true"><svg viewBox="0 0 150 150"><defs><path id="circ" d="M75,75 m-60,0 a60,60 0 1,1 120,0 a60,60 0 1,1 -120,0"/></defs><text><textPath href="#circ">People · Products · Progress · Rise Joe · </textPath></text></svg><div class="badge-rotate__core"><img src="assets/img/logo-mark.png" alt=""></div></div>'''

    paths = [
        ("01", "Students", "cap", "students.html", "Learn, work and grow with real e-commerce projects.",
         ["Launch your own business with expert guidance", "Hands-on work on supervised projects", "Learn directly from an active team"], "S"),
        ("02", "Clients", "handshake", "clients.html", "Flexible partnership models to build and manage your store.",
         ["Client-funded store management", "Agency-funded partnership options", "Pakistan, UK, USA, Australia & Canada"], "C"),
        ("03", "Investors", "seed", "investors.html", "Fund researched projects and products with transparent reporting.",
         ["Project funding opportunities", "Inventory & product funding", "Documented terms & progress updates"], "I"),
    ]
    path_html = "".join(f'''<a class="path spot" href="{h}" data-tilt="3">
  <span class="path__num">{n} — For {t.lower()}</span>
  <div class="path__icon">{icon(ic)}</div>
  <h3>{t}</h3><p>{d}</p>
  <ul>{"".join(f"<li>{x}</li>" for x in li)}</ul>
  <span class="link-arrow">Explore the {t.lower()} path {icon("arrow")}</span>
  <span class="path__bg" aria-hidden="true">{bg}</span>
</a>''' for n, t, ic, h, d, li, bg in paths)

    svc_html = "".join(svc_card(s, i + 1, p) for i, s in enumerate(SERVICES))

    journey = [("Start learning & exploring", "It began with curiosity: studying marketplaces, testing ideas and learning what really works."),
               ("Gained experience", "Years of hands-on selling across platforms built deep, practical e-commerce expertise."),
               ("Built team & systems", "A skilled team and proven processes turned individual know-how into a scalable agency."),
               ("Expanded to multiple offices", "Growth led to three offices in Lahore, two in Pak Arab Housing Society and one in Johar Town."),
               ("500+ community members", "Today, a growing network of sellers across Pakistan and beyond rises together.")]
    jcards = "".join(f'''<article class="journey-card spot{" journey-card--final" if i == len(journey) - 1 else ""}"><span class="journey-card__step">0{i+1}</span><h3>{t}</h3><p>{d}</p></article>''' for i, (t, d) in enumerate(journey))

    markets = [("UK", "United Kingdom", "Marketplace accounts, LTD registration, warehousing & distributors"),
               ("US", "United States", "LLC formation, wholesale supply, fulfilment & VPS"),
               ("AU", "Australia", "Product sourcing, warehousing & marketplace growth"),
               ("CA", "Canada", "Marketplace setup, sourcing & fulfilment support"),
               ("PK", "Pakistan", "Our home: three offices in Lahore & a 500+ community")]
    mk = "".join(f'<div class="market"><span class="market__code">{c}</span><span class="market__name">{n}</span><span class="market__info">{i}</span></div>' for c, n, i in markets)

    pillars = [("star", "Proven experience", "6+ years of hands-on e-commerce across the world's biggest marketplaces."),
               ("users", "Trusted community", "500+ active members supported with guidance, products and real projects."),
               ("target", "Real opportunities", "Clear pathways for students, clients and investors, built on real work."),
               ("route", "End-to-end support", "From product idea to warehouse shelf, we support you from A to Z.")]
    pil = "".join(f'<div class="pillar"><b>0{i+1}</b><div class="pillar__icon">{icon(ic)}</div><h3>{t}</h3><p>{d}</p></div>' for i, (ic, t, d) in enumerate(pillars))

    body = f'''
<section class="hero" data-cursor-zone>
  <canvas class="hero__canvas" data-constellation="1" aria-hidden="true"></canvas>
  <div class="hero__glow" aria-hidden="true"></div>
  <div class="hero__mark" aria-hidden="true"><img src="assets/img/logo-mark.png" alt=""></div>
  <div class="container">
    <div class="hero__top">
      <span class="pill" data-hero><i></i>Lahore, Pakistan · Serving UK · USA · Australia · Canada</span>
      <span class="scroll-cue" data-hero><i></i>Scroll to explore</span>
    </div>
    <h1 class="display hero__title" data-split>{lines("We build", '<span class="serif gold">e-commerce</span> brands', "that rise.")}</h1>
    <div class="hero__bottom">
      <div>
        <p class="lead hero__lead" data-hero>Rise Joe helps students, sellers and investors launch, grow and fund real businesses on Amazon, eBay, Etsy, Walmart, TikTok Shop and beyond, with one team from A to Z.</p>
        <div class="btn-row hero__actions" data-hero>{btn("Explore our services", "services.html")}{btn("Free account checkup", "services/free-account-checkup.html", "ghost")}</div>
      </div>
      <div data-hero>{badge}</div>
    </div>
    <div class="hero__stats" data-hero>{stat_html}</div>
  </div>
</section>

{marquee(["Amazon", "eBay", "Etsy", "Walmart", "TikTok Shop", "Shopify", "Temu", "Mercari"])}

<section class="section">
  <div class="container">
    <span class="eyebrow" data-reveal>Who we are</span>
    <p class="statement mt-40" data-fill>We don't just teach e-commerce, <span class="serif">we create real opportunities.</span> From the first product idea to the warehouse shelf, Rise Joe stands beside you with the knowledge, resources and team to help individuals and businesses grow.</p>
    <div class="btn-row mt-60" data-reveal>{btn("Our story", "about.html", "ghost")}</div>
  </div>
</section>

<section class="section" style="padding-top:0">
  <div class="container">
    {section_head("Three ways to rise", ["One agency.", 'Three <span class="serif gold">pathways.</span>'], "Whether you're learning, selling or investing, there's a clear, structured path designed around where you are today.", "split")}
    <div class="paths" data-stagger="0.12">{path_html}</div>
  </div>
</section>

<section class="section" style="padding-top:0">
  <div class="container">
    {section_head("What we do", ['Complete <span class="nowrap">e-commerce</span>', 'solutions, <span class="serif gold">one roof.</span>'], "Ten specialist services covering every stage, from opening your first seller account to sourcing, warehousing and scaling.", "split", f'<div class="mt-40" data-reveal>{btn("View all services", "services.html", "ghost")}</div>')}
    <div class="svc-grid" data-stagger="0.06">{svc_html}</div>
  </div>
</section>

<section class="hscroll">
  <div class="hscroll__pin">
    <div class="container hscroll__head">
      <span class="eyebrow" data-reveal>Our journey</span>
      <h2 class="h2" data-split style="margin-top:24px">{lines('From a vision to a', '<span class="serif gold">growing agency.</span>')}</h2>
    </div>
    <div class="hscroll__track">{jcards}</div>
    <div class="hscroll__line"><i></i></div>
  </div>
</section>

<section class="section">
  <div class="container founder">
    <div class="founder__wrap" data-reveal="left">
      <div class="founder__frame" aria-hidden="true"></div>
      <div class="founder__media" data-cursor="Founder">
        <img src="assets/img/founder.jpg?v=2" alt="Malik Yaseen Tanveer, Founder &amp; CEO of Rise Joe E-Commerce Agency" width="1000" height="1322" loading="lazy" data-parallax-img>
        <div class="founder__caption"><div><b>Malik Yaseen Tanveer</b><span>Founder &amp; CEO</span></div></div>
      </div>
      <div class="founder__badge">{badge}</div>
    </div>
    <div>
      <span class="eyebrow" data-reveal>Founder &amp; CEO</span>
      <blockquote class="quote" data-reveal>We don't just teach e-commerce. We create real opportunities.</blockquote>
      <p class="lead" data-reveal>With more than six years of e-commerce experience, Malik Yaseen Tanveer built Rise Joe to give people in Pakistan and beyond a genuine route into global online business.</p>
      <div class="vm" data-stagger>
        <div class="vm__item"><h3>Vision</h3><p>To create global opportunities through e-commerce, empower talent and build a strong community.</p></div>
        <div class="vm__item"><h3>Mission</h3><p>Providing knowledge, resources and real opportunities to help individuals and businesses grow.</p></div>
      </div>
    </div>
  </div>
</section>

{marquee(["People", "Products", "Progress"], big=True)}

<section class="section">
  <div class="container">
    {section_head("Where we operate", ['Local roots.', '<span class="serif gold">Global</span> markets.'], "Our team in Lahore serves eligible clients in five key markets, always in line with local rules and marketplace policies.", "split")}
    <div class="markets" data-stagger="0.08">{mk}</div>
  </div>
</section>

<section class="section" style="padding-top:0">
  <div class="container">
    {section_head("Why Rise Joe", ['Built on experience.', 'Driven by <span class="serif gold">people.</span>'], mode="center")}
    <div class="pillars" data-stagger="0.1">{pil}</div>
  </div>
</section>

{cta(p)}
'''
    page("index.html", "Rise Joe E-Commerce Agency | People · Products · Progress",
         "Rise Joe is a Lahore-based e-commerce agency helping students, clients and investors launch, grow and fund businesses on Amazon, eBay, Etsy, Walmart, TikTok Shop and more.",
         body, "home")


# ------------------------------------------------------------------
# ABOUT
# ------------------------------------------------------------------
def offices_block(p):
    return f'''
<div class="offices" data-stagger="0.1">
  <div class="office office--main spot">
    <div class="office__pin">{icon("pin")}</div>
    <small>Main office · Head office</small>
    <h3>Pak Arab Housing Society</h3>
    <p>{escape(CONFIG["address"])}</p>
    <a class="link-arrow" href="{CONFIG["maps"]}" target="_blank" rel="noopener">Get directions {icon("arrow")}</a>
  </div>
  <div class="office spot">
    <div class="office__pin">{icon("pin")}</div>
    <small>Office 02</small>
    <h3>Pak Arab Housing Society</h3>
    <p>Lahore, Pakistan. Visits by appointment; full address shared when you book.</p>
    <a class="link-arrow" href="{WA}" target="_blank" rel="noopener">Book a visit {icon("arrow")}</a>
  </div>
  <div class="office spot">
    <div class="office__pin">{icon("pin")}</div>
    <small>Office 03</small>
    <h3>Johar Town</h3>
    <p>Lahore, Pakistan. Visits by appointment; full address shared when you book.</p>
    <a class="link-arrow" href="{WA}" target="_blank" rel="noopener">Book a visit {icon("arrow")}</a>
  </div>
</div>'''


def build_about():
    p = ""
    steps = [("Start learning & exploring", "Rise Joe began with a simple drive: understand global marketplaces deeply and find out what truly works."),
             ("Gained experience", "Six-plus years of hands-on selling, sourcing and account management across leading platforms."),
             ("Built team & systems", "Specialists in research, sourcing, account setup, logistics and technology, working to proven processes."),
             ("Expanded to multiple offices", "Three offices in Lahore: two in Pak Arab Housing Society and one in Johar Town."),
             ("A 500+ seller community", "A growing network supported with guidance, product supply, real projects and training.")]
    st = "".join(f'<div class="step"><div class="step__dot">0{i+1}</div><div><h3>{t}</h3><p>{d}</p></div></div>' for i, (t, d) in enumerate(steps))
    values = [("shield", "Integrity first", "We follow every marketplace's rules. No shortcuts, no account rental, no identity lending, ever."),
              ("users", "People-centred", "Students, clients and investors each get a clear pathway and a team that knows them."),
              ("chart", "Results-minded", "Research, data and disciplined execution, with honest expectations and no false promises."),
              ("globe", "Globally focused", "A Lahore team serving clients across Pakistan, the UK, USA, Australia and Canada.")]
    vals = "".join(f'<div class="feature spot"><div class="feature__icon">{icon(ic)}</div><h3>{t}</h3><p>{d}</p></div>' for ic, t, d in values)
    body = f'''
{page_hero("About Rise Joe", ["A Lahore agency", 'with a <span class="serif gold">global</span> mindset.'], "Rise Joe E-Commerce Agency exists to turn ambition into real, compliant e-commerce businesses, for the people who build them, the clients who own them and the investors who fund them.", btn("Meet the founder", "#founder") + btn("Visit our offices", "#offices", "ghost"), [("About", None)], f'<div class="stat"><b><span data-count="500">500</span><sup>+</sup></b><span>Seller community members</span></div><div class="stat"><b><span data-count="6">6</span><sup>+</sup></b><span>Years of experience</span></div>', p=p)}

<section class="section" style="padding-top:40px">
  <div class="container split">
    <div class="sticky"><span class="eyebrow" data-reveal>Who we are</span><h2 class="h2" data-split style="margin-top:24px">{lines("People.", "Products.", '<span class="serif gold">Progress.</span>')}</h2></div>
    <div class="prose" data-stagger="0.1">
      <p>Rise Joe is a professional e-commerce agency based in Lahore, Pakistan, helping entrepreneurs and established businesses succeed on the world's leading online marketplaces.</p>
      <p>We bring together everything a modern seller needs under one roof: marketplace account setup, free account checkups, product hunting and sourcing, stock and wholesale supply, warehousing and fulfilment, website development, VPS services, distributor accounts and UK/US company registration assistance.</p>
      <p>Beyond services, we've built something rarer: structured pathways for students to learn through real work, partnership models for clients, and transparent funding opportunities for investors. All of it is grounded in compliance and honest expectations.</p>
      <div class="vm"><div class="vm__item"><h3>Vision</h3><p>To create global opportunities through e-commerce, empower talent and build a strong community.</p></div><div class="vm__item"><h3>Mission</h3><p>Providing knowledge, resources and real opportunities to help individuals and businesses grow.</p></div></div>
    </div>
  </div>
</section>

<section class="section" style="padding-top:0">
  <div class="container split">
    <div class="sticky"><span class="eyebrow" data-reveal>Our journey</span><h2 class="h2" data-split style="margin-top:24px">{lines("From a vision", 'to a <span class="serif gold">movement.</span>')}</h2><p class="lead mt-40" data-reveal>Every milestone has been earned through real work, real sellers and real results.</p></div>
    <div class="steps"><div class="steps__line"><i></i></div>{st}</div>
  </div>
</section>

<section class="section" id="founder" style="padding-top:0">
  <div class="container founder">
    <div class="founder__wrap" data-reveal="left">
      <div class="founder__frame" aria-hidden="true"></div>
      <div class="founder__media"><img src="assets/img/founder.jpg?v=2" alt="Malik Yaseen Tanveer, Founder &amp; CEO" width="1000" height="1322" loading="lazy" data-parallax-img><div class="founder__caption"><div><b>Malik Yaseen Tanveer</b><span>Founder &amp; CEO</span></div></div></div>
    </div>
    <div>
      <span class="eyebrow" data-reveal>Leadership</span>
      <blockquote class="quote" data-reveal>Our goal is simple: give every person who walks through our doors a real way to grow.</blockquote>
      <p class="lead" data-reveal>Malik Yaseen Tanveer founded Rise Joe after more than six years working across global marketplaces. Today the agency's team supports a 500+ seller community, three Lahore offices and clients across five countries.</p>
      <div class="btn-row mt-40" data-reveal>{btn("Work with us", "contact.html")}</div>
    </div>
  </div>
</section>

<section class="section" style="padding-top:0">
  <div class="container">
    {section_head("Our values", ["How we", '<span class="serif gold">work.</span>'], "Principles that guide every enquiry, partnership and project.", "split")}
    <div class="feature-grid" data-stagger="0.1">{vals}</div>
  </div>
</section>

<section class="section" id="offices" style="padding-top:0">
  <div class="container">
    {section_head("Our offices", ["Three offices.", 'One <span class="serif gold">city.</span>'], "Visit us in Lahore. All visits are by appointment, Monday to Friday.", "split")}
    {offices_block(p)}
  </div>
</section>

{cta(p)}
'''
    page("about.html", "About Us", "Meet Rise Joe E-Commerce Agency: our story, founder Malik Yaseen Tanveer, our values and our three offices in Lahore, Pakistan.", body, "about")


# ------------------------------------------------------------------
# STUDENTS
# ------------------------------------------------------------------
def build_students():
    p = ""
    learn = [("search", "Product research", "Find products with real demand using practical, data-led methods."),
             ("store", "Marketplace operations", "Listings, pricing, account health and day-to-day store management."),
             ("route", "Sourcing & logistics", "Suppliers, shipping, warehousing and fulfilment in the real world."),
             ("chart", "Growth & ads", "Visibility, conversion and advertising on leading marketplaces.")]
    lr = "".join(f'<div class="feature spot"><div class="feature__icon">{icon(ic)}</div><h3>{t}</h3><p>{d}</p></div>' for ic, t, d in learn)
    steps = [("Apply", "Send your enquiry with your skill level, goals and preferred pathway."),
             ("Conversation", "We get to know you and recommend the pathway that fits."),
             ("Evaluation", "For practical work, we assess fit and availability for internal projects."),
             ("Start", "Begin building your venture or contributing to supervised projects.")]
    pr = "".join(f'<div class="pr spot"><span class="pr__n">0{i+1}</span><h3>{t}</h3><p>{d}</p></div>' for i, (t, d) in enumerate(steps))
    fields = [
        {"t": "radio", "n": "skill_level", "l": "Current skill level", "o": ["Beginner", "Intermediate", "Advanced"], "r": True, "full": True},
        {"t": "radio", "n": "desired_pathway", "l": "Desired pathway", "o": ["Path A — Business Launch", "Path B — Practical Work", "Not sure yet"], "r": True, "full": True},
        {"t": "textarea", "n": "relevant_experience", "l": "Relevant experience", "ph": "Any e-commerce, freelancing, marketing or business experience", "full": True},
    ]
    body = f'''
{page_hero("For students", ["Learn. Work.", 'Grow. <span class="serif gold">Build your future.</span>'], "Two clear pathways into real e-commerce, whether you're ready to launch your own business or want to learn by working on supervised projects with our team.", btn("Apply now", "#enquiry") + btn("Compare pathways", "#paths", "ghost"), [("Students", None)], f'<div class="stat"><b><span data-count="500">500</span><sup>+</sup></b><span>Community members learning &amp; earning</span></div>', p=p)}

<section class="section" id="paths" style="padding-top:40px">
  <div class="container">
    {section_head("Choose your path", ["Two pathways.", 'One <span class="serif gold">destination.</span>'], "Your situation decides the route, not your potential. Both pathways lead to real, practical e-commerce experience.", "split")}
    <div class="models" data-stagger="0.12">
      <div class="model model--featured spot" data-tilt="3">
        <div class="model__label"><span>Path A · Business launch</span><i>A</i></div>
        <h3>Launch your own <span class="serif gold">e-commerce venture</span></h3>
        <p>For students with access to international business connections and/or investment who want to plan, establish and operate their own e-commerce business.</p>
        <ul class="checklist"><li>We help plan and set up your business, in Pakistan or overseas</li><li>Complete guidance on marketplace, products and operations</li><li>Ongoing support as you establish and run your venture</li><li>Access to our sourcing, logistics and account expertise</li></ul>
        <div class="mt-40">{btn("Apply for Path A", "#enquiry", "gold", ' data-preset="desired_pathway=Path A — Business Launch"')}</div>
      </div>
      <div class="model spot" data-tilt="3">
        <div class="model__label"><span>Path B · Practical work</span><i>B</i></div>
        <h3>Learn through <span class="serif gold">real projects</span></h3>
        <p>For students without investment or overseas connections who want to learn through supervised internal projects and potential agency work.</p>
        <ul class="checklist"><li>Join internal projects as a trainee</li><li>Gain real, hands-on e-commerce experience</li><li>Work alongside our experienced team</li><li>Potential agency work, subject to evaluation and availability</li></ul>
        <div class="mt-40">{btn("Apply for Path B", "#enquiry", "ghost", ' data-preset="desired_pathway=Path B — Practical Work"')}</div>
      </div>
    </div>
  </div>
</section>

<section class="section" style="padding-top:0">
  <div class="container">
    {section_head("What you'll learn", ["Skills that", '<span class="serif gold">actually sell.</span>'], mode="split")}
    <div class="feature-grid" data-stagger="0.1">{lr}</div>
  </div>
</section>

<section class="section" style="padding-top:0">
  <div class="container">
    {section_head("How it works", ["From application", 'to <span class="serif gold">action.</span>'], mode="split")}
    <div class="process-row" data-stagger="0.1">{pr}</div>
  </div>
</section>

<section class="section" style="padding-top:0">
  <div class="container split">
    <div class="sticky"><span class="eyebrow" data-reveal>Questions</span><h2 class="h2" data-split style="margin-top:24px">{lines("Student", '<span class="serif gold">FAQs.</span>')}</h2></div>
    {faq([("Do I need experience to apply?", "No. Beginners are welcome. Tell us your current skill level and we'll recommend the right starting point."),
          ("What's the difference between Path A and Path B?", "Path A is for students with international connections and/or investment who want to launch their own business. Path B is for students without investment who want to learn through supervised projects."),
          ("Is Path B guaranteed work?", "Practical work opportunities depend on evaluation and availability. We'll be transparent about what's available when you apply."),
          ("Can I switch pathways later?", "Yes. As your situation changes, we can discuss moving to the pathway that fits you best.")])}
  </div>
</section>

{form_section(p, ["Start your", '<span class="serif gold">journey.</span>'], "Tell us about yourself and the pathway you're interested in. We'll get back to you to discuss the next steps.", "Student Program", fields, "Student enquiry", details_label="Message", submit="Send application")}
'''
    page("students.html", "Student Program", "Two pathways for students: launch your own e-commerce business with Rise Joe, or gain practical experience on supervised agency projects.", body, "students")


# ------------------------------------------------------------------
# CLIENTS
# ------------------------------------------------------------------
def build_clients():
    p = ""
    manage = [("store", "Store management", "Listings, pricing, inventory, account health and daily operations."),
              ("search", "Product strategy", "Research-led product selection and sourcing for your store."),
              ("chart", "Growth & optimisation", "Visibility, conversion and advertising improvements."),
              ("doc", "Clear reporting", "Agreed reporting so you always understand progress.")]
    mg = "".join(f'<div class="feature spot"><div class="feature__icon">{icon(ic)}</div><h3>{t}</h3><p>{d}</p></div>' for ic, t, d in manage)
    steps = [("Enquiry", "Share your marketplace, jurisdiction, account status and objectives."),
             ("Eligibility review", "We review your situation against jurisdiction and marketplace policies."),
             ("Agree terms", "Management scope and commercial share are agreed and documented."),
             ("Launch & manage", "We operate and grow your store, with regular updates.")]
    pr = "".join(f'<div class="pr spot"><span class="pr__n">0{i+1}</span><h3>{t}</h3><p>{d}</p></div>' for i, (t, d) in enumerate(steps))
    mk = "".join(f'<span class="tag">{m}</span>' for m in MARKETS5)
    fields = [
        {"t": "check", "n": "target_marketplace", "l": "Target marketplace(s)", "o": PLATFORMS, "r": True, "full": True},
        {"t": "select", "n": "jurisdiction", "l": "Jurisdiction", "o": MARKETS5 + ["Other"], "r": True},
        {"t": "select", "n": "account_status", "l": "Existing account status", "o": ["I have an active seller account", "I have an account with issues", "I need a compliant new setup", "Not sure"], "r": True},
        {"t": "radio", "n": "investment_availability", "l": "Investment availability", "o": ["I can provide operating capital (Client-Funded)", "Interested in Agency-Funded", "Let's discuss"], "r": True, "full": True},
        {"t": "textarea", "n": "business_objectives", "l": "Business objectives", "ph": "What do you want to achieve in the next 6–12 months?", "r": True, "full": True},
    ]
    body = f'''
{page_hero("For clients", ["Flexible partnerships", 'for <span class="serif gold">serious sellers.</span>'], "Two partnership models for clients in Pakistan, the UK, USA, Australia and Canada. You bring a legitimate business; we bring the team, systems and experience to run and grow it.", btn("Start a partnership", "#enquiry") + btn("Compare models", "#models", "ghost"), [("Clients", None)], f'<div class="tags">{mk}</div>', p=p)}

<section class="section" id="models" style="padding-top:40px">
  <div class="container">
    {section_head("Partnership models", ["Choose the model", 'that <span class="serif gold">fits you.</span>'], "Every partnership is agreed individually and documented clearly, so you always know who does what and how results are shared.", "split")}
    <div class="models" data-stagger="0.12">
      <div class="model model--featured spot" data-tilt="3">
        <div class="model__label"><span>Option 01 · Client-funded</span><i>01</i></div>
        <h3>You invest. <span class="serif gold">We manage.</span></h3>
        <p>You supply a legitimately owned or authorised e-commerce account, or request a compliant setup, and provide the operating capital. We manage the store under agreed terms.</p>
        <ul class="checklist"><li>Complete store management and support</li><li>Profit-sharing terms agreed with you</li><li>Research-led products and sourcing</li><li>Transparent, regular reporting</li></ul>
        <div class="mt-40">{btn("Enquire about Client-Funded", "#enquiry", "gold", ' data-preset="investment_availability=I can provide operating capital (Client-Funded)"')}</div>
      </div>
      <div class="model spot" data-tilt="3">
        <div class="model__label"><span>Option 02 · Agency-funded</span><i>02</i></div>
        <h3>You participate. <span class="serif gold">We fund.</span></h3>
        <p>For eligible clients who provide legitimate business and account participation but not operating investment. The agency may finance agreed operations, with the commercial share negotiated individually.</p>
        <ul class="checklist"><li>Agency may finance agreed operations</li><li>Commercial share negotiated individually</li><li>Full operational management by our team</li><li>Subject to eligibility and review</li></ul>
        <div class="mt-40">{btn("Enquire about Agency-Funded", "#enquiry", "ghost", ' data-preset="investment_availability=Interested in Agency-Funded"')}</div>
      </div>
    </div>
    {disclaimer("We work only with legitimately owned or authorised accounts. Rise Joe never offers account rental, identity lending or verification circumvention. All partnerships are subject to jurisdiction rules and marketplace policies.")}
  </div>
</section>

<section class="section" style="padding-top:0">
  <div class="container">
    {section_head("What we handle", ["Your store,", '<span class="serif gold">expertly run.</span>'], mode="split")}
    <div class="feature-grid" data-stagger="0.1">{mg}</div>
  </div>
</section>

<section class="section" style="padding-top:0">
  <div class="container">
    {section_head("The process", ["Simple, clear,", '<span class="serif gold">documented.</span>'], mode="split")}
    <div class="process-row" data-stagger="0.1">{pr}</div>
  </div>
</section>

<section class="section" style="padding-top:0">
  <div class="container split">
    <div class="sticky"><span class="eyebrow" data-reveal>Questions</span><h2 class="h2" data-split style="margin-top:24px">{lines("Client", '<span class="serif gold">FAQs.</span>')}</h2></div>
    {faq([("Which countries do you work with?", "We serve eligible clients in Pakistan, the UK, USA, Australia and Canada, subject to jurisdiction rules and marketplace policies."),
          ("How is profit shared?", "Profit-sharing and commercial terms are agreed individually with each client and documented before work begins."),
          ("What if I don't have a seller account yet?", "We can help with a compliant setup. See our Marketplace Account Setup service, or mention it in your enquiry."),
          ("Do you guarantee sales?", "No. We bring experience, systems and effort, but we never promise specific sales outcomes. We'll always set honest expectations.")])}
  </div>
</section>

{form_section(p, ["Let's build", '<span class="serif gold">together.</span>'], "Tell us about your marketplace, account and goals. We'll review your eligibility and get back to you with the right partnership option.", "Client Partnership", fields, "Client enquiry")}
'''
    page("clients.html", "Client Partnerships", "Client-funded and agency-funded e-commerce partnership models for eligible clients in Pakistan, the UK, USA, Australia and Canada.", body, "clients")


# ------------------------------------------------------------------
# INVESTORS
# ------------------------------------------------------------------
def build_investors():
    p = ""
    flow = ["Enquiry", "Discovery call", "Project / product proposal", "Risk & terms review", "Investor approval", "Documented funding", "Progress updates"]
    fdesc = ["Tell us your interests, budget and preferred markets.",
             "We discuss your goals, risk appetite and expectations.",
             "We present a researched opportunity with allocation and timeline.",
             "Risks, terms and reporting arrangements reviewed together.",
             "You decide. Nothing proceeds without your approval.",
             "Funding is documented clearly before operations begin.",
             "Regular progress reporting throughout the project."]
    st = "".join(f'<div class="step"><div class="step__dot">0{i+1}</div><div><h3>{t}</h3><p>{d}</p></div></div>' for i, (t, d) in enumerate(zip(flow, fdesc)))
    fields = [
        {"t": "radio", "n": "investment_interest", "l": "Investment interest", "o": ["Project funding", "Inventory / product funding", "Both"], "r": True, "full": True},
        {"t": "select", "n": "investment_range", "l": "Indicative investment range", "o": ["Under $5,000", "$5,000 – $20,000", "$20,000 – $50,000", "$50,000+", "Prefer to discuss"], "r": True},
        {"t": "select", "n": "time_horizon", "l": "Time horizon", "o": ["Short-term (per sourcing cycle)", "6 – 12 months", "12 months+", "Flexible"]},
        {"t": "check", "n": "preferred_markets", "l": "Preferred markets", "o": MARKETS4, "full": True},
    ]
    body = f'''
{page_hero("For investors", ["Research-led", '<span class="serif gold">e-commerce</span> investment.'], "Fund vetted client-account projects or researched products for the UK, USA, Australia and Canada, with clear proposals, documented terms and regular progress reporting.", btn("Request a proposal", "#enquiry") + btn("See the workflow", "#workflow", "ghost"), [("Investors", None)], "", p=p)}

<section class="section" style="padding-top:40px">
  <div class="container">
    {section_head("Investment models", ["Two ways", 'to <span class="serif gold">participate.</span>'], "Each opportunity is presented with a clear allocation of capital, operating approach, timeline, risks and reporting arrangements.", "split")}
    <div class="models" data-stagger="0.12">
      <div class="model model--featured spot" data-tilt="3">
        <div class="model__label"><span>Model 01 · Project funding</span><i>01</i></div>
        <h3>Fund approved <span class="serif gold">client projects</span></h3>
        <p>We present approved client-account project opportunities with the proposed allocation of capital, operating approach, expected timeline, risks and reporting arrangements.</p>
        <ul class="checklist"><li>Vetted, approved client-account projects</li><li>Defined capital allocation & operating plan</li><li>Expected timeline and risk overview</li><li>Agreed reporting arrangements</li></ul>
      </div>
      <div class="model spot" data-tilt="3">
        <div class="model__label"><span>Model 02 · Inventory funding</span><i>02</i></div>
        <h3>Fund researched <span class="serif gold">products</span></h3>
        <p>We hunt and evaluate potential products, then present unit economics, sourcing options and fulfilment plans for the UK, USA, Australia and Canada markets.</p>
        <ul class="checklist"><li>Product research & market analysis</li><li>Unit economics and sourcing options</li><li>Procurement & fulfilment handled</li><li>Clear proposal before any commitment</li></ul>
      </div>
    </div>
  </div>
</section>

<section class="section" style="padding-top:0">
  <div class="container">
    {section_head("Sourcing routes", ["Illustrative", '<span class="serif gold">planning examples.</span>'], "Typical sourcing routes and the illustrative ROI targets we use for planning. Every proposal includes its own figures and risks.", "split")}
    <div class="roi" data-stagger="0.12">
      <div class="roi__card spot">
        <div class="roi__route">{icon("plane")} Fast sourcing</div>
        <div class="roi__big"><span class="gold">30–35%</span><small>Illustrative target ROI</small></div>
        <div class="roi__meta"><div><b>~3–10 days</b><span>Approximate sourcing time</span></div><div><b>Wholesale / air</b><span>Wholesalers, distributors or air routes</span></div></div>
      </div>
      <div class="roi__card spot">
        <div class="roi__route">{icon("ship")} Extended sourcing</div>
        <div class="roi__big"><span class="gold">40–50%</span><small>Illustrative target ROI</small></div>
        <div class="roi__meta"><div><b>~25–30 days</b><span>Approximate sourcing time</span></div><div><b>Overseas / sea</b><span>Longer overseas or sea routes</span></div></div>
      </div>
    </div>
    {disclaimer("These figures are illustrative planning examples, not guaranteed outcomes. Investment involves risk, including the possible loss of capital. Actual returns and lead times vary by product, market and conditions. Each opportunity is reviewed with its own risks and terms before you decide.")}
  </div>
</section>

<section class="section" id="workflow" style="padding-top:0">
  <div class="container split">
    <div class="sticky"><span class="eyebrow" data-reveal>Investor workflow</span><h2 class="h2" data-split style="margin-top:24px">{lines("Seven steps.", 'Full <span class="serif gold">transparency.</span>')}</h2><p class="lead mt-40" data-reveal>Nothing moves forward without your review and approval, and every commitment is documented.</p></div>
    <div class="steps"><div class="steps__line"><i></i></div>{st}</div>
  </div>
</section>

<section class="section" style="padding-top:0">
  <div class="container split">
    <div class="sticky"><span class="eyebrow" data-reveal>Questions</span><h2 class="h2" data-split style="margin-top:24px">{lines("Investor", '<span class="serif gold">FAQs.</span>')}</h2></div>
    {faq([("Are returns guaranteed?", "No. ROI figures shown are illustrative planning examples. Each proposal sets out its own projections and risks, and outcomes can vary."),
          ("What markets do you invest in?", "Inventory and product opportunities focus on the UK, USA, Australia and Canada marketplaces."),
          ("How will I receive updates?", "Reporting arrangements are agreed as part of your terms, with regular progress updates throughout."),
          ("What is the minimum investment?", "It depends on the opportunity. Share your indicative range in the form and we'll present suitable options.")])}
  </div>
</section>

{form_section(p, ["Request an", '<span class="serif gold">investor proposal.</span>'], "Share your interests and we'll arrange a discovery call to understand your goals before presenting any opportunity.", "Investor Partnership", fields, "Investor enquiry", details_label="Questions or comments")}
'''
    page("investors.html", "Investor Partnerships", "Project funding and inventory funding opportunities with Rise Joe: researched proposals, documented terms and regular progress updates.", body, "investors")


# ------------------------------------------------------------------
# SERVICES HUB
# ------------------------------------------------------------------
def build_services():
    p = "../"
    chips = "".join(f'<button class="chip{" is-active" if k == "all" else ""}" data-filter="{k}" aria-pressed="{"true" if k == "all" else "false"}">{l}</button>' for k, l in CATEGORIES)
    cards = "".join(svc_card(s, i + 1, p) for i, s in enumerate(SERVICES))
    body = f'''
{page_hero("Our services", ["Everything you need", 'to <span class="serif gold">sell globally.</span>'], "Ten specialist services, each with its own team and a dedicated enquiry flow. Pick what you need, answer a few relevant questions, and we'll route you to the right experts.", btn("Free account checkup", p + "services/free-account-checkup.html") + btn("Talk to us", p + "contact.html", "ghost"), [("Services", None)], "", p=p)}

<section class="section" style="padding-top:20px">
  <div class="container">
    <div class="filters" data-reveal>
      <div class="chips" role="group" aria-label="Filter services">{chips}</div>
      <label class="search">{icon("search")}<input type="search" placeholder="Search services…" data-search aria-label="Search services"></label>
    </div>
    <h2 class="sr-only">All e-commerce services</h2>
    <div class="svc-grid" data-filter-grid data-stagger="0.05">{cards}</div>
    <div class="empty-state">No services match your search. Try another keyword, or <a class="link-arrow" href="{p}contact.html">ask us directly</a>.</div>
  </div>
</section>

{marquee(["Research", "Source", "Setup", "Store", "Ship", "Scale"], big=True, reverse=True)}

<section class="section">
  <div class="container split">
    <div class="sticky"><span class="eyebrow" data-reveal>How enquiries work</span><h2 class="h2" data-split style="margin-top:24px">{lines("Straight to", 'the <span class="serif gold">right team.</span>')}</h2></div>
    <div class="steps"><div class="steps__line"><i></i></div>
      {"".join(f'<div class="step"><div class="step__dot">0{i+1}</div><div><h3>{t}</h3><p>{d}</p></div></div>' for i, (t, d) in enumerate([("Choose a service", "Open any service to see how it works, supported platforms and FAQs."), ("Answer relevant questions", "Each form asks only what that service's team needs."), ("Confirm & submit", "Accept the privacy consent and send. You'll see an instant confirmation."), ("Email acknowledgement", "A confirmation with your reference number arrives in your inbox."), ("Assigned follow-up", "A specialist from the relevant team contacts you to discuss next steps.")]))}
    </div>
  </div>
</section>

<section class="section" style="padding-top:0">
  <div class="container split">
    <div class="sticky"><span class="eyebrow" data-reveal>Questions</span><h2 class="h2" data-split style="margin-top:24px">{lines("Service", '<span class="serif gold">FAQs.</span>')}</h2></div>
    {faq([("Which marketplaces do you support?", "Amazon, eBay, Etsy, Walmart, Shopify, TikTok Shop, Temu and other applicable marketplaces, depending on the service."),
          ("Can I request more than one service?", "Yes. Submit an enquiry for each service you need, or contact us and we'll put together a combined plan."),
          ("Do you guarantee approvals or sales?", "No. We never promise account approvals, distributor approvals, specific sales outcomes or guaranteed lead times. We promise expert, honest work."),
          ("Will you ask for my account passwords?", "Never. We don't request passwords, OTP codes or sensitive credentials at any stage.")])}
  </div>
</section>

{cta(p)}
'''
    nodes = [{"@type": "ItemList", "@id": CONFIG["site_url"] + "/services/#list", "name": "Rise Joe e-commerce services",
              "numberOfItems": len(SERVICES), "itemListElement": [
                  {"@type": "ListItem", "position": i + 1, "name": x["title"],
                   "url": CONFIG["site_url"] + "/services/" + x["slug"]} for i, x in enumerate(SERVICES)]}]
    page("services/index.html", "Services", "Explore Rise Joe's ten e-commerce services: marketplace account setup, free account checkup, product hunting & sourcing, wholesale, warehousing, websites, VPS, distributor accounts and UK/US company registration.", body, "services", nodes=nodes)


# ------------------------------------------------------------------
# SERVICE PAGES
# ------------------------------------------------------------------
def build_service(s, idx):
    p = "../"
    path = f'services/{s["slug"]}.html'
    if s.get("hero_ctas"):
        actions = "".join(btn(l, h, k, f' data-preset="{pr}"' if pr else "") for l, h, k, pr in s["hero_ctas"])
    else:
        actions = btn("Request this service", "#enquiry") + btn("Ask on WhatsApp", WA, "ghost", ' target="_blank" rel="noopener"', "chat")
    aside = f'<span class="eyebrow">{s["chips_title"]}</span><div class="tags">{"".join(f"<span class=tag>{c}</span>" for c in s["chips"][:6])}</div>'
    benefits = "".join(f'<div class="benefit spot"><span class="benefit__n">0{i+1}</span><h3>{t}</h3><p>{d}</p></div>' for i, (t, d) in enumerate(s["benefits"]))
    steps = "".join(f'<div class="pr spot"><span class="pr__n">0{i+1}</span><h3>{t}</h3><p>{d}</p></div>' for i, (t, d) in enumerate(s["steps"]))
    options = ""
    if s.get("options"):
        oc = ""
        for i, (t, d, b, pr, ic) in enumerate(s["options"]):
            feat = " model--featured" if i == 0 else ""
            kind = "gold" if i == 0 else "ghost"
            oc += (f'<div class="model spot{feat}" data-tilt="3">'
                   f'<div class="model__label"><span>Option 0{i+1}</span><div class="feature__icon" style="margin:0">{icon(ic)}</div></div>'
                   f'<h3>{t}</h3><p>{d}</p>'
                   f'<div style="margin-top:auto;padding-top:20px">{btn(b, "#enquiry", kind, " data-preset=" + chr(34) + pr + chr(34))}</div></div>')
        cols = "repeat(3,1fr)" if len(s["options"]) == 3 else "1fr 1fr"
        options = f'''
<section class="section" style="padding-top:0">
  <div class="container">
    {section_head("Choose your request", ["How can we", '<span class="serif gold">help?</span>'], "Request each service on its own, or combine them. Pick an option to jump straight to the right form.", "split")}
    <div class="models svc-options" style="grid-template-columns:{cols}" data-stagger="0.1">{oc}</div>
  </div>
</section>'''
    related_items = [x for x in SERVICES if x["slug"] != s["slug"]]
    rel = related_items[idx % len(related_items):] + related_items[:idx % len(related_items)]
    related = "".join(svc_card(r, SERVICES.index(r) + 1, p, " related-card") for r in rel[:3])
    chips = "".join(f'<span class="tag">{c}</span>' for c in s["chips"])
    title_words = s["title"].split(" ")
    # split title into 2 lines, highlight last line in gold serif
    mid = (len(title_words) + 1) // 2
    t1, t2 = " ".join(title_words[:mid]), " ".join(title_words[mid:])
    body = f'''
{page_hero(s["tag"], [t1, f'<span class="serif gold">{t2}</span>'], s["lead"], actions, [("Services", "../services.html"), (s["short_title"], None)], aside, s["icon"], p)}

<section class="section" style="padding-top:40px">
  <div class="container split">
    <div class="sticky"><span class="eyebrow" data-reveal>Service overview</span><h2 class="h2" data-split style="margin-top:24px">{lines("What's", '<span class="serif gold">included.</span>')}</h2></div>
    <div>
      <div class="prose" data-stagger="0.1">{"".join(f"<p>{x}</p>" for x in s["overview"])}</div>
      <div class="benefits mt-60" data-stagger="0.08">{benefits}</div>
    </div>
  </div>
</section>
{options}
<section class="section" style="padding-top:0">
  <div class="container">
    {section_head("How it works", ["Four clear", '<span class="serif gold">steps.</span>'], mode="split")}
    <div class="process-row" data-stagger="0.1">{steps}</div>
  </div>
</section>

<section class="section" style="padding-top:0">
  <div class="container split split--center">
    <div><span class="eyebrow" data-reveal>{s["chips_title"]}</span><h2 class="h3" data-split style="margin-top:20px">{lines("Built for the platforms", "and markets you sell in.")}</h2></div>
    <div><div class="tags" data-stagger="0.04">{chips}</div>{disclaimer(s["note"])}</div>
  </div>
</section>

<section class="section" style="padding-top:0">
  <div class="container split">
    <div class="sticky"><span class="eyebrow" data-reveal>FAQs</span><h2 class="h2" data-split style="margin-top:24px">{lines("Common", '<span class="serif gold">questions.</span>')}</h2></div>
    {faq(s["faqs"])}
  </div>
</section>

{form_section(p, ["Request this", '<span class="serif gold">service.</span>'], f"Answer a few quick questions about your {' '.join(w if w.isupper() else w.lower() for w in s['short_title'].split())} needs. Your enquiry goes straight to the responsible team.", s["title"], s["fields"], "Service enquiry")}

<section class="section" style="padding-top:0">
  <div class="container">
    {section_head("Explore more", ["Related", '<span class="serif gold">services.</span>'], mode="split", extra=f'<div data-reveal>{btn("All services", "../services.html", "ghost")}</div>')}
    <div class="related" data-stagger="0.08">{related}</div>
  </div>
</section>

{cta(p)}
'''
    url = CONFIG["site_url"] + "/" + clean_url(path)
    svc = {"@type": "Service", "@id": url + "#service", "name": s["title"], "serviceType": s["title"],
           "description": s["short"], "url": url, "provider": {"@id": CONFIG["site_url"] + "/#organization"},
           "areaServed": [{"@type": "Country", "name": c} for c in AREAS],
           "category": "E-commerce services"}
    if s["slug"] == "free-account-checkup":
        svc["offers"] = {"@type": "Offer", "price": "0", "priceCurrency": "USD", "description": "Free account consultation and checkup"}
    page(path, s["title"], s["lead"], body, "services", nodes=[svc, faq_node(url, s["faqs"])])


# ------------------------------------------------------------------
# CONTACT
# ------------------------------------------------------------------
def build_contact():
    p = ""
    topics = ["General enquiry", "Student Program", "Client Partnership", "Investor Partnership"] + [s["title"] for s in SERVICES]
    fields = [{"t": "select", "n": "topic", "l": "What is your enquiry about?", "o": topics, "r": True, "full": True}]
    hours = "".join(f'<div><b style="font-weight:500">{a}</b><br><span class="muted">{b}</span></div>' for a, b in CONFIG["hours"])
    body = f'''
{page_hero("Contact us", ["Let's start", 'a <span class="serif gold">conversation.</span>'], "Whether you're a student, a seller, an investor or simply curious, reach out and we'll connect you with the right team.", btn("Send an enquiry", "#enquiry") + btn("WhatsApp us", WA, "ghost", ' target="_blank" rel="noopener"', "chat"), [("Contact", None)], "", p=p)}

<section class="section" style="padding-top:20px">
  <div class="container">
    <h2 class="sr-only">Ways to contact Rise Joe</h2>
    <div class="feature-grid" data-stagger="0.1">
      <a class="feature spot" href="{CONFIG["maps"]}" target="_blank" rel="noopener"><div class="feature__icon">{icon("pin")}</div><h3>Main office</h3><p>{escape(CONFIG["address"])}</p><span class="link-arrow mt-40">Get directions {icon("arrow")}</span></a>
      <a class="feature spot" href="{WA}" target="_blank" rel="noopener"><div class="feature__icon">{icon("chat")}</div><h3>WhatsApp</h3><p>{escape(CONFIG["phone_display"])}<br>Official number of Rise Joe, connected with Yaseen Enterprises.</p><span class="link-arrow mt-40">Start a chat {icon("arrow")}</span></a>
      <a class="feature spot" href="mailto:{CONFIG["email"]}"><div class="feature__icon">{icon("mail")}</div><h3>Email</h3><p>{CONFIG["email"]}<br>We reply to every enquiry.</p><span class="link-arrow mt-40">Write to us {icon("arrow")}</span></a>
      <div class="feature spot"><div class="feature__icon">{icon("clock")}</div><h3>Office hours</h3><div style="display:grid;gap:12px;font-size:15px">{hours}</div></div>
    </div>
  </div>
</section>

{form_section(p, ["Send us a", '<span class="serif gold">message.</span>'], "Choose a topic and tell us how we can help. For service-specific enquiries, you can also use the dedicated form on each service page.", "Contact form", fields, "General enquiry", details_label="Your message", details_req=True, submit="Send message")}

<section class="section" style="padding-top:0">
  <div class="container">
    {section_head("Our offices", ["Three offices", 'in <span class="serif gold">Lahore.</span>'], "Two in Pak Arab Housing Society and one in Johar Town. All visits are by appointment.", "split")}
    {offices_block(p)}
  </div>
</section>
'''
    page("contact.html", "Contact Us", f"Contact Rise Joe E-Commerce Agency. Main office: {CONFIG['address']}. WhatsApp, email and office hours.", body, "contact")


# ------------------------------------------------------------------
# LEGAL + 404
# ------------------------------------------------------------------
def build_legal():
    p = ""
    privacy = f'''
{page_hero("Legal", ["Privacy", '<span class="serif gold">Notice.</span>'], "How Rise Joe E-Commerce Agency collects and uses the information you share through this website.", "", [("Privacy Notice", None)], p=p)}
<section class="section" style="padding-top:20px"><div class="container"><div class="legal" data-reveal>
<p>This notice explains how Rise Joe E-Commerce Agency ("we", "us") handles personal information submitted through this website. Please review it with your legal adviser before publishing; it is a starting template.</p>
<h2>What we collect</h2><p>Only the information you choose to submit in our enquiry forms: your name, email, optional phone/WhatsApp number, country, and the details relevant to the service you are enquiring about.</p>
<h2>What we never ask for</h2><p>We never request marketplace passwords, OTP codes, verification codes or other sensitive login credentials. Please do not include them in any form.</p>
<h2>How we use it</h2><ul><li>To respond to your enquiry and route it to the responsible team</li><li>To send you an acknowledgement and follow-up about your request</li><li>To keep a basic record of the enquiry</li></ul>
<h2>Data minimisation</h2><p>We ask only for what each service needs. We do not sell your information or share it with third parties for marketing.</p>
<h2>Retention</h2><p>Enquiry information is kept only as long as needed to handle your request and any resulting relationship.</p>
<h2>Your choices</h2><p>You may ask us to access, correct or delete your information by contacting <a class="link-arrow" href="mailto:{CONFIG["email"]}">{CONFIG["email"]}</a>.</p>
<h2>Contact</h2><p>Rise Joe E-Commerce Agency, {escape(CONFIG["address"])}.</p>
</div></div></section>'''
    page("privacy.html", "Privacy Notice", "How Rise Joe E-Commerce Agency handles personal information submitted through this website.", privacy)
    terms = f'''
{page_hero("Legal", ["Terms of", '<span class="serif gold">use.</span>'], "The terms that apply when you use this website.", "", [("Terms", None)], p=p)}
<section class="section" style="padding-top:20px"><div class="container"><div class="legal" data-reveal>
<p>These terms are a starting template and should be reviewed by a qualified legal professional before publishing.</p>
<h2>Information only</h2><p>Content on this website describes our services in general terms. It does not constitute legal, tax, financial or investment advice.</p>
<h2>No guarantees</h2><p>We do not promise or guarantee investment returns, seller-account approvals, distributor approvals, company filing outcomes, specific sales results or sourcing lead times. Any ROI or timeline figures are illustrative planning examples only.</p>
<h2>Compliance</h2><p>We work only with legitimately owned or authorised accounts and follow each marketplace's eligibility, identity and ownership rules. We do not offer account rental, identity lending or verification circumvention.</p>
<h2>Enquiries</h2><p>Submitting an enquiry does not create a contract. Any services, partnerships or investments are subject to separate written terms agreed with you.</p>
<h2>Third parties</h2><p>Marketplace names mentioned on this site are trademarks of their respective owners and are used only to describe the platforms we support.</p>
<h2>Contact</h2><p>Questions about these terms: <a class="link-arrow" href="mailto:{CONFIG["email"]}">{CONFIG["email"]}</a>.</p>
</div></div></section>'''
    page("terms.html", "Terms of Use", "Terms of use for the Rise Joe E-Commerce Agency website.", terms)
    nf = f'''
<section class="notfound">
  <canvas class="hero__canvas" data-constellation="1" aria-hidden="true"></canvas>
  <div>
    <span class="eyebrow eyebrow--center">Page not found</span>
    <h1 class="gold" style="margin:20px 0">404</h1>
    <p class="lead" style="margin:0 auto 40px">This page has moved or never existed. Let's get you back on track.</p>
    <div class="btn-row" style="justify-content:center">{btn("Back to home", "/index.html")}{btn("View services", "/services.html", "ghost")}</div>
  </div>
</section>'''
    page("404.html", "Page not found", "The page you were looking for could not be found.", nf, prefix="/")


def build_meta():
    today = date.today().isoformat()
    urls = "".join(f"\n  <url>\n    <loc>{CONFIG['site_url']}/{clean_url(pth)}</loc>\n    <lastmod>{today}</lastmod>\n  </url>"
                   for pth in PAGES if pth != "404.html")
    (OUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}\n</urlset>\n')
    (OUT / "robots.txt").write_text(
        "User-agent: *\nAllow: /\nDisallow: /send.php\nDisallow: /smtp-test.php\nDisallow: /includes/\n\n"
        f"Sitemap: {CONFIG['site_url']}/sitemap.xml\n")


if __name__ == "__main__":
    build_home(); build_about(); build_students(); build_clients(); build_investors()
    build_services()
    for i, s in enumerate(SERVICES):
        build_service(s, i)
    build_contact(); build_legal(); build_meta()
    print(f"Built {len(PAGES)} pages into {OUT}")
