# modules/scanning/subdomain_enumeration.py

import os
from config import Config
from modules.execution import execute_tool

def enumerate_subdomains(domain):
    output_dir = os.path.join(Config.OUTPUT_DIR, f'subdomains_{domain}')
    os.makedirs(output_dir, exist_ok=True)

    subdoms_output = os.path.join(output_dir, f'{domain}_subdoms.txt')

    # Assetfinder
    execute_tool(Config.TOOL_PATHS['assetfinder'] + ' ' + domain + ' > ' + subdoms_output)

    # Subfinder
    execute_tool('sudo ' + Config.TOOL_PATHS['subfinder'] + ' -d ' + domain + ' -silent -all | anew ' + subdoms_output)

    # Chaos Client
    execute_tool(Config.TOOL_PATHS['chaos'] + ' -d ' + domain + ' | anew ' + subdoms_output)

    # Sorting and removing duplicates
    sorted_output = os.path.join(output_dir, f'{domain}_sorted_subdoms.txt')
    execute_tool('cat ' + subdoms_output + ' | sort -u | tee ' + sorted_output)

    return sorted_output
