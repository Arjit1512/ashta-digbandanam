from dotenv import load_dotenv
from groq import Groq
import os,json
from datetime import datetime
from zoneinfo import ZoneInfo

load_dotenv()


GROQ_API_KEY=os.getenv("GROQ_API_KEY")
GROQ_MODEL_NAME=os.getenv("GROQ_MODEL_NAME")


client = Groq(
    api_key=GROQ_API_KEY
)

prompt = """You are a professional Telugu YouTube script writer specializing in 
psychology and self-improvement content. Your channel mascot is 'Manas' - an anime-style 
male character with dark spiky hair, South Indian skin tone, purple glowing eyes, 
black jacket with purple accents, glowing purple brain energy around him.

{topics_selection}

TASK:
First, generate a UNIQUE, VIRAL, and PRACTICAL topic related to psychology/self-improvement.
The topic MUST be different every time and suitable for a 60-second YouTube Shorts.

Then write the full script based on that topic.

STRICT RULES:
- Tone: Positive, educational, empowering - NOT scary or manipulative  
- Language: Simple casual Telugu like how friends talk in Hyderabad
  (mix of Telugu + little English is FINE, like "stress అనేది మనల్ని destroy చేస్తుంది")
- Avoid pure/formal Telugu words - use everyday spoken Telugu
- Example of BAD Telugu: "స్వీయ దయను పెంపొందించుకోవడం"
- Example of GOOD Telugu: "మిమ్మల్ని మీరే love చేసుకోండి bro"
- Safe for YouTube monetization - no controversial content
- Teach viewers to PROTECT and IMPROVE themselves
- Reference real psychology concepts (Cognitive Behavioral Therapy, Stoicism, etc.)

Return ONLY a JSON response in this exact format, nothing else:
{{
  "topic": "topic in english",
  "topic_telugu": "topic in telugu",
  "hook": "first 5 seconds - attention grabbing line in Telugu",
  "body": [
    {{
      "point_number": 1,
      "title": "point title in Telugu",
      "script": "20-word explanation in Telugu",
      "psychology_concept": "real psychology term in english"
    }}
  ],
  "cta": "final 10 seconds call to action in Telugu",
  "hashtags": ["telugu", "psychology", "relevant tags"],
  "thumbnail_text": "short punchy text for thumbnail in Telugu (max 5 words)",
  "img_prompts": [
    "anime male character, dark spiky hair, South Indian skin tone, purple glowing eyes, black jacket with purple accents, glowing purple brain energy, [UNIQUE POSE/SCENE DESCRIPTION], white background, professional anime illustration, YouTube mascot",
    "anime male character, dark spiky hair, South Indian skin tone, purple glowing eyes, black jacket with purple accents, glowing purple brain energy, [UNIQUE POSE/SCENE DESCRIPTION], white background, professional anime illustration, YouTube mascot",
    "... 10 total items, each with a different pose or scene that matches the video script visually"
  ]
}}

IMPORTANT for img_prompts:
- Exactly 10 items in the array
- Each prompt must describe the SAME Manas character but in a DIFFERENT pose/expression/scene
- Each scene must visually relate to the script content at that moment
- Examples of poses: pointing at viewer, thinking pose, holding glowing brain, 
  reading book, arms crossed confidently, explaining with hand gestures, 
  meditating, writing on air, surprised expression, victorious pose
- Keep character description consistent in every prompt so all 10 images look like the same character
- White background always"""

def safe_parsed(content: str):
    content = content.strip()
    
    # Remove ```json or ``` fences if present
    if content.startswith("```"):
        lines = content.split("\n")
        # Remove first line (```json or ```) and last line (```)
        lines = lines[1:-1]
        content = "\n".join(lines)
    
    content = content.strip()
    
    # Find the first { and last } to extract pure JSON
    start = content.find("{")
    end = content.rfind("}") + 1
    
    if start == -1 or end == 0:
        raise ValueError("No valid JSON object found in response")
    
    content = content[start:end]
    
    return content

def get_used_topics() -> str:
    
    try:
        topics = []
        if os.path.exists("responses"):
            for filename in os.listdir("responses"):
                if filename.endswith(".json"):
                    with open(f"responses/{filename}" , "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if "topic" in data:
                            topics.append(data["topic"])

        print(f"TOPICS: {topics}\n")
        if topics == []:
            return "No topics used yet."

        return "ALREADY USED TOPICS (DO NOT REPEAT THESE):\n" + "\n".join(f"- {t}" for t in topics)


    except Exception as e:
        print(f"Error while fetching used topics due to {e}")
        exit()
    

def save_file(content: str):
    try:
        os.makedirs("responses",exist_ok=True)
        now = datetime.now(ZoneInfo("Asia/Kolkata")).strftime('%Y%m%d_%H%M%S')

        with open(f"responses/llm_response_{now}.json", "w", encoding="utf-8") as f:
            f.write(content)
        
        print("File saved successfully!")
        
    except Exception as e:
        print(f"Error while saving the file due to {e}")
        exit()

def call_llm():
    try:
        topics_selection = get_used_topics()
        messages = [
            {"role":"user","content":prompt.format(topics_selection=topics_selection)}
        ]
        res = client.chat.completions.create(
            model=GROQ_MODEL_NAME,
            messages=messages,
            max_tokens=3000
        )
        
        res_data=safe_parsed(res.choices[0].message.content)
        res_data=json.loads(res_data)
        
        script_data=json.dumps(res_data,ensure_ascii=False,indent=2)
        save_file(script_data)
        return script_data
    except Exception as e:
        print(f"Error due to {e}")
        exit()

if __name__=="__main__":
    # print(get_used_topics())
    result = call_llm()
    print(result)