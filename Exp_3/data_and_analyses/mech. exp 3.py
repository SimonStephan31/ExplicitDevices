import json
import pandas as pd
from openai import OpenAI

hal = OpenAI(api_key='XXX')
df = pd.read_excel("XXX.xlsx", header=0)
wieViel = df["scenario"].count()
output_file = "XXX.txt"
model="gpt-5-nano"

#list the other entities separately for target entitty.
worterbuch = {
    ("dragon", "A"): ["weight", "rope", "battleship", "ship",  "ship's bow", "stick", "boat", "button", "laundry machine", "dryer", "washing machine", "sail"], #what can this creature do?
    ("dragon", "B"): ["creature", "ninja", "ninja star", "flying disc", "shuriken", "dragon", "Draco", "Windragon", "button", "laundry machine", "dryer", "washing machine"], #What can this object do?
    ("dragon", "C"): ["creature", "ninja", "ninja star", "flying disc", "shuriken", "dragon", "Draco", "Windragon", "weight", "rope", "battleship", "ship",  "ship's bow", "stick", "boat", "laundry machine", "dryer", "washing machine", "sail"], #what can the button facing in this direction do?
    ("archer", "A"): ["balloon", "weight", "switch", "rope", "ball", "bowling ball", "ramp", "slope", "button", "light", "bulb", "lamp"], #what can this projectile do?
    ("archer", "B"): ["bow", "projectile", "arrow", "pointy arrow", "boxing arrow", "glove", "switch", "button", "light", "bulb", "lamp"], #What can this object do?
    ("archer", "C"): ["projectile", "arrow", "pointy arrow", "boxing arrow", "glove", "balloon", "weight", "switch", "rope", "ball", "bowling ball", "ramp", "slope", "button", "light", "bulb", "lamp"] #what can the bow aimed in this direction do?
}

Entitäten = {
    ("dragon", "A", "A"): "the ninja (creature)",
    ("dragon", "A", "B"): "the dragon (creature)",

    ("dragon", "B", "A"): "the weight on a rope (object)",
    ("dragon", "B", "B"): "the battle ship (object)",

    ("dragon", "C", "A"): "the button facing upwards (button)",
    ("dragon", "C", "B"): "the button facing leftward (button)",

    ("archer", "A", "A"): "the boxing arrow (projectile)",
    ("archer", "A", "B"): "the pointy arrow (projectile)",

    ("archer", "B", "A"): "the bowling ball (object)",
    ("archer", "B", "B"): "the balloon with weight (object)",

    ("archer", "C", "A"): "the bow aimed downward (direction)",
    ("archer", "C", "B"): "the bow aimed upward (direction)"
}

def llmExplicitJointCapacities (was, dinge):
     return f"""You are an AI that analyses responses to the question: what can {was} do? (with the synonym of the expression given in parentheses).
            Execute three steps:
            1. Create a (possibly empty) array of sub-arrays in the form [Activity, Entity]. Entity is an object, typically denoted by a noun.
            Activity denotes what {was} can do to Entity, what Entity can do to {was}, or what they can do together. 
            (Make sure that the Entity is not synonymous with {was}.)
            Activities indicate change, e.g., "push", "move", "blow", "match", "release". 
            In contrast, "has", "is", "contains", "part of", and "holds" are not activities. 
            Once you identify Activity and Entity, check that they are mentioned in the text and that Entity is not synonymous 
            with {was} (or with the parenthetical noun). Delete the sub-array if it fails this condition.
            Make sure that the sub-arrays are unique (i.e., no duplicates).
            2. Count these sub-arrays.
            3. Count how many of these sub-arrays contain an Entity synonymous with some item on the following list: {', '.join(dinge)}.

            Return a JSON object with three fields:
            {{
                "k": [[..., ...], [..., ...], ...],  # array of sub-arrays
                "n": ...,                            # total number of sub-arrays
                "m": ...                             # number of sub-arrays where the Entity belongs to {', '.join(dinge)}
            }}"""


with open(output_file, mode="w", encoding="utf-8") as f:
    f.write("i|exp|scenario|age|gender|zusammen|A|B|C|kA|nA|mA|kB|nB|mB|kC|nC|mC|\n")
    for i in range(wieViel):
        print("#########", i, "out of", wieViel, "#########")
        data = None        
        functional = df["experimentalbedingung"].iloc[i]
        scenario = df["scenario"].iloc[i]        
        age = df["age"].iloc[i]        
        gender = df["gender"].iloc[i]        
        ant_A = df["ant_A"].iloc[i]
        ant_B = df["ant_B"].iloc[i]
        ant_C = df["ant_C"].iloc[i]
        zusammen = ant_A + ant_B + ant_C
        A = df["erklarung_A"].iloc[i].replace("\n", " ").replace("\r", " ")
        B = df["erklarung_B"].iloc[i].replace("\n", " ").replace("\r", " ")
        C = df["erklarung_C"].iloc[i].replace("\n", " ").replace("\r", " ")
        print()
        f.write(f"{i}|{functional}|{scenario}|{age}|{gender}|{zusammen}|{A}|{B}|{C}|")
        # Ruf den API an
        for frage, ant, erklarung in [("A", ant_A, A), ("B", ant_B, B), ("C", ant_C, C)]:
            try:
                print(erklarung)
                response = hal.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": llmExplicitJointCapacities(Entitäten[scenario, frage, ant], worterbuch[scenario, frage])},
                        {"role": "user", "content": erklarung}
                    ],
                    response_format={"type": "json_object"}
                )
                print(response.choices[0].message.content)
                data = json.loads(response.choices[0].message.content)
                f.write(f"{str(data.get('k', 'error'))}|{str(data.get('n', 'error'))}|{str(data.get('m', 'error'))}|")
            except Exception as e:
                f.write("Error|Error|Error|")
                print(e)
        f.write("\n")
        print(i, "Erfolg")

print("Fertig!")


