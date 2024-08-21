import json
from connect_LLM_sample_test import get_related_subspace, get_response, parse_response_select_group, read_vis_list, \
    parse_response_select_insight
from asyncio import run

# get header list
def read_vis_list_vegalite(file_path):
    global header_list_vegalite
    header_list_vegalite = []

    with open(file_path, 'r') as file:
        lines = file.readlines()
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith("Header:"):
                header = eval(line.split(":")[1].strip())
                insights = []
                i += 1
                while i < len(lines) and not lines[i].startswith("Header:"):
                    if lines[i].startswith("Insight"):
                        insight_type = lines[i + 1].split(":")[1].strip()
                        insight_score = float(lines[i + 2].split(":")[1].strip())
                        insight_category = lines[i + 3].split(":")[1].strip()
                        insight_description = lines[i + 4].split(":")[1].strip()
                        data_str = lines[i + 5]
                        index = data_str.index('Vega-Lite Json: ')
                        insight_vegalite = data_str[index + len('Vega-Lite Json: '):]
                        insights.append(
                            {"Type": insight_type, "Score": insight_score, "Category": insight_category,
                             "Description": insight_description, "Vega-Lite": insight_vegalite})
                        i += 6
                    else:
                        i += 1
                header_list_vegalite.append({"Header": header, "Insights": insights})
            else:
                i += 1
    return header_list_vegalite


# insight list, fully info
def read_vis_list_into_insights(file_path):
    global insight_list
    insight_list = []

    with open(file_path, 'r') as file:
        lines = file.readlines()
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith("Header:"):
                header = eval(line.split(":")[1].strip())
                insights = []
                i += 1
                while i < len(lines) and not lines[i].startswith("Header:"):
                    if lines[i].startswith("Insight"):
                        insight_type = lines[i + 1].split(":")[1].strip()
                        insight_score = float(lines[i + 2].split(":")[1].strip())
                        insight_category = lines[i + 3].split(":")[1].strip()
                        insight_description = lines[i + 4].split(":")[1].strip()
                        data_str = lines[i + 5]
                        index = data_str.index('Vega-Lite Json: ')
                        insight_vegalite = data_str[index + len('Vega-Lite Json: '):]
                        insight_list.append({"Header": header, "Type": insight_type, "Score": insight_score,
                                             "Category": insight_category, "Description": insight_description,
                                             "Vega-Lite": insight_vegalite})
                        i += 6
                    else:
                        i += 1
            else:
                i += 1
    return insight_list


def get_insight_vega_by_header(header_str, insight_list):
    header = eval(header_str)
    # sort for matching
    header = tuple(sorted(map(str, header)))

    insights_info = []
    for index, item in enumerate(insight_list):
        if item['Header'] == header:
            insight_info = {
                'realId': index,
                'type': item['Type'],
                'category': item['Category'],
                'score': item['Score'],
                'description': item['Description'],
                'vegaLite': item['Vega-Lite']
            }
            insights_info.append(insight_info)
    return insights_info


def get_top_k_insights(k, insight_list):
    top_k = sorted(enumerate(insight_list), key=lambda x: x[1]['Score'], reverse=True)[:k]
    insights_info = []
    for index, (real_id, item) in enumerate(top_k):
        insight_info = {
            'realId': real_id,
            'type': item['Type'],
            'category': item['Category'],
            'score': item['Score'],
            'description': item['Description'],
            'vegaLite': item['Vega-Lite']
        }
        insights_info.append(insight_info)
    return insights_info


def get_vega_lite_spec_by_id(id, insight_list):
    # id: insight id (node real-id)
    print(id)
    item = insight_list[id]
    vl_spec = item['Vega-Lite']
    print(vl_spec)
    return vl_spec


def get_insight_by_id(insight_list, id):
    # id: insight id (node real-id)
    item = insight_list[id]
    return item


table_structure = {
    'Company': ['Nintendo', 'Sony', 'Microsoft'],
    'Brand': ['Nintendo 3DS (3DS)', 'Nintendo DS (DS)', 'Nintendo Switch (NS)', 'Wii (Wii)', 'Wii U (WiiU)',
              'PlayStation 3 (PS3)', 'PlayStation 4 (PS4)', 'PlayStation Vita (PSV)', 'Xbox 360 (X360)',
              'Xbox One (XOne)'],
    'Location': ['Europe', 'Japan', 'North America', 'Other'],
    'Season': ['DEC', 'JUN', 'MAR', 'SEP'],
    'Year': ['2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020']
}


def convert_header_to_data_scope(header):
    data_scope = {
        'Company': '*',
        'Brand': '*',
        'Location': '*',
        'Season': '*',
        'Year': '*'
    }

    for value in header:
        for key, values_list in table_structure.items():
            if value in values_list:
                data_scope[key] = value
                break

    return data_scope


def convert_data_scope_to_header(data_scope):
    data_dict = json.loads(data_scope)
    header = []
    for key in ['Company', 'Brand', 'Location', 'Season', 'Year']:
        value = data_dict.get(key, '*')
        if value != '*':
            header.append(value)
    return tuple(header)


question2_prompt = """
Next, I will provide you with some other subspaces related to the current subspace in terms of header structure. 
"""


async def qa_LLM(query, item, insight_list, node_id):
    print("=====qa_LLM=====")
    question2 = combine_question2(query, item)

    question3, categorized_headers = combine_question3(query, item)
    # let LLM select one group that best matches the question and crt subspace
    response = get_response(question2 + question3)
    print(f"1. Response choose group: \n{response}\n\n")

    insights_info_dict, sort_insight_prompt = parse_response_select_group(response, query, insight_list)

    # let LLM sort insights
    response = get_response(sort_insight_prompt)
    print(f"2. Response sort insights: \n{response}\n\n")

    next_nodes, node_id = parse_response_select_insight(response, insights_info_dict, categorized_headers, node_id)

    print(f"next_nodes: {next_nodes}\n")
    print("=" * 100)

    return next_nodes, node_id

# async def summarize_LLM(tree):
def summarize_LLM(tree):
    print("=====summarize_LLM=====")
    prompt1 = """
You are given a data structure called an "insight tree," which consists of nodes and edges. Each node represents a data insight with specific characteristics, and each edge describes the relationship between these insights. Your task is to generate a summary report that reflects the user's exploration journey through this insight tree.
Here is the insight tree:
Nodes:
- Each node has an `id`, a `type` that indicates the kind of insight (such as trend, outliers), a `description` that explains the data pattern of insight, and a `query` which represents the user's question or the data aspect that led to this insight.
Edges:
- Each edge has a `source` and a `target`, representing the starting and ending nodes of a relationship. It also includes a `query`, which reflects the question or aspect that connects these insights, a `relationship` that describes how the source insight leads to the target insight by semantically logical reasoning, and a `relType` indicating the structural type of relationship (same-level, generalization or specification).
Please analyze the provided insight tree and generate a coherent and logical report that outlines the user's exploration process, highlights significant insights discovered, and describes how the insights are interconnected. The report should also capture the logical reasoning behind the transitions from one insight to another.
Below is the JSON structure representing the insight tree:
    """

    tree_info = str(tree)

    prompt2 = """
The purpose of this summary report is to help the user automatically summarize their exploration process and findings, effectively creating a data story. The report should seamlessly connect the insights (nodes) and relationships (edges) from the insight tree.
In the report, the 'query' represents the user's question or the aspect they want to explore further for a particular insight. The 'relationship' reflects the logical reasoning that led from a parent node to a child node as the next step in the exploration. The 'relType' indicates the structural relationship between two nodes, such as specification (a deeper exploration of a specific aspect), generalization (expanding to a broader context), or same-level (exploring another perspective within the same scope).
The summary report should carefully weave together all the nodes and edges, including the user's queries and thoughts, into cohesive paragraphs. . This insight tree may represent the user's analysis of a specific problem from several perspectives (as subtrees). You should emphasize reasoning about the user's thought process and understand what kind of data story this insight tree expresses.
When writing this report, use a data storytelling narrative style. Begin with an introduction to the user's initial area of interest, then develop the exploration by narrating how each insight was derived, and conclude by highlighting the overall insights discovered. For example, "The user was initially interested in X, and they sought to explore the reasons behind X by investigating Y..."
Ensure that the report is structured into well-formed paragraphs, avoiding lists or bullet points. Do not refer to the insights by their IDs in the report. Instead, use descriptive language to convey the insights and their relationships.
"""
    question = prompt1 + tree_info + prompt2

    # let LLM generate summary
    response = get_response(question)
    print(f"LLM Response Report Summary: \n{response}\n\n")

    # let LLM label the report
    prompt_label = """
You have generated a summary report that outlines a user's exploration journey through an insight tree, containing various insights and relationships. Now, the task is to enhance this report for interactive highlighting by embedding it with <span> tags. These tags will associate specific sentences or phrases in the report with corresponding nodes or edges in the insight tree. This allows the frontend to implement a feature where hovering over a report sentence highlights the associated elements in the insight tree.
To achieve this, follow these guidelines:
1. Identify Insight Nodes: For each sentence that describes or references a specific insight from the tree, wrap the entire sentence with a `<span>` tag and assign it a class using the format `<span class="insight-node-<id>">...</span>`, where `<id>` corresponds to the ID of the node in the insight tree.
2. Highlight Relationships: For sentences that describe transitions or relationships between insights, wrap the entire sentence with a `<span>` tag using the format `<span class="insight-edge-<source>-<target>">...</span>`, where `<source>` and `<target>` are the IDs of the source and target nodes, respectively, in the insight tree.
3. Maintain Readability: Ensure that the addition of `<span>` tags does not disrupt the readability of the report. 
4. Selective Tagging: Not every sentence needs to be tagged. Only tag sentences that clearly correspond to a node or relationship in the insight tree.
5. Consistent Tagging: Ensure all insights and relationships mentioned in the report are tagged appropriately and consistently, providing comprehensive coverage for all nodes and edges in the insight tree.
Here’s an example of how the report text should be annotated:
- Before: "The user observed a significant drop in Sony's sales, leading to further analysis."
- After: "<span class="insight-node-70">The user observed a significant drop in Sony's sales.</span> <span class="insight-edge-70-71">This led to further analysis into the subsequent factors.</span>"
Below is the report. Please annotate it according to the above guidelines and return the annotated report directly without any additional comments or text.
"""

    question2 = prompt_label + response
    final_report = get_response(question2)

    print(f"After labeling(The final report):\n {final_report}\n")
    print("=" * 100)

    return final_report


def combine_question2(query, item):
    crt_header = str(item['Header'])

    question2 = "Question: " + query + "\n"
    question2 += "Current Subspace: " + str(crt_header) + "\n"
    question2 += "Insight: \n"

    question2 += "Type: " + item['Type'] + "\n"
    question2 += "Score: " + str(item['Score']) + "\n"
    question2 += "Description: " + item['Description'] + "\n"
    question2 += question2_prompt

    return question2


def combine_question3(query, item):
    crt_header = str(item['Header'])

    # question contains only the related headers not insight-info
    question3 = """You already know the current data subspace and a problem that needs to be solved, and next we need to constantly \
change the data subspace to analyze the data. I will provide you with a "Related Subspaces List," \
which lists other subspaces related to the current subspace.
These subspaces are categorized into three types based on their hierarchical relationship with the current subspace: \
same-level, elaboration, and generalization. Please select a group that is most likely to solve my current problem \
as the next direction for exploration."""
    question3 += "Related Subspaces List:\n"
    grouping_string, categorized_headers = get_related_subspace(crt_header)
    question3 += grouping_string

    repeat_str = """Please note that my current subspace is: {} , and the question need to be solved is: "{}". \
Considering the subspace groups mentioned above, select one group that best matches the question."""
    repeat_str = repeat_str.format(str(crt_header), query)
    question3 += repeat_str

    response_format = """Your answer should follow the format below:
Group type: {}
Group Criteria: {}
Among them, Group type is used to identify the three categories of Same-level group, Elaboration group, and Generalization group, and Group Criteria is used to determine specific groups within the category.
For example:
Group type: Same-level groups
Group Criteria: Brand
Please answer strictly according to the format and do not add additional markings such as bold, punctuation marks, etc.
"""
    question3 += response_format
    return question3, categorized_headers


# test

# insight_list = read_vis_list_into_insights('vis_list_VegaLite.txt')
#
# insight_id = 198
# query = "I want to know more about the sales in Japan of JUN."
# # query = "I want to know why the sale of the brand PlayStation 4 (PS4) is an outlier, what caused the unusually large value of this point?"
# #
# node_id = 0
# item = insight_list[insight_id]
# next_nodes = run(qa_LLM(query, item, insight_list, node_id))

# tree = """
# {
#     "nodes": [
#         {
#             "id": 1325,
#             "type": "dominance",
#             "description": "In Data scope (Sony,), The Sale of PlayStation 4 (PS4) dominates among all Brands.",
#             "query": "Why are PS4 sales so high? Do other companies also have dominated brands?"
#         },
#         {
#             "id": 2078,
#             "type": "outlier-temporal",
#             "description": "In Data scope (Microsoft, ), The Sale of Year 2014 is an outlier, which is significantly higher than the normal Sale of other Years.",
#             "query": "The sales of Microsoft are declining year by year. What is the reason? I noticed that unlike Sony and Nintendo, Microsoft does not have a dominant brand. Is this related to Microsoft's declining sales?"
#         },
#         {
#             "id": 2081,
#             "type": "dominance",
#             "description": "In Data scope (Microsoft, ), The Sale of North America dominates among all Locations.",
#             "query": "Q: The sales of Microsoft are declining year by year. What is the reason? Is it related to its competitors Sony and Nintendo?"
#         },
#         {
#             "id": 14,
#             "type": "top2",
#             "description": "In Data scope (Nintendo, ), The Sale proportion of Nintendo Switch (NS) and Nintendo 3DS (3DS) is significantly higher than that of other Brands.",
#             "query": NULL
#         },
#         {
#             "id": 2406,
#             "type": "dominance",
#             "description": "In Data scope (Microsoft, Xbox One(XOne)), The Sale of North America dominates among all Locations.",
#             "query": NULL
#         },
#         {
#             "id": 2088,
#             "type": "trend",
#             "description": "In Data scope (Microsoft, X360), Sales exhibit a clear downward trend over the Years from 2013 to 2020.",
#             "query": NULL
#         },
#         {
#             "id": 1322,
#             "type": "compound",
#             "description": "In Data scope (Sony,), The sale of Europe,Japan,North America,Other, are correlated. From MAR to SEP, values decreased fast, with a Minimum value in SEP. From SEP to DEC, values increased slowly.",
#             "query": NULL
#         },
#         {
#             "id": 2098,
#             "type": "trend",
#             "description": "In Data scope (Microsoft, Europe), Sales exhibit a clear downward trend over the Years from 2013 to 2020.",
#             "query": NULL
#         },
#         {
#             "id": 2095,
#             "type": "compound",
#             "description": "In Data scope (Microsoft, Europe), The sale of 2016,2017,2018, are correlated. From MAR to JUN, values decreased fast, with a Minimum value in JUN. From JUN to DEC, values increased slowly.",
#             "query": NULL
#         },
#         {
#             "id": 2096,
#             "type": "outlier-temporal",
#             "description": "In Data scope (Microsoft, Europe), The Sale of Year 2020 is an outlier, which is significantly lower than the normal Sale of other Years.",
#             "query": NULL
#         }
#     ],
#     "edges": [
#         {
#             "source": 1325,
#             "target": 2078,
#             "query": "Why are PS4 sales so high? Do other companies also have dominated brands?",
#             "relationship": "Insight 11 identifies that the sale of the year 2014 is an outlier for Microsoft, significantly higher than other years. This is important for understanding anomalies in sales data, which can be compared to any anomalies in Nintendo's sales data. By identifying outliers, we can investigate the reasons behind these anomalies, which might include market conditions, product launches, or other factors. This insight helps us understand the temporal distribution of sales and identify any unusual patterns that could explain high sales figures.",
#             "relType": "same-level"
#         },
#         {
#             "source": 1325,
#             "target": 2081,
#             "query": "Why are PS4 sales so high? Do other companies also have dominated brands?",
#             "relationship": "Insight 14 shows that the sale of North America dominates among all locations for Microsoft. This is relevant to the problem question as it provides a comparison point for regional dominance. By knowing that North America is a key market for Microsoft, we can compare this with Nintendo's regional sales to see if there are similar patterns of dominance. This insight helps us understand the geographical distribution of sales, which is crucial for comparing the performance of different companies.",
#             "relType": "same-level"
#         },
#         {
#             "source": 1325,
#             "target": 14,
#             "query": "Why are PS4 sales so high? Do other companies also have dominated brands?",
#             "relationship": "Insight 14 shows that the sale of North America dominates among all locations for Microsoft. This is relevant to the problem question as it provides a comparison point for regional dominance. By knowing that North America is a key market for Microsoft, we can compare this with Nintendo's regional sales to see if there are similar patterns of dominance. This insight helps us understand the geographical distribution of sales, which is crucial for comparing the performance of different companies.",
#             "relType": "same-level"
#         },
#         {
#             "source": 2078,
#             "target": 2406,
#             "query": "The sales of Microsoft are declining year by year. What is the reason? I noticed that unlike Sony and Nintendo, Microsoft does not have a dominant brand. Is this related to Microsoft's declining sales?",
#             "relationship": "Insight 10 shows that the sale of North America dominates among all locations for the Xbox One. This is relevant because it provides a geographical context to the sales data. Understanding that North America is the dominant market can lead to further investigation into market-specific factors that might be contributing to the decline in sales. For example, changes in consumer preferences, competition, or economic conditions in North America could be significant factors affecting Microsoft's overall sales performance.",
#             "relType": "specification"
#         },
#         {
#             "source": 2078,
#             "target": 2088,
#             "query": "The sales of Microsoft are declining year by year. What is the reason? I noticed that unlike Sony and Nintendo, Microsoft does not have a dominant brand. Is this related to Microsoft's declining sales?",
#             "relationship": "Insight 6 reveals a clear downward trend in sales from 2013 to 2020 for the Xbox 360. This is directly relevant to the problem of declining sales for Microsoft, as it provides a temporal context and shows that the decline is not just a short-term anomaly but a long-term trend. This insight helps us understand the broader pattern of declining sales over the years, which is crucial for addressing the question of why Microsoft's sales are declining.",
#             "relType": "specification"
#         },
#         {
#             "source": 2081,
#             "target": 1322,
#             "query": "The sales of Microsoft are declining year by year. What is the reason? Is it related to its competitors Sony and Nintendo?",
#             "relationship": "Insight 7 is selected because it mirrors Insight 1 but for Sony instead of Nintendo. This comparison is crucial for understanding the competitive landscape and how both companies' sales trends are correlated across different regions. By examining the same pattern in Sony's sales, we can infer whether the decline in Microsoft's sales might be influenced by similar market dynamics affecting both Nintendo and Sony.",
#             "relType": "same-level"
#         },
#         {
#             "source": 2081,
#             "target": 2098,
#             "query": "I want to explore the reasons for Microsoft's sales in location aspect.
# ",
#             "relationship": "Insight 1 shows a specific pattern for the years 2013 and 2020, but Insight 5 provides a broader context by indicating a clear downward trend in sales from 2013 to 2020. This helps in understanding the long-term trend and how the specific patterns observed in Insight 1 fit into the overall decline. This is important for problem relevance as it addresses the overarching question of why Microsoft's sales are changing over time in Europe.",
#             "relType": "specification"
#         },
#         {
#             "source": 2081,
#             "target": 2095,
#             "query": "I want to explore the reasons for Microsoft's sales in location aspect.
# ",
#             "relationship": "Insight 1 focuses on the years 2013 and 2020, while Insight 2 provides information on the sales patterns for 2016, 2017, and 2018, which are also correlated but show a different trend (decreasing fast from MAR to JUN and then increasing slowly). This comparison is valuable for data association, as it allows us to contrast different periods and understand how sales dynamics have shifted over different years, contributing to a comprehensive analysis of sales trends in Europe.",
#             "relType": "specification"
#         },
#         {
#             "source": 2081,
#             "target": 2096,
#             "query": "I want to explore the reasons for Microsoft's sales in location aspect.
# ",
#             "relationship": "Insight 1 indicates a pattern in sales for the years 2013 and 2020, with a peak in June and a subsequent decline. Insight 3 highlights that the sale of the year 2020 is an outlier, significantly lower than other years. This is a logical next step because understanding the outlier nature of 2020 can provide deeper insights into why the sales pattern deviated so drastically, which is crucial for identifying anomalies and their impact on overall sales trends.",
#             "relType": "specification"
#         }
#     ]
# }
# """
# summarize_LLM(tree)