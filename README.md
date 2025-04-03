# 3D Point Cloud Analysis and Surface Modeling

This project is divided into two parts based on assignments from the 41118 Artificial Intelligence in Robotics course at UTS, focusing on the classification and surface reconstruction of 3D point cloud data.

## 📌 Part 1: Point Cloud Classification (MQ1)

**Goal:** To classify raw point cloud data into meaningful categories using machine learning.

### 🔧 Methods:
- **Clustering**: K-Means clustering on 3D coordinates and RGB values
- **Dimensionality Reduction**: PCA for each cluster
- **Classification**: Support Vector Machine (SVM) for supervised learning

### 🔍 Highlights:
- Achieved high AUC scores on unseen test data
- Robust performance through threshold tuning and cluster-based learning

📄 Report: [`41118_MQ1.pdf`](./41118_MQ1.pdf)

---

## 📌 Part 2: Surface Modeling with Regression (MQ2)

**Goal:** To reconstruct building walls and terrain surfaces from 3D point clouds.

### 🔧 Methods:
- **Linear Regression**: Applied per-cluster to planar wall regions
- **Gaussian Process Regression (GPR)**: Used for terrain modeling with uncertainty estimation
- **MLE Optimization**: Automatically tuned hyperparameters for GPR

### 📊 Features:
- Visualized surface fitting accuracy and uncertainty in 3D
- Demonstrated model trade-offs between accuracy and confidence

📄 Report: [`41118_MQ2.pdf`](./41118_MQ2.pdf)

---

## 🔗 Folder Structure

