# 3D Point Cloud Perception and Surface Modeling

This repository provides a complete pipeline for semantic classification and accurate surface modeling of 3D point cloud data, developed for robotic perception and environmental understanding. The project was completed as part of the *41118 Artificial Intelligence in Robotics* coursework at the University of Technology Sydney (UTS).

---

## 🚩 Project Overview

The pipeline includes two major components:

### 📌 Part 1: Semantic Classification

- **Clustering**: K-Means clustering on spatial and RGB features
- **Feature Reduction**: Principal Component Analysis (PCA) per cluster
- **Classification**: Support Vector Machine (SVM) for supervised learning
- **Performance Metrics**: Confusion matrix, ROC curves, Area Under the Curve (AUC), F1 Score

<div align="center">
  <img src="classification/SVM_test.png" width="480">
  <p><em>SVM Classification Results (Test Set)</em></p>
</div>

### 📌 Part 2: Surface Modeling

- **Linear Regression**: Applied to segmented planar structures (e.g., walls)
- **Gaussian Process Regression (GPR)**: For terrain surface reconstruction and uncertainty quantification
- **Optimization**: Maximum Likelihood Estimation (MLE) of hyperparameters
- **Evaluation**: Mean Squared Error (MSE), Root Mean Squared Error (RMSE), residual analysis, and uncertainty calibration

<div align="center">
  <img src="modeling/Ground Truth + GP Prediction + Uncertainty (3-in-1).png" width="600">
  <p><em>Gaussian Process surface reconstruction with uncertainty</em></p>
</div>

---

## 📈 Quantitative Evaluation

| Model | Accuracy | F1 Score | AUC | MSE | RMSE | Mean Predicted Uncertainty |
|-------|----------|----------|-----|-----|------|----------------------------|
| **SVM (Test Set)** | 99.4% | 0.996 | 0.999 | – | – | – |
| **Gaussian Process Regression** | – | – | – | 0.1053 | 0.3245 | 0.1534 |

---

## 📂 Repository Structure

```
3D-Point-Cloud-Perception-and-Surface-Modeling/
├── pointcloud_classification.py             # Code: K-Means, PCA, SVM classification
├── surface_modeling_regression.py           # Code: Linear and GPR modeling
├── 41118_MQ1.pdf                            # Detailed report: Classification
├── 41118_MQ2.pdf                            # Detailed report: Surface modeling
├── figures/
│   ├── classification/                      # Images: ROC, PCA, K-Means clustering
│   └── modeling/                            # Images: Surface models, uncertainty analysis
└── README.md                                # Project overview and usage
```

---

## ⚙️ Installation & Usage

### Prerequisites

Ensure Python 3.8+ is installed. Required libraries:

```bash
pip install numpy pandas matplotlib scikit-learn
```

### Running the Code

1. **Classification**

```bash
python pointcloud_classification.py
```

2. **Surface Modeling**

```bash
python surface_modeling_regression.py
```

> **Note**: The original raw data was provided by UTS and is excluded from this repository.

---

## 🧑‍💻 Author

**Zhiye (Caesar) Zhao**  
MSc Robotics, University of Technology Sydney  
📧 [zhiye.zhao-1@student.uts.edu.au](mailto:zhiye.zhao-1@student.uts.edu.au)  
🌐 [Personal Portfolio](https://caesar1457.github.io/zhiyezhao/)

---

## 📜 License

This project is provided for academic and demonstration purposes only.  
© 2024 Caesar Zhao. All rights reserved.

