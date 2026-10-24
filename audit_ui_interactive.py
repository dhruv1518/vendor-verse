import os
import re
from pathlib import Path
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from django.conf import settings

print("=" * 70)
print("AUDITING TEMPLATE FORMS, BUTTONS & INTERACTIONS")
print("=" * 70)

template_dir = Path(settings.BASE_DIR) / 'templates'

form_issues = []
button_issues = []
post_forms_found = 0
get_forms_found = 0

for root, dirs, files in os.walk(template_dir):
    for f in files:
        if f.endswith('.html'):
            filepath = Path(root) / f
            rel_path = filepath.relative_to(template_dir)
            content = filepath.read_text(encoding='utf-8', errors='ignore')
            
            # Check all <form> tags
            form_matches = re.finditer(r'<form\b([^>]*)>(.*?)</form>', content, re.DOTALL | re.IGNORECASE)
            for fm in form_matches:
                form_attrs = fm.group(1)
                form_body = fm.group(2)
                
                method_match = re.search(r'method=[\'"]([^\'"]+)[\'"]', form_attrs, re.IGNORECASE)
                method = method_match.group(1).upper() if method_match else 'GET'
                
                if method == 'POST':
                    post_forms_found += 1
                    if 'csrf_token' not in form_body:
                        form_issues.append(f"{rel_path}: POST form is missing {{% csrf_token %}}! Attrs: {form_attrs}")
                else:
                    get_forms_found += 1
            
            # Check for dummy/dead buttons or links like href="#" or onclick="alert('...')" or missing handlers
            dead_links = re.finditer(r'<a\b[^>]*href=[\'"]#[\'"][^>]*>(.*?)</a>', content, re.IGNORECASE | re.DOTALL)
            for dl in dead_links:
                link_text = re.sub(r'<[^>]+>', '', dl.group(1)).strip()
                # If there's no @click, hx-*, or js attached, it might be dead
                full_tag = dl.group(0)
                if not any(k in full_tag.lower() for k in ['@click', 'x-on:click', 'onclick', 'hx-get', 'hx-post', ':href', 'javascript:']):
                    if link_text:
                        button_issues.append(f"{rel_path}: <a> has href='#' with no handler: '{link_text}'")

print(f"Total POST forms analyzed: {post_forms_found}")
print(f"Total GET forms analyzed: {get_forms_found}")

if form_issues:
    print(f"\n[FAIL] Found {len(form_issues)} form CSRF/method issue(s):")
    for fi in form_issues:
        print(f"  - {fi}")
else:
    print("\n[PASS] All POST forms contain valid {% csrf_token %} tags!")

if button_issues:
    print(f"\n[INFO] Found {len(button_issues)} href='#' links (checking if intentional or dead):")
    for bi in button_issues[:20]:
        print(f"  - {bi.encode('ascii', 'replace').decode('ascii')}")
    if len(button_issues) > 20:
        print(f"  ... and {len(button_issues) - 20} more.")
else:
    print("\n[PASS] No unhandled href='#' links found.")
