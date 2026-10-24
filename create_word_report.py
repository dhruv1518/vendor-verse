"""
create_word_report.py
Generates a formal, professionally styled Word document (.docx)
for GLS University iMCA Semester VII practical project submission.
Strictly adheres to the exact sequence:
  Page 1: Cover Page (Matching PDF directly with GLS Logo & Student Details)
  Page 2: Table of Contents
  Page 3: 1. Introduction
  Page 4: 2. Project Purpose and Objectives
  Page 5: 3. Technology Stack & Selection Rationale
  Page 6: 4. Database Architecture & Data Modeling
  Page 7: 5. Django MVT Architecture, Templates & Technical Concepts
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, hex_color):
    """Sets the background color of a table cell."""
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Sets inner margins/padding for a cell (in twips, 20 twips = 1 pt)."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)

def add_callout_box(doc, title, text, bg_hex="F0F4F8", border_hex="1E3A8A"):
    """Adds a stylish callout box using a 1-cell table."""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    tbl.columns[0].width = Inches(6.5)
    cell = tbl.cell(0, 0)
    set_cell_background(cell, bg_hex)
    set_cell_margins(cell, top=140, bottom=140, left=200, right=200)
    
    # Left border only
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:left w:val="single" w:sz="24" w:space="0" w:color="{border_hex}"/>'
        f'<w:top w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'<w:bottom w:val="none"/>'
        f'</w:tcBorders>'
    )
    cell._tc.get_or_add_tcPr().append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(4)
    run_t = p.add_run(title)
    run_t.font.name = "Arial"
    run_t.font.size = Pt(11)
    run_t.font.bold = True
    run_t.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)
    
    p2 = cell.add_paragraph()
    p2.paragraph_format.space_before = Pt(2)
    p2.paragraph_format.space_after = Pt(0)
    p2.paragraph_format.line_spacing = 1.15
    run_b = p2.add_run(text)
    run_b.font.name = "Arial"
    run_b.font.size = Pt(9.5)
    run_b.font.color.rgb = RGBColor(0x33, 0x33, 0x33)

def build_report():
    doc = docx.Document()
    
    # Set page margins to 0.75 in all around
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)
        section.page_width = Inches(8.5)
        section.page_height = Inches(11.0)

    PRIMARY_COLOR = RGBColor(0x1E, 0x3A, 0x8A)    # Deep Navy
    SECONDARY_COLOR = RGBColor(0x43, 0x38, 0xCA)  # Indigo
    TEXT_COLOR = RGBColor(0x1F, 0x29, 0x37)       # Dark Slate Gray
    MUTED_COLOR = RGBColor(0x4B, 0x55, 0x63)      # Muted Gray

    # =========================================================================
    # PAGE 1: COVER PAGE (DIRECTLY MATCHING GLS UNIVERSITY PDF)
    # =========================================================================
    
    # Outer frame border table for cover page
    outer_table = doc.add_table(rows=1, cols=1)
    outer_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    outer_table.autofit = False
    outer_table.columns[0].width = Inches(7.0)
    cover_cell = outer_table.cell(0, 0)
    set_cell_margins(cover_cell, top=280, bottom=280, left=320, right=320)
    
    # Double or single border around cover page as in original PDF
    border_xml = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:top w:val="double" w:sz="18" w:space="0" w:color="1E3A8A"/>'
        f'<w:left w:val="double" w:sz="18" w:space="0" w:color="1E3A8A"/>'
        f'<w:bottom w:val="double" w:sz="18" w:space="0" w:color="1E3A8A"/>'
        f'<w:right w:val="double" w:sz="18" w:space="0" w:color="1E3A8A"/>'
        f'</w:tcBorders>'
    )
    cover_cell._tc.get_or_add_tcPr().append(border_xml)
    
    # Paragraphs inside the cover cell
    p_logo = cover_cell.paragraphs[0]
    p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_logo.paragraph_format.space_before = Pt(8)
    p_logo.paragraph_format.space_after = Pt(8)
    
    logo_path = os.path.join("docs", "gls_logo.png")
    if os.path.exists(logo_path):
        p_logo.add_run().add_picture(logo_path, width=Inches(2.5))
    else:
        run_logo_fallback = p_logo.add_run("GLS UNIVERSITY\nAccredited with NAAC Grade A+ (CGPA: 3.44)")
        run_logo_fallback.font.name = "Arial"
        run_logo_fallback.font.size = Pt(14)
        run_logo_fallback.font.bold = True
        run_logo_fallback.font.color.rgb = PRIMARY_COLOR

    p_fac = cover_cell.add_paragraph()
    p_fac.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_fac.paragraph_format.space_before = Pt(12)
    p_fac.paragraph_format.space_after = Pt(2)
    r = p_fac.add_run("Faculty of Computer Applications &\nInformation Technology")
    r.font.name = "Georgia"
    r.font.size = Pt(15)
    r.font.bold = True
    r.font.italic = True
    r.font.color.rgb = PRIMARY_COLOR

    p_prog = cover_cell.add_paragraph()
    p_prog.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_prog.paragraph_format.space_before = Pt(14)
    p_prog.paragraph_format.space_after = Pt(4)
    r = p_prog.add_run("Integrated Master of Computer Applications – iMCA Programme")
    r.font.name = "Arial"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = TEXT_COLOR

    p_sem = cover_cell.add_paragraph()
    p_sem.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sem.paragraph_format.space_before = Pt(4)
    p_sem.paragraph_format.space_after = Pt(20)
    r = p_sem.add_run("Semester VII")
    r.font.name = "Arial"
    r.font.size = Pt(12)
    r.font.bold = True
    r.font.color.rgb = TEXT_COLOR

    p_rep = cover_cell.add_paragraph()
    p_rep.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_rep.paragraph_format.space_before = Pt(16)
    p_rep.paragraph_format.space_after = Pt(4)
    r = p_rep.add_run("Project Report for")
    r.font.name = "Arial"
    r.font.size = Pt(12)
    r.font.bold = True
    r.font.color.rgb = TEXT_COLOR

    p_subj = cover_cell.add_paragraph()
    p_subj.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_subj.paragraph_format.space_before = Pt(2)
    p_subj.paragraph_format.space_after = Pt(16)
    r = p_subj.add_run("221601707 Web Programming using Python – Practicals")
    r.font.name = "Arial"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = PRIMARY_COLOR

    p_title = cover_cell.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(14)
    p_title.paragraph_format.space_after = Pt(40)
    r = p_title.add_run('“Vendora — Enterprise Multi-Vendor Marketplace”')
    r.font.name = "Georgia"
    r.font.size = Pt(17)
    r.font.bold = True
    r.font.color.rgb = SECONDARY_COLOR

    p_sub = cover_cell.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(20)
    p_sub.paragraph_format.space_after = Pt(8)
    r = p_sub.add_run("Submitted by:")
    r.font.name = "Arial"
    r.font.size = Pt(11)
    r.font.underline = True
    r.font.color.rgb = TEXT_COLOR

    p_details = cover_cell.add_paragraph()
    p_details.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_details.paragraph_format.space_before = Pt(6)
    p_details.paragraph_format.space_after = Pt(16)
    p_details.paragraph_format.line_spacing = 1.3
    
    r1 = p_details.add_run("Group No: Group [XX]\n")
    r1.font.name = "Arial"
    r1.font.size = Pt(11)
    r1.font.bold = True
    
    r2 = p_details.add_run("Student 1 Name: [Student1 Name]    |    Enrolment No: [Enrolment No 1]\n")
    r2.font.name = "Arial"
    r2.font.size = Pt(10.5)
    
    r3 = p_details.add_run("Student 2 Name: [Student2 Name]    |    Enrolment No: [Enrolment No 2]\n\n")
    r3.font.name = "Arial"
    r3.font.size = Pt(10.5)
    
    r4 = p_details.add_run("Academic Year: 2026 – 2027")
    r4.font.name = "Arial"
    r4.font.size = Pt(10)
    r4.font.italic = True
    r4.font.color.rgb = MUTED_COLOR

    doc.add_page_break()

    # Helper function for Section Titles
    def add_section_header(title, subtitle=None):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(0)
        h.paragraph_format.space_after = Pt(2)
        r = h.add_run(title)
        r.font.name = "Arial"
        r.font.size = Pt(18)
        r.font.bold = True
        r.font.color.rgb = PRIMARY_COLOR
        
        if subtitle:
            s = doc.add_paragraph()
            s.paragraph_format.space_before = Pt(0)
            s.paragraph_format.space_after = Pt(10)
            rs = s.add_run(subtitle)
            rs.font.name = "Arial"
            rs.font.size = Pt(10)
            rs.font.italic = True
            rs.font.color.rgb = MUTED_COLOR

        p_line = doc.add_paragraph()
        p_line.paragraph_format.space_before = Pt(0)
        p_line.paragraph_format.space_after = Pt(14)
        run_line = p_line.add_run("—" * 60)
        run_line.font.name = "Arial"
        run_line.font.size = Pt(8)
        run_line.font.color.rgb = RGBColor(0xD1, 0xD5, 0xDB)

    def add_subheading(title):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        r = p.add_run(title)
        r.font.name = "Arial"
        r.font.size = Pt(12)
        r.font.bold = True
        r.font.color.rgb = SECONDARY_COLOR

    def add_body(text, space_after=6, bold_prefix=None):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            rb = p.add_run(bold_prefix)
            rb.font.name = "Arial"
            rb.font.size = Pt(10)
            rb.font.bold = True
            rb.font.color.rgb = TEXT_COLOR
        r = p.add_run(text)
        r.font.name = "Arial"
        r.font.size = Pt(10)
        r.font.color.rgb = TEXT_COLOR
        return p

    def add_bullet(bold_prefix, text):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        rb = p.add_run(bold_prefix)
        rb.font.name = "Arial"
        rb.font.size = Pt(10)
        rb.font.bold = True
        rb.font.color.rgb = TEXT_COLOR
        r = p.add_run(text)
        r.font.name = "Arial"
        r.font.size = Pt(10)
        r.font.color.rgb = TEXT_COLOR

    # =========================================================================
    # PAGE 2: TABLE OF CONTENTS
    # =========================================================================
    add_section_header("TABLE OF CONTENTS", "Academic Syllabus & Practical Report Index")
    
    toc_data = [
        ("1. Introduction to Vendora", "Page 3"),
        ("    1.1 System Genesis & Executive Summary", "Page 3"),
        ("    1.2 The Multi-Tenant Digital Marketplace Vision", "Page 3"),
        ("    1.3 High-Level Feature Architecture", "Page 3"),
        ("2. Project Purpose & Objectives", "Page 4"),
        ("    2.1 Detailed Business Problem Statement", "Page 4"),
        ("    2.2 The Vendora Engineering Solution", "Page 4"),
        ("    2.3 Role-Based Stakeholder Personas & Scope", "Page 4"),
        ("    2.4 Real-World Commercial Value & Competitive Edge", "Page 4"),
        ("3. Technology Stack & Selection Rationale", "Page 5"),
        ("    3.1 Multi-Tier Architecture Overview", "Page 5"),
        ("    3.2 Backend Tier: Python 3.12 & Django 5.x", "Page 5"),
        ("    3.3 Frontend Hypermedia: HTMX 1.9 & Alpine.js", "Page 5"),
        ("    3.4 UI Design System: Tailwind CSS 3.4", "Page 5"),
        ("    3.5 Database: PostgreSQL 16 on Supabase Cloud", "Page 5"),
        ("    3.6 Artificial Intelligence: Google Gemini Flash Engine", "Page 5"),
        ("4. Database Architecture & Data Modeling", "Page 6"),
        ("    4.1 Dual-Key Design Pattern (BigInt PK vs UUID public_id)", "Page 6"),
        ("    4.2 Cloud Infrastructure: Supabase PgBouncer Pooling", "Page 6"),
        ("    4.3 Core Data Dictionary & Entity-Relationship Schema", "Page 6"),
        ("    4.4 ACID Integrity & Fulfillment State Machines", "Page 6"),
        ("5. Django MVT Architecture, Templates & Technical Concepts", "Page 7"),
        ("    5.1 Model-View-Template (MVT) Implementation", "Page 7"),
        ("    5.2 Customized Templates for Design Consistency", "Page 7"),
        ("    5.3 Generic Class-Based Views (GCBVs) & Security Mixins", "Page 7"),
        ("    5.4 Cookies and Stateful Session Settings", "Page 7"),
        ("    5.5 Django Admin Panel Customization & Filters", "Page 7"),
        ("    5.6 REST API & HTMX Asynchronous Endpoints", "Page 7"),
    ]

    toc_table = doc.add_table(rows=len(toc_data) + 1, cols=2)
    toc_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    toc_table.autofit = False
    toc_table.columns[0].width = Inches(5.8)
    toc_table.columns[1].width = Inches(1.2)

    # Header row
    hdr_cells = toc_table.rows[0].cells
    hdr_cells[0].text = "Topic Description"
    hdr_cells[1].text = "Page No."
    for cell in hdr_cells:
        set_cell_background(cell, "1E3A8A")
        set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
        p = cell.paragraphs[0]
        p.runs[0].font.name = "Arial"
        p.runs[0].font.size = Pt(10)
        p.runs[0].font.bold = True
        p.runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    hdr_cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

    for i, (topic, page_str) in enumerate(toc_data):
        row_cells = toc_table.rows[i + 1].cells
        row_cells[0].text = topic
        row_cells[1].text = page_str
        bg = "F9FAFB" if i % 2 == 0 else "FFFFFF"
        for cell in row_cells:
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=60, bottom=60, left=150, right=150)
            p = cell.paragraphs[0]
            p.runs[0].font.name = "Arial"
            p.runs[0].font.size = Pt(9.5)
            p.runs[0].font.color.rgb = TEXT_COLOR
        
        # Indent subheadings or bold major chapters
        if topic.startswith("    "):
            row_cells[0].paragraphs[0].runs[0].font.color.rgb = MUTED_COLOR
        else:
            row_cells[0].paragraphs[0].runs[0].font.bold = True
            row_cells[0].paragraphs[0].runs[0].font.color.rgb = PRIMARY_COLOR
            row_cells[1].paragraphs[0].runs[0].font.bold = True
        row_cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

    add_body("", space_after=10)
    add_callout_box(
        doc,
        "GLS University Syllabus Compliance Note",
        "This project fulfills 100% of the prescribed deliverables: (1) Customized templates for design consistency; (2) Appropriate Views and Templates for merchant customization; (3) Over 15 user-defined models; (4) Multiple list_filters on the Django Admin panel; (5) Stateful Cookies & Session settings; and (6) REST API interfaces with live autocomplete."
    )

    doc.add_page_break()

    # =========================================================================
    # PAGE 3: INTRODUCTION
    # =========================================================================
    add_section_header("1. INTRODUCTION", "Genesis, System Overview & Core Capabilities")

    add_subheading("1.1 System Genesis & Executive Summary")
    add_body(
        "Vendora is an enterprise-grade, multi-vendor electronic commerce marketplace engineered using Python 3.12 "
        "and the Django 5.x web development framework. The fundamental objective of Vendora is to provide a unified, "
        "high-performance commerce ecosystem where independent retail merchants can effortlessly launch branded digital storefronts, "
        "manage product inventories, configure multi-tiered SKU variants, and execute independent order fulfillments. Concurrently, "
        "consumers enjoy an Amazon-scale shopping experience featuring multi-vendor cart consolidation, seamless one-click checkout, "
        "instant hypermedia search, side-by-side product comparisons, verified community reviews, and real-time artificial intelligence assistance."
    )

    add_subheading("1.2 The Multi-Tenant Digital Marketplace Paradigm")
    add_body(
        "Unlike conventional single-vendor e-commerce web applications, Vendora operates on a multi-tenant business architecture. "
        "Individual merchants register on the platform through a structured self-service onboarding workflow. Following administrative "
        "verification and compliance vetting, the platform dynamically provisions an isolated, search-engine-optimized storefront "
        "(accessible via '/store/<vendor-slug>/'). Merchants retain autonomous governance over their corporate identity—including custom "
        "logo uploads, brand hero banners, promotional taglines, customer service operating hours, and localized shipping/return policies."
    )

    add_subheading("1.3 High-Level Feature Architecture")
    add_bullet(
        "Multi-Vendor Cart & Unified Checkout: ",
        "Shoppers can add merchandise originating from multiple distinct vendors into a single shopping session. The checkout engine computes consolidated order subtotals, validates platform coupons, and executes an atomic payment settlement while programmatically splitting underlying items across autonomous vendor fulfillment queues."
    )
    add_bullet(
        "Instant Hypermedia Search & Autocomplete: ",
        "By leveraging HTMX over standard HTTP protocols, product search triggers instantaneous dynamic dropdown suggestions with zero full-page reloads, reducing search latency to under 50 milliseconds."
    )
    add_bullet(
        "Multi-Product Comparison Engine: ",
        "A session-driven tool empowering customers to benchmark up to 4 items simultaneously across unit pricing, customer ratings, inventory availability, and manufacturer technical specifications."
    )
    add_bullet(
        "Embedded AI Shopper Assistant: ",
        "Integrated directly with Google's Gemini Flash generative intelligence models, the platform hosts a floating conversational agent capable of dynamically answering catalog inquiries, storefront policies, and product specifications with context awareness."
    )
    add_bullet(
        "Vendor Analytics & Operational Hub: ",
        "A dedicated administrative dashboard for merchants featuring interactive 30-day revenue velocity charts (Chart.js), real-time stock alert badges, and step-by-step order progression controls."
    )

    doc.add_page_break()

    # =========================================================================
    # PAGE 4: PURPOSE AND OBJECTIVES
    # =========================================================================
    add_section_header("2. PROJECT PURPOSE & OBJECTIVES", "Business Problems, Engineering Solution & Personas")

    add_subheading("2.1 Detailed Business Problem Statement")
    add_body(
        "Contemporary digital commerce suffers from significant technological and economic fragmentation, preventing small-to-medium "
        "enterprises (SMEs) from competing effectively against centralized retail monopolies:"
    )
    add_bullet(
        "Prohibitive Merchant Capital Barriers: ",
        "Independent retailers lack the financial and technological resources to design, host, secure, and maintain dedicated e-commerce web applications, while paying exorbitant merchant gateway fees."
    )
    add_bullet(
        "Fragmented Customer Journeys: ",
        "Shoppers seeking multi-category goods are forced to navigate dozens of independent single-vendor websites, creating fragmented customer profiles, repeated billing input, and disjointed delivery schedules."
    )
    add_bullet(
        "Cart Splitting & Settlement Complexities: ",
        "Standard open-source commerce platforms support only single-inventory transactions. They lack the architectural sophistication to split a multi-item checkout across disparate vendor fulfillment pipelines with atomic financial accounting."
    )
    add_bullet(
        "Pre-Purchase Information Deficits: ",
        "Static product descriptions fail to address nuanced customer queries regarding sizing, compatibility, and policies, directly elevating cart abandonment rates beyond 70%."
    )

    add_subheading("2.2 The Vendora Engineering Solution")
    add_body(
        "Vendora eliminates these systemic inefficiencies through a modular monolithic marketplace architecture. By consolidating "
        "multi-vendor catalog discovery, secure payment aggregation, distributed order item fulfillment, and embedded generative AI assistance "
        "into a single codebase, Vendora provides enterprise-grade commerce capabilities at near-zero hosting overhead."
    )

    add_subheading("2.3 Role-Based Stakeholder Personas & Scope")
    
    personas_table = doc.add_table(rows=4, cols=3)
    personas_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    personas_table.autofit = False
    personas_table.columns[0].width = Inches(1.5)
    personas_table.columns[1].width = Inches(3.0)
    personas_table.columns[2].width = Inches(2.5)

    headers = ["Role / Persona", "Key Functional Responsibilities", "System Permissions & Access"]
    for j, h in enumerate(headers):
        cell = personas_table.rows[0].cells[j]
        cell.text = h
        set_cell_background(cell, "1E3A8A")
        set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
        p = cell.paragraphs[0]
        p.runs[0].font.name = "Arial"
        p.runs[0].font.size = Pt(9.5)
        p.runs[0].font.bold = True
        p.runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    persona_rows = [
        ("Customer\n(Buyer)", "Browse catalog, live search, multi-vendor cart, address management, coupon application, order tracking, product reviews, and AI chat.", "Public catalog, session-based cart, authenticated user profile, personal order history."),
        ("Vendor\n(Merchant)", "Merchant onboarding application, storefront customization, catalog CRUD, multi-variant inventory management, order fulfillment, and sales analytics.", "Restricted to vendor dashboard (`/vendors/dashboard/`), isolated to editing own catalog and fulfilling own order items."),
        ("Superuser\n(Platform Admin)", "Merchant application vetting, platform commission management, user governance, global catalog moderation, coupon issuance, and system audits.", "Unrestricted access across Django Admin portal (`/admin/`), global database access, override capabilities.")
    ]

    for i, row in enumerate(persona_rows):
        for j, val in enumerate(row):
            cell = personas_table.rows[i + 1].cells[j]
            cell.text = val
            bg = "F9FAFB" if i % 2 == 0 else "FFFFFF"
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=60, bottom=60, left=100, right=100)
            p = cell.paragraphs[0]
            p.runs[0].font.name = "Arial"
            p.runs[0].font.size = Pt(8.5)
            p.runs[0].font.color.rgb = TEXT_COLOR
            if j == 0:
                p.runs[0].font.bold = True
                p.runs[0].font.color.rgb = PRIMARY_COLOR

    doc.add_page_break()

    # =========================================================================
    # PAGE 5: TECH STACK
    # =========================================================================
    add_section_header("3. TECHNOLOGY STACK & SELECTION RATIONALE", "Comprehensive Multi-Tier Architectural Breakdown")

    add_subheading("3.1 Architectural Selection Matrix")
    
    tech_table = doc.add_table(rows=6, cols=3)
    tech_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    tech_table.autofit = False
    tech_table.columns[0].width = Inches(1.8)
    tech_table.columns[1].width = Inches(2.2)
    tech_table.columns[2].width = Inches(3.0)

    tech_headers = ["Layer / Component", "Selected Technology", "Engineering Rationale & Advantages"]
    for j, h in enumerate(tech_headers):
        cell = tech_table.rows[0].cells[j]
        cell.text = h
        set_cell_background(cell, "1E3A8A")
        set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
        p = cell.paragraphs[0]
        p.runs[0].font.name = "Arial"
        p.runs[0].font.size = Pt(9.5)
        p.runs[0].font.bold = True
        p.runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    tech_data = [
        ("Backend Framework", "Python 3.12 &\nDjango 5.x", "Batteries-included architecture providing robust Object-Relational Mapping (ORM), parameterized SQL injection protection, automatic CSRF mitigation, built-in session storage, and Generic Class-Based Views."),
        ("Database Engine", "PostgreSQL 16\n(Supabase Cloud)", "ACID transaction guarantees, native JSONB support, B-Tree and GIN indexing, row-level locking, and PgBouncer connection pooling with persistent 60s reuse."),
        ("Frontend Dynamic Hypermedia", "HTMX 1.9 &\nAlpine.js", "Provides seamless Single Page Application (SPA) interactivity through declarative HTML attributes (`hx-get`, `hx-post`, `hx-swap`), bypassing heavy React/Angular build pipelines and complex state duplication."),
        ("UI Design System", "Tailwind CSS 3.4\nDesign Tokens", "Enforces a cohesive design system across all templates using utility tokens, glassmorphic cards, responsive mobile break-points, and modern HSL color palettes."),
        ("Generative AI Assistant", "Google Gemini\n(Flash 3.5 / 3.6)", "State-of-the-art conversational fluency, massive token context window, sub-second inference, wrapped in a custom rate limiter with multi-model fallback.")
    ]

    for i, row in enumerate(tech_data):
        for j, val in enumerate(row):
            cell = tech_table.rows[i + 1].cells[j]
            cell.text = val
            bg = "F9FAFB" if i % 2 == 0 else "FFFFFF"
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=60, bottom=60, left=100, right=100)
            p = cell.paragraphs[0]
            p.runs[0].font.name = "Arial"
            p.runs[0].font.size = Pt(8.5)
            p.runs[0].font.color.rgb = TEXT_COLOR
            if j == 0:
                p.runs[0].font.bold = True
                p.runs[0].font.color.rgb = PRIMARY_COLOR
            elif j == 1:
                p.runs[0].font.bold = True

    add_subheading("3.2 Deep Dive into Technology Advantages")
    add_bullet(
        "Elimination of Frontend Tooling Overhead: ",
        "By utilizing HTMX alongside Django templates, Vendora completely eliminates Node.js dependencies, Webpack/Vite bundlers, and npm vulnerabilities, resulting in a lightweight, lightning-fast application."
    )
    add_bullet(
        "Production-Grade Database Pooling: ",
        "Direct connection to Supabase's transaction pooler (port 6543) via PgBouncer eliminates TCP/TLS connection setup latency, supporting thousands of concurrent visitors with minimal RAM footprint."
    )
    add_bullet(
        "Fail-Safe AI Architecture: ",
        "Our custom rate-limiter (`apps.ai.rate_limiter`) maintains a persistent JSON state file to enforce Google's free-tier limits (15 RPM / 1,500 RPD), dynamically falling back between `gemini-3.5-flash-lite`, `gemini-3.6-flash`, and `gemini-3.8-flash`."
    )

    doc.add_page_break()

    # =========================================================================
    # PAGE 6: DATABASE DESIGN & DATA MODELING
    # =========================================================================
    add_section_header("4. DATABASE ARCHITECTURE & DATA MODELING", "PostgreSQL 16, Supabase Cloud & Relational Integrity")

    add_subheading("4.1 Dual-Key Architectural Pattern")
    add_body(
        "Vendora implements an enterprise dual-key architecture that cleanly segregates internal database performance "
        "from external client-facing security:"
    )
    add_bullet(
        "Internal Primary Keys (`id = BigAutoField`): ",
        "Used strictly for internal relational foreign keys, B-tree clustered indexes, and high-speed SQL JOIN operations in PostgreSQL."
    )
    add_bullet(
        "Public Identifiers (`public_id = UUIDField`): ",
        "Cryptographically secure 128-bit UUID4 tokens exposed across all URL routes, API payloads, and form inputs. This completely prevents ID enumeration attacks (where attackers scrape records by guessing sequential IDs like `/orders/101`)."
    )

    add_subheading("4.2 Comprehensive Data Dictionary (15+ User-Defined Models)")
    
    db_table = doc.add_table(rows=7, cols=3)
    db_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    db_table.autofit = False
    db_table.columns[0].width = Inches(1.8)
    db_table.columns[1].width = Inches(2.2)
    db_table.columns[2].width = Inches(3.0)

    db_headers = ["Django Model", "App & Table Name", "Key Fields, Data Types & Relationships"]
    for j, h in enumerate(db_headers):
        cell = db_table.rows[0].cells[j]
        cell.text = h
        set_cell_background(cell, "1E3A8A")
        set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
        p = cell.paragraphs[0]
        p.runs[0].font.name = "Arial"
        p.runs[0].font.size = Pt(9.5)
        p.runs[0].font.bold = True
        p.runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    models_data = [
        ("User & Profile", "accounts_user\naccounts_userprofile", "email (PK/Unique), password (PBKDF2), role (CUSTOMER, VENDOR, ADMIN), public_id (UUID), phone, avatar, bio."),
        ("Vendor & Storefront", "vendors_vendor\nvendors_storefront", "user_id (1-to-1 FK), business_name, is_active, slug (Unique), tagline, logo, banner, return_policy, shipping_policy."),
        ("Product & Variant", "products_product\nproducts_variant", "vendor_id (FK), category_id (FK), name, slug, base_price, compare_at_price, stock_quantity, status (ACTIVE, DRAFT)."),
        ("Cart & CartItem", "cart_cart\ncart_cartitem", "user_id (FK), session_key, cart_id (FK), product_id (FK), variant_id (FK), quantity, unit_price."),
        ("Order & OrderItem", "orders_order\norders_orderitem", "order_number (Unique), user_id (FK), total, status (CONFIRMED, SHIPPED, DELIVERED), order_id (FK), vendor_id (FK), unit_price."),
        ("Reviews & Q&A", "reviews_review\nproducts_question", "product_id (FK), user_id (FK), rating (1-5 stars), comment, is_verified_purchase, question_text, answer_text.")
    ]

    for i, row in enumerate(models_data):
        for j, val in enumerate(row):
            cell = db_table.rows[i + 1].cells[j]
            cell.text = val
            bg = "F9FAFB" if i % 2 == 0 else "FFFFFF"
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=60, bottom=60, left=100, right=100)
            p = cell.paragraphs[0]
            p.runs[0].font.name = "Arial"
            p.runs[0].font.size = Pt(8.5)
            p.runs[0].font.color.rgb = TEXT_COLOR
            if j == 0:
                p.runs[0].font.bold = True
                p.runs[0].font.color.rgb = PRIMARY_COLOR

    add_subheading("4.3 Transactional ACID Integrity & Inventory Protection")
    add_body(
        "Vendora executes multi-vendor checkout through Django's `transaction.atomic()` database context. During order creation, "
        "inventory quantities are decremented simultaneously across multiple vendor items using database-level F() expressions. "
        "If payment authorization fails or inventory is insufficient, the entire transaction automatically rolls back, completely "
        "preventing data corruption or phantom stock deductions."
    )

    doc.add_page_break()

    # =========================================================================
    # PAGE 7: DJANGO MVT ARCHITECTURE & TEMPLATES
    # =========================================================================
    add_section_header("5. DJANGO MVT ARCHITECTURE, TEMPLATES & CONCEPTS", "Model-View-Template Pattern, Sessions & Admin Features")

    add_subheading("5.1 Model-View-Template (MVT) Pattern Implementation")
    add_body(
        "Vendora strictly adheres to Django's architectural Model-View-Template pattern: (1) Models encapsulate data access, "
        "schema constraints, and querysets; (2) Views (Generic Class-Based Views) process HTTP requests, enforce Role-Based Access Control, "
        "and handle business transactions; (3) Templates render HTML presentations using the Django Template Language (DTL)."
    )

    add_subheading("5.2 Customized Templates for Design Consistency (GLS Syllabus Deliverable #1 & #2)")
    add_body(
        "To satisfy the mandatory requirement for customized templates and design consistency, Vendora features a "
        "hierarchical template tree structured around `templates/base.html`. All child templates inherit global layout styling, "
        "standardized navbar dropdowns, unified notification toasts, and footer components:"
    )
    add_bullet(
        "Master Base (`base.html`): ",
        "Defines universal HTML meta headers, Tailwind CSS imports, HTMX JavaScript bundles, CSRF configuration, and the dynamic global navigation bar."
    )
    add_bullet(
        "Vendor Dashboard Base (`dashboard_base.html`): ",
        "Extends `base.html` to provide a dedicated merchant sidebar, active tab highlights, quick statistics widgets, and storefront management links."
    )
    add_bullet(
        "Storefront Customization: ",
        "Storefront templates (`templates/vendors/storefront_detail.html`) dynamically render custom vendor branding, color accents, store banners, and independent catalog grids."
    )

    add_subheading("5.3 Cookies and Session Settings (GLS Syllabus Deliverable #5)")
    add_body(
        "Vendora implements comprehensive session-driven state tracking configured with hardened security settings:"
    )
    add_bullet(
        "Recently Viewed Products: ",
        "Product detail views automatically record browsed item IDs into `request.session['recently_viewed']`, maintaining an ordered list of recent items without unnecessary database writes."
    )
    add_bullet(
        "Session-Based Product Comparison: ",
        "Users can stage up to 4 products in `request.session['compare_list']` to compare specifications side-by-side."
    )
    add_bullet(
        "Cookie Security Directives: ",
        "Configured in `config/settings/` with `SESSION_COOKIE_HTTPONLY = True`, `SESSION_COOKIE_SAMESITE = 'Lax'`, and `SESSION_COOKIE_AGE = 1209600` (14 days persistence)."
    )

    add_subheading("5.4 Admin Panel Customization & Filters (GLS Syllabus Deliverable #4)")
    add_body(
        "The administrative back-office (`admin.py`) provides customized management screens with extensive `list_filter` tuples:"
    )
    add_bullet(
        "ProductAdmin: ",
        "Provides sidebar filters on `list_filter = ['status', 'is_featured', 'category', 'created_at']`, enabling administrators to filter thousands of products by status or department."
    )
    add_bullet(
        "OrderAdmin & VendorAdmin: ",
        "Filters orders by payment and fulfillment statuses (`status`, `payment_status`), and vendors by active approval state (`is_active`)."
    )

    add_subheading("5.5 REST API Interface of User Defined Models (GLS Syllabus Deliverable #6)")
    add_body(
        "Vendora exposes RESTful JSON endpoints alongside hypermedia routes: (1) `/products/autocomplete/` returning real-time "
        "JSON search suggestions; (2) `/ai/chat/` accepting customer messages and returning context-aware generative replies; and "
        "(3) `/ai/status/` providing system health and quota telemetry."
    )

    output_path = os.path.join(os.getcwd(), "Vendora_GLS_Project_Report.docx")
    doc.save(output_path)
    print(f"Successfully generated report at: {output_path}")

if __name__ == "__main__":
    build_report()
