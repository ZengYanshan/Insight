import numpy as np
import pandas as pd
from io import StringIO
from insightCalculator import check_is_temporal, calc_point_insight, calc_outlier, calc_outlier_temporal, calc_shape_insight, calc_compound_insight, calc_distribution_insight

data = """
      Company                   Brand       Location  Sale
0    Nintendo      Nintendo 3DS (3DS)         Europe   760
1    Nintendo      Nintendo 3DS (3DS)          Japan  1030
2    Nintendo      Nintendo 3DS (3DS)  North America  1260
3    Nintendo      Nintendo 3DS (3DS)          Other     0
4    Nintendo        Nintendo DS (DS)         Europe     0
5    Nintendo        Nintendo DS (DS)          Japan     0
6    Nintendo        Nintendo DS (DS)  North America     0
7    Nintendo        Nintendo DS (DS)          Other     0
8    Nintendo    Nintendo Switch (NS)         Europe     0
9    Nintendo    Nintendo Switch (NS)          Japan     0
10   Nintendo    Nintendo Switch (NS)  North America     0
11   Nintendo    Nintendo Switch (NS)          Other     0
12   Nintendo               Wii (Wii)         Europe     0
13   Nintendo               Wii (Wii)          Japan     0
14   Nintendo               Wii (Wii)  North America     0
15   Nintendo               Wii (Wii)          Other     0
16   Nintendo            Wii U (WiiU)         Europe   140
17   Nintendo            Wii U (WiiU)          Japan    50
18   Nintendo            Wii U (WiiU)  North America    90
19   Nintendo            Wii U (WiiU)          Other     0
20       Sony     PlayStation 3 (PS3)         Europe    60
21       Sony     PlayStation 3 (PS3)          Japan    10
22       Sony     PlayStation 3 (PS3)  North America    40
23       Sony     PlayStation 3 (PS3)          Other    30
24       Sony     PlayStation 4 (PS4)         Europe  3330
25       Sony     PlayStation 4 (PS4)          Japan   900
"""

df = pd.read_csv(StringIO(data), delim_whitespace=True)
print(df)

ins_type = ''
ins_score = 0
ins_description = ""
if check_is_temporal(df):
    ins_type, ins_score, ins_description = calc_shape_insight(df)
    print("Insight Type:", ins_type)
    print("Insight Score:", ins_score)
    print("Description:", ins_description)
    print("-------------")
    ins_type, ins_score, ins_description = calc_outlier_temporal(df)
    print("Insight Type:", ins_type)
    print("Insight Score:", ins_score)
    print("Description:", ins_description)
    print("-------------")
else:
    ins_type, ins_score, ins_description = calc_point_insight(df, False)
    print("Insight Type:", ins_type)
    print("Insight Score:", ins_score)
    print("Description:", ins_description)
    print("-------------")
    ins_type, ins_score, ins_description = calc_outlier(df)
    print("Insight Type:", ins_type)
    print("Insight Score:", ins_score)
    print("Description:", ins_description)
    print("-------------")

    # remove all zeros when calculating distribution insight
    scope_data = df[df != 0]
    ins_type, ins_score, ins_description = calc_distribution_insight(scope_data)
    print("Insight Type:", ins_type)
    print("Insight Score:", ins_score)
    print("Description:", ins_description)
    print("-------------")




