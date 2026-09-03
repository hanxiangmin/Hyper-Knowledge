# Machine Learning

**Disciplinary Classification**: Artificial Intelligence
**Creation Date**: February 22, 2026
**Last Updated**: February 22, 2026

---

## Overview

**Machine Learning (ML)** is an important branch of **Artificial Intelligence (AI)** dedicated to researching how computer systems can automatically improve through experience.

The core idea of machine learning is: not relying on explicit hard-coded rules, but learning patterns and rules from data through algorithms.

---

## Definition

Machine learning is a multidisciplinary field involving **probability theory**, **statistics**, **approximation theory**, **convex analysis**, **computational complexity theory**, and other disciplines.

It is the core of artificial intelligence and the fundamental approach to giving computers intelligence. Machine learning algorithms analyze large amounts of data, automatically discover patterns, and use these patterns to make predictions or decisions on unknown data.

---

## Classification System

### 1. Supervised Learning

Supervised learning uses **labeled training data** for learning. Algorithms learn mapping relationships from input features and corresponding output labels.

**Common Algorithms**:
- Linear Regression
- Logistic Regression
- Decision Tree
- Random Forest
- Support Vector Machine (SVM)
- Neural Networks

**Application Scenarios**:
- House price prediction
- Spam email classification
- Image recognition
- Medical diagnosis

### 2. Unsupervised Learning

Unsupervised learning uses **unlabeled data**, where algorithms need to discover structures and patterns in the data on their own.

**Common Algorithms**:
- Clustering: K-Means, Hierarchical Clustering, DBSCAN
- Dimensionality Reduction: PCA, t-SNE, Autoencoders
- Association Rule Mining: Apriori, FP-Growth

**Application Scenarios**:
- Customer segmentation
- Anomaly detection
- Recommendation systems
- Topic modeling

### 3. Reinforcement Learning (RL)

Reinforcement learning learns through **interaction between an Agent and an Environment**. The agent obtains rewards through trial and error, with the goal of maximizing long-term cumulative rewards.

**Core Concepts**:
- State
- Action
- Policy
- Reward
- Value Function

**Common Algorithms**:
- Q-Learning
- Policy Gradient
- Actor-Critic
- DQN (Deep Q-Network)
- PPO (Proximal Policy Optimization)

**Application Scenarios**:
- Game AI (such as AlphaGo)
- Robot control
- Autonomous driving
- Resource scheduling

### 4. Semi-Supervised Learning

Combines small amounts of labeled data with large amounts of unlabeled data for learning.

### 5. Self-Supervised Learning

Constructs supervisory signals from the data itself without requiring manual labeling.

---

## Key Concepts

### 1. Feature

Features are measurable attributes or variables that describe data. In machine learning, features are the representation of raw data input into the model.

**Examples**:
- In house price prediction: area, number of rooms, location, year built
- In spam classification: word frequency, sender address, email length
- In image recognition: pixel values, edges, textures

### 2. Model

A model is a mathematical representation that learns patterns from data. It can be linear models, tree-based models, neural networks, etc.

**Model Training**: The process of adjusting model parameters to minimize the difference between predictions and actual values.

**Model Evaluation**: Using metrics such as accuracy, precision, recall, F1 score to assess model performance.

### 3. Overfitting and Underfitting

- **Overfitting**: Model performs well on training data but poorly on new, unseen data. The model learns noise in the training data.
- **Underfitting**: Model performs poorly on both training data and new data. The model is too simple to capture data patterns.

### 4. Training Set, Validation Set, and Test Set

- **Training Set**: Data used for model training
- **Validation Set**: Data used for hyperparameter tuning and model selection
- **Test Set**: Data used to evaluate final model performance

---

## Common Algorithms

### Regression Algorithms

| Algorithm | Applicable Scenarios | Advantages | Disadvantages |
|---|---|---|---|
| Linear Regression | Continuous value prediction | Simple, interpretable | Only captures linear relationships |
| Ridge Regression | High-dimensional data | Handles multicollinearity | Feature selection not performed |
| Lasso Regression | High-dimensional data | Performs feature selection | May over-regularize |

### Classification Algorithms

| Algorithm | Applicable Scenarios | Advantages | Disadvantages |
|---|---|---|---|
| Logistic Regression | Binary classification | Simple, interpretable | Only captures linear boundaries |
| Decision Tree | Classification and regression | Easy to interpret | Prone to overfitting |
| Random Forest | Complex classification | High accuracy, handles missing values | Model is a black box |
| SVM | High-dimensional classification | Effective in high-dimensional spaces | Sensitive to parameter selection |
| Neural Networks | Complex pattern recognition | Can learn complex patterns | Requires large amounts of data |

### Clustering Algorithms

| Algorithm | Applicable Scenarios | Advantages | Disadvantages |
|---|---|---|---|
| K-Means | Spherical clusters | Fast, scalable | Requires specifying K value |
| DBSCAN | Arbitrary-shaped clusters | Automatically determines cluster count | Sensitive to parameter selection |
| Hierarchical | Small to medium datasets | Creates dendrogram showing hierarchy | Computationally intensive |

---

## Application Fields

### Computer Vision

- Image classification (e.g., ResNet, VGG)
- Object detection (e.g., YOLO, Faster R-CNN)
- Image segmentation (e.g., U-Net, Mask R-CNN)
- Face recognition

### Natural Language Processing

- Text classification
- Named entity recognition
- Machine translation
- Question answering systems
- Text generation

### Speech Recognition

- Speech-to-text
- Speaker recognition
- Voice assistants

### Recommendation Systems

- Collaborative filtering
- Content-based recommendation
- Hybrid recommendation systems

### Autonomous Driving

- Environmental perception
- Path planning
- Decision control

### Healthcare

- Medical image analysis
- Drug discovery
- Disease prediction
- Personalized treatment

---

## Development Trends

### Deep Learning Dominance

Since 2012, deep learning has dominated many machine learning benchmarks, especially in computer vision and natural language processing.

**Key Milestones**:
- 2012: AlexNet wins ImageNet competition
- 2014: GAN (Generative Adversarial Networks) proposed
- 2015: ResNet introduces residual connections
- 2017: Transformer architecture proposed
- 2020: GPT-3 demonstrates few-shot learning capabilities

### Large Language Models

Since 2020, large language models (LLMs) have developed rapidly:
- GPT series (OpenAI)
- BERT series (Google)
- Claude (Anthropic)
- LLaMA (Meta)

These models demonstrate emergent capabilities in tasks such as text generation, translation, summarization, and question answering.

### AI for Science

Machine learning is increasingly applied to scientific research:
- Protein structure prediction (AlphaFold)
- Materials discovery
- Climate modeling
- Drug discovery

### Edge AI

As hardware improves and model compression techniques advance, AI models are increasingly deployed on edge devices:
- Mobile phones
- IoT devices
- Embedded systems

---

## Ethical Considerations

### Bias and Fairness

ML models may inherit and amplify biases present in training data, leading to unfair decisions.

### Privacy Protection

ML models may inadvertently memorize sensitive information from training data.

### Interpretability

Complex ML models (especially deep learning) are often "black boxes," making their decisions difficult to interpret.

### Security

ML models face various security threats:
- Adversarial attacks
- Data poisoning
- Model inversion

---

## Learning Resources

### Recommended Books

1. "Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow" — Aurélien Géron
2. "Pattern Recognition and Machine Learning" — Christopher Bishop
3. "Deep Learning" — Ian Goodfellow, Yoshua Bengio, Aaron Courville

### Online Courses

1. Andrew Ng's Machine Learning Course (Stanford)
2. fast.ai Practical Deep Learning for Coders
3. Coursera Deep Learning Specialization

### Open Source Frameworks

- **TensorFlow**: Google-developed deep learning framework
- **PyTorch**: Facebook-developed deep learning framework
- **Scikit-learn**: Classic machine learning library
- **JAX**: Google's high-performance ML library

---

## Summary

Machine learning, as a core technology of artificial intelligence, is profoundly changing various aspects of society. With continuous algorithm innovation, expanding application scenarios, and increasing computational power, machine learning will continue to drive technological progress and social development.

Understanding the basic concepts, common algorithms, and application fields of machine learning is essential for professionals across disciplines.
