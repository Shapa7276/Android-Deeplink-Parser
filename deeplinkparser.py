from xml.dom.minidom import parseString
import xml.dom.minidom
import os
import subprocess
import time
import sys
import json
from datetime import datetime
import argparse
from pathlib import Path

class DeeplinkScanner:
    def __init__(self, apk_path):
        self.apk_path = apk_path
        self.apk_name = os.path.basename(apk_path)
        self.out_dir = self.apk_name.rsplit(".", 1)[0].replace(' ', '_')
        self.results_dir = "scan_results"
        self.results_file = os.path.join(self.results_dir, f"{self.out_dir}_results.json")
        self.string_resources = {}  # Cache for string resources
        self.string_resources_loaded = False
        self.resolution_stack = set() 
        
    def should_scan(self):
        """Check if results already exist for this APK"""
        if not os.path.exists(self.results_dir):
            os.makedirs(self.results_dir)
        return not os.path.exists(self.results_file)

    def load_string_resources(self):
        """Load all string resources from various values directories"""
        if self.string_resources_loaded:
            return

        try:
            # Check main values directory and language-specific directories
            values_dirs = []
            res_dir = os.path.join(self.out_dir, 'res')
            
            if os.path.exists(res_dir):
                for dir_name in os.listdir(res_dir):
                    if dir_name.startswith('values'):
                        values_dirs.append(os.path.join(res_dir, dir_name))

            for values_dir in values_dirs:
                strings_path = os.path.join(values_dir, 'strings.xml')
                if os.path.exists(strings_path):
                    self._parse_strings_file(strings_path)

            self.string_resources_loaded = True

        except Exception as e:
            print(f"Error loading string resources: {str(e)}")
            self.string_resources = {}

    def _parse_strings_file(self, file_path):
        """Parse a single strings.xml file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                strdata = f.read()
            
            strdom = parseString(strdata)
            strings = strdom.getElementsByTagName('string')
            
            for string_elem in strings:
                try:
                    # Get the name attribute
                    if string_elem.hasAttribute("name"):
                        name = string_elem.attributes["name"].value
                        
                        # Get the text content, handling CDATA and special characters
                        text = ''
                        for node in string_elem.childNodes:
                            if node.nodeType in [node.TEXT_NODE, node.CDATA_SECTION_NODE]:
                                text += node.data
                        
                        # Handle escaped characters
                        text = text.strip()
                        text = text.replace("\\'", "'")
                        text = text.replace('\\"', '"')
                        text = text.replace('\\n', '\n')
                        
                        # Store in cache
                        self.string_resources[name] = text
                
                except Exception as e:
                    print(f"Error parsing string element: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"Error parsing strings file {file_path}: {str(e)}")

    def resolve_string_reference(self, reference):
        """
        Resolve a string reference, handling nested references
        
        Args:
            reference (str): String reference like '@string/some_name'
            
        Returns:
            str: Resolved string value or None if not found
        """
        try:
            # If it's not a string reference, return as is
            if not reference.startswith('@string/'):
                return reference
                
            # Extract the resource name
            resource_name = reference.replace('@string/', '')
            
            # Check for circular references
            if resource_name in self.resolution_stack:
                print(f"Warning: Circular reference detected for '{resource_name}'")
                return None
                
            # Add to resolution stack
            self.resolution_stack.add(resource_name)
            
            try:
                # Get the value from our cached resources
                if resource_name not in self.string_resources:
                    print(f"Warning: String resource '{resource_name}' not found")
                    return None
                    
                value = self.string_resources[resource_name]
                
                # If the value is another reference, resolve it recursively
                if value.startswith('@string/'):
                    value = self.resolve_string_reference(value)
                    
                return value
                
            finally:
                # Always remove from resolution stack
                self.resolution_stack.remove(resource_name)
                
        except Exception as e:
            print(f"Error resolving string reference '{reference}': {str(e)}")
            return None

    def strdomvalue(self, name):
        """
        Resolve a string resource to its final value, handling nested references
        
        Args:
            name (str): The string resource reference (e.g., "@string/resource_name")
            
        Returns:
            str: The resolved string value or None if not found
        """
        try:
            # Load string resources if not already loaded
            if not self.string_resources_loaded:
                self.load_string_resources()
            
            # Clear resolution stack for new resolution
            self.resolution_stack.clear()
            
            # Resolve the reference
            return self.resolve_string_reference(name)
            
        except Exception as e:
            print(f"Error in strdomvalue for '{name}': {str(e)}")
            return None

    def deeplink(self):
        deeplinks = []
        try:
            with open(f'{self.out_dir}/AndroidManifest.xml', 'r') as f:
                data = f.read()
            
            dom = parseString(data)
            activities = dom.getElementsByTagName('activity') + dom.getElementsByTagName('activity-alias')
            package = dom.getElementsByTagName('manifest')
            
            for lol in package:
                package_name = lol.attributes["package"].value

            for activity in activities:
                activity_deeplinks = []
                intentFilterTag = activity.getElementsByTagName("intent-filter")
                if len(intentFilterTag) > 0:
                    activity_name = activity.attributes["android:name"].value
                    for intent in intentFilterTag:
                        # Process all data tags in this intent filter together
                        dataTags = intent.getElementsByTagName("data")
                        if len(dataTags) > 0:
                            deeplink_urls = self.process_intent_filter_data(dataTags)
                            activity_deeplinks.extend(deeplink_urls)
                    
                    if activity_deeplinks:
                        deeplinks.append({
                            "activity": activity_name,
                            "deeplinks": activity_deeplinks
                        })
            
            return deeplinks
        except Exception as e:
            print(f"Error processing deeplinks: {str(e)}")
            return []

    def process_intent_filter_data(self, dataTags):
        """Process all data tags in an intent filter to handle multiple schemes, hosts, and paths"""
        urls = []
        
        # Collect all components
        schemes = set()
        hosts = set()
        path_prefixes = set()
        path_patterns = set()
        
        # First pass: collect all components
        for data in dataTags:
            if data.hasAttribute("android:scheme"):
                scheme_value = data.attributes["android:scheme"].value
                scheme = self.strdomvalue(scheme_value) if "@string" in scheme_value else scheme_value
                if scheme:
                    schemes.add(scheme)
                    
            if data.hasAttribute("android:host"):
                host_value = data.attributes["android:host"].value
                host = self.strdomvalue(host_value) if "@string" in host_value else host_value
                if host:
                    hosts.add(host)
                    
            if data.hasAttribute("android:pathPrefix"):
                path_value = data.attributes["android:pathPrefix"].value
                path = self.strdomvalue(path_value) if "@string" in path_value else path_value
                if path:
                    # Remove trailing wildcard if present
                    path = path.rstrip('.*')
                    path_prefixes.add(path)
                    
            if data.hasAttribute("android:pathPattern"):
                path_value = data.attributes["android:pathPattern"].value
                path = self.strdomvalue(path_value) if "@string" in path_value else path_value
                if path:
                    # Convert Android path pattern to a more readable format
                    # Replace .* with {wildcard} for clarity
                    path = path.replace(".*", "{wildcard}")
                    # Replace /.* at the start with {wildcard}/ for clarity
                    path = path.replace("/.*", "{wildcard}/")
                    path_patterns.add(path)
        
        # Generate URLs for all valid combinations
        for scheme in schemes:
            for host in hosts:
                # Base URL without path
                base_url = f"{scheme}://{host}"
                
                # Add URLs with path prefixes
                for prefix in path_prefixes:
                    # Ensure prefix starts with /
                    if not prefix.startswith('/'):
                        prefix = '/' + prefix
                    urls.append(f"{base_url}{prefix}")
                
                # Add URLs with path patterns
                for pattern in path_patterns:
                    # Ensure pattern starts with /
                    if not pattern.startswith('/'):
                        pattern = '/' + pattern
                    urls.append(f"{base_url}{pattern}")
                
                # If no paths specified, add the base URL
                if not path_prefixes and not path_patterns:
                    urls.append(base_url)
        
        return sorted(list(set(urls)))  # Remove duplicates and sort

    def generate_html_report(self, results):
            """Generate an HTML report from scan results"""
            # Read the HTML template
            html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>APK Deeplink Report</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
        }
        .activity-section {
            margin: 20px 0;
            padding: 15px;
            background: #f8f9fa;
            border-left: 4px solid #007bff;
            border-radius: 4px;
        }
        .activity-name {
            color: #343a40;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .deeplink {
            display: block;
            padding: 8px 12px;
            margin: 5px 0;
            background: #e9ecef;
            border-radius: 4px;
            color: #007bff;
            text-decoration: none;
            word-break: break-all;
        }
        .deeplink:hover {
            background: #dee2e6;
        }
        .timestamp {
            color: #6c757d;
            font-size: 0.9em;
            margin-top: 20px;
        }
        .exported-section {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 2px solid #eee;
        }
        .exported-component {
            padding: 8px 12px;
            margin: 5px 0;
            background: #e9ecef;
            border-radius: 4px;
            font-family: monospace;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Deeplink Report  </h1> 
        <h3>{APK_Name}<h3> 
        
        <div id="timestamp" class="timestamp">

            Generated on: <script>document.write(new Date().toLocaleString())</script>
            
        </div>
        
        <div id="deeplinks">
            <h2>Deeplinks by Activity</h2>
            {DEEPLINKS_PLACEHOLDER}
        </div>

        <div class="exported-section">
            <h2>Exported Components</h2>
            {EXPORTED_PLACEHOLDER}
        </div>
    </div>
</body>
</html>"""  # Copy the HTML content from above
            
            # Generate deeplinks HTML
            deeplinks_html = []
            for activity in results['deeplinks']:
                activity_html = f"""
                <div class="activity-section">
                    <div class="activity-name">{activity['activity']}</div>
                    <div class="deeplinks">
                """
                
                for deeplink in activity['deeplinks']:
                    # Create clickable link
                    activity_html += f'<a href="{deeplink}" class="deeplink" target="_blank">{deeplink}</a>\n'
                
                activity_html += "</div></div>"
                deeplinks_html.append(activity_html)
            
            # Generate exported components HTML
            exported_html = []
            for comp_type, components in results['exported_components'].items():
                if components:
                    exported_html.append(f"<h3>{comp_type.title()}</h3>")
                    for component in components:
                        exported_html.append(f'<div class="exported-component">{component}</div>')
            
            # Replace placeholders
            html_content = html_template.replace(
                "{DEEPLINKS_PLACEHOLDER}", 
                "\n".join(deeplinks_html)
            ).replace(
                "{EXPORTED_PLACEHOLDER}",
                "\n".join(exported_html)
            ).replace("{APK_Name}","\n".join(results['apk_name'])
                      )
            
            # Save HTML report
            report_path = os.path.join(self.results_dir, f"{self.out_dir}_report.html")
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return report_path

    def process_data_tag(self, data):
        if not data.attributes:
            return None
            
        scheme = host = path = None
        
        if data.hasAttribute("android:scheme"):
            scheme_value = data.attributes["android:scheme"].value
            scheme = self.strdomvalue(scheme_value) if "@string" in scheme_value else scheme_value
            
        if data.hasAttribute("android:host"):
            host_value = data.attributes["android:host"].value
            host = self.strdomvalue(host_value) if "@string" in host_value else host_value
            
        for path_type in ["android:pathPrefix", "android:pathPattern", "android:path"]:
            if data.hasAttribute(path_type):
                path_value = data.attributes[path_type].value
                path = self.strdomvalue(path_value) if "@string" in path_value else path_value
                break
                
        if scheme:
            if host:
                return f"{scheme}://{host}{path if path else ''}"
            return f"{scheme}://"
        return None

    def exported_components(self):
        exported = {
            "activities": [],
            "receivers": [],
            "providers": [],
            "services": []
        }
        
        with open(f'{self.out_dir}/AndroidManifest.xml', 'r') as f:
            data = f.read()
        
        dom = parseString(data)
        
        # Process each component type
        components = {
            "activities": dom.getElementsByTagName('activity') + dom.getElementsByTagName('activity-alias'),
            "receivers": dom.getElementsByTagName('receiver'),
            "providers": dom.getElementsByTagName('provider'),
            "services": dom.getElementsByTagName('service')
        }
        
        for comp_type, elements in components.items():
            for element in elements:
                if element.hasAttribute("android:exported"):
                    if str(element.attributes["android:exported"].value) == 'true':
                        exported[comp_type].append(element.attributes["android:name"].value)
        
        return exported

    def scan(self):
        if not self.should_scan():
            print(f"Results already exist for {self.apk_name}. Loading cached results...")
            results = self.load_results()
        else:
            # Decompile APK
            cmd = f"apktool d {self.apk_path} -o {self.out_dir}"
            print(f"Decompiling APK: {cmd}")
            os.system(cmd)

            # Scan for deeplinks and exported components
            results = {
                "apk_name": self.apk_name,
                "scan_date": datetime.now().isoformat(),
                "deeplinks": self.deeplink(),
                "exported_components": self.exported_components()
            }

            # Save results
            self.save_results(results)
            
            # Clean up decompiled files
            if os.path.exists(self.out_dir):
                import shutil
                shutil.rmtree(self.out_dir)
        
        # Generate HTML report
        report_path = self.generate_html_report(results)
        print(f"\nHTML report generated: {report_path}")
        
        return results
    def save_results(self, results):
        with open(self.results_file, 'w') as f:
            json.dump(results, f, indent=4)
        print(f"Results saved to {self.results_file}")

    def load_results(self):
        with open(self.results_file, 'r') as f:
            return json.load(f)

def validate_apk(apk_path):
    """Validate APK file exists and has correct extension"""
    path = Path(apk_path)
    
    if not path.exists():
        print(f"Error: APK file not found: {apk_path}")
        sys.exit(1)
        
    if path.suffix.lower() != '.apk':
        print(f"Error: File does not have .apk extension: {apk_path}")
        sys.exit(1)
        
    return path.absolute()

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Android APK Deeplink Scanner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python script.py -a path/to/app.apk
  python script.py --apk app.apk
  python script.py -a app.apk --force  # Force rescan even if results exist
        '''
    )
    
    parser.add_argument(
        '-a', '--apk',
        required=True,
        help='Path to the APK file to analyze'
    )
    
    parser.add_argument(
        '-f', '--force',
        action='store_true',
        help='Force rescan even if results already exist'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Custom output directory for results (default: scan_results)',
        default='scan_results'
    )
    
    return parser.parse_args()

def main():
    # Parse arguments
    args = parse_arguments()
    
    # Validate APK file
    apk_path = validate_apk(args.apk)
    
    try:
        # Initialize scanner with custom output directory
        scanner = DeeplinkScanner(str(apk_path))
        
        # Override output directory if specified
        if args.output:
            scanner.results_dir = args.output
            
        # Override cache check if force flag is used
        if args.force:
            scanner.should_scan = lambda: True
        
        # Run the scan
        print(f"\nScanning APK: {apk_path}")
        results = scanner.scan()
        
        print("\nScan completed successfully!")
        print(f"Results saved to: {scanner.results_file}")
        print(f"HTML report available at: {scanner.results_dir}/{scanner.out_dir}_report.html")
        
    except Exception as e:
        print(f"\nError during scan: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()