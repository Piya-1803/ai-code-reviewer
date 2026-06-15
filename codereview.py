import os 
import anthropic 
from github import Github , Auth

Anthropic_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

claude = anthropic.Anthropic()
auth = Auth.Token(GITHUB_TOKEN)
github = Github(auth=auth)


# Defining tools

tools = [
    {
        "name" : "post_comment",
        "description" : "Post a review comment on the PR when you find a bug, security issue,or bag practice. call this for every single issue you find.",
        "input_schema":{
            "type": "object",
            "properties": {
                "filename": {
                    "type":"string",
                    "description":"The file where the issue was found  e.g app.py"
                },
                "issue": {
                    "type": "string",
                    "description":"Clear explaination of the bug and exactly how to fix it"
                }
            },
            "required": ["filename","issue"]
        }
    },
    {
        "name": "request_changes",
        "description":"Call this when you found bugs or issues that MUST be fixed before merging . Call this after you haveposted all individual comments.",
        "input_schema":{
            "type": "object",
            "properties":{
                "summary":{
                    "type":"string",
                    "description":"Overall summary of all the issues found that need to be fixed"
                }
            },
            "required": ["summary"]

        }
    },
    {
        "name": "approve_pr",
        "description": "Call this ONLY when the code looks good with no bugs or issues. call this after reviewing everything",
        "input_schema": {
            "type":"object",
            "properties" : {
                "summary": {
                    "type": "string",
                    "description": "Summary of why the code is good and safe to merge"
                }
            },
            "required": ["summary"]
        }
    }
]


#Fuctions for those tools 

def get_pr_diff(repo_name,pr_number):
    """
    Fetches all changed code from a PR.
    Returns one big string with all the changes.
    This is what Claude will read to do the review.
    """

    repo = github.get_repo(repo_name)  
    pr = repo.get_pull(pr_number)

    full_diff = ""

    for file in pr.get_files():
            full_diff += f"\nFile : {file.filename}\n"
            if file.patch:
                    full_diff += file.patch
            full_diff += "\n"
    return full_diff

def post_github_comment(repo_name,pr_number,filename,issue):
    """
    Posts a single bug comment on the GitHub PR.
    Called every time Claude finds one issue.
    """
    repo = github.get_repo(repo_name)  
    pr = repo.get_pull(pr_number)

    comment = f" ** AI Code review - '{filename}'  ** \n\n {issue}"

    pr.create_issue_comment(comment)
    print(f"Comment posted on {filename}")

def post_request_changes (repo_name , pr_number , summary):
    """
    Posts the final summary when bugs were found.
    This tells the developer what needs to be fixed.
    """
    repo = github.get_repo(repo_name)
    pr = repo.get_pull(pr_number)

    comment = f"** AI CODE REVIEW - CHANGES REQUIRED \n\n {summary}"

    pr.create_issue_comment(comment)
    print(" Changes requested!")

def post_approval(repo_name,pr_number,summary):
    """
    Posts the final summary when code looks clean.
    This tells the developer the code is good to merge.
    """
    repo = github.get_repo(repo_name)
    pr = repo.get_pull(pr_number)  

    comment = f"** AI Code Review — Approved!**\n\n{summary}"

    pr.create_issue_comment(comment)
    print("  PR Approved!")
def run_tool(tool_name, tool_input, repo_name, pr_number):
    """
    Receives the tool name and inputs from Claude.
    Runs the matching real function.
    Returns a result string back to Claude.
    """

    if tool_name == "post_comment":
       
        post_github_comment(
            repo_name,
            pr_number,
            tool_input["filename"],   
            tool_input["issue"]       
        )
        return "Comment posted successfully" 
    elif tool_name == "request_changes":
        
        post_request_changes(
            repo_name,
            pr_number,
            tool_input["summary"]     
        )
        return "Changes requested successfully"

    elif tool_name == "approve_pr":
        
        post_approval(
            repo_name,
            pr_number,
            tool_input["summary"]     
        )
        return "PR approved successfully"

def review_pr(repo_name,pr_number):
     print (f"\n Starting review of PR #{pr_number} in {repo_name}")

     diff = get_pr_diff(repo_name , pr_number)
     print ("Code fetched from github")

     messages = [
          {
              "role": "user",
            "content": f"""You are an expert code reviewer.

Review the following Pull Request code changes carefully.

For every bug, security issue, or bad practice you find:
- Call post_comment with the filename and a detailed explanation of the issue and how to fix it

After reviewing ALL the code:
- If you found issues: call request_changes with an overall summary
- If code looks clean: call approve_pr with a positive summary

Here are the code changes to review:

{diff}"""
          }
     ]

     print ("Claude is reviewing\n")

     while True:
            response = claude.messages.create(
               model = "claude-sonnet-4-6",
               max_tokens = 4096,
               tools = tools,
               messages = messages 
          )
            messages.append({
                  "role" : "assistant",
                  "content": response.content
            })
            if response.stop_reason == "end_turn":
           
                print("\n🎉 Review complete! Check your GitHub PR for comments.")
                break

            elif response.stop_reason == "tool_use":
            

                tool_results = [] 

            for block in response.content:
                
                if block.type == "tool_use":
                    print(f"🔧 Claude calling: {block.name}")
                    print(f"   Input: {block.input}")

                    
                    result = run_tool(
                        block.name,     
                        block.input,    
                        repo_name,
                        pr_number
                    )

                    
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,   
                        "content": result
                    })

            messages.append({
                "role": "user",
                "content": tool_results
            })


repo_name = os.environ.get("REPO_NAME")   
pr_number = int(os.environ.get("PR_NUMBER"))  

review_pr(repo_name, pr_number)

            