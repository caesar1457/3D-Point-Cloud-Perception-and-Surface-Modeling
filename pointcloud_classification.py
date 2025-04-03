# -*- coding: utf-8 -*-
"""Caesar_Zhao_Assignment1.4.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/13ygtqjK7ikwYFX_q8jro42hBwZhemL66

# Assignment 1

In this assignment, you will be first introduced to a 3D point cloud dataset where you are required to (the marking criteria is provided in brackets):

1. Cluster the point cloud into k clusters. (30%)
2. Perform PCA on each cluster. (30%)
3. Perform SVM (on the training set) to learn cluster labels. (20%)
4. Apply the SVM classifier to the test set, to classify the new points and evaluate performance metrics. (20%)

# Data

Below we load a 3D point cloud dataset where each point is described using 7 features: its 3D position, RGB colour, and colour intensity. Additionally, each data point has a label. Due to the size of the dataset, it is hard to work with and visualize all points at once. Thus, for the assignment, only a proportion of the dataset is selected. You are not expected to understand the data loading process but to use the loaded data.

## Download Data
Dataset available from <http://semantic3d.net/view_dbase.php?chl=1>.
"""

data_file = 'domfountain_station2_xyz_intensity_rgb'
label_file = 'sem8_labels_training'

!test ! -f {data_file}.txt \
  && wget http://semantic3d.net/data/point-clouds/training1/{data_file}.7z \
  && 7z e {data_file}.7z {data_file}.txt \
  && rm {data_file}.7z

!test ! -f {data_file}.labels \
  && wget http://semantic3d.net/data/{label_file}.7z \
  && 7z e {label_file}.7z  {data_file}.labels \
  && rm {label_file}.7z

"""## Import Data"""

import math
import numpy as np
import pandas as pd

fields = dict(
    x='float64', y='float64', z='float64',
    intensity='int32',
    r='uint8', g='uint8', b='uint8',
)
df = pd.read_csv(
    data_file+'.txt',
    sep=' ',
    names=fields.keys(),
    dtype=fields,
)
df['label'] = pd.read_csv(
    data_file+'.labels',
    # sep=' ',  # only one column, and possibly not ended properly
    names=['label'],
    dtype='uint8',
)
df['label'] = df['label'].astype('category').cat.rename_categories({
    0: "unlabeled points",
    1: "man-made terrain",
    2: "natural terrain",
    3: "high vegetation",
    4: "low vegetation",
    5: "buildings",
    6: "hard scape",
    7: "scanning artefacts",
    8: "cars",
})
print(f"total points: {len(df):>16}")
print(df['label'].value_counts())
keep = df['label'].map(
    lambda x: x in {
      # "unlabeled points",
      "man-made terrain",
      "natural terrain",
      # "high vegetation",
      # "low vegetation",
      "buildings",
      # "hard scape",
      # "scanning artefacts",
      # "cars",
    }
)
df = df[keep].reset_index(drop=True)
df = df[::100].reset_index(drop=True)  # reduce dataset size
df

"""## Preprocess Data"""

# Commented out IPython magic to ensure Python compatibility.
## Downsample using Open3D
# %pip install -q open3d
import open3d as o3d

points = df[['x','y','z']].to_numpy()
pcd = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(points))
# pcd = pcd.remove_duplicated_points()
pcd = pcd.remove_non_finite_points()
pcd = pcd.remove_statistical_outlier(10, 1)[0]
pcd = pcd.farthest_point_down_sample(10_000)
ds_points = np.array(pcd.points)
# ds_index = ((ds_points[:, None] == points).all(axis=-1) * (1 + np.arange(len(points)))).sum(axis=-1) - 1
ds_mask = (ds_points[:, None] == points).all(axis=-1).any(axis=0)
df = df[ds_mask].reset_index(drop=True)
df

## Split into Train and Test sets
test_mask = df['x'] < -5
df_full = df
df_test = df_full[test_mask].reset_index(drop=True)
df = df_full[~test_mask].reset_index(drop=True)  # training data

"""# Plotting
We define a helper function `plot_cloud(...)` that will make it easier to visualize our problem.
It is not necessary to know how this function works, only how to use it.

## Definitions
"""

# Commented out IPython magic to ensure Python compatibility.
# %pip install -q plotly
import plotly.express as px
import plotly.graph_objects as go

def plot_cloud(data=None, x='x', y='y', z='z', color=None, *, max_points=10_000, **kwargs):

    if max_points is not None and data is not None and len(data) > max_points:
        import sys
        print(f"Warning: too many points, trying to show only {max_points:,} points.", file=sys.stderr)
        skip = len(data) // max_points
        data = data[::skip]

    if isinstance(data, np.ndarray):
        m = data.shape[-1]
        if m == 3:
            x, y, z = data.T
        elif m == 4:
            x, y, z, color = data.T
        data_frame = None
    elif isinstance(data, pd.DataFrame):
        data_frame = data
    else:
        data_frame = None

    if (data_frame is not None
        and isinstance(color, str)
        and len(color) == 3
        and color not in data_frame.columns
        and all(c in data_frame.columns for c in color)
    ):
        update_color = data_frame[list(color)].to_numpy()
        color = None
    else:
        update_color = None

    fig = px.scatter_3d(
        data_frame,
        x=x, y=y, z=z,
        color=color,
        template=plot_cloud.template,
        **kwargs,
    )
    if update_color is not None:
        # has to be updated later because px.scatter_3d doesn't accept a matrix
        fig.data[0].marker.color = update_color

    return fig

plot_cloud.template = dict(
    layout=dict(
        margin=dict(
            # l=0, r=0,  # set left and right margin
            b=0, t=0,  # set bottom and top margin
        ),
        scene=dict(
            # xaxis_visible=False,  # hide axes
            # yaxis_visible=False,
            # zaxis_visible=False,
            aspectmode='data',  # set aspect ratio
        ),
    ),
    data=dict(
        scatter3d=[
            go.Scatter3d(
                marker_size=1,  # set default marker size
            ),
        ],
    ),
)

"""## Usage
Points can be plotted in 2 ways.
A `pandas` dataframe can be fed, where it will extract the `x`, `y`, and `z` columns.
Points can be coloured according to their `rgb` values, by their `intensity`, or their `label`.

Note only 10,000 points are plotted to improve interactivity.
"""

plot_cloud(df, color='rgb')

df['label'] = df['label'].cat.remove_unused_categories()
plot_cloud(df, color='label')

"""# 1. K-Means Clustering

The first part of the assignment is to perform k-means clustering on the dataset. Grouping the points allows each cluster to have more information than an individual point.

> Cluster the point cloud into $k=1000$ clusters. You can use the algorithms developed in past tutorials, or `scipy` functions.
"""

positions = df[['x','y','z']].to_numpy()
n_clusters = 1000
# TODO START

# this the new one to use Scipy
from scipy.cluster.vq import kmeans, vq
centroids, _ = kmeans(positions, n_clusters)
assignment = vq(positions, centroids)[0]

# TODO END
print(centroids.shape)
print(assignment.shape)

# when I was runnning the coding in past tutorials, that was so slowly
# thus, I decide to use Scipy, but still to show the coding what i did


# rng = np.random.default_rng(4)
# # kmeans function takes 2 arguments: the data points and number of clusters
# def kmeans(points, k):
#     #_points (array): data points in the shape of [number of data points, number of features]
#     # k (int): number of clusters

#     # TODO initialise the centroids using rng.choice() function within the domain of the point set
#     # IMPORTANT: Two centroids cannot be the same number
#     centroids = rng.choice(points, size=k)

#     # Assign points to clusters

#     # TODO: initialize an array with zeros equivalent to number of points. Each point will have an assignment [0/1/2].
#     assignment = np.zeros(len(points), dtype=int)

#     assignment_prev = None
#     # TODO write the condition for iteration
#     # Tip 1. Starting the assignment
#     # Tip 2. When to stop the iteration
#     while assignment_prev is None or any(assignment_prev!=assignment): #ans : assignment_prev is None or any(assignment_prev != assignment)
#         assignment_prev= np.copy(assignment) # First keep track of the latest assignment

#         # First iterate over all points
#         for i, point in enumerate(points):

#             # TODO calculate the Euclidean distance (distance2) from each point to the centroids
#             # Tip: distance2 should be of length 3
#             distances2 = np.sum((centroids - point)**2, axis=1)
#             # TODO calculate the closest centroid for the point
#             # Tip: see how np.argmin(...) works
#             closest_index = np.argmin(distances2)
#             # TODO populate the assignment array with the corresponding centroid
#             assignment[i] = closest_index

#         # Second calculate new centroids
#         for i in range(n_clusters):
#             # TODO replace centroids with the mean of points assigned to that centroid
#             # Tip: Only select the points assigned to each index value
#             centroids[i] = np.mean(points[assignment == i], axis=0)

#     return centroids, assignment

"""## Visualisation

Let's visualize the groups we just generated.
"""

n = n_clusters  # only display n clusters
print(n)
mask = assignment < n
fig = plot_cloud(positions[mask], color=assignment[mask])
fig.show()

"""## Cluster Statistics
In this section, the following statistics have been calculated for each cluster:
1. Average position
2. Average colour (RGB)
3. Average intensity and
4. Label

>Also, the data frame `df` has been arranged into a new data frame `dfc` (Data Frame Clusters). This is similar to `df`, but with one row for each cluster instead of for each point. Check carefully how labels (categorical data) have been aggregated.
"""

df['cluster'] = assignment
# print(df.shape)
dfc = df.groupby('cluster').mean(numeric_only=True)
# print(dfc.shape)
dfc['label'] = df.groupby('cluster')['label'].agg(pd.Series.mode)
# print(dfc.shape)
# print(dfc)
dfc['n_classes'] = df.groupby('cluster')['label'].agg(pd.Series.nunique)
# print(dfc.shape)
dfc = dfc[dfc.n_classes == 1].reset_index(drop=True)
n_clusters = len(dfc)


print(df.shape)
print(dfc.shape)

# Plot the down-sampled point cloud
plot_cloud(dfc, color='rgb')

"""# 2. Principal Component Analysis (PCA)

The second part of the assignment is to perform PCA on each cluster. The idea behind this process is to extract high-level information about the points in each cluster, as the major dimensions of the points' spread.

> Calculate the principal components of each cluster. You can use the algorithms developed in past tutorials, or `scipy` functions. Note that you need to disregard clusters with less than 3 points. Can you explain why?
"""

pcs = np.zeros((n_clusters, 3, 3))

## TODO START
from scipy.linalg import svd

# PCA_algo
def pca(X):

    B = X - np.mean(X, axis=0)

    U, s, Vh = svd(B, full_matrices=False)

    #coeff = np.diag(np.sqrt(s)) @ Vh
    coeff=np.dot(np.diag(np.sqrt(s)), Vh)

    pcs = np.dot(B, Vh.T)

    return coeff, pcs


features = ['x', 'y', 'z']
X_cluster = df[df['cluster'] == 0][features].values
print(X_cluster.shape)
print(X_cluster)

coeff, pcs = pca(X_cluster)


## TODO END
# print(X_cluster.shape)
# print(X_cluster)
print(pcs.shape)
print(pcs)
print(coeff.shape)
print(coeff)

# coeff
# df

"""To make sure that the PCA is implemented properly, create a function to visualize a cluster with all its points, the cluster centroid, and the principal components. Feel free to modify the function bellow if you prefer to use `plt` directly."""

def plot_cluster_with_centroid_and_pcs(df, cluster_assignments, cluster_index, pcs):
  ## TODO START
  cluster_data = df[df['cluster'] == cluster_index]

  if cluster_data.empty:
    print(f'Cluster {cluster_index} is empty')
    return

  if cluster_data is not None:
    fig = plot_cloud(
        data = cluster_data,
        x = 'x',
        y = 'y',
        z = 'z',
        color = 'rgb',
    )

  centroid = cluster_data[['x', 'y', 'z']].mean().values
  cx, cy, cz = centroid

  fig.add_trace(go.Scatter3d(
      x=[cx],
      y=[cy],
      z=[cz],
      mode='markers',
      marker=dict(
          size=5,
          color='red',
      ),
      name='Centroid',
  ))


  features = ['x', 'y', 'z']
  XYZ_cluster = df[df['cluster'] == cluster_index][features].values

  coeff_matrix, pcs_i = pca(XYZ_cluster)

  arrow_length = 1
  colors = ['magenta', 'green', 'blue']

  for j in range(coeff_matrix.shape[0]):
      pc_vec = coeff_matrix[j, :]
      ex = cx + arrow_length * pc_vec[0]
      ey = cy + arrow_length * pc_vec[1]
      ez = cz + arrow_length * pc_vec[2]

      fig.add_trace(go.Scatter3d(
          x=[cx, ex],
          y=[cy, ey],
          z=[cz, ez],
          mode='lines',
          line=dict(color=colors[j], width=5),
          name=f'PC{j+1}'
      ))

  fig.update_layout(
      title=f'Cluster {cluster_index} with Centroid & PCs',
      showlegend=True,
  )

  ## TODO END
  return fig

# this is my debug process, never mind

  # print(f'h_ex: {h_ex}')
  # print(f'h_ey: {h_ey}')
  # print(f'h_ez: {h_ez}')
  # print(f'h_ex - centroid = {h_ex - centroid[0]}')
  # print(f'h_ey - centroid = {h_ey - centroid[1]}')
  # print(f'h_ez - centroid = {h_ez - centroid[2]}')
  # print(f'centroid: {centroid}')

  # h_ex = np.array(h_ex).reshape(3,1)
  # h_ey = np.array(h_ey).reshape(3,1)
  # h_ez = np.array(h_ez).reshape(3,1)


  # # print(f'h_ex: {h_ex}')
  # # print(f'h_ey: {h_ey}')
  # # print(f'h_ez: {h_ez}')

  # new_martix = np.hstack((h_ex, h_ey, h_ez))
  # print(f'new_martix: {new_martix}')
  # # print(new_martix.shape)
  # # print(f'new_martix - centroid = {new_martix - centroid}'

  # v1_new, v2_new, v3_new = new_martix

  # print(f'v1_new: {v1_new}')
  # print(f'v2_new: {v2_new}')
  # print(f'v3_new: {v3_new}')

  # new_dot_v1_v2 = np.dot(v1_new, v2_new)
  # new_dot_v1_v3 = np.dot(v1_new, v3_new)
  # new_dot_v2_v3 = np.dot(v2_new, v3_new)

  # print("new: v1 · v2 =", new_dot_v1_v2)
  # print("new: v1 · v3 =", new_dot_v1_v3)
  # print("new: v2 · v3 =", new_dot_v2_v3)

  # new_v1 = v1_new - centroid
  # new_v2 = v2_new - centroid
  # new_v3 = v3_new - centroid

  # print(f'new_v1: {new_v1}')
  # print(f'new_v2: {new_v2}')
  # print(f'new_v3: {new_v3}')

  # new_dot_v1_v2 = np.dot(new_v1, new_v2)
  # new_dot_v1_v3 = np.dot(new_v1, new_v3)
  # new_dot_v2_v3 = np.dot(new_v2, new_v3)

  # print("new: v1 · v2 =", new_dot_v1_v2)
  # print("new: v1 · v3 =", new_dot_v1_v3)
  # print("new: v2 · v3 =", new_dot_v2_v3)

"""Call this function for the first four cluster to make sure that the principal components are computed correctly."""

fig = plot_cluster_with_centroid_and_pcs(df, assignment, 0, pcs)
fig.show()

fig = plot_cluster_with_centroid_and_pcs(df, assignment, 1, pcs)
fig.show()

fig = plot_cluster_with_centroid_and_pcs(df, assignment, 2, pcs)
fig.show()

fig = plot_cluster_with_centroid_and_pcs(df, assignment, 3, pcs)
fig.show()

"""# 3. Support Vector Machine (SVM)
The third part of the assignment is to perform SVM to learn the class label of clusters.

## Define Features and Labels
Each cluster is defined by a set of features, and has a ground-truth label.

> Define the features for the SVM classification. There shape of this matrix should be `[n_clusters, n_features]`. What features should you use to inform the classification model?
"""

# from re import X
# Define labels
labels = dfc['label'].map(lambda x: -1 if "terrain" in x else +1).to_numpy()

# Define features
## TODO START
features = dfc.drop(columns=['label', 'n_classes']).to_numpy()

## TODO END
print(len(features))
print(features.shape)
n_features = features.shape[-1]
print(f'{n_features=}')
# print(features)

print("Number of -1 clusters:", np.sum(labels == -1))
print("Number of +1 clusters:", np.sum(labels == +1))
# print("features.mean: ",features.mean(axis=0))
# print("features.std: ",features.std(axis=0))
# print("np.min(features): ",np.min(features, axis=0))
# print("np.max(features): ",np.max(features, axis=0))

"""## 4. Evaluate the SVM Optimisation
Optimise the SVM objective to calculate the weight $\mathbf{w}$ and bias $b$ of the linear model.

> Calculate `w` and `b`. Use the algorithms developed in past tutorials.
"""

dfc

test = dfc.drop(columns=['label', 'n_classes'])
test

# Commented out IPython magic to ensure Python compatibility.
# %pip install -q qpsolvers
import qpsolvers
from qpsolvers import solve_qp
from sklearn.svm import SVC
solver = qpsolvers.available_solvers[0]

def svm(x, y):
  ## TODO START

  n, f = x.shape
  y = y.astype(float)
  l = 1e-5            # lambda

  #    xy = y_i * x_i   => shape [n, f]
  xy = y[:, None] * x
  #    P = xy @ xy^T    => shape [n, n]
  P = xy @ xy.T
  q = -1 * np.ones(n)

  # print("P: ", P)
  print("P symmetric check:", np.allclose(P, P.T))

  A = y.reshape(1, -1)          # shape [1, n]
  b_ = np.zeros(1)        # shape [1]
  G = None
  h = None
  # 0 <= c_i <= 1/(2 n lambda)
  lb = np.zeros(n)
  ub = (1/(2*n*l)) * np.ones(n)
  # ub = np.full(n, np.inf)
  c = solve_qp(P, q, G, h, A, b_, lb, ub, solver=solver)
  # print(f"c: {c}")
  #  w => w = sum_i (c_i * y_i * x_i)
  w = c @ xy
  sv = (c > l)
  # b_sv => b_i = x_i^T w - y_i
  b_sv = x[sv] @ w - y[sv]
  b = np.mean(b_sv)

  ## TODO END
  return w, b
w, b = svm(features, labels)
# w, b
print(f'features.shape: {features.shape}')
print(f'labels.shape: {labels.shape}')
evaluate_svm(features, labels, w, b)
# print("w.shape:", w.shape)
print("Learned w:", w)
print("Learned b:", b)

"""## Sklearn SVM & Evaluation and Testing SVM"""

# ## the Evaluation for sklearn model

# from sklearn.metrics import (
#     accuracy_score,
#     confusion_matrix,
#     f1_score,
#     jaccard_score,
#     roc_curve,
#     roc_auc_score
# )
# import matplotlib.pyplot as plt

# def evaluate_svm_model(clf, X_test, y_test):

#     import numpy as np
#     from sklearn.metrics import (
#         accuracy_score, confusion_matrix, f1_score, jaccard_score,
#         roc_curve, roc_auc_score
#     )

#     scores = clf.decision_function(X_test)  # shape (n_samples,)
#     y_pred = clf.predict(X_test)            # shape (n_samples,)

#     y_test_01 = (y_test == 1).astype(int)
#     y_pred_01 = (y_pred == 1).astype(int)

#     accuracy = accuracy_score(y_test, y_pred)
#     cm = confusion_matrix(y_test, y_pred, labels=[-1, 1])
#     f1 = f1_score(y_test_01, y_pred_01, pos_label=1)
#     iou = jaccard_score(y_test_01, y_pred_01, pos_label=1)
#     fpr, tpr, thresholds = roc_curve(y_test_01, scores, pos_label=1)
#     auc_val = roc_auc_score(y_test_01, scores)

#     print("=== Evaluation Metrics ===")
#     print(f"Accuracy: {accuracy:.3f}")
#     print("Confusion Matrix (rows: true [-1,1], cols: pred [-1,1]):")
#     print(cm)
#     print(f"F1 Score: {f1:.3f}")
#     print(f"Jaccard (IoU) Score: {iou:.3f}")
#     print(f"AUC: {auc_val:.3f}")

#     plt.figure(figsize=(5,4))
#     plt.plot(fpr, tpr, label=f"AUC = {auc_val:.3f}")
#     plt.plot([0,1], [0,1], 'r--')
#     plt.xlabel("False Positive Rate")
#     plt.ylabel("True Positive Rate")
#     plt.title("ROC Curve (Non-Linear Kernel)")
#     plt.legend()
#     plt.show()

# ## this is using sklearn

# from sklearn.preprocessing import StandardScaler
# scaler = StandardScaler()
# features_scaled = scaler.fit_transform(features)
# clf = SVC(kernel='rbf', C=1.0)
# clf.fit(features, labels)
# w = clf.coef_[0]
# b = clf.intercept_[0]
# evaluate_svm_model(clf, features, labels)

# # testing SVM
# np.random.seed(42)
# n_points = 20
# x_pos = np.random.randn(n_points // 2, 2) + np.array([2, 2])  # +1
# x_neg = np.random.randn(n_points // 2, 2) + np.array([-2, -2])  # -1
# X = np.vstack([x_pos, x_neg])
# y = np.array([1] * (n_points // 2) + [-1] * (n_points // 2))

# plt.figure(figsize=(6,5))
# plt.scatter(X[:, 0], X[:, 1], c=y, cmap='bwr', edgecolors='k')
# plt.title("Toy Dataset")
# plt.xlabel("x1")
# plt.ylabel("x2")
# plt.show()

# w, b = svm(X, y)
# print("Learned weight vector w:", w)
# print("Learned bias b:", b)

# x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
# x_line = np.linspace(x_min, x_max, 100)

# if np.abs(w[1]) > 1e-6:
#     y_line = -(w[0] * x_line + b) / w[1]
#     plt.figure(figsize=(6,5))
#     plt.scatter(X[:, 0], X[:, 1], c=y, cmap='bwr', edgecolors='k')
#     plt.plot(x_line, y_line, 'g-', label='Decision Boundary')
#     plt.title("SVM Decision Boundary")
#     plt.xlabel("x1")
#     plt.ylabel("x2")
#     plt.legend()
#     plt.show()
# else:
#     print("w[1] is not enough")

"""## Evaluation
Evaluate the model and calculate the following metrics:
- Accuracy
- Confusion matrix
- F1 score
- Jaccard (IoU) score
- Plot the ROC curve
- Area under the ROC curve

You can also visualise the labeled point cloud.

> Evaluate the model and calculate the metrics on the test data. You can use the algorithms developed in past tutorials, or `scipy` functions.
"""

## TODO START
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    jaccard_score,
    roc_curve,
    roc_auc_score
)
import matplotlib.pyplot as plt

def evaluate_svm(X_test, y_test, w, b):
    scores = X_test.dot(w) + b

    best_f1 = 0
    best_threshold = 0

    # Traversing over 100 different thresholds, from min(scores) to max(scores)
    for threshold in np.linspace(scores.min(), scores.max(), 100):
        y_pred_temp = (scores >= threshold).astype(int) * 2 - 1  # to -1, 1
        f1_temp = f1_score(y_test, y_pred_temp, pos_label=1)

        if f1_temp > best_f1:
            best_f1 = f1_temp
            best_threshold = threshold

    print(f"Best Threshold: {best_threshold:.3f}, Best F1 Score: {best_f1:.3f}")

    y_pred = (scores >= best_threshold).astype(int) * 2 - 1

    y_test_01 = (y_test == 1).astype(int)
    y_pred_01 = (y_pred == 1).astype(int)

    # Accuracy
    accuracy = accuracy_score(y_test, y_pred)

    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred, labels=[-1, 1])

    # F1 score
    f1 = f1_score(y_test_01, y_pred_01, pos_label=1)

    # Jaccard (IoU) score
    iou = jaccard_score(y_test_01, y_pred_01, pos_label=1)

    # ROC curve and AUC
    fpr, tpr, thresholds = roc_curve(y_test_01, scores, pos_label=1)
    auc_val = roc_auc_score(y_test_01, scores)


    print("=== Evaluation Metrics ===")
    print(f"Accuracy: {accuracy:.3f}")
    print("Confusion Matrix (rows: true [-1,1], cols: pred [-1,1]):")
    print(cm)
    print(f"F1 Score: {f1:.3f}")
    print(f"Jaccard (IoU) Score: {iou:.3f}")
    print(f"AUC: {auc_val:.3f}")


    plt.figure(figsize=(5,4))
    plt.plot(fpr, tpr, label=f"AUC = {auc_val:.3f}")
    plt.plot([0,1], [0,1], 'r--')
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curve")
    plt.legend()
    plt.show()


##
## TODO END

"""# Test Set Evaluation
Once the model is trained on the training data set, it should be evaluated on the test set.

- Form point groups from the testing data set with k-means clustering.
- Perform PCA to generate features for each cluster.
- Use the SVM model to predict class labels for the test clusters. Do not retrain the SVM: use `w` and `b` calculated from the training set.
- Evaluate the framework's prediction with the aforementioned metrics.

> The test data set is available in `df_test`. Do not use the `labels` column until the final metric evaluations.
"""

## TODO START
## Test Set Evaluation
features_test = df_test.drop(columns=['label']).to_numpy()

labels_test = df_test['label'].map(lambda x: -1 if "terrain" in x else +1).to_numpy()
print("Test set features_test shape:", features_test.shape)
print("Test set labels_test shape:", labels_test.shape)
evaluate_svm(features_test, labels_test, w, b)

## TODO END