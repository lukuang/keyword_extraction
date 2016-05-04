"""
example code from http://scikit-learn.org/stable/auto_examples/model_selection/grid_search_digits.html#example-model-selection-grid-search-digits-py
"""

from __future__ import print_function

from sklearn import datasets
from sklearn.cross_validation import train_test_split
from sklearn.cross_validation import StratifiedShuffleSplit
from sklearn.grid_search import GridSearchCV
from sklearn.metrics import classification_report
from sklearn.svm import SVC
import numpy as np
import sys
import json


print(__doc__)

# Loading the Digits dataset
digits = datasets.load_digits()

# To apply an classifier on this data, we need to flatten the image, to
# turn the data in a (samples, feature) matrix:
n_samples = len(digits.images)
if len(sys.argv)==3:
    X = json.load(open(sys.argv[1]))
    y = json.load(open(sys.argv[2]))
    train = []
    test = []
    sss = StratifiedShuffleSplit(y, 1, test_size=0.5, random_state=0)
    for tr, te in sss:
        train = tr
        test = te
    X_train = np.asarray([ X[j]   for j in train  ])
    X_test = np.asarray([ X[j]   for j in test ])
    y_train = np.asarray([y[i] for i in train])
    y_test = np.asarray([y[i] for i in test])
    pos_train = 0 
    pos_test = 0 
    for i in y_test:
        if i==1:
            pos_test += 1
    for i in y_train:
        if i==1:
            pos_train += 1
    print ("%d pos in train and %d pos in test" %(pos_train, pos_test))

else:
    X = digits.images.reshape((n_samples, -1))
    y = digits.target
    # Split the dataset in two equal parts
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.5, random_state=0)


# Set the parameters by cross-validation
tuned_parameters = [{'kernel': ['rbf'], 'gamma': [1e-3, 1e-4],
                     'C': [1, 10, 100, 1000]},
                    {'kernel': ['linear'], 'C': [1, 10, 100, 1000]}]

scores = ['f1']

for score in scores:
    print("# Tuning hyper-parameters for %s" % score)
    print()

    clf = GridSearchCV(SVC(C=1), tuned_parameters, cv=5,
                       scoring='%s_weighted' % score)
    clf.fit(X_train, y_train)

    print("Best parameters set found on development set:")
    print()
    print(clf.best_params_)
    print()
    print("Grid scores on development set:")
    print()
    for params, mean_score, scores in clf.grid_scores_:
        print("%0.3f (+/-%0.03f) for %r"
              % (mean_score, scores.std() * 2, params))
    print()

    print("Detailed classification report:")
    print()
    print("The model is trained on the full development set.")
    print("The scores are computed on the full evaluation set.")
    print()
    y_true, y_pred = y_test, clf.predict(X_test)
    print(classification_report(y_true, y_pred))
    print()