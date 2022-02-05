# %%
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
# %%

#seaborn theme for slides
sns.set_style("whitegrid")
sns.set_context("talk")

# set plot size
plt.rcParams["figure.figsize"] = (10, 6)


df = pd.read_csv("export.csv")
#replace na with "unknown"
df = df.fillna("other")
sns.countplot(data=df, x="offenses", order = df['offenses'].value_counts().index)
plt.xticks(rotation=90)

plt.ylabel("Case Count")
plt.xlabel("Offense Type")
# add padding below title

plt.title("Offense Type Distribution for the Sentencing Remark Dataset.", y=1.05, x=0.45)

# %%
