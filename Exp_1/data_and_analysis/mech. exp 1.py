import json
import pandas as pd
from openai import OpenAI

hal = OpenAI(api_key='XXX')
df = pd.read_excel("XXX.xlsx")
wieViel = df["machine_description"].count()
output_file = "XXX.txt"

with open(output_file, mode="w", encoding="utf-8") as f:
    f.write("nummer | machine_type | model | entities | activities | arrangements | expl_length | num_ent | num_act | num_arr\n")
    for i in range(wieViel):
        prompt = df["machine_description"].iloc[i]
        nummer = df["nummer"].iloc[i]
        machine_type = df["machine_type"].iloc[i]
        data = None

        for welcheModel in range(3):
            try:
                match welcheModel:
                    case 0:  model="gpt-3.5-turbo"
                    case 1:  model="gpt-4o-mini"
                    case 2:  model="gpt-5-nano"                    

                response = hal.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                """You are an AI that extracts information from human-generated text.
                                    From the text, identify and list:
                                    1. Entities (objects that are mentioned, such as a balloon, arrow, or mouse). Entities typically refer to material objects, animals, or humans. If two terms refer to the same object (as in “there is a mouse or some kind of rodent”), list only one (e.g., “mouse”). Grammatically, entities are typically indicated by nouns or noun phrases.
                                    2. Activities (such as shooting, activating, falling). Activities typically bring about some change or refer to movement. In contrast, being attached, hanging on, being connected, positioned, or pointing at are not activities. Grammatically, activities are typically indicated by verbs or verb phrases.
                                    3. Arrangements (such as being hung on the wall, pointed at, resting on). Arrangements signal the position of the object, especially relative to other objects. Grammatically, arrangements are typically indicated by prepositions,  prepositional phrases, or verb phrases.
                                    An expression can be classified at most as one of the three categories, but many expressions do not belong to any of the categories.
                                    Ignore references to the person ("I see") or the image itself.
                                    Return a JSON object:
                                    {
                                        "entities": [...],
                                        "activities": [...],
                                        "arrangements": [...]
                                    }
                                    The arrays may be empty."""
                            )
                        },
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"}
                )
                data = json.loads(response.choices[0].message.content)
                
            except Exception as e:
                data = None
                error_message = str(e)
            
            # Output for every attempt
            f.write(f"{nummer} | {machine_type} | {model} | ")
            if data is None:
                f.write("Failed parsing the text.\n")
                print(nummer, "exception")
            else:
                entities = data.get("entities", [])
                activities = data.get("activities", [])
                arrangements = data.get("arrangements", [])

                print(nummer, machine_type, entities, activities, arrangements)
                f.write(", ".join(entities) + " | ")
                f.write(", ".join(activities) + " | ")
                f.write(", ".join(arrangements) + " | ")
                f.write(f"{len(prompt.split())} | {len(entities)} | {len(activities)} | {len(arrangements)}\n")



print("Fertig!")





