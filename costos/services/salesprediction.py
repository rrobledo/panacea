import pandas as pd
from sklearn.datasets import load_diabetes

data = pd.read_csv("./../../ml/datalake/panacea_sales.csv", delimiter=",", header="infer")
data.head()
p = data.data.shape

diabetes = load_diabetes()
t = diabetes.target[:3]
s = diabetes.data.shape

pass