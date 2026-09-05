# Project scaffold file
"""
Technical Interview Question Bank

Location:
    interview_engine/question_generation/technical_questions.py

Purpose:
    Provides technical interview questions organized by:
    - Programming languages
    - Backend
    - Frontend
    - Databases
    - Cloud
    - DevOps
    - AI / ML
    - Generative AI
    - Data structures and algorithms
    - System design
    - Security
    - Software engineering

This module is intentionally independent from the question generator.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


# ============================================================================
# Data Models
# ============================================================================


@dataclass(frozen=True)
class TechnicalQuestion:
    """Represents a technical interview question."""

    question: str
    topic: str
    difficulty: str = "medium"
    skill: str | None = None
    expected_answer_points: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ============================================================================
# Python
# ============================================================================


PYTHON_QUESTIONS = {
    "easy": [
        "What are the main features of Python?",
        "What is the difference between a list and a tuple in Python?",
        "What is the difference between == and is in Python?",
        "What are mutable and immutable objects in Python?",
        "What is None in Python?",
        "What is the difference between a set and a dictionary?",
        "What are *args and **kwargs?",
        "What is list comprehension?",
        "What is exception handling in Python?",
        "What is the difference between local and global variables?",
    ],
    "medium": [
        "Explain Python decorators with an example.",
        "What are generators in Python and when would you use them?",
        "What is the difference between shallow copy and deep copy?",
        "How does Python handle memory management?",
        "What is the Global Interpreter Lock (GIL)?",
        "Explain iterators and iterables in Python.",
        "What is a context manager in Python?",
        "How does inheritance work in Python?",
        "What are lambda functions?",
        "How would you optimize a slow Python program?",
    ],
    "hard": [
        "Explain Python's descriptor protocol.",
        "How does Python's garbage collector work?",
        "Explain method resolution order (MRO) in Python.",
        "How does asyncio work in Python?",
        "When would you use multiprocessing instead of multithreading in Python?",
        "How would you diagnose a memory leak in a Python application?",
        "Explain metaclasses and practical use cases.",
        "How would you design a highly concurrent Python service?",
        "How would you optimize a CPU-intensive Python application?",
        "Explain how Python imports and module caching work.",
    ],
}


# ============================================================================
# Java
# ============================================================================


JAVA_QUESTIONS = {
    "easy": [
        "What are the main features of Java?",
        "What is the difference between JDK, JRE, and JVM?",
        "What is the difference between == and equals() in Java?",
        "What is method overloading?",
        "What is method overriding?",
        "What are Java access modifiers?",
        "What is an interface?",
        "What is an abstract class?",
        "What is exception handling in Java?",
        "What is the difference between ArrayList and LinkedList?",
    ],
    "medium": [
        "Explain the Java Collections Framework.",
        "How does HashMap work internally?",
        "What is the difference between HashMap and ConcurrentHashMap?",
        "Explain Java garbage collection.",
        "What is the difference between checked and unchecked exceptions?",
        "Explain Java streams.",
        "What are functional interfaces?",
        "What is dependency injection?",
        "Explain multithreading in Java.",
        "What is the difference between synchronized and volatile?",
    ],
    "hard": [
        "How does the JVM manage memory?",
        "Explain the Java memory model.",
        "How does ConcurrentHashMap achieve thread safety?",
        "Explain JVM garbage collection algorithms.",
        "How would you troubleshoot high CPU usage in a Java application?",
        "How would you design a highly concurrent Java service?",
        "Explain class loading in the JVM.",
        "What causes deadlocks and how would you diagnose them?",
        "How would you optimize a Java application with high latency?",
        "Explain JVM tuning strategies for a production service.",
    ],
}


# ============================================================================
# JavaScript
# ============================================================================


JAVASCRIPT_QUESTIONS = {
    "easy": [
        "What is the difference between var, let, and const?",
        "What are JavaScript primitive data types?",
        "What is the difference between == and ===?",
        "What is a JavaScript function?",
        "What is an arrow function?",
        "What is an array in JavaScript?",
        "What is an object in JavaScript?",
        "What is JSON?",
        "What is the DOM?",
        "What is event handling in JavaScript?",
    ],
    "medium": [
        "Explain closures in JavaScript.",
        "What is the JavaScript event loop?",
        "What are promises?",
        "What is async/await?",
        "Explain prototypal inheritance.",
        "What is hoisting?",
        "What is event delegation?",
        "What is debouncing and throttling?",
        "What are higher-order functions?",
        "How does JavaScript handle asynchronous operations?",
    ],
    "hard": [
        "Explain the JavaScript event loop in detail.",
        "How does the microtask queue differ from the task queue?",
        "How would you optimize a large JavaScript application?",
        "How would you diagnose a memory leak in a browser application?",
        "Explain JavaScript garbage collection.",
        "How does V8 optimize JavaScript execution?",
        "How would you design a real-time JavaScript application?",
        "Explain module bundling and code splitting.",
        "How would you improve frontend performance?",
        "Explain service workers and their use cases.",
    ],
}


# ============================================================================
# TypeScript
# ============================================================================


TYPESCRIPT_QUESTIONS = {
    "easy": [
        "What is TypeScript?",
        "Why would you use TypeScript instead of JavaScript?",
        "What are interfaces in TypeScript?",
        "What are type aliases?",
        "What are union types?",
        "What are optional properties?",
        "What is type inference?",
        "What are enums?",
    ],
    "medium": [
        "Explain generics in TypeScript.",
        "What are utility types?",
        "Explain keyof and typeof.",
        "What are mapped types?",
        "What is type narrowing?",
        "What are discriminated unions?",
        "How do interfaces and type aliases differ?",
        "How would you type an API response?",
    ],
    "hard": [
        "Explain conditional types.",
        "Explain advanced TypeScript generics.",
        "How would you design a strongly typed API client?",
        "How would you model complex domain types?",
        "Explain TypeScript structural typing.",
        "How can TypeScript be used to enforce compile-time architecture constraints?",
    ],
}


# ============================================================================
# SQL
# ============================================================================


SQL_QUESTIONS = {
    "easy": [
        "What is SQL?",
        "What is the difference between WHERE and HAVING?",
        "What is a primary key?",
        "What is a foreign key?",
        "What is normalization?",
        "What is a JOIN?",
        "What is the difference between INNER JOIN and LEFT JOIN?",
        "What is GROUP BY?",
        "What is ORDER BY?",
        "What is a database index?",
    ],
    "medium": [
        "Explain database normalization forms.",
        "What are composite indexes?",
        "How does a database index improve query performance?",
        "What is a transaction?",
        "Explain ACID properties.",
        "What are isolation levels?",
        "What is a correlated subquery?",
        "What are window functions?",
        "How would you optimize a slow SQL query?",
        "What is the difference between DELETE, TRUNCATE, and DROP?",
    ],
    "hard": [
        "Explain database transaction isolation in detail.",
        "How would you diagnose database deadlocks?",
        "How would you design indexes for a high-volume database?",
        "How would you optimize a query scanning millions of rows?",
        "Explain database partitioning.",
        "What is database sharding?",
        "How would you design a highly available database?",
        "Explain MVCC.",
        "How would you handle database replication lag?",
        "How would you migrate a large production database with minimal downtime?",
    ],
}


# ============================================================================
# PostgreSQL
# ============================================================================


POSTGRESQL_QUESTIONS = {
    "easy": [
        "What is PostgreSQL?",
        "What are schemas in PostgreSQL?",
        "What is a PostgreSQL primary key?",
        "What are PostgreSQL indexes?",
        "What is a PostgreSQL sequence?",
    ],
    "medium": [
        "Explain PostgreSQL JSONB.",
        "What is VACUUM in PostgreSQL?",
        "What is EXPLAIN ANALYZE?",
        "How does PostgreSQL handle transactions?",
        "What is the difference between JSON and JSONB?",
        "How would you optimize a PostgreSQL query?",
        "What are partial indexes?",
        "What are materialized views?",
    ],
    "hard": [
        "Explain PostgreSQL MVCC.",
        "How does PostgreSQL vacuuming work internally?",
        "How would you optimize PostgreSQL for high write throughput?",
        "How would you design PostgreSQL replication?",
        "How would you troubleshoot database bloat?",
        "How would you partition a large PostgreSQL table?",
    ],
}


# ============================================================================
# MongoDB
# ============================================================================


MONGODB_QUESTIONS = {
    "easy": [
        "What is MongoDB?",
        "What is a document in MongoDB?",
        "What is a collection?",
        "What is BSON?",
        "What is an index in MongoDB?",
    ],
    "medium": [
        "What is MongoDB aggregation?",
        "How do MongoDB indexes work?",
        "When would you embed documents?",
        "When would you reference documents?",
        "How does MongoDB handle transactions?",
        "How would you optimize a MongoDB query?",
    ],
    "hard": [
        "Explain MongoDB sharding.",
        "How does MongoDB replication work?",
        "How would you design MongoDB for high availability?",
        "How would you handle a very large MongoDB collection?",
        "How would you diagnose slow MongoDB queries?",
    ],
}


# ============================================================================
# FastAPI
# ============================================================================


FASTAPI_QUESTIONS = {
    "easy": [
        "What is FastAPI?",
        "Why is FastAPI commonly used for REST APIs?",
        "What are FastAPI path parameters?",
        "What are query parameters?",
        "What is Pydantic used for in FastAPI?",
    ],
    "medium": [
        "How does dependency injection work in FastAPI?",
        "How would you implement authentication in FastAPI?",
        "How would you validate request data?",
        "How would you handle exceptions globally?",
        "How would you structure a large FastAPI application?",
        "How do async endpoints work in FastAPI?",
    ],
    "hard": [
        "How would you design a production-grade FastAPI application?",
        "How would you optimize a high-throughput FastAPI service?",
        "How would you implement distributed authentication?",
        "How would you handle background jobs in FastAPI?",
        "How would you design API versioning in FastAPI?",
        "How would you implement rate limiting?",
    ],
}


# ============================================================================
# Django
# ============================================================================


DJANGO_QUESTIONS = {
    "easy": [
        "What is Django?",
        "What is Django ORM?",
        "What is a Django model?",
        "What is a Django view?",
        "What is middleware in Django?",
    ],
    "medium": [
        "Explain Django migrations.",
        "How does Django authentication work?",
        "What are Django class-based views?",
        "How would you optimize Django ORM queries?",
        "What is select_related?",
        "What is prefetch_related?",
    ],
    "hard": [
        "How would you scale a Django application?",
        "How would you optimize Django under heavy traffic?",
        "How would you implement distributed caching?",
        "How would you design Django background processing?",
        "How would you handle database connection scaling?",
    ],
}


# ============================================================================
# React
# ============================================================================


REACT_QUESTIONS = {
    "easy": [
        "What is React?",
        "What is a React component?",
        "What are props?",
        "What is state in React?",
        "What is JSX?",
        "What is the Virtual DOM?",
        "What is useState?",
        "What is useEffect?",
    ],
    "medium": [
        "Explain the React component lifecycle.",
        "What are controlled and uncontrolled components?",
        "What is React Context?",
        "What is memoization in React?",
        "What is useMemo?",
        "What is useCallback?",
        "How would you optimize a React application?",
        "How do you manage state in a large React application?",
    ],
    "hard": [
        "Explain React reconciliation.",
        "How does React rendering work internally?",
        "How would you optimize a complex React application?",
        "How would you design state management for a large frontend?",
        "Explain React concurrent rendering.",
        "How would you diagnose unnecessary component re-renders?",
    ],
}


# ============================================================================
# Node.js
# ============================================================================


NODEJS_QUESTIONS = {
    "easy": [
        "What is Node.js?",
        "Why is Node.js useful for backend development?",
        "What is npm?",
        "What is the Node.js event loop?",
        "What is a Node.js module?",
    ],
    "medium": [
        "How does asynchronous programming work in Node.js?",
        "What are streams in Node.js?",
        "What are buffers?",
        "How would you handle errors in Node.js?",
        "How would you structure a Node.js API?",
        "What is middleware in Express.js?",
    ],
    "hard": [
        "How would you scale a Node.js application?",
        "How would you handle CPU-intensive work in Node.js?",
        "Explain Node.js worker threads.",
        "How would you diagnose memory leaks?",
        "How would you design a high-throughput Node.js API?",
    ],
}


# ============================================================================
# REST API
# ============================================================================


REST_API_QUESTIONS = {
    "easy": [
        "What is a REST API?",
        "What are HTTP methods?",
        "What is the difference between GET and POST?",
        "What are HTTP status codes?",
        "What is JSON?",
    ],
    "medium": [
        "What makes an API RESTful?",
        "What is idempotency?",
        "How would you design API pagination?",
        "How would you implement API authentication?",
        "How would you handle API versioning?",
        "What is the difference between PUT and PATCH?",
    ],
    "hard": [
        "How would you design a highly scalable REST API?",
        "How would you implement distributed rate limiting?",
        "How would you ensure API backward compatibility?",
        "How would you design API observability?",
        "How would you handle distributed transactions across APIs?",
    ],
}


# ============================================================================
# Docker
# ============================================================================


DOCKER_QUESTIONS = {
    "easy": [
        "What is Docker?",
        "What is a Docker image?",
        "What is a Docker container?",
        "What is a Dockerfile?",
        "What is Docker Compose?",
    ],
    "medium": [
        "What is the difference between an image and a container?",
        "How does Docker networking work?",
        "What are Docker volumes?",
        "How would you reduce Docker image size?",
        "What is a multi-stage Docker build?",
        "How would you debug a failing container?",
    ],
    "hard": [
        "How would you secure Docker containers?",
        "How would you optimize containers for production?",
        "Explain Docker container isolation.",
        "How would you design a containerized microservices platform?",
        "How would you troubleshoot container networking issues?",
    ],
}


# ============================================================================
# Kubernetes
# ============================================================================


KUBERNETES_QUESTIONS = {
    "easy": [
        "What is Kubernetes?",
        "What is a Pod?",
        "What is a Deployment?",
        "What is a Service?",
        "What is a Namespace?",
    ],
    "medium": [
        "What is a Kubernetes ConfigMap?",
        "What are Secrets?",
        "What are readiness and liveness probes?",
        "How does Kubernetes service discovery work?",
        "What is Horizontal Pod Autoscaling?",
        "How would you deploy an application to Kubernetes?",
    ],
    "hard": [
        "How does Kubernetes scheduling work?",
        "How would you design a highly available Kubernetes cluster?",
        "How would you troubleshoot a pod stuck in CrashLoopBackOff?",
        "How would you implement zero-downtime deployments?",
        "How would you secure a Kubernetes cluster?",
        "How would you design Kubernetes resource limits?",
    ],
}


# ============================================================================
# AWS
# ============================================================================


AWS_QUESTIONS = {
    "easy": [
        "What is AWS?",
        "What is Amazon EC2?",
        "What is Amazon S3?",
        "What is AWS IAM?",
        "What is Amazon RDS?",
    ],
    "medium": [
        "What is the difference between EC2 and Lambda?",
        "How does S3 storage work?",
        "How would you secure an S3 bucket?",
        "What is an IAM role?",
        "How does AWS Auto Scaling work?",
        "What is Amazon CloudWatch?",
        "What is a VPC?",
    ],
    "hard": [
        "How would you design a highly available AWS application?",
        "How would you design a multi-region AWS architecture?",
        "How would you secure a production AWS environment?",
        "How would you optimize AWS infrastructure costs?",
        "How would you design an event-driven AWS architecture?",
        "How would you handle disaster recovery in AWS?",
    ],
}


# ============================================================================
# Machine Learning
# ============================================================================


MACHINE_LEARNING_QUESTIONS = {
    "easy": [
        "What is machine learning?",
        "What is supervised learning?",
        "What is unsupervised learning?",
        "What is classification?",
        "What is regression?",
        "What is overfitting?",
        "What is underfitting?",
        "What is a training dataset?",
        "What is a test dataset?",
        "What is feature engineering?",
    ],
    "medium": [
        "Explain the bias-variance tradeoff.",
        "What is cross-validation?",
        "What is regularization?",
        "How do you handle missing data?",
        "How do you handle imbalanced datasets?",
        "What is feature scaling?",
        "How do you select machine learning features?",
        "How would you evaluate a classification model?",
        "What is precision versus recall?",
        "What is an ROC-AUC score?",
    ],
    "hard": [
        "How would you diagnose model overfitting in production?",
        "How would you design an ML training pipeline?",
        "How would you monitor model drift?",
        "How would you handle data drift?",
        "How would you design a scalable model-serving system?",
        "How would you optimize model inference latency?",
        "How would you build an explainable ML system?",
        "How would you evaluate an ML model when labels are delayed?",
    ],
}


# ============================================================================
# Deep Learning
# ============================================================================


DEEP_LEARNING_QUESTIONS = {
    "easy": [
        "What is deep learning?",
        "What is a neural network?",
        "What is an activation function?",
        "What is an epoch?",
        "What is a batch size?",
    ],
    "medium": [
        "What is backpropagation?",
        "What is gradient descent?",
        "What is dropout?",
        "What is batch normalization?",
        "What is the difference between CNN and RNN?",
        "What is transfer learning?",
    ],
    "hard": [
        "Explain vanishing and exploding gradients.",
        "How would you optimize deep learning training?",
        "How would you reduce model inference latency?",
        "How would you design distributed deep learning training?",
        "How would you choose an architecture for a new deep learning problem?",
    ],
}


# ============================================================================
# NLP
# ============================================================================


NLP_QUESTIONS = {
    "easy": [
        "What is natural language processing?",
        "What is tokenization?",
        "What is stemming?",
        "What is lemmatization?",
        "What are stop words?",
        "What is TF-IDF?",
    ],
    "medium": [
        "What are word embeddings?",
        "What is the difference between Word2Vec and TF-IDF?",
        "What is named entity recognition?",
        "What is sentiment analysis?",
        "What is attention in NLP?",
        "What is a transformer?",
    ],
    "hard": [
        "Explain transformer architecture.",
        "How does self-attention work?",
        "How would you fine-tune an NLP model?",
        "How would you evaluate an NLP system?",
        "How would you reduce hallucinations in an NLP application?",
        "How would you build a production NLP pipeline?",
    ],
}


# ============================================================================
# Generative AI
# ============================================================================


GENERATIVE_AI_QUESTIONS = {
    "easy": [
        "What is Generative AI?",
        "What is a large language model?",
        "What is prompt engineering?",
        "What is a token in an LLM?",
        "What is an embedding?",
        "What is a context window?",
    ],
    "medium": [
        "What is Retrieval-Augmented Generation?",
        "How does semantic search work?",
        "What is chunking in a RAG pipeline?",
        "What is vector search?",
        "What is temperature in an LLM?",
        "How would you evaluate an LLM application?",
        "What is function calling or tool use?",
        "What is prompt injection?",
    ],
    "hard": [
        "How would you design a production RAG system?",
        "How would you reduce hallucinations in a RAG application?",
        "How would you evaluate retrieval quality?",
        "How would you optimize LLM inference cost?",
        "How would you design an LLM application for high concurrency?",
        "How would you protect an LLM application against prompt injection?",
        "How would you choose between RAG and fine-tuning?",
        "How would you implement LLM observability?",
    ],
}


# ============================================================================
# RAG
# ============================================================================


RAG_QUESTIONS = {
    "easy": [
        "What is Retrieval-Augmented Generation?",
        "Why is RAG useful?",
        "What is a vector database?",
        "What are embeddings?",
        "What is document chunking?",
    ],
    "medium": [
        "How would you design a basic RAG pipeline?",
        "How do you choose chunk size?",
        "What is semantic retrieval?",
        "How would you improve retrieval relevance?",
        "What is hybrid search?",
        "How would you evaluate a RAG system?",
    ],
    "hard": [
        "How would you design a production-scale RAG architecture?",
        "How would you reduce hallucinations in RAG?",
        "How would you handle stale documents?",
        "How would you implement multi-tenant RAG?",
        "How would you optimize vector search latency?",
        "How would you evaluate retrieval and generation separately?",
    ],
}


# ============================================================================
# System Design
# ============================================================================


SYSTEM_DESIGN_QUESTIONS = {
    "easy": [
        "What is horizontal scaling?",
        "What is vertical scaling?",
        "What is caching?",
        "What is a load balancer?",
        "What is a database replica?",
    ],
    "medium": [
        "How would you design a URL shortener?",
        "How would you design a notification system?",
        "How would you design a file upload service?",
        "How would you design a rate limiter?",
        "How would you design a basic chat application?",
        "How would you design a job queue?",
    ],
    "hard": [
        "Design a highly scalable distributed messaging system.",
        "Design a globally distributed URL-shortening service.",
        "Design a large-scale video streaming platform.",
        "Design a multi-tenant SaaS platform.",
        "Design a distributed search system.",
        "Design a highly available payment processing system.",
        "Design a large-scale recommendation system.",
    ],
}


# ============================================================================
# Data Structures & Algorithms
# ============================================================================


DSA_QUESTIONS = {
    "easy": [
        "What is the difference between an array and a linked list?",
        "What is a stack?",
        "What is a queue?",
        "What is a hash table?",
        "What is binary search?",
        "What is recursion?",
        "What is Big-O notation?",
        "What is a binary tree?",
    ],
    "medium": [
        "How would you detect a cycle in a linked list?",
        "How would you find the middle of a linked list?",
        "How would you merge two sorted linked lists?",
        "How would you find the first and last position of an element?",
        "How does binary search work on a rotated sorted array?",
        "How would you find the maximum subarray sum?",
        "How would you implement a stack using queues?",
        "How would you implement a queue using stacks?",
    ],
    "hard": [
        "How would you design an LRU cache?",
        "How would you find the kth largest element efficiently?",
        "How would you detect cycles in a directed graph?",
        "How would you find the shortest path in a weighted graph?",
        "How would you solve the N-Queens problem?",
        "How would you design a trie?",
        "How would you solve a dynamic programming problem with overlapping subproblems?",
    ],
}


# ============================================================================
# Software Engineering
# ============================================================================


SOFTWARE_ENGINEERING_QUESTIONS = {
    "easy": [
        "What is object-oriented programming?",
        "What are the four pillars of OOP?",
        "What is encapsulation?",
        "What is inheritance?",
        "What is polymorphism?",
        "What is abstraction?",
    ],
    "medium": [
        "What are SOLID principles?",
        "What is dependency injection?",
        "What is unit testing?",
        "What is integration testing?",
        "What is mocking?",
        "What is clean architecture?",
        "What is technical debt?",
    ],
    "hard": [
        "How would you refactor a legacy application?",
        "How would you design a maintainable microservices architecture?",
        "How would you introduce backward-compatible API changes?",
        "How would you manage technical debt in a large engineering organization?",
        "How would you design a reliable distributed service?",
    ],
}


# ============================================================================
# Security
# ============================================================================


SECURITY_QUESTIONS = {
    "easy": [
        "What is authentication?",
        "What is authorization?",
        "What is encryption?",
        "What is hashing?",
        "What is HTTPS?",
    ],
    "medium": [
        "What is JWT authentication?",
        "What is OAuth 2.0?",
        "What is SQL injection?",
        "What is cross-site scripting?",
        "What is CSRF?",
        "How should passwords be stored securely?",
    ],
    "hard": [
        "How would you secure a production REST API?",
        "How would you design an OAuth-based authentication system?",
        "How would you protect a web application from common attacks?",
        "How would you design secrets management?",
        "How would you implement zero-trust service communication?",
    ],
}


# ============================================================================
# DevOps / CI-CD
# ============================================================================


DEVOPS_QUESTIONS = {
    "easy": [
        "What is CI/CD?",
        "What is continuous integration?",
        "What is continuous deployment?",
        "What is infrastructure as code?",
        "What is Git?",
    ],
    "medium": [
        "How would you design a CI/CD pipeline?",
        "What is blue-green deployment?",
        "What is canary deployment?",
        "How would you handle deployment rollbacks?",
        "What is infrastructure as code?",
        "How would you monitor a production service?",
    ],
    "hard": [
        "How would you design a zero-downtime deployment system?",
        "How would you design CI/CD for multiple microservices?",
        "How would you implement progressive delivery?",
        "How would you secure a CI/CD pipeline?",
        "How would you design production observability?",
    ],
}


# ============================================================================
# Technology Registry
# ============================================================================


TECHNICAL_QUESTION_BANK = {
    "python": PYTHON_QUESTIONS,
    "java": JAVA_QUESTIONS,
    "javascript": JAVASCRIPT_QUESTIONS,
    "typescript": TYPESCRIPT_QUESTIONS,
    "sql": SQL_QUESTIONS,
    "postgresql": POSTGRESQL_QUESTIONS,
    "postgres": POSTGRESQL_QUESTIONS,
    "mongodb": MONGODB_QUESTIONS,
    "mongo": MONGODB_QUESTIONS,
    "fastapi": FASTAPI_QUESTIONS,
    "django": DJANGO_QUESTIONS,
    "react": REACT_QUESTIONS,
    "node.js": NODEJS_QUESTIONS,
    "nodejs": NODEJS_QUESTIONS,
    "express.js": NODEJS_QUESTIONS,
    "express": NODEJS_QUESTIONS,
    "rest": REST_API_QUESTIONS,
    "rest api": REST_API_QUESTIONS,
    "docker": DOCKER_QUESTIONS,
    "kubernetes": KUBERNETES_QUESTIONS,
    "k8s": KUBERNETES_QUESTIONS,
    "aws": AWS_QUESTIONS,
    "machine learning": MACHINE_LEARNING_QUESTIONS,
    "machine-learning": MACHINE_LEARNING_QUESTIONS,
    "ml": MACHINE_LEARNING_QUESTIONS,
    "deep learning": DEEP_LEARNING_QUESTIONS,
    "deep-learning": DEEP_LEARNING_QUESTIONS,
    "dl": DEEP_LEARNING_QUESTIONS,
    "nlp": NLP_QUESTIONS,
    "natural language processing": NLP_QUESTIONS,
    "generative ai": GENERATIVE_AI_QUESTIONS,
    "genai": GENERATIVE_AI_QUESTIONS,
    "llm": GENERATIVE_AI_QUESTIONS,
    "large language model": GENERATIVE_AI_QUESTIONS,
    "rag": RAG_QUESTIONS,
    "retrieval augmented generation": RAG_QUESTIONS,
    "system design": SYSTEM_DESIGN_QUESTIONS,
    "dsa": DSA_QUESTIONS,
    "data structures": DSA_QUESTIONS,
    "algorithms": DSA_QUESTIONS,
    "software engineering": SOFTWARE_ENGINEERING_QUESTIONS,
    "oop": SOFTWARE_ENGINEERING_QUESTIONS,
    "security": SECURITY_QUESTIONS,
    "cybersecurity": SECURITY_QUESTIONS,
    "devops": DEVOPS_QUESTIONS,
    "ci/cd": DEVOPS_QUESTIONS,
}


# ============================================================================
# Skill Aliases
# ============================================================================


SKILL_ALIASES = {
    "py": "python",
    "python3": "python",
    "js": "javascript",
    "ts": "typescript",
    "postgres": "postgresql",
    "postgresql database": "postgresql",
    "mongo": "mongodb",
    "mongodb database": "mongodb",
    "node": "nodejs",
    "node.js": "nodejs",
    "express.js": "nodejs",
    "k8s": "kubernetes",
    "amazon web services": "aws",
    "artificial intelligence": "generative ai",
    "gen ai": "generative ai",
    "gen-ai": "generative ai",
    "large language models": "llm",
    "retrieval augmented generation": "rag",
}


# ============================================================================
# Question Bank Class
# ============================================================================


class TechnicalQuestionBank:
    """
    Interface for retrieving technical interview questions.

    Example:

        bank = TechnicalQuestionBank()

        questions = bank.get_questions(
            skill="Python",
            difficulty="medium",
            count=5,
        )
    """

    def __init__(
        self,
        question_bank: dict[str, dict[str, list[str]]] | None = None,
    ) -> None:

        self.question_bank = (
            question_bank
            if question_bank is not None
            else TECHNICAL_QUESTION_BANK
        )

    # ------------------------------------------------------------------
    # Normalization
    # ------------------------------------------------------------------

    @staticmethod
    def normalize_skill(
        skill: str,
    ) -> str:
        """Normalize skill names."""

        value = str(
            skill
        ).strip().lower()

        value = SKILL_ALIASES.get(
            value,
            value,
        )

        return value

    @staticmethod
    def normalize_difficulty(
        difficulty: str,
    ) -> str:
        """Normalize question difficulty."""

        value = str(
            difficulty
        ).strip().lower()

        if value not in {
            "easy",
            "medium",
            "hard",
        }:
            return "medium"

        return value

    # ------------------------------------------------------------------
    # Availability
    # ------------------------------------------------------------------

    def supported_skills(self) -> list[str]:
        """Return supported skills."""

        return sorted(
            self.question_bank.keys()
        )

    def has_skill(
        self,
        skill: str,
    ) -> bool:
        """Check whether a skill exists."""

        normalized = (
            self.normalize_skill(
                skill
            )
        )

        return normalized in self.question_bank

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def get_questions(
        self,
        *,
        skill: str,
        difficulty: str = "medium",
        count: int | None = None,
    ) -> list[TechnicalQuestion]:
        """
        Get technical questions for a skill.
        """

        normalized_skill = (
            self.normalize_skill(
                skill
            )
        )

        difficulty = (
            self.normalize_difficulty(
                difficulty
            )
        )

        bank = self.question_bank.get(
            normalized_skill
        )

        if not bank:
            return []

        questions = bank.get(
            difficulty,
            bank.get(
                "medium",
                [],
            ),
        )

        if count is not None:

            count = max(
                0,
                int(count),
            )

            questions = questions[
                :count
            ]

        return [
            TechnicalQuestion(
                question=question,
                topic=normalized_skill,
                difficulty=difficulty,
                skill=normalized_skill,
                tags=(
                    normalized_skill,
                    "technical",
                ),
            )
            for question in questions
        ]

    def get_all_questions(
        self,
        *,
        skill: str,
    ) -> list[TechnicalQuestion]:
        """Return all difficulty levels for a skill."""

        normalized_skill = (
            self.normalize_skill(
                skill
            )
        )

        bank = self.question_bank.get(
            normalized_skill,
            {},
        )

        result: list[
            TechnicalQuestion
        ] = []

        for difficulty in (
            "easy",
            "medium",
            "hard",
        ):

            for question in bank.get(
                difficulty,
                [],
            ):

                result.append(
                    TechnicalQuestion(
                        question=question,
                        topic=normalized_skill,
                        difficulty=difficulty,
                        skill=normalized_skill,
                        tags=(
                            normalized_skill,
                            "technical",
                        ),
                    )
                )

        return result

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search(
        self,
        keyword: str,
        *,
        difficulty: str | None = None,
        skill: str | None = None,
    ) -> list[TechnicalQuestion]:
        """Search the technical question bank."""

        keyword = str(
            keyword
        ).strip().lower()

        difficulties = (
            [self.normalize_difficulty(difficulty)]
            if difficulty
            else [
                "easy",
                "medium",
                "hard",
            ]
        )

        skills = (
            [self.normalize_skill(skill)]
            if skill
            else list(
                self.question_bank.keys()
            )
        )

        results: list[
            TechnicalQuestion
        ] = []

        seen: set[str] = set()

        for current_skill in skills:

            bank = self.question_bank.get(
                current_skill,
                {},
            )

            for current_difficulty in difficulties:

                for question in bank.get(
                    current_difficulty,
                    [],
                ):

                    if keyword not in question.lower():
                        continue

                    key = question.lower()

                    if key in seen:
                        continue

                    seen.add(key)

                    results.append(
                        TechnicalQuestion(
                            question=question,
                            topic=current_skill,
                            difficulty=current_difficulty,
                            skill=current_skill,
                            tags=(
                                current_skill,
                                "technical",
                            ),
                        )
                    )

        return results

    # ------------------------------------------------------------------
    # Random Selection
    # ------------------------------------------------------------------

    def random_question(
        self,
        *,
        skill: str,
        difficulty: str = "medium",
    ) -> TechnicalQuestion | None:
        """Return one random technical question."""

        import random

        questions = self.get_questions(
            skill=skill,
            difficulty=difficulty,
        )

        if not questions:
            return None

        return random.choice(
            questions
        )

    # ------------------------------------------------------------------
    # Mixed Skill Questions
    # ------------------------------------------------------------------

    def get_mixed_questions(
        self,
        *,
        skills: list[str],
        difficulty: str = "medium",
        count: int = 10,
    ) -> list[TechnicalQuestion]:
        """
        Get questions across multiple skills.
        """

        count = max(
            1,
            int(count),
        )

        result: list[
            TechnicalQuestion
        ] = []

        seen: set[str] = set()

        normalized_skills = []

        for skill in skills:

            normalized = (
                self.normalize_skill(
                    skill
                )
            )

            if normalized in normalized_skills:
                continue

            normalized_skills.append(
                normalized
            )

        if not normalized_skills:
            return result

        index = 0

        while (
            len(result) < count
            and index < count * 5
        ):

            skill = normalized_skills[
                index
                % len(normalized_skills)
            ]

            index += 1

            question = (
                self.random_question(
                    skill=skill,
                    difficulty=difficulty,
                )
            )

            if question is None:
                continue

            key = question.question.lower()

            if key in seen:
                continue

            seen.add(key)

            result.append(
                question
            )

        return result

    # ------------------------------------------------------------------
    # Adaptive Difficulty
    # ------------------------------------------------------------------

    def next_difficulty(
        self,
        *,
        current_difficulty: str,
        score: float,
    ) -> str:
        """
        Calculate next difficulty based on candidate performance.

        Score:
            0-100

        >= 85:
            Increase difficulty.

        <= 45:
            Decrease difficulty.
        """

        current = (
            self.normalize_difficulty(
                current_difficulty
            )
        )

        try:
            score = float(
                score
            )
        except (
            TypeError,
            ValueError,
        ):
            return current

        if score >= 85:

            if current == "easy":
                return "medium"

            return "hard"

        if score <= 45:

            if current == "hard":
                return "medium"

            return "easy"

        return current

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    @staticmethod
    def to_dict(
        questions: list[TechnicalQuestion],
    ) -> list[dict[str, Any]]:
        """Serialize questions."""

        return [
            question.to_dict()
            for question in questions
        ]


# ============================================================================
# Convenience Functions
# ============================================================================


_default_bank = TechnicalQuestionBank()


def get_technical_questions(
    skill: str,
    difficulty: str = "medium",
    count: int | None = None,
) -> list[dict[str, Any]]:
    """Convenience function for retrieving questions."""

    questions = _default_bank.get_questions(
        skill=skill,
        difficulty=difficulty,
        count=count,
    )

    return _default_bank.to_dict(
        questions
    )


def get_random_technical_question(
    skill: str,
    difficulty: str = "medium",
) -> dict[str, Any] | None:
    """Return one random technical question."""

    question = _default_bank.random_question(
        skill=skill,
        difficulty=difficulty,
    )

    if question is None:
        return None

    return question.to_dict()


def search_technical_questions(
    keyword: str,
    difficulty: str | None = None,
    skill: str | None = None,
) -> list[dict[str, Any]]:
    """Search technical questions."""

    questions = _default_bank.search(
        keyword,
        difficulty=difficulty,
        skill=skill,
    )

    return _default_bank.to_dict(
        questions
    )


# ============================================================================
# Public API
# ============================================================================


__all__ = [
    "TechnicalQuestion",
    "TechnicalQuestionBank",
    "TECHNICAL_QUESTION_BANK",
    "PYTHON_QUESTIONS",
    "JAVA_QUESTIONS",
    "JAVASCRIPT_QUESTIONS",
    "TYPESCRIPT_QUESTIONS",
    "SQL_QUESTIONS",
    "POSTGRESQL_QUESTIONS",
    "MONGODB_QUESTIONS",
    "FASTAPI_QUESTIONS",
    "DJANGO_QUESTIONS",
    "REACT_QUESTIONS",
    "NODEJS_QUESTIONS",
    "REST_API_QUESTIONS",
    "DOCKER_QUESTIONS",
    "KUBERNETES_QUESTIONS",
    "AWS_QUESTIONS",
    "MACHINE_LEARNING_QUESTIONS",
    "DEEP_LEARNING_QUESTIONS",
    "NLP_QUESTIONS",
    "GENERATIVE_AI_QUESTIONS",
    "RAG_QUESTIONS",
    "SYSTEM_DESIGN_QUESTIONS",
    "DSA_QUESTIONS",
    "SOFTWARE_ENGINEERING_QUESTIONS",
    "SECURITY_QUESTIONS",
    "DEVOPS_QUESTIONS",
    "get_technical_questions",
    "get_random_technical_question",
    "search_technical_questions",
]