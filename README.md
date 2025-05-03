# CodeCliBattle: AI Code Assistants Comparison

This repository contains a structured comparison of four leading AI code assistants and their ability to generate Python code for a specific task.

## Challenge Overview

Each AI assistant was given the same prompt to create a Python integration with the DeepL API:

```
Write all the Python code required to integrate with the DeepL API. See the DeepL integration documentation at https://developers.deepl.com/docs.

Ensure that:

1. Your code is as secure as possible.
2. Your code does not create or promote memory leaks.
3. You follow best software‐development practices and patterns—including SOLID principles, DRY, KISS, and relevant design patterns (Gang of Four or newer).
4. All code is properly documented.
5. You include a README.md explaining the repository structure.
6. Your code is modular and reusable, with high cohesion and loose coupling.
7. Your code reads the DEEPL_API_KEY environment variable to obtain the API key.
8. You include unit tests and integration tests for every method you implement.
9. You separate unit tests and integrations tests into multiple files (not one big test file).
10. After completing your implementation, create demo.py that uses your code to translate the following string into English, Ukrainian, and Italian: "Un Saludos a mis queridos colegas de IOL"
```

## AI Code Assistants Evaluated

1. **Amazon Q** - Implementation in `DeepL.AmazonQ/`
2. **Claude Code** - Implementation in `DeepL.ClaudeCLI/`
3. **OpenAI Codex** - Implementation in `DeepL.Codex/`
4. **Plandex AI** - Implementation in `DeepL.Plandex/`

## Repository Structure

```
├── DeepL.AmazonQ/      # Amazon Q's implementation
├── DeepL.ClaudeCLI/    # Claude Code's implementation
├── DeepL.Codex/        # OpenAI Codex's implementation
├── DeepL.Plandex/      # Plandex AI's implementation
├── Evaluation.md       # Comprehensive evaluation of all implementations
└── README.md           # This file
```

## Evaluation Criteria

The code from each assistant is evaluated using the following criteria:

1. **Security (20%)**
   - Proper handling of API keys
   - Use of secure libraries and methods
   - Adherence to secure coding best practices

2. **Code Quality and Design Principles (25%)**
   - Adherence to SOLID principles
   - Following DRY and KISS principles
   - Application of appropriate design patterns

3. **Modularity and Reusability (15%)**
   - Clear separation of concerns
   - Loose coupling between components
   - Modular structure facilitating integration and reuse

4. **Documentation (15%)**
   - Code documentation clarity
   - Comprehensive README.md
   - Explicit and helpful descriptions for methods and classes

5. **Testing (15%)**
   - Presence of both unit and integration tests
   - Proper separation of test files
   - Coverage and thoroughness of tests

6. **Resource Management (10%)**
   - No patterns that could lead to memory leaks
   - Efficient management of resources
   - Performance considerations in implementation

## How to Review

1. Examine each implementation directory to see how each AI assistant approached the problem
2. Review the `Evaluation.md` file for a detailed assessment of each implementation
3. Run each implementation (following the instructions in their respective README files) to see them in action

## Purpose

This repository serves as a benchmark for evaluating AI code assistants' capabilities in generating production-ready code that follows best practices. The results can help developers make informed decisions about which AI assistant might best suit their coding needs. 