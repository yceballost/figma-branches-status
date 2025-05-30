import requests
import pandas as pd
import os
import re
import sys
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

# Function to get the status of an issue from GitHub Projects (GraphQL)
def get_issue_status(repo_owner, repo_name, issue_number, github_token):
    url = "https://api.github.com/graphql"
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    query = """
    query($owner: String!, $repo: String!, $issueNumber: Int!) {
      repository(owner: $owner, name: $repo) {
        issue(number: $issueNumber) {
          projectItems(first: 50) {
            nodes {
              fieldValueByName(name: "Status") {
                ... on ProjectV2ItemFieldSingleSelectValue {
                  name
                }
              }
            }
          }
        }
      }
    }
    """
    
    variables = {
        "owner": repo_owner,
        "repo": repo_name,
        "issueNumber": int(issue_number)
    }
    
    response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)
    
    print("GitHub GraphQL Response:", response.json()) 
    
    if response.status_code == 200:
        data = response.json()
        try:
            status = data["data"]["repository"]["issue"]["projectItems"]["nodes"][0]["fieldValueByName"]["name"]
            return status if status else "No Status"
        except (IndexError, TypeError, KeyError):
            return "Unknown"
    else:
        print(f"Error fetching issue status: {response.status_code} - {response.text}")
        return "Error"

# Function to get the files from specific Figma projects
def get_figma_project_files(project_ids, figma_token):
    headers = {
        "X-Figma-Token": figma_token
    }
    file_keys = []
    
    for project_id in project_ids:
        print(f"Fetching files for project ID: {project_id}")
        project_files_url = f"https://api.figma.com/v1/projects/{project_id}/files"
        files_response = requests.get(project_files_url, headers=headers)
        
        if files_response.status_code == 200:
            files = files_response.json().get("files", [])
            for file in files:
                file_keys.append({"key": file["key"], "name": file["name"]})
        else:
            print(f"Error fetching files for project {project_id}: {files_response.status_code}")
    
    return file_keys

# Function to get information from a Figma file, using the branch_data=true parameter
def get_figma_file_data(file_key, figma_token):
    headers = {
        "X-Figma-Token": figma_token
    }
    url = f"https://api.figma.com/v1/files/{file_key}?branch_data=true"
    response = requests.get(url, headers=headers, verify=True)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching data for file {file_key}: {response.status_code}")
        return None

# Function to format the time difference into years, months, and days
def format_time_difference(days):
    years = days // 365
    remaining_days = days % 365
    months = remaining_days // 30
    remaining_days = remaining_days % 30

    # Build the formatted string based on the components
    formatted_time = []
    if years > 0:
        formatted_time.append(f"{years} yr{'s' if years > 1 else ''}")
    if months > 0:
        formatted_time.append(f"{months} mo")
    if remaining_days > 0 or (years == 0 and months == 0):
        formatted_time.append(f"{remaining_days} d")
    if remaining_days == 0 and years == 0 and months == 0:
        return "Today"
    
    return ", ".join(formatted_time)

# Function to process files and generate a table with the desired information
def analyze_files(file_keys, figma_token, repo_owner, repo_name, github_token):
    table_data = []
    
    for file in file_keys:
        file_key = file["key"]
        file_name = file["name"]
        file_data = get_figma_file_data(file_key, figma_token)
        
        if file_data:
            branches = file_data.get("branches", [])
            num_branches = len(branches)
            
            if num_branches > 0:
                first_branch = True
                for branch in branches:
                    branch_name = branch["name"]
                    branch_link = f"[{branch_name}](https://www.figma.com/file/{file_key}/branch/{branch['key']})"
                    
                    # Extract the issue number using regex
                    issue_match = re.match(r"#(\d+)", branch_name)
                    issue_number = issue_match.group(1) if issue_match else None
                    issue_display = f"#{issue_number}" if issue_number else ""

                    # Get the issue status from GitHub
                    issue_status = get_issue_status(repo_owner, repo_name, issue_number, github_token) if issue_number else ""

                    # Calculate the days since the last modification using timezone-aware datetime
                    last_modified_str = branch["last_modified"]
                    last_modified_dt = datetime.strptime(last_modified_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                    current_time = datetime.now(timezone.utc)
                    days_since_modification = (current_time - last_modified_dt).days
                    
                    # Format the time difference
                    formatted_time = format_time_difference(days_since_modification)
                    
                    table_data.append({
                        "File Name": file_name if first_branch else "",
                        "Branch Names": branch_link,
                        "Issue": issue_display,
                        "Status": issue_status,
                        "Last Modification": formatted_time
                    })

                    first_branch = False
    
    df = pd.DataFrame(table_data)
    return df

# Function to update the issue on GitHub
def update_github_issue(issue_number, repo_owner, repo_name, markdown_content, github_token):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues/{issue_number}"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "body": markdown_content
    }

    response = requests.patch(url, json=data, headers=headers)

    if response.status_code == 200:
        print(f"Issue #{issue_number} updated successfully")
    else:
        print(f"Failed to update issue #{issue_number}: {response.status_code} - {response.text}")

# Debug information
print("Environment variables:")
print(f"GITHUB_REPOSITORY: {os.getenv('GITHUB_REPOSITORY')}")
print(f"PROJECT_ID: {os.getenv('PROJECT_ID')}")
print(f"ISSUE_NUMBER: {os.getenv('ISSUE_NUMBER')}")

# Personal access token for Figma and GitHub APIs
figma_token = os.getenv("FIGMA_TOKEN")
if not figma_token:
    print("Error: FIGMA_TOKEN environment variable is not set.")
    sys.exit(1)
    
github_token = os.getenv("GITHUB_TOKEN")
if not github_token:
    print("Error: GITHUB_TOKEN environment variable is not set.")
    sys.exit(1)

repo_full = os.getenv("GITHUB_REPOSITORY")  # e.g. "owner/name"
if repo_full and "/" in repo_full:
    repo_owner, repo_name = repo_full.split("/", 1)
else:
    print("Error: Invalid GITHUB_REPOSITORY format. Expected 'owner/name'.")
    sys.exit(1)

# List of Figma project IDs
project_id_env = os.getenv("PROJECT_ID")
if not project_id_env:
    print("Error: No project ID provided in the environment variable PROJECT_ID.")
    sys.exit(1)
    
project_ids = [pid.strip() for pid in project_id_env.split(",") if pid.strip()]
if not project_ids:
    print("Error: No valid project IDs found after parsing PROJECT_ID.")
    sys.exit(1)
    
print(f"Using project IDs: {project_ids}")

# Get issue number from environment variable (with fallback to default)
issue_number_env = os.getenv("ISSUE_NUMBER", "1927")
try:
    issue_number = int(issue_number_env)
    print(f"Using issue number: {issue_number}")
except ValueError:
    print(f"Error: Invalid issue number '{issue_number_env}'. Must be an integer.")
    sys.exit(1)

# Fetch all file keys from the specified Figma projects
file_keys = get_figma_project_files(project_ids, figma_token)
if not file_keys:
    print("Warning: No files found in the specified projects.")
    sys.exit(0)

# Analyze the files and generate the table
df = analyze_files(file_keys, figma_token, repo_owner, repo_name, github_token)
if df.empty:
    print("Warning: No data to display. The result table is empty.")
    markdown_table = "No branches found in the specified Figma projects."
else:
    # Convert the table to markdown format
    markdown_table = df.to_markdown(index=False)

# Update the issue on GitHub
update_github_issue(issue_number, repo_owner, repo_name, markdown_table, github_token)

# Print the table to the console
print(markdown_table)