
import requests
import csv
import time

# GitHub API and token setup
GITHUB_TOKEN = "your_personal_access_token"  # Replace with your GitHub token
HEADERS = {"Authorization": f"token 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"}
USER_URL = "https://api.github.com/search/users?q=location:Moscow+followers:>50"
REPOS_URL_TEMPLATE = "https://api.github.com/users/{username}/repos"

# Function to fetch all users in Moscow with >50 followers
def fetch_users():
    users = []
    page = 1

    while True:
        print(f"Fetching page {page} of users...")
        response = requests.get(f"{USER_URL}&page={page}&per_page=30", headers=HEADERS)
        data = response.json()

        if 'items' not in data:
            print("No more data or rate-limited. Check your GitHub token.")
            break

        users.extend(data['items'])

        # Exit if last page
        if len(data['items']) < 30:
            break
        page += 1
        time.sleep(1)  # Delay to respect rate limits

    return users

# Function to fetch repositories for each user
def fetch_user_repos(username):
    repos = []
    page = 1

    while True:
        print(f"Fetching repos for {username}, page {page}...")
        response = requests.get(f"{REPOS_URL_TEMPLATE.format(username=username)}?page={page}&per_page=100", headers=HEADERS)
        data = response.json()

        if not data:
            break

        repos.extend(data)

        # Exit if last page or if we reach 500 repositories
        if len(data) < 100 or len(repos) >= 500:
            break
        page += 1
        time.sleep(1)  # Delay to respect rate limits

    return repos[:500]

# Main function to gather and save data
def main():
    users = fetch_users()

    # Open CSV files for writing
    with open("users.csv", mode="w", newline="", encoding="utf-8") as users_file, open("repositories.csv", mode="w", newline="",encoding="utf-8") as repos_file:
        users_writer = csv.writer(users_file)
        repos_writer = csv.writer(repos_file)

        # Write headers
        users_writer.writerow(["login", "name", "company", "location", "email", "hireable", "bio", "public_repos", "followers", "following", "created_at"])
        repos_writer.writerow(["login", "full_name", "created_at","stargazers_count", "watchers_count","language","has_projects","has_wiki", "license_name"])

        # Process each user
        for user in users:
            username = user['login']
            print(f"Processing user {username}...")

            # Fetch full user profile
            user_data = requests.get(f"https://api.github.com/users/{username}", headers=HEADERS).json()

            # Clean up company name
            company = user_data.get("company", "")
            if company and company.startswith("@"):
                company = company[1:].strip().upper()

            # Write user data to users.csv
            users_writer.writerow([
                user_data.get("login", ""),
                user_data.get("name", ""),
                company,
                user_data.get("location", ""),
                user_data.get("email", ""),
                str(user_data.get("hireable", "")).lower(),
                user_data.get("bio", ""),
                user_data.get("public_repos", 0),
                user_data.get("followers", 0),
                user_data.get("following", 0),
                user_data.get("created_at", "")
            ])

            # Fetch user's repositories
            repos = fetch_user_repos(username)
            for repo in repos:
                repos_writer.writerow([
                    repo.get("login",""),
                    repo.get("name",""),
                    repo.get("created_at", ""),
                    repo.get("stargazers_count", 0),
                    repo.get("watchers_count", 0),
                    repo.get("language", ""),
                    repo.get("has_projects", 0),
                    repo.get("has_wiki", ""),
                    repo.get("license", {}).get("name", "") if repo.get("license") is not None else ""
                ])

            # Respect GitHub's rate limit
            time.sleep(1)

# Run the main function
if __name__ == "__main__":
    main()