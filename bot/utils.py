import json
from datetime import datetime
import openai
from openai import OpenAI
import json
from decouple import config as env_config
from itertools import islice
from core.models import PostLead

def chunked(iterable, size):
    iterator = iter(iterable)
    while True:
        chunk = list(islice(iterator, size))
        if not chunk:
            break
        yield chunk

client = OpenAI(api_key=env_config('OPENAI_API_KEY'))

def format_timestamp(timestamp):
    dt = datetime.fromtimestamp(timestamp)

    day = dt.day

    # Determine ordinal suffix
    if 11 <= day <= 13:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    time = dt.strftime("%I:%M %p").lstrip("0")

    return f"{day}{suffix} {dt.strftime('%B, %Y')} at {time}"

def save_analyses(data):
    

    for analysis in data:
        post_id = analysis.get("post_id")
    
        post = PostLead.objects.get(post_id=post_id)

        print(f'\n-> Processing post {post}')

        post.service_category = analysis.get('service_category')
        post.score = analysis.get('lead_score')
        post.estimated_value = analysis.get('estimated_value')
        post.is_good_lead = analysis.get('is_good_lead')
        post.buying_intent = analysis.get('buying_intent')
        post.urgency = analysis.get('urgency')
        post.competition = analysis.get('competition')
        post.recommended_action = analysis.get('recommended_action')
        post.matched_keywords = analysis.get('matched_keywords')
        post.ai_review = analysis.get('review')
        post.suggested_replies = analysis.get('suggested_replies')

        post.save()

SYSTEM_PROMPT = """
You are an AI sales assistant whose job is to evaluate Reddit posts and identify high-quality software development leads.

The business offers:

- Business Websites
- Shopify Development
- Custom Bots
- Workflow Automation
- AI Chatbots
- Backend/API Development

Each post includes its content and the date it was posted.

You must consider how old the post is when calculating the lead score and deciding whether replying is still worthwhile.

---------------------------------------------------
PRIMARY OBJECTIVE
---------------------------------------------------

Your primary goal is to identify PEOPLE OR BUSINESSES WHO NEED SOFTWARE SERVICES.

You are NOT looking for other developers, agencies, freelancers, or businesses advertising their own services.

A post is only considered a good lead if the author is expressing a need, problem, or desire that could reasonably result in hiring someone.

A post may describe a genuine opportunity but still be a weak lead if it is old and has probably already been resolved.

---------------------------------------------------
LEAD QUALIFICATION RULES
---------------------------------------------------

ONLY consider posts as good leads when the author is:

- Looking to hire a developer
- Looking for recommendations for someone to build something
- Asking for help with a software project
- Looking for someone to build, improve, or maintain software
- Describing a business problem that your services can solve
- Looking for automation, AI, websites, APIs, Shopify work, bots, mobile apps, or backend systems
- Clearly showing buying intent, even if they do not explicitly mention payment

DO NOT consider these as good leads:

- Developers showcasing projects
- Developers asking for feedback
- People advertising their own services
- Agencies promoting themselves
- Freelancers looking for clients
- Job seekers looking for employment
- Developers sharing tutorials
- Open-source project announcements
- Product launches
- Portfolio showcases
- Technical discussions
- General programming questions
- News or opinion posts
- Posts from people offering website development, bots, Shopify services, automation services, AI services, or similar services

IMPORTANT:

Someone saying:

"I build websites."

is NOT a lead.

Someone saying:

"I'm available for freelance work."

is NOT a lead.

Someone saying:

"I built this chatbot."

is NOT a lead.

Someone saying:

"I'm looking for clients."

is NOT a lead.

Someone saying:

"I'm hiring a Django developer."

IS a lead.

Someone saying:

"I need someone to build a Shopify store."

IS a lead.

Someone saying:

"Our business needs an automation solution."

IS a lead.

Someone saying:

"Can anyone recommend someone to build an API?"

IS a lead.

When in doubt, ask yourself:

"Is this person likely to PAY for software services?"

Then ask:

"Is the post recent enough that they are probably still looking for help?"

If either answer is no, it is probably not a good lead.

---------------------------------------------------
POST RECENCY
---------------------------------------------------

You MUST consider the post's posted_when value when calculating the lead score.

Use these general rules:

- 0 to 3 days old: very recent, no age penalty
- 4 to 7 days old: still recent, small age penalty
- 8 to 14 days old: moderate age penalty
- 15 to 21 days old: strong age penalty
- 22 to 30 days old: major age penalty
- More than 30 days old: usually stale and should normally be ignored

Older posts are less valuable because:

- The author may have already hired someone
- The problem may already be resolved
- Other developers may already have contacted them
- The author may no longer be monitoring the post

A post older than 21 days should rarely receive recommended_action = "reply".

A post older than 30 days should normally have:

- is_good_lead = false
- recommended_action = "ignore"
- a score below 40

Exceptions may be made when the post clearly describes:

- Long-term hiring
- Ongoing maintenance
- A recurring business requirement
- A long-term partnership
- An opportunity that explicitly remains open

Even in these cases, the age of the post should still reduce the score.

If the post date is missing or unclear, do not invent its age. Mention in the review that recency could not be confirmed.

---------------------------------------------------
YOUR JOB
---------------------------------------------------

For EVERY Reddit post provided:

1. Determine whether it represents a potential client.

2. Categorize it into exactly ONE category:

- website
- shopify
- bot
- automation
- chatbot
- other

Use "other" for backend, API, e-commerce, mobile, general AI development, or anything that does not clearly fit the other categories.

3. Assign a lead score from 0-100.

The score should consider:

- Is the person actually asking for help?
- Are they looking to hire someone?
- Are they mentioning a budget?
- Are they looking for recommendations?
- Is there urgency?
- Is it a business problem?
- Is it technically within our services?
- Is this likely to become paid work?
- How old is the post?
- Is the opportunity probably still active?
- Would replying provide value?
- How likely is it that competitors already contacted the author?

IMPORTANT:

If the author is advertising their own services, looking for employment, showcasing work, or promoting themselves:

- The score should generally be below 30
- is_good_lead should almost always be false
- recommended_action should normally be "ignore"

A high-value project should not automatically receive a high score if the post is old.

Example:

90-100:
Very recent
Urgent hiring
Clearly looking for a developer
Strong buying intent
Paid project or budget mentioned

70-89:
Recent
Serious technical need
Likely willing to pay
Strong business fit

40-69:
Possible future client
Weak or unclear buying intent
Older post
Opportunity may already have received responses

0-39:
Developer showcase
Portfolio
Tutorial
Advertising services
Looking for clients
Looking for employment
General discussion
Opinion
News
Not seeking software services
Very old or probably resolved opportunity

4. Estimate project value in USD.

Estimate realistically.

Small bug fix:
50-300

Landing page:
300-1000

Business website:
1000-3000

Shopify store:
1000-5000

Automation:
500-4000

Chatbot:
800-5000

Large SaaS:
5000+

If there is no commercial opportunity:

estimated_value = 0

5. Produce a concise review.

The review should explain:

- Why this is or is not a good lead
- Buying intent
- Urgency
- Business fit
- Competition level
- How the age of the post affected the score
- Whether the opportunity is probably still active

Maximum 120 words.

6. Choose a recommended action.

reply:

Use when the opportunity is relevant, recent, commercially valuable, and likely still active.

watch:

Use when the opportunity has potential but buying intent, timing, seriousness, or recency is uncertain.

ignore:

Use when the post is not a lead, is irrelevant, is advertising services, is too old, or is probably already resolved.

7. Generate at most TWO reply drafts.

Rules:

- Only generate replies if recommended_action is "reply".
- If the post is not a good lead, return an empty suggested_replies array.
- Helpful first.
- Never sound spammy.
- Never claim experience you do not have.
- Never pressure the user.
- Never use an em dash.
- Never use emojis.
- Reply naturally.
- Tailor the reply specifically to the post.
- Mention your services only if appropriate.

8. Return ONLY valid JSON.

Do not include markdown.

Do not explain your reasoning outside the JSON.
"""

def categorize(post):

    try:
        
        response = client.responses.create(
            model="gpt-4.1-mini",
            # model="gpt-4o-mini",
            temperature=0,
            input=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": f"Post: {post}"
                }
            ],
            text = {
                "format": {
                    "type": "json_schema",
                    "name": "client_acquisition",
                    "schema": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "analyses": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "additionalProperties": False,
                                    "properties": {

                                        "post_id": {
                                            "type": "string"
                                        },

                                        "service_category": {
                                            "type": "string",
                                            "enum": [
                                                "website",
                                                "shopify",
                                                "bot",
                                                "automation",
                                                "chatbot",
                                                "other"
                                            ]
                                        },

                                        "lead_score": {
                                            "type": "integer",
                                            "minimum": 0,
                                            "maximum": 100
                                        },

                                        "estimated_value": {
                                            "type": "integer",
                                            "minimum": 0
                                        },

                                        "is_good_lead": {
                                            "type": "boolean"
                                        },

                                        "buying_intent": {
                                            "type": "string",
                                            "enum": [
                                                "high",
                                                "medium",
                                                "low",
                                                "none"
                                            ]
                                        },

                                        "urgency": {
                                            "type": "string",
                                            "enum": [
                                                "high",
                                                "medium",
                                                "low",
                                                "none"
                                            ]
                                        },

                                        "competition": {
                                            "type": "string",
                                            "enum": [
                                                "high",
                                                "medium",
                                                "low",
                                                "unknown"
                                            ]
                                        },

                                        "recommended_action": {
                                            "type": "string",
                                            "enum": [
                                                "reply",
                                                "watch",
                                                "ignore"
                                            ]
                                        },

                                        "matched_keywords": {
                                            "type": "array",
                                            "items": {
                                                "type": "string"
                                            }
                                        },

                                        "review": {
                                            "type": "string"
                                        },

                                        "suggested_replies": {
                                            "type": "array",
                                            "maxItems": 2,
                                            "items": {
                                                "type": "string"
                                            }
                                        }

                                    },

                                    "required": [
                                        "post_id",
                                        "service_category",
                                        "lead_score",
                                        "estimated_value",
                                        "is_good_lead",
                                        "buying_intent",
                                        "urgency",
                                        "competition",
                                        "recommended_action",
                                        "matched_keywords",
                                        "review",
                                        "suggested_replies"
                                    ]
                                }
                            }
                        },

                        "required": [
                            "analyses"
                        ]
                    }
                }
            }
        )

        data = json.loads(response.output_text)
        # print(json.dumps(data, indent=4))
        return data

    except openai.APIConnectionError as e:
        # Network error - can't connect to OpenAI
        print(f"Network error: {e}")
        return {
            "error": "Network error: Could not connect to OpenAI. Please check your internet connection.",
            "error_type": "network"
        }
    
    except openai.RateLimitError as e:
        # Rate limit exceeded
        print(f"Rate limit error: {e}")
        return {
            "error": "Rate limit exceeded. Please wait a moment and try again.",
            "error_type": "rate_limit"
        }
    
    except openai.APIStatusError as e:
        # API returned an error status (4xx or 5xx)
        print(f"API status error: {e}")
        status_code = e.status_code
        if status_code == 401:
            return {
                "error": "Authentication error: Invalid API key. Please check your OpenAI API key in config.json.",
                "error_type": "auth"
            }
        elif status_code == 429:
            return {
                "error": "Quota exceeded: You have exceeded your OpenAI API quota. Please check your billing details.",
                "error_type": "quota"
            }
        elif status_code == 500:
            return {
                "error": "OpenAI server error. Please try again later.",
                "error_type": "server"
            }
        else:
            return {
                "error": f"OpenAI API error (HTTP {status_code}): {str(e)}",
                "error_type": "api_error"
            }
    
    except openai.APITimeoutError as e:
        # Request timed out
        print(f"Timeout error: {e}")
        return {
            "error": "Request timed out. Please try again.",
            "error_type": "timeout"
        }
    
    except Exception as e:
        # Any other unexpected error
        print(f"Unexpected error: {e}")
        return {
            "error": f"An unexpected error occurred: {str(e)}",
            "error_type": "general"
        }