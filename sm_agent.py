import os
from datetime import datetime
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key = os.getenv("GOOGLE_API_KEY"))

def generate_post(topic, style,max_length=280):
    style_prompt = {
        "Casual":"Write in a friendly, conversational tone",
        "Funny":"Write in a humorous, entertaining tone",
        "Professional":"Write in a professional, business tone",
        "Informative":"Write in an educational, informative tone"
    }

    style_instruction = style_prompt.get(style,style_prompt['Casual'])

    prompt = f"""
Write a complete, polished, and finished social media post about "{topic}".

Requirements:
- {style_instruction}
- Stay strictly related to the topic: {topic}
- Maximum {max_length} characters
- Engaging and attention-grabbing
- Include 1-3 relevant hashtags related to {topic}
- The post MUST be complete (do not cut off mid-sentence)
- Do not write anything unrelated to {topic}

At the end, add 2-4 relevant and specific hashtags related to {topic}.
Do not exceed 4 hashtags.
Return only the final post text.
"""
    response = client.models.generate_content(
        model="gemini-2.5-flash",  
        contents=[
            {
                "role": "user",
                "parts": [
                    {
                        "text": (
                            "You are a creative social media content creator.\n\n"
                            + prompt
                        )
                    }
                ]
            }
        ],
        config={
            "temperature": 0.5,   # creativity
            "top_p":0.3,
            "max_output_tokens": 500
        }
    )

    return response.text.strip()


def review_post(post_text):
    prompt = f"""Review this social media post for potential issues:

"{post_text}"

Check for:
- Offensive content
- Misinformation claims
- Promotional spam
- Privacy violations

If there are concerns, list them. If the post is fine, respond with "APPROVED".
Be strict but fair."""
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",   # or gemini-1.5-pro
    contents=(
        "You are a content moderator focused on safety and ethics.\n\n"
        f"{prompt}"
    ),
    config={
        "temperature": 0.5,     # lower = more consistent
        "top_p":0.3,
        "max_output_tokens": 500
    }
    )

    result = response.text.strip()

    if "approved" in result.lower():
        return True, []
    else:
        return False, [result]
    

def save_approved_post(post_text, topic):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("approved_posts.txt","a",encoding="utf-8") as f:
        f.write(f"\n{'='*60}\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"Topic: {topic}\n")
        f.write(f"Post:\n{post_text}\n")


def get_style_choice():
    print("\nChoose a writing style:")
    print("1.Casual (friendly and conversational)")
    print("2.Professional (business-like)")
    print("3.Funny (humorous and entertaining)")
    print("4.Informative (educational)")

    while True:
        choice = input("\nEnter 1-4: ").strip()
        styles = {"1":"Casual","2":"Professional","3":"Funny","4":"Informative"}

        if choice in styles:
            return styles[choice]
        print("Invalid choice. Please enter between 1-4.")


def main():
    print("=" * 60)
    print("Social Media AI Agent with Approval")
    print("=" * 60)
    print()
    print("This AI helps you create social media posts.")
    print("You'll review and approve each post before saving.")
    print()

    while True:
        print("-"*60)
        topic = input("\nEnter a topic for your post(or 'quit' to exit): ").strip()

        if topic.lower() in ['quit','exit','q']:
            print("\nGoodbye")
            break
        if not topic:
            continue

        style = get_style_choice()
        print("\n Generating post...")
            
            # Generate the post
        try:
            post = generate_post(topic, style)
        except Exception as e:
            print(f"\nError generating post: {e}")
            continue

        print("\n" + "="*60)
        print("GENERATED POST:")
        print("="*60)
        print(post)
        print("="*60)
        print(f"\nCharacter count: {len(post)}")


        print("\n🔍 Running safety check...")
        is_safe, issues = review_post(post)
            
        if not is_safe:
            print("\nSAFETY CONCERNS DETECTED:")
            for issue in issues:
                print(f"  - {issue}")
            print("\nThis post may need revision.")
        else:
            print("Safety check passed")

        print("\n"+"-"*60)
        print("Do you approve this post?")
        print("1. Approve and save")
        print("2. Reject")
        print("3. Generate a new version")

        while True:
                decision = input("\nEnter 1-3:").strip()

                if decision == "1":
                    save_approved_post(post,topic)
                    print("Post approved and saved as approved_posts.txt")
                    return
                elif decision == "2":
                    print("Post rejected and discarded.")
                    return
                elif decision == "3":
                    print("\n🤖 Generating new version...")
                    
                    try:
                        post = generate_post(topic, style)
                    except Exception as e:
                        print(f"Error generating new version: {e}")
                        continue

                    print("\n" + "="*60)
                    print("NEW GENERATED POST:")
                    print("="*60)
                    print(post)
                    print("="*60)
                    print(f"\nCharacter count: {len(post)}")

                    print("\n🔍 Running safety check...")
                    is_safe, issues = review_post(post)

                    if not is_safe:
                        print("\nSAFETY CONCERNS DETECTED:")
                        for issue in issues:
                            print(f"  - {issue}")
                    else:
                        print("Safety check passed")

                else:
                    print("\n"+"-"*60)
                    print("Do you approve this post?")
                    print("1. Approve and save")
                    print("2. Reject")
                    print("3. Generate a new version")
                    print("Invalid choice. Please enter 1-3.")


if __name__ == "__main__":
    main()

