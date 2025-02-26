from openai import OpenAI
import os

os.environ["http_proxy"] = "http://localhost:7890"
os.environ["https_proxy"] = "http://localhost:7890"

# 6.27
client = OpenAI(
    base_url='https://api.openai-proxy.org/v1',
    api_key='sk-6DaZUZ7TTJVTRheXy3mr0PZra6ZLq87PXXzjcsT2mAT7OO0I',
)

def generate_description_from_vega(vega_json):
#     prompt = f"""
#     You will receive the VegaLite visualization code of a data insight. Based on this VegaLite code, generate a brief description focusing on the key insight of the data. The description should highlight any significant trends, anomalies, or patterns, and provide a concise overview of the most notable findings without going into excessive detail.
#     Here is the VegaLite visualization code (truncated for brevity):
#
#     {vega_json}
#
#     Please generate a concise and focused description of the data insight based on this VegaLite code.
#     The description should be similar to:
#     "Block 1, Insight 1 (outlier): Microsoft Xbox 360 sales in North America are significantly higher compared to other regions, while Nintendo 3DS has higher sales in Europe. Sales in other regions are generally lower, especially in Japan.
# """
    prompt = f"""
    Please generate a concise text description based on the following Vega-Lite visualization code to describe the data insight.
    
    {vega_json}
"""
    try:
        response = client.chat.completions.create(

            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            max_tokens=150,
            temperature=0.7
        )
        # 返回模型的描述
        print(f"描述: {response.choices[0].message.content}")
        return response.choices[0].message.content
    except Exception as e:
        print("--------------------------------------------------------------")
        print(f"An ERROR occurred while generating the description: {e}")
        print(f"ERROR Vage_Lite：{vega_json}")
        print("--------------------------------------------------------------")
        return "Description generation ERROR."


# if __name__ == '__main__':
#     response = generate_description_from_vega("11")
#     print(response)