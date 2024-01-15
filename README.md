# Cloud Market API

- [Introduction](#introduction)
- [Data Model](#data-model)
- [User API](#user-api)
  - [Get Users](#get-users)
- [Product API](#product-api)
  - [Create a Product](#create-a-product)
  - [Get a Product](#get-a-product)
  - [List all Products](#list-all-products)
  - [Edit a Product](#edit-a-product)
  - [Edit a Product partially](#edit-a-product-partially)
  - [Delete a Product](#delete-a-product)
- [Order API](#order-api)
  - [Create an Order](#create-an-order)
  - [Get an Order](#get-an-order)
  - [List all Orders](#list-all-orders)
  - [Edit an Order](#edit-an-order)
  - [Edit an Order partially](#edit-an-order-partially)
  - [Delete an Order](#delete-an-order)
  - [Add a Product to an Order](#add-a-product-to-an-order)
  - [Remove a Product from an Order](#remove-a-product-from-an-order)

## Introduction

This is the API specification for a RESTful API of the Marketplace app. The app allows users to manage and order a product using Google Cloud Datastore to store the data. The app is deployed on Google App Engine.

## Data Model

The app stores three kinds of entities in Datastore,`User`, `Product` and `Order`.

**Users**

Represent users of the marketplace.

| **Property** | **Data Type** | **Notes**                            |
| :----------- | :------------ | :----------------------------------- |
| id           | Integer       | Unique identifier of the user.       |
| name         | String        | Name of the user.                    |
| email        | String        | Email address of the user.           |
| orders       | List          | A list of orders placed by the user. |
| self         | String        | The URL of the user.                 |

**Products**

Represent products available on the marketplace.

| **Property** | **Data Type** | **Notes**                                                  |
| :----------- | :------------ | :--------------------------------------------------------- |
| id           | Integer       | Unique identifier id of the product.                       |
| name         | String        | Name of the product. Must be 1-100 characters long.        |
| description  | String        | Description of the product. Must be 0-500 characters long. |
| price        | Float         | Price of the product. Must be a positive number.           |
| stock        | Integer       | Stock of the product. Must be a positive number.           |
| self         | String        | The URL of the product.                                    |

**Orders**

Represent orders placed by users.

| **Property**   | **Data Type** | **Notes**                                                                                       |
| :------------- | :------------ | :---------------------------------------------------------------------------------------------- |
| id             | Integer       | Unique identifier of the order.                                                                 |
| user           | Integer       | The user who placed the order.                                                                  |
| products       | List          | A list of products in the order.                                                                |
| status         | String        | Status of the order. Must be one of the following: "pending", "completed", "canceled".          |
| paymentMethod  | String        | Payment method of the order. Must be one of the following: "cash", "credit card", "debit card". |
| billingAddress | String        | Billing address of the order.                                                                   |
| total          | Float         | Total price of the order.                                                                       |
| dateCreated    | String        | The date the order was placed.                                                                  |
| dateModified   | String        | The date the order was last modified.                                                           |
| self           | String        | The URL of the order.                                                                           |

## User API

### Get Users

Allows you to get all users.

| GET /users |
| :--------- |

**Request**

Path Parameters

None

Request Body

None

**Response**

Response Body Format

JSON

Response Statuses

| **Outcome** | **Status Code** | **Notes** |
| :---------- | :-------------- | :-------- |
| Success     | 200 OK          |           |

Response Examples

_Success_

```json
Status: 200 OK

{
    "totalItems": 2,
    "users": [
        {
            "email": "user1@users.com",
            "id": "auth0|65737eb618710d662aeb86e4",
            "name": "user1@users.com",
            "orders": [
                {
                    "billingAddress": "86 Cypress St.Niceville, FL 32578",
                    "dateCreated": "Sun, 10 Dec 2023 12:01:14 GMT",
                    "dateModified": "Sun, 10 Dec 2023 12:01:15 GMT",
                    "id": 4860105484926976,
                    "paymentMethod": "credit",
                    "products": [],
                    "self": "http://127.0.0.1:8080/orders/4860105484926976",
                    "status": "pending",
                    "total": 0.0,
                    "user": "auth0|65737eb618710d662aeb86e4"
                }
            ],
            "self": "http://127.0.0.1:8080/users/auth0|65737eb618710d662aeb86e4"
        },
        {
            "email": "user2@users.com",
            "id": "auth0|65737fdbe94488fb5f75debe",
            "name": "user2@users.com",
            "orders": [],
            "self": "http://127.0.0.1:8080/users/auth0|65737fdbe94488fb5f75debe"
        }
    ]
}
```

## Product API

### Create a Product

Allows you to create a new product.

| POST /products |
| :------------- |

**Request**

Path Parameters

None

Request Body

Required

Request Body Format

JSON

Request JSON Attributes

| **Name**    | **Description**                                     | **Required?** |
| :---------- | :-------------------------------------------------- | :------------ |
| name        | The name of the product.                            | Yes           |
| description | The description of the product.                     | Yes           |
| price       | Price of the product.                               | Yes           |
| stock       | Stock of the product. Default is 0 if not provided. | No            |

Request Body Example

```json
{
  "name": "Loud Mouth",
  "description": "A very loud speaker",
  "price": 22.99,
  "stock": 10
}
```

**Response**

Response Body Format

JSON

Response Statuses

| **Outcome** | **Status Code**    | **Notes**                                                                                                                                                                                                |
| :---------- | :----------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Success     | 201 Created        |                                                                                                                                                                                                          |
| Failure     | 400 Bad Request    | If the request is missing any of the required attributes, or has any extra attribute, or has any attribute with an invalid value, the product must not be created, and 400 status code must be returned. |
| Failure     | 406 Not Acceptable | The request must accept JSON.                                                                                                                                                                            |

Response Examples

_Success_

```json
Status: 201 Created

{
  "id": 123,
  "name": "Loud Mouth",
  "description" : "A very loud speaker",
  "price": 22.99,
  "stock": 10,
  "self": "https://appspot.com/products/123"
}
```

_Failure_

```json
Status: 400 Bad Request

{
  "Error": "The request object has missing attributes: price"
}
```

```json
Status: 406 Not Acceptable

{
  "Error": "The request must accept JSON"
}
```

### Get a Product

Allows you to get an existing product.

| GET /products/:product_id |
| :------------------------ |

**Request**

Path Parameters

| **Name**   | **Description**   |
| :--------- | :---------------- |
| product_id | ID of the product |

Request Body

None

**Response**

Response Body Format

JSON or HTML

Response Statuses

| **Outcome** | **Status Code**    | **Notes**                              |
| :---------- | :----------------- | :------------------------------------- |
| Success     | 200 OK             |                                        |
| Failure     | 404 Not Found      | No product with this product_id exists |
| Failure     | 406 Not Acceptable | The request must accept JSON or HTML.  |

Response Examples

_Success_

```json
Status: 200 OK

{
  "id": 123,
  "name": "Loud Mouth",
  "description" : "A very loud speaker",
  "price": 22.99,
  "stock": 10,
  "self": "https://appspot.com/products/123"
}
```

_Failure_

```json
Status: 404 Not Found

{
  "Error": "No product with this product_id exists"
}
```

```json
Status: 406 Not Acceptable

{
  "Error": "The request must accept JSON or HTML"
}
```

### List all Products

List all the products with pagination. This app uses offset pagination. Without any query parameters, the API returns the first 5 products. A `next` link can be used to get the next 5 products if there are more products. The `next` link will be null if there are no more products.

| GET /products?limit=`<number>`&cursor=`<cursor>` |
| :----------------------------------------------- |

**Request**

Path Parameters

| **Name** | **Description**                                 |
| :------- | :---------------------------------------------- |
| limit    | The number of products to return. Default is 5. |
| cursor   | The cursor to start from. Default is 0.         |

Request Body

None

**Response**

Response Body Format

JSON

Response Statuses

| **Outcome** | **Status Code** | **Notes** |
| :---------- | :-------------- | :-------- |
| Success     | 200 OK          |           |

Response Examples

_Success_

```json
Status: 200 OK

{
  "totalItems": 11,
  "products": [
    {
      "id": 123,
      "name": "Loud Mouth",
      "description" : "A very loud speaker",
      "price": 22.99,
      "stock": 10,
      "orders": [],
      "self": "https://appspot.com/products/123"
    },
    {
      "id": 456,
      "name": "Smart Glasses",
      "description" : "Glasses with AI built-in.",
      "price": 209.99,
      "stock": 5,
      "orders": [],
      "self": "https://appspot.com/products/456"
    },
    {
      "id": 789,
      "name": "Smart Watch",
      "description" : "A smart watch.",
      "price": 99.99,
      "stock": 0,
      "orders": [],
      "self": "https://appspot.com/products/789"
    },
    {
      "id": 101,
      "name": "Smart Phone",
      "description" : "A smart phone.",
      "price": 299.99,
      "stock": 2,
      "orders": [],
      "self": "https://appspot.com/products/101"
    },
    {
      "id": 102,
      "name": "Smart TV",
      "description" : "A smart TV.",
      "price": 499.99,
      "stock": 1,
      "orders": [],
      "self": "https://appspot.com/products/102"
    }
  ],
  "next": "https://appspot.com/products?limit=5&cursor=5"
}
```

### Edit a Product

Allows you to edit a product.

| PUT /products/:product_id |
| :------------------------ |

**Request**

Path Parameters

| **Name**   | **Description**   |
| :--------- | :---------------- |
| product_id | ID of the product |

Request Body

Required

Request Body Format

JSON

Request JSON Attributes

| **Name**    | **Description**                 | **Required?** |
| :---------- | :------------------------------ | :------------ |
| name        | The name of the product.        | Yes           |
| description | The description of the product. | Yes           |
| price       | Price of the product.           | Yes           |
| stock       | stock of the product.           | Yes           |

Request Body Example

```json
{
  "name": "Loud Mouth",
  "description": "A very loud speaker",
  "price": 15.99,
  "stock": 10
}
```

**Response**

Response Body Format

JSON

Response Statuses

| **Outcome** | **Status Code**    | **Notes**                                                                                                                                                             |
| :---------- | :----------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Success     | 200 OK             |                                                                                                                                                                       |
| Failure     | 400 Bad Request    | If the request has any missing or extra attribute, or has any attribute with an invalid value, the product must not be updated, and 400 status code must be returned. |
| Failure     | 404 Not Found      | No product with this product_id exists                                                                                                                                |
| Failure     | 406 Not Acceptable | The request must accept JSON.                                                                                                                                         |

Response Examples

_Success_

```json
Status: 200 OK

{
  "id": 123,
  "name": "Loud Mouth",
  "description" : "A very loud speaker",
  "price": 22.99,
  "stock": 8,
  "self": "https://appspot.com/products/123"
}
```

_Failure_

```json
Status: 400 Bad Request

{
  "Error": "The request object is missing at least one of the required attributes or has invalid attributes"
}
```

```json
Status: 404 Not Found

{
  "Error": "No product with this product_id exists"
}
```

```json
Status: 406 Not Acceptable

{
  "Error": "The request must accept JSON"
}
```

### Edit a Product partially

Allows you to edit some attributes of a product.

| PATCH /products/:product_id |
| :-------------------------- |

**Request**

Path Parameters

| **Name**   | **Description**   |
| :--------- | :---------------- |
| product_id | ID of the product |

Request Body

Required

Request Body Format

JSON

Request JSON Attributes

| **Name**    | **Description**                                     | **Required?** |
| :---------- | :-------------------------------------------------- | :------------ |
| name        | The name of the product.                            | No            |
| description | The description of the product.                     | No            |
| price       | Price of the product.                               | No            |
| stock       | stock of the product. Default is 0 if not provided. | No            |

Request Body Example

```json
{
  "stock": 5
}
```

**Response**

Response Body Format

JSON

Response Statuses

| **Outcome** | **Status Code**    | **Notes**                                                                                                                                                  |
| :---------- | :----------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Success     | 200 OK             |                                                                                                                                                            |
| Failure     | 400 Bad Request    | If the request has any extra attribute, or has any attribute with an invalid value, the product must not be updated, and 400 status code must be returned. |
| Failure     | 404 Not Found      | No product with this product_id exists                                                                                                                     |
| Failure     | 406 Not Acceptable | The request must accept JSON.                                                                                                                              |

Response Examples

_Success_

```json
Status: 200 OK

{
  "id": 123,
  "name": "Loud Mouth",
  "description" : "A very loud speaker",
  "price": 22.99,
  "stock": 5,
  "self": "https://appspot.com/products/123"
}
```

_Failure_

```json
Status: 400 Bad Request

{
  "Error": "The request object is missing at least one of the required attributes or has invalid attributes"
}
```

```json
Status: 404 Not Found

{
  "Error": "No product with this product_id exists"
}
```

```json
Status: 406 Not Acceptable

{
  "Error": "The request must accept JSON"
}
```

### Delete a Product

Allows you to delete a product.

| DELETE /products/:product_id |
| :--------------------------- |

**Request**

Path Parameters

| **Name**   | **Description**   |
| :--------- | :---------------- |
| product_id | ID of the product |

Request Body

None

**Response**

No body

Response Body Format

Success: No body

Failure: JSON

Response Statuses

| **Outcome** | **Status Code** | **Notes**                              |
| :---------- | :-------------- | :------------------------------------- |
| Success     | 204 No Content  |                                        |
| Failure     | 404 Not Found   | No product with this product_id exists |

Response Examples

_Success_

```json
Status: 204 No Content
```

_Failure_

```json
Status: 404 Not Found
{
  "Error": "No product with this product_id exists"
}
```

## Order API

### Create an Order

Allows you to create a new order.

| POST /orders |
| :----------- |

**Request**

Path Parameters

None

Request Body

Required

Request Body Format

JSON

Request JSON Attributes

| **Name**       | **Description**                                | **Required?** |
| :------------- | :--------------------------------------------- | :------------ |
| status         | The status of the order. Default is "pending". | No            |
| billingAddress | The billing address of the order.              | Yes           |
| paymentMethod  | The payment method of the order.               | Yes           |

**Response**

Response Body Format

JSON

Response Statuses

| **Outcome** | **Status Code**    | **Notes**                                                                                                                                                                                              |
| :---------- | :----------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Success     | 201 Created        |                                                                                                                                                                                                        |
| Failure     | 400 Bad Request    | If the request is missing any of the required attributes, or has any extra attribute, or has any attribute with an invalid value, the order must not be created, and 400 status code must be returned. |
| Failure     | 401 Unauthorized   | If the request does not have an Authorization header with a valid token, the order must not be created, and 401 status code must be returned.                                                          |
| Failure     | 406 Not Acceptable | The request must accept JSON.                                                                                                                                                                          |

Response Examples

_Success_

```json
Status: 201 Created

{
  "id": 123,
  "user": 456,
  "billingAddress": "86 Cypress St.Niceville, FL 32578",
  "paymentMethod": "credit",
  "status": "pending",
  "products": [],
  "total": 0,
  "dateCreated": "2023-10-06T00:00:00.000Z",
  "dateModified": "2023-10-06T00:00:00.000Z",
  "self": "https://appspot.com/orders/123"
}
```

_Failure_

```json
Status: 400 Bad Request

{
  "Error": "The request object is missing at least one of the required attributes or has invalid attributes"
}
```

```json
Status: 401 Unauthorized

{
  "Error": "The request does not have an Authorization header with a valid token"
}
```

```json
Status: 406 Not Acceptable

{
  "Error": "The request must accept JSON"
}
```

### Get an Order

Allows you to get an existing order.

| GET /orders/:order_id |
| :-------------------- |

**Request**

Path Parameters

| **Name** | **Description** |
| :------- | :-------------- |
| order_id | ID of the order |

Request Body

None

**Response**

Response Body Format

JSON or HTML

Response Statuses

| **Outcome** | **Status Code**    | **Notes**                                                                                                                                         |
| :---------- | :----------------- | :------------------------------------------------------------------------------------------------------------------------------------------------ |
| Success     | 200 OK             |                                                                                                                                                   |
| Failure     | 401 Unauthorized   | If the request does not have an Authorization header with a valid token, the order must not be created, and 401 status code must be returned.     |
| Failure     | 403 Forbidden      | If the request has a valid token, but the order does not belong to the user, the order must not be created, and 403 status code must be returned. |
| Failure     | 404 Not Found      | No order with this order_id exists                                                                                                                |
| Failure     | 406 Not Acceptable | The request must accept JSON or HTML.                                                                                                             |

Response Examples

_Success_

```json
Status: 200 OK

{
  "id": 123,
  "user": 456,
  "billingAddress": "86 Cypress St.Niceville, FL 32578",
  "paymentMethod": "credit",
  "status": "pending",
  "products": [],
  "total": 0,
  "dateCreated": "2023-10-06T00:00:00.000Z",
  "dateModified": "2023-10-06T00:00:00.000Z",
  "self": "https://appspot.com/orders/123"
}
```

_Failure_

```json
Status: 401 Unauthorized

{
  "Error": "The request does not have an Authorization header with a valid token"
}
```

```json
Status: 403 Forbidden

{
  "Error": "The order does not belong to the user"
}
```

```json
Status: 404 Not Found

{
  "Error": "No order with this order_id exists"
}
```

```json
Status: 406 Not Acceptable

{
  "Error": "The request must accept JSON or HTML"
}
```

### List all Orders

List all the orders of the current logged in user with pagination. This app uses offset pagination. Without any query parameters, the API returns the first 5 orders. A `next` link can be used to get the next 5 orders if there are more orders. The `next` link will be null if there are no more orders.

| GET /orders?limit=`<number>`&cursor=`<cursor>` |
| :--------------------------------------------- |

**Request**

Path Parameters

| **Name** | **Description**                               |
| :------- | :-------------------------------------------- |
| limit    | The number of orders to return. Default is 5. |
| cursor   | The cursor to start from. Default is 0.       |

Request Body

None

**Response**

Response Body Format

JSON

Response Statuses

| **Outcome** | **Status Code**    | **Notes**                                                                                                                                     |
| :---------- | :----------------- | :-------------------------------------------------------------------------------------------------------------------------------------------- |
| Success     | 200 OK             |                                                                                                                                               |
| Failure     | 401 Unauthorized   | If the request does not have an Authorization header with a valid token, the order must not be created, and 401 status code must be returned. |
| Failure     | 406 Not Acceptable | The request must accept JSON.                                                                                                                 |

Response Examples

_Success_

```json

Status: 200 OK

{
    "orders": [
        {
            "billingAddress": "86 Cypress St.Niceville, FL 32578",
            "dateCreated": "Sun, 10 Dec 2023 12:01:14 GMT",
            "dateModified": "Sun, 10 Dec 2023 12:01:15 GMT",
            "id": 123,
            "paymentMethod": "credit",
            "products": [],
            "self": "http://appspot.com/orders/123",
            "status": "pending",
            "total": 0.0,
            "user": "629"
        },
        {
            "billingAddress": "86 Cypress St.Niceville, FL 32578",
            "dateCreated": "Sun, 10 Dec 2023 12:52:12 GMT",
            "dateModified": "Sun, 10 Dec 2023 12:52:12 GMT",
            "id": 456,
            "paymentMethod": "credit",
            "products": [],
            "self": "http://appspot.com/orders/456",
            "status": "pending",
            "total": 0.0,
            "user": "629"
        }
    ],
    "totalItems": 2
}
```

### Edit an Order

Allows you to edit an order.

| PUT /orders/:order_id |
| :-------------------- |

**Request**

Path Parameters

| **Name** | **Description** |
| :------- | :-------------- |
| order_id | ID of the order |

Request Body

Required

Request Body Format

JSON

Request JSON Attributes

| **Name**       | **Description**                                | **Required?** |
| :------------- | :--------------------------------------------- | :------------ |
| status         | The status of the order. Default is "pending". | Yes           |
| billingAddress | The billing address of the order.              | Yes           |
| paymentMethod  | The payment method of the order.               | Yes           |

Request Body Example

```json
{
  "status": "canceled",
  "billingAddress": "86 Cypress St.Niceville, FL 32578",
  "paymentMethod": "credit"
}
```

**Response**

Response Body Format

JSON

Response Statuses

| **Outcome** | **Status Code**    | **Notes**                                                                                                                                                           |
| :---------- | :----------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Success     | 200 OK             |                                                                                                                                                                     |
| Failure     | 400 Bad Request    | If the request has any missing or extra attribute, or has any attribute with an invalid value, the order must not be updated, and 400 status code must be returned. |
| Failure     | 401 Unauthorized   | If the request does not have an Authorization header with a valid token, the order must not be created, and 401 status code must be returned.                       |
| Failure     | 403 Forbidden      | If the request has a valid token, but the order does not belong to the user, the order must not be created, and 403 status code must be returned.                   |
| Failure     | 404 Not Found      | No order with this order_id exists                                                                                                                                  |
| Failure     | 406 Not Acceptable | The request must accept JSON.                                                                                                                                       |

Response Examples

_Success_

```json
Status: 200 OK

{
  "id": 123,
  "user": 456,
  "billingAddress": "86 Cypress St.Niceville, FL 32578",
  "paymentMethod": "credit",
  "status": "canceled",
  "products": [],
  "total": 0,
  "dateCreated": "2023-10-06T00:00:00.000Z",
  "dateModified": "2023-10-06T00:00:00.000Z",
  "self": "https://appspot.com/orders/123"
}
```

_Failure_

```json
Status: 400 Bad Request

{
  "Error": "The request object is missing at least one of the required attributes or has invalid attributes"
}
```

```json
Status: 401 Unauthorized

{
  "Error": "The request does not have an Authorization header with a valid token"
}
```

```json

Status: 403 Forbidden

{
  "Error": "The order does not belong to the user"
}
```

```json
Status: 404 Not Found

{
  "Error": "No order with this order_id exists"
}
```

```json
Status: 406 Not Acceptable

{
  "Error": "The request must accept JSON"
}
```

### Edit an Order partially

Allows you to edit some attributes of an order.

| PATCH /orders/:order_id |
| :---------------------- |

**Request**

Path Parameters

| **Name** | **Description** |
| :------- | :-------------- |
| order_id | ID of the order |

Request Body

Required

Request Body Format

JSON

Request JSON Attributes

| **Name**       | **Description**                                | **Required?** |
| :------------- | :--------------------------------------------- | :------------ |
| status         | The status of the order. Default is "pending". | Yes           |
| billingAddress | The billing address of the order.              | Yes           |
| paymentMethod  | The payment method of the order.               | Yes           |

Request Body Example

```json
{
  "status": "canceled"
}
```

**Response**

Response Body Format

JSON

Response Statuses

| **Outcome** | **Status Code**    | **Notes**                                                                                                                                                           |
| :---------- | :----------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Success     | 200 OK             |                                                                                                                                                                     |
| Failure     | 400 Bad Request    | If the request has any missing or extra attribute, or has any attribute with an invalid value, the order must not be updated, and 400 status code must be returned. |
| Failure     | 401 Unauthorized   | If the request does not have an Authorization header with a valid token, the order must not be created, and 401 status code must be returned.                       |
| Failure     | 403 Forbidden      | If the request has a valid token, but the order does not belong to the user, the order must not be created, and 403 status code must be returned.                   |
| Failure     | 404 Not Found      | No order with this order_id exists                                                                                                                                  |
| Failure     | 406 Not Acceptable | The request must accept JSON.                                                                                                                                       |

Response Examples

_Success_

```json
Status: 200 OK

{
  "id": 123,
  "user": 456,
  "billingAddress": "86 Cypress St.Niceville, FL 32578",
  "paymentMethod": "credit",
  "status": "canceled",
  "products": [],
  "total": 0,
  "dateCreated": "2023-10-06T00:00:00.000Z",
  "dateModified": "2023-10-06T00:00:00.000Z",
  "self": "https://appspot.com/orders/123"
}
```

_Failure_

```json
Status: 400 Bad Request

{
  "Error": "The request object is missing at least one of the required attributes or has invalid attributes"
}
```

```json
Status: 401 Unauthorized

{
  "Error": "The request does not have an Authorization header with a valid token"
}
```

```json

Status: 403 Forbidden

{
  "Error": "The order does not belong to the user"
}
```

```json
Status: 404 Not Found

{
  "Error": "No order with this order_id exists"
}
```

```json
Status: 406 Not Acceptable

{
  "Error": "The request must accept JSON"
}
```

### Delete an Order

Allows you to delete an order.

| DELETE /orders/:order_id |
| :----------------------- |

**Request**

Path Parameters

| **Name** | **Description** |
| :------- | :-------------- |
| order_id | ID of the order |

Request Body

None

**Response**

No body

Response Body Format

Success: No body

Failure: JSON

Response Statuses

| **Outcome** | **Status Code**  | **Notes**                                                                                                                                         |
| :---------- | :--------------- | :------------------------------------------------------------------------------------------------------------------------------------------------ |
| Success     | 204 No Content   |                                                                                                                                                   |
| Failure     | 401 Unauthorized | If the request does not have an Authorization header with a valid token, the order must not be created, and 401 status code must be returned.     |
| Failure     | 403 Forbidden    | If the request has a valid token, but the order does not belong to the user, the order must not be created, and 403 status code must be returned. |
| Failure     | 404 Not Found    | No order with this order_id exists                                                                                                                |

Response Examples

_Success_

```json
Status: 204 No Content
```

_Failure_

```json
Status: 401 Unauthorized

{
  "Error": "The request does not have an Authorization header with a valid token"
}
```

```json
Status: 403 Forbidden

{
  "Error": "The order does not belong to the user"
}
```

```json
Status: 404 Not Found
{
  "Error": "No order with this order_id exists"
}
```

### Add a Product to an Order

Allows you to add a product to a non-pending order.

| PUT /orders/:order_id/products/:product_id?quantity=`<number>` |
| :------------------------------------------------------------- |

**Request**

Path Parameters

| **Name**   | **Description**                               |
| :--------- | :-------------------------------------------- |
| order_id   | ID of the order                               |
| product_id | ID of the product                             |
| quantity   | Quantity of the product to add. Default is 1. |

Request Body

None

**Response**

Response Body Format

No body

Response Statuses

| **Outcome** | **Status Code**    | **Notes**                                                                                                                                         |
| :---------- | :----------------- | :------------------------------------------------------------------------------------------------------------------------------------------------ |
| Success     | 204 No Content     |                                                                                                                                                   |
| Failure     | 400 Bad Request    |                                                                                                                                                   |
| Failure     | 401 Unauthorized   | If the request does not have an Authorization header with a valid token, the order must not be created, and 401 status code must be returned.     |
| Failure     | 403 Forbidden      | If the request has a valid token, but the order does not belong to the user, the order must not be created, and 403 status code must be returned. |
| Failure     | 404 Not Found      | No order with this order_id exists                                                                                                                |
| Failure     | 406 Not Acceptable | The request must accept JSON.                                                                                                                     |

Response Examples

_Success_

```json
Status: 204 No Content
```

_Failure_

```json
Status: 401 Unauthorized

{
  "Error": "The request does not have an Authorization header with a valid token"
}
```

```json
Status: 403 Forbidden

{
  "Error": "The order does not belong to the user"
}
```

```json
Status: 404 Not Found
{
  "Error": "No order with this order_id exists"
}
```

```json
Status: 406 Not Acceptable

{
  "Error": "The request must accept JSON"
}
```

### Remove a Product from an Order

Allows you to remove a product from a non-pending order.

| PUT /orders/:order_id/products/:product_id |
| :----------------------------------------- |

**Request**

Path Parameters

| **Name**   | **Description**   |
| :--------- | :---------------- |
| order_id   | ID of the order   |
| product_id | ID of the product |

Request Body

None

**Response**

Response Body Format

No body

Response Statuses

| **Outcome** | **Status Code**    | **Notes**                                                                                                                                         |
| :---------- | :----------------- | :------------------------------------------------------------------------------------------------------------------------------------------------ |
| Success     | 204 No Content     |                                                                                                                                                   |
| Failure     | 400 Bad Request    |                                                                                                                                                   |
| Failure     | 401 Unauthorized   | If the request does not have an Authorization header with a valid token, the order must not be created, and 401 status code must be returned.     |
| Failure     | 403 Forbidden      | If the request has a valid token, but the order does not belong to the user, the order must not be created, and 403 status code must be returned. |
| Failure     | 404 Not Found      | No order with this order_id exists                                                                                                                |
| Failure     | 406 Not Acceptable | The request must accept JSON.                                                                                                                     |

Response Examples

_Success_

```json
Status: 204 No Content
```

_Failure_

```json
Status: 401 Unauthorized

{
  "Error": "The request does not have an Authorization header with a valid token"
}
```

```json
Status: 403 Forbidden

{
  "Error": "The order does not belong to the user"
}
```

```json
Status: 404 Not Found
{
  "Error": "No order with this order_id exists"
}
```

```json
Status: 406 Not Acceptable

{
  "Error": "The request must accept JSON"
}
```
