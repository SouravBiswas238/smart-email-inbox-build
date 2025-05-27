import os
import re
import sys
import subprocess

# Function to install missing packages
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Try to import BeautifulSoup, install if not available
try:
    from bs4 import BeautifulSoup
except ImportError:
    print("BeautifulSoup4 not found. Installing it now...")
    install('beautifulsoup4')
    from bs4 import BeautifulSoup
    print("Installation complete.")

def main():
    checks_passed = True
    check_results = []

    # Read the content of index.html
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # Find position of "{% load static %}"
    static_load_pos = content.find("{% load static %}")

    if static_load_pos == -1:
        checks_passed = False
        check_results.append("[Error] = '{% load static %}' tag not found in index.html.")
    else:
        check_results.append("'{% load static %}' tag is included in index.html.")

    # Parse the HTML content
    soup = BeautifulSoup(content, 'html.parser')

    # Initialize lists to collect css and js files
    css_files = []
    js_files = []

    # Process <link> tags
    links = soup.find_all('link', rel='stylesheet')
    for link in links:
        href = link.get('href')
        if href:
            if "{% static '" in href and "' %}" in href:
                # Extract the filename
                m = re.search(r"{% static '(.*?)' %}", href)
                if m:
                    filename = m.group(1)
                    css_files.append((filename, href))
                else:
                    checks_passed = False
                    check_results.append(f"[Error] = Link tag with href '{href}' has incorrect static tag format.")
            else:
                checks_passed = False
                check_results.append(f"Link tag with href '{href}' does not use static tag properly.")

    # Process <script> tags
    scripts = soup.find_all('script')
    for script in scripts:
        src = script.get('src')
        if src:
            if "{% static '" in src and "' %}" in src:
                # Extract the filename
                m = re.search(r"{% static '(.*?)' %}", src)
                if m:
                    filename = m.group(1)
                    js_files.append((filename, src))
                else:
                    checks_passed = False
                    check_results.append(f"[Error] = Script tag with src '{src}' has incorrect static tag format.")
            else:
                # Ignore external scripts
                pass

    # Check that "{% load static %}" tag is included before loading static css and js files
    statics_positions = [m.start() for m in re.finditer(r"{% static", content)]

    if statics_positions:
        first_static_pos = min(statics_positions)
        if static_load_pos != -1 and static_load_pos < first_static_pos:
            check_results.append("'{% load static %}' tag is included before loading static css and js files.")
        else:
            checks_passed = False
            check_results.append("[Error] = '{% load static %}' tag is not included before loading static css and js files.")
    else:
        # No static files used
        check_results.append("[Error] = No static files found in index.html.")

    # Check if css and js files are available under ./assets/ folder
    for filename, href in css_files + js_files:
        filepath = os.path.join('.', 'assets', filename)
        if os.path.isfile(filepath):
            check_results.append(f"File '{filename}' exists in './assets/' folder.")
        else:
            checks_passed = False
            check_results.append(f"[Error] = File '{filename}' does not exist in './assets/' folder.")

    # Print all check results one by one
    for result in check_results:
        print(result)

    if not checks_passed:
        print("\nSome checks failed. Please review the issues above.")
    else:
        print("\nAll checks passed.")

if __name__ == "__main__":
    main()
