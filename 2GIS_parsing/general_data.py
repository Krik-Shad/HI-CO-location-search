import static_parsing
import dynamic_parsing
import pandas as pd

df_static = pd.DataFrame(static_parsing.data[1:], columns=static_parsing.data[0])
df_dynamic = pd.DataFrame(dynamic_parsing.data[1:], columns=dynamic_parsing.data[0])

df_combined = pd.concat([df_static, df_dynamic], ignore_index=True)
data = [df_combined.columns.tolist()] + df_combined.values.tolist()

# print(data)