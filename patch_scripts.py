import os

html_files = [f for f in os.listdir('.') if f.endswith('.html')]

custom_tags = """
  <!-- Custom Alerts & Responsive CSS -->
  <link rel="stylesheet" href="assets/custom_alert.css">
  <link rel="stylesheet" href="assets/responsive.css">
</head>"""

custom_script = """
  <!-- Custom Alerts JS -->
  <script src="assets/custom_alert.js"></script>
</body>"""

for f in html_files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    modified = False
    if 'custom_alert.css' not in content and '</head>' in content:
        content = content.replace('</head>', custom_tags)
        modified = True
        
    if 'custom_alert.js' not in content and '</body>' in content:
        content = content.replace('</body>', custom_script)
        modified = True
        
    if modified:
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"Patched {f}")

print("Done patching.")
