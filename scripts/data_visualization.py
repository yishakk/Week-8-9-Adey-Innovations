import matplotlib.pyplot as plt
import seaborn as sns

def plot_univariate(data, column, title=None):
    plt.figure(figsize=(10, 6))
    sns.histplot(data[column], kde=True, bins=30)
    plt.title(title or f"Univariate Analysis of [{column}")
    plt.xlabel(column)
    plt.ylabel("Frequency")
    plt.show()

def plot_univariate_pie(data, column, title=None):
    plt.figure(figsize=(10, 6))
    sns.barplot(data[column], kde=True, bins=30)
    plt.title(title or f"Univariate Analysis of [{column}")
    plt.xlabel(column)
    plt.ylabel("Frequency")
    plt.show()

def plot_bivariate(data, x_column, y_column, title=None):
    plt.figure(figsize=(8, 6))
    sns.scatterplot(x=data[x_column], y=data[y_column])
    plt.title(title or f"Bivariate Analysis: {x_column} vs {y_column}")
    plt.xlabel(x_column)
    plt.ylabel(y_column)
    plt.show()

def plot_visual(data, x_column, y_column, title=None, plt_kind=None, plt_color=None):
    plt.figure(figsize=(10, 6))
    data.plot(kind=plt_kind, color=plt_color)
    plt.title(title)
    plt.xlabel(x_column)
    plt.ylabel(y_column)
    plt.xticks(rotation=45)
    plt.show()