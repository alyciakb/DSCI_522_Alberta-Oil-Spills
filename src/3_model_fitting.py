# # 3_model_fitting.py
# Huijue Chen, Nov. 22, 2018
#
# This script creates graphs and tables for analyzing the Alberta Oil Spills data.
# Input:
#      - Clean Data: "data/clean_data.csv"
#
# Output:
#      - Decision Tree Model: "results/finalized_model.sav"
#      - Mapping: "results/cause.csv" "results/source.csv" "results/location.csv" "results/substance.csv"
#      - Optimal hyperparameter: "results/depth_compare.png"
#      - Model Scores: "results/model_score.csv"
#      - Features Importance: "results/feature_compare.csv"
#
# Arguments:
#     ARG1 = input file path
#     ARG2 = output file path
#
# Usage:
#     “python src/3_model_fitting.py data/clean_data.csv  results/"

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import argparse
import pickle

from sklearn import tree
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import LabelEncoder

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', help='Data file path')
    parser.add_argument('output_path', help='Output file path')
    args = parser.parse_args()
    return args.input_file, args.output_path

def main():
    # Set up the random state
    state = 10

    # Get command line arguments
    input_file_path, output_file_path = get_args()

    # 1. Data Importing
    oil_spills = pd.read_csv(input_file_path).iloc[:, 1:]

    # 2. Categorical data mapping
    # 2.1 Record the mapping from categorical data to numerical values in dataframes, then export to CSV
    number = LabelEncoder()
    categories = ['cause','source','location','substance']
    for c in categories:
        number.fit(oil_spills[c])
        mapping = dict(zip(number.transform(number.classes_),number.classes_))
        mdf=pd.DataFrame.from_dict(mapping, orient='index',columns=[c])
        mdf.to_csv(output_file_path + c + ".csv")

    # 2.2  update correspondingly in the data frame
    oil_spills['cause']=number.fit_transform(oil_spills['cause'].astype('str'))
    oil_spills['source']=number.fit_transform(oil_spills['source'].astype('str'))
    oil_spills['location']=number.fit_transform(oil_spills['location'].astype('str'))
    oil_spills['substance']=number.fit_transform(oil_spills['substance'].astype('str'))

    # 3. Model Fitting
    # 3.1 Create X (i.e., features) and y (i.e., target)
    X = oil_spills.iloc[:,2:]
    y = oil_spills.iloc[:,1]

    # 3.2 Split the training data (X,y) into two sets: train set and test set
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=state)
    feature_cols=X.columns.values.tolist()

    # 3.3 find the optimal hyperparameter by comparing the scores from cross validation.
    depth_range = range(1,10)
    train_cv = []
    test_cv = []
    for d in depth_range:
        model = DecisionTreeClassifier(max_depth=d)
        train_cv.append(np.mean(cross_val_score(model, X_train, y_train, cv=10)))
    max_cv = max(train_cv)
    opt_d = train_cv.index(max_cv)+1

    # 3.4 plot for the hyperparameter vs. cv scores to visualize the best hyperparameter
    plt.plot(depth_range, train_cv)
    plt.xlabel("depth values")
    plt.ylabel("10-fold cross validation scores")
    plt.savefig(output_file_path+"depth_compare.png")
    plt.close()

    # 3.5 Set train model with the optimal max_depth
    model = DecisionTreeClassifier(max_depth=opt_d)
    model.fit(X_train,y_train)
    train_score = round(model.score(X_train, y_train),4)
    test_score= round(model.score(X_test, y_test),4)
    print("We choose the max_depth of", opt_d, ". The training accuracy is:", train_score,
    "\nThe testing accuracy is:", test_score)

    # 4 Exporting
    # 4.1 Export the model to file
    filename = output_file_path + 'finalized_model.sav'
    pickle.dump(model, open(filename, 'wb'))

    # 4.2 Find the most important features, export the features comparison to CSV
    fea_importance = model.tree_.compute_feature_importances(normalize=False)
    feature_df = pd.DataFrame([fea_importance], columns = feature_cols)
    feature_df.to_csv(output_file_path + "feature_compare.csv")

    #4.3 Export the training and test accuracy scores to CSV
    score_d = {"Type": ["Training Accuracy", "Test Accuracy"],
              "Score": [train_score, test_score]}
    score_df = pd.DataFrame(score_d)
    score_df.to_csv(output_file_path + "model_score.csv")

if __name__ == "__main__":
    main()
