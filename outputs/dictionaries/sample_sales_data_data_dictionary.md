# Data Dictionary: sample_sales_data

*Generated: 2025-12-01T20:58:55.838327*

## Overview

Dataset containing 30 records across 15 fields

- **Records**: 30
- **Fields**: 15
- **Size**: 0.02 MB
- **Last Updated**: 2025-12-01

## Data Quality

- **Completeness**: 100.00%
- **Quality Score**: 100% (Excellent)
- **Duplicate Records**: 0

## Column Definitions

### Order Number (`order_id`)

Unique identifier for each sales transaction

- **Data Type**: VARCHAR(6)
- **Nullable**: False
- **Null Rate**: 0.00%
- **Unique Values**: 30
- **Owner**: Sales Operations Team
- **Sample Values**: ORD001, ORD002, ORD003, ORD004, ORD005

### Customer Identifier (`customer_id`)

Unique code assigned to each customer account

- **Data Type**: VARCHAR(8)
- **Nullable**: False
- **Null Rate**: 0.00%
- **Unique Values**: 19
- **Owner**: Customer Success Team
- **Sample Values**: CUST1001, CUST1002, CUST1003, CUST1001, CUST1004

### Customer Name (`customer_name`)

Legal business name or individual name of the customer

- **Data Type**: VARCHAR(18)
- **Nullable**: False
- **Null Rate**: 0.00%
- **Unique Values**: 19
- **Owner**: Customer Success Team
- **⚠️ Contains PII**
- **Sample Values**: Acme Corporation, Global Industries, Tech Solutions Inc, Acme Corporation, Startup Ventures

### Product Code (`product_id`)

Unique identifier for each product in the catalog

- **Data Type**: VARCHAR(7)
- **Nullable**: False
- **Null Rate**: 0.00%
- **Unique Values**: 8
- **Owner**: Product Management Team
- **Sample Values**: PROD101, PROD102, PROD103, PROD104, PROD101

### Product Name (`product_name`)

Marketing name or title of the product

- **Data Type**: VARCHAR(13)
- **Nullable**: False
- **Null Rate**: 0.00%
- **Unique Values**: 8
- **Owner**: Product Management Team
- **Sample Values**: Widget A, Widget B, Gadget X, Tool Pro, Widget A

### Product Category (`category`)

High-level classification of products for inventory and reporting

- **Data Type**: VARCHAR(11)
- **Nullable**: False
- **Null Rate**: 0.00%
- **Unique Values**: 4
- **Owner**: Product Management Team
- **Sample Values**: Electronics, Electronics, Technology, Industrial, Electronics

### Order Quantity (`quantity`)

Number of units ordered in a single transaction

- **Data Type**: SMALLINT
- **Nullable**: False
- **Null Rate**: 0.00%
- **Unique Values**: 17
- **Owner**: Sales Operations Team
- **Sample Values**: 5, 3, 10, 2, 1

### Unit Price (`unit_price`)

Price per single unit of the product at time of sale

- **Data Type**: DECIMAL(18,2)
- **Nullable**: False
- **Null Rate**: 0.00%
- **Unique Values**: 8
- **Owner**: Pricing Team
- **Sample Values**: 299.99, 399.99, 149.99, 599.99, 299.99

### Total Order Value (`total_amount`)

Total revenue from the order (quantity × unit price)

- **Data Type**: DECIMAL(18,2)
- **Nullable**: False
- **Null Rate**: 0.00%
- **Unique Values**: 30
- **Owner**: Finance Team
- **Sample Values**: 1499.95, 1199.97, 1499.9, 1199.98, 299.99

### Order Date (`order_date`)

Date when the customer placed the order

- **Data Type**: VARCHAR(10)
- **Nullable**: False
- **Null Rate**: 0.00%
- **Unique Values**: 30
- **Owner**: Sales Operations Team
- **Sample Values**: 2024-01-15, 2024-01-16, 2024-01-17, 2024-01-18, 2024-01-19

### Ship Date (`ship_date`)

Date when the order was shipped to the customer

- **Data Type**: VARCHAR(10)
- **Nullable**: False
- **Null Rate**: 0.00%
- **Unique Values**: 30
- **Owner**: Logistics Team
- **Sample Values**: 2024-01-17, 2024-01-18, 2024-01-19, 2024-01-20, 2024-01-21

### Sales Region (`region`)

Geographic territory where the sale occurred

- **Data Type**: VARCHAR(5)
- **Nullable**: False
- **Null Rate**: 0.00%
- **Unique Values**: 4
- **Owner**: Sales Operations Team
- **Sample Values**: North, South, East, North, West

### Sales Representative (`sales_rep`)

Name of the account executive responsible for the sale

- **Data Type**: VARCHAR(13)
- **Nullable**: False
- **Null Rate**: 0.00%
- **Unique Values**: 4
- **Owner**: Sales Operations Team
- **⚠️ Contains PII**
- **Sample Values**: John Smith, Sarah Johnson, Mike Davis, John Smith, Emily Brown

### Payment Method (`payment_method`)

Method of payment used by the customer

- **Data Type**: VARCHAR(11)
- **Nullable**: False
- **Null Rate**: 0.00%
- **Unique Values**: 2
- **Owner**: Finance Team
- **Sample Values**: Credit Card, Invoice, Credit Card, Invoice, Credit Card

### Customer Segment (`customer_segment`)

Business classification of the customer for targeting and analysis

- **Data Type**: VARCHAR(10)
- **Nullable**: False
- **Null Rate**: 0.00%
- **Unique Values**: 4
- **Owner**: Marketing Team
- **Sample Values**: Enterprise, Enterprise, SMB, Enterprise, Startup
