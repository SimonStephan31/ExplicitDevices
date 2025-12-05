import json
import pandas as pd
from openai import OpenAI

hal = OpenAI(api_key='XXX')
df = pd.read_excel("XXX.xlsx")
wieViel = df["machine_type"].count()
output_file = "XXX.txt"

model="gpt-5-nano"
parts = ["cutter", "balloon", "crossbow", "wheel"]
dinge = {
    ("cutter", "correct"): "knife",
    ("cutter", "incorrect"): "whisk",
    ("balloon", "correct"): "weight",
    ("balloon", "incorrect"): "kid",
    ("crossbow", "correct"): "star",
    ("crossbow", "incorrect"): "suction cup",
    ("wheel", "correct"): "mouse",
    ("wheel", "incorrect"): "reflector"
}


def llmRequest (object, andereKomponenten):
     return f"""You are an AI that extracts information from responses to a psychological survey.
                    From the text, identify:
                    1. Does the response bring up the dispositions of the {object}, explicitly mentioning how these dispositions allow it to interact with any of the following entities (which may have been referred to by a synonym too): {', '.join(andereKomponenten)}? (1 for yes, 0 for no);
                    2. List the expressions referring to the dispositions of the {object} that you based your decision on; the array may be empty if no dispositions are mentioned.
                    Return a JSON object with one number and one array containing strings:
                    {{
                        "mention": ...,
                        "expressions": [...]
                    }}"""


with open(output_file, mode="w", encoding="utf-8") as f:
    f.write("i | machine")
    for element in parts:
            f.write(" | " + element + "_correct")
            f.write(" | " + element + "_mention")
            f.write(" | " + element + "_expressions")
    f.write("\n")
    for i in range(wieViel):
        print("#########", i, "out of", wieViel, "#########")
        data = None
        worterbuch = {}
        machine_type = df["machine_type"].iloc[i]
        for k in range(len(parts)):
            element = parts[k]
            print(element + "\n")
            prompt = df["expl_" + element].iloc[i]
            correcto = df["sel_comp_" + element].iloc[i]
            object = dinge[(element, correcto)]
            andereKomponenten = ["rocket", "platform", "switch", "boot", "string", "rope"]
            for j in (parts[:k] + parts[k+1:]):
                andereKomponenten += [j, dinge[(j, "correct")], dinge[(j, "incorrect")]]
            print(andereKomponenten)
            print("\n")
            # Ruf das API an
            try:
                response = hal.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": llmRequest(object, andereKomponenten)
                        },
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"}
                )
                print(response.choices[0].message.content)
                data = json.loads(response.choices[0].message.content)
                worterbuch[element + "_correct"] = correcto
                worterbuch[element + "_mention"] = data.get("mention", "error")
                worterbuch[element + "_expressions"] = data.get("expressions", ["error"])

            except Exception as e:
                worterbuch[element + "_correct"] = "error"
                worterbuch[element + "_mention"] = "-1"
                worterbuch[element + "_expressions"] = ["error"]
            
        # Output         
        f.write(f"{i} | {machine_type}")        
        for element in parts:
            f.write(f" | {worterbuch[element + '_correct']}")
            f.write(f" | {worterbuch[element + '_mention']}")
            f.write(f" | {', '.join(worterbuch[element + '_expressions'])}")
            
        f.write("\n")
        print(i, "Erfolg")

print("Fertig!")



