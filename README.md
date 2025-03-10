# FastAPI Demonstration

## Overview
This project is a FastAPI application designed for image analysis and invoice processing. It utilizes SQL Server for database management and integrates with the Anthropic API for AI-driven analysis.

## Features
- Image analysis using AI models.
- Invoice processing with support for multiple prompts.
- Basic authentication for secure API access.
- Database support for storing prompts and analysis results.

## Installation

### Prerequisites
- Python 3.10 or higher
- Poetry for dependency management

### Setup
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

3. Set up environment variables:
   - `ANTHROPIC_API_KEY`: Your API key for the Anthropic service.
   - `BASIC_AUTH_USERNNAME`: Username for basic authentication.
   - `BASIC_AUTH_PASSWORD`: Password for basic authentication.
   - `DATABASE_URL`: Connection string for your database.

4. Run the application:
   ```bash
   poetry run uvicorn main:app --host 0.0.0.0 --reload
   ```

## API Endpoints

### Analyze Invoice
- **POST** `/api/v1/analyze_invoice`
  - Request Body:
    ```json
    {
      "image_url": "string",
      "questions": ["string"],
      "prompt_id": 1
    }
    ```
  - Description: Analyzes the provided image URL using the specified prompt.

- **GET** `/api/v1/analyze_invoice/{guid}`
  - Description: Retrieves the analysis result for a specific invoice by GUID.

### Prompts
- **GET** `/api/v1/prompts`
  - Description: Retrieves a list of prompts.

- **POST** `/api/v1/prompts/`
  - Request Body:
    ```json
    {
      "name": "string",
      "prompt": "string"
    }
    ```
  - Description: Creates a new prompt.

- **GET** `/api/v1/prompts/{prompt_id}`
  - Description: Retrieves a specific prompt by ID.

- **PUT** `/api/v1/prompts/{prompt_id}`
  - Request Body:
    ```json
    {
      "name": "string",
      "prompt": "string"
    }
    ```
  - Description: Updates an existing prompt.

- **DELETE** `/api/v1/prompts/{prompt_id}`
  - Description: Deletes a specific prompt by ID.

### Image Comparison
- **POST** `/api/v1/image_comparison`
  - Request Body:
    ```json
    {
      "product_image": "string",
      "captured_image": "string",
      "prompt_id": 1
    }
    ```
  - Description: Compares two images and returns the analysis result.

- **GET** `/api/v1/image_comparison/{guid}`
  - Description: Retrieves the comparison result for a specific image comparison by GUID.

### Shipping Document Review
- **POST** `/api/v2/analyze_invoice`
  - Request Body:
    ```json
    {
      "image_url": "string",
      "prompt_id": 1
    }
    ```
  - Description: Analyzes the provided image URL for shipping documents using the specified prompt.

- **GET** `/api/v2/analyze_invoice/{guid}`
  - Description: Retrieves the analysis result for a specific shipping document by GUID.


