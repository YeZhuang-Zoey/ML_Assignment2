# -*- coding: utf-8 -*-
"""ML_Assignment2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1fZ5w-OI6wcDvbwVTYa0f1KGJtQTbRt1_

# Import package & Load the data
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, cross_val_score
import graphviz

from sklearn.metrics import confusion_matrix

from sklearn import tree
from sklearn.tree import DecisionTreeClassifier
from sklearn.tree import plot_tree

from sklearn import preprocessing

url = 'https://raw.githubusercontent.com/YeZhuang-Zoey/ML_Assignment2/main/Iris.csv'
Iris_data = pd.read_csv(url)

'''from sklearn.datasets import load_iris
iris = load_iris()
x = iris.data
y = iris.target'''

"""# Iris Data Information"""

Iris_data.head(10)

Iris_data.info()

Iris_data.describe()

Iris_data.Species.value_counts()

"""# Iris data Visulisation"""

sns.set_style('whitegrid')
sns.FacetGrid(Iris_data, hue = 'Species') \
   .map(plt.scatter, 'SepalLengthCm','SepalWidthCm') \
   .add_legend()

plt.show()

# Visualize the whole dataset
sns.pairplot(Iris_data, hue='Species')

"""#Generate Decision Tree"""

class TreeNode():
    def __init__(self, feature_index=None, threshold=None, left=None, right=None, info_gain=None, value=None):
        
        # for Decision Node
        self.feature_index = feature_index
        self.threshold = threshold
        self.left = left
        self.right = right
        self.info_gain = info_gain
        
        # for Leaf Node
        self.value = value

class DecisionTree():
    def __init__(self, min_samples_split=2, max_depth=2):
        
        self.root = None
        
        # stopping conditions
        self.min_samples_split = min_samples_split
        self.max_depth = max_depth
        
    def build_tree(self, dataset, curr_depth=0):
        
        X, Y = dataset[:,:-1], dataset[:,-1]
        num_samples, num_features = np.shape(X)
        
        # split until stopping conditions are met
        if num_samples >= self.min_samples_split and curr_depth <= self.max_depth:
            # find the best split
            best_split = self.get_best_split(dataset, num_samples, num_features)
            # check if IG is positive
            if best_split["info_gain"] > 0:
                # recur left
                left_subtree = self.build_tree(best_split["dataset_left"], curr_depth+1)
                # recur right
                right_subtree = self.build_tree(best_split["dataset_right"], curr_depth+1)
                # return Decision Node
                return TreeNode(best_split["feature_index"], best_split["threshold"], 
                            left_subtree, right_subtree, best_split["info_gain"])
        
        # compute Leaf Node
        leaf_value = self.calculate_leaf_value(Y)
        # return Leaf Node
        return TreeNode(value=leaf_value)

    #[Find_the_best_split]
    def get_best_split(self, dataset, num_samples, num_features):
        
        # dictionary to store the best split
        best_split = {}
        max_info_gain = -float("inf")
        
        # loop over all the features
        for feature_index in range(num_features):
            feature_values = dataset[:, feature_index]
            possible_thresholds = np.unique(feature_values)
            # loop over all the feature values present in the data
            for threshold in possible_thresholds:
                # get current split
                dataset_left, dataset_right = self.split(dataset, feature_index, threshold)
                # check if childs are not null
                if len(dataset_left)>0 and len(dataset_right)>0:
                    y, left_y, right_y = dataset[:, -1], dataset_left[:, -1], dataset_right[:, -1]
                    # compute information gain
                    curr_info_gain = self.compute_info_gain(y, left_y, right_y, "gini")
                    # update the best split if needed
                    if curr_info_gain>max_info_gain:
                        best_split["feature_index"] = feature_index
                        best_split["threshold"] = threshold
                        best_split["dataset_left"] = dataset_left
                        best_split["dataset_right"] = dataset_right
                        best_split["info_gain"] = curr_info_gain
                        max_info_gain = curr_info_gain
                        
        # return best split
        return best_split

    #[Split_data]
    def split(self, dataset, feature_index, threshold):
        
        dataset_left = np.array([row for row in dataset if row[feature_index]<=threshold])
        dataset_right = np.array([row for row in dataset if row[feature_index]>threshold])
        return dataset_left, dataset_right
    
    #[Compute_Info_Gain]
    def compute_info_gain(self, parent, l_child, r_child, mode = "entropy"):
        
        weight_l = len(l_child) / len(parent)
        weight_r = len(r_child) / len(parent)
        if mode=="gini":
            gain = self.gini_index(parent) - (weight_l * self.gini_index(l_child) + weight_r * self.gini_index(r_child))
        else:
            gain = self.entropy(parent) - (weight_l * self.entropy(l_child) + weight_r * self.entropy(r_child))
        return gain

    #[Compute_Entropy]
    def compute_entropy(self, y):

        label_column = y[:, -1]
        _, counts = np.unique(label_column, return_counts=True)

        probabilities = counts / counts.sum()
        entropy = sum(probabilities * -np.log2(probabilities))

        return entropy

        '''
        class_labels = np.unique(y)
        entropy = 0
        for cls in class_labels:
            p_cls = len(y[y == cls]) / len(y)
            entropy += -p_cls * np.log2(p_cls)
        return entropy
        '''
    
    #[Compute_Gini_Index]
    def gini_index(self, y):
        
        class_labels = np.unique(y)
        gini = 0
        for cls in class_labels:
            p_cls = len(y[y == cls]) / len(y)
            gini += p_cls ** 2
        return 1 - gini

    #[Compute_Leaf_Index]    
    def calculate_leaf_value(self, Y):
        
        Y = list(Y)
        return max(Y, key = Y.count)
    
    #[Print_Tree]
    def print_tree(self, tree=None, indent=" "):
        
        if not tree:
            tree = self.root

        if tree.value is not None:
            print(tree.value)
    
    #[Training]
    def fit(self, X, Y):
        
        dataset = np.concatenate((X, Y), axis=1)
        self.root = self.build_tree(dataset)
    
    #[Predict_dataset]
    def predict(self, X):
        
        preditions = [self.make_prediction(x, self.root) for x in X]
        return preditions
    
    #[Predict_data_point]
    def make_prediction(self, x, tree):
        
        if tree.value != None: return tree.value
        feature_val = x[tree.feature_index]
        if feature_val <= tree.threshold:
            return self.make_prediction(x, tree.left)
        else:
            return self.make_prediction(x, tree.right)

"""# Model Training"""

# Separate target variables
X = Iris_data[['SepalLengthCm', 'SepalWidthCm', 'PetalLengthCm', 'PetalWidthCm']]
y = Iris_data['Species']

# Split into Actual Train / Test Dataset
X_train, X_test, Y_train, Y_test = train_test_split(X, y, test_size = 0.4, random_state = 42)

# Spliting into Validation Train / Test
Xt, Xcv, Yt, Ycv = train_test_split(X_train, Y_train, test_size = 0.2, random_state = 42)

# Fitting data
decisionTree_clf = DecisionTreeClassifier(criterion='gini', min_samples_split=2)
decisionTree_clf.fit(Xt, Yt)

"""# Visualise Decision Tree"""

#Visualizing Decision Tree
tree.plot_tree(decisionTree_clf)

dot_data = tree.export_graphviz(decisionTree_clf, out_file=None)

graph = graphviz.Source(dot_data)
graph

"""# Entropy Calculation for each attribute"""

dataFrame = pd.DataFrame(Iris_data)
dataFrame.columns=['Id', 'SepalLengthCm', 'SepalWidthCm', 'PetalLengthCm', 'PetalWidthCm', 'Species']

result = dataFrame.copy()
columns=['SepalLengthCm', 'SepalWidthCm', 'PetalLengthCm', 'PetalWidthCm']

for i in range(4):
    max_value = dataFrame[columns[i]].max()
    min_value = dataFrame[columns[i]].min()
    result[columns[i]] = (dataFrame[columns[i]]-min_value)/(max_value-min_value)
    
print (result)

# Calculate Entropy for each attributes
for i in range(4):
    prob = dataFrame[columns[i]].value_counts(normalize = True)/50
    
    entropy = -1* np.sum(np.log2(prob)*prob)
    print("Entropy for ", columns[i]," is : ", entropy)

"""# Model Evaluation

Accuracy Score
"""

# Predict from the Test Dataset
Y_predict = decisionTree_clf.predict(X_test) 

# Calculate Accuracy
from sklearn.metrics import accuracy_score
print("Accuracy Score: ", accuracy_score(Y_test, Y_predict) * 100, '%')

# A detailed classification report
from sklearn.metrics import classification_report
print(classification_report(Y_test, Y_predict))

"""Confusion Matrix"""

sns.heatmap(confusion_matrix(Y_test, Y_predict),annot = True)